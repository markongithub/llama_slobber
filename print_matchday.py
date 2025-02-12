import sys
from llama_slobber import get_matchday


def print_matchday(league_number, matchday_number, division, shadow_url=None):
    matchday = get_matchday(league_number, matchday_number, division)
    questions = matchday[2]

    if league_number == "102" and matchday_number == "20":
        questions[2]["answer"] = 'SOY SAUCE (and merely "soy" was NOT accepted)'
    if league_number == "103" and matchday_number == "2":
        questions[1]["answer"] = 'PUNIC (and "Phoenician" was NOT accepted)'
    if league_number == "103" and matchday_number == "2":
        questions[0]["answer"] = 'ICE HOCKEY (but just "hockey" was accepted too)'
    if league_number == "103" and matchday_number == "4":
        questions[0]["answer"] = 'LIFE IN HELL (and "is" was NOT accepted)'
    if league_number == "103" and matchday_number == "9":
        questions[0][
            "answer"
        ] = "MUSCLE SHOALS (you can spell that first word the other way)"
    if league_number == "103" and matchday_number == "11":
        questions[5][
            "answer"
        ] = "GUACAMOLE (but, per the note below, ANY answer was counted as correct)"
    if league_number == "103" and matchday_number == "15":
        questions[1]["answer"] = 'GETTING REAL ("being" was NOT accepted)'
    if league_number == "103" and matchday_number == "19":
        questions[3]["answer"] = 'AUSTRALIAN RULES FOOTBALL ("Aussie" was accepted)'
    if league_number == "103" and matchday_number == "20":
        questions[3]["answer"] = '5000 METERS ("5k" was accepted)'
    if league_number == "103" and matchday_number == "21":
        questions[1][
            "answer"
        ] = "JOHN PAUL (I) (the French form of the name was accepted; maybe others were too?)"
    if league_number == "104" and matchday_number == "1":
        questions[2]["answer"] = 'MILK OF MAGNESIA (no, they did not accept it spelled -UM)'
    max_answer_length = max([len(question["answer"]) for question in questions])
    # A value between 0 and 9 based on the lengths of the questions. It will look
    # random but be the same on every run for a given match day.
    deterministic_random_looking_value = (
        sum([len(question["text"]) for question in questions]) % 10
    )
    intended_length = max_answer_length + 10 + deterministic_random_looking_value

    date = matchday[1]["date"]
    # December 8, 2023: LL99 Match Day 17
    print(f"{date}: LL{league_number} Match Day {matchday_number}")
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
    url = f"https://learnedleague.com/match.php?{league_number}&{matchday_number}"
    print(f"[Leaguewide stats]({url}) - but beware of spoilers in the category labels!")
    if shadow_url:
        print(f"[Lounge shadow]({shadow_url}).")


if __name__ == "__main__":
    league_number = sys.argv[1]
    matchday_number = sys.argv[2]

    shadow_url = None
    if len(sys.argv) > 3:
        shadow_url = sys.argv[3]
    print_matchday(league_number, matchday_number, "C_Galaxy_Div_2", shadow_url)
