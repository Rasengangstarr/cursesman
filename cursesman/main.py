import sys
import logging
import pickle
import socketio
import random
import curses
from curses import wrapper
import datetime
import time
import copy
import threading
import pyfiglet
from cursesman.entities import *
from cursesman.settings import *
from cursesman.rooms import rooms
from cursesman.utils import loop_sound

logging.basicConfig(filename='main.log', filemode='w', format='%(name)s - %(message)s')
#how many characters to use to represent one 'block' in game

def start_screen(stdscr):
    h,w = stdscr.getmaxyx()
    
    states = ["S", "C", "M", "E"]
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
            stdscr.addstr(22,0,pyfiglet.figlet_format("*     MULTIPLAYER", font="standard")) 
        else:
            stdscr.addstr(22,0,pyfiglet.figlet_format("      MULTIPLAYER", font="standard")) 

        if state == 3:
            stdscr.addstr(28,0,pyfiglet.figlet_format("*     EXIT", font="standard")) 
        else:
            stdscr.addstr(28,0,pyfiglet.figlet_format("      EXIT", font="standard")) 
        
        stdscr.refresh()
        
        inp = stdscr.getch()
        if inp in [ord('w'), ord('k')] and state > 0:
            state -= 1
        elif inp in [ord('s'), ord('j')] and state < len(states) - 1:
            state += 1 
        elif inp == ord(' '):
            if state in [0, 2]:
                return states[state]
            elif state == 3:
                quit()
        continue

