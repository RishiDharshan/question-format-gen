import json
import random
import os

topics = [
    "Structure & Forms of arguments and categorical propositions",
    "Uses of language, Connotations, denotations of terms",
    "Classical square of opposition",
    "Mood and Figure",
    "Formal and Informal fallacies",
    "Deductive and inductive reasoning",
    "Venn diagram: Simple and multiple",
    "Indian Logic: Means of knowledge",
    "Pramanas: Types of Pramanas",
    "Structure and kinds of Anumana, Vyapti, and Hetvabhasas"
]

req_counts = {
    "3-Statement Based MCQ questions": 2,
    "2-Statement Based MCQ questions": 2,
    "Match the Following MCQ questions": 2,
    "Assertion-Reason MCQ questions": 2,
    "Direct MCQ questions": 6
}

difficulties = [5, 6, 7, 8]

ar_samples = """1. Assertion (A): Deductive reasoning moves from the general to the particular.
Reason (R): In a valid deductive argument, if the premises are true, the conclusion must be true.

Options:
1. Both (A) and (R) are true and (R) is the correct explanation of (A).
2. Both (A) and (R) are true but (R) is NOT the correct explanation of (A).
3. (A) is true but (R) is false.
4. (A) is false but (R) is true."""

ar_style = "Assertion-Reason questions. Provide one Assertion (A) and one Reason (R) as single sentences. Options must strictly be the standard 4 choices: Both true & R explains A, Both true & R does not explain A, A true & R false, A false & R true. Options strictly numbered 1., 2., 3., 4."

for old_i in range(1, 5):
    old_file = f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/logical_reasoning_sample_{old_i}.json"
    if os.path.exists(old_file):
        os.remove(old_file)

for diff in difficulties:
    pool = []
    for type_name, count in req_counts.items():
        pool.extend([type_name] * count)
    
    random.shuffle(pool)
    random.shuffle(topics)
    
    topic_alloc = {t: [] for t in topics}
    for i in range(10):
        topic_alloc[topics[i]].append(pool.pop())
    
    for i in range(4):
        topic_alloc[topics[i]].append(pool.pop())
        
    json_topics = []
    for t, types_for_t in topic_alloc.items():
        if types_for_t:
            q_list = []
            type_counts = {}
            for ty in types_for_t:
                type_counts[ty] = type_counts.get(ty, 0) + 1
            
            for ty, c in type_counts.items():
                q_list.append({
                    "type": ty,
                    "count": c,
                    "difficulty": diff  # Set to the specific difficulty for this sample
                })
            
            json_topics.append({
                "topic": t,
                "questions": q_list
            })
            
    json_topics.sort(key=lambda x: topics.index(x["topic"]) if x["topic"] in topics else 0)

    data = {
        "subjects": [
            {
                "subject": "Logical Reasoning",
                "topics": json_topics
            }
        ],
        "types": {
            "Direct MCQ questions": {
                "samples": "31. Fixed cost is a cost:\n\n1. Which changes in total in proportion to changes in output\n2. Which is partly fixed and partly variable in relation to output\n3. Which do not change in total during a given period despite changes in output\n4. Which remains same for each unit of output",
                "style": "ABSOLUTE STRICT BREVITY: The question stem MUST be exactly ONE SHORT line — maximum 10-15 words. No elaboration, no clauses, no multi-line stems. Write the shortest possible direct question. Options should strictly be numbered 1., 2., 3., 4. with a blank line between the question and the options."
            },
            "Match the Following MCQ questions": {
                "samples": "80. Match the following terms with their descriptions:\n\na. Term A                I. Desc I\nb. Term B                II. Desc II\nc. Term C                III. Desc III\nd. Term D                IV. Desc IV\n\nWhich of the pairs given above is/are correctly matched?\n\n1. a-III, b-I, c-II, d-IV\n2. a-III, b-II, c-I, d-IV\n3. a-I, b-III, c-II, d-I\n4. a-IV, b-I, c-III, d-II",
                "style": "Match-the-following questions. Intro stem MUST be ONE SHORT line (max 10 words). Provide a list with items a, b, c, d and another list with Roman numerals I, II, III, IV. Ask which pairs are correctly matched. Options must be strictly numbered 1., 2., 3., 4. Add blank lines between sections for spacing."
            },
            "2-Statement Based MCQ questions": {
                "samples": "91. Consider the following statements:\n1. Statement one is here.\n2. Statement two is here.\n\nWhich of the statements given above is/are correct?\n1. 1 only\n2. 2 only\n3. Both 1 and 2\n4. Neither 1 nor 2",
                "style": "2-Statement based questions. Intro stem MUST be ONE SHORT line (max 10 words). Each statement MUST be ONE brief sentence — no compound sentences or elaboration. Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4. Add blank lines between sections."
            },
            "3-Statement Based MCQ questions": {
                "samples": "95. Consider the following statements:\n1. Statement one is here.\n2. Statement two is here.\n3. Statement three is here.\n\nWhich of the statements given above are correct?\n1. 1 and 2 only\n2. 2 and 3 only\n3. 1 and 3 only\n4. 1, 2, and 3",
                "style": "3-Statement based questions. Intro stem MUST be ONE SHORT line (max 10 words). Each statement MUST be ONE brief sentence — no compound sentences or elaboration. Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4. Add blank lines between sections for spacing."
            },
            "Assertion-Reason MCQ questions": {
                "samples": ar_samples,
                "style": ar_style
            }
        },
        "no_of_options": 4,
        "db_file": f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/logical_reasoning_sample_d{diff}.sqlite3",
        "outputs_dir": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/outputs",
        "exam_name": f"Logical Reasoning Sample (Difficulty {diff})"
    }

    with open(f"/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/logical_reasoning_sample_d{diff}.json", "w") as f:
        json.dump(data, f, indent=2)

print("Generated 4 sample JSON files with correct naming and difficulty.")
