import json
import asyncio
from pathlib import Path
from doc_maker import generate_and_make_mock

base_json_path = 'content_meta/ssc_sample_8.json'
with open(base_json_path, 'r') as f:
    base_data = json.load(f)

async def main():
    for diff in [5, 6, 7]:
        print(f"Generating for difficulty {diff}...")
        
        # deep copy and modify
        data = json.loads(json.dumps(base_data))
        for t in data["subjects"][0]["topics"]:
            for q in t["questions"]:
                q["difficulty"] = diff
                
        new_json_path = f'content_meta/ssc_sample_d{diff}.json'
        with open(new_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        await generate_and_make_mock(
            json_path=new_json_path, 
            db_file=data["db_file"], 
            doc_save_path=Path(data["outputs_dir"]),
            output_filename=f"ssc_sample_d{diff}.docx"
        )
        print(f"Finished difficulty {diff}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())



