import tkinter as tk
from GUI import QueueingSystemSetup


if __name__ == "__main__":
    root = tk.Tk()
    setup = QueueingSystemSetup(root)
    root.mainloop()
