import json

file_path = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_d5.json'

with open(file_path, 'r') as f:
    data = json.load(f)

new_topic_prompt = "[UGC-NET STYLE: Wording strictly max 2 lines, direct, less theory-heavy. Prefer statement-based MCQs, assertion-reason, and matching questions. DO NOT mix Western and Indian logic. Keep Square of Opposition, Nyaya, and equivalence simple and straight-forward.]"

for subject in data.get('subjects', []):
    for topic in subject.get('topics', []):
        topic_name = topic['topic'].split('[UGC-NET')[0].strip()
        topic['topic'] = f"{topic_name} {new_topic_prompt}"

styles = {
    "Scenario-Based Fallacy Spotting MCQ": "Scenario-Based Fallacy Spotting MCQ. Present a very short scenario (strictly max 2 lines). Direct and less theory-heavy. Ask which fallacy is committed. NTA style. Do not mix Western and Indian logic.",
    "Truth-Value Deduction MCQ": "Truth-Value Deduction MCQ. Give one short proposition as true/false. Ask which other is true/false based on Square of Opposition. Keep it simple. Prefer statement-based or assertion-reason. Strictly max 2 lines.",
    "Logical Equivalence Matching MCQ": "Logical Equivalence Matching MCQ. Give statements to find logical equivalence. Keep it simple and straightforward. Prefer matching or statement-based. Strictly max 2 lines.",
    "Square of Opposition Application MCQ": "Square of Opposition Application MCQ. Ask about contradictory, contrary, etc. Keep it simple and straightforward. Prefer statement-based MCQs or Assertion-Reason. Strictly max 2 lines.",
    "Indian Logic Applied Example MCQ": "Indian Logic Applied Example MCQ. Ask simple, direct questions on Nyaya/Pramanas/Hetvabhasa. Strictly max 2 lines. DO NOT mix with Western logic. Prefer Assertion-Reason or statement-based.",
    "Direct Conceptual MCQ": "Direct Conceptual MCQ. Ask direct, less theory-heavy questions on logical rules. Prefer Assertion-Reason, Statement-based, or matching. Strictly max 2 lines. Keep it simple."
}

for type_name, new_style in styles.items():
    if type_name in data['types']:
        data['types'][type_name]['style'] = new_style

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print("JSON updated successfully.")
