import json
import asyncio
from pathlib import Path
from doc_maker import generate_and_make_mock

subjects_dist = {
    "History": {
        "chapters": ["Ancient History", "Medieval History", "Modern History", "World History"],
        "counts": {"Straight forward": 20, "2 statement": 10, "3 statement": 6, "4 statement": 4, "Lengthy statements in options": 15, "Assertion reason": 5}
    },
    "Geography": {
        "chapters": ["Physical Geography", "Indian Geography", "World Geography", "Economic Geography"],
        "counts": {"Straight forward": 20, "2 statement": 10, "3 statement": 6, "4 statement": 4, "Lengthy statements in options": 15, "Assertion reason": 5}
    },
    "Biology": {
        "chapters": ["Human Body & Diseases", "Cell Biology & Genetics", "Plant Physiology", "Ecology"],
        "counts": {"Straight forward": 10, "2 statement": 3, "4 statement": 2, "Lengthy statements in options": 5}
    },
    "Chemistry": {
        "chapters": ["Physical Chemistry", "Organic Chemistry", "Inorganic Chemistry", "Everyday Chemistry"],
        "counts": {"Straight forward": 5, "2 statement": 3, "3 statement": 2, "Lengthy statements in options": 5, "Assertion reason": 5}
    },
    "Physics": {
        "chapters": ["Mechanics", "Thermodynamics", "Optics", "Electromagnetism"],
        "counts": {"Straight forward": 5, "2 statement": 3, "3 statement": 2, "Lengthy statements in options": 5, "Assertion reason": 5}
    },
    "Polity": {
        "chapters": ["Constitution of India", "Parliament and State Legislatures", "Judiciary", "Local Self Government"],
        "counts": {"Straight forward": 20, "2 statement": 10, "3 statement": 6, "4 statement": 4, "Lengthy statements in options": 15, "Assertion reason": 5}
    },
    "Economy": {
        "chapters": ["Macroeconomics", "Indian Banking System", "Five Year Plans", "Public Finance"],
        "counts": {"Straight forward": 12, "2 statement": 3, "3 statement": 3, "4 statement": 2, "Lengthy statements in options": 7, "Assertion reason": 3}
    },
    "Art and culture": {
        "chapters": ["Indian Dance Forms", "Festivals and Fairs", "Indian Architecture", "Music and Paintings"],
        "counts": {"Straight forward": 15, "2 statement": 5, "3 statement": 5, "4 statement": 3, "Lengthy statements in options": 8, "Assertion reason": 4}
    },
    "Static": {
        "chapters": ["Census 2011", "Books and Authors", "Sports Achievements", "Important Dates and Events"],
        "counts": {"Straight forward": 15, "2 statement": 5, "3 statement": 5, "4 statement": 3, "Lengthy statements in options": 8, "Assertion reason": 4}
    }
}

