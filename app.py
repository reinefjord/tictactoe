#!/usr/bin/env python3
import json

import tornado.ioloop
import tornado.web
import tornado.websocket


WS_CLIENTS = []

STATE = {
    'x': set(),
    'o': set(),
    'turn': 'x',
    'winner': 'Ingen'
}

WINSTATES = [
    {1, 2, 3},
    {4, 5, 6},
    {7, 8, 9},
    {1, 4, 7},
    {2, 5, 8},
    {3, 6, 9},
    {1, 5, 9},
    {3, 5, 7}
]


def reset():
    STATE['x'] = set()
    STATE['o'] = set()
    STATE['turn'] = 'x'


def is_win(moves):
    for win in WINSTATES:
        if win <= moves:
            return True
    return False


def is_end():
    if len(STATE['x']) + len(STATE['o']) == 9:
        return True
    return False


def is_valid_move(move):
    return move not in STATE['x'] | STATE['o']


def send_state(ws):
    state = {'positions': {}, 'turn': STATE['turn'], 'winner': STATE['winner']}
    for i in range(1, 10):
        if i in STATE['x']:
            state['positions'][i] = 'x'
        elif i in STATE['o']:
            state['positions'][i] = 'o'
        else:
            state['positions'][i] = None
    state['turn'] = STATE['turn']
    data = json.dumps(state)
    ws.write_message(data)


def announce_state():
    for ws in WS_CLIENTS:
        send_state(ws)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        with open('index.html') as f:
            self.write(f.read())


class TicTacWebSocket(tornado.websocket.WebSocketHandler):
    def open(self):
        WS_CLIENTS.append(self)
        send_state(self)

    def on_message(self, message):
        player = STATE['turn']
        move = int(message)
        if not is_valid_move(move):
            return
        STATE[player].add(move)
        if is_win(STATE[player]):
            STATE['winner'] = player
            reset()
        elif is_end():
            STATE['winner'] = 'Ingen'
            reset()
        else:
            STATE['turn'] = 'x' if player == 'o' else 'o'
        announce_state()

    def on_close(self):
        WS_CLIENTS.remove(self)


def make_app():
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static"}),
            (r"/websocket", TicTacWebSocket),
        ],
        websocket_ping_interval=10
    )


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
