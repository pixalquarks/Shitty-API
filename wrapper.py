from http import HTTPStatus
import json
from dataclasses import dataclass


class RequestObject:
    def __init__(self, headers, body):
        self.method = headers["method"]
        self.uri = headers["uri"]
        self.headers = headers
        self.body = body
        self.path_variables = {}


class ResponseObject:
    def __init__(self, headers):
        self.__protocol = headers["protocol"]
        self.status = HTTPStatus.OK
        self.__headers = {}

    def set_response(self, body):
        self.body = body
        self.set_header("Content-Length", len(self.body))

    def set_json_response(self, body: dict):
        self.body = json.dumps(body)
        self.set_header("Content-Length", len(self.body))

    def set_header(self, key, value):
        self.__headers[key] = value

    def format_response(self):
        res = [f"{self.__protocol} {self.status.value} {self.status.phrase}\r\n"]
        for header, value in self.__headers.items():
            res.append(f"{header}: {value}\r\n")
        res.append("\r\n")
        if self.body:
            res.append(self.body)
        return "".join(res)


@dataclass
class Message:
    message: str
