import datetime
import os
import threading

import websocket


SHOW_ERRORS = int(os.environ.get('SHELIX_SHOW_LOGGING_ERRORS', '0'))


def on_message(ws, message):
    pass


def on_error(ws, error):
    if SHOW_ERRORS:
        ws.printer(error)


def on_close(ws, close_status_code, close_msg):
    ws.printer("websocket closed")


def on_open(ws):
    ws.printer("websocket open")


def run_ws(ws):
    ws.run_forever()


class WSPrinter(websocket.WebSocketApp):
    def __init__(self, ws_url, prefix, prefix_ts, *args, **kwargs):
        self.prefix = prefix
        self.prefix_ts = prefix_ts
        super().__init__(ws_url, *args, **kwargs)

    def printer(self, line):
        line = str(line)

        if self.prefix_ts:
            now = datetime.datetime.now(datetime.timezone.utc)
            line = self.prefix + f'{now.isoformat()}: ' + line

        else:
            line = self.prefix + line

        print(line)


def start_socket(ws_url, prefix='', prefix_ts=False):
    ws = WSPrinter(
        ws_url,
        prefix,
        prefix_ts,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    thread = threading.Thread(target=run_ws, args=(ws,), daemon=True)
    thread.start()

    return ws
