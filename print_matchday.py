import random
import sys
from llama_slobber import get_matchday

league_number = 99  # FIX THIS
matchday_number = sys.argv[2]
matchday = get_matchday(league_number, matchday_number, "C_Galaxy")
questions = matchday[2]

max_answer_length = max([len(question["answer"]) for question in questions])
intended_length = max_answer_length + random.randint(10, 20)

date = matchday[1]["date"]
# December 8, 2023: LL99 Match Day 17
print(f"{date}: LL{league_number} Match Day {matchday_number}")
print()
for question in questions:
    print(f"{question['number']}. {question['text']}")
    padded = f" {question['answer']}".rjust(intended_length + 1, "_")
    print(f">!`{padded}`!<")
    print()

print()
url = f"https://learnedleague.com/match.php?{league_number}&{matchday_number}"
print(f"[Leaguewide stats]({url}) - but beware of spoilers in the category labels!")
if len(sys.argv) > 3:
    shadow_url = sys.argv[3]
    print(f"[Lounge shadow]({shadow_url}).")
