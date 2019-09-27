import sys
import threading


class Console:
    def __init__(self):
        self.lock = threading.Lock()
        self.prompting = False

    def __enter__(self):
        self.lock.acquire()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.lock.release()

    def prompt(self):
        with self:
            sys.stdout.write('> ')
            self.prompting = True

    def say(self, msg):
        with self:
            if self.prompting:
                sys.stdout.write('\n')
                self.prompting = False
            sys.stdout.write(msg)
            sys.stdout.write('\n')
