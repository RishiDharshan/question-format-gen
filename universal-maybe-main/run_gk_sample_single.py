import asyncio
import os
from pathlib import Path
from doc_maker import generate_and_make_mock
import json

async def run_single_doc():
    json_path = "content_meta/jk_accounts_finance.json"
    
    with open(json_path, 'r') as f:
        config = json.load(f)
        
    db_file = config["db_file"]
    outputs_dir = config["outputs_dir"]
    os.makedirs(outputs_dir, exist_ok=True)
    
    output_filename = "JK_Accounts_Finance_Full_Mock.docx"
    
    print(f"Generating full GK Mock Test into single document: {output_filename}...")
    
    try:
        await generate_and_make_mock(
            json_path=json_path,
            db_file=db_file,
            doc_save_path=Path(outputs_dir),
            output_filename=output_filename
        )
        print(f"Successfully saved to {outputs_dir}/{output_filename}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(run_single_doc())
