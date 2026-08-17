import json

file_path = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_d5.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# The topics have total 14 questions, we want 10. Let's keep the first 10.
count = 0
for subject in data.get('subjects', []):
    for topic in subject.get('topics', []):
        new_questions = []
        for q in topic.get('questions', []):
            if count < 10:
                new_questions.append(q)
                count += q['count']
            else:
                break
        topic['questions'] = new_questions
    
    # remove empty topics
    subject['topics'] = [t for t in subject['topics'] if len(t['questions']) > 0]

data['db_file'] = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/lr_ugc_d5_sample10.sqlite3'
out_path = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/lr_ugc_sample10.json'

with open(out_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Created sample 10 json.")
