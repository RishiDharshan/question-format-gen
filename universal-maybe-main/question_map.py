import re

def get_question_bank(text_lines: list, re_exprs: str) -> dict:
    '''
    What it does is identifies the starting of questions using the regex and then form dictionary with it.
    
    :param text_lines: The content as lines. dtype is list of strs
    :param re_exprs: regular expression to identify if the start of a line is a question or not.
    '''
    pattern = re.compile(re_exprs)
    question_count = 1
    question = []
    current_question = ""
    previous_question = ""
    question_map = {}
    for line in text_lines:
        if pattern.match(line):
            current_question = pattern.match(line).group(0)
            if current_question:
                previous_question = current_question
                current_question = pattern.match(line).group(0)
            if previous_question:
                if question:
                    key = f"Question no. {question_count}"
                    length_of_question_repres = len(previous_question) - 1
                    question_map[key] = '\n'.join(question)[length_of_question_repres:]
                    question = []
                    question_count += 1
            question.append(line)
        else:
            question.append(line)
    if question:
        key = f"Question no. {question_count}"
        length_of_question_repres = len(previous_question)
        question_map[key] = '\n'.join(question)[length_of_question_repres:]
    return question_map