from cursesman.sprite_loader import Sprite
from cursesman.utils import play_sound
from cursesman.settings import FIDELITY

from functools import reduce
from playsound import playsound
import threading
import time
import random
import logging
import wave
import math
import uuid
import numpy as np
import pyastar

playerXDraw = 8*FIDELITY
playerYDraw = 6*FIDELITY

logging.basicConfig(filename='entities.log', filemode='w', format='%(name)s - %(message)s')
class State():
    def __init__(self, name, valididty):
        self.start = time.time()
        self.name = name
        self.valididty = valididty
    
    def check_validity(self):
        now = time.time()
        return self.start + self.valididty > now

# interfaces
class Unwalkable(): pass

class Destructable(): pass

class Explosive():
    def explode(self):
        # explode must be implemented
        pass

# entities
class Entity():
    def __init__(self, name, x, y, col=0):
        self.uuid = uuid.uuid4()
        self.name = name
        self.states = []
        self.x = x
        self.y = y
        self.col = col
        self.sprite = Sprite(self.name, self.get_state())
        self.alive = True
        self.flamepass = False
        self.owner = None

    def get_state(self):
        # idle if only idle - else latest state that isnt idle
        if len(self.states) == 0:
            return 'idle'
        else:
            return self.states[-1].name
        
    def die(self):
        self.alive = False

    #render relative to the player by default
    def render(self, stdscr, px, py, col_override=None):
        h,w = stdscr.getmaxyx()

        drawX = self.x+playerXDraw-px
        drawY = self.y+playerYDraw-py

        if drawX < w-FIDELITY and drawY < h-FIDELITY and drawX > 0 and drawY > 2: # dont overwrite stats
            #print (str(drawX))
            #print (str(drawY))
            col = self.col if col_override is None else col_override
            self.sprite.render(stdscr, drawX, drawY, col=col)

    def update_state(self, state, animation_time=0.3):
        old_state = self.get_state()
        self.states.append(State(state, animation_time))
        self.tick(old_state=old_state)

    def tick(self, old_state=None):
        # stale out anything we dont need
        if old_state is None:
            old_state = self.get_state()
        self.states = list(filter(lambda x: x.check_validity(), self.states))
        new_state = self.get_state()
        if old_state != new_state:
            self.sprite = Sprite(self.name, new_state)

