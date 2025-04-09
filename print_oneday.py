#!/usr/bin/python
# Copyright (c) 2019 Warren Usui, MIT License
# pylint: disable=W0223
"""
Function used to extract a list of players for a oneday
"""
from datetime import date
from html.parser import HTMLParser

from llama_slobber.ll_local_io import get_session
from llama_slobber.ll_local_io import ONEDAYS
from llama_slobber.handle_conn_err import handle_conn_err
from llama_slobber.ll_parse_oneday_get_date import parse_oneday_get_date
from llama_slobber.ll_read_csv_file import get_csv_oneday_data
from llama_slobber.ll_local_io import get_page_data


DATE_BOUNDARIES = [
    date(2011, 12, 31),
    date(2012, 2, 28),
    date(2014, 7, 31),
    date(2017, 12, 31),
    date.today(),
]
MODERN_BOUNDARY = 3
CSV_BOUNDARY = 4
ERROR_BOUNDARY = 5
FILE_PATTERNS = ["/%s.shtml", "/%s.php", ".php?%s", "/results.php?%s&1"]


@handle_conn_err
def ll_oneday_better(oneday, session=None):
    """
    Extract a list of players from the oneday passed in
    """
    if session is None:
        session = get_session()
    # this only works for onedays after 2017-12-31
    data = get_csv_oneday_data(oneday, session=session)
    correct_answers_by_question = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # indices 4 to 15
    for player_record in data:
        correct_answers_by_question = [
            correct_answers_by_question[i] + int(player_record[i + 4])
            for i in range(12)
        ]
    corrects_with_indices = sorted(
        list(zip(correct_answers_by_question, range(1, 13))), reverse=True
    )
    if corrects_with_indices[4][0] == corrects_with_indices[5][0]:
        raise (
            "There is a tie for fifth-hardest question so I can't calculate optimal moneys."
        )
    optimal_money_indices = set([q[1] for q in corrects_with_indices[0:5]])
    # indices 16 to 27
    for player_record in data:
        moneyed = set([i for i in range(1, 13) if player_record[i + 15] == "1"])
        if moneyed == optimal_money_indices:
            print(f"{player_record[0]} moneyed PERFECTLY!")
        else:
            print(
                f"{player_record[0]} should have moneyed {optimal_money_indices.difference(moneyed)} and not moneyed {moneyed.difference(optimal_money_indices)}"
            )

    return optimal_money_indices


@handle_conn_err
def ll_oneday_players(oneday, session=None):
    """
    Extract a list of players from the oneday passed in
    """
    if session is None:
        session = get_session()
    dval = parse_oneday_get_date(oneday, session=session)
    print(f"dval: {dval}")
    indx = 0
    for boundary in DATE_BOUNDARIES:
        if dval < boundary:
            break
        indx += 1
    if indx == ERROR_BOUNDARY:
        return []
    if indx == CSV_BOUNDARY:
        return get_csv_oneday_players(oneday, session=session)
    ostr = ONEDAYS + FILE_PATTERNS[indx] % oneday
    odata = get_page_data(ostr, GetOldOnedayData(indx), session=session)
    retval = []
    for entry in odata:
        if entry == "LearnedLeague":
            continue
        retval.append(entry[0])
    return list(set(retval))


class GetOldOnedayData(HTMLParser):
    """
    Parse older onedays.
    """

    def __init__(self, htype):
        HTMLParser.__init__(self)
        self.result = []
        self.this_llama = []
        self.scan = False
        self.htype = htype

    def handle_starttag(self, tag, attrs):
        for apt in attrs:
            if apt[0] == "class" and self.htype == MODERN_BOUNDARY:
                fletter = apt[1][0].lower()
                if fletter != apt[1][0]:
                    self.this_llama = [apt[1]]
                    self.scan = True
            if apt[0] == "alt":
                self.this_llama = [apt[1]]
                self.scan = True
        if tag == "td":
            for apt in attrs:
                if apt[0] == "class":
                    if apt[1].startswith("om"):
                        if self.scan:
                            self.this_llama.append(apt[1])

    def handle_data(self, data):
        if self.scan:
            self.this_llama.append(data)

    def handle_endtag(self, tag):
        if tag == "tr":
            if self.scan:
                self.scan = False
                if self.this_llama:
                    self.result.append(self.this_llama)
                    self.this_llama = []


if __name__ == "__main__":
    print(ll_oneday_better("6718"))
