import json
import random
from pathlib import Path

topics = [
    "Structure & Forms of arguments and categorical propositions",
    "Uses of language, Connotations, denotations of terms",
    "Classical square of opposition",
    "Mood and Figure",
    "Formal and Informal fallacies",
    "Indian Logic: Means of knowledge",
    "Pramanas: Types of Pramanas",
    "Structure and kinds of Anumana, Vyapti, and Hetvabhasas"
]

# UGC-NET aligned question types based on the UGC Request doc
req_counts = {
    "Scenario-Based Fallacy Spotting MCQ": 3,       # "Molecules/Qutub Minar" style - identify fallacy in argument
    "Truth-Value Deduction MCQ": 3,                  # Given X is true, what can be inferred as false?
    "Logical Equivalence Matching MCQ": 2,           # Which statements are logically equivalent?
    "Square of Opposition Application MCQ": 2,       # Contradictory/Contrary/Subcontrary pairs
    "Indian Logic Applied Example MCQ": 2,           # Recognize Hetvabhasa/Pramana in a given argument
    "Direct Conceptual MCQ": 2                       # Direct rule/definition based (e.g., rules of syllogism)
}

UGC_THEORY_TAG = " [UGC-NET STYLE: Ask questions in the style of NTA UGC-NET Logical Reasoning — direct, application-based, scenario-driven. Focus on identifying fallacies in scenarios, deducing truth values from Square of Opposition, finding logical equivalences, recognizing Indian logic concepts in arguments. Do NOT generate rote-definition questions. Make them scenario or rule-application based.]"

