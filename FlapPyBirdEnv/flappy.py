from itertools import cycle
import random
import math
import sys
import numpy as np
import pygame
from pygame.locals import *


FPS = 30
SCREENWIDTH  = 288
SCREENHEIGHT = 512
PIPEGAPSIZE  = 100 # gap between upper and lower part of pipe
BASEY        = SCREENHEIGHT * 0.79
# image, sound and hitmask  dicts
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# list of all possible players (tuple of 3 positions of flap)
PLAYERS_LIST = (
    # red bird
    (
        'assets/sprites/redbird-upflap.png',
        'assets/sprites/redbird-midflap.png',
        'assets/sprites/redbird-downflap.png',
    ),
    # blue bird
    (
        'assets/sprites/bluebird-upflap.png',
        'assets/sprites/bluebird-midflap.png',
        'assets/sprites/bluebird-downflap.png',
    ),
    # yellow bird
    (
        'assets/sprites/yellowbird-upflap.png',
        'assets/sprites/yellowbird-midflap.png',
        'assets/sprites/yellowbird-downflap.png',
    ),
)

# list of backgrounds
BACKGROUNDS_LIST = (
    'assets/sprites/background-day.png',
    'assets/sprites/background-night.png',
)

# list of pipes
PIPES_LIST = (
    'assets/sprites/pipe-green.png',
    'assets/sprites/pipe-red.png',
)


try:
    xrange
except NameError:
    xrange = range


class Player:
    def __init__(self):
        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        self.images = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

        # hitmask for player
        self.hitmasks = (
            self.getHitmask(self.images[0]),
            self.getHitmask(self.images[1]),
            self.getHitmask(self.images[2]),
        )

        self.w = self.images[0].get_width()     # width of image (34)
        self.h = self.images[0].get_height()    # height of image (24)
        self.x = int(SCREENWIDTH * 0.2)         # placing bird in a fixed point
        self.y = int((SCREENHEIGHT - self.h) / 2)
        self.indexGen = cycle([0, 1, 2, 1])     # index of images to change respectively to show birds wings is flapping (changes each 5 iteration)
        self.index = 0                          # index of current image to blit on screen

        # player velocity, max velocity, downward accleration, accleration on flap
        self.velY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.maxVelY =  10   # max vel along Y, max descend speed
        self.minVelY =  -8   # min vel along Y, max ascend speed
        self.accY    =   1   # players downward accleration
        self.rot     =  45   # player's rotation
        self.velRot  =   3   # angular speed
        self.rotThr  =  20   # rotation threshold
        self.flapAcc =  -9   # players speed on flapping
        self.flapped = False # True when player flaps


    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in xrange(image.get_width()):
            mask.append([])
            for y in xrange(image.get_height()):
                mask[x].append(bool(image.get_at((x,y))[3]))
        return mask


class Pipe:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def set_point(self, x, y):
        self.x = x
        self.y = y


# Pair of upper and lower pipe (two Pipe object)
class Pipeline:
    def __init__(self):
        self.upper_pipe = Pipe(0, 0)
        self.lower_pipe = Pipe(0, 0)

    def set_upper(self, x, y):
        self.upper_pipe.set_point(x, y)

    def set_lower(self, x, y):
        self.lower_pipe.set_point(x, y)


class Base:
    def __init__(self):
        self.x = 0

        # amount by which base can maximum shift to left
        self.shift = IMAGES['base'].get_width() - IMAGES['background'].get_width()


