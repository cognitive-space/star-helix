#!/usr/bin/env python3

import datetime
import time
import sys

from haikunator import Haikunator


haikunator = Haikunator()
wait = 3
limit = 100
if len(sys.argv) >= 2:
    wait = int(sys.argv[1])

if len(sys.argv) >= 3:
    limit = int(sys.argv[2])

for i in range(0, limit):
    sys.stdout.write(
        "Out: {} {}\n".format(datetime.datetime.now(), haikunator.haikunate(delimiter=" ")))
    sys.stderr.write(
        "Err: {} {}\n".format(datetime.datetime.now(), haikunator.haikunate(delimiter=" ")))
    time.sleep(wait)
