#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# Albert Dinh (CCID: dadinh; student ID: 1642083)

import json
import re
import socket
import sys

# you may use urllib to encode data appropriately
import urllib.parse

DEBUG = False


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    # def get_host_port(self,url):
    # refereneced private members in python through here: https://www.scaler.com/topics/python-private-variables/
    __header = {}
    __socket = None

    def connect(self, host, port):
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data[0].split(" ")[1])

    def get_headers(self, data):
        return data.split("\r\n")

    def get_body(self, data):
        return data[-1]

    def sendall(self, data):
        self.__socket.sendall(data.encode("utf-8"))

    def close(self):
        self.__socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if part:
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode("utf-8")

    def GET(self, url, args=None):
        code = 500
        body = ""
        # referenced urllib.parse from here: https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        if path == "":
            path = "/"
        host = parsed_url.hostname
        port = parsed_url.port
        if port == None:
            port = 80
        if port == "":
            port = 80
        self.__header["Host"] = host
        self.connect(host, port)
        # learn how to set up some header fields from here: https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        req_str = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        self.sendall(req_str)
        res = self.recvall(self.__socket)
        tokenized_res = self.get_headers(res)
        code = self.get_code(tokenized_res)
        body = self.get_body(tokenized_res)
        print("-" * 50)
        print("GET response is: \n", res)
        print("-" * 50)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        if args:
            # referenced urlencode here: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlencode
            args = urllib.parse.urlencode(args)
        code = 500
        body = ""
        # referenced urllib.parse from here: https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        if path == "":
            path = "/"
        host = parsed_url.hostname
        port = parsed_url.port
        if port == None:
            port = 80
        # learn how to set up some header fields from here: https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        self.__header["Host"] = host
        if args:
            self.__header[
                "Content-Type"
            ] = "application/x-www-form-urlencoded application/json"
            self.__header["Content-Length"] = str(len(str(args)))
        self.__header["Connection"] = "close"
        temp_header = "\r\n".join(
            [
                f"{header_field}: {header_value}"
                for header_field, header_value in self.__header.items()
            ]
        )
        self.connect(host, port)
        if args:
            temp_header += "\r\n\r\n" + args
        # learn how to set up some header fields from here: https://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        req_str = f"POST {path} HTTP/1.1\r\nHost: {host}\r\{temp_header}\r\n\r\n"
        self.sendall(req_str)
        res = self.recvall(self.__socket)
        tokenized_res = self.get_headers(res)
        if len(tokenized_res) > 1:
            body = self.get_body(tokenized_res)
            code = self.get_code(tokenized_res)
        print("-" * 50)
        print("POST response is: \n", res)
        print("-" * 50)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
