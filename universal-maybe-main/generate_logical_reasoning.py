import json
import asyncio
from pathlib import Path
from doc_maker import generate_and_make_mock

async def main():
    for diff in [5, 6, 7, 8]:
        print(f"Generating for difficulty {diff}...")
        json_path = f'content_meta/logical_reasoning_sample_d{diff}.json'
        
        with open(json_path, 'r') as f:
            data = json.load(f)
            
        await generate_and_make_mock(
            json_path=json_path, 
            db_file=data["db_file"], 
            doc_save_path=Path(data["outputs_dir"]),
            output_filename=f"logical_reasoning_sample_d{diff}.docx"
        )
        print(f"Finished difficulty {diff}")
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
