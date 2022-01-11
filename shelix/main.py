#!/usr/bin/env python3

import copy
import datetime
import json
import os
import queue
import shlex
import subprocess
import time
import traceback

import typer

import asynchronousfilereader as asfr

from shelix_cli.log_socket import start_socket

os.environ.setdefault('SHELIX_WS_URL', 'wss://star-helix.herokuapp.com/')


class FullSafeReader(asfr.AsynchronousFileReader):
    def run(self):
        while 1:
            try:
                return super().run()

            except queue.Full:
                pass
                # drop messages when full


def send_lines(ws, log_id, content, last_send, force=False):
    send = False
    if content:
        now = datetime.datetime.utcnow()

        if force:
            send = True

        elif len(content) > 1024 * 300:
            send = True

        else:
            diff = now - last_send
            diff = diff.total_seconds()
            send = diff >= 3

        if send:
            try:
                ws.send(json.dumps({'log_id': log_id, 'content': content}))

            except:
                traceback.print_exc()
                content = ''

            else:
                content = ''
                last_send = now

    return content, last_send

def main(
        command: str,
        log_id: str = typer.Argument("Log ID", envvar='SHELIX_LOGID'),
        token: str = typer.Argument("API Token", envvar='SHELIX_TOKEN'),
        ws_url: str = typer.Argument("Server URL", envvar='SHELIX_WS_URL')
    ):

    q = queue.Queue(maxsize=1024 * 1024)

    env = copy.copy(os.environ)
    env['PYTHONUNBUFFERED'] = '1'

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        bufsize=0,
        env=env,
    )

    reader = asfr.AsynchronousFileReader(process.stdout, q)
    last_send = datetime.datetime.utcnow()
    content = ''

    ws_url = f'{ws_url}/?token={token}'
    ws = start_socket(ws_url)

    while not reader.eof():
        while not q.empty():
            line = q.get()
            if line:
                line = line.decode()
                print(line, end='')
                content += line
                content, last_send = send_lines(ws, log_id, content, last_send)

        time.sleep(0.1)

    send_lines(ws, log_id, content, last_send, force=True)
    ws.close()


if __name__ == "__main__":
    typer.run(main)
