import queue
import threading
import time
import random


class Server(threading.Thread):
    def __init__(self, server_id, queue, service_rate, discipline, update_gui):
        super().__init__()
        self.server_id = server_id
        self.queue = queue
        self.service_rate = service_rate
        self.discipline = discipline
        self.running = True
        self.update_gui = update_gui

    def run(self):
        while self.running:
            try:
                if self.discipline == 'FIFO':
                    customer = self.queue.get(timeout=1)
                elif self.discipline == 'LIFO':
                    customer = self.queue.queue.pop()
                    self.queue.task_done()
                else:
                    raise ValueError(f"Unsupported discipline: {self.discipline}")

                self.update_gui(self.server_id, f"Serving {customer}")
                service_time = random.expovariate(self.service_rate)
                time.sleep(service_time)
                self.update_gui(self.server_id, "Idle")
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
