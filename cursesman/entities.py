from sprite_loader import Sprite

from functools import reduce
import threading
import time

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

    def render(self, stdscr):
        self.sprite.render(stdscr, self.x, self.y, col=self.col)

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

class Player(Character):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)

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
