#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import vk_auth
import json
import urllib.request as urllib
from urllib.parse import urlencode
import os
import getpass
import sys

def call_api(method, params, token):
    params.append(("access_token", token))
    url = "https://api.vk.com/method/{}?{}".format(method, urlencode(params))
    res = urllib.urlopen(url).read().decode('utf-8')
    return json.loads(str(res))["response"]

def get_albums(user_id, token):
    return call_api("photos.getAlbums", [("uid", user_id)], token)

def get_photos_urls(user_id, album_id, token):
    photos_list = call_api("photos.get", [("uid", user_id), ("aid", album_id)], token)
    result = []
    for photo in photos_list:
        if "src_xxbig" in photo:
            url = photo["src_xxbig"]
        elif "src_xbig" in photo:
            url = photo["src_xbig"]
        elif "src_big" in photo:
            url = photo["src_big"]
        else:
            url = photo["src"]
        result.append(url)
    return result

def save_photos(urls, directory):
    if not os.path.exists(directory):
        os.mkdir(directory)
    names_pattern = "%%0%dd.jpg" % len(str(len(urls)))
    for num, url in enumerate(urls):
        filename = os.path.join(directory, names_pattern % (num + 1))
        print("Downloading {}".format(filename))
        open(filename, "wb").write(urllib.urlopen(url).read())

def main():
    # directory = None
    email = input("Login: ")
    password = getpass.getpass()
    client_id = "4906664"
    token, user_id = vk_auth.auth(email, password, client_id, "photos")
    albums = get_albums(user_id, token)
    print("\n".join("{}. {}".format(num, album["title"]) for num, album in enumerate(albums)))
    choice = -1
    while choice not in range(len(albums)):
        choice = int(input("Choose album number: "))

    if len(sys.argv) == 2:
        directory = sys.argv[1]
    else:
        directory = albums[choice]["title"]

    photos_urls = get_photos_urls(user_id, albums[choice]["aid"], token)
    save_photos(photos_urls, directory)

if __name__ == '__main__':
    main()
