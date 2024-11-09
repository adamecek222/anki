#!/usr/bin/python3

import pygame as pg
from Pinguin import Pingu, Gender
from typing import List, Tuple
import math
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


BACKGROUND_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
TEXT_COLOR = (0, 0, 0)

PINGU_SIZE = 50


class VisTreeNode:
    def __init__(self, pingu: Pingu, level):
        self.level = level
        self.offset = -1
        self.pingu = pingu

    def getPos(self, screenW, screenH, treeH):
        layerHeight = screenH // (1 + treeH)
        yPos = layerHeight * (1 + self.level)
        xPos = screenW * self.offset
        return (xPos, yPos)


class VisTree:
    def __init__(self, king: Pingu):
        self.nodes: List[VisTreeNode] = []
        self.edges: List[Tuple[VisTreeNode]] = []
        self.width = -1
        self.height = -1
        self.__createNodesAndEdges(king)
        self.__fillOffsets()

    def __createNodesAndEdges(self, king: Pingu):
        q = []
        q.append((king, None))
        visited = set()
        while len(q) > 0:
            act, parent = q.pop(0)
            if act.getName() in visited:
                self.edges.append(
                    (parent, [x for x in self.nodes if x.pingu.getName() == act.getName()][0]))
                continue
            visited.add(act.getName())
            actNode = VisTreeNode(
                act, 0 if parent is None else parent.level + 1)
            if parent is not None:
                self.edges.append((parent, actNode))
            self.nodes.append(actNode)
            for child in act.getChildren():
                q.append((child, actNode))

    def __fillOffsets(self):
        widths = {}
        for node in self.nodes:
            self.height = max(self.height, node.level + 1)
            if node.level not in widths:
                widths[node.level] = 0
            widths[node.level] += 1
        used = {}
        for node in self.nodes:
            if node.level not in used:
                used[node.level] = 0
            used[node.level] += 1
            node.offset = used[node.level] / (widths[node.level] + 1)

        for w in widths.values():
            self.width = max(self.width, 1 + w)


class Visualization:
    def __init__(self, killedOrder: List[str], king: Pingu, kingsOrder: List[str]):
        self.__killedOrder = killedOrder
        self.__nextKill = 0
        self.__tree = VisTree(king)
        self.__screen_width = -1
        self.__screen_height = -1
        self.__image_library = {}
        self.__screen = None
        self.__kingsOrder = kingsOrder

    def __pygame_init(self):
        pg.init()
        infoObject = pg.display.Info()
        self.__screen_width, self.__screen_height = (
            infoObject.current_w, infoObject.current_h)
        self.__screen_height = int(0.8 * self.__screen_height)
        self.__screen_width = int(0.8 * self.__screen_width)
        pg.display.set_caption("KSI Monarchie")
        self.__screen = pg.display.set_mode(
            (self.__screen_width, self.__screen_height))

    def __draw_text(self, text, size, position, color):
        font = pg.font.Font(pg.font.match_font('Droid Sans Mono'), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (position[0], position[1] - 20)
        self.__screen.blit(text_surface, text_rect)

    def __get_image(self, path, size):
        image = self.__image_library.get(path)
        if image is None:
            canonicalized_path = path.replace(
                '/', os.sep).replace('\\', os.sep)
            image = pg.image.load(canonicalized_path)
            image = pg.transform.scale(image, size)
            self.__image_library[path] = image
        return image

    def __isKing(self, pingu):
        killed = self.__killedOrder[:self.__nextKill]
        try:
            kingName = [x for x in self.__kingsOrder if not x in killed][0]
        except:
            kingName = ""
        return kingName == pingu.getName()

    def __recalculateArrowEndPos(self, start, end):
        dist = math.sqrt((start[0] - end[0])**2 + (start[1] - end[1]) ** 2)
        ratio = 2 * PINGU_SIZE / (3 * dist)
        newEndX = end[0] + (start[0] - end[0]) * ratio
        newEndY = end[1] + (start[1] - end[1]) * ratio
        return (newEndX, newEndY)

    def __draw_arrow(self, start, end):
        rad = math.pi / 180
        end = self.__recalculateArrowEndPos(start, end)
        trirad = 8
        pg.draw.line(self.__screen, LINE_COLOR, start, end, 2)
        rotation = (math.atan2(start[1] - end[1],
                               end[0] - start[0])) + math.pi/2
        pg.draw.polygon(self.__screen, LINE_COLOR, ((end[0] + trirad * math.sin(rotation),
                                                     end[1] + trirad * math.cos(rotation)),
                                                    (end[0] + trirad * math.sin(rotation - 120*rad),
                                                     end[1] + trirad * math.cos(rotation - 120*rad)),
                                                    (end[0] + trirad * math.sin(rotation + 120*rad),
                                                     end[1] + trirad * math.cos(rotation + 120*rad))))

    def __draw_penguin(self, pingu: Pingu, pos: Tuple[int]):
        path = ""
        if self.__isKing(pingu):
            path = "img/king_karlik.png" if pingu.getName() == "Karlík Veliký" else "img/king.png"
        elif pingu.getGender() == Gender.MALE:
            path = "img/karlik.png" if pingu.getName() == "Karlík Veliký" else "img/male.png"
            if self.__is_killed(pingu.getName()):
                path = "img/male_killed.png"
        else:
            path = "img/female.png"
            if self.__is_killed(pingu.getName()):
                path = "img/female_killed.png"
        self.__screen.blit(self.__get_image(
            path, (PINGU_SIZE, PINGU_SIZE)), pos)

    def __drawTree(self):
        for edge in self.__tree.edges:
            xStartPos, yStartPos = edge[0].getPos(
                self.__screen_width, self.__screen_height, self.__tree.height)
            xEndPos, yEndPos = edge[1].getPos(
                self.__screen_width, self.__screen_height, self.__tree.height)
            self.__draw_arrow((xStartPos, yStartPos), (xEndPos, yEndPos))
        for node in self.__tree.nodes:
            xPos, yPos = node.getPos(
                self.__screen_width, self.__screen_height, self.__tree.height)
            self.__draw_penguin(
                node.pingu, (xPos - PINGU_SIZE // 2, yPos - PINGU_SIZE // 2))
            self.__draw_text(str(node.pingu.getAge()),
                             32, (xPos, yPos + PINGU_SIZE), TEXT_COLOR)

    def __draw(self):
        self.__screen.fill(BACKGROUND_COLOR)
        self.__drawTree()

    def __is_killed(self, name):
        killed = self.__killedOrder[:self.__nextKill]
        return name in killed

    def run(self):
        self.__pygame_init()
        exit = False
        self.__draw()
        while not exit:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit = True
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE or event.key == pg.K_RIGHT:
                        self.__nextKill += 1
                        if self.__nextKill > len(self.__killedOrder):
                            self.__nextKill = len(self.__killedOrder)
                        self.__draw()
                    elif event.key == pg.K_LEFT:
                        self.__nextKill -= 1
                        if self.__nextKill < 0:
                            self.__nextKill = 0
                        self.__draw()
            pg.display.flip()
