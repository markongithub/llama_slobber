import sys
from llama_slobber import get_matchday


def print_matchday(league_number, matchday_number, division, shadow_url=None):
    matchday = get_matchday(league_number, matchday_number, division)

    results = matchday[0]
    info = matchday[1]
    questions = matchday[2]
    points_by_rank = {
        results[player]["rank"]: results[player]["pts"] for player in results
    }
    max_points_left = 2 * (25 - int(matchday_number))
    for player in results:
        if results[player]["rank"] == 1:
            rival_points_for_first = points_by_rank[2]
        else:
            rival_points_for_first = points_by_rank[1]
        if results[player]["pts"] + max_points_left < rival_points_for_first:
            print(f"{player} cannot possibly win first place.")
        elif rival_points_for_first + max_points_left < results[player]["pts"]:
            print(f"{player} has CLINCHED first place!")
        else:
            points_to_clinch = (
                rival_points_for_first + max_points_left + 1 - results[player]["pts"]
            )
            print(
                f"{player} needs {points_to_clinch} more standings points to clinch first."
            )

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
        questions[2][
            "answer"
        ] = "MILK OF MAGNESIA (no, they did not accept it spelled -UM)"
    if league_number == "105" and matchday_number == "4":
        questions[1]["answer"] = 'SPRAT (and they accepted it with a leading "Jack")'
    if league_number == "105" and matchday_number == "5":
        questions[4]["answer"] = 'INTEGRAL (and Fly says they accepted "integration")'
    if league_number == "105" and matchday_number == "8":
        questions[4][
            "answer"
        ] = 'CHRISTIAN DEMOCRATIC UNION (CDU) ("Christian Democrats" was accepted too)'
    if league_number == "105" and matchday_number == "12":
        questions[2][
            "answer"
        ] = 'BOIL (prepending "crab" was allowed and maybe other shellfish too)'
    if league_number == "105" and matchday_number == "16":
        questions[5][
            "answer"
        ] = 'NIGIRI (first they accepted "onagiri" then they took it back)'
    if league_number == "105" and matchday_number == "18":
        questions[4][
            "answer"
        ] = 'SITTING/INCUMBENT VICE-PRESIDENT (simply "vice president" was not enough)'
    if league_number == "105" and matchday_number == "23":
        questions[2]["answer"] = 'MICKEY (and they did not accept "Nicky")'
    if league_number == "106" and matchday_number == "10":
        questions[1]["answer"] = 'DESICCANT (but they apparently accepted "desiccate")'
    if league_number == "106" and matchday_number == "17":
        questions[3]["answer"] = 'TO THE MANNER BORN (and "manor" was allowed)'
    if league_number == "106" and matchday_number == "24":
        questions[5]["answer"] = 'APPLE (CORPS) (yes they accepted "records")'
    if league_number == "107" and matchday_number == "4":
        questions[2][
            "answer"
        ] = "DACHSUND (they also accepted Wiener, not sure what else)"
    if league_number == "107" and matchday_number == "8":
        questions[0][
            "answer"
        ] = 'LUNAR MARIA/SEAS OF THE MOON (they let me have "areas of the moon")'
    if league_number == "107" and matchday_number == "18":
        questions[5]["answer"] = 'SNL ("Saturday Night Live" was NOT accepted)'
    if league_number == "108" and matchday_number == "4":
        questions[4][
            "answer"
        ] = 'ERWIN SCHRÖDINGER (They let me have it without the "N". Or the umlaut.)'
    if league_number == "108" and matchday_number == "8":
        questions[0]["answer"] = "PITTSBURGH (but they accepted the show name too)"
        questions[3]["answer"] = "JUICE WRLD (both words required)"
    if league_number == "108" and matchday_number == "10":
        questions[3][
            "answer"
        ] = 'BABIES/INFANTS (they accepted "children", and "newborns" after SJ appealed it)'
    if league_number == "108" and matchday_number == "18":
        questions[3]["answer"] = "COSINE, SINE (which had to be in that order)"
    if league_number == "108" and matchday_number == "23":
        questions[4][
            "answer"
        ] = "KHMER EMPIRE (Cambodia not accepted which I think is wrong)"
    max_answer_length = max([len(question["answer"]) for question in questions])
    # A value between 0 and 9 based on the lengths of the questions. It will look
    # random but be the same on every run for a given match day.
    deterministic_random_looking_value = (
        sum([len(question["text"]) for question in questions]) % 10
    )
    print(f"Maximum answer length: {max_answer_length}")
    if max_answer_length > 60:
        intended_length = max_answer_length
    else:
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
    print_matchday(league_number, matchday_number, "C_Galaxy_Div_1", shadow_url)
