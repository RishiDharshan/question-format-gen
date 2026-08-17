import json
import asyncio
from pathlib import Path
from doc_maker import generate_and_make_mock
import time

config_path = 'content_meta/jk_accounts_finance.json'

with open(config_path, 'r') as f:
    data = json.load(f)

# Change distribution to total 60 (15 for each of the 4 types)
counts = [15, 15, 15, 15]
for i, qtype in enumerate(data["subjects"][0]["types_of_questions"]):
    qtype["distribution"] = counts[i]

data["db_file"] = "/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/jk_accounts_sample_60.sqlite3"
data["exam_name"] = "JK Accounts/Finance (Sample 60 Theory Only)"

sample_json_path = 'content_meta/jk_accounts_finance_sample_60.json'
with open(sample_json_path, 'w') as f:
    json.dump(data, f, indent=2)

async def main():
    print(f"Generating questions from {sample_json_path} to DOCX...")
    output_filename = f"jk_accounts_finance_sample_60_{int(time.time())}.docx"
    await generate_and_make_mock(
        json_path=sample_json_path,
        db_file=data["db_file"],
        doc_save_path=Path(data["outputs_dir"]),
        output_filename=output_filename
    )
    print(f"\nSuccessfully generated sample of 60 questions and saved to {data['outputs_dir']}/{output_filename}")

if __name__ == "__main__":
    asyncio.run(main())
