#!../venv/bin/python
from itertools import cycle
import random
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

# Static size definition for physics mode
BASEW = 336
BACKW = 288
PIPEH = 320
PIPEW = 52
PLAYERH = 24
PLAYERW = 34

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

class FlappyGame:
    def __init__(self, render=True):
        self.render = render
        if render:
            self.initStaticGraphics()
            self.initRandomGraphics()
        self.initGame()
        

    def initStaticGraphics(self):
        global SCREEN, FPSCLOCK, IMAGES, SOUNDS
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
        pygame.display.set_caption('Deep QL Flappy Bird')

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
        # message sprite for welcome screen
        IMAGES['message'] = pygame.image.load('assets/sprites/message.png').convert_alpha()
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


    def initRandomGraphics(self):
        # select random background sprites
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = pygame.image.load(BACKGROUNDS_LIST[randBg]).convert()

        # select random player sprites
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            pygame.image.load(PLAYERS_LIST[randPlayer][0]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][1]).convert_alpha(),
            pygame.image.load(PLAYERS_LIST[randPlayer][2]).convert_alpha(),
        )

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

        # hitmask for player
        HITMASKS['player'] = (
            self.getHitmask(IMAGES['player'][0]),
            self.getHitmask(IMAGES['player'][1]),
            self.getHitmask(IMAGES['player'][2]),
        )


    def showWelcomeAnimation(self):
        """Shows welcome screen animation of flappy bird"""
        # index of player to blit on screen
        playerIndex = 0
        playerIndexGen = cycle([0, 1, 2, 1])
        # iterator used to change playerIndex after every 5th iteration
        loopIter = 0

        playerx = int(SCREENWIDTH * 0.2)
        playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)

        messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
        messagey = int(SCREENHEIGHT * 0.12)

        basex = 0
        # amount by which base can maximum shift to left
        baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()

        # player shm for up-down motion on welcome screen
        playerShmVals = {'val': 0, 'dir': 1}

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    # make first flap sound and return values for mainGame
                    SOUNDS['wing'].play()
                    return {
                        'playery': playery + playerShmVals['val'],
                        'basex': basex,
                        'playerIndexGen': playerIndexGen,
                    }

            # adjust playery, playerIndex, basex
            if (loopIter + 1) % 5 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 4) % baseShift)
            playerShm(playerShmVals)

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0,0))
            SCREEN.blit(IMAGES['player'][playerIndex],
                        (playerx, playery + playerShmVals['val']))
            SCREEN.blit(IMAGES['message'], (messagex, messagey))
            SCREEN.blit(IMAGES['base'], (basex, BASEY))

            pygame.display.update()
            FPSCLOCK.tick(FPS)


        score = playerIndex = loopIter = 0
        playerIndexGen = movementInfo['playerIndexGen']
        playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']

        basex = movementInfo['basex']
        if render:
            baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
        else:
            baseShift = BASEW - BACKW

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = getRandomPipe()
        newPipe2 = getRandomPipe()

        # list of upper pipes
        upperPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        lowerPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
        ]

        pipeVelX = -4

        # player velocity, max velocity, downward accleration, accleration on flap
        playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        playerMaxVelY =  10   # max vel along Y, max descend speed
        playerMinVelY =  -8   # min vel along Y, max ascend speed
        playerAccY    =   1   # players downward accleration
        playerRot     =  45   # player's rotation
        playerVelRot  =   3   # angular speed
        playerRotThr  =  20   # rotation threshold
        playerFlapAcc =  -9   # players speed on flapping
        playerFlapped = False # True when player flaps


        while True:
            action = 0
            if render:
                for event in pygame.event.get():
                    if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                        pygame.quit()
                        sys.exit()
            
            # action = ?
            updateGame(action, render=render)
            FPSCLOCK.tick(FPS)


        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery > -2 * IMAGES['player'][0].get_height():
                        playerVelY = playerFlapAcc
                        self.playerFlapped = True
                        SOUNDS['wing'].play()

            # check for crash here
            crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex},
                                upperPipes, lowerPipes)
            if crashTest[0]:
                return {
                    'y': playery,
                    'groundCrash': crashTest[1],
                    'basex': basex,
                    'upperPipes': upperPipes,
                    'lowerPipes': lowerPipes,
                    'score': score,
                    'playerVelY': playerVelY,
                    'playerRot': playerRot
                }

            # check for score
            playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    score += 1
                    SOUNDS['point'].play()

            # playerIndex basex change
            if (loopIter + 1) % 3 == 0:
                playerIndex = next(playerIndexGen)
            loopIter = (loopIter + 1) % 30
            basex = -((-basex + 100) % baseShift)

            # rotate the player
            if playerRot > -90:
                playerRot -= playerVelRot

            # player's movement
            if playerVelY < playerMaxVelY and not self.playerFlapped:
                playerVelY += playerAccY
            if self.playerFlapped:
                self.playerFlapped = False

                # more rotation to cover the threshold (calculated in visible rotation)
                playerRot = 45

            playerHeight = IMAGES['player'][playerIndex].get_height()
            playery += min(playerVelY, BASEY - playery - playerHeight)
    
            # move pipes to left
            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                uPipe['x'] += pipeVelX
                lPipe['x'] += pipeVelX

            # add new pipe when first pipe is about to touch left of screen
            if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
                newPipe = getRandomPipe()
                upperPipes.append(newPipe[0])
                lowerPipes.append(newPipe[1])

            # remove first pipe if its out of the screen
            if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
                upperPipes.pop(0)
                lowerPipes.pop(0)

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0,0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            # print score so player overlaps the score
            showScore(score)

            # Player rotation has a threshold
            visibleRot = playerRotThr
            if playerRot <= playerRotThr:
                visibleRot = playerRot
            
            playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
            SCREEN.blit(playerSurface, (playerx, playery))

            pygame.display.update()
            FPSCLOCK.tick(FPS)


    def showGameOverScreen(self, crashInfo):
        """crashes the player down ans shows gameover image"""
        score = crashInfo['score']
        playerx = SCREENWIDTH * 0.2
        playery = crashInfo['y']
        playerHeight = IMAGES['player'][0].get_height()
        playerVelY = crashInfo['playerVelY']
        playerAccY = 2
        playerRot = crashInfo['playerRot']
        playerVelRot = 7

        basex = crashInfo['basex']

        upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

        # play hit and die sounds
        SOUNDS['hit'].play()
        if not crashInfo['groundCrash']:
            SOUNDS['die'].play()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                    if playery + playerHeight >= BASEY - 1:
                        return

            # player y shift
            if playery + playerHeight < BASEY - 1:
                playery += min(playerVelY, BASEY - playery - playerHeight)

            # player velocity change
            if playerVelY < 15:
                playerVelY += playerAccY

            # rotate only when it's a pipe crash
            if not crashInfo['groundCrash']:
                if playerRot > -90:
                    playerRot -= playerVelRot

            # draw sprites
            SCREEN.blit(IMAGES['background'], (0,0))

            for uPipe, lPipe in zip(upperPipes, lowerPipes):
                SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
                SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

            SCREEN.blit(IMAGES['base'], (basex, BASEY))
            showScore(score)

            


            playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
            SCREEN.blit(playerSurface, (playerx,playery))
            SCREEN.blit(IMAGES['gameover'], (50, 180))

            FPSCLOCK.tick(FPS)
            pygame.display.update()


    def playerShm(self, playerShm):
        """oscillates the value of playerShm['val'] between 8 and -8"""
        if abs(playerShm['val']) == 8:
            playerShm['dir'] *= -1

        if playerShm['dir'] == 1:
            playerShm['val'] += 1
        else:
            playerShm['val'] -= 1


    def getRandomPipe(self):
        """returns a randomly generated pipe"""
        # y of gap between upper and lower pipe
        gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
        gapY += int(BASEY * 0.2)
        pipeHeight = PIPEH
        pipeX = SCREENWIDTH + 10

        return [
            {'x': pipeX, 'y': gapY - pipeHeight},  # upper pipe
            {'x': pipeX, 'y': gapY + PIPEGAPSIZE}, # lower pipe
        ]


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


    def checkCrash(self, player, upperPipes, lowerPipes):
        """returns True if player collders with base or pipes."""
        pi = player['index']

        if self.render:
            player['w'] = IMAGES['player'][0].get_width()
            player['h'] = IMAGES['player'][0].get_height()
        else:
            player['w'] = PLAYERW
            player['h'] = PLAYERH

        # if player crashes into ground
        if player['y'] + player['h'] >= BASEY - 1:
            return [True, True]
        else:
            playerRect = pygame.Rect(player['x'], player['y'],
                        player['w'], player['h'])

            if self.render:           
                pipeW = IMAGES['pipe'][0].get_width()
                pipeH = IMAGES['pipe'][0].get_height()
            else:
                pipeW = PIPEW
                pipeH = PIPEH

            for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
                # upper and lower pipe rects
                uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
                lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)

                if self.render:
                    # player and upper/lower pipe hitmasks
                    pHitMask = HITMASKS['player'][pi]
                    uHitmask = HITMASKS['pipe'][0]
                    lHitmask = HITMASKS['pipe'][1]

                    # if bird collided with upipe or lpipe
                    uCollide = self.pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
                    lCollide = self.pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)
                else:
                    uCollide = self.sizeCollision(playerRect, uPipeRect)
                    lCollide = self.sizeCollision(playerRect, lPipeRect)

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


    def sizeCollision(self, rect1, rect2):
        """Checks if two objects collide by their size"""

        # player 4 points
        p1 = (rect1.x + PLAYERW, rect1.y)
        p2 = (rect1.x, rect1.y + PLAYERH)
        p3 = (rect1.x + PLAYERW, rect1.y)
        p4 = (rect1.x + PLAYERW, rect1.y + PLAYERH)

        # point 1 and 4 of pipe
        q1 = (rect2.x, rect2.y)
        q2 = (rect2.x + PIPEW, rect2.y + PIPEH)

        # checking either any of 4 points of bird is inside the pipe rect
        if self.isInsideRect(p1, (q1, q2)):
            return True

        if self.isInsideRect(p2, (q1, q2)):
            return True

        if self.isInsideRect(p3, (q1, q2)):
            return True

        if self.isInsideRect(p4, (q1, q2)):
            return True
        
        return False


    def isInsideRect(self, p, rect):
        q1 = rect[0]
        q2 = rect[1]
        return p[0] >= q1[0] and p[0] <= q2[0] and p[1] >= q1[1] and p[1] <= q2[1]


    def getHitmask(self, image):
        """returns a hitmask using an image's alpha."""
        mask = []
        for x in xrange(image.get_width()):
            mask.append([])
            for y in xrange(image.get_height()):
                mask[x].append(bool(image.get_at((x,y))[3]))
        return mask


