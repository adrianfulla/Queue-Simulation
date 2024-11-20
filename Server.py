import queue
import threading
import time
import random


class Server(threading.Thread):
    def __init__(self, server_id, queue, service_dist, update_gui, server_states):
        super().__init__()
        self.server_id = server_id
        self.queue = queue
        self.service_dist = service_dist
        self.running = True
        self.update_gui = update_gui
        self.server_states = server_states

    def run(self):
        while self.running:
            try:
                customer = self.queue.get(timeout=1)
                self.server_states[self.server_id] = True 
                self.update_gui(self.server_id, f"Atendiendo a {customer}")
                service_time = self.service_dist.rvs()
                time.sleep(service_time)
                self.queue.task_done()
                self.server_states[self.server_id] = False
                self.update_gui(self.server_id, "Idle")
                self.update_gui(-1, None)
            except queue.Empty:
                continue

    def stop(self):
        self.running = False