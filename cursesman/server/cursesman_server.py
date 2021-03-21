from cursesman.entities import *
from cursesman.settings import SERVER_PORT
from cursesman.main import *
from cursesman.rooms import rooms

import threading
import asyncio
import socketio
import tornado
import pickle
import uuid
import time

SERVER_UUID = str(uuid.uuid4())

class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()

    def cancel(self):
        self._task.cancel()

class CursesmanServer():
    def __init__(self):
        self.room = []
        self.current_room = 0
        self.last_act_time = time.time()
        self.running = False

    async def init_room(self):
        self.room = init_room([], rooms[self.current_room])
        self.running = True
        await self.start_loop()

    def destroy_game(self):
        self.room = []
        self.current_room = 0
        self.last_act_time = time.time()
        self.running = False

    async def start_loop(self):
        await self.event_loop()

    def update_room(self, update):
        client_uuid = [e.uuid for e in update if isinstance(e, Player)][0]
        updated_bomb = False
        # figure out what not to change
        cond = lambda x: x.owner != client_uuid
        unchanged_room = [e for e in self.room if cond(e)]
        # for the update, we should claim ownership of any bombs
        for b in [e for e in update if isinstance(e, Bomb) or isinstance(e, Explosion)]:
            if b.owner != SERVER_UUID:
                updated_bomb = True
                b.fuse += 1
                b.burnFuse(quiet=True)
                b.owner = SERVER_UUID

        self.room = unchanged_room + update


    async def event_loop(self):

        # remove uuid duplicates here?
        #self.stats()
        # event loop
        players = [e for e in self.room if isinstance(e, Player)]

        # now deal with interactions
        handle_exploded_bombs(self.room, players)
        handle_powerups(self.room)
        self.last_act_time = handle_enemies(self.room, self.last_act_time)
        self.current_room, _, _, self.room = handle_doors(self.room, self.current_room, None)
        # remove dead stuff
        self.room = [e for e in self.room if e.alive]

        await broadcast_update(self.room)

        if len(sids) == 0:
            self.running = False

        if self.running:
            Timer(0.05, self.event_loop)



    def stats(self):
        print('------------------')
        print('Stats:')
        print(f'SIDs: {len(sids)}')
        print(f'Players: {len([e for e in self.room if isinstance(e, Player)])}')
        print(f'Bombs: {len([e for e in self.room if isinstance(e, Bomb)])}')
        print(f'Boomba: {len([e for e in self.room if isinstance(e, Explosion)])}')
        for i, p in enumerate(sorted([e for e in self.room if isinstance(e, Player)], key=lambda x: x.uuid)):
            print(f'Player {p.uuid}, x={p.x}, y={p.y}')

cursesman_server = CursesmanServer()
sids = []

sio = socketio.AsyncServer(async_mode='tornado')

app = tornado.web.Application(
    [
        (r"/socket.io/", socketio.get_tornado_handler(sio)),
    ],
)

async def broadcast_update(room_state):
    await sio.emit('room_server_refresh', pickle.dumps(room_state))

@sio.event
def room_event(sid, data):
    # update internal room representation
    room = pickle.loads(data)
    print(room)
    # resolve conflicts
    cursesman_server.update_room(room)

@sio.event
async def connect(sid, environ, *args, **kwargs):
    global sids
    print('connect ', sid)
    sids.append(sid)
    if len(sids) == 1:
        # init the room
        await cursesman_server.init_room()
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

