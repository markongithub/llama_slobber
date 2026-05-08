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
import os
import requests
from playwright.sync_api import sync_playwright
import time

LLHEADER = "https://www.learnedleague.com"
LOGINFILE = LLHEADER + "/ucp.php?mode=login"
USER_DATA = LLHEADER + "/profiles/previous.php?%s"
QHIST = LLHEADER + "/profiles.php?%s&9"
MATCH_DATA = LLHEADER + "/match.php?%s"
MINI_MATCH_DATA = LLHEADER + "/mini/match.php?%s"
ONEDAYS = LLHEADER + "/oneday"
STANDINGS = "/standings.php?"
LLSTANDINGS = LLHEADER + STANDINGS
ARUNDLE = LLSTANDINGS + "%d&A_%s"
INPUTDATA = "logindata.ini"
TOTAL_MATCHES_PER_SEASON = 25
TMP_PATH = "/tmp"
RATE_LIMIT_SECONDS = 1

class SessionWrapper:
    def __init__(self):
        self.playwright_page = None
        self.requests_session = None
        self.last_request_time = 0

    def get_with_playwright(self, url):
        print(f"get_with_playwright({url})")
        if time.time() - self.last_request_time < RATE_LIMIT_SECONDS:
            time.sleep(RATE_LIMIT_SECONDS - (time.time() - self.last_request_time))
        if self.playwright_page is None:
            print("Starting browser, hopefully we only do this once...")
            sync = sync_playwright().start()
            browser = sync.chromium.launch_persistent_context(headless=True, user_data_dir="./user_data_dir",
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            self.playwright_page = browser.new_page()
        if url.endswith(".csv"):
            return self.get_csv_with_playwright(url)
        self.playwright_page.goto(url)
        self.last_request_time = time.time()
        content = self.playwright_page.content()
        if content is None:
            raise Exception("went to page and content was None")
        print(f"content: {len(content)} characters")
        return content

    def get_csv_with_playwright(self, url):
        print(f"get_csv_with_playwright({url})")
        with self.playwright_page.expect_download() as download_info:
            #If we navigate without try, it will throw an exception and it will stop our script, so, we wrap it inside a try except block
            try:
                self.playwright_page.goto(url)
            except Exception as e:
                # Check if it's the specific "Download is starting" error
                if "Download is starting" not in str(e):
                    raise e
            download = download_info.value
            temp_file = os.path.join(TMP_PATH, download.suggested_filename)
            download.save_as(temp_file)
            with open(temp_file, "r") as f:
                return f.read()

    def get(self, url, use_playwright=True):
        if use_playwright:
            return self.get_with_playwright(url)
        else:
            if self.requests_session is None:
                self.requests_session = get_requests_session()
            return self.requests_session.get(url).text

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
    print("Logging in with username and password - ideally we only do this once.")
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
    print(f"going to retrieve {url}")
    if cache_path:
        cache_filename = f"{cache_path}/{url[30:]}"
        try:
            with open(cache_filename, "r") as file:
                text = file.read()
                print(f"Loaded {cache_filename} from disk, {len(text)} characters")
                return text
        except FileNotFoundError:
            print(f"Cache not found at {cache_filename}, retrieving from web")
    if session is None:
        session = get_session()

    text = session.get(url)
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
    if session is None:
        session = get_session()
    text = get_page_text(url, session, cache_path)
    parser1 = parser
    parser1.feed(text)
    return parser1.result
