import numpy as np
from pygame.locals import *
import pygame


def speedFunc(maxSpeed, t, timeNeededToReachMax):
    if timeNeededToReachMax == 0:
        return 0
    else:
        return maxSpeed * np.tanh(t / (timeNeededToReachMax))


def jumpingSpeed(F, m):
    return F / m


def fallingSpeed(g, t):
    return g * t


class Actor:
    def __init__(self, *args):
        self.width = args[0]
        self.height = args[1]
        self.color = np.array((30, 30, 200))
        self.weight = 1
        self.jumpingStrength = 20
        self.direction = None

        self.speed = np.array((0.0, 0.0), dtype=np.float)  # en pixels/s
        self.pos = np.array(args[2])  # en pixels par rapport au repère local
        self.startPos = tuple(args[2])

        self.onGround = False
        self.canMoveLeft = True
        self.canMoveRight = True
        self.jumping = False
        self.crouched = False

        self.xAcceleration = 4  # en pixels/s
        self.yAcceleration = 10
        self.secondsToMaxHorizontalSpeed = .5
        self.secondsToStop = .2

        self.secondsMovingLeft = 0
        self.secondsMovingRight = 0
        self.secondsStopping = 0
        self.secondsFalling = 0

        self.sprite = pygame.image.load(r'assets\balkany.png')

    def move(self, keys, dt):
        """
        :param keys: list of keys pressed
        :param time: current time of the game since init not to make speed frame dependent
        """
        if keys[K_LEFT] and keys[K_RIGHT]:
            self.speed[0] = 0
            self.secondsMovingLeft = 0
            self.secondsMovingRight = 0

        elif keys[K_LEFT] and self.canMoveLeft:
            if self.direction != K_LEFT:
                self.direction = K_LEFT
                self.secondsMovingLeft = 0
                self.speed[0] = 0

            if self.speed[0] > -self.xAcceleration:
                self.speed[0] = -speedFunc(self.xAcceleration, self.secondsMovingLeft, self.secondsToMaxHorizontalSpeed)
                self.secondsMovingLeft += dt

            self.pos[0] += int(round(self.speed[0]))

        elif keys[K_RIGHT] and self.canMoveRight:
            if self.direction != K_RIGHT:
                self.direction = K_RIGHT
                self.secondsMovingRight = 0
                self.speed[0] = 0

            if self.speed[0] < self.xAcceleration:
                self.speed[0] = speedFunc(self.xAcceleration, self.secondsMovingRight, self.secondsToMaxHorizontalSpeed)
                self.secondsMovingRight += dt

            self.pos[0] += int(round(self.speed[0]))

    def fall(self, dt):
        self.speed[1] += fallingSpeed(-self.yAcceleration * self.weight, self.secondsFalling)
        self.secondsFalling += dt

    def jump(self):
        if self.onGround and not self.jumping:
            self.jumping = True
            self.onGround = False
            self.speed[1] += jumpingSpeed(self.jumpingStrength, self.weight)

    def reset(self):
        self.pos = np.array(self.startPos)
        self.speed = np.array((0, 0))
        self.onGround = False
        self.canMoveLeft = True
        self.canMoveRight = True
        self.jumping = False
        self.secondsMovingRight = 0
        self.secondsFalling = 0
        self.secondsJumping = 0
        self.secondsMovingLeft = 0

    def crouch(self):
        if not self.crouched:
            self.crouched = True
            self.height -= 1

    def unCrouch(self):
        if self.crouched:
            self.crouched = False
            self.height += 1

    def update(self, keys, dt):
        if keys[K_RIGHT] or keys[K_LEFT]:
            self.secondsStopping = 0
            self.move(keys, dt)
        else:
            self.secondsMovingRight = 0
            self.secondsMovingLeft = 0
            if self.direction == K_LEFT:
                self.speed[0] = speedFunc(self.xAcceleration, self.secondsStopping, self.secondsToStop) - self.xAcceleration
                self.secondsStopping += dt
            elif self.direction == K_RIGHT:
                self.speed[0] = -speedFunc(self.xAcceleration, self.secondsStopping, self.secondsToStop) + self.xAcceleration
                self.secondsStopping += dt

        if not self.onGround:
            self.fall(dt)

        if self.onGround:
            self.onGround = True
            self.jumping = False
            self.speed[1] = 0
            self.secondsFalling = 0

        if keys[K_SPACE] or self.jumping or keys[K_KP0]:
            self.jump()

        if keys[K_r]:
            self.reset()

        if keys[K_DOWN]:
            self.crouch()
        else:
            self.unCrouch()

        self.pos += np.int32(np.round(self.speed))

    def draw(self, screen, coords, width, height):
        screen.blit(pygame.transform.scale(self.sprite, (width, height)), coords - (0, height))

    def checkCollisions(self, gameObjects, caseSize):
        self.onGround = False
        self.canMoveRight = True
        self.canMoveLeft = True

        for gameObj in gameObjects:

            # Check y related collisions

            if self.pos[0] < (gameObj.pos[0] - 1 + gameObj.width) * caseSize[0] and \
                    self.pos[0] + self.width * caseSize[0] > (gameObj.pos[0] - 1) * caseSize[0]:

                if self.pos[1] >= gameObj.pos[1] * caseSize[1] >= self.pos[1] + self.speed[1]:
                    self.pos[1] = gameObj.pos[1] * caseSize[1]
                    self.onGround = True

            # Check x related collisions

            # if x + dx >= gameObj.x + gameObj.width
            # or x + dx <= gameObj.x
            # or y >= gameObj.y
            # or y + height <= gameObj.y - gameObj.height
            # -1 for gameObj x coordinates is the offset due to the geometrical landmark
            # We negate the expression to be able to flip the variable if the player can actually not move otherwise it depends on the order of the gameObjs
            # We also don't want the player to teleport to a side so we avoid checking for collisions while on air for x collisions only
            if not ((self.pos[0] + self.speed[0] >= (gameObj.pos[0] + gameObj.width - 1) * caseSize[0]
                     or self.pos[0] + self.speed[0] <= (gameObj.pos[0] - 1) * caseSize[0])
                    or self.pos[1] >= gameObj.pos[1] * caseSize[1]
                    or self.pos[1] + self.height * caseSize[1] <= (gameObj.pos[1] - gameObj.height) * caseSize[
                        1]) and not self.jumping and self.onGround:

                if self.pos[1] + self.height * caseSize[1] <= (gameObj.pos[1] - gameObj.height) * caseSize[1]:
                    self.crouch()
                else:
                    self.pos[0] = (gameObj.pos[0] - 1 + gameObj.width) * caseSize[0]
                    self.canMoveLeft = False

            # if x + dx + width <= gameObj.x
            # or x + dx + width >= gameObj.x + gameObj.width
            # or y >= gameObj.y
            # or y + height <= gameObj.y - gameObj.height
            # -1 for gameObj x coordinates is the offset due to the geometrical landmark
            # We negate the expression to be able to flip the variable if the player can actually not move otherwise it depends on the order of the gameObjs
            # We also don't want the player to teleport to a side so we avoid checking for collisions while on air for x collisions only
            if not ((self.pos[0] + self.speed[0] + (self.width * caseSize[0]) <= (gameObj.pos[0] - 1) * caseSize[0]
                     or self.pos[0] + self.speed[0] + (self.width * caseSize[0]) >= (
                             gameObj.pos[0] + gameObj.width - 1) * caseSize[0])
                    or self.pos[1] >= gameObj.pos[1] * caseSize[1]
                    or self.pos[1] + self.height * caseSize[1] <= (gameObj.pos[1] - gameObj.height) * caseSize[
                        1]) and not self.jumping and self.onGround:

                if self.pos[1] + self.height * caseSize[1] <= (gameObj.pos[1] - gameObj.height) * caseSize[1]:
                    self.crouch()
                else:
                    self.pos[0] = (gameObj.pos[0] - 1 - self.width) * caseSize[0] + 1
                    self.canMoveRight = False


class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(args[0], args[1], args[2])

    def __repr__(self):
        return "<class : Player \n pos : {}>".format(self.pos)
