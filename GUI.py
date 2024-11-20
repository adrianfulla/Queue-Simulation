from QueuingSystem import QueueingSystem
import threading
from tkinter import ttk
import tkinter as tk
from scipy.stats import expon, erlang, uniform


class QueueingSystemSetup:
    def __init__(self, root):
        self.root = root
        self.root.title("Queueing System Setup")
        self.frame = tk.Frame(root)
        self.frame.pack(padx=20, pady=20)

        self.params = {
            "arrival_dist": tk.StringVar(value="Markoviana"),
            "arrival_param": tk.DoubleVar(value=2.0),
            "service_dist": tk.StringVar(value="Markoviana"),
            "service_param": tk.DoubleVar(value=1.5),
            "num_servers": tk.StringVar(value="2"),
            "discipline": tk.StringVar(value="FIFO"),
            "max_system_size": tk.StringVar(value="10"),
            "source_size": tk.StringVar(value="20")
        }

        self.create_form()
        self.start_button = ttk.Button(self.frame, text="Iniciar Simulación", command=self.start_simulation)
        self.start_button.grid(row=8, column=0, columnspan=2, pady=10)
    
    def toggle_infinity(self, key, entry_widget):
        """Alternar entre infinito y valor editable."""
        current_value = self.params[key].get()
        if current_value == "∞":
            self.params[key].set("1")
            entry_widget.config(state="normal")
        else:
            self.params[key].set("∞")
            entry_widget.config(state="disabled")
        
    def create_form(self):
        ttk.Label(self.frame, text="Distribución de llegadas:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(self.frame, textvariable=self.params["arrival_dist"], values=["Markoviana", "Erlang", "Constante"]).grid(row=0, column=1)

        ttk.Label(self.frame, text="Parámetro de llegadas (λ):").grid(row=1, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["arrival_param"]).grid(row=1, column=1)

        ttk.Label(self.frame, text="Distribución de servicio:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(self.frame, textvariable=self.params["service_dist"], values=["Markoviana", "Erlang", "Constante"]).grid(row=2, column=1)

        ttk.Label(self.frame, text="Parámetro de servicio (μ):").grid(row=3, column=0, sticky="w")
        ttk.Entry(self.frame, textvariable=self.params["service_param"]).grid(row=3, column=1)

        ttk.Label(self.frame, text="Número de servidores:").grid(row=4, column=0, sticky="w")
        server_entry = ttk.Entry(self.frame, textvariable=self.params["num_servers"])
        server_entry.grid(row=4, column=1)
        ttk.Button(self.frame, text="∞", command=lambda: self.toggle_infinity("num_servers", server_entry)).grid(row=4, column=2)


        ttk.Label(self.frame, text="Disciplina de cola:").grid(row=5, column=0, sticky="w")
        ttk.Combobox(self.frame, textvariable=self.params["discipline"], values=["FIFO", "LIFO"]).grid(row=5, column=1)

        ttk.Label(self.frame, text="Tamaño máximo del sistema:").grid(row=6, column=0, sticky="w")
        max_system_entry = ttk.Entry(self.frame, textvariable=self.params["max_system_size"])
        max_system_entry.grid(row=6, column=1)
        ttk.Button(self.frame, text="∞", command=lambda: self.toggle_infinity("max_system_size", max_system_entry)).grid(row=6, column=2)

        ttk.Label(self.frame, text="Tamaño de la fuente:").grid(row=7, column=0, sticky="w")
        source_size_entry = ttk.Entry(self.frame, textvariable=self.params["source_size"])
        source_size_entry.grid(row=7, column=1)
        ttk.Button(self.frame, text="∞", command=lambda: self.toggle_infinity("source_size", source_size_entry)).grid(row=7, column=2)

    def parse_parameter(self, value):
        if value == "∞":
            return float('inf')
        return int(value) if value.isdigit() else float(value)


    def get_distribution(self, dist_name, param):
        if dist_name == "Markoviana":
            return expon(scale=1/param)  # λ is the rate parameter
        elif dist_name == "Erlang":
            k = int(param)  # Erlang's shape parameter
            return erlang(k, scale=1/param)
        elif dist_name == "Constante":
            return uniform(0, 1/param)  # Uniform(0, param)
        else:
            raise ValueError(f"Unsupported distribution: {dist_name}")

    def start_simulation(self):
        arrival_dist = self.get_distribution(self.params["arrival_dist"].get(), self.params["arrival_param"].get())
        service_dist = self.get_distribution(self.params["service_dist"].get(), self.params["service_param"].get())

        num_servers = self.parse_parameter(self.params["num_servers"].get())
        max_system_size = self.parse_parameter(self.params["max_system_size"].get())
        source_size = self.parse_parameter(self.params["source_size"].get())


        self.frame.destroy()
        gui = QueueingSystemGUI(self.root, {
            "arrival_dist": arrival_dist,
            "service_dist": service_dist,
            "num_servers": num_servers,
            "discipline": self.params["discipline"].get(),
            "max_system_size": max_system_size,
            "source_size": source_size
        })
        gui.start()

class QueueingSystemGUI:
    def __init__(self, root, system_params):
        self.root = root
        self.root.title("Queueing System Simulation")

        self.source_size = system_params["source_size"]
        # Servidores infinitos
        self.inf_servers = type(system_params["num_servers"]) is float
        self.attended = 0
        # Fuente
        self.source_label = ttk.Label(root, text=f"Fuente: {self.source_size}")
        self.source_label.pack(pady=10)

        # Cola
        self.queue_frame = tk.Frame(root)
        self.queue_frame.pack()
        self.queue_label = ttk.Label(self.queue_frame, text="Cola:")
        self.queue_label.grid(row=0, column=0, sticky="w")
        self.queue_listbox = tk.Listbox(self.queue_frame, height=10, width=30)
        self.queue_listbox.grid(row=1, column=0, padx=10, pady=5)

        # Servidores
        self.servers_frame = tk.Frame(root)
        self.servers_frame.pack()
        self.server_labels = []
        if not self.inf_servers:
            for i in range(system_params["num_servers"]):
                label = ttk.Label(self.servers_frame, text=f"Servidor {i}: Idle")
                label.pack(anchor="w", padx=10)
                self.server_labels.append(label)
        
        label = ttk.Label(self.servers_frame, text=f"Clientes Atendidos: {self.attended}")
        label.pack(anchor="w", padx=10)
        self.server_labels.append(label)
        
        # Botón para volver al Setup (escondido inicialmente)
        self.back_to_setup_button = ttk.Button(root, text="Volver al Setup", command=self.return_to_setup)
        self.back_to_setup_button.pack(pady=10)
        self.back_to_setup_button.pack_forget()  # Esconde el botón al inicio

        # Inicialización del sistema
        self.system = QueueingSystem(
            system_params["arrival_dist"],
            system_params["service_dist"],
            system_params["num_servers"],
            system_params["discipline"],
            system_params["max_system_size"],
            self.source_size,
            self.update_gui
        )
        self.simulation_thread = threading.Thread(target=self.run_simulation)

    def update_gui(self, key, value):
        if key == -1:  # Actualizar cola
            self.queue_listbox.delete(0, tk.END)
            for customer in list(self.system.queue.queue):
                self.queue_listbox.insert(tk.END, f"Cliente {customer}")
        elif key == "source":  # Actualizar fuente
            self.source_label.config(text=f"Fuente: {value}")
        else:  # Actualizar servidor
            if not self.inf_servers:
                self.server_labels[key].config(text=f"Servidor {key}: {value}")
            if value != "Idle":
                self.attended += 1
                self.server_labels[-1].config(text=f"Clientes Atendidos: {self.attended}")

    def run_simulation(self):
        self.system.start()
        self.back_to_setup_button.pack()

    def return_to_setup(self):
        # Detener la simulación y regresar a la pantalla de Setup
        self.system.stop()
        self.simulation_thread.join()
        for widget in self.root.winfo_children():
            widget.destroy()  # Eliminar todos los widgets de la pantalla actual
        QueueingSystemSetup(self.root)  # Regresar a la pantalla de Setup

    def start(self):
        self.simulation_thread.start()

    def stop(self):
        self.system.stop()
        self.simulation_thread.join()    