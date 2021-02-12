import socket
import sys
import os
import pathlib
import playsound
import time
import pydub
import pydub.playback
import collections
import threading
from multiprocessing import Queue

__all__ = [
        'Listener',
        'Player',
        'Rocker'
    ]

class Listener:
    def __init__(self, trigger, port, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', port))
        self.sock.listen(1)
        self._message = trigger
        self.alive = True

    def listen(self):
        '''
        Yield True when trigger message is received
        '''
        while self.alive:
            client, addr = self.sock.accept()
            try:
                while self.alive:
                    data = client.recv(4096)
                    if data == self._message:
                        yield True
                    else:
                        break
            finally:
                client.close()
        self.sock.close()


class Player:
    def __init__(self, path, *args, **kwargs):
        self.directory = None
        self.file = None
        self._asset = None
        self._path = pathlib.Path(path)
        if self._path.is_file():
            self.file = self._path
            self.directory = self._path.parent
            self._select_asset()
        elif self._path.is_dir():
            self.directory = self._path
            self.get_next()

    def _select_asset(self):
        print(f'Selecting file {self.file.name}')
        self._asset = pydub.AudioSegment.from_wav(self.file)
        self._asset -= 24

    def get_next(self, selectFirstItem=False):
        selectNext = selectFirstItem
        previous = self.file
        for p in self.directory.glob('**/*'):
            if p.is_file():
                if ((self.file is None) or selectNext):
                    self.file = p
                    self._select_asset()
                    break
                elif p.samefile(self.file):
                    selectNext = True
        else:
            if self.file == previous:
                self.get_next(selectFirstItem=True)
                self._select_asset()
                return
            else:
                self.file = None

    def play(self):
        if self._asset is None:
            self.get_next()
        pydub.playback.play(self._asset)


class Rocker(Player, Listener):
    def __init__(self, path='.', trigger=b'letsrock', port=54045, *args, **kwargs):
        super().__init__(path, *args, **kwargs)
        Listener.__init__(self, trigger, port, *args, **kwargs)
        self.queue = Queue()
        self.terminator = Queue()
        self.threads = collections.deque()
        t = threading.Thread(target=self.play_in_thread)
        t.start()
        self.threads.append(t)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.alive = False
        self.terminator.put(True)
        for t in self.threads:
            t.join()

    def play_in_thread(self):
        while self.alive and self.terminator.empty():
            if not self.queue.empty():
                print("LET'S ROCK")
                super().play()
                super().get_next()
                self.queue.get()
            time.sleep(.0000001)

    def run(self):
        for triggered in super().listen():
            if self.queue.empty():
                self.queue.put(True)