for diff in [5, 6]:
    pool = []
    for type_name, count in req_counts.items():
        pool.extend([type_name] * count)
    random.shuffle(pool)

    topic_alloc = {t: [] for t in topics}
    topic_list = list(topics)
    random.shuffle(topic_list)

    # Phase 1: every topic gets at least 1
    for t in topic_list:
        topic_alloc[t].append(pool.pop())

    # Phase 2: distribute remaining 6
    extra_targets = random.sample(topic_list, 6)
    for t in extra_targets:
        topic_alloc[t].append(pool.pop())

    assert len(pool) == 0
    total = sum(len(v) for v in topic_alloc.values())
    assert total == 14, f"Expected 14 questions, got {total}"

    json_topics = []
    for t in topics:
        types_for_t = topic_alloc[t]
        assert len(types_for_t) >= 1
        type_counts = {}
        for ty in types_for_t:
            type_counts[ty] = type_counts.get(ty, 0) + 1
        q_list = [{"type": ty, "count": c, "difficulty": diff} for ty, c in type_counts.items()]
        json_topics.append({"topic": t + UGC_THEORY_TAG, "questions": q_list})

    total_q = sum(q["count"] for t in json_topics for q in t["questions"])
    print(f"[d{diff}] Topics: {len(json_topics)}/8, Total questions: {total_q}")

    data = {
        "subjects": [{"subject": "UGC-NET Logical Reasoning", "topics": json_topics}],
        "types": {
            "Scenario-Based Fallacy Spotting MCQ": {
                "samples": '1. "Molecules are in random motion. Qutub Minar is composed of molecules. Therefore, Qutub Minar is in constant random motion." Identify the fallacy committed.\n\n1. Equivocation\n2. Slippery slope\n3. Hasty generalization\n4. Fallacy of composition\n\n2. "If one eats mushrooms after a long gap, one falls ill. I have been having some digestive issues since morning. Therefore, there must have been mushroom in that mixed vegetable soup we had last night." Which fallacy, if any, is committed?\n\n1. It is a valid argument\n2. Affirming the consequent\n3. Hasty Generalization\n4. Begging the question',
                "style": 'Scenario-Based Fallacy Spotting MCQ. Present a SHORT scenario or argument (2-3 sentences max) in quotes, then ask "Which fallacy is committed?" or "Identify the fallacy." The scenario must clearly commit a specific logical fallacy. Options must be 4 named fallacies. One correct, three plausible distractors. Options numbered 1., 2., 3., 4. This is the NTA UGC-NET style. NO abstract definitions — the fallacy must be demonstrated in a concrete scenario. STRICTLY NO NUMERICAL QUESTIONS.'
            },
            "Truth-Value Deduction MCQ": {
                "samples": '1. If the statement "Some birds are not mammals" is given as true, which of the following statements can be immediately inferred to be false?\n\n1. Some mammals are not birds\n2. Some birds are mammals\n3. No birds are mammals\n4. All birds are mammals\n\n2. If the statement "Some rectangles are squares" is given as true, which of the following statements can be inferred to be false?\n\n(A) All rectangles are squares\n(B) Some rectangles are not squares\n(C) Some squares are not rectangles\n(D) No rectangles are squares\n\nChoose the correct answer:\n1. (B), (C) and (D) only\n2. (D) only\n3. (B) and (C) only\n4. (A), (B), (C) and (D)',
                "style": 'Truth-Value Deduction MCQ. Present a single proposition stated as true (e.g., "Some X are Y"). Ask which other proposition(s) can be inferred as false, using rules of the Square of Opposition. Options are other categorical propositions about the same subject. Correct answer follows strict Square of Opposition rules (contradictories, contraries, subcontraries). Options numbered 1., 2., 3., 4. STRICTLY NO NUMERICAL QUESTIONS.'
            },
            "Logical Equivalence Matching MCQ": {
                "samples": '1. Which of the following statements are logically equivalent?\n(A) Some non-birds are mammals\n(B) Some birds are not mammals\n(C) Some non-mammals are non-birds\n(D) Some non-mammals are not non-birds\n\nChoose the most appropriate answer:\n1. A, B and C only\n2. A and C only\n3. B and D only\n4. A, B, C and D\n\n2. From the following, identify the propositions that are logically equivalent:\n(A) Some books are novels\n(B) Some books are not non-novels\n(C) Some novels are not non-books\n(D) Some novels are books\n\n1. (C) and (D) only\n2. (A) and (D) only\n3. (A) and (C) only\n4. (A), (B), (C) and (D)',
                "style": 'Logical Equivalence Matching MCQ. Present 4 propositions labeled (A), (B), (C), (D) — all variations of the same base statement using obversion, conversion, contraposition, double negation. Ask which set is logically equivalent. Options are combinations like "A and D only", "A, B, C and D", etc. Numbered 1., 2., 3., 4. STRICTLY NO NUMERICAL QUESTIONS.'
            },
            "Square of Opposition Application MCQ": {
                "samples": '1. Which of the following propositions are contradictory?\n(A) All squares are rectangles\n(B) No squares are rectangles\n(C) Some squares are rectangles\n(D) Some squares are not rectangles\n\n1. (C) and (D) only\n2. (A) and (D) only\n3. (B) and (D) only\n4. (A) and (B) only\n\n2. Which of the following pairs are contrary propositions?\n1. "All S are P" and "No S are P"\n2. "All S are P" and "Some S are not P"\n3. "No S are P" and "Some S are P"\n4. "Some S are P" and "Some S are not P"',
                "style": 'Square of Opposition Application MCQ. Ask about contradictory, contrary, subcontrary, or subaltern pairs. Either present 4 propositions and ask which pair has a given relationship, OR give statements labeled (A)-(D) and ask which are contradictory/contrary etc. Options numbered 1., 2., 3., 4. Based strictly on the classical Square of Opposition rules. STRICTLY NO NUMERICAL QUESTIONS.'
            },
            "Indian Logic Applied Example MCQ": {
                "samples": '1. According to classical Indian school of logic (Nyaya), which fallacy is committed in the argument: "Anything that is thinkable is nameable because it is thinkable"?\n\n1. Asadhana\n2. Sadhana\n3. Ashraya-asiddha\n4. Svarup-asiddha\n\n2. "Somdutta who is never seen eating during the day is constantly gaining weight. Therefore, she must be eating during the night." As per classical Indian philosophy, which instrument of knowledge is used here?\n\n1. Perception\n2. Analogy\n3. Verbal authority\n4. Postulation',
                "style": 'Indian Logic Applied Example MCQ. Give a short scenario or argument (1-3 sentences) and ask which Hetvabhasa, Pramana, or Indian logic concept applies. The scenario must DEMONSTRATE the concept, not just name it. Options are 4 Sanskrit terms with meanings implied. Students must recognize the concept from context, not from rote definition. Options numbered 1., 2., 3., 4. STRICTLY NO NUMERICAL QUESTIONS.'
            },
            "Direct Conceptual MCQ": {
                "samples": '1. Which of the following is correct in the context of syllogism?\nA. With two negative premises, affirmative conclusion can be drawn.\nB. Predicate of the conclusion is the minor term.\nC. Middle term must be distributed at least once in the premises.\nD. With two universal premises, particular conclusion can be drawn.\nE. The term distributed in the conclusion must be distributed in the premises.\n\nChoose the most appropriate answer:\n1. B and C only\n2. A and C only\n3. D and E only\n4. C and E only\n\n2. Which of the following best describes the function of the middle term in a syllogism?\n\n1. It appears in the conclusion only\n2. It connects the major and minor terms in the premises\n3. It is the subject of the major premise only\n4. It is distributed in all premises',
                "style": 'Direct Conceptual MCQ. Ask about rules, definitions, or principles of logic in the NTA style. Acceptable formats: (a) "Which of the following is correct about X?" with multi-option choose-correct, or (b) single direct question. Options test precise understanding of logical rules. NO scenario needed — test the rule or principle directly. Options numbered 1., 2., 3., 4. STRICTLY NO NUMERICAL QUESTIONS.'
            }
        },
        "no_of_options": 4,
        "db_file": f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/lr_ugc_d{diff}.sqlite3",
        "outputs_dir": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/outputs",
        "exam_name": f"UGC-NET Paper-I Logical Reasoning (Difficulty {diff})"
    }

    path = f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_d{diff}.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"  Created {path}")

print("\nAll JSON files created.")