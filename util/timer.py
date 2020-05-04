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
        self.use_thread = False
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self._timer     = None
        self._processor = None

    def _timer(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def _process(self):
        sleep(self.interval)
        self.function(*self.args, **self.kwargs)
        self._process()

    def start(self, use_thread = True):
        self.use_thread = use_thread
        if not self.is_running:
            if self.use_thread:
                self._timer = PythonTimer(self.interval, self._timer)
                self._timer.start()
            else:
                self._processor = Process(target=self._process)
                self._processor.start()
            self.is_running = True

    def stop(self):
        if self._timer and self.is_running:
            if self.use_thread:
                self._timer.cancel()
            else:
                self._processor.terminate()
            self.is_running = False

    def toggle(self, use_thread = True):
        if self.is_running:
            self.stop()
        else:
            self.start(use_thread)

class ProcessTimer(Process):
    def __init__(self, interval, function, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super(ProcessTimer, self).__init__()
        self.interval = interval
        self.function = function
        self.finished = Event()
        self.is_running = False

    def toggle(self):
        if self.is_running:
            self.stop()
        else:
            self.start()

    def stop(self):
        """Stop the timer if it hasn't finished yet"""
        self.finished.set()
        self.is_running = False

    def start(self):
        self.is_running = True
        self.finished.wait(self.interval)
        if not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
        self.finished.set()
