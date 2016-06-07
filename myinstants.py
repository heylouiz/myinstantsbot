#!/bin/env python

"""
    Module that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import re
import sys

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.myinstants.com/{}"
SEARCH_URL = "search/?name={}"

MP3_MATCH = re.compile(r"play\('(.*?)'\)")

def search_instants(query):
    """Search instant
       Params:
           query: String to search
    """
    query_string = "+".join(query) if isinstance(query, list) else query.replace(" ", "+")
    url = BASE_URL.format(SEARCH_URL.format(query_string))

    req = requests.get(url)

    if req.status_code != 200:
        return {}

    soup = BeautifulSoup(req.text, "html.parser")
    response = []
    for div_obj in soup.find_all("div", class_="instant"):
        text = div_obj.find("a", attrs={"style": "text-decoration: underline;"}).string
        mp3 = MP3_MATCH.search(div_obj.find("div", class_="small-button")["onclick"]).group(1)
        url = BASE_URL.format(mp3)
        response.append({"text": text,
                         "url": url})

    return response

def main():
    """Main function"""
    try:
        response = search_instants(sys.argv[1:])
    except requests.exceptions.Timeout:
        print("Timeout")
        response = []

    print(response)

if __name__ == "__main__":
    main()

