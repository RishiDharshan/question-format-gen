# How to use:

### make three additional folders: content_meta, outputs and question_store

1. content_meta: This is where the requirements file is stored. You can store it and if you want, reuse it according to need.
2. Outputs: This is the default output location. The generated documents will come here.
3. question_store: This is where you store the sqlite3 files for content generation.

### Generation requirement template - JSON

Essentially, you should only spend time designing your requirement. The required JSON format is:

```
{
  "subjects": [
    {
      "subject": "<Subject Name>",
      "chapters": [
        "<Chapter 1>",
        "<Chapter 2>",    
        "<Chapter 3>"
      ],
      "types_of_questions": [
        {
          "type": "Direct MCQ questions",
          "distribution": 10,
          "difficulty": 6
        },
        {
          "type": "Match the Following MCQ questions",
          "distribution": 10,
          "difficulty": 6
        }
      ]
    },
    {
      "subject": "<Subject Name>",
      "chapters": [
        "<Chapter 1>",
        "<Chapter 2>",    
        "<Chapter 3>"
      ],
      "types_of_questions": [
        {
          "type": "Direct MCQ questions",
          "distribution": 10,
          "difficulty": 6
        },
        {
          "type": "Match the Following MCQ questions",
          "distribution": 10,
          "difficulty": 6
        }
      ]
    }
  ],
  "types": {
    "Direct MCQ questions": {
      "samples": "<Paste 2–3 sample Direct MCQ questions here>",
      "style": "Direct questions. One-liners. Should be concise."
    },
    "Match the Following MCQ questions": {
      "samples": "<Paste 2–3 sample Match the Following questions here>",
      "style": "Match-the-following/pairing questions. Give two lists (a–d) and (1–5), then ask which option shows the correct matching."
  }
  },
  "no_of_options": 4,
  "db_file": "<Absolute path to your .sqlite3 database file>",
  "outputs_dir": "<Absolute path to your outputs directory>",
  "exam_name": "<Name of the Exam>"
}
```

Any number of subjects and chapters. Any type of question. Distribution for each. Edit all you want. Put it in a json file and put it in content_meta or whatever you want to call the dir.

### How to generate content

1. Go to doc_maker.py
2. You'll find a place to paste the json file's path. Paste it there.
3. Run the code.
4. Results will be available in the output location of your choice.
