import os
from quotedb.scripts.runscript import runScript

from quotedb.scripts.kill_from_pid import killFromPid
import sys
import time


rundir = os.environ['RUNDIR']
if not os.path.exists(rundir):
    print('EPIC FAIIL')
    sys.exit()
pidfile = os.path.join(rundir, "startcandles.pid")
runScript('startcandles.py')
while True:
    time.sleep(50)
    killFromPid(pidfile)