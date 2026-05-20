from abc import ABC, abstractmethod
from typing import Any
import sys

class Zone:
    def __init__(self, name: str, coordinates: tuple, meta_data: dict = {}) -> None:
        self.name: str = name
        self.coordinates: tuple(int, int) = coordinates
        self.meta_data : dict[str, str | int] = meta_data


class Graph:
    ...
