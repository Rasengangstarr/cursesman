from cursesman.sprite_loader import Sprite
import threading

class Entity():
    def __init__(self, name, x, y, col=0):
        self.name = name
        self.last_state = 'idle' # this is used to do animation changes
        self.state = 'idle' # idle is always the default state, everything needs an idle state
        self.x = x
        self.y = y
        self.col = col
        self.sprite = Sprite(self.name, self.state)
        self.alive = True
    def die(self):
        self.alive = False
    def render(self, stdscr):
        self.sprite.render(stdscr, self.x, self.y, col=self.col)
    def update_state(self, new_state):
        self.last_state = self.state
        self.state = new_state
        if self.state != self.last_state:
            self.sprite = Sprite(self.name, self.state)

class DestructibleWall(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('destructible_wall', x, y, col=col)

class Character(Entity):
    def move(self, dx, dy):
        self.update_state('move')
        self.x += dx
        self.y += dy

class Player(Character):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)

class Bomb(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('bomb', x, y, col=col)
        self.fuse = 1
        self.exploded = False
        self.burnFuse()

    def burnFuse(self):
        if self.fuse > 0:
            self.fuse -= 1
            threading.Timer(1.0, self.burnFuse).start()
        else:
            self.explode()

    def explode(self):
        self.state = 'explode'
        self.sprite = Sprite(self.name, 'explode')
        self.exploded = True
        threading.Timer(1.0, self.die).start()
        

