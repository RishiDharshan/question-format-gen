from __future__ import annotations

import json
from typing import List, Optional
import random
from typing import List, Optional
import asyncio
from generator import agenerate
from openai import AsyncOpenAI
from dataclasses import dataclass
from dotenv import load_dotenv
from enum import Enum
from output_schema import GeneratorOutput, SubTopicOutput
from tqdm.asyncio import tqdm
from db_ope import build_avoid_list_text, build_concept_avoid_text, hash_question, extract_question_line, init_db
from collections import Counter
load_dotenv()

CLIENT = AsyncOpenAI()

class OperationStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"

@dataclass
class GenerationStatus:
    status: OperationStatus
    data: Optional[GeneratorOutput] = None
    message: str = ""

def load_json(json_path: str) -> dict:
    try:
        with open(json_path, 'r') as f:
            data: dict = json.load(f)
    except Exception as e:
        print(str(e))
        return None
    return data

# we need a function which takes in the inputs and builds a prompt
def _build_prompt(topic: str, 
                  question_type: str, 
                  samples: str, 
                  style: str, 
                  difficulty: str, 
                  no_of_options: str,
                  avoid_text: str,
                  exam_name: str,
                  concept_avoid_text: str = "",
                  prompt_template: str = "") -> str | None:
    try:
        if not prompt_template:
            from prompt import prompt as default_prompt
            prompt_template = default_prompt
        formatted_prompt = prompt_template.format(topic=topic, question_type=question_type, samples=samples, style=style, difficulty=difficulty, no_of_options=no_of_options, exam_name=exam_name, concept_avoid_text=concept_avoid_text)
        return f"{formatted_prompt}\n\n{avoid_text}" if avoid_text else f"{formatted_prompt}"
    except Exception:
        return None

async def _fetch_distinct_subtopics(subject: str, chapter: str, count: int, difficulty: int) -> List[str]:
    if difficulty <= 5:
        focus_instruction = "Focus on standard, widely-taught, and fundamental areas. Pick distinct but common facts. Do NOT pick highly obscure or overly complex topics."
    else:
        focus_instruction = "Focus on obscure, lesser-known but factual areas. Pick highly specific subsets of the topic."

    prompt_text = f"You are an expert on {subject}. Provide exactly {count} sub-topics within the chapter '{chapter}'. CRITICAL: Each sub-topic MUST come from a completely DIFFERENT category or domain within this chapter. Do NOT cluster multiple sub-topics around the same area. For example, if the chapter is 'Transport', give one from railways, one from airways, one from waterways — NOT three different railway facts. Maximize the breadth of coverage. {focus_instruction}"
    result = await agenerate(client=CLIENT, user_prompt=prompt_text, response_model=SubTopicOutput)
    if hasattr(result, 'subtopics'):
        subtopics = result.subtopics
    else:
        subtopics = [chapter] * count
    
    while len(subtopics) < count:
        subtopics.append(chapter)
    return subtopics[:count]

def _return_pool(chapter_list: List[str], distribution: int) -> None:
    if not chapter_list:
        return None
    number_of_chapters: int = len(chapter_list)

    if number_of_chapters <= distribution:
        fill_window: int = distribution - number_of_chapters
        if fill_window > number_of_chapters:
            repeat: int = distribution // number_of_chapters
            serial_chapters: List[str] = chapter_list * repeat

            fill_window = distribution - len(serial_chapters)
            if fill_window == 0:
                return serial_chapters
            else:
                random_chapters: List[str] = random.sample(chapter_list, k=fill_window)
                return serial_chapters + random_chapters
        else:
            random_chapters: List[str] = random.sample(chapter_list, k=fill_window)
            return chapter_list + random_chapters
    else:
        random_chapters: List[str] = random.sample(chapter_list, k=distribution)
        return random_chapters
    
