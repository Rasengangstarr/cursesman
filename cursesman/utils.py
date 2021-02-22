import ctypes
from cursesman.settings import MUSIC_DIR

from playsound import playsound
import threading


def play_sound(path):
    k = lambda: playsound(str(MUSIC_DIR / path))
    t = threading.Thread(target=k)
    t.start()

def loop_sound_wrapper(path, length):
    threading.Timer(length, loop_sound_wrapper, [path, length]).start()
    play_sound(path)

def loop_sound(path, length):
    k = lambda: loop_sound_wrapper(path, length)
    t = threading.Thread(target=k)
    t.start()
    return t
