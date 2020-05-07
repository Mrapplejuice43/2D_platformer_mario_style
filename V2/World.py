from V2.GameObjects import *
from V2.Actors import *
from V2.Camera import *


class World:
    def __init__(self, canvasSize, tileSize, gameScale, level=None):
        self.canvasSize = (canvasSize[0], canvasSize[1])
        self.worldOrigin = np.array((0, canvasSize[1]))
        self.tileSize = np.array(tileSize)
        self.scale = gameScale
        self.backgroundColor = (50, 201, 255)
        self.debugMode = False
        self.objects = []
        self.boxes = []
        self.gameObjects = []
        self.actors = []
        self.players = []

    def addGameObject(self, gameObj):
        if isinstance(gameObj, GameObject):
            self.gameObjects.append(gameObj)
            self.objects.append(gameObj)

    def addActor(self, actor):
        if isinstance(actor, Player):
            self.players.append(actor)
            self.objects.append(actor)
        else:
            self.actors.append(actor)
            self.objects.append(actor)

    def addBox(self, box):
        if isinstance(box, Box):
            self.gameObjects.append(box)
            self.boxes.append(box)
            self.objects.append(box)

    def resize(self, windowSize, tileSize):
        for player in self.players:
            player.pos = np.array((player.pos[0] * windowSize[0] // self.canvasSize[0],
                          player.pos[1] * windowSize[1] // self.canvasSize[1]))
            player.startPos = (player.startPos[0] * windowSize[0] // self.canvasSize[0],
                               player.startPos[1] * windowSize[1] // self.canvasSize[1])

        self.worldOrigin = np.array((self.worldOrigin[0],
                                     self.worldOrigin[1] * windowSize[1] // self.canvasSize[1]))
        self.canvasSize = windowSize
        self.tileSize = tileSize

    def readWorld(self, fic):
        f = open(fic, 'r')
        for l in f.readlines():
            # type width height posx posy
            tmp = l.split()
            if len(tmp) == 5:
                if tmp[0] == 'p':
                    self.addGameObject(Plateforme(
                        int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == 'g':
                    self.addGameObject(Ground(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == 'P':
                    self.addActor(Player(float(tmp[1]), float(tmp[2]), (int(tmp[3]), int(tmp[4])) * self.tileSize))
                elif tmp[0] == 'b':
                    self.addBox(Box(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))

    def switchDebugMode(self):
        self.debugMode = not self.debugMode
        for obj in self.objects:
            obj.debugMode = not obj.debugMode

    def calculateDrawingCoordinates(self, obj):
        """
        Calculates coordinates in global geometrical landmark from local origin at the bottom left corner x+ towards left and y+ towards up
        :param obj: the object we calculate the coordinates into global geometric landmark
        """
        if isinstance(obj, Actor):
            return (obj.pos + (0, obj.height) * self.tileSize - self.worldOrigin) * np.array((1, -1))

        elif isinstance(obj, GameObject):
            return ((obj.pos + (0, obj.height)) * self.tileSize - self.worldOrigin) * np.array((1, -1))

        elif isinstance(obj, Camera):
            # return (pos, rect) position of the camera and boundaries
            return ((obj.pos - self.worldOrigin) * np.array((1, -1)),  # pos
                    ((obj.initialValues[0], obj.ymin - self.worldOrigin[1]),  # rect part 1
                     ((obj.initialValues[1] - obj.initialValues[0]),
                      -(self.worldOrigin[1] - obj.ymin + (obj.ymax - self.worldOrigin[1])))))  # rect part 2

    def draw(self, screen):
        screen.fill(self.backgroundColor)

        for go in self.gameObjects:
            go.draw(screen, self.calculateDrawingCoordinates(go), go.width * self.tileSize[0],
                    go.height * self.tileSize[1])

        for actor in self.actors:
            if isinstance(actor, Actor):
                actor.draw(screen, self.calculateDrawingCoordinates(actor),
                           actor.width * self.tileSize[0], actor.height * self.tileSize[1])

        for player in self.players:
            if isinstance(player, Player):
                player.draw(screen, self.calculateDrawingCoordinates(player),
                            player.width * self.tileSize[0], player.height * self.tileSize[1])
