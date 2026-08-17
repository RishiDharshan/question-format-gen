import asyncio
import json
from pathlib import Path
from doc_maker import generate_and_make_mock

async def run():
    # Use the newly created sample configuration
    config_path = 'content_meta/new_ssc_full.json'
    print(f"Loading config from {config_path}...")
    
    with open(config_path, 'r') as f:
        data = json.load(f)
        
    db_file = data.get("db_file")
    outputs_dir = data.get("outputs_dir", "outputs")
    doc_save_path = Path(outputs_dir)
    doc_save_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Using database: {db_file}")
    
    # Run the generation engine through doc_maker which handles DB deduplication
    await generate_and_make_mock(json_path=config_path, db_file=db_file, doc_save_path=doc_save_path, output_filename="new_ssc_sample_full.docx")
    
    print(f"\nSuccessfully generated questions and saved to {outputs_dir}/new_ssc_sample_full.docx")

if __name__ == "__main__":
    asyncio.run(run())
