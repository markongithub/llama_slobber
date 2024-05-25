import random
import sys
from llama_slobber import get_matchday
import secret_tracking_list

league_number = sys.argv[1]
matchday_number = sys.argv[2]
tracked_results = {}
total_players = 0
TRACKED = secret_tracking_list.TRACKED
for division in TRACKED:
    matchday = get_matchday(league_number, matchday_number, division)
    results = matchday[0]
    players = TRACKED[division]
    total_players += len(players)
    for player in players:
        tracked_results[player] = results[player]

players_by_question = [[], [], [], [], [], []]
for player in tracked_results:
    answers = tracked_results[player]["answers"]
    for i in range(6):
        if answers[i] == "1":
            players_by_question[i].append(player)
for i in range(6):
    print(
        f"Q{i+1}: {len(players_by_question[i])}/{total_players} {players_by_question[i]}"
    )
