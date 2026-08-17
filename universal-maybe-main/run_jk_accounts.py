import asyncio
from generation_engine import get_questions
import os
import json

async def run():
    config_path = 'content_meta/jk_accounts_finance_sample_10.json'
    print(f"Loading config from {config_path}...")
    
    # Run the generation engine
    questions = await get_questions(config_path)
    
    # Combine results
    all_questions = '\n\n'.join(questions)
    
    # Save to output file
    output_filename = f"jk_accounts_finance_output_{int(asyncio.get_event_loop().time())}.txt"
    output_path = os.path.join('outputs', output_filename)
    
    os.makedirs('outputs', exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(all_questions)
        
    print(f"\nSuccessfully generated questions and saved to {output_path}")
    print("\n--- Generated Questions ---\n")
    print(all_questions)

if __name__ == "__main__":
    asyncio.run(run())
