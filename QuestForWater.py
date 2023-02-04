# Quest For Water
# Global Game Jam 2023
# Oslo
# Jordi Santonja
import pgzrun

from pygame import image, Color, Surface
from random import randint

gridWidth, gridHeight = 8, 6
grid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
tileSize = 80
gridStart = (116, 88)

waterGrid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]

startButton = (4,520)
endButton = (4 + 104, 520 + 48)
overButton = False

numberNextTiles = 5
nextTilesStart = (11, 88)
nextTiles = [randint(1, 15) for y in range(numberNextTiles)]

tileMouse = (-1, -1)
mousePosition = (0,0)
firstPosition = (3, 0)
tileSelected = -1

totalTime = 0.0
INTRO = 0
PLAYING = 1
CHECKING = 2
GAME_OVER_TIME = 3
GAME_OVER_LOOP = 4
GAME_OVER_NOWATER = 5
GAME_OVER_OPEN = 6
gameStatus = INTRO

posLeaves = (16, 48)
distLeaves = 80
maxLeaves = 10
levelMaxTime = 200
level = 1

timeChecking = 0
timeToCheck = 0.15

points = 0

def SetLevel():
    global totalTime, levelMaxTime, waterGrid, grid
    totalTime = 0
    levelMaxTime = 300 * pow(0.85, level)
    grid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
    waterGrid = [[0 for x in range(gridWidth)] for y in range(gridHeight)]
    if level < gridHeight - 1:
        waterLevel = 1 + level
        for x in range(gridWidth):
            waterGrid[waterLevel][x] = 2
        for y in range(waterLevel + 1, gridHeight):
            for x in range(gridWidth):
                waterGrid[y][x] = 4
    else:
        posWater = randint(0, gridWidth - 2)
        waterGrid[gridHeight - 1][posWater] = 1
        waterGrid[gridHeight - 1][posWater + 1] = 3

