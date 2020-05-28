import numpy as np
from pygame.locals import *
from GameObjects import Box
import pygame


def speedFunc(maxSpeed, t, timeNeededToReachMax):
    if timeNeededToReachMax == 0:
        return 0
    else:
        return maxSpeed * np.tanh(2 * t / timeNeededToReachMax)


def jumpingSpeed(F, m):
    return F / m


def slowSpeed(maxSpeed, t, timeNeededToStop):
    if timeNeededToStop == 0:
        return 0
    else:
        return maxSpeed * np.exp(-t / timeNeededToStop)


def fallingSpeed(g, t):
    return g * t


class Actor:
    def __init__(self, *args):
        """
        Constructor of the Actor class
        :param args: args[0] the width of the actor in tiles, args[1] the height, args[2] the pos in pixels
        """
        self.width = args[0]
        self.height = args[1]
        self.fullHeight = args[1]
        self.color = np.array((30, 30, 200))  # not useful except for rendering an actor as a square of a certain color
        self.weight = 1
        self.jumpingStrength = 10
        self.direction = [None, None]
        self.onScreen = True
        self.life = 1

        self.speed = np.array((0.0, 0.0), dtype=np.float)  # en pixels/s used to store what speed the player should have
        self.movementSpeed = np.array((0.0, 0.0), dtype=np.float)  # used to move the player
        self.pos = np.array(args[2])
        self.startPos = tuple(args[2])

        # Moving states of the actor
        self.onGround = False
        self.canMoveLeft = True
        self.canMoveRight = True
        self.canMoveUp = True
        self.canUncrouch = True
        self.jumping = False
        self.crouched = False
        self.controllable = True

        self.maxHorizontalSpeed = 6  # en pixels/s
        self.maxVerticalSpeed = 5
        self.fallbackSpeed = 6
        self.secondsToMaxHorizontalSpeed = .5
        self.secondsToStop = .1
        self.recoveryTime = .5  # Time where the player is uncontrollable after upon taking damage (in seconds)

        self.secondsMovingLeft = 0
        self.secondsMovingRight = 0
        self.secondsStopping = 0
        self.secondsFalling = 0
        self.peakSpeed = .0
        self.secondsRecovering = .0

        self.sprite = None
        self.debugMode = False

    def move(self, keys, dt, sizeRatio, gameScale):
        """
        :param keys: list of keys pressed
        :param time: current time of the game since init not to make speed frame dependent
        """
        if keys[K_LEFT] and keys[K_RIGHT]:
            self.speed[0] = 0
            self.peakSpeed = .0
            self.secondsMovingLeft = 0
            self.secondsMovingRight = 0

        elif keys[K_LEFT] and self.canMoveLeft:
            if self.direction[0] != K_LEFT:
                self.direction[0] = K_LEFT
                self.secondsMovingLeft = 0
                self.speed[0] = 0
                self.peakSpeed = .0

            if self.speed[0] > -self.maxHorizontalSpeed:
                self.speed[0] = (-speedFunc(self.maxHorizontalSpeed, self.secondsMovingLeft,
                                            self.secondsToMaxHorizontalSpeed)) * sizeRatio[0] * gameScale
                self.secondsMovingLeft += dt
                self.peakSpeed = self.speed[0]

        elif keys[K_RIGHT] and self.canMoveRight:
            if self.direction[0] != K_RIGHT:
                self.direction[0] = K_RIGHT
                self.secondsMovingRight = 0
                self.speed[0] = 0
                self.peakSpeed = .0

            if self.speed[0] < self.maxHorizontalSpeed:
                self.speed[0] = (speedFunc(self.maxHorizontalSpeed, self.secondsMovingRight,
                                           self.secondsToMaxHorizontalSpeed)) * sizeRatio[0] * gameScale
                self.secondsMovingRight += dt
                self.peakSpeed = self.speed[0]

    def fall(self, dt, sizeRatio, gameScale):
        self.speed[1] += (fallingSpeed(-self.maxVerticalSpeed * self.weight, self.secondsFalling)) * sizeRatio[
            1] * gameScale
        self.secondsFalling += dt

    def jump(self, sizeRatio, gameScale, speed=None):
        if self.onGround and not self.jumping:
            self.jumping = True
            self.onGround = False
            if speed == None:
                self.speed[1] += (jumpingSpeed(self.jumpingStrength, self.weight)) * sizeRatio[1] * gameScale
            else:
                self.speed[1] += (jumpingSpeed(speed, self.weight)) * sizeRatio[1] * gameScale

    def reset(self):
        self.pos = np.array(self.startPos)
        self.speed = np.array((0.0, 0.0), dtype=np.float)
        self.direction = [None, None]

        self.onGround = False
        self.canMoveLeft = True
        self.canMoveRight = True
        self.canMoveUp = True
        self.canUncrouch = True
        self.jumping = False
        self.crouched = False
        self.height = self.fullHeight

        self.secondsMovingLeft = 0
        self.secondsMovingRight = 0
        self.secondsStopping = 0
        self.secondsFalling = 0

    def crouch(self):
        if not self.crouched:
            self.crouched = True
            self.height = 2 * self.height / 3

    def unCrouch(self):
        if self.crouched:
            self.crouched = False
            self.height = 3 * self.height / 2

    def draw(self, screen, coords, width, height):
        screen.blit(pygame.transform.scale(self.sprite, (int(width), int(height))), coords)
        if self.debugMode:
            pygame.draw.rect(screen, (200, 0, 0), pygame.Rect(coords, (width, height)), 2)
            pygame.draw.ellipse(screen, (0, 0, 0), pygame.Rect(coords - (3, 3 - height), (6, 6)), 0)
            screen.blit(pygame.font.SysFont("Consolas", 12).render(
                "{0}, {1}".format(self.pos, self.speed), False, (0, 0, 0)), coords - (50, 20))

            if isinstance(self, Player):
                screen.blit(pygame.font.SysFont("Consolas", 12).render(
                    "canMoveUp : {0} canMoveLeft : {1} canMoveRight : {2} onGround : {3}".format(
                        self.canMoveUp, self.canMoveLeft, self.canMoveRight, self.onGround), False, (0, 0, 0)),
                    (200, 20))

    def checkPositionCollisions(self, gameObjects, tileSize):
        # Temporary vars in order to make collision detection independent from gameObjects order and improve efficiency
        # TODO Make an improvement on collision detection to avoid checking all objects on screen
        actor = self
        onGround = False
        canMoveUp = True
        canMoveRight = True
        canMoveLeft = True
        canUncrouch = True
        if self.jumping:
            jumping = True
        else:
            jumping = False

        tmpSpeed = np.int32(np.round(actor.speed))
        tmpPos = actor.pos

        for gameObj in gameObjects:

            if gameObj.onScreen:
                xCollide, yCollide = False, False

                # Check if player and obj overlap on the x direction
                if (actor.pos[1] + tmpSpeed[1] <= (gameObj.pos[1] + gameObj.height) * tileSize[1]
                        and actor.pos[1] + tmpSpeed[1] + actor.height * tileSize[1] >= gameObj.pos[1] * tileSize[1]):
                    xCollide = True

                # Check if player and obj overlap on the y direction
                if (actor.pos[0] + tmpSpeed[0] <= (gameObj.pos[0] + gameObj.width) * tileSize[0]
                        and actor.pos[0] + tmpSpeed[0] + actor.width * tileSize[0] >= gameObj.pos[0] * tileSize[0]):
                    yCollide = True

                    above = actor.pos[1] >= (gameObj.pos[1] + gameObj.height) * tileSize[1]
                    below = actor.pos[1] + actor.height * tileSize[1] <= gameObj.pos[1] * tileSize[1]

                    if below:
                        if actor.crouched:
                            canUncrouch = actor.pos[1] + actor.fullHeight * tileSize[1] <= gameObj.pos[1] * tileSize[1]

                # If they overlap on both x and y axis they collide
                if xCollide and yCollide:

                    # Look where the player is from the object
                    above = actor.pos[1] >= (gameObj.pos[1] + gameObj.height) * tileSize[1]
                    below = actor.pos[1] + actor.height * tileSize[1] <= gameObj.pos[1] * tileSize[1]
                    right = actor.pos[0] >= (gameObj.pos[0] + gameObj.width) * tileSize[0]
                    left = actor.pos[0] + actor.width * tileSize[0] <= gameObj.pos[0] * tileSize[0]

                    # if the player is on the left it means that he was moving to the right so
                    # we put him against the object and removes his speed while changing his canMoveRight state
                    if above:
                        onGround = True
                        tmpPos[1] = (gameObj.pos[1] + gameObj.height) * tileSize[1]
                        self.movementSpeed[1] = 0
                    elif below:
                        canMoveUp = False
                        jumping = False
                        tmpPos[1] = (gameObj.pos[1] - actor.height) * tileSize[1]
                        self.movementSpeed[1] = 0
                        self.speed[1] /= 1.5

                        if isinstance(actor, Player) and isinstance(gameObj, Box) and self.jumping:
                            gameObj.activate()


                    elif left:
                        canMoveRight = False
                        tmpPos[0] = (gameObj.pos[0] - actor.width) * tileSize[0]
                        self.movementSpeed[0] = 0
                    elif right:
                        canMoveLeft = False
                        tmpPos[0] = (gameObj.pos[0] + gameObj.width) * tileSize[0]
                        self.movementSpeed[0] = 0

        self.onGround = onGround
        self.canMoveUp = canMoveUp
        self.canMoveRight = canMoveRight
        self.canMoveLeft = canMoveLeft
        self.canUncrouch = canUncrouch
        self.jumping = jumping
        self.pos = tmpPos

    def actorCollision(self, actors, tileSize):
        testedActor = self

        for actor in actors:

            if actor.onScreen:
                xCollide, yCollide = False, False

                # Check if player and obj overlap on the x direction
                if (testedActor.pos[1] + testedActor.speed[1] <= actor.pos[1] + actor.speed[1] + (
                        actor.height * tileSize[1]) and testedActor.pos[1] + testedActor.speed[1] + testedActor.height *
                        tileSize[1] >= actor.pos[1] + actor.speed[1]):
                    xCollide = True

                # Check if player and obj overlap on the y direction
                if (testedActor.pos[0] + testedActor.speed[0] <= actor.pos[0] + actor.speed[0] + (
                        actor.width * tileSize[0]) and testedActor.pos[0] + testedActor.speed[0] + testedActor.width *
                        tileSize[0] >= actor.pos[0] + actor.speed[0]):
                    yCollide = True

                # If they overlap on both x and y axis they collide
                if xCollide and yCollide:

                    # Above
                    if testedActor.pos[1] >= actor.pos[1] + actor.height * tileSize[1]:
                        testedActor.pos[1] = actor.pos[1] + actor.height * tileSize[1]

                        self.secondsFalling = 0

                        testedActor.movementSpeed[1] = 0
                        testedActor.speed[1] = testedActor.fallbackSpeed
                        actor.life -= 1

                    else:
                        self.controllable = False

                        if isinstance(testedActor, Player):
                            testedActor.life -= 1

                        # Reset movements timings
                        self.secondsStopping = 0
                        self.secondsMovingLeft = 0
                        self.secondsMovingRight = 0
                        self.secondsFalling = 0

                        # Reset speed
                        testedActor.movementSpeed[0] = 0
                        testedActor.movementSpeed[1] = 0

                        # Below
                        if testedActor.pos[1] + testedActor.height * tileSize[1] <= actor.pos[1]:
                            testedActor.pos[1] = actor.pos[1] - testedActor.height * tileSize[1]
                            testedActor.speed[1] = -testedActor.fallbackSpeed

                        # Left
                        elif testedActor.pos[0] + testedActor.width * tileSize[0] <= actor.pos[0]:
                            testedActor.pos[0] = actor.pos[0] - testedActor.width * tileSize[0]
                            testedActor.speed[1] = testedActor.fallbackSpeed

                        # Right
                        elif testedActor.pos[0] >= actor.pos[0] + actor.width * tileSize[0]:
                            testedActor.pos[0] = actor.pos[0] + actor.width * tileSize[0]
                            testedActor.speed[1] = testedActor.fallbackSpeed

                        # Simulate fallback from taking damages
                        if testedActor.direction[0] == K_LEFT:
                            testedActor.speed[0] = testedActor.fallbackSpeed
                        elif testedActor.direction[0] == K_RIGHT:
                            testedActor.speed[0] = -testedActor.fallbackSpeed
                        else:
                            testedActor.direction[0] = K_LEFT
                            testedActor.speed[0] = -testedActor.fallbackSpeed

                        testedActor.peakSpeed = testedActor.speed[0]


