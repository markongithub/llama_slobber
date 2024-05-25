#!/usr/bin/python
# Copyright (c) 2018 Warren Usui, MIT License
# pylint: disable=W0223
# pylint: disable=E1111
"""
Handle the compilation of information for a match day.
"""
from html.parser import HTMLParser

from llama_slobber.ll_local_io import get_session
from llama_slobber.ll_local_io import get_page_data
from llama_slobber.ll_local_io import MATCH_DATA
from llama_slobber.handle_conn_err import handle_conn_err

NUMBER = "number"
CATEGORY = "category"
TEXT = "text"
ANSWER = "answer"
NULL_QUESTION = {NUMBER: None, CATEGORY: None, TEXT: None, ANSWER: None}


class GetMatchDay(HTMLParser):
    """
    Isolate the fields in a match day page and stash those values in an
    ordered self.result list.  The fields being extracted are people's names,
    indicators as to whether a person got a question right or wrong, and the
    score given to that question.  It turns out there are 14 times as many
    of these data fields as there are per person in the rundle.  Six entries
    for a person's correctness for the questions.  Six entries for what that
    person's opponent scored each question at, and two entries for the person's
    name.  The first occurrence of a person's name is in the pairings list and
    can be used to identify an opponent on this match day.  The second
    occurrence of a person's name is after the scoring information.
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self.getdata = False
        self.result = {"raw_data": [], "questions": [], "date": None}
        self.current_question = NULL_QUESTION.copy()
        self.this_question_field = None
        self.ongoing_question = ""
        self.in_date_heading = False

    def handle_starttag(self, tag, attrs):
        for apt in attrs:
            if apt[0] == "title":
                self.result["raw_data"].append(apt[1])
            if apt[0] == "class":
                if apt[1] == "c0" or apt[1] == "c1" or apt[1] == "cF":
                    self.result["raw_data"].append(apt[1])
                    self.getdata = True
                if apt[1] == "a-red":
                    end_category_index = self.ongoing_question.find(" - ")
                    category = self.ongoing_question[1:end_category_index]
                    text = self.ongoing_question[(end_category_index + 3) :]
                    self.current_question[CATEGORY] = category
                    self.current_question[TEXT] = text
                    self.ongoing_question = ""
                    self.this_question_field = ANSWER
            if apt[0] == "href":
                if apt[1].startswith("/question.php?"):
                    self.this_question_field = NUMBER
        if self.this_question_field == TEXT:
            if tag == "i":
                self.ongoing_question += "_"
            elif tag == "b":
                self.ongoing_question += "**"
            elif tag == "sub":
                self.ongoing_question += "~"
        if tag == "h1":
            self.in_date_heading = True

    def handle_endtag(self, tag):
        if tag == "span" and self.current_question[NUMBER]:
            self.this_question_field = TEXT
        elif self.this_question_field == TEXT:
            if tag == "i":
                self.ongoing_question += "_"
            elif tag == "b":
                self.ongoing_question += "**"
            elif tag == "sub":
                self.ongoing_question += "~"
        elif tag == "h1":
            self.in_date_heading = False

    def handle_data(self, data):
        if self.getdata:
            self.result["raw_data"].append(data)
            self.getdata = False
        if self.this_question_field in [NUMBER, ANSWER]:
            self.current_question[self.this_question_field] = data
        if self.this_question_field == NUMBER:
            self.this_question_field = None
        if self.this_question_field == ANSWER:
            self.result["questions"].append(self.current_question)
            self.current_question = NULL_QUESTION.copy()
            self.this_question_field = None
        if self.this_question_field == TEXT:
            self.ongoing_question += data
            self.current_question[CATEGORY] = "BULLSHIT"
        if self.in_date_heading:
            self.result["date_heading"] = data


class MatchDay(object):
    """
    Match Day is the unit object that represents a set of matches for one
    day in a rundle.
    """

    INFO_PER_USER = 14
    PLOC = INFO_PER_USER - 2
    PSIZE = INFO_PER_USER - 1
    QTOTAL = 6

    def __init__(self, season, match_day, rundle, session=None):
        self.info = {}
        self.info["season"] = season
        self.info["day"] = match_day
        parts = rundle.split("_")
        self.info["rundle"] = parts[0]
        self.info["league"] = parts[1]
        self.info["division"] = 0
        self.result = {}
        if len(parts) > 2:
            self.info["division"] = int(parts[-1])
        page = "&".join([str(season), str(match_day), rundle])
        self.url = MATCH_DATA % page
        parsed = get_page_data(self.url, GetMatchDay(), session=session)
        self.raw_data = parsed["raw_data"]
        self.questions = parsed["questions"]
        self.info["date"] = parsed["date_heading"].strip().split(":", 1)[0]
        discrepancy = len(self.raw_data) % MatchDay.INFO_PER_USER
        if discrepancy == 1:
            print(f"raw_data is too long by 1, so I am going to drop the first element, {self.raw_data[0]}")
            self.raw_data.pop(0)
        elif discrepancy:
            raise ValueError(f"We have {discrepancy} elements too many in raw_data.")
            # raise ValueError('LL Parsing Error')
        self.num_folks = len(self.raw_data) // MatchDay.INFO_PER_USER

    def get_results(self):
        """
        Take the data in self.raw_data and if not previously formated,
        format that data into records for each player.  Save results in
        self.result.  Every entry in self.result consists of a list of
        answer results (right, wrong, or forfeited), a list of points
        assigned, and the person's opponent
        """
        if self.result:
            return self.result
        for i in range(0, self.num_folks, 2):
            self.result[self.raw_data[i]] = {"opp": self.raw_data[i + 1]}
            self.result[self.raw_data[i + 1]] = {"opp": self.raw_data[i]}
        indx = self.num_folks
#        for i in range(len(self.raw_data)):
#            print(f"self.raw_data[{i}]: {self.raw_data[i]}")

        for i in range(0, self.num_folks):
            person = self.raw_data[indx + MatchDay.PLOC]
            if person in self.result:
                self.result[person]["ratings"] = []
                self.result[person]["answers"] = []
                for qnum in range(0, MatchDay.QTOTAL * 2, 2):
                    qindx = qnum + indx
                    answer = self.raw_data[qindx][-1]
                    rating = int(self.raw_data[qindx + 1])
                    self.result[person]["answers"].append(answer)
                    self.result[person]["ratings"].append(rating)
                indx += MatchDay.PSIZE
            else:
                print(
                    f"self.result did not have an index of {person} so I just skipped that person."
                )
        return self.result

    def get_info(self):
        """
        Return what is essentially the metadata in a match day object.
        """
        return self.info


@handle_conn_err
def get_matchday(season, day, rundle, session=None):
    """
    Extract match day information

    Input:
        season -- season number
        day -- match day number in range 1 to 25
        rundle -- name of rundle (R_Pacific_Div_2, for example)

    Returns:
        A list with two entries.
        The first entry is a dict indexed by player name, whose contents are
            dicts containing the following information:
                answers -- list of right ('1'), wrong ('0'), or forfeited
                           answers
                ratings -- list of the point assignments for the questions
                opp -- name of this day's opponent.
        The second entry is a dictionary of values related to the entire
        match day object (league, rundle, division, day, season).
    """
    matchday = MatchDay(season, day, rundle, session=session)
    return [matchday.get_results(), matchday.get_info(), matchday.questions]


if __name__ == "__main__":
    XVAL = get_matchday(78, 25, "B_Pacific")
    print(XVAL)
