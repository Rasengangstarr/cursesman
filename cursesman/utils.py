from playsound import playsound
import threading

def play_sound(path):
    k = lambda: playsound(path)
    t = threading.Thread(target=k)
    t.start()

def loop_sound(path, length):
    threading.Timer(length, loop_sound, [path, length]).start()
    play_sound(path)
