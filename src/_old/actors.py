import pygame
from pygame.locals import K_LEFT, K_RIGHT, K_DOWN, K_UP, K_r, K_KP0, K_SPACE
import numpy as np

from .constants import BALKANY_PATH, POLICE_PATH
from .game_objects import Box


def speed_func(max_speed, delta_time, time_needed_to_reach_max):
    if time_needed_to_reach_max == 0:
        return 0
    else:
        return max_speed * np.tanh(2 * delta_time / time_needed_to_reach_max)


def jumping_speed(force, mass):
    return force / mass


def slow_speed(max_speed, t, time_needed_to_stop):
    if time_needed_to_stop == 0:
        return 0
    else:
        return max_speed * np.exp(-t / time_needed_to_stop)


def falling_speed(gravity_force, delta_time):
    return gravity_force * delta_time


class Actor:
    def __init__(self, *args):
        """
        Constructor of the Actor class
        :param args: args[0] the width of the actor in tiles, args[1] the height, args[2] the pos in pixels
        """
        self.width = args[0]
        self.height = args[1]
        self.full_height = args[1]
        # not useful except for rendering an actor as a square of a certain color
        self.color = np.array((30, 30, 200))
        self.weight = 1
        self.jumping_strength = 10
        self.direction = [None, None]
        self.on_screen = True
        self.life = 1

        # pixels/s used to store what speed the player should have
        self.speed = np.array((0.0, 0.0), dtype=float)
        self.movement_speed = np.array((0.0, 0.0), dtype=float)  # used to move the player
        self.pos = np.array(args[2])
        self.start_pos = tuple(args[2])

        # Moving states of the actor
        self.on_ground = False
        self.can_move_left = True
        self.can_move_right = True
        self.can_move_up = True
        self.can_uncrouch = True
        self.jumping = False
        self.crouched = False
        self.controllable = True

        self.max_horizontal_speed = 6  # pixels/s
        self.max_vertical_speed = 5
        self.fallback_speed = 6
        self.seconds_to_max_horizontal_speed = 0.5
        self.seconds_to_stop = 0.1
        # Time where the player is uncontrollable after upon taking damage (in seconds)
        self.recovery_time = 0.5

        self.seconds_moving_left = 0
        self.seconds_moving_right = 0
        self.seconds_stopping = 0
        self.seconds_falling = 0
        self.peak_speed = 0.0
        self.seconds_recovering = 0.0

        self.sprite = None
        self.debug_mode = False

    def move(self, keys, dt, size_ratio, game_scale):
        """
        :param keys: list of keys pressed
        :param time: current time of the game since init not to make speed frame dependent
        """
        if keys[K_LEFT] and keys[K_RIGHT]:
            self.speed[0] = 0
            self.peak_speed = 0.0
            self.seconds_moving_left = 0
            self.seconds_moving_right = 0

        elif keys[K_LEFT] and self.can_move_left:
            if self.direction[0] != K_LEFT:
                self.direction[0] = K_LEFT
                self.seconds_moving_left = 0
                self.speed[0] = 0
                self.peak_speed = 0.0

            if self.speed[0] > -self.max_horizontal_speed:
                self.speed[0] = (
                    (
                        -speed_func(
                            self.max_horizontal_speed,
                            self.seconds_moving_left,
                            self.seconds_to_max_horizontal_speed,
                        )
                    )
                    * size_ratio[0]
                    * game_scale
                )
                self.seconds_moving_left += dt
                self.peak_speed = self.speed[0]

        elif keys[K_RIGHT] and self.can_move_right:
            if self.direction[0] != K_RIGHT:
                self.direction[0] = K_RIGHT
                self.seconds_moving_right = 0
                self.speed[0] = 0
                self.peak_speed = 0.0

            if self.speed[0] < self.max_horizontal_speed:
                self.speed[0] = (
                    (
                        speed_func(
                            self.max_horizontal_speed,
                            self.seconds_moving_right,
                            self.seconds_to_max_horizontal_speed,
                        )
                    )
                    * size_ratio[0]
                    * game_scale
                )
                self.seconds_moving_right += dt
                self.peak_speed = self.speed[0]

    def fall(self, dt, size_ratio, game_scale):
        self.speed[1] += (
            (falling_speed(-self.max_vertical_speed * self.weight, self.seconds_falling)) * size_ratio[1] * game_scale
        )
        self.seconds_falling += dt

    def jump(self, size_ratio, game_scale, speed=None):
        if self.on_ground and not self.jumping:
            self.jumping = True
            self.on_ground = False
            if speed is None:
                self.speed[1] += (jumping_speed(self.jumping_strength, self.weight)) * size_ratio[1] * game_scale
            else:
                self.speed[1] += (jumping_speed(speed, self.weight)) * size_ratio[1] * game_scale

    def reset(self):
        self.pos = np.array(self.start_pos)
        self.speed = np.array((0.0, 0.0), dtype=float)
        self.direction = [None, None]

        self.on_ground = False
        self.can_move_left = True
        self.can_move_right = True
        self.can_move_up = True
        self.can_uncrouch = True
        self.jumping = False
        self.crouched = False
        self.height = self.full_height

        self.seconds_moving_left = 0
        self.seconds_moving_right = 0
        self.seconds_stopping = 0
        self.seconds_falling = 0

    def crouch(self):
        if not self.crouched:
            self.crouched = True
            self.height = 2 * self.height / 3

    def uncrouch(self):
        if self.crouched:
            self.crouched = False
            self.height = 3 * self.height / 2

    def draw(self, screen, coords, width, height):
        screen.blit(pygame.transform.scale(self.sprite, (int(width), int(height))), coords)
        if self.debug_mode:
            pygame.draw.rect(screen, (200, 0, 0), pygame.Rect(coords, (width, height)), 2)
            pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect(coords - (3, 3 - height), (6, 6)), 0)
            screen.blit(
                pygame.font.SysFont("Consolas", 12).render("{0}, {1}".format(self.pos, self.speed), False, (0, 0, 0)),
                coords - (50, 20),
            )

            if isinstance(self, Player):
                screen.blit(
                    pygame.font.SysFont("Consolas", 12).render(
                        "canMoveUp : {0} canMoveLeft : {1} canMoveRight : {2} onGround : {3}".format(
                            self.can_move_up,
                            self.can_move_left,
                            self.can_move_right,
                            self.on_ground,
                        ),
                        False,
                        (0, 0, 0),
                    ),
                    (200, 20),
                )

    def check_position_collisions(self, game_objects, tile_size):
        # Temporary vars in order to make collision detection independent from gameObjects order and improve efficiency
        actor = self
        on_ground = False
        can_move_up = True
        can_move_right = True
        can_move_left = True
        can_uncrouch = True
        if self.jumping:
            jumping = True
        else:
            jumping = False

        tmp_speed = np.int32(np.round(actor.speed))
        tmp_pos = actor.pos

        for game_obj in game_objects:
            if game_obj.on_screen:
                x_collide, y_collide = False, False

                # Check if player and obj overlap on the x direction
                if (
                    actor.pos[1] + tmp_speed[1] <= (game_obj.pos[1] + game_obj.height) * tile_size[1]
                    and actor.pos[1] + tmp_speed[1] + actor.height * tile_size[1] >= game_obj.pos[1] * tile_size[1]
                ):
                    x_collide = True

                # Check if player and obj overlap on the y direction
                if (
                    actor.pos[0] + tmp_speed[0] < (game_obj.pos[0] + game_obj.width) * tile_size[0]
                    and actor.pos[0] + tmp_speed[0] + actor.width * tile_size[0] > game_obj.pos[0] * tile_size[0]
                ):
                    y_collide = True

                    above = actor.pos[1] >= (game_obj.pos[1] + game_obj.height) * tile_size[1]
                    below = actor.pos[1] + actor.height * tile_size[1] <= game_obj.pos[1] * tile_size[1]

                    if below:
                        if actor.crouched:
                            can_uncrouch = (
                                actor.pos[1] + actor.full_height * tile_size[1] <= game_obj.pos[1] * tile_size[1]
                            )

                # If they overlap on both x and y axis they collide
                if x_collide and y_collide:
                    # Look where the player is from the object
                    above = actor.pos[1] >= (game_obj.pos[1] + game_obj.height) * tile_size[1]
                    below = actor.pos[1] + actor.height * tile_size[1] <= game_obj.pos[1] * tile_size[1]
                    right = actor.pos[0] >= (game_obj.pos[0] + game_obj.width) * tile_size[0]
                    left = actor.pos[0] + actor.width * tile_size[0] <= game_obj.pos[0] * tile_size[0]

                    # if the player is on the left it means that he was moving to the right so
                    # we put him against the object and removes his speed while changing his canMoveRight state
                    if above:
                        on_ground = True
                        tmp_pos[1] = (game_obj.pos[1] + game_obj.height) * tile_size[1]
                        self.movement_speed[1] = 0
                    elif below:
                        can_move_up = False
                        jumping = False
                        tmp_pos[1] = (game_obj.pos[1] - actor.height) * tile_size[1]
                        self.movement_speed[1] = 0
                        self.speed[1] /= 1.5

                        if isinstance(actor, Player) and isinstance(game_obj, Box) and self.jumping:
                            game_obj.activate()

                    elif left:
                        can_move_right = False
                        tmp_pos[0] = (game_obj.pos[0] - actor.width) * tile_size[0]
                        self.movement_speed[0] = 0
                    elif right:
                        can_move_left = False
                        tmp_pos[0] = (game_obj.pos[0] + game_obj.width) * tile_size[0]
                        self.movement_speed[0] = 0

        self.on_ground = on_ground
        self.can_move_up = can_move_up
        self.can_move_right = can_move_right
        self.can_move_left = can_move_left
        self.can_uncrouch = can_uncrouch
        self.jumping = jumping
        self.pos = tmp_pos

    def actor_collision(self, actors, tile_size):
        tested_actor = self

        for actor in actors:
            if actor.on_screen:
                x_collide, y_collide = False, False

                # Check if player and obj overlap on the x direction
                if (
                    tested_actor.pos[1] + tested_actor.speed[1]
                    <= actor.pos[1] + actor.speed[1] + (actor.height * tile_size[1])
                    and tested_actor.pos[1] + tested_actor.speed[1] + tested_actor.height * tile_size[1]
                    >= actor.pos[1] + actor.speed[1]
                ):
                    x_collide = True

                # Check if player and obj overlap on the y direction
                if (
                    tested_actor.pos[0] + tested_actor.speed[0]
                    <= actor.pos[0] + actor.speed[0] + (actor.width * tile_size[0])
                    and tested_actor.pos[0] + tested_actor.speed[0] + tested_actor.width * tile_size[0]
                    >= actor.pos[0] + actor.speed[0]
                ):
                    y_collide = True

                # If they overlap on both x and y axis they collide
                if x_collide and y_collide:
                    # Above
                    if tested_actor.pos[1] >= actor.pos[1] + actor.height * tile_size[1]:
                        tested_actor.pos[1] = actor.pos[1] + actor.height * tile_size[1]

                        self.seconds_falling = 0

                        tested_actor.movement_speed[1] = 0
                        tested_actor.speed[1] = tested_actor.fallback_speed
                        actor.life -= 1

                    else:
                        self.controllable = False

                        if isinstance(tested_actor, Player):
                            tested_actor.life -= 1

                        # Reset movements timings
                        self.seconds_stopping = 0
                        self.seconds_moving_left = 0
                        self.seconds_moving_right = 0
                        self.seconds_falling = 0

                        # Reset speed
                        tested_actor.movement_speed[0] = 0
                        tested_actor.movement_speed[1] = 0

                        # Below
                        if tested_actor.pos[1] + tested_actor.height * tile_size[1] <= actor.pos[1]:
                            tested_actor.pos[1] = actor.pos[1] - tested_actor.height * tile_size[1]
                            tested_actor.speed[1] = -tested_actor.fallback_speed

                        # Left
                        elif tested_actor.pos[0] + tested_actor.width * tile_size[0] <= actor.pos[0]:
                            tested_actor.pos[0] = actor.pos[0] - tested_actor.width * tile_size[0]
                            tested_actor.speed[1] = tested_actor.fallback_speed

                        # Right
                        elif tested_actor.pos[0] >= actor.pos[0] + actor.width * tile_size[0]:
                            tested_actor.pos[0] = actor.pos[0] + actor.width * tile_size[0]
                            tested_actor.speed[1] = tested_actor.fallback_speed

                        # Simulate fallback from taking damages
                        if tested_actor.direction[0] == K_LEFT:
                            tested_actor.speed[0] = tested_actor.fallback_speed
                        elif tested_actor.direction[0] == K_RIGHT:
                            tested_actor.speed[0] = -tested_actor.fallback_speed
                        else:
                            tested_actor.direction[0] = K_LEFT
                            tested_actor.speed[0] = -tested_actor.fallback_speed

                        tested_actor.peak_speed = tested_actor.speed[0]