class Door(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('door', x, y, col=col)
        self.flamepass = True

class StaticWall(Entity, Unwalkable):
    def __init__(self, x, y, col=0):
        super().__init__('static_wall', x, y, col=col)

class DestructibleWall(Entity, Unwalkable, Destructable):
    def __init__(self, x, y, col=0):
        super().__init__('destructible_wall', x, y, col=col)

class Character(Entity):
    def __init__(self, name, x, y, col=0):
        super().__init__(name, x, y, col=col)
        self.speed = 1
        # maybe not all characters will have the ability to drop bombs
        self.max_bombs = 1
        self.bomb_power = 1
        self.wallpass = False
        self.bombpass = False
        self.flamepass = False

    def changeDirectionAimlessly(self):
        threading.Timer(1.0, self.changeDirectionAimlessly).start()
        self.changeDirection()

    def changeDirection(self):
        self.direction = random.randint(0,4) 
    
    def check_can_move(self, x, y, walls):
        # apply powerups
        if self.wallpass:
            walls = [e for e in walls if not isinstance(e, DestructibleWall)]
        if self.bombpass:
            walls = [e for e in walls if not isinstance(e, Bomb)]

        for wall in walls:
            if math.floor(x) > wall.x-FIDELITY and math.floor(x) < wall.x+FIDELITY and math.floor(y) > wall.y-FIDELITY and math.floor(y) < wall.y+FIDELITY:
            #if already inside the wall
                if math.floor(self.x) > wall.x-FIDELITY and math.floor(self.x) < wall.x+FIDELITY and math.floor(self.y) > wall.y-FIDELITY and math.floor(self.y) < wall.y+FIDELITY: 
                    continue
                else:
                    return False
        return True

    def move(self, dx, dy, room):
        walls = [e for e in room if isinstance(e, Unwalkable)]
        if not self.check_can_move(self.x+dx, self.y+dy, walls):
            return # do nothing
        if dy < 0:
            self.update_state('move_up')
        elif dy > 0:
            self.update_state('move_down')
        elif dx > 0:
            self.update_state('move_right')
        elif dx < 0:
            self.update_state('move_left')
        self.x += dx
        self.y += dy
    
    #during pathfinding, ignore collisions to deal with any rounding errors if the enemies
    #movement speed doesn't go into 1 a whole number of times
    def move_regardless(self,dx,dy,room):
        if dy < 0:
            self.update_state('move_up')
        elif dy > 0:
            self.update_state('move_down')
        elif dx > 0:
            self.update_state('move_right')
        elif dx < 0:
            self.update_state('move_left')
        self.x += dx
        self.y += dy
        

    def apply_powerup(self, powerup_name):
        powerup_field, powerup_func = {
            'powerup_bombs': ('max_bombs', lambda x: x + 1),
            'powerup_flames': ('bomb_power', lambda x: x + 1),
            'powerup_speed': ('speed', lambda x: x + 0), # need to implement this properly
            'powerup_wallpass': ('wallpass', lambda x: True),
            'powerup_bombpass': ('bombpass', lambda x: True),
            'powerup_flamepass': ('flamepass', lambda x: True),
        }.get(powerup_name)

        setattr(self, powerup_field, powerup_func(getattr(self, powerup_field)))
        
    def get_path_to_target(self, target, room):
        world = np.ones((21, 15))
        for e in [r for r in room if isinstance(r,Entity) and isinstance(r,Unwalkable)]:
            world[int(e.x/FIDELITY),int(e.y/FIDELITY)] = 1000
        world = world.astype(np.float32) 
        path = pyastar.astar_path(world, (int(self.x/FIDELITY), int(self.y/FIDELITY)), (round(target.x/FIDELITY), round(target.y/FIDELITY)), allow_diagonal=False)
        
        return path

class Enemy(Character, Destructable):
    def __init__(self, name, x, y, col=0):
        super().__init__(name, x, y, col=col)
        self.score_value = 100
        self.direction = 1
        self.target_x = -1
        self.target_y = -1
        self.view_radius = 0

    def act_dumb(self,room) :
        original_xy = (self.x, self.y)
        if self.direction == 0:
            self.move(-self.speed, 0, room)
        if self.direction == 1:
                self.move(self.speed, 0, room)
        if self.direction == 2:
            self.move(0, -self.speed, room)
        if self.direction == 3:
            self.move(0, self.speed, room)
        if original_xy == (self.x, self.y):
            self.changeDirection()
        
    def act_smart(self,room):
        players = [e for e in room if type(e) == Player]
        player_to_home = None
        homing_player = False
        self.x = round(self.x, 3)
        self.y = round(self.y, 3)
        for p in players:
            if (((p.x-self.x)**2+(p.y-self.y)**2) ** 0.5) <= self.view_radius:
                homing_player = True
                player_to_home = p
        if homing_player == False:
            original_xy = (self.x, self.y)
            if self.direction == 0:
                self.move(self.speed, 0, room)
            if self.direction == 1:
                    self.move(self.speed, 0, room)
            if self.direction == 2:
                self.move(0, -self.speed, room)
            if self.direction == 3:
                self.move(0, self.speed, room)
            if original_xy == (self.x, self.y):
                self.changeDirection()
        elif self.target_x == -1 and self.target_y == -1:
            new_target = self.get_path_to_target(player_to_home, room)[1]
            self.target_x = new_target[0]*FIDELITY
            self.target_y = new_target[1]*FIDELITY
        else:
            if self.x < self.target_x:
                self.move_regardless(self.speed, 0, room)
            elif self.x > self.target_x:
                self.move_regardless(-self.speed, 0, room)
            elif self.y < self.target_y:
                self.move_regardless(0, self.speed, room)
            elif self.y > self.target_y:
                self.move_regardless(0, -self.speed, room)
            else:
                self.target_x = -1
                self.target_y = -1

    def act(self,room): pass

class Balloom(Enemy):
    def __init__(self, x, y, col=2):
        super().__init__('balloom', x, y, col=col)
        self.speed = 0.05
        self.changeDirectionAimlessly()
        self.view_radius = 0;
    def act(self, room):
        self.act_dumb(room)

class Oneil(Enemy):
    def __init__(self, x, y, col=1):
        super().__init__('oneil', x, y, col=col)
        self.view_radius = 20
        self.speed = 0.1
        self.changeDirectionAimlessly()

    def act(self, room):
        self.act_smart(room)

class Doll(Enemy):
    def __init__(self, x, y, col=4):
        super().__init__('doll', x, y, col=col)
        self.speed = 0.1
        self.view_radius = 0
        self.changeDirectionAimlessly()

    def act(self, room):
        self.act_dumb(room)

class Ovapi(Enemy):
    def __init__(self, x, y, col=1):
        super().__init__('ovapi', x, y, col=col)
        self.speed = 0.05
        self.view_radius = 20
        self.changeDirectionAimlessly()

    def act(self, room):
        self.act_smart(room)

class Pass(Enemy):
    def __init__(self, x, y, col=1):
        super().__init__('pass', x, y, col=col)
        self.speed = 0.15
        self.view_radius = 40 
        self.changeDirectionAimlessly()

    def act(self, room):
        self.act_smart(room)


class Player(Character, Destructable):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)
        self.lives = 3
        self.score = 0
        self.owner = self.uuid

    def central_render(self, stdscr, px, py):
        #always draw the player at the same location
        self.sprite.render(stdscr, playerXDraw, playerYDraw, col=self.col)

    def die(self):
        self.lives -= 1
        if self.lives >= 0:
            self.x = FIDELITY
            self.y = FIDELITY
            self.update_state('revive', animation_time=1)
        else:
            # game over
            pass

