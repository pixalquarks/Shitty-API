from typing import List
from dataclasses import dataclass, field
from copy import deepcopy


def get_next_index():
    idx = 1
    while True:
        yield idx
        idx += 1


index = get_next_index()


@dataclass
class Todo:
    """
    Todo entity class
    """

    id: int = field(default=next(index), init=False)
    todo: str
    done: bool = False


class Database:
    """
    Database Wrapper Classs
    """

    def __init__(self) -> None:
        self.__data: List[Todo] = []

    def get_all(self):
        """
        Get All Items
        """
        return deepcopy(self.__data)

    def get_by_id(self, id: int):
        return deepcopy(next(filter(lambda x: x.id == id, self.__data), None))

    def save(self, todo: Todo):
        todo.id = next(index)
        self.__data.append(todo)
        return todo

    def update(self, update: Todo):
        todo = next(filter(lambda x: x.id == update.id, self.__data), None)
        todo.todo = update.todo
        todo.done = update.done
        return deepcopy(todo)

    def delete(self, id: int):
        todo = self.get_by_id(id)
        if not todo:
            return
        self.__data.remove(todo)