class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(args[0], args[1], args[2])
        self.sprite = pygame.image.load(BALKANY_PATH)
        self.on_screen = True
        self.life = 1

    def update(self, keys, dt, size_ratio, game_objects, actors, tile_size, game_scale):
        if not self.controllable:
            self.seconds_recovering += dt

        if self.seconds_recovering > self.recovery_time:
            self.controllable = True
            self.seconds_recovering = 0.0

        if (keys[K_RIGHT] or keys[K_LEFT]) and self.controllable:
            self.seconds_stopping = 0
            self.move(keys, dt, size_ratio, game_scale)
        else:
            self.secondsMovingRight = 0
            self.secondsMovingLeft = 0

            if abs(self.speed[0]) < 0.01 and self.direction[0]:
                self.speed[0] = 0
                self.seconds_stopping = 0
                self.direction[0] = None

            if self.direction[0] == K_LEFT or self.direction[0] == K_RIGHT:
                self.speed[0] = slow_speed(self.peak_speed, self.seconds_stopping, self.seconds_to_stop) * size_ratio[0]
                self.seconds_stopping += dt

        if not self.on_ground:
            self.fall(dt, size_ratio, game_scale)

        if self.on_ground:
            self.jumping = False
            self.speed[1] = 0
            self.seconds_falling = 0

        if (keys[K_SPACE] or keys[K_KP0]) and self.can_move_up and self.controllable:
            self.jump(size_ratio, game_scale)

        if keys[K_r]:
            self.reset()

        if keys[K_DOWN] and self.controllable:
            self.crouch()
        elif self.can_uncrouch:
            self.uncrouch()

        if self.speed[1] > 0:
            self.direction[1] = K_UP
        else:
            self.direction[1] = K_DOWN

        self.movement_speed = np.array(self.speed.tolist(), dtype=float)
        self.check_position_collisions(game_objects, tile_size)

        if self.controllable:
            self.actor_collision(actors, tile_size)

        self.pos += np.int32(np.round(self.movement_speed))


class Enemy(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(args[0], args[1], args[2])
        self.sprite = pygame.image.load(POLICE_PATH)

        self.life = 1

    def update(self, dt, size_ratio, game_objects, tile_size, game_scale):
        if not self.on_ground:
            self.fall(dt, size_ratio, game_scale)
        else:
            self.speed[1] = 0

        self.movement_speed = np.array(self.speed.tolist(), dtype=float)
        self.check_position_collisions(game_objects, tile_size)
        self.pos += np.int32(np.round(self.movement_speed))
