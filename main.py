#!/usr/bin/python3
# -*- coding: utf-8 -*-

# build-in modules:
from time import time
from os import getpid, getenv, chdir
from os.path import isdir
from random import Random
from pathlib import Path

# pip modules:
from requests import post, Response
from rich.traceback import install
from rich import print
from rich.console import Console


class RandomNameSequence:
    characters = "abcdefghijklmnopqrstuvwxyz0123456789-"

    @property
    def rng(self):
        cur_pid = getpid()
        if cur_pid != getattr(self, '_rng_pid', None):
            self._rng = Random()
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def __next__(self):
        return ''.join(self.rng.choices(self.characters, k=8))


class WrongStatusCode(Exception):
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def __str__(self) -> str:
        return f"Wrong status code: {self.status_code}"


def get_timestamp(timestamp: int = None):
    if not timestamp:
        return round(time() * 1000)
    return timestamp


class LevelOSAPI():
    def __init__(self, username: str = None, password: str = None, URL: str = "https://os.leveloper.cc") -> str:
        self.URL = URL

        if not (username is None or password is None):
            self.login(username, password)

        self.level_cloud = LevelCloud(self)
        self.lstore = lStore(self)

    def post(self, endpoint: str, data: dict = None) -> Response:
        response = post(
            url=f"{self.URL}/{endpoint}",
            data=data,
            headers={
                "Cookie": self.userID
            }
        )

        if response.status_code != 200:
            raise WrongStatusCode(response.status_code)

        try:
            if int(response.text) != 200:
                raise WrongStatusCode(response.text)
        except ValueError:
            pass

        return response

    def login(self, username: str, password: str) -> Response:
        response = post(
            url=f"{self.URL}/auth.php",
            data={
                "username": username,
                "password": password
            }
        )

        if response.status_code != 200:
            raise WrongStatusCode(response.status_code)

        try:
            if int(response.text) != 200:
                raise WrongStatusCode(response.text)
        except ValueError:
            pass

        self.userID = response.headers["Set-Cookie"]

        return response


class LevelCloud():
    def __init__(self, levelos_api: LevelOSAPI) -> None:
        self.__levelos_api = levelos_api

    def upload(self, path: str, content: str, timestamp: int = None) -> Response:
        return self.__levelos_api.post(
            endpoint="cUpload.php",
            data={
                "path": path,
                "content": content,
                "timestamp": get_timestamp(timestamp)
            }
        )

    def mkdir(self, path: str) -> Response:
        return self.__levelos_api.post(
            endpoint="cMkDir.php",
            data={
                "path": path
            }
        )

    def delete(self, path: str) -> Response:
        return self.__levelos_api.post(
            endpoint="cDelete.php",
            data={
                "path": path
            }
        )


class Listings():
    PUBLIC = "public"
    UNLISTED = "unlisted"


class lStore():
    def __init__(self, levelos_api: LevelOSAPI) -> None:
        self.__levelos_api = levelos_api

    def put(self, title: str, path: str, listing: Listings = Listings.PUBLIC, timestamp: int = None) -> Response:
        return self.__levelos_api.post(
            endpoint="sProject.php",
            data={
                "title": title,
                "path": path,
                "timestamp": get_timestamp(timestamp),
                "listing": listing
            }
        )


def main():
    title = getenv("INPUT_TITLE")

    print("[bright_green]Logging in [bright_yellow]...")
    levelos_api = LevelOSAPI(
        username=getenv("INPUT_USERNAME"),
        password=getenv("INPUT_PASSWORD")
    )

    temp_fodler = f"temp-{next(RandomNameSequence())}"

    print(
        f"[bright_green]Creating Temporay Folder ([bright_magenta]{temp_fodler}[bright_green]) [bright_yellow]...")
    levelos_api.level_cloud.mkdir(temp_fodler)

    data_folder = getenv("INPUT_PATH")
    chdir(data_folder)

    for path in Path(".").rglob('*'):
        if isdir(path):
            print(
                f"[bright_green]Creating folder ([bright_magenta]{temp_fodler}/{path}[bright_green]) [bright_yellow]...")
            levelos_api.level_cloud.mkdir(f"{temp_fodler}/{path}")
        else:
            with open(path, "r") as file:
                print(
                    f"[bright_green]Uploading ([bright_magenta]{temp_fodler}/{path}[bright_green]) [bright_yellow]...")
                content = file.read()
                levelos_api.level_cloud.upload(
                    f"{temp_fodler}/{path}",
                    content=content
                )
                file.close()

    print(f"[bright_green]Uploading package to LStore [bright_yellow]...")
    response = levelos_api.lstore.put(title, temp_fodler)

    print("[bright_green]Uploaded as [bright_blue]" + response.text)
    print(
        "[bright_green]Run \"[white]lStore get " + title +
        "\"[bright_green] or \"[white]lStore get " + response.text +
        "\"[bright_green] to download anywhere"
    )

    print("[bright_green]Clean Up [bright_yellow]...")
    levelos_api.level_cloud.delete(temp_fodler)


if __name__ == "__main__":
    install(console=Console(force_terminal=True))
    main()
