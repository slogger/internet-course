#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import urllib.request as urllib
import urllib.parse as urlparse
import http.cookiejar
from html.parser import HTMLParser

class FormParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.url = None
        self.params = {}
        self.in_form = False
        self.form_parsed = False
        self.method = "GET"

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "form":
            if self.form_parsed:
                raise RuntimeError("Second form on page")
            if self.in_form:
                raise RuntimeError("Already in form")
            self.in_form = True
        if not self.in_form:
            return
        attrs = dict((name.lower(), value) for name, value in attrs)
        if tag == "form":
            self.url = attrs["action"]
            if "method" in attrs:
                self.method = attrs["method"].upper()
        elif tag == "input" and "type" in attrs and "name" in attrs:
            if attrs["type"] in ["hidden", "text", "password"]:
                self.params[attrs["name"]] = attrs["value"] if "value" in attrs else ""

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "form":
            if not self.in_form:
                raise RuntimeError("Unexpected end of <form>")
            self.in_form = False
            self.form_parsed = True

def auth(email, password, client_id, scope):
    def split_key_value(kv_pair):
        kv = kv_pair.split("=")
        return kv[0], kv[1]

    def auth_user(email, password, client_id, scope, opener):
        url_base = "http://oauth.vk.com/oauth/authorize"
        url_redirect = "?redirect_uri=http://oauth.vk.com/blank.html"
        response_type = "&response_type=token"
        url = url_base + url_redirect+ response_type
        response = opener.open(
            url + "&client_id={}&scope={}&display=wap".format(
                client_id, ",".join(scope))
            )
        doc = response.read()
        parser = FormParser()
        parser.feed(str(doc))
        parser.close()
        if not parser.form_parsed or parser.url is None or "pass" not in parser.params or \
          "email" not in parser.params:
              raise RuntimeError("Something go wrong")
        parser.params["email"] = email
        parser.params["pass"] = password
        if parser.method == "POST":
            response = opener.open(parser.url, bytes(urlparse.urlencode(parser.params), 'utf8'))
        else:
            raise NotImplementedError("Method '{}''".format(parser.method))
        return response.read(), response.geturl()

    def give_access(doc, opener):
        parser = FormParser()
        parser.feed(doc)
        parser.close()
        if not parser.form_parsed or parser.url is None:
              raise RuntimeError("Something wrong")
        if parser.method == "POST":
            response = opener.open(parser.url, urllib.urlencode(parser.params))
        else:
            raise NotImplementedError("Method '{}'".format(parser.method))
        return response.geturl()

    if not isinstance(scope, list):
        scope = [scope]

    opener = urllib.build_opener(
        urllib.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    doc, url = auth_user(email, password, client_id, scope, opener)

    if urlparse.urlparse(url).path != "/blank.html":
        url = give_access(doc, opener)
    if urlparse.urlparse(url).path != "/blank.html":
        raise RuntimeError("Expected success here")
    answer = dict(split_key_value(kv_pair) for kv_pair in urlparse.urlparse(url).fragment.split("&"))
    if "access_token" not in answer or "user_id" not in answer:
        raise RuntimeError("Missing some values in answer")
    return answer["access_token"], answer["user_id"]
