import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_moved(self, event):
        print(event.event_type,'\n',event.src_path,'\n',event.dest_path)
    
    def on_modified(self, event):
        if (event.is_directory):
            return
        return (event.event_type,event.src_path)

    def on_deleted(self, event):
        print(event.event_type,event.src_path)

    def on_created(self, event):
        print(event.event_type,event.src_path)

if __name__ == "__main__":
    path = "."
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()