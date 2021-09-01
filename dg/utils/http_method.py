from enum import Enum, auto


class HTTPMethod(Enum):
    DELETE = auto()
    GET = auto()
    HEAD = auto()
    OPTIONS = auto()
    PATCH = auto()
    POST = auto()
    PUT = auto()

    def __str__(self):
        return self.name
