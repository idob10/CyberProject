import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class DirectoryObserver(FileSystemEventHandler):
    def __init__(self, modify_queue):
        self._modify_queue = modify_queue

    def on_moved(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path + ',' + event.dest_path+','+str(event.is_directory))

    def on_modified(self, event):
        if (event.is_directory):
            return

        self._modify_queue.append(event.event_type + ',' + event.src_path)

    def on_deleted(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path+','+str(event.is_directory))

    def on_created(self, event):
        self._modify_queue.append(event.event_type + ',' + event.src_path+','+str(event.is_directory))

    def get_modify_queue(self):
        return self._modify_queue


if __name__ == "__main__":
    path = ".."
    q = []
    event_handler = DirectoryObserver(modify_queue=q)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
            if len(q) != 0:
                print(q.pop(0))
    finally:
        observer.stop()
        observer.join()