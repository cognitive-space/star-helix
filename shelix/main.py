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


from haikunator import Haikunator

import asynchronousfilereader as asfr
import typer


from shelix.log_socket import start_socket

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
        ws_url: str = typer.Argument("Server URL", envvar='SHELIX_WS_URL'),
        bypass: bool = typer.Option(False, help="Bypass Reporting to the server", envvar="SHELIX_BYPASS"),
        prefix: str = typer.Option('', help="Prefix log output", envvar="SHELIX_PREFIX"),
        prefix_disable_random: bool = typer.Option(False, envvar="SHELIX_PREFIX_DISABLE_RANDOM"),
        prefix_ts: bool = typer.Option(False, help="Prefix log output with Timestamp", envvar="SHELIX_TS_PREFIX"),
    ):

    if prefix:
        if prefix_disable_random:
            prefix = f'{prefix}: '

        else:
            haikunator = Haikunator()
            rando = '-'.join(haikunator.haikunate(token_length=3).split('-')[1:])
            prefix = f'{prefix}[{rando}]: '

    q = queue.Queue(maxsize=1024 * 1024)

    env = copy.copy(os.environ)
    env['PYTHONUNBUFFERED'] = '1'

    if bypass:
        print('Bypassing log send to server')

    else:
        ws_url = f'{ws_url}/?token={token}'
        ws = start_socket(ws_url, prefix, prefix_ts)

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

    while not reader.eof():
        while not q.empty():
            line = q.get()
            if line:
                if prefix_ts:
                    now = datetime.datetime.now(datetime.timezone.utc)
                    line = prefix + f'{now.isoformat()}: ' + line.decode()

                else:
                    line = prefix + line.decode()

                print(line, end='')
                if not bypass:
                    content += line
                    content, last_send = send_lines(ws, log_id, content, last_send)

        time.sleep(0.1)

    if not bypass:
        send_lines(ws, log_id, content, last_send, force=True)
        ws.close()


def run_cli():
    typer.run(main)


if __name__ == "__main__":
    run_cli()
