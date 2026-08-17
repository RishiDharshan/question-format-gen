from __future__ import annotations
import sqlite3, hashlib, re, datetime, json
from pathlib import Path
from typing import List
import numpy as np

DEDUP_MAX_AVOID = 300
CONCEPT_MAX_AVOID = 500

def _db_connect(db_file):
    Path(db_file).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_file)

def init_db(db_file):
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qhash TEXT UNIQUE,
                qtext TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qhash TEXT,
                concept TEXT,
                chapter TEXT,
                created_at TEXT,
                FOREIGN KEY (qhash) REFERENCES questions(qhash)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                qhash TEXT UNIQUE,
                embedding TEXT,
                created_at TEXT,
                FOREIGN KEY (qhash) REFERENCES questions(qhash)
            )
        """)
        conn.commit()

def get_known_questions(db_file, limit: int=DEDUP_MAX_AVOID):
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        c.execute("SELECT qtext FROM questions ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
    return [r[0] for r in rows]

def insert_concept(db_file: str, qhash: str, concept: str, chapter: str = ""):
    """Store the core concept tag for a generated question."""
    now = datetime.datetime.now().isoformat(timespec='seconds')
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO concepts (qhash, concept, chapter, created_at) VALUES (?, ?, ?, ?)",
                (qhash, concept.strip().lower(), chapter.strip(), now)
            )
        except sqlite3.Error:
            pass
        conn.commit()

def get_covered_concepts(db_file: str, limit: int = CONCEPT_MAX_AVOID) -> List[str]:
    """Return distinct concepts already covered, most recent first."""
    try:
        with _db_connect(db_file=db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT concept, COUNT(*) as cnt FROM concepts GROUP BY concept ORDER BY cnt DESC LIMIT ?",
                (limit,)
            )
            rows = c.fetchall()
        return [r[0] for r in rows]
    except sqlite3.OperationalError:
        return []

def get_concept_frequency(db_file: str, concept: str) -> int:
    """Return how many times a specific concept has been used."""
    try:
        with _db_connect(db_file=db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT COUNT(*) FROM concepts WHERE concept = ?",
                (concept.strip().lower(),)
            )
            row = c.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0

def get_concepts_grouped_by_chapter(db_file: str, limit: int = CONCEPT_MAX_AVOID) -> dict:
    """Return concepts grouped by chapter for smarter prompt injection."""
    try:
        with _db_connect(db_file=db_file) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT chapter, concept, COUNT(*) as cnt FROM concepts GROUP BY chapter, concept ORDER BY cnt DESC LIMIT ?",
                (limit,)
            )
            rows = c.fetchall()
        grouped = {}
        for chapter, concept, cnt in rows:
            ch = chapter if chapter else "General"
            if ch not in grouped:
                grouped[ch] = []
            grouped[ch].append(f"{concept} (×{cnt})")
        return grouped
    except sqlite3.OperationalError:
        return {}

def build_concept_avoid_text(db_file: str) -> str:
    """Build a concept-level avoid list grouped by chapter for better LLM comprehension."""
    grouped = get_concepts_grouped_by_chapter(db_file=db_file, limit=CONCEPT_MAX_AVOID)
    if not grouped:
        # Fallback to flat list
        concepts = get_covered_concepts(db_file=db_file, limit=CONCEPT_MAX_AVOID)
        if not concepts:
            return ""
        bullets = "\n".join(f"- {c}" for c in concepts)
        return (
            "\n\nCONCEPT DIVERSITY REQUIREMENT — The following concepts have already been covered. "
            "Do NOT generate questions testing these specific concepts:\n"
            f"{bullets}\n"
        )
    
    sections = []
    for chapter, concepts_list in grouped.items():
        concept_bullets = ", ".join(concepts_list)
        sections.append(f"  [{chapter}]: {concept_bullets}")
    grouped_text = "\n".join(sections)
    
    return (
        "\n\nCONCEPT DIVERSITY REQUIREMENT — The following concepts/sub-topics have already been covered (grouped by chapter). "
        "Do NOT generate questions testing these specific concepts. Choose a COMPLETELY DIFFERENT sub-topic or angle "
        "within the assigned chapter that is NOT in this list:\n"
        f"{grouped_text}\n"
        "Pick a fresh, uncovered concept. If you cannot find one within the chapter, choose the LEAST covered concept and approach it from a completely new angle.\n"
    )

def insert_embedding(db_file: str, qhash: str, embedding: List[float]):
    """Store the embedding vector for a question."""
    now = datetime.datetime.now().isoformat(timespec='seconds')
    embedding_json = json.dumps(embedding)
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        try:
            c.execute(
                "INSERT OR IGNORE INTO embeddings (qhash, embedding, created_at) VALUES (?, ?, ?)",
                (qhash, embedding_json, now)
            )
        except sqlite3.Error:
            pass
        conn.commit()

def get_all_embeddings(db_file: str) -> List[List[float]]:
    """Return all stored embedding vectors."""
    try:
        init_db(db_file)  # ensure embeddings table exists
        with _db_connect(db_file=db_file) as conn:
            c = conn.cursor()
            c.execute("SELECT embedding FROM embeddings")
            rows = c.fetchall()
        return [json.loads(r[0]) for r in rows if r[0]]
    except (sqlite3.OperationalError, json.JSONDecodeError):
        return []

def build_avoid_list_text(db_file) -> str | bool:
    try:
        prior = get_known_questions(db_file=db_file, limit=DEDUP_MAX_AVOID)
    except sqlite3.OperationalError:
        init_db(db_file=db_file)
        return False
    if not prior:
        return ""
    # keep it compact to save tokens
    bullets = "\n".join(f"- {norm_question_text(q)[:300]}" for q in reversed(prior))
    return (
        "\n\nDo-Not-Repeat (avoid exact or near-duplicate questions to any of the following):\n"
        f"{bullets}\n"
        "If any candidate question resembles these in stem OR in options logic, discard and draft a new one.\n"
    )

def clean_response(text: str) -> str:
    """
    Remove lines containing 'retry' or similar unwanted indicators,
    collapse multiple blank lines, and strip leading/trailing whitespace.
    """
    lines = text.splitlines()
    cleaned_lines = []
    for line in lines:
        if re.search(r'\bretr(?:y|ying)\b', line, re.IGNORECASE):
            continue
        if not line.strip():
            if cleaned_lines and not cleaned_lines[-1].strip():
                continue
            cleaned_lines.append("")
        else:
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()



def split_question_blocks(text: str):
    """
    Split full output into question blocks starting with a numbered line: '1. ...'
    Returns list of block strings.
    """
    lines = text.strip().splitlines()
    starts = [i for i, ln in enumerate(lines) if re.match(r'^\(\d+\)\.\s', ln)]
    if not starts:
        return []
    blocks = []

    for idx, s in enumerate(starts):
        e = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        blocks.append("\n".join(lines[s:e]).strip())
    return blocks

def dedup_blocks_against_db(blocks, db_file):
    """
    Separate blocks into (unique_blocks, duplicate_blocks) using SQLite ledger.
    """
    unique_blocks, dup_blocks = [], []

    
    # pull all known hashes once for speed
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        c.execute("SELECT qhash FROM questions")
        known_hashes = {row[0] for row in c.fetchall()}

    for b in blocks:
        qline = extract_question_line(b)
        h = hash_question(qline)
        if h in known_hashes:
            dup_blocks.append(b)
        else:
            unique_blocks.append(b)
    return unique_blocks, dup_blocks

def insert_questions(qtexts, db_file):
    now = datetime.datetime.now().isoformat(timespec='seconds')
    with _db_connect(db_file=db_file) as conn:
        c = conn.cursor()
        for q in qtexts:
            try:
                c.execute(
                    "INSERT OR IGNORE INTO questions (qhash, qtext, created_at) VALUES (?, ?, ?)",
                    (hash_question(q), q, now)
                    
                )
            except sqlite3.Error:
                pass
        conn.commit()

def extract_question_line(block: str) -> str:
    """
    From a block, return the question line without the leading number and dot.
    """
    first = block.splitlines()[0]
    q = re.sub(r'^\s*\d+\.\s*', '', first).strip()
    return q

def norm_question_text(q: str) -> str:
    q = re.sub(r'\s+', ' ', q).strip().lower()
    return q

def hash_question(q: str) -> str:
    return hashlib.sha256(norm_question_text(q).encode('utf-8')).hexdigest()



