from cursesman.entities import *
from cursesman.settings import SERVER_PORT
from cursesman.main import *
from cursesman.rooms import rooms

import asyncio
import socketio
import tornado
import pickle
import uuid

SERVER_UUID = str(uuid.uuid4())

class CursesmanServer():
    def __init__(self):
        self.room = []
        self.current_room = 0

    def init_room(self):
        self.room = init_room([], rooms[self.current_room])

    def destroy_game(self):
        self.room = []
        self.current_room = 0

    def update_room(self, update):
        if self.room == []:
            self.room = update
        else:
            client_uuid = [e.uuid for e in update if isinstance(e, Player)][0]
            # figure out what not to change
            cond = lambda x: x.owner != client_uuid
            unchanged_room = [e for e in self.room if cond(e)]
            # for the update, we should claim ownership of any bombs
            for b in [e for e in update if isinstance(e, Bomb) or isinstance(e, Explosion)]:
                print('boomba : ' + str(b.uuid))
                if b.owner != SERVER_UUID:
                    b.fuse += 1
                    b.burnFuse(quiet=True)
                    b.owner = SERVER_UUID

            self.room = unchanged_room + update

            players = [e for e in self.room if isinstance(e, Player)]

            # now deal with interactions
            handle_exploded_bombs(self.room, players)
            handle_powerups(self.room)
            handle_enemies(self.room)
            self.current_room, _, _, self.room = handle_doors(self.room, self.current_room, None)
            # remove dead stuff
            self.room = [e for e in self.room if e.alive]


    def stats(self):
        print('------------------')
        print('Stats:')
        print(f'Players: {len([e for e in self.room if isinstance(e, Player)])}')
        print(f'Bombs: {len([e for e in self.room if isinstance(e, Bomb)])}')
        print(f'Boomba: {len([e for e in self.room if isinstance(e, Explosion)])}')
        for i, p in enumerate([e for e in self.room if isinstance(e, Player)]):
            print(f'Player {i+1}, x={p.x}, y={p.y}')

cursesman_server = CursesmanServer()
sids = []

sio = socketio.AsyncServer(async_mode='tornado')

app = tornado.web.Application(
    [
        (r"/socket.io/", socketio.get_tornado_handler(sio)),
    ],
)

@sio.event
async def room_event(sid, data):
    # update internal room representation
    cursesman_server.stats()
    room = pickle.loads(data)
    # resolve conflicts
    cursesman_server.update_room(room)
    # broadcast
    await sio.emit('room_server_refresh', pickle.dumps(cursesman_server.room))

@sio.event
async def connect(sid, environ, *args, **kwargs):
    global sids
    print('connect ', sid)
    sids.append(sid)
    if len(sids) == 1:
        # init the room
        cursesman_server.init_room()
        await sio.emit('init_room_from_server', pickle.dumps(cursesman_server.room))

    else:
        if len(cursesman_server.room) != 0:
            await sio.emit('init_room_from_server', pickle.dumps(cursesman_server.room))

@sio.event
async def disconnect(sid, *args, **kwargs):
    global sids
    sids = [s for s in sids if s != sid]
    print('disconnect ', sid)
    if len(sids) == 0:
        cursesman_server.room = []
        return


app.listen(SERVER_PORT)
tornado.ioloop.IOLoop.current().start()

