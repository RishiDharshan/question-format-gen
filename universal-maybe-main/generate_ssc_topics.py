import json
import asyncio
from pathlib import Path
from doc_maker import generate_and_make_mock

topics_config = {
    "history": [
        "Ancient History - Indus Valley Civilization",
        "Ancient History - Buddhism & Jainism",
        "Modern History - Indian National Movement",
        "Modern History - Revolt of 1857"
    ],
    "physics": [
        "Physics - Mechanics and Kinematics",
        "Physics - Thermodynamics and Heat",
        "Physics - Optics and Waves",
        "Physics - Electricity and Magnetism"
    ],
    "general_awareness": [
        "Economy - Indian Banking System (RBI, Nationalization, etc.)",
        "Economy - Five Year Plans & Economic Planning",
        "Biology - Human Body & Diseases",
        "Biology - Cell Biology & Genetics"
    ]
}

types_snippet = {
    "Direct MCQ questions": {
      "samples": "Consider the following statements:\nMadhabi Puri Buch became the first woman to head SEBI in March 2022.\nTuhin Kanta Pandey has been appointed as the new SEBI Chief for three years from February 28, 2025.\nSaudi Arabia has awarded PM Narendra Modi the Order of Mubarak Al-Kabeer.\nWhich of the above statement(s) is/are correct?",
      "style": "STRICT BREVITY: Provide direct, clearly formatted questions. Keep intro text strictly under 1 line. Options must be strictly numbered 1., 2., 3., 4., etc. Add blank lines between sections for spacing."
    },
    "Statement Based MCQ questions": {
      "samples": "1. Consider the following statements regarding Financial Statements:\n1. Balance Sheet shows the financial position of a business.\n2. Profit and Loss Account reveals the net profit or loss.\n3. Trading Account shows the gross profit or loss.\n\nWhich of the statements given above are correct?\n1. 1 and 2 only\n2. 2 and 3 only\n3. 1, 2, and 3\n4. 1 and 3 only\n\n2. Which of the following statements is/are correct about accounting concepts?\n1. Going concern concept assumes business will continue indefinitely.\n2. Dual aspect concept is the basis of double entry bookkeeping.\n3. Materiality concept requires all insignificant events to be recorded.\n\n1. 1, 2 and 3\n2. 1 and 2 only\n3. 2 and 3 only\n4. 1 and 3 only",
      "style": "3-Statement based questions. Provide a 1-line introductory stem followed by 3 numbered statements (1., 2., 3.). Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4. Add blank lines between sections."
    },
    "Match the Following MCQ questions": {
      "samples": "1. Match List I with List II regarding accounting terms:\n\na. Assets            I. Amount invested by owner\nb. Liabilities       II. Resources owned by business\nc. Capital           III. Obligations of the business\nd. Expenses          IV. Costs incurred to earn revenue\n\nWhich of the pairs given above is/are correctly matched?\n\n1. a-II, b-III, c-I, d-IV\n2. a-I, b-II, c-III, d-IV\n3. a-II, b-I, c-III, d-IV\n4. a-III, b-II, c-IV, d-I",
      "style": "Match-the-following questions. Provide a list with items a, b, c, d and another list with Roman numerals I, II, III, IV. Ask which pairs are correctly matched. Keep intro text under 1 line. Options must be strictly numbered 1., 2., 3., 4. Add blank lines between sections."
    }
}

base_config = {
  "exam_name": "SSC General Awareness Mock",
  "prompt_file": "ssc_prompt",
  "db_file": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/ssc_sample.sqlite3",
  "outputs_dir": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/outputs",
  "no_of_options": 4,
  "types": types_snippet
}

async def generate():
    for doc_name, subtopics in topics_config.items():
        print(f"Generating questions for {doc_name}...")
        subjects = []
        # Total 60 questions, distributed across 4 subtopics -> 15 questions per subtopic
        # and there are 3 question types. So 5 questions of each type per subtopic.
        formatted_topics = []
        for subtopic in subtopics:
            q_types = []
            for q_type in types_snippet.keys():
                q_types.append({
                    "type": q_type,
                    "count": 5, 
                    "difficulty": 6
                })
            
            formatted_topics.append({
                "topic": subtopic,
                "questions": q_types
            })
            
        subjects.append({
            "subject": f"SSC {doc_name.capitalize()}",
            "topics": formatted_topics
        })
        
        doc_config = base_config.copy()
        doc_config["subjects"] = subjects
        
        json_path = f"content_meta/ssc_{doc_name}_generated.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(doc_config, f, indent=2)
            
        await generate_and_make_mock(
            json_path=json_path,
            db_file=doc_config["db_file"],
            doc_save_path=Path(doc_config["outputs_dir"]),
            output_filename=f"{doc_name}.docx"
        )
        print(f"Done generating {doc_name}.docx")

if __name__ == "__main__":
    asyncio.run(generate())