#################################################
##                                             ##
##  Functions needed for training and playing  ##
##                                             ##
#################################################

    def initGame(self):
        """ Initialize game starting coordinates """
        # index of player to blit on screen
        self.score, self.loopIter, self.playerIndex = 0, 0, 0
        self.playerIndexGen = cycle([0, 1, 2, 1])
        # iterator used to change playerIndex after every 5th iteration

        self.playerx = int(SCREENWIDTH * 0.2)
        if self.render:
            self.playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
        else:
            self.playery = int((SCREENHEIGHT - PLAYERH) / 2)

        self.basex = 0

        # player shm for up-down motion on welcome screen
        playerShmVals = {'val': 0, 'dir': 1}
        self.playery += playerShmVals['val']

        if self.render:
            self.baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
        else:
            self.baseShift = BASEW - BACKW

        # get 2 new pipes to add to upperPipes lowerPipes list
        newPipe1 = self.getRandomPipe()
        newPipe2 = self.getRandomPipe()

        # list of upper pipes
        self.upperPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
        ]

        # list of lowerpipe
        self.lowerPipes = [
            {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
            {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
        ]

        self.pipeVelX = -4
        self.isCrashed = False
        self.last_action = 0

        # player velocity, max velocity, downward accleration, accleration on flap
        self.playerVelY    =  -9   # player's velocity along Y, default same as playerFlapped
        self.playerMaxVelY =  10   # max vel along Y, max descend speed
        self.playerMinVelY =  -8   # min vel along Y, max ascend speed
        self.playerAccY    =   1   # players downward accleration
        self.playerRot     =  45   # player's rotation
        self.playerVelRot  =   3   # angular speed
        self.playerRotThr  =  20   # rotation threshold
        self.playerFlapAcc =  -9   # players speed on flapping
        self.playerFlapped = False # True when player flaps
        self.visibleRot = self.playerRotThr


    def resetGame(self):
        self.initRandomGraphics()
        self.initGame()


    def updateGame(self, action):
        
        if self.is_done():
            print('Game Over!')
            return

        self.last_action = action

        if self.render:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        if action == 1:
            if self.render and self.playery > -2 * IMAGES['player'][0].get_height():
                self.playerVelY = self.playerFlapAcc
                self.playerFlapped = True
                SOUNDS['wing'].play()
            elif self.playery > -2 * PLAYERH:
                self.playerVelY = self.playerFlapAcc
                self.playerFlapped = True


        # check for crash here
        self.isCrashed = self.checkCrash({'x': self.playerx, 'y': self.playery, 'index': self.playerIndex},
                            self.upperPipes, self.lowerPipes)[0]
        
        if self.isCrashed:
            return
        
        # updating game physics
        # playerIndex basex change
        if (self.loopIter + 1) % 3 == 0:
            self.playerIndex = next(self.playerIndexGen)
        self.loopIter = (self.loopIter + 1) % 30
        self.basex = -((-self.basex + 100) % self.baseShift)

        # rotate the player
        if self.playerRot > -90:
            self.playerRot -= self.playerVelRot

        # player's movement
        if self.playerVelY < self.playerMaxVelY and not self.playerFlapped:
            self.playerVelY += self.playerAccY
        if self.playerFlapped:
            self.playerFlapped = False

        # more rotation to cover the threshold (calculated in visible rotation)
        self.playerRot = 45

        if self.render:
            self.playerHeight = IMAGES['player'][self.playerIndex].get_height()
        else:
            self.playerHeight = PLAYERH

        self.playery += min(self.playerVelY, BASEY - self.playery - self.playerHeight)
    
        # move pipes to left
        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            uPipe['x'] += self.pipeVelX
            lPipe['x'] += self.pipeVelX

        # add new pipe when first pipe is about to touch left of screen
        if len(self.upperPipes) > 0 and 0 < self.upperPipes[0]['x'] < 5:
            newPipe = self.getRandomPipe()
            self.upperPipes.append(newPipe[0])
            self.lowerPipes.append(newPipe[1])

        # remove first pipe if its out of the screen
        if self.render and len(self.upperPipes) > 0 and self.upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)
        elif len(self.upperPipes) > 0 and self.upperPipes[0]['x'] < -PIPEW:
            self.upperPipes.pop(0)
            self.lowerPipes.pop(0)

        # Player rotation has a threshold
        self.visibleRot = self.playerRotThr
        if self.playerRot <= self.playerRotThr:
            self.visibleRot = self.playerRot

        if self.render:
            self.view()


    def action(self, action):
        self.updateGame(action)   # one iteration, one frame

        
    def evaluate(self):
        if self.isCrashed:
            return -5

        if self.render:                                # passed a pipe
            playerMidPos = self.playerx + IMAGES['player'][0].get_width() / 2
            for pipe in self.upperPipes:
                pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    return 1
        else:
            playerMidPos = self.playerx + PLAYERW / 2
            for pipe in self.upperPipes:
                pipeMidPos = pipe['x'] + PIPEW / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    return 1

        
        if self.upperPipes[0]['x'] + PIPEW - self.playerx > 0:  # passed the pipe
            p = 0
        else:
            p = 1

        # l_y = self.lowerPipes[p]['y']
        # u_y = self.upperPipes[p]['y'] + PIPEH
        # distance = abs((self.playery + PLAYERH) - (u_y + (l_y - u_y) / 2))

        # return 0.1 - distance * 0.0001
        return 0.01


    def is_done(self):
        return self.isCrashed


    def observe(self):
        if self.upperPipes[0]['x'] + PIPEW - self.playerx > 0:  # passed the pipe
            p = 0
        else:
            p = 1

        return np.array([[self.upperPipes[p]['x'] - (self.playerx + PLAYERW),          # Horizontal distance with pipeline
                        self.lowerPipes[p]['y'] - (self.playery + PLAYERH)]])          # Vertical distance with lower pipe


    def view(self):
        if not self.render:
            print('Render mode is not enabled.')
            return

        # check for score
        playerMidPos = self.playerx + IMAGES['player'][0].get_width() / 2
        for pipe in self.upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                self.score += 1
                SOUNDS['point'].play()

        # draw sprites
        SCREEN.blit(IMAGES['background'], (0,0))

        for uPipe, lPipe in zip(self.upperPipes, self.lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))

        SCREEN.blit(IMAGES['base'], (self.basex, BASEY))
        # print score so player overlaps the score
        self.showScore(self.score)

        playerSurface = pygame.transform.rotate(IMAGES['player'][self.playerIndex], self.visibleRot)
        SCREEN.blit(playerSurface, (self.playerx, self.playery))

        pygame.display.update()
        FPSCLOCK.tick(FPS)
