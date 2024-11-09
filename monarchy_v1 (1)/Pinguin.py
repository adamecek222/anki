#!/usr/bin/python3

from typing import List, Callable
from enum import Enum


class Gender(Enum):
    MALE = 0
    FEMALE = 1

    @staticmethod
    def parse(label: str) -> 'Gender':
        if label.lower() == "male":
            return Gender.MALE
        elif label.lower() == "female":
            return Gender.FEMALE
        raise ValueError("MALE or FEMALE expected")

    @staticmethod
    def to_string(gender: 'Gender') -> str:
        return "MALE" if gender == Gender.MALE else "FEMALE"


class Pingu:
    def __init__(self, name: str, gender: Gender, age: int, children: List['Pingu'], kill: Callable[[], None]):
        self._children = children
        self.__age = age
        self.__name = name
        self.__gender = gender
        self.__kill = kill

    def getName(self: 'Pingu') -> str:
        return self.__name

    def getGender(self: 'Pingu') -> Gender:
        return self.__gender

    def getAge(self: 'Pingu') -> int:
        return self.__age

    def getChildren(self: 'Pingu') -> List['Pingu']:
        return self._children

    def kill(self: 'Pingu'):
        self.__kill(self)
