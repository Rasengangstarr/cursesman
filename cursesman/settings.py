import os
from pathlib import Path
# magic numbers, path defenitions etc should live here


ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = ROOT_DIR / 'sprites'
MUSIC_DIR = ROOT_DIR / 'music'

# constants

FIDELITY = 4


# netcode stuff
SERVER_ADDRESS = od.environ.get('CURSESMAN_SERVER_ADDRESS', 'localhost') # load from environment var if set
SERVER_PORT = 12321
