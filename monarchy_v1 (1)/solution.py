#!/usr/bin/python3

from Pinguin import Gender, Pingu

TARGET_PENGUIN = "Karlík Veliký"


def killPenguins(king: Pingu):
   # TODO your solution here
   pass


# Primitive example algorithm that kills only the king and his first son
# def killPenguins(king: Pingu):
#     king.kill()
#     oldestAge = -1
#     pingu = None
#     for p in king.getChildren():
#         if p.getGender() == Gender.MALE and p.getAge() > oldestAge:
#             pingu = p
#             oldestAge = p.getAge()
#     if pingu is not None:
#         pingu.kill()
