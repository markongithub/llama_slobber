#!/usr/bin/python
# Copyright (c) 2018 Warren Usui, MIT License
# pylint: disable=W0223
"""
Function used to find members of a rundle.
"""
from html.parser import HTMLParser
from json import dumps
from typing import List

from llama_slobber.ll_personal_data import get_personal_data
from llama_slobber.ll_local_io import get_session
from llama_slobber.ll_local_io import get_page_data
from llama_slobber.ll_local_io import LLSTANDINGS
from llama_slobber.handle_conn_err import handle_conn_err


class StandingsParser(HTMLParser):
    def __init__(
        self,
        decode_html_entities: bool = False,
        data_separator: str = ' ',
    ) -> None:

        HTMLParser.__init__(self, convert_charrefs=decode_html_entities)

        self._data_separator = data_separator

        self._in_table = False
        self._in_td = False
        self._in_th = False
        self._current_row = []
        self._current_cell = []
        self._integer_result = None
        self.result = {
            "standings": [],
            "num_promotions": None,
            "num_relegations": None}

    def handle_starttag(self, tag: str, attrs: List) -> None:
        """ We need to remember the opening point for the content of interest.
        The other tags (<table>, <tr>) are only handled at the closing point.
        """
        if tag == "table":
            for apt in attrs:
                if apt[0] == 'summary':
                    if apt[1] == "Data table for current LL standings":
                        # print("I think we found the table.")
                        self._in_table = True
        if self._in_table and tag == 'td':
            self._in_td = True
        if self._in_table and tag == 'th':
            self._in_th = True
        if tag == "span" and not self._integer_result:
            for apt in attrs:
                if apt[0] == 'class':
                    if apt[1] == "promotion":
                        self._integer_result = "num_promotions"
                    elif apt[1] == "relegation":
                        self._integer_result = "num_relegations"


    def handle_data(self, data: str) -> None:
        """ This is where we save content to a cell """
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())
        if self._integer_result:
            try: 
                value = int(data)
                self.result[self._integer_result] = value
                self._integer_result = None
            except ValueError:
                pass
    
    def handle_endtag(self, tag: str) -> None:
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row. If the closing tag is </table>, we save the
        current table and prepare for a new one.
        """
        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False

        if self._in_table and tag in ['td', 'th']:
            final_cell = self._data_separator.join(self._current_cell).strip()
            self._current_row.append(final_cell)
            self._current_cell = []
        elif self._in_table and tag == 'tr':
            self.result["standings"].append(self._current_row)
            self._current_row = []
        elif tag == 'table':
            self._in_table = False


@handle_conn_err
def get_standings(season, rundle, session=None):
    """
    Get players in a rundle

    Input:
        season -- season number
        rundle -- rundle name (B_Pacific, for example)
        session request

    Returns list of user names of players in the rundle
    """
    if session is None:
        session = get_session()
    page = "%s%d&%s" % (LLSTANDINGS, season, rundle)
    return get_page_data(page, StandingsParser(), session=session)


def get_rundle_members(season, rundle, session=None):
    """
    Get players in a rundle

    Input:
        season -- season number
        rundle -- rundle name (B_Pacific, for example)
        session request

    Returns list of user names of players in the rundle
    """
    return [r[2] for r in get_standings(season, rundle, session)["standings"][1:]]


def get_rundle_personal(season, rundle, session=None):
    """
    Call get_personal_data on all members of a rundle.

    Input:
        season -- season number
        rundle -- rundle name (B_Pacific, for example)
        session request

    Return personal info in a dictionary indexed by person.
    """
    if session is None:
        session = get_session()
    retv = {}
    plist = get_rundle_members(season, rundle, session=session)
    for person in plist:
        retv[person] = get_personal_data(person, session=session)
    return retv

def analyze_standings(result):
    #i = 0
    #column_indices_by_name = {}
    #for column_header in result["standings"][0]:
    #    column_indices_by_name[column_header] = i
    #    i += 1
    num_players = len(result["standings"]) - 1
    max_rank_to_stay = num_players - result["num_relegations"]
    
    

if __name__ == "__main__":
    print(dumps(get_rundle_personal(79, 'E_Zephyr_Div_2'), indent=4))
