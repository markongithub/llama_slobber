#!/usr/bin/python
# Copyright (c) 2018 Warren Usui, MIT License
# pylint: disable=W0223
# pylint: disable=E1111
"""
Handle the compilation of information for a minileague match day.
"""
from html.parser import HTMLParser

from llama_slobber.ll_local_io import get_session
from llama_slobber.ll_local_io import get_page_data
from llama_slobber.ll_local_io import MINI_MATCH_DATA
from llama_slobber.handle_conn_err import handle_conn_err

NUMBER = "number"
TEXT = "text"
ANSWER = "answer"
NULL_QUESTION = {NUMBER: None, TEXT: None, ANSWER: None}


class GetMiniMatchDay(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.getdata = False
        self.result = {"questions": [], "date": None}
        self.current_question = NULL_QUESTION.copy()
        self.this_question_field = None
        self.ongoing_question = ""
        self.in_date_heading = False

    def handle_starttag(self, tag, attrs):
        for apt in attrs:
            if apt[0] == "class":
                if apt[1] == "answer3":
                    # We have reached the end of a question but not yet entered the answer text.
                    self.current_question[TEXT] = self.ongoing_question.strip()
                    self.ongoing_question = ""
                    self.this_question_field = None
                if apt[1] == "a-red":
                    # We have reached the answer text.
                    self.this_question_field = ANSWER
            if apt[0] == "href":
                if apt[1].startswith("/mini/question.php?"):
                    self.this_question_field = NUMBER
        if self.this_question_field == TEXT:
            if tag == "i":
                if not self.ongoing_question:
                    ends_in_space = "is empty so far"
                elif self.ongoing_question[-1] == ' ':
                    ends_in_space = "ends in a space"
                else:
                    ends_in_space = "does NOT end in a space"
                print(f"I am appending an underscore to this ongoing question, which {ends_in_space}: {self.ongoing_question}")
                self.ongoing_question += "_"
            elif tag == "b":
                self.ongoing_question += "**"
            elif tag == "sub":
                self.ongoing_question += "~"
        if tag == "h1":
            self.in_date_heading = True
        if tag == "br":
            self.in_date_heading = False

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
        if self.this_question_field in [NUMBER, ANSWER]:
            self.current_question[self.this_question_field] = data.strip()
        if self.this_question_field == NUMBER:
            self.this_question_field = None
        if self.this_question_field == ANSWER:
            self.result["questions"].append(self.current_question)
            self.current_question = NULL_QUESTION.copy()
            self.this_question_field = None
        if self.this_question_field == TEXT:
            # you might be tempted to put data.strip() here. Don't. Only strip
            # after reaching the end of the question
            self.ongoing_question += data
        if self.in_date_heading:
            self.result["date_heading"] = data


class MiniMatchDay(object):
    """
    Match Day is the unit object that represents a set of matches for one
    day in a rundle.
    """

    def __init__(self, minileague_name, match_day, session=None):
        if session is None:
            session = get_session()
        self.info = {}
        self.info["minileague_name"] = minileague_name
        self.info["day"] = match_day
        self.result = {}
        page = "&".join([str(minileague_name), str(match_day)])
        self.url = MINI_MATCH_DATA % page
        parsed = get_page_data(self.url, GetMiniMatchDay(), session=session)
        self.questions = parsed["questions"]
        self.info["date"] = parsed["date_heading"].strip()


@handle_conn_err
def get_mini_matchday(minileague_name, day, session=None):
    """
    Returns:
        Just questions and info.
    """
    if session is None:
        session = get_session()
    matchday = MiniMatchDay(minileague_name, day, session=session)
    return matchday


if __name__ == "__main__":
    XVAL = get_mini_matchday("math3", 3)
    print(XVAL.questions)
