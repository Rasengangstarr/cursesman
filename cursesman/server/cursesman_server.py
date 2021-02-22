from cursesman.entities import *
from cursesman.settings import SERVER_PORT

import asyncio
import socketio
import tornado
import pickle

class CursesmanServer():
    def __init__(self):
        self.room = []

    def update_room(self, update):
        if self.room == []:
            self.room = update
        else:
            # for now just merge
            new_entities = {e.uuid for e in update}
            old = [e for e in self.room if e.uuid not in new_entities] 
            self.room = update + old

    def stats(self):
        print('------------------')
        print('Stats:')
        print(f'Players: {len([e for e in self.room if isinstance(e, Player)])}')
        print(f'Bombs: {len([e for e in self.room if isinstance(e, Bomb)])}')
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
    sids.append(sid)
    print('connect ', sid)
    if len(cursesman_server.room) != 0:
        await sio.emit('room_server_refresh', pickle.dumps(cursesman_server.room))

@sio.event
def disconnect(sid, *args, **kwargs):
    global sids
    sids = [s for s in sids if s != sid]
    print('disconnect ', sid)
    if len(sids) == 0:
        cursesman_server.room = []


app.listen(SERVER_PORT)
tornado.ioloop.IOLoop.current().start()

