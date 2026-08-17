prompt = """
You are an expert question setter for NTA UGC-NET Paper-I (Logical Reasoning). Your questions must match the EXACT style, depth, and format of real UGC-NET past paper questions.

EXAM CONTEXT: UGC-NET Paper-I Logical Reasoning tests a candidate's ability to apply logical rules to scenarios — NOT to recall definitions. Every question must be application-based or scenario-based.

CRITICAL — UGC-NET STYLE RULES (NON-NEGOTIABLE):
1. NO rote definition questions like "What is a syllogism?" or "Define connotation." These are NOT UGC-NET style.
2. ALWAYS ground the question in a concrete scenario, a set of propositions, or a logical situation.
3. For fallacy questions: present a SHORT argument (2-4 sentences) and ask to identify the fallacy.
4. For Square of Opposition: present actual categorical propositions (e.g., "All S are P", "Some S are not P") and ask about their relationship or truth-value implications.
5. For logical equivalence: present 4-5 propositions labeled (A)(B)(C)(D) and ask which are equivalent.
6. For Indian Logic: present a short scenario or argument and ask which Pramana or Hetvabhasa is demonstrated.
7. For syllogism rules: ask "which of the following is/are correct about syllogism?" with multiple rule-statements to evaluate.
8. STRICTLY NO NUMERICAL QUESTIONS of any kind.
9. Options must be plausible and test genuine understanding — not obviously wrong.

{difficulty}

Task:
- Generate 1 entirely original multiple-choice question.
- The question has to be of type: {question_type}
- The style has to be: {style}
- Topic context: {topic}
- Exam: {exam_name}

Sample questions for reference (STRUCTURE ONLY — do not reuse content):
{samples}

INSTRUCTION ON USING SAMPLES:
These samples demonstrate the FORMAT and DEPTH expected. Do NOT copy terms, subjects, or scenarios. Create entirely new content on the given topic. The style (scenario-based, proposition-based, etc.) must match the sample type.

4. Output Structure:
(<Question Number>). <Question Text>

(1) <Option>
(2) <Option>
(3) <Option>
(4) <Option>

Answer Key: <correct option number>

Solution:
<Step-by-step logical explanation of why the correct option is right>
<Explain why each wrong option is wrong>

Further Insights:
<2-3 bullet points of related UGC-NET relevant facts about the underlying concept>
<These should be facts that could themselves be asked as UGC-NET questions>
<Focus on rules, classifications, or connected concepts — not exam tips>

Use exactly {no_of_options} options per question, each on its own line.
End with "Answer Key: <correct option>" on its own line.
Begin "Solution:" on a new line.
Add a blank line between each section for readability.
Entire output must be plain text (copy-paste ready to Microsoft Word).

5. Originality & Variation:
100% Original: Do not copy, paraphrase, or mimic any external source or past questions.
Vary the subjects in propositions (use different nouns — animals, objects, professions, etc.).
Answer Distribution: Spread correct answers across options 1-4 randomly.

6. Quality Control:
The correct answer must be provably correct by strict logical rules.
Distractors must be plausible but clearly wrong upon careful analysis.
Solution must explain the logical rule being applied, not just name the answer.

7. Final Instruction:
- Generate 1 entirely original UGC-NET style question.
- {difficulty}
- Type: {question_type}
- Style: {style}
- Output only English content.
{concept_avoid_text}
"""
