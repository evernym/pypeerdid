import threading


class CmdLog:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.lock.release()


