import re
from typing import List
from datetime import datetime
from wrapper import RequestObject, ResponseObject


class Route:
    def __init__(self, method: str, route_str, function):
        self.method: str = method
        self.route_str: str = route_str
        self.function = function
        self.static = True
        self.keys = []
        self.__replace_regex()

    def match(self, method: str, uri: str):
        return method == self.method and self.uri.fullmatch(uri)

    def __replace_regex(self):
        t = self.route_str.split("/")
        res = []
        static = True
        keys = []
        for i, w in enumerate(t):
            if not w.startswith("<"):
                res.append(w)
                continue
            static = False
            x = w[1:-1]
            key, type = x.split(":")
            if type == "int":
                res.append("\\d+")
            else:
                res.append("\\w+")
            keys.append((i, key))
        self.static = static
        self.keys = keys
        uri = "\\/".join(res)
        print("original: ", self.route_str)
        print("uri: ", uri)
        self.uri = re.compile(uri)

    def parse_path_variables(self, uri):
        t = uri.split("/")
        path_variables = {}
        for i, key in self.keys:
            path_variables[key] = t[i]
        return path_variables


class Router:
    def __init__(self, default_header={}):
        self.routes: List[Route] = []
        self.all_route_headers = default_header
        self.__datetime_format = "%a, %d %b %Y %H:%M:%S %Z"

    def add_route(self, route: Route):
        self.routes.append(route)

    def route_request(self, req: RequestObject, resp: ResponseObject):
        for route in self.routes:
            if route.match(req.method, req.uri):
                for key, value in self.all_route_headers.items():
                    resp.set_header(key, value)
                if not route.static:
                    req.path_variables = route.parse_path_variables(req.uri)
                route.function(req, resp)
                resp.set_header("Date", datetime.now().strftime(self.__datetime_format))
                return resp
