import queue
import threading
import time
import random


class Server(threading.Thread):
    def __init__(self, server_id, queue, service_dist, update_gui):
        super().__init__()
        self.server_id = server_id
        self.queue = queue
        self.service_dist = service_dist
        self.running = True
        self.update_gui = update_gui

    def run(self):
        while self.running:
            try:
                customer = self.queue.get(timeout=1)
                self.update_gui(self.server_id, f"Serving {customer}")
                service_time = self.service_dist.rvs()
                time.sleep(service_time)
                self.update_gui(self.server_id, "Idle")
            except queue.Empty:
                continue

    def stop(self):
        self.running = False