class FlappyGame:
    def __init__(self):
        pygame.init()

        global SCREEN, FPSCLOCK
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # numbers sprites for score display
        IMAGES['numbers'] = (
            pygame.image.load('assets/sprites/0.png').convert_alpha(),
            pygame.image.load('assets/sprites/1.png').convert_alpha(),
            pygame.image.load('assets/sprites/2.png').convert_alpha(),
            pygame.image.load('assets/sprites/3.png').convert_alpha(),
            pygame.image.load('assets/sprites/4.png').convert_alpha(),
            pygame.image.load('assets/sprites/5.png').convert_alpha(),
            pygame.image.load('assets/sprites/6.png').convert_alpha(),
            pygame.image.load('assets/sprites/7.png').convert_alpha(),
            pygame.image.load('assets/sprites/8.png').convert_alpha(),
            pygame.image.load('assets/sprites/9.png').convert_alpha()
        )

        # game over sprite
        IMAGES['gameover'] = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        # base (ground) sprite
        IMAGES['base'] = pygame.image.load('assets/sprites/base.png').convert_alpha()

        # sounds
        if 'win' in sys.platform:
            soundExt = '.wav'
        else:
            soundExt = '.ogg'

        SOUNDS['die']    = pygame.mixer.Sound('assets/audio/die' + soundExt)
        SOUNDS['hit']    = pygame.mixer.Sound('assets/audio/hit' + soundExt)
        SOUNDS['point']  = pygame.mixer.Sound('assets/audio/point' + soundExt)
        SOUNDS['swoosh'] = pygame.mixer.Sound('assets/audio/swoosh' + soundExt)
        SOUNDS['wing']   = pygame.mixer.Sound('assets/audio/wing' + soundExt)

        self.score = self.loopIter = 0

        self.is_crashed = False    # gym variables
        self.reward = 0

        self.initRandomElements()
        self._base = Base()
        self._player = Player()


    def initRandomElements(self):
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random pipe sprites
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        IMAGES['pipe'] = (
            pygame.transform.flip(
                pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(), False, True),
            pygame.image.load(PIPES_LIST[pipeindex]).convert_alpha(),
        )

        # hismask for pipes
        HITMASKS['pipe'] = (
            self.getHitmask(IMAGES['pipe'][0]),
            self.getHitmask(IMAGES['pipe'][1]),
        )

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipeline1 = self.getRandomPipeline()
        newPipeline2 = self.getRandomPipeline()

        # list of upper pipes
        self.upperPipes = [
            Pipe(SCREENWIDTH + 200, newPipeline1.upper_pipe.y),
            Pipe(SCREENWIDTH + 200 + (SCREENWIDTH / 2), newPipeline2.upper_pipe.y)
        ]

        # list of lowerpipe
        self.lowerPipes = [
            Pipe(SCREENWIDTH + 200, newPipeline1.lower_pipe.y),
            Pipe(SCREENWIDTH + 200 + (SCREENWIDTH / 2), newPipeline2.lower_pipe.y)
        ]


    def action(self, action):
        self.mainGame(action)   # one iteration, one frame

        
    def evaluate(self):
        return self.reward


    def is_done(self):
        return self.is_crashed


    def observe(self):
        return np.array([[self.upperPipes[0].x - self._player.x + self._player.w,                   # Horizontal distance with pipeline
                        self.upperPipes[0].y + IMAGES['pipe'][0].get_height() - self._player.y,     # Vertical distance with upper pipe
                        self.lowerPipes[0].y - self._player.y + self._player.h,                     # Vertical distance with lower pipe
                        BASEY - self._player.y]])                                                   # Distance with ground


    def view(self):
        pygame.display.update()
        FPSCLOCK.tick(FPS)


    def mainGame(self, action):     # updates games one iteration
        loopIter = self.loopIter

        # get 2 new pipes to add to upperPipes lowerPipes list
        if len(self.upperPipes) == 0 and len(self.lowerPipes) == 0:
            newPipeline1 = self.getRandomPipeline()
            newPipeline2 = self.getRandomPipeline()

            # list of upper pipes
            self.upperPipes.extend([
                Pipe(SCREENWIDTH + 200, newPipeline1.upper_pipe.y),
                Pipe(SCREENWIDTH + 200 + (SCREENWIDTH / 2), newPipeline2.upper_pipe.y)
            ])

            # list of lowerpipe
            self.lowerPipes.extend([
                Pipe(SCREENWIDTH + 200, newPipeline1.lower_pipe.y),
                Pipe(SCREENWIDTH + 200 + (SCREENWIDTH / 2), newPipeline2.lower_pipe.y)
            ])


        pipeVelX = -4

        if(action == 1):
            if self._player.y > -2 * self._player.images[0].get_height():
                self._player.velY = self._player.flapAcc
                self._player.flapped = True
                SOUNDS['wing'].play()



        # check for crash here
        self.is_crashed = self.checkCrash(self.upperPipes, self.lowerPipes)
        self.is_crashed = self.is_crashed[0] or self.is_crashed[1]
        
        if self.is_crashed:
            self.reward = -2000
        elif self._player.y < 0:
            self.reward += (-50 * abs(self._player.y))
        else:
            self.reward = 10 + self.score * 200
        

        # check for score
        playerMidPos = self._player.x + self._player.w / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe.x + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                SOUNDS['point'].play()

        # playerIndex basex change
        if (loopIter + 1) % 3 == 0:
            self._player.index = next(self._player.indexGen)
        self.loopIter = (loopIter + 1) % 30
        self._base.x = -((-self._base.x + 100) % self._base.shift)

        # rotate the player
        if self._player.rot > -90:
            self._player.rot -= self._player.velRot

        # player's movement
        if self._player.velY < self._player.maxVelY and not self._player.flapped:
            self._player.velY += self._player.accY
        if self._player.flapped:
            self._player.flapped = False

            # more rotation to cover the threshold (calculated in visible rotation)
            self._player.rot = 45

        self._player.y += min(self._player.velY, BASEY - self._player.y - self._player.h)

        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe.x += pipeVelX
            lPipe.x += pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(self.upperPipes) > 0 and 0 < self.upperPipes[0].x < 5:
            newPipeline = self.getRandomPipeline()
            self.upperPipes.append(newPipeline.upper_pipe)
            self.lowerPipes.append(newPipeline.lower_pipe)

        # remove first pipe if its out of the screen
        if len(self.upperPipes) > 0 and self.upperPipes[0].x < -IMAGES['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe.x, uPipe.y))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe.x, lPipe.y))

        SCREEN.blit(IMAGES['base'], (self._base.x, BASEY))
        # print score so player overlaps the score
        self.showScore(self.score)

        # Player rotation has a threshold
        visibleRot = self._player.rotThr
        if self._player.rot <= self._player.rotThr:
            visibleRot = self._player.rot
        
        playerSurface = pygame.transform.rotate(self._player.images[self._player.index], visibleRot)
        SCREEN.blit(playerSurface, (self._player.x, self._player.y))


    def getRandomPipeline(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
        gapY += int(BASEY * 0.2)
        pipeHeight = IMAGES['pipe'][0].get_height()
        pipeX = SCREENWIDTH + 10

        pipeline = Pipeline()
        pipeline.set_upper(pipeX, gapY - pipeHeight)
        pipeline.set_lower(pipeX, gapY + PIPEGAPSIZE)
        
        return pipeline


    def showScore(self, score):
        """displays score in center of screen"""
        scoreDigits = [int(x) for x in list(str(score))]
        totalWidth = 0 # total width of all numbers to be printed

        for digit in scoreDigits:
            totalWidth += IMAGES['numbers'][digit].get_width()

        Xoffset = (SCREENWIDTH - totalWidth) / 2

        for digit in scoreDigits:
            SCREEN.blit(IMAGES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.1))
            Xoffset += IMAGES['numbers'][digit].get_width()


    def checkCrash(self, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes.
            Returns: [hasCrashed, groundCrash]
        """

        # if player crashes into ground
        if self._player.y + self._player.h >= BASEY - 1:
            return [True, True]
        else:

            playerRect = self._player.get_rect()
            pipeW = IMAGES['pipe'][0].get_width()
            pipeH = IMAGES['pipe'][0].get_height()

            for uPipe, lPipe in zip(upperPipes, lowerPipes):    # ==> for each Pipeline(pairs)
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe.x, uPipe.y, pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe.x, lPipe.y, pipeW, pipeH)

                # player and upper/lower pipe hitmasks
                pHitMask = self._player.hitmasks[self._player.index]
                uHitmask = HITMASKS['pipe'][0]
                lHitmask = HITMASKS['pipe'][1]

                # if bird collided with upipe or lpipe
                uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)

                if uCollide or lCollide:
                    return [True, False]

        return [False, False]


    def pixelCollision(self, rect1, rect2, hitmask1, hitmask2):
        """Checks if two objects collide and not just their rects"""
        rect = rect1.clip(rect2)

        if rect.width == 0 or rect.height == 0:
            return False

        x1, y1 = rect.x - rect1.x, rect.y - rect1.y
        x2, y2 = rect.x - rect2.x, rect.y - rect2.y

        for x in xrange(rect.width):
            for y in xrange(rect.height):
                if hitmask1[x1+x][y1+y] and hitmask2[x2+x][y2+y]:
                    return True
        return False


    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in xrange(image.get_width()):
            mask.append([])
            for y in xrange(image.get_height()):
                mask[x].append(bool(image.get_at((x,y))[3]))
        return mask
