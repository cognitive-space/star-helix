import threading

import websocket


def on_message(ws, message):
    pass


def on_error(ws, error):
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("websocket closed")


def on_open(ws):
    print("websocket open")


def run_ws(ws):
    ws.run_forever()


def start_socket(ws_url):
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    thread = threading.Thread(target=run_ws, args=(ws,), daemon=True)
    thread.start()

    return ws
