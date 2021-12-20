#!/usr/bin/env python3

import copy
import os
import queue
import shlex
import subprocess
import time

import typer

import asynchronousfilereader as asfr


def main(command):
    q = queue.Queue()

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

    while not reader.eof():
        while not q.empty():
            line = q.get()
            print(line.decode(), end='')

        time.sleep(0.1)


if __name__ == "__main__":
    typer.run(main)
