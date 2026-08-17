import asyncio
from doc_maker import generate_and_make_mock
from pathlib import Path
import os
import json

async def run():
    config_path = 'content_meta/jkjunior.json'
    
    # Load config to get db_file and outputs_dir
    with open(config_path, 'r') as f:
        data = json.load(f)
    
    db_file = data.get("db_file")
    outputs_dir = data.get("outputs_dir", "outputs")
    
    print(f"Generating questions from {config_path} to DOCX...")
    
    # Run the doc maker which handles generation, dedup, and docx creation
    output_filename = f"jkjunior_output_{int(asyncio.get_event_loop().time())}.docx"
    
    await generate_and_make_mock(
        json_path=config_path,
        db_file=db_file,
        doc_save_path=Path(outputs_dir),
        output_filename=output_filename
    )

    
    
    print(f"\nSuccessfully generated questions and saved to {os.path.join(outputs_dir, output_filename)}")

if __name__ == "__main__":
    asyncio.run(run())
