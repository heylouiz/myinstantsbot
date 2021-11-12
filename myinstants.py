#!/bin/env python

"""
    Module that search sounds in www.myinstants.com
    Author: Luiz Francisco Rodrigues da Silva <luizfrdasilva@gmail.com>
"""

import os
import re
import sys
from urllib.parse import urljoin

import parsel
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from user_agent import generate_user_agent

SEARCH_URL = "https://www.myinstants.com/search/?name={}"
MEDIA_URL = "https://www.myinstants.com{}"
UPLOAD_URL = "https://www.myinstants.com/new/"
LOGIN_URL = "https://www.myinstants.com/accounts/login/"


class MyInstantsApiException(Exception):
    """General exception for myinstants api"""

    pass


class HTTPErrorException(MyInstantsApiException):
    """HTTP error exception for myinstants api"""

    pass


class NameAlreadyExistsException(MyInstantsApiException):
    """ "Exception throw when an instants name already exists"""

    pass


class FileSizeException(MyInstantsApiException):
    """Exception throw when the instants file size is bigger than supported"""

    pass


class LoginErrorException(MyInstantsApiException):
    """Exception thrown when the login failed"""

    pass


class InvalidPageErrorException(MyInstantsApiException):
    """Exception thrown when an invalid page is downloaded"""

    pass


def search_instants(query):
    """Search instant
    Params:
        query: String to search
    """
    query_string = (
        "+".join(query) if isinstance(query, list) else query.replace(" ", "+")
    )
    response = requests.get(
        SEARCH_URL.format(query_string),
        headers={
            "User-Agent": generate_user_agent(),
        },
    )

    if response.status_code != 200:
        return {}

    sel = parsel.Selector(response.text)
    names = sel.css(".instant .instant-link::text").getall()
    links = map(
        MEDIA_URL.format,
        sel.css(".instant .small-button::attr(onmousedown)").re("play\('(.*)'\)"),
    )
    return [
        {
            "text": text,
            "url": url,
        }
        for text, url in zip(names, links)
    ]


def upload_instant(name, filepath):
    """Upload sound for Myinstants
    Params:
        name: Name of the instants to be uploaded
        filepath: Path of the sound file to be uploaded
    """

    # Create session and get cookies
    session = requests.session()
    response = session.get(
        LOGIN_URL,
        headers={
            "User-Agent": generate_user_agent(),
        },
    )

    sel = parsel.Selector(response.text)
    token = sel.css("input[name=csrfmiddlewaretoken]::attr(value)").get()

    if not token:
        raise InvalidPageErrorException

    data = {
        "csrfmiddlewaretoken": token,
        "login": os.environ["MYINSTANTS_USERNAME"],
        "password": os.environ["MYINSTANTS_PASSWORD"],
        "next": "/new/",
    }

    # Login
    response = session.post(
        LOGIN_URL,
        data=data,
        headers={
            "User-Agent": generate_user_agent(),
        },
    )

    if response.status_code != 200:
        raise LoginErrorException

    # Get upload token
    sel = parsel.Selector(response.text)
    token = sel.css("input[name=csrfmiddlewaretoken]::attr(value)").get()

    if not token:
        raise InvalidPageErrorException

    filename = os.path.basename(filepath)

    multipart_data = MultipartEncoder(
        fields={
            "csrfmiddlewaretoken": token,
            "name": name,
            "sound": (
                filename,
                open(filepath, "rb"),
                "audio/mpeg",
            ),
            "image": ("", None, ""),
            "color": "00FF00",
            "category": "",
            "description": "",
            "tags": "",
            "accept_terms": "on",
        }
    )

    # Upload sound
    response = session.post(
        UPLOAD_URL,
        data=multipart_data,
        headers={
            "Content-Type": multipart_data.content_type,
            "Referer": UPLOAD_URL,
            "User-Agent": generate_user_agent(),
        },
    )

    sel = parsel.Selector(response.text)
    errors = "\n".join(sel.css("ul.errorlist").getall())
    if "instant with this name already exists." in errors:
        raise NameAlreadyExistsException
    if "please keep filesize under 300.0 kb" in errors:
        raise FileSizeException
    if response.status_code != 200:
        raise HTTPErrorException

    last_uploaded_element = sel.xpath(
        "//a[contains(@class, 'instant-link') and text()=$name]/@href", name=name
    ).get()
    if not last_uploaded_element:
        return response.url

    # Return sound url
    return urljoin(response.url, last_uploaded_element)


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
