import random
import sys
from llama_slobber import get_matchday, get_session
from secret_tracking_list import TCA_RECORDS, TRACKED
from print_matchday import print_matchday


def get_contention_statuses(
    results, matchday_number, maximum_promotion_rank, minimum_relegation_rank
):
    number_one_points = None
    number_two_points = None
    points_inside_promotion = None
    points_outside_promotion = None
    points_inside_relegation = None
    points_outside_relegation = None
    for player, stats in results.items():
        # These are probably ordered by rank but I want it to work even if
        # they're not.
        rank = int(stats["rank"])
        points = int(stats["pts"])
        if rank == 1:
            number_one_points = points
        if rank == 2:
            number_two_points = points
        if maximum_promotion_rank and rank == maximum_promotion_rank:
            points_inside_promotion = points
        if maximum_promotion_rank and rank == maximum_promotion_rank + 1:
            points_outside_promotion = points
        if minimum_relegation_rank and rank == minimum_relegation_rank - 1:
            points_outside_relegation = points
        if minimum_relegation_rank and rank == minimum_relegation_rank:
            points_inside_relegation = points
    statuses = {}
    maximum_points_to_go = 2 * (25 - matchday_number)
    for player, stats in results.items():
        rank = int(stats["rank"])
        points = int(stats["pts"])
        points_to_beat_for_number_one = None
        points_to_beat_for_promotion = None
        points_to_beat_to_avoid_relegation = None
        if rank == 1:
            points_to_beat_for_number_one = number_two_points
        else:
            points_to_beat_for_number_one = number_one_points
        if rank <= maximum_promotion_rank:
            # you're in the promotion zone, so you only need to do better than
            # the best player outside it.
            points_to_beat_for_promotion = points_outside_promotion
        else:
            # you're outside the promotion zone, so you need to do better
            # than the bottom player inside it.
            points_to_beat_for_promotion = points_inside_promotion
        if minimum_relegation_rank is None:
            points_to_beat_to_avoid_relegation = None
        elif rank < minimum_relegation_rank:
            # you're outside the relegation zone, so you only need to do better
            # than the best player inside it.
            points_to_beat_to_avoid_relegation = points_inside_relegation
        else:
            # you're inside the promotion zone, so you need to do better
            # than the bottom player above it.
            points_to_beat_to_avoid_relegation = points_outside_relegation
        necessary_points_for_number_one = necessary_points(
            matchday_number, points, points_to_beat_for_number_one
        )
        if necessary_points_for_number_one <= 0:
            statuses[player] = "has already clinched the division"
        elif necessary_points_for_number_one == (maximum_points_to_go * 2) + 1:
            statuses[player] = (
                "can win the division if everything goes perfectly, but only via tiebreakers"
            )
        elif necessary_points_for_number_one <= (maximum_points_to_go * 2):
            statuses[player] = (
                f"needs {necessary_points_for_number_one} more standings points to win the division (or {necessary_points_for_number_one - 1} and tiebreakers)"
            )
        else:
            statuses[player] = "cannot win the division"
    return statuses


def necessary_points(matchday_number, my_points, rival_points):
    maximum_points_left = 2 * (25 - matchday_number)
    return rival_points + maximum_points_left + 1 - my_points


league_number = sys.argv[1]
matchday_number = sys.argv[2]
shadow_url = None
if len(sys.argv) > 3:
    shadow_url = sys.argv[3]
tracked_results = {}
championship_slots = []
promotion_slots = []
relegation_slots = []
tca_record_chances = []
tracked_contention_statuses = {}
total_players = 0
session = get_session()
for division in TRACKED:
    matchday = get_matchday(league_number, matchday_number, division, session)
    results = matchday[0]
    info = matchday[1]
    players = TRACKED[division]
    total_players += len(players)
    questions_left = 6 * (25 - int(matchday_number))
    contention_statuses = get_contention_statuses(
        results,
        int(matchday_number),
        info["maximum_promotion_rank"],
        info["minimum_relegation_rank"],
    )
    for player in players:
        tracked_results[player] = results[player]
        tracked_contention_statuses[player] = contention_statuses[player]
        rank = results[player]["rank"]
        if division[0] == "A" and rank <= 3:
            championship_slots.append(player)
        if rank <= info["maximum_promotion_rank"]:
            promotion_slots.append(player)
        if info["minimum_relegation_rank"] and rank >= info["minimum_relegation_rank"]:
            relegation_slots.append(player)
        if player in TCA_RECORDS and questions_left <= 30:
            record = TCA_RECORDS[player]
            to_tie_record = record - results[player]["tca"]
            if to_tie_record <= questions_left:
                tca_record_chances.append((player, to_tie_record))


print_matchday(league_number, matchday_number, TRACKED.popitem()[0], shadow_url)

right_by_question = [[], [], [], [], [], []]
wrong_by_question = [[], [], [], [], [], []]
forfeiters = set()
for player in tracked_results:
    answers = tracked_results[player]["answers"]
    for i in range(6):
        if answers[i] == "1":
            right_by_question[i].append(player)
        if answers[i] == "0":
            wrong_by_question[i].append(player)
        if answers[i] == "F":
            forfeiters.add(player)
submitted_players = total_players - len(forfeiters)
for i in range(6):
    if submitted_players == len(right_by_question[i]):
        player_list = "everyone!"
    elif submitted_players - len(right_by_question[i]) < 5:
        player_list = f"everyone but {sorted(wrong_by_question[i])}"
    else:
        player_list = sorted(right_by_question[i])
    print(f"Q{i+1}: {len(right_by_question[i])}/{submitted_players} ({player_list})")


def number_description(number):
    if number == submitted_players:
        return f"a perfect {number}"
    else:
        return number


if forfeiters:
    players_disclaimer = " who actually submitted answers"
else:
    players_disclaimer = ""
print(
    f"Out of {submitted_players} tracked players{players_disclaimer}, {number_description(len(right_by_question[0]))} got Q1, {number_description(len(right_by_question[1]))} Q2, {number_description(len(right_by_question[2]))} Q3, {number_description(len(right_by_question[3]))} Q4, {number_description(len(right_by_question[4]))} Q5, and {number_description(len(right_by_question[5]))} Q6."
)
print(f"In line for championship: {championship_slots}")
print(f"In line for promotion: {promotion_slots}")
print(f"In line for relegation: {relegation_slots}")
for player, status in tracked_contention_statuses.items():
    print(f"{player} {status}")
for player, number in tca_record_chances:
    print(f"{player} needs {number} correct answers to tie their record.")
