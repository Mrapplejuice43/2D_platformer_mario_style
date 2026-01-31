import numpy as np

from actors import Actor, Enemy, Player
from camera import Camera
from game_objects import Box, GameObject, Ground, Plateforme


class World:
    def __init__(self, canvas_size, tile_size, game_scale, level=None):
        self.canvas_size = (canvas_size[0], canvas_size[1])
        self.world_origin = np.array((0, canvas_size[1]))
        self.camera = Camera(canvas_size, tile_size, game_scale)
        self.level = level
        self.tile_size = np.array(tile_size)
        self.scale = game_scale
        self.background_color = (50, 201, 255)
        self.debug_mode = False
        self.objects = []
        self.boxes = []
        self.game_objects = []
        self.actors = []
        self.player = None

        if self.level is not None:
            self.read_world(level)

    def add_game_object(self, game_obj):
        """
        Adds the gameObject to the corresponding lists
        :param gameObj:
        :return:
        """
        if isinstance(game_obj, GameObject):
            self.game_objects.append(game_obj)
            self.objects.append(game_obj)

    def add_actor(self, actor):
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

    def add_box(self, box):
        """
        Adds the box gameObject to the corresponding lists
        :param box:
        :return:
        """
        if isinstance(box, Box):
            self.game_objects.append(box)
            self.boxes.append(box)
            self.objects.append(box)

    def resize(self, window_size, tile_size):
        """
        Resize the game depending on the size of the window. Also adjust the size of the tiles
        :param windowSize:
        :param tileSize:
        :return:
        """
        self.player.pos = np.ceil(
            np.array(
                (
                    self.player.pos[0] * window_size[0] / self.canvas_size[0],
                    self.player.pos[1] * window_size[1] / self.canvas_size[1],
                )
            )
        )
        self.player.start_pos = np.ceil(
            (
                self.player.start_pos[0] * window_size[0] / self.canvas_size[0],
                self.player.start_pos[1] * window_size[1] / self.canvas_size[1],
            )
        )

        self.world_origin = np.array(
            (
                self.world_origin[0],
                self.world_origin[1] * window_size[1] // self.canvas_size[1],
            )
        )
        self.canvas_size = window_size
        self.tile_size = tile_size
        self.camera.resize(window_size, tile_size)

    def change_level(self, new_level):
        """Made for code clarity"""
        self.read_world(new_level)

    def reset_world(self):
        """Made for code clarity"""
        self.read_world(self.level)
        self.camera.reset()
        self.world_origin = np.array((0, self.canvas_size[1]))

    def read_world(self, fic):
        """
        Parse and reads the file that contains formatted data about the world
        Format example : type width height x y
        Types : g (Ground), P (Player), E (Enemy), b (Box), p (Platform)
        Case matters !
        """
        self.objects = []
        self.boxes = []
        self.game_objects = []
        self.actors = []
        self.player = None
        if self.level is None:
            self.level = fic

        f = open(fic, "r")
        for line in f.readlines():
            # type width height posx posy
            tmp = line.split()
            if len(tmp) == 5:
                if tmp[0] == "p":
                    self.add_game_object(Plateforme(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == "g":
                    self.add_game_object(Ground(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == "P":
                    self.add_actor(
                        Player(
                            float(tmp[1]),
                            float(tmp[2]),
                            (int(tmp[3]), int(tmp[4])) * self.tile_size,
                        )
                    )
                elif tmp[0] == "b":
                    self.add_box(Box(int(tmp[1]), int(tmp[2]), (int(tmp[3]), int(tmp[4]))))
                elif tmp[0] == "E":
                    self.add_actor(
                        Enemy(
                            float(tmp[1]),
                            float(tmp[2]),
                            (int(tmp[3]), int(tmp[4])) * self.tile_size,
                        )
                    )

    def switch_debug_mode(self):
        self.debug_mode = not self.debug_mode
        for obj in self.objects:
            obj.debugMode = not obj.debugMode

    def calculate_drawing_coordinates(self, obj):
        """
        Calculates coordinates in global geometrical landmark from local origin at the bottom left corner x+ towards left and y+ towards up
        :param obj: the object we calculate the coordinates into global geometric landmark
        """
        if isinstance(obj, Actor):
            return (obj.pos + (0, obj.height) * self.tile_size - self.world_origin) * np.array((1, -1))

        elif isinstance(obj, GameObject):
            return ((obj.pos + (0, obj.height)) * self.tile_size - self.world_origin) * np.array((1, -1))

        elif isinstance(obj, Camera):
            # return (pos, rect) position of the camera and boundaries
            return (
                (obj.pos - self.world_origin) * np.array((1, -1)),  # pos
                (
                    (
                        obj.initialValues[0],
                        obj.ymin - self.world_origin[1],
                    ),  # rect part 1
                    (
                        (obj.initialValues[1] - obj.initialValues[0]),
                        # rect part 2
                        -(self.world_origin[1] - obj.ymin + (obj.ymax - self.world_origin[1])),
                    ),
                ),
            )

    def draw(self, screen):
        """
        Draw function of the game
        :param screen:
        :return:
        """
        screen.fill(self.background_color)

        for go in self.game_objects:
            go.draw(
                screen,
                self.calculate_drawing_coordinates(go),
                go.width * self.tile_size[0],
                go.height * self.tile_size[1],
            )

        for actor in self.actors:
            if isinstance(actor, Actor):
                actor.draw(
                    screen,
                    self.calculate_drawing_coordinates(actor),
                    actor.width * self.tile_size[0],
                    actor.height * self.tile_size[1],
                )

        if self.player is not None:
            self.player.draw(
                screen,
                self.calculate_drawing_coordinates(self.player),
                self.player.width * self.tile_size[0],
                self.player.height * self.tile_size[1],
            )

        if self.debug_mode:
            self.camera.draw(screen)

    def update(self, keys, dt, size_ratio):
        camera_offset_left = self.camera.xmin - (self.camera.initialValues[0] * self.tile_size[0])
        for go in self.game_objects:
            if (go.pos[0] + go.width) * self.tile_size[0] > camera_offset_left and go.pos[0] < camera_offset_left + self.canvas_size[0]:
                go.onScreen = True
            else:
                go.onScreen = False

        for actor in self.actors:
            if (
                actor.pos[0] + (actor.width * self.tile_size[0]) > camera_offset_left
                and actor.pos[0] < camera_offset_left + self.canvas_size[0]
            ):
                actor.onScreen = True
            else:
                actor.onScreen = False

            if actor.life < 1:
                self.actors.remove(actor)

            actor.update(dt, size_ratio, self.game_objects, self.tile_size, self.scale)

        self.camera.check_player_pos(self.player)

        if self.player.pos[1] + self.player.height * self.tile_size[1] < 0 or self.player.life <= 0:
            self.reset_world()

        self.player.update(
            keys,
            dt,
            size_ratio,
            self.game_objects,
            self.actors,
            self.tile_size,
            self.scale,
        )

    def move_camera(self, dx, dy):
        self.world_origin += (dx, dy)
        self.camera.move(dx, dy)
