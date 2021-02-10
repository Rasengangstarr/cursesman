import random
import curses
from curses import wrapper
import datetime
import time
from entities import Player, DestructibleWall, Bomb

#init curses
#curses.noecho()
#stdscr.nodelay(1)

#how many characters to use to represent one 'block' in game
fidelity = 4

def drawmap(stdscr):
    for x in range (0,16):
        for y in range (0,13):
            #draw a gapped checkerboard like in screenshot
            if x % 2 == 0 and y % 2 == 0:
                #draw in blocks of 'fidelity', such that we can scale it up or down
                for bx in range(0,fidelity):
                    for by in range(0,fidelity):
                        stdscr.addch(y*fidelity+by, x*fidelity+bx, 'X')

def add_destructible_walls():
    walls = []
    for _ in range(20):
        x = random.randint(0, 13)
        y = random.randint(0, 13)
        if x % 2 == 0 and y % 2 == 0:
            continue
        else:
            walls.append(DestructibleWall(x*fidelity, y*fidelity))
    return walls

def init_curses(stdscr):

    # TODO: replace with proper resfresh code
    #curses.halfdelay(3) # 10/10 = 1[s] inteval
    #curses.curs_set(0)
    stdscr.nodelay(1)
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    event_loop(stdscr)

def check_can_move(x, y, walls):
    # first check permanent walls
    # TODO: dave 
    # now check dwalls
    for wall in walls:
        if x > wall.x-4 and x < wall.x+4 and y > wall.y-4 and y < wall.y+4:
            return False
    return True

def is_adjacent(a, b):
    return abs(a.x/4 - b.x/4) + abs(a.y/4 - b.y/4) < 2

def event_loop(stdscr):
    # Clear screen
    height, width = stdscr.getmaxyx()

    player = Player(4, 4)
    dwalls = add_destructible_walls()
    
    room = [player] + dwalls 

    lastDrawTime = time.time()

    while 1:
        currentTime = time.time()
        
        explodedBombs = [b for b in room if type(b) == Bomb and b.exploded]
        for b in explodedBombs:
            room = [e for e in room if not (type(e) == DestructibleWall and is_adjacent(b,e))]


        if currentTime >= lastDrawTime + 0.01:
            #clean up any dead elements
            room = [e for e in room if e.alive == True]
            stdscr.erase() 
            lastDrawTime = currentTime
            drawmap(stdscr)
            for entity in room:
                entity.render(stdscr)
            stdscr.refresh()
        
        unwalkableEntities = [e for e in room if type(e) == DestructibleWall]

        # input logic
        # TODO: move this to a proper handler class
        inp = stdscr.getch()

        if inp in [ord('w'), ord('k')]:
            if check_can_move(player.x, player.y-1, unwalkableEntities):
                player.move(0, -1)
        elif inp in [ord('s'), ord('j')]:
            if check_can_move(player.x, player.y+1, unwalkableEntities):
                player.move(0, 1)
        elif inp in [ord('a'), ord('h')]:
            if check_can_move(player.x-1, player.y, unwalkableEntities):
                player.move(-1, 0)
        elif inp in [ord('d'), ord('l')]:
            if check_can_move(player.x+1, player.y, unwalkableEntities):
                player.move(1, 0)
        elif inp in [ord(' '), ord('e')]:
            room.append(Bomb(player.x, player.y))
        else:
            # it would be nice to automatically update all non movign entities as idle
            player.update_state('idle')



def main():
    wrapper(init_curses)

if __name__ == '__main__':
    main()

