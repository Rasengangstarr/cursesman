from cursesman.entities import *
from cursesman.settings import SERVER_PORT

import asyncio
import socketio
import tornado
import pickle

class CursesmanServer():
    def __init__(self):
        self.room = []

    def update_room(self, update, master):
        if self.room == []:
            self.room = update
        else:
            # check if we are dealing with master or not
            client_uuid = [e.uuid for e in update if isinstance(e, Player)][0]
            # figure out what not to change
            print(master)
            if master:
                cond = lambda x: x.owner is not None and x.owner != client_uuid
            else:
                cond = lambda x: x.owner != client_uuid
            unchanged_room = [e for e in self.room if cond(e)]
            for k in unchanged_room:
                print(k.name)
            self.room = unchanged_room + update

    def stats(self):
        print('------------------')
        print('Stats:')
        print(f'Players: {len([e for e in self.room if isinstance(e, Player)])}')
        print(f'Bombs: {len([e for e in self.room if isinstance(e, Bomb)])}')
        for i, p in enumerate([e for e in self.room if isinstance(e, Player)]):
            print(f'Player {i+1}, x={p.x}, y={p.y}')

cursesman_server = CursesmanServer()
sids = []
master_sid = None

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
    cursesman_server.update_room(room, sid == master_sid)
    # broadcast
    await sio.emit('room_server_refresh', pickle.dumps(cursesman_server.room))

@sio.event
async def connect(sid, environ, *args, **kwargs):
    global sids
    global master_sid
    sids.append(sid)
    if len(sids) == 1:
        await sio.emit('set_master', '', room=sid)
        master_sid = sid
        print('master set to ' + sid)

    print('connect ', sid)
    if len(cursesman_server.room) != 0:
        await sio.emit('room_server_refresh', pickle.dumps(cursesman_server.room))

@sio.event
async def disconnect(sid, *args, **kwargs):
    global sids
    global master_sid
    sids = [s for s in sids if s != sid]
    print('disconnect ', sid)
    if len(sids) == 0:
        cursesman_server.room = []
        return
    if not master_sid in sids:
        master_sid = sids[0]
        await sio.emit('set_master', '', room=master_sid)




app.listen(SERVER_PORT)
tornado.ioloop.IOLoop.current().start()

