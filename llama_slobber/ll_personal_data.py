#!/usr/bin/python
# Copyright (c) 2018 Warren Usui, MIT License
# pylint: disable=W0223
"""
Function used to find personal info.
"""
from html.parser import HTMLParser

from llama_slobber.ll_local_io import get_session
from llama_slobber.ll_local_io import get_page_data
from llama_slobber.ll_local_io import LLHEADER
from llama_slobber.handle_conn_err import handle_conn_err


class GetPersonalInfo(HTMLParser):
    """
    Parse profile page.
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.current_attr = None
        self.entering_demolabel = False
        self.result = {}

    def handle_starttag(self, tag, attrs):
        """
        Find personal data
        """
        if tag == 'span':
            for apt in attrs:
                if apt[0] == 'class':
                    if apt[1].startswith('demolabel'):
                        self.entering_demolabel = True

    def handle_data(self, data):
        if self.entering_demolabel:
            attr_name = data.strip().strip(':')
            if attr_name in ["Gender", "Location", "College"]:
                self.current_attr = attr_name
            self.entering_demolabel = False
            return
        if self.current_attr and data != ":":
            self.result[self.current_attr] = data.strip()
            self.current_attr = None
            return

    def handle_endtag(self, tag):
        if tag == 'p':
            self.parsetext = False


@handle_conn_err
def get_personal_data(person, session=None):
    """
    Get information on a person

    Input:
        person -- LL id.
        session request

    Returns: dictionary of user's metadata (Location, Gender, College)
    """
    if session is None:
        session = get_session()
    page = "%s/profiles.php?%s" % (LLHEADER, person.lower())
    return get_page_data(page, GetPersonalInfo(), session=session)


if __name__ == "__main__":
    print(get_personal_data('ConryM_Illuminati=REAL?'))
    print(get_personal_data('UsuiW'))