async def _create_subject_prompt_pool(subject_data: dict, question_type_info: dict, no_of_options: int, db_file: str, exam_name: str, prompt_template: str = ""):

    question_types: List[dict] | None = subject_data.get("types_of_questions", None)
    subject_name: str | None = subject_data.get("subject", None)
    subject_chapters: List[str] | None = subject_data.get("chapters", None)

    # Pre-calculate global uniform chapter distribution across all types
    if subject_chapters and question_types:
        total_distribution = sum(t.get("distribution", 5) for t in question_types)
        global_chapter_pool = _return_pool(chapter_list=subject_chapters, distribution=total_distribution)
        random.shuffle(global_chapter_pool)
        
        # Fetch all subtopics for the whole subject globally to ensure uniqueness
        chapter_counts = Counter(global_chapter_pool)
        
        async def fetch_and_map_global(chapter, count):
            if count <= 0: return []
            subtopics = await _fetch_distinct_subtopics(subject_name, chapter, count, 5)
            return [f"{subject_name}: {chapter} (Specific Focus: {subtopic})" for subtopic in subtopics]

        tasks = [fetch_and_map_global(c, count) for c, count in chapter_counts.items()]
        results = await asyncio.gather(*tasks)
        global_chapter_pool = [item for sublist in results for item in sublist]
        random.shuffle(global_chapter_pool)
    else:
        global_chapter_pool = None
        
    prompts = []
    pool_index = 0

    for type in question_types:
        question_type: str = type.get("type", "direct-MCQs")
        question_type_extra: dict | None = question_type_info.get(question_type, None)
        if question_type_extra is not None:
            samples: str | None = question_type_extra.get("samples", None)
            style: str | None = question_type_extra.get("style", None)
        else:
            samples: None = None
            style: None = None
        distribution: int = type.get("distribution", 5)
        difficulty: int = type.get("difficulty", 7)

        if global_chapter_pool:
            chapter_pool = global_chapter_pool[pool_index:pool_index + distribution]
            pool_index += distribution
        else:
            chapter_pool = _return_pool(chapter_list=[subject_name], distribution=distribution)

        if difficulty <= 5:
            difficulty_instruction = f"Difficulty Level {difficulty}/10: Focus on fundamental concepts, basic factual recall, and straightforward questions. Avoid overly complex, tricky, or highly obscure distractors."
        else:
            difficulty_instruction = f"Difficulty Level {difficulty}/10: Emphasize application and analysis (higher-order thinking). Create distractors that are challenging yet unambiguous. Dive into deeper complexity."

        prompt_pool = [
            {
                "topic": chapter,
                "question_type": question_type,
                "samples": samples,
                "style": style,
                "difficulty": difficulty_instruction,
                "no_of_options": no_of_options,
                "exam_name": exam_name,
                "prompt_template": prompt_template
            }
            for chapter in chapter_pool
        ]
        prompts.extend(prompt_pool)
    return prompts #all prompts are formed now use this for generation.

async def _create_topic_based_prompt_pool(subject_data: dict, question_type_info: dict, no_of_options: int, db_file: str, exam_name: str, prompt_template: str = ""):
    """Handles per-topic question distribution schema where each topic specifies its own question types and counts."""

    subject_name: str = subject_data.get("subject", "Unknown Subject")
    topics: List[dict] = subject_data.get("topics", [])

    prompts = []

    for topic_entry in topics:
        topic_str: str = topic_entry.get("topic", subject_name)
        question_specs: List[dict] = topic_entry.get("questions", [])
        
        # Group counts globally for this topic
        total_count = sum(q.get("count", 1) for q in question_specs)
        if total_count > 0:
            all_subtopics = await _fetch_distinct_subtopics(subject_name, topic_str, total_count, 5)
            all_topic_pool = [f"{subject_name}: {topic_str} (Specific Focus: {subtopic})" for subtopic in all_subtopics]
            random.shuffle(all_topic_pool)
        else:
            all_topic_pool = []

        pool_index = 0
        for q_spec in question_specs:
            question_type: str = q_spec.get("type", "Direct MCQ questions")
            count: int = q_spec.get("count", 1)
            difficulty: int = q_spec.get("difficulty", 5)

            question_type_extra: dict | None = question_type_info.get(question_type, None)
            if question_type_extra is not None:
                samples: str | None = question_type_extra.get("samples", None)
                style: str | None = question_type_extra.get("style", None)
            else:
                samples = None
                style = None

            topic_pool = all_topic_pool[pool_index:pool_index + count]
            pool_index += count

            if difficulty <= 5:
                difficulty_instruction = f"Difficulty Level {difficulty}/10: Focus on fundamental concepts, basic factual recall, and straightforward questions. Avoid overly complex, tricky, or highly obscure distractors."
            else:
                difficulty_instruction = f"Difficulty Level {difficulty}/10: Emphasize application and analysis (higher-order thinking). Create distractors that are challenging yet unambiguous. Dive into deeper complexity."
            
            prompt_pool = [
                {
                    "topic": t,
                    "question_type": question_type,
                    "samples": samples,
                    "style": style,
                    "difficulty": difficulty_instruction,
                    "no_of_options": no_of_options,
                    "exam_name": exam_name,
                    "prompt_template": prompt_template
                }
                for t in topic_pool
            ]
            prompts.extend(prompt_pool)

    return prompts
    
