from cursesman.sprite_loader import Sprite
from cursesman.utils import play_sound

from functools import reduce
from playsound import playsound
import threading
import time
import random
import logging
import wave
import math

playerXDraw = 8*4
playerYDraw = 6*4

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
        self.name = name
        self.states = []
        self.x = x
        self.y = y
        self.col = col
        self.sprite = Sprite(self.name, self.get_state())
        self.alive = True
        self.flamepass = False
    def get_state(self):
        # idle if only idle - else latest state that isnt idle
        if len(self.states) == 0:
            return 'idle'
        else:
            return self.states[-1].name
        
    def die(self):
        self.alive = False

    #render relative to the player by default
    def render(self, stdscr, px, py):
        h,w = stdscr.getmaxyx()

        drawX = self.x+playerXDraw-px
        drawY = self.y+playerYDraw-py

        if drawX < w-4 and drawY < h-4 and drawX > 0 and drawY > 2: # dont overwrite stats
            #print (str(drawX))
            #print (str(drawY))
            self.sprite.render(stdscr, drawX, drawY, col=self.col)

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

    def check_can_move(self, x, y, walls):
        # apply powerups
        if self.wallpass:
            walls = [e for e in walls if not isinstance(e, DestructibleWall)]
        if self.bombpass:
            walls = [e for e in walls if not isinstance(e, Bomb)]

        for wall in walls:
            if math.floor(x) > wall.x-4 and math.floor(x) < wall.x+4 and math.floor(y) > wall.y-4 and math.floor(y) < wall.y+4:
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

class Enemy(Character, Destructable):
    def __init__(self, name, x, y, col=0):
        super().__init__(name, x, y, col=col)
        self.score_value = 100

    def act(self,room): pass

#The Balloom seems to float around randomly
class Balloom(Enemy):
    def __init__(self, x, y, col=2):
        super().__init__('balloom', x, y, col=col)
        self.speed = 0.05
        #TODD this should be whatever python calls an enum
        self.direction = 1
        self.changeDirectionAimlessly()

    def changeDirectionAimlessly(self):
        threading.Timer(1.0, self.changeDirectionAimlessly).start()
        self.changeDirection()

    def changeDirection(self):
        self.direction = random.randint(0,4) 

    def act(self, room):
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

#The Balloom seems to float around randomly
class Oneil(Enemy):
    def __init__(self, x, y, col=1):
        super().__init__('oneil', x, y, col=col)
        self.speed = 0.1
        #TODD this should be whatever python calls an enum
        self.direction = 1
        self.changeDirectionAimlessly()

    def changeDirectionAimlessly(self):
        threading.Timer(1.0, self.changeDirectionAimlessly).start()
        self.changeDirection()

    def changeDirection(self):
        self.direction = random.randint(0,4) 

    def act(self, room):
        players = [e for e in room if type(e) == Player]
        player_to_home = None
        homing_player = False
        for p in players:
            if (((p.x-self.x)**2+(p.y-self.y)**2) ** 0.5) <= 24:
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
        else:
            if math.floor(self.x) < player_to_home.x :
                self.move(self.speed, 0, room)
                logging.warning("TRYING TO MOVE RIGHT" + " " + str(player_to_home.x) + " " + str(math.floor(self.x)))
            if math.floor(self.x) > player_to_home.x :
                logging.warning("TRYING TO MOVE LEFT")
                self.move(-self.speed, 0, room)
            if math.floor(self.y) < player_to_home.y :
                logging.warning("TRYING TO MOVE DOWN")
                self.move(0, self.speed, room)
            if math.floor(self.y) > player_to_home.y :
                logging.warning("TRYING TO MOVE UP")
                self.move(0, -self.speed, room)


class Player(Character, Destructable):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)
        self.lives = 3
        self.score = 0

    def render(self, stdscr, px, py):
        #always draw the player at the same location
        self.sprite.render(stdscr, playerXDraw, playerYDraw, col=self.col)

    def die(self):
        self.lives -= 1
        if self.lives >= 0:
            self.x = 4
            self.y = 4
            self.update_state('revive', animation_time=1)
        else:
            # game over
            pass

class Bomb(Entity, Explosive, Destructable): # Unwalkable
    def __init__(self, x, y, col=0, power=1):
        super().__init__('bomb', x, y, col=col)
        self.fuse = 3
        self.power = power
        self.exploded = False
        self.burnFuse()
        self.explosions = []

    def burnFuse(self):
        if self.fuse > 0:
            self.fuse -= 1
            threading.Timer(1.0, self.burnFuse).start()
        else:
            self.explode()

    def explode(self):
        #this way the list is ordered in directional groups, from the inside out.
        logging.warning("power = " + str(self.power))
        explosions = []
        
        #left explosions
        for p in range (1, self.power+1):
            explosions.append(Explosion(self.x-4*p, self.y, col=self.col))
            explosions.append(Explosion(self.x+4*p, self.y, col=self.col))
            explosions.append(Explosion(self.x, self.y-4*p, col=self.col))
            explosions.append(Explosion(self.x, self.y+4*p, col=self.col))
        explosions.append(Explosion(self.x, self.y, col=self.col))

        self.explosions = explosions
        play_sound("explosion.wav")
        logging.warning(self.explosions)
        self.exploded = True 
        
class Explosion(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('explosion', x, y, col=col)
    def schedule_for_deletion(self, timer):
        threading.Timer(timer, self.die).start()

class Powerup(Entity):
    def __init__(self, name, x, y, col=0):
        super().__init__(name, x, y, col=col)
        self.flamepass = True
        self.score_value = 1000


