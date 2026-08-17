import json

file_path = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_d6.json'

with open(file_path, 'r') as f:
    data = json.load(f)

new_prompt = "[UGC-NET STYLE: Keep the questions SHORT, NOT lengthy. Use simple, direct wording without heavy academic jargon. Questions should be straightforward and avoid dense, heavy academic phrasing.]"

for subject in data.get('subjects', []):
    for topic in subject.get('topics', []):
        base_topic = topic['topic'].split('[UGC-NET')[0].strip()
        topic['topic'] = f"{base_topic} {new_prompt}"

with open(file_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Updated topic prompts")