def generic_screen(stdscr, text, t=2):
    h,w = stdscr.getmaxyx()
    start = time.time()
    
    while True:
        stdscr.erase()
        stdscr.addstr(h//2,0,pyfiglet.figlet_format(text.upper() , font = "standard"))
        stdscr.refresh()
        if time.time() - start > t:
            return

#obselete
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
    walls.append(StaticWall(w*FIDELITY, h*FIDELITY))
    for x in range (0,w):
        walls.append(StaticWall(x*FIDELITY,0))
        walls.append(StaticWall(x*FIDELITY,h*FIDELITY))
    for x in range (0,h):
        walls.append(StaticWall(0,x*FIDELITY))
        walls.append(StaticWall(w*FIDELITY,x*FIDELITY))
    #checkerboard
    for x in range (1,w-1):
        for y in range (1,h-1):
            if x*FIDELITY%(FIDELITY*2) == 0 and y*FIDELITY%(FIDELITY*2) == 0:
                walls.append(StaticWall(x*FIDELITY, y*FIDELITY))
    return walls

def place_room_entities(w, h, p):
    walls = []
    doorplaced = False
    #make a quater of the room destructable
    for _ in range(round((w*h)/FIDELITY)):
        x = random.randint(2, w-1)
        y = random.randint(2, h-1)
        if x % 2 == 0 and y % 2 == 0:
            continue
        else:
            #drop a door behind the first wall you draw. Powerups could be placed similarly.
            if not doorplaced:
                walls.append(Door(x*FIDELITY, y*FIDELITY))
                doorplaced = True
            else:
                p.x = x*FIDELITY
                p.y = y*FIDELITY
                walls.append(p)
            walls.append(DestructibleWall(x*FIDELITY, y*FIDELITY))

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
    curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    
    event_loop(stdscr)

def is_adjacent(a, b, dist=2):
    return abs(a.x/FIDELITY - b.x/FIDELITY) + abs(a.y/FIDELITY - b.y/FIDELITY) < dist

def is_inside(a,b):
    return a.x == b.x and a.y == b.y

def init_room(player, room):
    player.x = FIDELITY
    player.y = FIDELITY

    return_room = place_room_entities(room[1], room[2], room[4]) + add_static_walls(room[1], room[2]) + [player]

    #enemies
    for e in room[3]:
        while True:
            f = copy.deepcopy(e)

            if len([en for en in return_room if en.x == f.x and en.y == f.y]) > 0:
                f.x = random.randint(6, room[1]) * FIDELITY
                f.y = random.randint(6, room[2]) * FIDELITY
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
    generic_screen(stdscr, 'GAME OVER')

def handle_exploded_bombs(room, players):
    unexploded = [b for b in room if isinstance(b, Explosive)and not b.exploded]
    explodedBombs = [b for b in room if type(b) == Bomb and b.exploded]
    indestructableEntities = [e for e in room if not isinstance(e, Destructable) and not e.flamepass]
    
    for b in explodedBombs:
        logging.warning("roo")
       
        #for each directional group of explosions
        for g in range(0, 4):
            #for each explosion in the group
            for ex in range(0,b.power):
                thisExplosion = g+ex*FIDELITY
                if not any([is_adjacent(b.explosions[thisExplosion], entity, dist=0.75) for entity in indestructableEntities]):
                    #we must make a copy of the explosion at this point, since the bomb it belongs to will need to be destroyed.
                    logging.warning(str(g+ex*FIDELITY) + " exploded")
                    explosionInWorld = copy.deepcopy(b.explosions[thisExplosion])
                    explosionInWorld.schedule_for_deletion(0.3)
                    room.append(explosionInWorld)
                    for bu in unexploded:
                        if is_adjacent(b.explosions[thisExplosion], bu, dist=0.75):
                            bu.explode()
                            handle_exploded_bombs(room, players)
                    
                    # handle players
                    for p in players:
                        logging.warning("flamepass" + str(p.flamepass))
                        if is_adjacent(b.explosions[thisExplosion], p, dist=1) and not p.flamepass:
                            p.die()
                        # add scores
                        p.score += sum(map(lambda x: x.score_value, filter(lambda x: (isinstance(x, Enemy) and is_adjacent(b.explosions[thisExplosion], x, dist=1)), room)))
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
    currentRoom = 1
    display_room = True
    master = False
    player = Player(FIDELITY, FIDELITY, col=1)
    local_player_id = player.uuid
    room = init_room(player, rooms[currentRoom])
        
    lastDrawTime = time.time()
    room_time = 200
    room_start = time.time()
    game_over = False

    state = start_screen(stdscr)
    multiplayer = state == 'M'
    # init socket io client if multiplayer
    if multiplayer:
        sio = socketio.Client()
        sio.connect(f'http://{SERVER_ADDRESS}:{SERVER_PORT}')
        # setup event handlers

        @sio.event
        def room_server_refresh(data):
            nonlocal room # ew ew ew lets make it a class?
            updated_room = pickle.loads(data)
            if master:
                # only load other player
                cond = lambda x: x.owner is not None and x.owner != local_player_id
            else:
                # also load other deets
                cond = lambda x: x.owner != local_player_id
            local = [e for e in room if not cond(e)]
            updated_room = [e for e in updated_room if cond(e)]
            updated_room += local
            room = updated_room

        @sio.event
        def set_master(data):
            nonlocal master
            master = True

    music_thread = loop_sound('chipchoon1.mp3', 35)

    if debug_mode:
        player.max_bombs = 3
        player.bomb_power=5
        player.flamepass = True
        player.wallpass = True

    render_iter = 0 
    while not game_over:
        if debug_mode:
            stdscr.addstr(2, 5, str(player.x))
            stdscr.addstr(2, 10, str(player.y))
        time_remaining = room_time - (time.time() - room_start)
        if display_room:
            generic_screen(stdscr, f'     ROOM      {currentRoom}')
            display_room = False
        
        render_stats(player, stdscr, time_remaining)
        indestructableEntities = [e for e in room if not isinstance(e, Destructable)]
        unwalkableEntities = [e for e in room if isinstance(e, Unwalkable)]
        enemies = [e for e in room if isinstance(e, Enemy)]
        powerups = [e for e in room if isinstance(e, Powerup)]
        nbombs = len([e for e in room if isinstance(e, Bomb)])
        nplayerbombs = len([e for e in room if isinstance(e, Bomb) and e.owner == local_player_id])
        players = [e for e in room if isinstance(e, Player)]
        player_uuids = {p.uuid for p in players}
        
        handle_exploded_bombs(room, players)

        for p in powerups:
            for pl in players:
                if is_inside(p, pl):
                    pl.apply_powerup(p.name)
                    pl.score += p.score_value
                    p.die()

        for ene in enemies:
            for pl in players:
                if is_adjacent(ene, pl, dist=0.5):
                    pl.die()

        # deal with doors
        doors = [d for d in room if type(d) == Door]
        for d in doors:
            if is_inside(player, d):
                room_start = time.time()
                currentRoom += 1
                room = init_room(player,rooms[currentRoom])   
                display_room = True
        
        room = [e for e in room if e.alive]

        if player.lives < 0:
            #music_thread.kill() 
            music_thread.join()
            game_over=True
            render_game_over(stdscr)
            break
        
        currentTime = time.time()
        #do rendering
        if currentTime >= lastDrawTime + 0.01:
            #reset draw timer
            lastDrawTime = currentTime 
            render_iter += 1
            stdscr.erase() 

            for entity in room:
                if entity.uuid == local_player_id:
                    entity.central_render(stdscr, player.x, player.y)
                else:
                    col_override = 2 if entity.owner is not None and entity.owner != local_player_id else None
                    entity.render(stdscr, player.x, player.y, col_override=col_override)
            for enemy in [e for e in room if isinstance(e, Enemy)]:
                enemy.act(room)
            stdscr.refresh()
            
            if multiplayer and render_iter % 10 == 0:
                if master:
                    cond = lambda x: x.owner is None or x.owner == local_player_id
                else:
                    cond = lambda x: x.owner == local_player_id
                dumps = pickle.dumps([e for e in room if cond(e)])
                sio.emit('room_event', dumps)

        

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
            if nplayerbombs < player.max_bombs:
                room.append(Bomb(player.x, player.y, col=player.col, power=player.bomb_power, owner=local_player_id))


        player.tick()


def main():
    wrapper(init_curses)

if __name__ == '__main__':
    main()

