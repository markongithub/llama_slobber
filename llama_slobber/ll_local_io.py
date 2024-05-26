#!/usr/bin/python
# Copyright (c) 2018, 2019 Warren Usui, MIT License
"""
Handle Local I/O and global definitions

INPUTDATA (logindata.ini) is a local file that controls what happens here.

In the DEFAULT section of INPUTDATA, the following must be defined:
    username -- a valid LL name
    password -- the LL password corresponding to username
"""
import configparser
import requests


LLHEADER = "https://www.learnedleague.com"
LOGINFILE = LLHEADER + "/ucp.php?mode=login"
USER_DATA = LLHEADER + "/profiles/previous.php?%s"
QHIST = LLHEADER + "/profiles/qhist.php?%s"
MATCH_DATA = LLHEADER + "/match.php?%s"
ONEDAYS = LLHEADER + "/oneday"
STANDINGS = "/standings.php?"
LLSTANDINGS = LLHEADER + STANDINGS
ARUNDLE = LLSTANDINGS + "%d&A_%s"
INPUTDATA = "logindata.ini"
TOTAL_MATCHES_PER_SEASON = 25


class SessionWrapper:
    def __init__(self):
        self.requests_session = None

    def get(self, url):
        if self.requests_session is None:
            self.requests_session = get_requests_session()
        return self.requests_session.get(url)


def get_session():
    return SessionWrapper()


def get_requests_session():
    """
    Read an ini file, establish a login session

    Input:
        inifile -- name of local ini file with control information

    Returns: logged in requests session to be used in later operations
    """
    config = configparser.ConfigParser()
    config.read(INPUTDATA)
    payload = {"login": "Login"}
    for attrib in ["username", "password"]:
        payload[attrib] = config["DEFAULT"][attrib]
    ses1 = requests.Session()
    try:
        loginfile = config["DEFAULT"]["loginfile"]
    except KeyError:
        loginfile = LOGINFILE
    ses1.post(loginfile, data=payload)
    return ses1


def get_page_text(url, session=None, cache_path="./cache"):
    """
    Extract text from a url or cache

    Input:
        url -- url we are extracting data from
        session -- results login session
        cache_path -- whatevz

    Returns:
        text from web or cache
    """
    if cache_path:
        cache_filename = f"{cache_path}/{url[30:]}"
        try:
            with open(cache_filename, "r") as file:
                text = file.read()
                print(f"Loaded {cache_filename} from disk")
                return text
        except FileNotFoundError:
            print(f"Cache not found on disk, retrieving from web")
    if session is None:
        session = get_session()

    text = session.get(url).text
    if cache_path:
        cache_filename = f"{cache_path}/{url[30:]}"
        with open(cache_filename, "w") as f:
            f.write(text)
    return text


def get_page_data(url, parser, session=None, cache_path="./cache"):
    """
    Extract data from a url

    Input:
        url -- url we are extracting data from
        parser -- http parser that collects the data to be extracted
        session -- results login session

    Returns:
        data collected by parser
    """
    text = get_page_text(url, session, cache_path)
    parser1 = parser
    parser1.feed(text)
    return parser1.result