class Bomb(Entity, Unwalkable, Explosive, Destructable): # Unwalkable
    def __init__(self, x, y, col=0, power=1, owner=None):
        super().__init__('bomb', x, y, col=col)
        self.fuse = 3
        self.power = power
        self.exploded = False
        self.burnFuse()
        self.explosions = []
        self.owner = owner

    def burnFuse(self):
        if self.fuse > 0:
            self.fuse -= 1
            threading.Timer(1.0, self.burnFuse).start()
        else:
            self.explode()

    def explode(self):
        #this way the list is ordered in directional groups, from the inside out.
        logging.warning("power = " + str(self.power))
        explosions = []#[Explosion(self.x, self.y, col=self.col)]
        
        #left explosions
        for p in range (1, self.power+1):
            explosions.append(Explosion(self.x-FIDELITY*p, self.y, col=self.col, owner=self.owner))
            explosions.append(Explosion(self.x+FIDELITY*p, self.y, col=self.col, owner=self.owner))
            explosions.append(Explosion(self.x, self.y-FIDELITY*p, col=self.col, owner=self.owner))
            explosions.append(Explosion(self.x, self.y+FIDELITY*p, col=self.col, owner=self.owner))
        explosions.append(Explosion(self.x, self.y, col=self.col))

        self.explosions = explosions
        play_sound("explosion.wav")
        logging.warning(self.explosions)
        self.exploded = True 
        
class Explosion(Entity):
    def __init__(self, x, y, col=0, owner=None):
        super().__init__('explosion', x, y, col=col)
        self.owner = owner

    def schedule_for_deletion(self, timer):
        threading.Timer(timer, self.die).start()

class Powerup(Entity):
    def __init__(self, name, x, y, col=0):
        super().__init__(name, x, y, col=col)
        self.flamepass = True
        self.score_value = 1000


