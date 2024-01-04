from http import HTTPStatus
import json
import socket
from pprint import pprint
from dataclasses import asdict
from wrapper import RequestObject, ResponseObject, Message
from router import Route, Router
from db.db import Database, Todo

HOST = ""
PORT = 8000

message = "HTTP/1.1 200 OK\r\n\r\n{response}\r\n\r\n"


def parse_header(socket_stream: socket):
    headers = {}
    start_line = []
    while True:
        d = socket_stream.recv(1)
        start_line.append(d.decode())
        if start_line[-1] == "\n":
            break
    start_line = "".join(start_line)
    request_line = start_line.strip().split()
    headers["method"] = request_line[0]
    headers["uri"] = request_line[1]
    headers["protocol"] = request_line[2]

    while True:
        header_line = []
        while True:
            d = socket_stream.recv(1)
            header_line.append(d.decode())
            if header_line[-1] == "\n":
                break
        if not header_line or len(header_line) == 2:
            break
        header_line_str = "".join(header_line).strip()
        split_idx = header_line_str.index(":")
        key, value = header_line_str[:split_idx], header_line_str[split_idx + 1 :]
        headers[key] = value.strip()
    return headers


database = Database()


def home_route(req: RequestObject, res: ResponseObject):
    resp = Message("Hello, World!")
    res.set_json_response(asdict(resp))


def get_all_todos(req: RequestObject, res: ResponseObject):
    res.set_json_response([asdict(todo) for todo in database.get_all()])


def get_todo(req: RequestObject, res: ResponseObject):
    id = req.path_variables.get("id", None)
    id = int(id)

    todo = database.get_by_id(id)

    if todo == None:
        resp = Message(f"No todo found with id: {id}")
        res.set_json_response(asdict(resp))
        res.status = HTTPStatus.NOT_FOUND
        return

    res.set_json_response(asdict(todo))


def create_todo(req: RequestObject, res: ResponseObject):
    body = req.body
    if not body:
        resp = Message("No todo provided")
        res.set_json_response(asdict(resp))
        res.status = HTTPStatus.BAD_REQUEST
        return
    todo_data = json.loads(body)
    todo = Todo(**todo_data)
    todo = database.save(todo)
    res.set_json_response(asdict(todo))
    res.status = HTTPStatus.CREATED


def delete_todo(req: RequestObject, res: ResponseObject):
    id = req.path_variables["id"]
    id = int(id)
    database.delete(id)
    res.status = HTTPStatus.NO_CONTENT


def toggle_todo(req: RequestObject, res: ResponseObject):
    id = req.path_variables["id"]
    id = int(id)
    todo = database.get_by_id(id)
    if todo == None:
        resp = Message(f"No todo found with id: {id}")
        res.set_json_response(asdict(resp))
        res.status = HTTPStatus.NOT_FOUND
        return

    todo.done = not todo.done
    todo = database.update(todo)
    res.set_json_response(asdict(todo))


default_headers = {"Content-Type": "application/json", "Server": "ShittyAPI"}


router = Router(default_headers)
router.add_route(Route("GET", "/", home_route))
router.add_route(Route("GET", "/todos/<id:int>", get_todo))
router.add_route(Route("GET", "/todos", get_all_todos))
router.add_route(Route("POST", "/todos", create_todo))
router.add_route(Route("DELETE", "/todos/<id:int>", delete_todo))
router.add_route(Route("POST", "/todos/<id:int>", toggle_todo))


def start():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.settimeout(0.5)
        s.listen()
        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    print("Device connected: ", addr)
                    headers = parse_header(conn)
                    print("headers:")
                    pprint(headers)
                    body = ""
                    if headers["method"] in ["POST", "PUT"]:
                        l = int(headers.get("Content-Length", 0))
                        if l > 0:
                            body_raw = conn.recv(l)
                            body = body_raw.decode()
                    request_object = RequestObject(headers, body)
                    response = ResponseObject(headers)
                    router.route_request(request_object, response)
                    conn.sendall(response.format_response().encode())
                    conn.close()
            except socket.timeout:
                continue
            except IOError as err:
                print(err)
                continue
            except KeyboardInterrupt as _:
                print("Closing the server")
                break


print("Starting server")
start()
