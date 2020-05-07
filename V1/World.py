from V1.GameObjects import *
from V1.Actors import *


class World:
    def __init__(self, level=None):
        self.boxes = []
        self.gameObjects = []
        self.actors = []
        self.players = []

    def addGameObject(self, gameObj):
        if isinstance(gameObj, GameObject):
            self.gameObjects.append(gameObj)

    def addActor(self, actor):
        if isinstance(actor, Player):
            self.players.append(actor)
        else:
            self.actors.append(actor)

    def addBox(self, box):
        if isinstance(box, Box):
            self.gameObjects.append(box)
            self.boxes.append(box)