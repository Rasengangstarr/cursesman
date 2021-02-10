from curses import wrapper
import datetime

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


def drawplayer(stdscr, px, py):
    stdscr.addstr(round(py*fidelity), round(px*fidelity), "[oo]")
    stdscr.addstr(round(py*fidelity+1), round(px*fidelity), "qTTp")
    stdscr.addstr(round(py*fidelity+2), round(px*fidelity), " ii ")
    stdscr.addstr(round(py*fidelity+3), round(px*fidelity), "_||_")


def event_loop(stdscr):
    # Clear screen
    px = 0
    py = 0
    while 1:
        stdscr.refresh()
        stdscr.clear()
        
        drawmap(stdscr)
        drawplayer(stdscr, px, py)
        inp = stdscr.getch()
        if inp == ord('w'):
            py = py - 0.25
        if inp == ord('s'):
            py = py + 0.25
        if inp == ord('a'):
            px = px - 0.25
        if inp == ord('d'):
            px = px + 0.25

def main():
    wrapper(event_loop)

if __name__ == '__main__':
    wrapper(main)

