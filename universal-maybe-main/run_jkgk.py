from __future__ import annotations
import json
import asyncio
import sys
import os
from pathlib import Path
from doc_maker import generate_and_make_mock

async def run(json_path: str):
    with open(json_path, 'r') as f:
        full_config = json.load(f)
    
    db_file = full_config["db_file"]
    outputs_dir = full_config["outputs_dir"]
    os.makedirs(outputs_dir, exist_ok=True)
    
    subjects = full_config["subjects"]
    
    for i, subject in enumerate(subjects, 1):
        subject_name = subject["subject"]
        total_qs = sum(
            q.get("count", 1)
            for t in subject.get("topics", [])
            for q in t.get("questions", [])
        )
        print(f"\n{'='*50}")
        print(f"[{i}/{len(subjects)}] Generating: {subject_name} ({total_qs} questions)")
        print(f"{'='*50}")
    
        # Create a temporary config with just this subject
        temp_config = {k: v for k, v in full_config.items() if k != "subjects"}
        temp_config["subjects"] = [subject]
        
        safe_name = subject_name.replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
        temp_json_path = f"content_meta/jkgk_temp_{safe_name}.json"
        
        with open(temp_json_path, 'w') as f:
            json.dump(temp_config, f, indent=2)
        
        output_filename = f"JKGK_{safe_name}.docx"
        
        try:
            await generate_and_make_mock(
                json_path=temp_json_path,
                db_file=db_file,
                doc_save_path=Path(outputs_dir),
                output_filename=output_filename
            )
            print(f"  -> Saved: {output_filename}")
        except Exception as e:
            print(f"  -> ERROR generating {subject_name}: {e}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_json_path):
                os.remove(temp_json_path)
   
    print(f"\n{'='*50}")
    print(f"All topics generated! Files saved to: {outputs_dir}")
    print(f"{'='*50}")

if __name__ == "__main__":
    json_path = sys.argv[1] if len(sys.argv) > 1 else "content_meta/jkgk_sample.json"
    print(f"Using config: {json_path}")
    asyncio.run(run(json_path))
