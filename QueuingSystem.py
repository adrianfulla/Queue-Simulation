import random
import threading
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
        self.remaining_source = source_size
        self.queue = queue.Queue(maxsize=(max_system_size - num_servers))
        self.inf_servers = num_servers == float('inf')
        if not self.inf_servers:
            self.server_states = [False] * num_servers
            self.servers = [
                Server(i, self.queue, service_dist, update_gui, self.server_states)
                for i in range(num_servers)
            ]
        self.running = True
        self.update_gui = update_gui

    def start(self):
        if not self.inf_servers:
            for server in self.servers:
                server.start()

        customer_id = 0
        while self.running:
            if self.remaining_source == 0 and self.queue.empty() and (self.inf_servers or not any(self.server_states)):
                self.running = False
                break
            
            if self.queue.qsize() < self.max_system_size:
                inter_arrival_time = self.arrival_dist.rvs()
                time.sleep(inter_arrival_time)
                
                if self.remaining_source > 0:
                    try:
                        self.queue.put_nowait(customer_id)
                        self.remaining_source -= 1
                        self.update_gui("source", self.remaining_source)
                        self.update_gui(-1, customer_id)
                        if self.inf_servers:
                            threading.Thread(target=self.process_client, args=(customer_id,)).start()

                        customer_id += 1
                    except queue.Full:
                        self.remaining_source -= 1
                        self.update_gui("source", self.remaining_source)
                        print("Sistema no permite más")
            else:
                time.sleep(0.1)

    def process_client(self,customer_id):
        try:
            # Obtener cliente de la cola
            customer = self.queue.get(timeout=1)
            self.update_gui("server", f"Atendiendo al cliente {customer}")
            
            # Simular tiempo de servicio
            service_time = self.service_dist.rvs()
            time.sleep(service_time)
            
            # Marcar como terminado
            self.queue.task_done()
            self.update_gui("server", "Idle")
            self.update_gui(-1, None)  # Actualizar cola en la GUI
        except queue.Empty:
            pass

    def stop(self):
        self.running = False
        if not self.inf_servers:
            for server in self.servers:
                server.stop()
            for server in self.servers:
                server.join()