#!/bin/env python

"""
    Module that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import re
import sys

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from bs4 import BeautifulSoup
import os

BASE_URL = "https://www.myinstants.com/{}"
SEARCH_URL = "search/?name={}"
UPLOAD_URL = 'https://www.myinstants.com/new/'

MP3_MATCH = re.compile(r"play\('(.*?)'\)")

class MyInstantsApiException(Exception):
    """General exception for myinstants api"""
    pass

class HTTPErrorException(MyInstantsApiException):
    """HTTP error exception for myinstants api"""
    pass

class NameAlreadyExistsException(MyInstantsApiException):
    """"Exception throw when an instants name already exists"""
    pass

class FileSizeException(MyInstantsApiException):
    """Exception throw when the instants file size is bigger than supported"""
    pass

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
        text = div_obj.find("a", attrs={"style": "text-decoration: underline; font-size: 14px;"}).string
        mp3 = MP3_MATCH.search(div_obj.find("div", class_="small-button")["onmousedown"]).group(1)
        url = BASE_URL.format(mp3)
        response.append({"text": text,
                         "url": url})

    return response

def upload_instant(name, filepath):
    """Upload sound for Myinstants
        Params:
            name: Name of the instants to be uploaded
            filepath: Path of the sound file to be uploaded
    """
    client = requests.session()

    r = client.get(UPLOAD_URL)

    token = client.cookies['csrftoken']

    cookies = dict(csrftoken=token)

    filename = os.path.basename(filepath)

    multipart_data = MultipartEncoder(fields={'csrfmiddlewaretoken': token,
                                              'name': name,
                                              'sound': (filename, open(filepath, 'rb'), 'audio/mpeg'),
                                              'image': ('', None, ''),
                                              'color': '00FF00',
                                              'description': ''})

    response = requests.post(UPLOAD_URL, data=multipart_data, cookies=cookies,
                             headers={'Content-Type': multipart_data.content_type,
                             'Referer': UPLOAD_URL})

    soup = BeautifulSoup(response.text, "html.parser")
    for ul_obj in soup.find_all("ul", class_="errorlist"):
        if ul_obj.text.lower().find("instant with this name already exists.") >= 0:
            raise NameAlreadyExistsException
        if ul_obj.text.lower().find("please keep filesize under 300.0 kb") >= 0:
            raise FileSizeException
    if response.status_code != 200:
        raise HTTPErrorException

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

