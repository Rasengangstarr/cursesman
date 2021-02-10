import curses
from curses import wrapper
import datetime

from cursesman.entities import Player

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


def init_curses(stdscr):

    # TODO: replace with proper resfresh code
    curses.halfdelay(3) # 10/10 = 1[s] inteval
    curses.curs_set(0)

    # Clear and refresh the screen for a blank canvas
    #stdscr.clear()
    #stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    event_loop(stdscr)

def event_loop(stdscr):
    # Clear screen
    height, width = stdscr.getmaxyx()

    player = Player(0, 0)
    while 1:
        stdscr.erase()
        stdscr.refresh()

        # rendering
        # NOTE: rendering needs to happen before inptu logic
        drawmap(stdscr)
        player.render(stdscr)
        for i, bomb in enumerate(player.bombs):
            bomb.render(stdscr)
            if bomb.fuse <= -5:
                del player.bombs[i]

        
        # input logic
        # TODO: move this to a proper handler class
        inp = stdscr.getch()

        if inp in [ord('w'), ord('k')]:
            player.move(0, -1)
        elif inp in [ord('s'), ord('j')]:
            player.move(0, 1)
        elif inp in [ord('a'), ord('h')]:
            player.move(-1, 0)
        elif inp in [ord('d'), ord('l')]:
            player.move(1, 0)
        elif inp in [ord(' '), ord('e')]:
            player.make_bomb()
        else:
            # it would be nice to automatically update all non movign entities as idle
            player.update_state('idle')



def main():
    wrapper(init_curses)

if __name__ == '__main__':
    main()

