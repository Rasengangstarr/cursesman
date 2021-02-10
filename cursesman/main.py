import curses
from curses import wrapper
import datetime

from cursesman.sprite_loader import Sprite

#init curses
#curses.noecho()
#stdscr.nodelay(1)

#how many characters to use to represent one 'block' in game
fidelity = 4


chstr = "oo\nJL"

def drawmap(stdscr):
    for x in range (0,16):
        for y in range (0,13):
            #draw a gapped checkerboard like in screenshot
            if x % 2 == 0 and y % 2 == 0:
                #draw in blocks of 'fidelity', such that we can scale it up or down
                for bx in range(0,fidelity):
                    for by in range(0,fidelity):
                        stdscr.addch(y*fidelity+by, x*fidelity+bx, 'X')


def event_loop(stdscr):
    # Clear screen
    curses.curs_set(0)
    px = 5
    py = 5

    sprite = Sprite('player')
    while 1:
        stdscr.refresh()
        stdscr.clear()
        
        drawmap(stdscr)
        sprite.render(stdscr, px, py)
        inp = stdscr.getch()
        if inp in [ord('w'), ord('k')]:
            py = py - 1
        if inp in [ord('s'), ord('j')]:
            py = py + 1
        if inp in [ord('a'), ord('h')]:
            px = px - 1
        if inp in [ord('d'), ord('l')]:
            px = px + 1

def main():
    wrapper(event_loop)

if __name__ == '__main__':
    wrapper(main)

