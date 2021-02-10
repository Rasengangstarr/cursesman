from cursesman.sprite_loader import Sprite

class Entity():
    def __init__(self, name, x, y, col=0):
        self.name = name
        self.last_state = 'idle' # this is used to do animation changes
        self.state = 'idle' # idle is always the default state, everything needs an idle state
        self.x = x
        self.y = y
        self.col = col
        self.sprite = Sprite(self.name, self.state)

    def render(self, stdscr):
        self.sprite.render(stdscr, self.x, self.y, col=self.col)

    def update_state(self, new_state):
        self.last_state = self.state
        self.state = new_state
        if self.state != self.last_state:
            self.sprite = Sprite(self.name, self.state)


class Character(Entity):
    def move(self, dx, dy):
        self.update_state('move')
        self.x += dx
        self.y += dy

class Player(Character):
    def __init__(self, x, y, col=1):
        super().__init__('player', x, y, col=col)
        self.bombs = [] # bombs the player has made

    def make_bomb(self):
        self.bombs.append(
            Bomb(self.x, self.y, col=self.col)
        )

class Bomb(Entity):
    def __init__(self, x, y, col=0):
        super().__init__('bomb', x, y, col=col)
        self.fuse = 50
        self.exploded = False

    def explode(self):
        self.state = 'explode'
        self.sprite = Sprite(self.name, 'explode')
        self.exploded = True

    def render(self, stdscr):
        self.fuse -= 1
        if self.fuse == 0:
            self.explode()
        super().render(stdscr)
