from cursesman.sprite_loader import Sprite

from functools import reduce
import threading
import time
import random

playerXDraw = 8*4
playerYDraw = 6*4

class State():
    def __init__(self, name, valididty):
        self.start = time.time()
        self.name = name
        self.valididty = valididty
    
    def check_validity(self):
        now = time.time()
        return self.start + self.valididty > now

class Entity():
    def __init__(self, name, x, y, col=0):
        self.name = name
        self.states = []
        self.x = x
        self.y = y
        self.col = col
        self.sprite = Sprite(self.name, self.get_state())
        self.alive = True

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

        if drawX < w-4 and drawY < h-4 and drawX > 0 and drawY > 0:
            #print (str(drawX))
            #print (str(drawY))
            self.sprite.render(stdscr, drawX, drawY)

    def update_state(self, state):
        old_state = self.get_state()
        self.states.append(State(state, 0.3))
        self.tick(old_state=old_state)

    def tick(self, old_state=None):
        # stale out anything we dont need
        if old_state is None:
            old_state = self.get_state()
        self.states = list(filter(lambda x: x.check_validity(), self.states))
        new_state = self.get_state()
        if old_state != new_state:
            self.sprite = Sprite(self.name, new_state)

class Unwalkable(): pass

class Destructable(): pass

class Door(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('door', x, y, col=col)

class StaticWall(Entity, Unwalkable):
    def __init__(self, x, y, col=0):
        super().__init__('static_wall', x, y, col=col)

class DestructibleWall(Entity, Unwalkable, Destructable):
    def __init__(self, x, y, col=0):
        super().__init__('destructible_wall', x, y, col=col)

class Character(Entity):
    def move(self, dx, dy):
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

class Enemy(Character, Destructable):
    def act(self,room): pass

#The Balloom seems to float around randomly
class Balloom(Enemy):
    def __init__(self, x, y, col=1):
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


    #TODD this obviously doesn't live here but i'm sleepy and wanna get it building so move it wherever you wish
    def check_can_move(self, x, y, walls):
      for wall in walls:
          if x > wall.x-4 and x < wall.x+4 and y > wall.y-4 and y < wall.y+4:
              return False
      return True
    

    def act(self, room):
        walls = [e for e in room if isinstance(e, Unwalkable)]
        if self.direction == 0:
            if (self.check_can_move(self.x-1,self.y, walls)):
                self.move(-self.speed, 0)
            else:
                self.changeDirection()
        if self.direction == 1:
            if (self.check_can_move(self.x+1,self.y, walls)):
                self.move(self.speed, 0)
            else:
                self.changeDirection()

        if self.direction == 2:
            if (self.check_can_move(self.x,self.y-1, walls)):
                self.move(0, -self.speed)
            else:
                self.changeDirection()
            
        if self.direction == 3:
            if (self.check_can_move(self.x,self.y+1, walls)):
                self.move(0, self.speed)
            else:
                self.changeDirection()



class Player(Character):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)

    def render(self, stdscr, px, py):
        #always draw the player at the same location
        self.sprite.render(stdscr, playerXDraw, playerYDraw)

class Bomb(Entity):
    def __init__(self, x, y, col=0, power=1):
        super().__init__('bomb', x, y, col=col)
        self.fuse = 1
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
        self.exploded = True
        self.explosions = [
            Explosion(self.x+dx, self.y+dy, col=self.col)
            for dx in range(-self.power*4, self.power*4+4, 4)
            for dy in range(-self.power*4, self.power*4+4, 4)
            if 0 in [dx, dy]
        ]
        self.die()


        
class Explosion(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('explosion', x, y, col=col)
        threading.Timer(0.3, self.die).start()
