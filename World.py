from GameObjects import *
from Actors import *
from Camera import *


class World:
    def __init__(self, canvasSize, tileSize, gameScale, level=None):
        self.canvasSize = (canvasSize[0], canvasSize[1])
        self.worldOrigin = np.array((0, canvasSize[1]))
        self.level = level
        self.tileSize = np.array(tileSize)
        self.scale = gameScale
        self.backgroundColor = (50, 201, 255)
        self.debugMode = False
        self.objects = []
        self.boxes = []
        self.gameObjects = []
        self.actors = []
        self.player = None

        if self.level is not None:
            self.readWorld(level)

    def addGameObject(self, gameObj):
        """
        Adds the gameObject to the corresponding lists
        :param gameObj:
        :return:
        """
        if isinstance(gameObj, GameObject):
            self.gameObjects.append(gameObj)
            self.objects.append(gameObj)

    def addActor(self, actor):
        """
        Adds the actor to the corresponding lists
        :param actor:
        :return:
        """
        if isinstance(actor, Player):
            self.player = actor
            self.objects.append(actor)
        else:
            self.actors.append(actor)
            self.objects.append(actor)

    def addBox(self, box):
        """
        Adds the box gameObject to the corresponding lists
        :param box:
        :return:
        """
        if isinstance(box, Box):
            self.gameObjects.append(box)
            self.boxes.append(box)
            self.objects.append(box)

    def resize(self, windowSize, tileSize):
        """
        Resize the game depending on the size of the window. Also adjust the size of the tiles
        :param windowSize:
        :param tileSize:
        :return:
        """
        self.player.pos = np.ceil(np.array((self.player.pos[0] * windowSize[0] / self.canvasSize[0],
                                            self.player.pos[1] * windowSize[1] / self.canvasSize[1])))
        self.player.startPos = np.ceil((self.player.startPos[0] * windowSize[0] / self.canvasSize[0],
                                        self.player.startPos[1] * windowSize[1] / self.canvasSize[1]))

        self.worldOrigin = np.array((self.worldOrigin[0],
                                     self.worldOrigin[1] * windowSize[1] // self.canvasSize[1]))
        self.canvasSize = windowSize
        self.tileSize = tileSize

    def changeLevel(self, newLevel):
        """Made for code clarity"""
        self.readWorld(newLevel)

    def resetWorld(self):
        """Made for code clarity"""
        self.readWorld(self.level)

    def readWorld(self, fic):
        """
        Parse and reads the file that contains formatted data about the world
        Format example : type width height x y
        Types : g (Ground), P (Player), E (Enemy), b (Box), p (Platform)
        Case matters !
        """
        self.objects = []
        self.boxes = []
        self.gameObjects = []
        self.actors = []
        self.player = None
        if self.level is None:
            self.level = fic

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
                elif tmp[0] == 'E':
                    self.addActor(Enemy(float(tmp[1]), float(tmp[2]), (int(tmp[3]), int(tmp[4])) * self.tileSize))

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
        """
        Draw function of the game
        :param screen:
        :return:
        """
        screen.fill(self.backgroundColor)

        for go in self.gameObjects:
            go.draw(screen, self.calculateDrawingCoordinates(go), go.width * self.tileSize[0],
                    go.height * self.tileSize[1])

        for actor in self.actors:
            if isinstance(actor, Actor):
                actor.draw(screen, self.calculateDrawingCoordinates(actor),
                           actor.width * self.tileSize[0], actor.height * self.tileSize[1])

        self.player.draw(screen, self.calculateDrawingCoordinates(self.player),
                         self.player.width * self.tileSize[0], self.player.height * self.tileSize[1])

    def update(self, keys, dt, sizeRatio):
        if self.player.pos[1] + self.player.height * self.tileSize[1] < 0 or self.player.life <= 0:
            self.resetWorld()

        self.player.update(keys, dt, sizeRatio, self.gameObjects, self.actors, self.tileSize,
                           self.scale)
