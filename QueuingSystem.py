import random
import queue
import time
from Server import Server

class QueueingSystem:
    def __init__(self, arrival_dist, service_dist, num_servers, discipline, max_system_size, source_size, update_gui):
        self.arrival_dist = arrival_dist
        self.service_dist = service_dist
        self.num_servers = num_servers
        self.discipline = discipline
        self.max_system_size = max_system_size
        self.source_size = source_size
        self.queue = queue.Queue(maxsize=max_system_size)
        self.servers = [
            Server(i, self.queue, service_dist, update_gui)
            for i in range(num_servers)
        ]
        self.running = True
        self.update_gui = update_gui

    def start(self):
        for server in self.servers:
            server.start()

        customer_id = 0
        while self.running:
            if self.queue.qsize() < self.max_system_size:
                inter_arrival_time = self.arrival_dist.rvs()
                time.sleep(inter_arrival_time)
                if customer_id < self.source_size:
                    try:
                        self.queue.put_nowait(customer_id)
                        self.update_gui(-1, customer_id)
                        customer_id += 1
                    except queue.Full:
                        print("Queue is full. Customer could not enter.")
            else:
                time.sleep(0.1)

    def stop(self):
        self.running = False
        for server in self.servers:
            server.stop()
        for server in self.servers:
            server.join()