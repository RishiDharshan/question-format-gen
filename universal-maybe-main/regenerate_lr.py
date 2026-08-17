import json
import random
from pathlib import Path

topics = [
    "Structure & Forms of arguments and categorical propositions",
    "Uses of language, Connotations, denotations of terms",
    "Classical square of opposition",
    "Mood and Figure",
    "Formal and Informal fallacies",
    "Deductive and inductive reasoning",
    "Indian Logic: Means of knowledge",
    "Pramanas: Types of Pramanas",
    "Structure and kinds of Anumana, Vyapti, and Hetvabhasas"
]

# Removed Match the Following and Assertion-Reason
# Redistributed 4 questions to Direct (6 -> 10) to maintain 14 total
req_counts = {
    "3-Statement Based MCQ questions": 2,
    "2-Statement Based MCQ questions": 2,
    "Direct MCQ questions": 10
}

for diff in [6, 7, 8]:
    pool = []
    for type_name, count in req_counts.items():
        pool.extend([type_name] * count)
    
    random.shuffle(pool)
    topic_list = list(topics)
    random.shuffle(topic_list)
    
    topic_alloc = {t: [] for t in topic_list}
    # 9 topics, 14 questions: 1 each first (9), then 5 more to random topics
    for i in range(9):
        topic_alloc[topic_list[i]].append(pool.pop())
    for i in range(5):
        topic_alloc[topic_list[i]].append(pool.pop())
        
    json_topics = []
    for t in topics:  # Use original order
        types_for_t = topic_alloc[t]
        if types_for_t:
            type_counts = {}
            for ty in types_for_t:
                type_counts[ty] = type_counts.get(ty, 0) + 1
            q_list = []
            for ty, c in type_counts.items():
                q_list.append({"type": ty, "count": c, "difficulty": diff})
            json_topics.append({"topic": t, "questions": q_list})

    data = {
        "subjects": [{"subject": "Logical Reasoning", "topics": json_topics}],
        "types": {
            "Direct MCQ questions": {
                "samples": "31. Fixed cost is a cost:\n\n1. Which changes in total in proportion to changes in output\n2. Which is partly fixed and partly variable in relation to output\n3. Which do not change in total during a given period despite changes in output\n4. Which remains same for each unit of output",
                "style": "ABSOLUTE STRICT BREVITY: The question stem MUST be exactly ONE SHORT line — maximum 10-15 words. No elaboration, no clauses, no multi-line stems. Write the shortest possible direct question. Options should strictly be numbered 1., 2., 3., 4. with a blank line between the question and the options."
            },
            "2-Statement Based MCQ questions": {
                "samples": "91. Consider the following statements:\n1. Statement one is here.\n2. Statement two is here.\n\nWhich of the statements given above is/are correct?\n1. 1 only\n2. 2 only\n3. Both 1 and 2\n4. Neither 1 nor 2",
                "style": "2-Statement based questions. Intro stem MUST be ONE SHORT line (max 10 words). Each statement MUST be ONE brief sentence — no compound sentences or elaboration. Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4. Add blank lines between sections."
            },
            "3-Statement Based MCQ questions": {
                "samples": "95. Consider the following statements:\n1. Statement one is here.\n2. Statement two is here.\n3. Statement three is here.\n\nWhich of the statements given above are correct?\n1. 1 and 2 only\n2. 2 and 3 only\n3. 1 and 3 only\n4. 1, 2, and 3",
                "style": "3-Statement based questions. Intro stem MUST be ONE SHORT line (max 10 words). Each statement MUST be ONE brief sentence — no compound sentences or elaboration. Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4. Add blank lines between sections for spacing."
            }
        },
        "no_of_options": 4,
        "db_file": f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/logical_reasoning_v2_d{diff}.sqlite3",
        "outputs_dir": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/outputs",
        "exam_name": f"Logical Reasoning V2 (Difficulty {diff})"
    }

    path = f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/logical_reasoning_v2_d{diff}.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Created {path}")

print("Done creating 3 JSON files.")
