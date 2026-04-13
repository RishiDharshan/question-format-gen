import re, asyncio, random
from question_map import get_question_bank
from generation_engine import get_questions
from pathlib import Path
import docx
from db_ope import split_question_blocks, dedup_blocks_against_db, extract_question_line, insert_questions

def clean_xml(s: str) -> str:
    if s is None:
        return ""
    if not isinstance(s, str):
        s = str(s)

    # XML 1.0 valid chars:
    # 0x9, 0xA, 0xD, and 0x20–0xD7FF, 0xE000–0xFFFD, 0x10000–0x10FFFF
    def ok(cp: int) -> bool:
        return (
            cp == 0x9 or cp == 0xA or cp == 0xD or
            (0x20 <= cp <= 0xD7FF) or
            (0xE000 <= cp <= 0xFFFD) or
            (0x10000 <= cp <= 0x10FFFF)
        )

    return "".join(ch for ch in s if ok(ord(ch)))

async def make_docs(raw_response, db_file):

    blocks = split_question_blocks(raw_response)
    if not blocks:
        # no recognizable questions; accept as-is
        final_cleaned = raw_response
    else:

        file_lock = asyncio.Lock()

        async with file_lock:
            unique_blocks, dup_blocks = dedup_blocks_against_db(blocks, db_file=db_file)

        cleaned_response = '\n'.join(unique_blocks)
        unique_blocks_for_db = unique_blocks
        if dup_blocks:
            print(f"  → Proceeding with output (duplicates present: {len(dup_blocks)}). They will not be added to the DB.")
        if unique_blocks_for_db:
            async with file_lock:
                new_q_lines = [extract_question_line(b) for b in unique_blocks_for_db]
                insert_questions(new_q_lines, db_file=db_file)
                print(f"  → Stored {len(new_q_lines)} new question(s) in {db_file}")

        final_cleaned = cleaned_response

    question_lines = final_cleaned.splitlines()

    regex = r'^\(\d+\)\.\s'
    question_map = get_question_bank(text_lines=question_lines, re_exprs=regex)

    return list(question_map.values())

def number_questions(questions: list[str]) -> list[str]:
    no_of_questions = len(questions)
    
    for i in range(0, no_of_questions):
        questions[i] = f"{i+1}. "+questions[i].strip()
    
    return questions

async def generate_and_make_mock(json_path: str, db_file: str, doc_save_path: Path):
    result_pool = await get_questions(json_path=json_path)
    questions = []
    for result in result_pool:
        final_questions = await make_docs(raw_response=result, db_file=db_file)
        questions.extend(final_questions)
        
    questions = number_questions(questions=questions)
        
    random_string = ''.join([str(random.randint(0,9)) for _ in range(10)])
    docx_save_path = doc_save_path / f'sample_{random_string}.docx'

    doc = docx.Document()

    formatted_questions = '\n\n'.join(questions)
    pattern = r"(\*\*|__)(.*?)\1"
    clean_text = re.sub(pattern, r"\2", formatted_questions)

    try:
        doc.add_paragraph(clean_xml(clean_text))
        doc.save(path_or_stream=docx_save_path)
    except Exception as e:
        print(f"Error: {e}")





if __name__ == "__main__":
    import json
    import sys
    default_json = '/Users/rishidharshan/projects/question format gen/universal-maybe-main/content_meta/jkssb_full.json'
    json_path = sys.argv[1] if len(sys.argv) > 1 else default_json
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    try:
        db_file = data.get("db_file")
        outputs_dir = data.get("outputs_dir")
        doc_save_path = Path(outputs_dir)
    except Exception as e:
        print("Exception occured: {e}")
        import sys
        sys.exit(1)
    asyncio.run(generate_and_make_mock(json_path=json_path, db_file=db_file, doc_save_path=doc_save_path))



    


