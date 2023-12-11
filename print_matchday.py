import random
import sys
from llama_slobber import get_matchday

matchday = get_matchday(99, sys.argv[2], "C_Galaxy")
questions = matchday[2]

max_answer_length = max([len(question["answer"]) for question in questions])
intended_length = max_answer_length + random.randint(10, 20)

for question in questions:
    print(f"{question['number']}. {question['text']}")
    padded = f" {question['answer']}".rjust(intended_length + 1, "_")
    print(f">!`{padded}`!<")
    print()