types_snippet = {
    "Straight forward": {
        "samples": "Madhabi Puri Buch became the first woman to head SEBI in March 2022. Who was the first woman to head SEBI?\n1. Madhabi Puri Buch\n2. Tuhin Kanta Pandey\n3. Arundhati Bhattacharya\n4. Chanda Kochhar",
        "style": "STRICT BREVITY: Provide direct, clearly formatted questions. Keep intro text strictly under 1 line. Options must be strictly numbered 1., 2., 3., 4., etc. Add blank lines between sections for spacing."
    },
    "2 statement": {
        "samples": "Consider the following statements:\n1. Madhabi Puri Buch became the first woman to head SEBI in March 2022.\n2. Tuhin Kanta Pandey has been appointed as the new SEBI Chief for three years from February 28, 2025.\nWhich of the above statement(s) is/are correct?\n1. 1 only\n2. 2 only\n3. Both 1 and 2\n4. Neither 1 nor 2",
        "style": "2-Statement based questions. Provide a 1-line introductory stem followed by 2 numbered statements (1., 2.). Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4."
    },
    "3 statement": {
        "samples": "Consider the following statements:\n1. Madhabi Puri Buch became the first woman to head SEBI in March 2022.\n2. Tuhin Kanta Pandey has been appointed as the new SEBI Chief for three years from February 28, 2025.\n3. Saudi Arabia has awarded PM Narendra Modi the Order of Mubarak Al-Kabeer.\nWhich of the above statement(s) is/are correct?\n1. 1 and 2 only\n2. 2 and 3 only\n3. 1, 2, and 3\n4. 1 and 3 only",
        "style": "3-Statement based questions. Provide a 1-line introductory stem followed by 3 numbered statements (1., 2., 3.). Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4."
    },
    "4 statement": {
        "samples": "Which of the following statements are correct regarding the Unique Land Parcel Identification Number (ULPIN) system?\n1. ULPIN assigns a unique ID to every land parcel in India.\n2. ULPIN is a 14-digit identification number.\n3. ULPIN helps track land ownership and resolve disputes.\n4. ULPIN is only for urban areas and not rural land.\nChoose the correct option(s):\n1. 1, 2 and 3\n2. 2, 3 and 4\n3. 1, 3 and 4\n4. All of the above",
        "style": "4-Statement based questions. Provide a 1-line introductory stem followed by 4 numbered statements (1., 2., 3., 4.). Then provide options that are combinations of these statements. Options must be strictly labeled 1., 2., 3., 4."
    },
    "Lengthy statements in options": {
        "samples": "Which of the following statements correctly describes the process of vertical heating of the atmosphere?\n1. The process of vertical heating of the atmosphere is known as advection.\n2. The transfer of heat through horizontal movement of air is called convection.\n3. 'Loo' winds in northern India during summer are caused by advection.\n4. The process of vertical heating of the atmosphere is known as convection.",
        "style": "Provide a 1-line introductory question. The 4 options must be detailed and lengthy statements. Options must be strictly numbered 1., 2., 3., 4."
    },
    "Assertion reason": {
        "samples": "Given below are the statements in Assertion and Reason. Choose the correct option:\nAssertion (A): The naming of 'Good Friday' as a positive term is universally accepted among Christian scholars and traditions.\nReason (R): The day is termed 'Good' to signify the positive theological meaning of Jesus's sacrificial death.\nOptions:\n1. Both A and R are individually true and R is the correct explanation of A.\n2. Both A and R are individually true but R is not the correct explanation of A.\n3. A is true but R is false.\n4. A is false but R is true.",
        "style": "Assertion and Reason format. Provide an Assertion (A) and a Reason (R). Provide the standard 4 Assertion/Reason options."
    }
}

base_config = {
  "exam_name": "SSC Mock Questions",
  "prompt_file": "ssc_prompt",
  "db_file": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/question_store/ssc_full.sqlite3",
  "outputs_dir": "/Users/rishidharshan/projects/question format gen/universal-maybe-main/outputs",
  "no_of_options": 4,
  "types": types_snippet
}

async def generate():
    for subject_name, data in subjects_dist.items():
        print(f"Generating questions for {subject_name}...")
        
        types_of_questions = []
        for q_type, count in data["counts"].items():
            if count > 0:
                types_of_questions.append({
                    "type": q_type,
                    "distribution": count,
                    "difficulty": 6
                })
        
        subject_dict = {
            "subject": subject_name,
            "chapters": data["chapters"],
            "types_of_questions": types_of_questions
        }
        
        doc_config = base_config.copy()
        doc_config["subjects"] = [subject_dict]
        
        json_path = f"content_meta/ssc_final_{subject_name}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(doc_config, f, indent=2)
            
        await generate_and_make_mock(
            json_path=json_path,
            db_file=doc_config["db_file"],
            doc_save_path=Path(doc_config["outputs_dir"]),
            output_filename=f"SSC_{subject_name}_Mock.docx"
        )
        print(f"Done generating {subject_name}.docx")

if __name__ == "__main__":
    asyncio.run(generate())
    
