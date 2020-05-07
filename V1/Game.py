from V1.Camera import *
from V1.Window import *
from V1.World import *


class Game:
    def __init__(self, window, world, camera):

        self.window = window
        self.world = world
        self.camera = camera
        self.clock = pygame.time.Clock()
        self.targetFPS = 60
        self.fps = self.clock.get_fps()
        self.time = pygame.time.get_ticks()

        self.worldOrigin = np.array((0, self.window.height))

    def addGameObject(self, gameObj):
        """
        Adds a game object to the world
        :param gameObj: The game object to add
        """
        if isinstance(gameObj, GameObject):
            self.world.addGameObject(gameObj)

    def addActor(self, actor):
        """
        Add an actor to the world
        :param actor: The actor to add
        """
        if isinstance(actor, Actor):
            self.world.addActor(actor)

    def addBox(self, box):
        """
        Adds a box to the world
        :param box: The box to add
        """
        self.world.addBox(box)

    def calculateDrawingCoordinates(self, obj):
        """
        Calculates coordinates in global geometrical landmark from local origin at the bottom left corner x+ towards left and y+ towards up
        :param obj: the object we calculate the coordinates into global geometric landmark
        """
        if isinstance(obj, Actor):
            return (obj.pos - self.worldOrigin) * np.array((1, -1))
        if isinstance(obj, GameObject):
            return ((obj.pos - (1, 0)) * self.window.caseSize - self.worldOrigin) * np.array((1, -1))

        if isinstance(obj, Camera):
            # return (pos, rect) position of the camera and boundaries
            return ((obj.pos - self.worldOrigin) * np.array((1, -1)), # pos
                    ((obj.initialValues[0], self.worldOrigin[1] - obj.ymin),  # rect part 1
                     ((obj.initialValues[1] - obj.initialValues[0]), -(self.worldOrigin[1] - obj.ymin + (obj.ymax - self.worldOrigin[1]))))) # rect part 2

    def update(self):
        """
        Updates origin depending on the size of the window and the fps of the game
        """
        if self.world.players[0]:
            self.camera.checkPlayerPos(self.world.players[0], self.window.caseSize)
        self.fps = self.clock.get_fps()
        self.time = pygame.time.get_ticks()

    def readWorld(self, fic):
        """
        Reads a formatted file which determine what is in the world
        :param fic: Path of the file to read
        """
        f = open(fic, 'r')
        for l in f.readlines():
            tmp = l.split()
            if len(tmp) == 5:
                if tmp[0] == 'p':
                    self.addGameObject(Plateforme(
                        int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == 'g':
                    self.addGameObject(
                        Ground(int(tmp[1]), int(tmp[4]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == 'P':
                    self.addActor(Player(int(tmp[1]), int(tmp[2]), (
                        int(tmp[3]) * self.window.caseSize[0], int(tmp[4]) * self.window.caseSize[0])))
                elif tmp[0] == 'b':
                    self.addBox(Box(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == '#':
                    continue

    def getKeys(self):
        """
        :return: list of keys pressed
        """
        return pygame.key.get_pressed()

    def handleEvents(self):
        for event in pygame.event.get():

            if event.type == QUIT:
                self.window.shouldClose = True

            if event.type == CAMERA_TRIGGER:
                self.worldOrigin += (event.__dict__["dx"], event.__dict__["dy"])

            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.window.shouldClose = True

                if event.key == K_g:
                    self.window.isGridDrawn = not self.window.isGridDrawn

                if event.key == K_F10:
                    self.window.showFPS = not self.window.showFPS

                if event.key == K_r:
                    self.worldOrigin = np.array((0, self.window.height))
                    self.camera.reset()

                if event.key == K_t:
                    self.targetFPS += 5

                if event.key == K_y:
                    self.targetFPS -= 5

    def reset(self, player):
        player.reset()
        self.worldOrigin = np.array((0, self.window.height))
        self.camera.reset()

    def run(self):
        """
        Main loop of the game
        """
        while not self.window.shouldClose:
            self.clock.tick(self.targetFPS)
            self.update()
            self.handleEvents()

            for player in self.world.players:
                if self.fps > 0:
                    player.update(self.getKeys(), (self.clock.get_time()) / 1000)
                    player.checkCollisions(self.world.gameObjects, self.window.caseSize)
                    if player.pos[1] + player.height * self.window.caseSize[1] < 0:
                        self.reset(player)

            self.window.screen.fill((50, 201, 255))
            self.draw()
            if self.window.isGridDrawn:
                self.window.drawGrid()

            pygame.display.flip()

    def draw(self):
        """
        Drawing function of the game
        """
        for go in self.world.gameObjects:
            go.draw(self.window.screen, self.calculateDrawingCoordinates(go), go.width * self.window.caseSize[0],
                    go.height * self.window.caseSize[1])

        for actor in self.world.actors:
            if isinstance(actor, Actor):
                actor.draw(self.window.screen, self.calculateDrawingCoordinates(actor),
                           actor.width * self.window.caseSize[0], actor.height * self.window.caseSize[1])

        noPlayer = 0
        for player in self.world.players:
            if isinstance(player, Player):
                player.draw(self.window.screen, self.calculateDrawingCoordinates(player),
                            player.width * self.window.caseSize[0], player.height * self.window.caseSize[1])

                if self.window.showFPS:
                    pygame.draw.ellipse(self.window.screen, (0, 0, 0), pygame.Rect(self.calculateDrawingCoordinates(player) - 3, (6, 6)), 0)
                    self.window.screen.blit(
                        pygame.font.SysFont("Consolas", 14, bold=True).render("{}".format(self.fps), False,
                                                                              (50, 200, 200)), (0, 0))

                    self.camera.draw(self.window.screen, self.calculateDrawingCoordinates(self.camera))

                    self.window.screen.blit(
                        pygame.font.SysFont("Consolas", 14, bold=True).render(
                            "pos : {0} startPos : {1}  drawOrigin : {2} cameraPos : {3} {4}".format(
                                player.pos, player.startPos, self.worldOrigin, self.camera.pos, self.camera.triggerBounds), False, (0, 0, 0)),
                        (200, 20 * noPlayer))
            noPlayer += 1


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()
    w = Window(1280, 720)
    game = Game(w, World(), Camera((w.width, w.height), w.caseSize))
    game.readWorld(r"worldTest.wd")
    game.run()
