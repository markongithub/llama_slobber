import sys
from llama_slobber import get_mini_matchday


minileague_pretty_names = {
    "math3": "Math 3"    
}

def print_mini_matchday(minileague_id, matchday_number, shadow_url=None):
    matchday = get_mini_matchday(minileague_id, matchday_number)
    questions = matchday.questions

    if minileague_id == "not_a_real_minileague" and matchday_number == "2":
        questions[2]["answer"] = 'NORMAL ANSWERE (and a note on what else they did or did not accept)'

    if minileague_id == "1990smusic" and matchday_number == "7":
        questions[5]["answer"] = 'WHITNEY HOUSTON (yes I know the wording is fucked)'
    max_answer_length = max([len(question["answer"]) for question in questions])
    # A value between 0 and 9 based on the lengths of the questions. It will look
    # random but be the same on every run for a given match day.
    deterministic_random_looking_value = (
        sum([len(question["text"]) for question in questions]) % 10
    )
    intended_length = max_answer_length + 10 + deterministic_random_looking_value

    date = matchday.info["date"]
    minileague_name = matchday.info["league_name"]
    # December 8, 2023: Math 3 Match Day 17
    print(f"{date}: {minileague_name} Mini-League Match Day {matchday_number}")
    print()
    first_question = True
    for question in questions:
        if first_question:
            first_question = False
        else:
            print(">")

        print(f"> {question['number']}. {question['text']}")
        padded = f" {question['answer']}".rjust(intended_length + 1, "_")
        print(f"> >!`{padded}`!<")

    print()
    url = f"https://learnedleague.com/mini/match.php?{minileague_id}&{matchday_number}"
    print(f"[Leaguewide stats]({url})")
    if shadow_url:
        print(f"[Lounge shadow]({shadow_url}).")


if __name__ == "__main__":
    minileague_id = sys.argv[1]
    matchday_number = sys.argv[2]

    shadow_url = None
    if len(sys.argv) > 3:
        shadow_url = sys.argv[3]
    print_mini_matchday(minileague_id, matchday_number, shadow_url)
