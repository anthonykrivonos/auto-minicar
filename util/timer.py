import sys
from os.path import join, dirname
from threading import Timer as PythonTimer
from multiprocessing import Process, Event
from time import sleep

sys.path.append(join(dirname(__file__), '..'))

# reference: https://stackoverflow.com/a/13151104/7432026

class Timer(object):

    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.function   = function
        self.interval   = interval
        self.use_thread = True
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self._timer     = None
        self._processor = None
        self._on_kill   = None

    def _timer(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def _process(self):
        sleep(self.interval)
        self.function(*self.args, **self.kwargs)
        self._process()

    def use_mp(self):
        print("Using multiprocessing")
        new_timer = Timer(self.interval, self.function, *self.args, **self.kwargs)
        new_timer.use_thread = False
        return new_timer

    def start(self):
        if not self.is_running:
            if self.use_thread:
                print("Started thread timer")
                self._timer = PythonTimer(self.interval, self._timer)
                self._timer.start()
            else:
                print("Started multiprocessing timer")
                self._processor = Process(target=self._process)
                self._processor.start()
            self.is_running = True

    def stop(self):
        if ((self.use_thread and self._timer) or (not self.use_thread and self._processor)) and self.is_running:
            if self.use_thread:
                print("Canceled timer")
                self._timer.cancel()
            else:
                print("Terminated processor")
                self._processor.terminate()
            self.is_running = False

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()
    
    def on_kill(self, callback):
        self._on_kill = callback
        return self

    def kill(self):
        self.stop()
        if self._on_kill:
            self._on_kill()
