"""
Semantic similarity checking for anti-repetition.
Uses OpenAI text-embedding-3-small to detect questions that are
conceptually identical even when worded differently.
"""
from __future__ import annotations

import json
import numpy as np
from typing import List, Tuple
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

EMBEDDING_MODEL = "text-embedding-3-small"

async def get_embedding(client: AsyncOpenAI, text: str) -> List[float]:
    """Get embedding vector for a piece of text."""
    text = text.replace("\n", " ").strip()
    if not text:
        return []
    resp = await client.embeddings.create(
        input=[text],
        model=EMBEDDING_MODEL
    )
    return resp.data[0].embedding


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a_arr = np.array(a, dtype=np.float32)
    b_arr = np.array(b, dtype=np.float32)
    dot = np.dot(a_arr, b_arr)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))


async def is_too_similar(
    client: AsyncOpenAI,
    new_question_text: str,
    db_file: str,
    threshold: float = 0.85
) -> Tuple[bool, float, List[float]]:
    """
    Check if a new question is semantically too similar to any existing question.
    
    Returns:
        (is_duplicate, max_similarity_score, embedding_vector)
    """
    from db_ope import get_all_embeddings

    new_embedding = await get_embedding(client, new_question_text)
    if not new_embedding:
        return False, 0.0, []

    stored_embeddings = get_all_embeddings(db_file)
    if not stored_embeddings:
        return False, 0.0, new_embedding

    max_sim = 0.0
    for stored_emb in stored_embeddings:
        sim = cosine_similarity(new_embedding, stored_emb)
        if sim > max_sim:
            max_sim = sim
        # Early exit if we already found a match above threshold
        if max_sim >= threshold:
            return True, max_sim, new_embedding

    return max_sim >= threshold, max_sim, new_embedding
