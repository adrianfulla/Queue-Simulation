from QueuingSystem import QueueingSystem
import threading
from tkinter import ttk
import tkinter as tk


class QueueingSystemGUI:
    def __init__(self, root, system_params):
        self.root = root
        self.root.title("Queueing System Simulation")
        self.queue_frame = tk.Frame(root)
        self.queue_frame.pack()

        self.source_label = ttk.Label(self.queue_frame, text="Source:")
        self.source_label.grid(row=0, column=0, padx=10, pady=5)

        self.queue_label = ttk.Label(self.queue_frame, text="Queue:")
        self.queue_label.grid(row=0, column=1, padx=10, pady=5)

        self.servers_frame = tk.Frame(root)
        self.servers_frame.pack()

        self.source_customers = tk.Listbox(self.queue_frame, height=10, width=20)
        self.source_customers.grid(row=1, column=0, padx=10, pady=5)

        self.queue_customers = tk.Listbox(self.queue_frame, height=10, width=30)
        self.queue_customers.grid(row=1, column=1, padx=10, pady=5)

        self.server_labels = []
        for i in range(system_params["num_servers"]):
            label = ttk.Label(self.servers_frame, text=f"Server {i}: Idle")
            label.pack(anchor="w", padx=10)
            self.server_labels.append(label)

        self.system = QueueingSystem(
            system_params["arrival_rate"],
            system_params["service_rate"],
            system_params["num_servers"],
            system_params["discipline"],
            system_params["max_system_size"],
            system_params["source_size"],
            self.update_gui
        )
        self.simulation_thread = threading.Thread(target=self.system.start)

    def update_gui(self, server_id, message):
        if server_id == -1:
            self.queue_customers.delete(0, tk.END)
            for customer in list(self.system.queue.queue):
                self.queue_customers.insert(tk.END, f"Customer {customer}")
        else:
            self.server_labels[server_id].config(text=f"Server {server_id}: {message}")

    def start(self):
        self.simulation_thread.start()

    def stop(self):
        self.system.stop()
        self.simulation_thread.join()


class QueueingSystemSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Queueing System Setup")
        self.frame = tk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        self.params = {
            "arrival_rate": tk.DoubleVar(value=2.0),
            "service_rate": tk.DoubleVar(value=1.5),
            "num_servers": tk.IntVar(value=2),
            "discipline": tk.StringVar(value="FIFO"),
            "max_system_size": tk.IntVar(value=10),
            "source_size": tk.IntVar(value=20)
        }

        self.create_form()
        self.start_button = ttk.Button(self.frame, text="Iniciar Simulación", command=self.start_simulation)
        self.start_button.grid(row=6, column=0, columnspan=2, pady=10)

    def create_form(self):
        ttk.Label(self.frame, text="Tasa de llegada (λ):").grid(row=0, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["arrival_rate"]).grid(row=0, column=1)

        ttk.Label(self.frame, text="Tasa de servicio (μ):").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["service_rate"]).grid(row=1, column=1)

        ttk.Label(self.frame, text="Número de servidores:").grid(row=2, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["num_servers"]).grid(row=2, column=1)

        ttk.Label(self.frame, text="Disciplina de cola:").grid(row=3, column=0, sticky="w")
        ttk.Combobox(self.frame, textvariable=self.params["discipline"], values=["FIFO", "LIFO"]).grid(row=3, column=1)

        ttk.Label(self.frame, text="Tamaño máximo del sistema:").grid(row=4, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["max_system_size"]).grid(row=4, column=1)

        ttk.Label(self.frame, text="Tamaño de la fuente:").grid(row=5, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["source_size"]).grid(row=5, column=1)

    def start_simulation(self):
        self.frame.destroy()
        gui = QueueingSystemGUI(self.root, {key: var.get() for key, var in self.params.items()})
        gui.start()
