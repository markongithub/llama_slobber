import random
from llama_slobber import get_matchday

questions = get_matchday(99, 5, "B_Galaxy")[2]

max_answer_length = max([len(question["answer"]) for question in questions])
intended_length = max_answer_length + random.randint(10, 20)

for question in questions:
    print(f"{question['number']}. {question['text']}")
    padded = f" {question['answer']}".rjust(intended_length + 1, "_")
    print(f">!`{padded}`!<")
    print()
