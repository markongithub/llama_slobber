import random
import sys
from llama_slobber import get_matchday, get_session
import secret_tracking_list
from print_matchday import print_matchday

league_number = sys.argv[1]
matchday_number = sys.argv[2]
shadow_url = None
if len(sys.argv) > 3:
    shadow_url = sys.argv[3]
tracked_results = {}
championship_slots = []
promotion_slots = []
relegation_slots = []
total_players = 0
TRACKED = secret_tracking_list.TRACKED
session = get_session()
for division in TRACKED:
    matchday = get_matchday(league_number, matchday_number, division, session)
    results = matchday[0]
    info = matchday[1]
    players = TRACKED[division]
    total_players += len(players)
    for player in players:
        tracked_results[player] = results[player]
        rank = results[player]["rank"]
        if division[0] == "A" and rank <= 3:
            championship_slots.append(player)
        if rank <= info["maximum_promotion_rank"]:
            promotion_slots.append(player)
        if info["minimum_relegation_rank"] and rank >= info["minimum_relegation_rank"]:
            relegation_slots.append(player)


print_matchday(league_number, matchday_number, TRACKED.popitem()[0], shadow_url)

players_by_question = [[], [], [], [], [], []]
forfeiters = set()
for player in tracked_results:
    answers = tracked_results[player]["answers"]
    for i in range(6):
        if answers[i] == "1":
            players_by_question[i].append(player)
        if answers[i] == "F":
            forfeiters.add(player)
submitted_players = total_players - len(forfeiters)
for i in range(6):
    print(
        f"Q{i+1}: {len(players_by_question[i])}/{submitted_players} {sorted(players_by_question[i])}"
    )


def number_description(number):
    if number == submitted_players:
        return f"a perfect {number}"
    else:
        return number


print(
    f"Out of {submitted_players} tracked players, {number_description(len(players_by_question[0]))} got Q1, {number_description(len(players_by_question[1]))} Q2, {number_description(len(players_by_question[2]))} Q3, {number_description(len(players_by_question[3]))} Q4, {number_description(len(players_by_question[4]))} Q5, and {number_description(len(players_by_question[5]))} Q6."
)
print(f"In line for championship: {championship_slots}")
print(f"In line for promotion: {promotion_slots}")
print(f"In line for relegation: {relegation_slots}")
