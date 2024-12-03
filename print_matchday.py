import random
import sys
from llama_slobber import get_matchday

league_number = sys.argv[1]
matchday_number = sys.argv[2]
matchday = get_matchday(league_number, matchday_number, "A_Galaxy")
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
max_answer_length = max([len(question["answer"]) for question in questions])
intended_length = max_answer_length + random.randint(10, 20)

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
if len(sys.argv) > 3:
    shadow_url = sys.argv[3]
    print(f"[Lounge shadow]({shadow_url}).")
