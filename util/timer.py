import sys
from os.path import join, dirname
from threading import Timer as PythonTimer

sys.path.append(join(dirname(__file__), '..'))

# reference: https://stackoverflow.com/a/13151104/7432026

class Timer(object):

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = PythonTimer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer and self.is_running:
            self._timer.cancel()
            self.is_running = False