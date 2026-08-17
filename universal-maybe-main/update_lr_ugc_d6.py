import json

file_path = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_d6.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# Define the new types
new_types = {
    "4-Statement Based MCQ questions": {
        "samples": "95. Consider the following statements:\n1. Statement one is here.\n2. Statement two is here.\n3. Statement three is here.\n4. Statement four is here.\n\nWhich of the statements given above are correct?\n1. 1 and 2 only\n2. 2, 3 and 4 only\n3. 1, 3 and 4 only\n4. 1, 2, 3 and 4",
        "style": "4-Statement based questions. Intro stem MUST be ONE SHORT line. Present exactly 4 short statements. Each statement MUST be ONE brief sentence \u2014 very direct, no academic jargon. Options are combinations of these statements numbered 1., 2., 3., 4."
    },
    "Assertion-Reason MCQ questions": {
        "samples": "1. Assertion (A): Deductive reasoning moves from the general to the particular.\nReason (R): In a valid deductive argument, if the premises are true, the conclusion must be true.\n\nOptions:\n1. Both (A) and (R) are true and (R) is the correct explanation of (A).\n2. Both (A) and (R) are true but (R) is NOT the correct explanation of (A).\n3. (A) is true but (R) is false.\n4. (A) is false but (R) is true.",
        "style": "Assertion-Reason questions. Provide one Assertion (A) and one Reason (R) as single, simple, short sentences. Not too academic or wordy. Options must strictly be the standard 4 choices. Options strictly numbered 1., 2., 3., 4."
    },
    "Match the Following MCQ questions": {
        "samples": "80. Match the following terms with their descriptions:\n\na. Term A                I. Desc I\nb. Term B                II. Desc II\nc. Term C                III. Desc III\nd. Term D                IV. Desc IV\n\nWhich of the pairs given above is/are correctly matched?\n\n1. a-III, b-I, c-II, d-IV\n2. a-III, b-II, c-I, d-IV\n3. a-I, b-III, c-II, d-I\n4. a-IV, b-I, c-III, d-II",
        "style": "Match-the-following questions. Intro stem MUST be ONE SHORT line. Provide a list with items a, b, c, d and another list with Roman numerals I, II, III, IV. Use simple, direct language. Options must be numbered 1., 2., 3., 4."
    },
    "Direct MCQ questions": {
        "samples": "31. Fixed cost is a cost:\n\n1. Which changes in total in proportion to changes in output\n2. Which is partly fixed and partly variable in relation to output\n3. Which do not change in total during a given period despite changes in output\n4. Which remains same for each unit of output",
        "style": "ABSOLUTE STRICT BREVITY: The question stem MUST be exactly ONE SHORT line. No elaboration, no academic heaviness. Very direct. Options should strictly be numbered 1., 2., 3., 4."
    }
}

data['types'] = new_types

# Distribute equally
question_types = list(new_types.keys())
type_idx = 0

for subject in data.get('subjects', []):
    for topic in subject.get('topics', []):
        # We will give each topic 2 questions, assigning types in a round-robin fashion
        topic['questions'] = [
            {
                "type": question_types[type_idx % 4],
                "count": 1,
                "difficulty": 6
            },
            {
                "type": question_types[(type_idx + 1) % 4],
                "count": 1,
                "difficulty": 6
            }
        ]
        type_idx += 2

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Updated lr_ugc_d6.json")
