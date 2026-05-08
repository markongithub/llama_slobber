import sys
from llama_slobber import get_qhist, get_matchday, get_session
import time

if __name__ == "__main__":
    profile_number = sys.argv[1]
    session = get_session()
    qvals = get_qhist(profile_number, session)
    # {'AMER HIST': {'correct': ['108-22-5', '108-19-6', '94-3-2'], 'wrong': ['107-18-3'...
    wrong_questions = qvals["ART"]["wrong"]
    num_wrong_questions = len(wrong_questions)
    questions_counted = 0
    questions_to_output = []
    for qval in wrong_questions:
        [season, matchday_number, question_index] = qval.split("-")
        matchday = get_matchday(season, matchday_number, "B_Galaxy", session)
        question = matchday[2][int(question_index) - 1]
        questions_to_output.append((question["text"], question["text"]))
        questions_counted += 1
        if questions_counted % 10 == 0:
            print(f"Questions processed: {questions_counted}/{num_wrong_questions}")
        time.sleep(1)
    for question, answer in questions_to_output:
        print(f"> {question}: {answer}")
