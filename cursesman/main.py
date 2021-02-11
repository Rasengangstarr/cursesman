import random
import curses
from curses import wrapper
import datetime
import time
from entities import *

#how many characters to use to represent one 'block' in game
fidelity = 4

def add_static_walls():
    walls = []
    #borders
    walls.append(StaticWall(12*4, 12*4))
    for x in range (0,12):
        walls.append(StaticWall(x*4,0))
        walls.append(StaticWall(x*4,12*4))
        walls.append(StaticWall(0,x*4))
        walls.append(StaticWall(12*4,x*4))
    #checkerboard
    for x in range (1,12):
        for y in range (1,12):
            if x*4%8 == 0 and y*4%8 == 0:
                walls.append(StaticWall(x*4, y*4))
    return walls

def add_destructible_walls():
    walls = []
    for _ in range(20):
        x = random.randint(1, 11)
        y = random.randint(1, 11)
        if x % 2 == 0 and y % 2 == 0:
            continue
        else:
            walls.append(DestructibleWall(x*fidelity, y*fidelity))
    return walls

def init_curses(stdscr):

    stdscr.nodelay(1)
    curses.curs_set(0)
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
    for wall in walls:
        if x > wall.x-4 and x < wall.x+4 and y > wall.y-4 and y < wall.y+4:
            return False
    return True

def is_adjacent(a, b, dist=2):
    return abs(a.x/4 - b.x/4) + abs(a.y/4 - b.y/4) < dist

def event_loop(stdscr):
    # Clear screen
    height, width = stdscr.getmaxyx()

    player = Player(4, 4)
    dwalls = add_destructible_walls()
    swalls = add_static_walls() 
    room = [player] + dwalls + swalls
        
    lastDrawTime = time.time()

    while 1:
        
        indestructableEntities = [e for e in room if not isinstance(e, Destructable)]
        #deal with bombs
        explodedBombs = [b for b in room if type(b) == Bomb and b.exploded]
        explosions = []
        for b in explodedBombs:
            explosions += b.explosions
            b.explosions = []
        # remove explosions that are clipping with indestructable entities
        explosions = [e for e in explosions if check_can_move(e.x, e.y, indestructableEntities)]
        room += explosions

        # deal with explosions
        for exp in [exp for exp in room if type(exp) == Explosion]:
            room = [e for e in room if not (isinstance(e, Destructable) and is_adjacent(exp, e, dist=1))]
       
        currentTime = time.time()
        #do rendering
        if currentTime >= lastDrawTime + 0.01:
            #reset draw timer
            lastDrawTime = currentTime 
            #clean up any dead elements
            room = [e for e in room if e.alive]
            
            stdscr.erase() 

            for entity in room:
                entity.render(stdscr)
            stdscr.refresh()
        
        unwalkableEntities = [e for e in room if isinstance(e, Unwalkable)]

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
            room.append(Bomb(player.x, player.y, col=player.col))


        player.tick()


def main():
    wrapper(init_curses)

if __name__ == '__main__':
    main()