class Player(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(args[0], args[1], args[2])
        self.sprite = pygame.image.load(r'assets\balkany.png')
        self.onScreen = True
        self.life = 1

    def update(self, keys, dt, sizeRatio, gameObjects, actors, tileSize, gameScale):
        if not self.controllable:
            self.secondsRecovering += dt

        if self.secondsRecovering > self.recoveryTime:
            self.controllable = True
            self.secondsRecovering = .0

        if (keys[K_RIGHT] or keys[K_LEFT]) and self.controllable:
            self.secondsStopping = 0
            self.move(keys, dt, sizeRatio, gameScale)
        else:
            self.secondsMovingRight = 0
            self.secondsMovingLeft = 0

            if abs(self.speed[0]) < .01 and self.direction[0]:
                self.speed[0] = 0
                self.secondsStopping = 0
                self.direction[0] = None

            if self.direction[0] == K_LEFT:
                self.speed[0] = slowSpeed(self.peakSpeed, self.secondsStopping, self.secondsToStop) * sizeRatio[0]
                self.secondsStopping += dt
            elif self.direction[0] == K_RIGHT:
                self.speed[0] = slowSpeed(self.peakSpeed, self.secondsStopping, self.secondsToStop) * sizeRatio[0]
                self.secondsStopping += dt

        if not self.onGround:
            self.fall(dt, sizeRatio, gameScale)

        if self.onGround:
            self.jumping = False
            self.speed[1] = 0
            self.secondsFalling = 0

        if (keys[K_SPACE] or keys[K_KP0]) and self.canMoveUp and self.controllable:
            self.jump(sizeRatio, gameScale)

        if keys[K_r]:
            self.reset()

        if keys[K_DOWN] and self.controllable:
            self.crouch()
        elif self.canUncrouch:
            self.unCrouch()

        if self.speed[1] > 0:
            self.direction[1] = K_UP
        else:
            self.direction[1] = K_DOWN

        self.movementSpeed = np.array(self.speed.tolist(), dtype=np.float)
        self.checkPositionCollisions(gameObjects, tileSize)

        if self.controllable:
            self.actorCollision(actors, tileSize)

        self.pos += np.int32(np.round(self.movementSpeed))


class Enemy(Actor):
    def __init__(self, *args, **kwargs):
        super().__init__(args[0], args[1], args[2])
        self.sprite = pygame.image.load(r'assets\police.jpg')
        self.life = 1

    def update(self, dt, sizeRatio, gameObjects, tileSize, gameScale):

        if not self.onGround:
            self.fall(dt, sizeRatio, gameScale)
        else:
            self.speed[1] = 0

        self.movementSpeed = np.array(self.speed.tolist(), dtype=np.float)
        self.checkPositionCollisions(gameObjects, tileSize)
        self.pos += np.int32(np.round(self.movementSpeed))