def draw():
    global gameStatus
    if gameStatus == INTRO:
        screen.blit('background_intro', (0,0))
    else:
        screen.blit('background', (0,0))
        for y in range(gridHeight):
            for x in range(gridWidth):
                if waterGrid[y][x] != 0:
                    screen.blit('water_'+str(waterGrid[y][x]), (
                        gridStart[0] + x * tileSize,
                        gridStart[1] + y * tileSize))
        for y in range(gridHeight):
            for x in range(gridWidth):
                screen.blit('block', (
                    gridStart[0] + x * tileSize,
                    gridStart[1] + y * tileSize))
        for i in range(numberNextTiles):
            if i != tileSelected:
                screen.blit('root_'+str(nextTiles[i]), (
                    nextTilesStart[0],
                    nextTilesStart[1] + i * tileSize))
        for y in range(gridHeight):
            for x in range(gridWidth):
                if grid[y][x] != 0:
                    screen.blit('root_'+str(grid[y][x]), (
                        gridStart[0] + x * tileSize,
                        gridStart[1] + y * tileSize))
        if tileSelected != -1:
            if tileMouse != (-1, -1):
                if CheckFillableTile(tileMouse):
                    screen.blit('green_block', (
                        gridStart[0] + tileMouse[0] * tileSize,
                        gridStart[1] + tileMouse[1] * tileSize))
                else:
                    screen.blit('red_block', (
                        gridStart[0] + tileMouse[0] * tileSize,
                        gridStart[1] + tileMouse[1] * tileSize))
            screen.blit('root_'+str(nextTiles[tileSelected]), (
                mousePosition[0] - tileSize//2,
                mousePosition[1] - tileSize//2))
        if gameStatus == PLAYING:
            if overButton:
                screen.blit('button2', startButton)
            else:
                screen.blit('button', startButton)
        #if gameStatus == PLAYING or gameStatus == CHECKING:
        numLeaves = int(totalTime / levelMaxTime * maxLeaves)
        for i in range(numLeaves):
            screen.blit('leaf', (
                posLeaves[0] + i * distLeaves,
                posLeaves[1]))
        screen.blit('leaf', (
            posLeaves[0] + numLeaves * distLeaves,
            -posLeaves[1] + 2 * (totalTime - numLeaves * levelMaxTime / maxLeaves) / levelMaxTime * maxLeaves * posLeaves[1]))
        if numLeaves >= maxLeaves:
            gameStatus = GAME_OVER_TIME
        if gameStatus == CHECKING:
            screen.blit('levelcomplete', (88,256))
        if gameStatus == GAME_OVER_TIME or gameStatus == GAME_OVER_LOOP or gameStatus == GAME_OVER_NOWATER or gameStatus == GAME_OVER_OPEN:
            if gameStatus == GAME_OVER_TIME:
                screen.blit('gameover_time', (0,0))
            elif gameStatus == GAME_OVER_LOOP:
                screen.blit('gameover_loop', (0,0))
            elif gameStatus == GAME_OVER_NOWATER:
                screen.blit('gameover_nowater', (0,0))
            else:
                screen.blit('gameover_open', (0,0))
        screen.draw.text("Points: "+str(points), center=(800//2, 60), fontsize=45)
        

def update(dt):
    global totalTime, gameStatus, level, timeChecking
    if gameStatus == PLAYING:
        totalTime += dt
    elif gameStatus == CHECKING:
        timeChecking += dt
        if timeChecking > timeToCheck:
            timeChecking = 0
            if not FindLoops():
                if IsEmpty():
                    level += 1
                    SetLevel()
                    gameStatus = PLAYING
                else:
                    gameStatus = GAME_OVER_LOOP

def on_mouse_down(pos):
    global mousePosition, tileSelected
    tileSelected = -1
    if gameStatus == PLAYING:
        if pos[0] > nextTilesStart[0] and pos[1] > nextTilesStart[1]:
            if pos[0] < nextTilesStart[0] + tileSize and pos[1] < nextTilesStart[1] + numberNextTiles * tileSize:
                tileSelected = (pos[1] - nextTilesStart[1]) // tileSize
                mousePosition = pos        

def on_mouse_up(pos):
    global tileSelected, nextTiles, gameStatus, level, timeChecking
    if gameStatus == INTRO or gameStatus == GAME_OVER_TIME or gameStatus == GAME_OVER_LOOP or gameStatus == GAME_OVER_NOWATER or gameStatus == GAME_OVER_OPEN:
        gameStatus = PLAYING
        level = 1
        SetLevel()
        points = 0
        tileSelected = -1
    elif gameStatus == PLAYING:
        if tileSelected == -1:
            if overButton:
                nextTiles = [randint(1, 15) for y in range(numberNextTiles)]
        elif tileMouse != (-1, -1):
            if CheckFillableTile(tileMouse):
                grid[tileMouse[1]][tileMouse[0]] = nextTiles[tileSelected]
                nextTiles[tileSelected] = randint(1, 15)
                if ClosedRoot():
                    if not WaterReached():
                        gameStatus = GAME_OVER_NOWATER
                    else:
                        gameStatus = CHECKING
                        timeChecking = 0
                elif IsOpenBlocked():
                    gameStatus = GAME_OVER_OPEN
        tileSelected = -1

def on_mouse_move(pos):
    global mousePosition, tileMouse, overButton
    mousePosition = pos
    tileMouse = (-1, -1)
    if tileSelected != -1:
        if pos[0] > gridStart[0] and pos[1] > gridStart[1]:
            if pos[0] < gridStart[0] + gridWidth * tileSize and pos[1] < gridStart[1] + gridHeight * tileSize:
                tileMouse = ((pos[0] - gridStart[0]) // tileSize, (pos[1] - gridStart[1]) // tileSize)
    else:
        if pos[0] > startButton[0] and pos[1] > startButton[1] and pos[0] < endButton[0] and pos[1] < endButton[1]:
            overButton = True
        else:
            overButton = False

def CheckFillableTile(tileMouse):
    if grid[firstPosition[1]][firstPosition[0]] == 0 and tileMouse == firstPosition:
        if nextTiles[tileSelected] & 8:
            return True
        else:
            return False
    if grid[tileMouse[1]][tileMouse[0]] != 0:
        return False
    if tileMouse[0] == 0 and nextTiles[tileSelected] & 4:
        return False
    if tileMouse[0] == gridWidth - 1 and nextTiles[tileSelected] & 1:
        return False
    if tileMouse[1] == 0 and nextTiles[tileSelected] & 8:
        return False
    if tileMouse[1] == gridHeight - 1 and nextTiles[tileSelected] & 2:
        return False
    if tileMouse[0] > 0:
        if nextTiles[tileSelected] & 4 and grid[tileMouse[1]][tileMouse[0] - 1] & 1:
            return True
    if tileMouse[0] < gridWidth - 1:
        if nextTiles[tileSelected] & 1 and grid[tileMouse[1]][tileMouse[0] + 1] & 4:
            return True
    if tileMouse[1] > 0:
        if nextTiles[tileSelected] & 8 and grid[tileMouse[1] - 1][tileMouse[0]] & 2:
            return True
    if tileMouse[1] < gridHeight - 1:
        if nextTiles[tileSelected] & 2 and grid[tileMouse[1] + 1][tileMouse[0]] & 8:
            return True
    return False

def ClosedRoot():
    for y in range(gridHeight):
        for x in range(gridWidth + 1):
            leftConnect, rigthConnect = False, False
            if x > 0:
                leftConnect = grid[y][x - 1] & 1 != 0
            if x < gridWidth:
                rigthConnect = grid[y][x] & 4 != 0
            if (leftConnect and not rigthConnect) or (not leftConnect and rigthConnect):
                return False
    for x in range(gridWidth):
        for y in range(gridHeight + 1):
            topConnect, bottomConnect = False, False
            if y > 0:
                topConnect = grid[y - 1][x] & 2 != 0
            if y < gridHeight:
                bottomConnect = grid[y][x] & 8 != 0
            if (topConnect and not bottomConnect) or (not topConnect and bottomConnect):
                if (x,y) != firstPosition:
                    return False
    return True

def WaterReached():
    for y in range(gridHeight):
        for x in range(gridWidth):
            if grid[y][x] and waterGrid[y][x]:
                return True
    return False

def IsEmpty():
    for y in range(gridHeight):
        for x in range(gridWidth):
            if grid[y][x] != 0:
                if (x,y) != firstPosition:
                    return False
    return True

def FindLoops():
    global points
    for y in range(gridHeight):
        for x in range(gridWidth):
            if grid[y][x] == 1 or grid[y][x] == 2 or grid[y][x] == 4 or grid[y][x] == 8:
                if grid[y][x] == 1:
                    grid[y][x + 1] &= 11
                elif grid[y][x] == 2:
                    grid[y + 1][x] &= 7
                elif grid[y][x] == 4:
                    grid[y][x - 1] &= 14
                elif grid[y][x] == 8:
                    grid[y - 1][x] &= 13
                grid[y][x] = 0
                points += level
                return True
    return False

def IsOpenBlocked():
    for y in range(gridHeight):
        for x in range(gridWidth - 1):
            if grid[y][x] != 0 and grid[y][x + 1] != 0:
                leftConnect = grid[y][x] & 1 != 0
                rigthConnect = grid[y][x + 1] & 4 != 0
                if leftConnect != rigthConnect:
                    return True
    for x in range(gridWidth):
        for y in range(gridHeight - 1):
            if grid[y][x] != 0 and grid[y + 1][x] != 0:
                topConnect = grid[y][x] & 2 != 0
                bottomConnect = grid[y + 1][x] & 8 != 0
                if topConnect != bottomConnect:
                    return True
    return False
    

pgzrun.go() 
