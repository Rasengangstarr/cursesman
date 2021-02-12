import random
import curses
from curses import wrapper
import datetime
import time
from cursesman.entities import *

#how many characters to use to represent one 'block' in game
fidelity = 4

def roll_powerup(x, y):
    rnd = random.random()
    if rnd < 0.93:
        return None
    elif rnd < 0.95:
        return Powerup('powerup_bombs', x, y)
    elif rnd < 0.97:
        return Powerup('powerup_flames', x, y)
    elif rnd < 0.985:
        return Powerup('powerup_speed', x, y)
    elif rnd < 0.99:
        return Powerup('powerup_bombpass', x, y)
    elif rnd < 0.995:
        return Powerup('powerup_wallpass', x, y)
    elif rnd < 1:
        return Powerup('powerup_flamepass', x, y)

def add_static_walls(w,h):
    walls = []
    #borders
    walls.append(StaticWall(w*4, h*4))
    for x in range (0,w):
        walls.append(StaticWall(x*4,0))
        walls.append(StaticWall(x*4,h*4))
    for x in range (0,h):
        walls.append(StaticWall(0,x*4))
        walls.append(StaticWall(w*4,x*4))
    #checkerboard
    for x in range (1,w-1):
        for y in range (1,h-1):
            if x*4%8 == 0 and y*4%8 == 0:
                walls.append(StaticWall(x*4, y*4))
    return walls

def add_destructible_walls(w, h):
    walls = []
    doorplaced = False
    #make a quater of the room destructable
    for _ in range(round((w*h)/4)):
        x = random.randint(2, w-1)
        y = random.randint(2, h-1)
        if x % 2 == 0 and y % 2 == 0:
            continue
        else:
            #drop a door behind the first wall you draw. Powerups could be placed similarly.
            if not doorplaced:
                walls.append(Door(x*fidelity, y*fidelity))
                doorplaced = True
            else:
                powerup = roll_powerup(x*fidelity, y*fidelity)
                if powerup is not None:
                    walls.append(powerup)
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

def is_adjacent(a, b, dist=2):
    return abs(a.x/fidelity - b.x/fidelity) + abs(a.y/fidelity - b.y/fidelity) < dist

def is_inside(a,b):
    return a.x == b.x and a.y == b.y

def init_room(player, width, height, enemies):
    player.x = 4
    player.y = 4
    return add_destructible_walls(width, height) + add_static_walls(width, height) + [player] + enemies

def render_stats(player, stdscr, time_remaining):
    stdscr.addstr(1, 5, f'TIME {int(time_remaining)}')
    stdscr.addstr(1, 15, f'{int(player.score)}')
    stdscr.addstr(1, 25, f'LEFT {int(player.lives)}')

def render_game_over(stdscr):
    while True:
        stdscr.clear()
        stdscr.addstr(20, 20, f'GAME OVER')
        inp = stdscr.getch()
        if inp is not None:
            break
        stdscr.refresh()

def event_loop(stdscr):
    # Clear screen

    player = Player(4, 4, col=1)
    room = init_room(player, 8, 8, [Balloom(16,4)])
        
    lastDrawTime = time.time()
    room_time = 200
    room_start = time.time()
    game_over = False
    
    while not game_over:
        time_remaining = room_time - (time.time() - room_start)
        
        render_stats(player, stdscr, time_remaining)
        indestructableEntities = [e for e in room if not isinstance(e, Destructable)]
        unwalkableEntities = [e for e in room if isinstance(e, Unwalkable)]
        enemies = [e for e in room if isinstance(e, Enemy)]
        powerups = [e for e in room if isinstance(e, Powerup)]
        nbombs = len([e for e in room if isinstance(e, Bomb)])
        
        #deal with bombs
        explodedBombs = [b for b in room if type(b) == Bomb and b.exploded]
        explosions = []
        for b in explodedBombs:
            explosions += b.explosions
            b.explosions = []

        # deal with explosions
        for exp in [exp for exp in explosions]:
            # handle player
            if is_adjacent(exp, player, dist=1) and not player.flamepass:
                player.die()
                if player.lives < 0:
                    game_over=True
                    break
            # add scores
            player.score += sum(map(lambda x: x.score_value, filter(lambda x: (isinstance(x, Enemy) and is_adjacent(exp, x, dist=1)), room)))
            # remove destructable stuff
            room = [e for e in room if not (isinstance(e, Destructable) and is_adjacent(exp, e, dist=1))]

        for p in powerups:
            if is_inside(p, player):
                player.apply_powerup(p.name)
                player.score += p.score_value
                p.die()


        for ene in enemies:
            if is_adjacent(ene, player, dist=0.5):
                player.die()
                if player.lives < 0:
                    game_over=True
                    break

        
        # remove explosions that are clipping with indestructable entities
        explosions = [e for e in explosions if not any([is_adjacent(e, i, dist=0.75) for i in indestructableEntities])]
        
        room += explosions
        
        # deal with doors
        doors = [d for d in room if type(d) == Door]
        for d in doors:
            if is_inside(player, d):
                room_start = time.time()
                room = init_room(player, 20, 13, [Balloom(8,12)])

        currentTime = time.time()
        room = [e for e in room if e.alive]
        #do rendering
        if currentTime >= lastDrawTime + 0.01:
            #reset draw timer
            lastDrawTime = currentTime 
            #clean up any dead elements
            
            stdscr.erase() 

            for entity in room:
                entity.render(stdscr, player.x, player.y)
            for enemy in [e for e in room if isinstance(e, Enemy)]:
                enemy.act(room)
            stdscr.refresh()
        

        # input logic
        # TODO: move this to a proper handler class
        inp = stdscr.getch()

        if inp in [ord('w'), ord('k')]:
            player.move(0, -player.speed, room)
        elif inp in [ord('s'), ord('j')]:
            player.move(0, player.speed, room)
        elif inp in [ord('a'), ord('h')]:
            player.move(-player.speed, 0, room)
        elif inp in [ord('d'), ord('l')]:
            player.move(player.speed, 0, room)
        elif inp in [ord(' '), ord('e')]:
            if nbombs < player.max_bombs:
                room.append(Bomb(player.x, player.y, col=player.col, power=player.bomb_power))


        player.tick()
    render_game_over(stdscr)


def main():
    wrapper(init_curses)

if __name__ == '__main__':
    main()

