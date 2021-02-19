import sys
import logging
import random
import curses
from curses import wrapper
import datetime
import time
import copy
import pyfiglet
from entities import *
from rooms import rooms

logging.basicConfig(filename='main.log', filemode='w', format='%(name)s - %(message)s')
#how many characters to use to represent one 'block' in game
fidelity = 4

def start_screen(stdscr):
    h,w = stdscr.getmaxyx()
    
    states = ["S", "C", "E"]
    state = 0
    while True:
        stdscr.erase()
        
        stdscr.addstr(0,0,pyfiglet.figlet_format("  CURSESMAN", font = "rounded"))
        if state == 0:
            stdscr.addstr(10,0,pyfiglet.figlet_format("*     START" , font = "standard"))
        else:
            stdscr.addstr(10,0,pyfiglet.figlet_format("      START" , font = "standard"))
        if state == 1:
            stdscr.addstr(16,0,pyfiglet.figlet_format("*      CONTINUE", font="standard"))
        else:
            stdscr.addstr(16,0,pyfiglet.figlet_format("      CONTINUE", font="standard"))
        
        if state == 2:
            stdscr.addstr(22,0,pyfiglet.figlet_format("*     EXIT", font="standard")) 
        else:
            stdscr.addstr(22,0,pyfiglet.figlet_format("      EXIT", font="standard")) 
        
        stdscr.refresh()
        
        inp = stdscr.getch()
        if inp in [ord('w'), ord('k')] and state > 0:
            state -= 1
        elif inp in [ord('s'), ord('j')] and state < len(states) - 1:
            state += 1 
        elif inp == ord(' '):
            if state == 0:
                return
            elif state == 2:
                quit()
        continue

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

def init_room(player, room):
    player.x = 4
    player.y = 4

    return_room = add_destructible_walls(room[1], room[2]) + add_static_walls(room[1], room[2]) + [player]

    for e in room[3]:
        while True:
            f = copy.deepcopy(e)

            if len([en for en in return_room if en.x == f.x and en.y == f.y]) > 0:
                f.x = random.randint(0, room[1]) * 4
                f.y = random.randint(0, room[2]) * 4
                e = f
            else:
                return_room.append(f)
                break

    return return_room
        

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

def handle_exploded_bombs(room, player):
    unexploded = [b for b in room if isinstance(b, Explosive)and not b.exploded]
    explodedBombs = [b for b in room if type(b) == Bomb and b.exploded]
    indestructableEntities = [e for e in room if not isinstance(e, Destructable) and not e.flamepass]
    
    for b in explodedBombs:
        logging.warning("roo")
       
        #for each directional group of explosions
        for g in range(0, 4):
            #for each explosion in the group
            for ex in range(0,b.power):
                thisExplosion = g+ex*4
                if not any([is_adjacent(b.explosions[thisExplosion], entity, dist=0.75) for entity in indestructableEntities]):
                    #we must make a copy of the explosion at this point, since the bomb it belongs to will need to be destroyed.
                    logging.warning(str(g+ex*4) + " exploded")
                    explosionInWorld = copy.deepcopy(b.explosions[thisExplosion])
                    explosionInWorld.schedule_for_deletion(0.3)
                    room.append(explosionInWorld)
                    for bu in unexploded:
                        if is_adjacent(b.explosions[thisExplosion], bu, dist=0.75):
                            bu.explode()
                            handle_exploded_bombs(room, player)
                    
                    logging.warning("flamepass" + str(player.flamepass))
                    # handle player
                    if is_adjacent(b.explosions[thisExplosion], player, dist=1) and not player.flamepass:
                        player.die()
                        logging.warning("ded")
                        if player.lives < 0:
                            game_over=True
                            break
                    # add scores
                    player.score += sum(map(lambda x: x.score_value, filter(lambda x: (isinstance(x, Enemy) and is_adjacent(b.explosions[thisExplosion], x, dist=1)), room)))
                    # remove destructable stuff
                    [e.die() for e in room if (isinstance(e, Destructable) and is_adjacent(b.explosions[thisExplosion], e, dist=1))]
            

                else:
                    #stop processing this group
                    break
        #the bomb is spent, so get rid of it
        b.die()


def event_loop(stdscr):
    # Clear screen
    debug_mode = len(sys.argv) > 1 and sys.argv[1] == '--debug'
    currentRoom = 0
    player = Player(4, 4, col=1)
    room = init_room(player, rooms[currentRoom])
        
    lastDrawTime = time.time()
    room_time = 200
    room_start = time.time()
    game_over = False

    start_screen(stdscr)
    
    if debug_mode:
        player.max_bombs = 3
        player.bomb_power=5
        player.flamepass = True
        player.wallpass = True
    
    while not game_over:
        time_remaining = room_time - (time.time() - room_start)
        
        render_stats(player, stdscr, time_remaining)
        indestructableEntities = [e for e in room if not isinstance(e, Destructable)]
        unwalkableEntities = [e for e in room if isinstance(e, Unwalkable)]
        enemies = [e for e in room if isinstance(e, Enemy)]
        powerups = [e for e in room if isinstance(e, Powerup)]
        nbombs = len([e for e in room if isinstance(e, Bomb)])
        
        handle_exploded_bombs(room, player)

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

        # deal with doors
        doors = [d for d in room if type(d) == Door]
        for d in doors:
            if is_inside(player, d):
                room_start = time.time()
                currentRoom += 1
                room = init_room(player,rooms[currentRoom])   
        
        room = [e for e in room if e.alive]
        
        currentTime = time.time()
        #do rendering
        if currentTime >= lastDrawTime + 0.01:
            #reset draw timer
            lastDrawTime = currentTime 
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