async def get_individual_jobs(data: dict) -> dict | None:
    subjects: List[dict] | None = data.get("subjects", None)
    types: dict | None = data.get("types", None)
    no_of_options: int = data.get("no_of_options", 4)
    db_file: str = data.get("db_file")
    exam_name: str = data.get("exam_name")
    prompt_file: str = data.get("prompt_file", "prompt")
    
    import importlib
    try:
        prompt_module = importlib.import_module(prompt_file)
        prompt_template = prompt_module.prompt
    except Exception as e:
        print(f"Failed to load prompt template from {prompt_file}. Error: {e}")
        from prompt import prompt as default_prompt
        prompt_template = default_prompt

    if subjects is None:
        return None
    else:
        subject_prompt_map = {}
        for sub_no, subject in enumerate(subjects, 1):
            # Detect schema: new per-topic schema has 'topics', old schema has 'chapters'
            if "topics" in subject:
                prompt_pool: List[str] = await _create_topic_based_prompt_pool(subject_data=subject, question_type_info=types, no_of_options=no_of_options, db_file=db_file, exam_name=exam_name, prompt_template=prompt_template)
            else:
                prompt_pool: List[str] = await _create_subject_prompt_pool(subject_data=subject, question_type_info=types, no_of_options=no_of_options, db_file=db_file, exam_name=exam_name, prompt_template=prompt_template)
            subject_name: str = subject.get("subject", f"subject no: {sub_no}")
            subject_prompt_map[subject_name] = prompt_pool

        return subject_prompt_map if subject_prompt_map else None
    
async def chapter_safe_task(prompt_kwargs: dict, db_file: str = "") -> GenerationStatus:
    try:
        # Dynamically fetch avoid lists right before generating
        avoid_text = build_avoid_list_text(db_file=db_file) if db_file else ""
        concept_avoid_text = build_concept_avoid_text(db_file=db_file) if db_file else ""
        
        # Build the full prompt string
        prompt = _build_prompt(**prompt_kwargs, avoid_text=avoid_text, concept_avoid_text=concept_avoid_text)
        
        result: GeneratorOutput = await agenerate(client=CLIENT, user_prompt=prompt, response_model=GeneratorOutput)
    except Exception as e:
        return GenerationStatus(
            status=OperationStatus.FAILED,
            message=f"The following issue occured: {e}"
        )
    
    # Return the raw generated question text for downstream dedup + storage
    return GenerationStatus(
        status=OperationStatus.SUCCESS,
        data=result.question,
        message="Success!!!"
    )
    
async def subject_safe_task(prompt_list: List[dict], db_file: str = ""):

    sem_2 = asyncio.Semaphore(25)

    async def chapter_worker_wrapper(prompt_kwargs: dict):
        async with sem_2:
            return await chapter_safe_task(prompt_kwargs=prompt_kwargs, db_file=db_file)
        
    tasks = [chapter_worker_wrapper(prompt_kwargs=p) for p in prompt_list]

    chapter_results = await tqdm.gather(*tasks)

    results = [result.data for result in chapter_results if result.status == OperationStatus.SUCCESS]
    return '\n'.join(results)
    
async def main_worker(prompt_maps: dict, db_file: str = ""):
    
    prompt_lists: List[List[dict]] = [prompt_list for prompt_list in prompt_maps.values()]

    sem_1: asyncio.Semaphore  = asyncio.Semaphore(50)

    async def subject_worker_wrapper(prompt_list: List[dict]):
        async with sem_1:
            return await subject_safe_task(prompt_list=prompt_list, db_file=db_file)
        
    tasks = [subject_worker_wrapper(prompt_list=prompt_list) for prompt_list in prompt_lists]

    subject_result = await tqdm.gather(*tasks)

    return subject_result
    

async def get_questions(json_path: str):
    data = load_json(json_path=json_path)
    db_file: str = data.get("db_file", "")
    subject_prompt_map = await get_individual_jobs(data=data)

    result_pool: List[str] = await main_worker(prompt_maps=subject_prompt_map, db_file=db_file)

    return result_pool
    
if __name__ == "__main__":
    get_questions('trial.json')

