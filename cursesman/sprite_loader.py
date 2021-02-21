from cursesman.settings import SPRITES_DIR

import curses



class Sprite():
    def __init__(self, entity, state):
        # load the sprite sheet
        path = f'{entity}/{state}.txt'
        self.sprite_data = [list(l.replace('\n', '')) for l in open(str(SPRITES_DIR / path)).readlines()
                            if l != '']
        self.height = len(self.sprite_data)
        self.width = max([len(l) for l in self.sprite_data])
        # check how many times height does into width
        self.sprite_count = int(self.height / self.width)
        self.sprite_list = [
            self.sprite_data[(i*self.width):(i*self.width)+self.width]
            for i in range(self.sprite_count)
        ]
        self.render_count = 0

    def render(self, stdscr, x, y, col=0):
        stdscr.attron(curses.color_pair(col))
        rid = int(self.render_count/15) % self.sprite_count
        sprite_frame = self.sprite_list[rid]
        sx = int(x)
        sy = int(y)
        cx, cy = sx, sy
        for i in range(self.width):
            string = sprite_frame[i]
            stdscr.addstr(cy+i, cx, ''.join(string))
        self.render_count += 1
        stdscr.attroff(curses.color_pair(col))



