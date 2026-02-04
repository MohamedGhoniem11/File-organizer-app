import customtkinter as ctk
from src.services.logger import logger, log_queue
import queue

class LogsFrame(ctk.CTkFrame):
    """A scrollable frame for real-time log display."""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Application Logs", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        self.textbox = ctk.CTkTextbox(self, state="disabled", font=ctk.CTkFont(family="Consolas", size=12))
        self.textbox.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        self.after(100, self.update_logs)

    def update_logs(self):
        """Processes logs from the queue and displays them."""
        while not log_queue.empty():
            try:
                record = log_queue.get_nowait()
                msg = f"{record.levelname}: {record.getMessage()}\n"
                
                self.textbox.configure(state="normal")
                self.textbox.insert("end", msg)
                self.textbox.see("end")
                self.textbox.configure(state="disabled")
            except queue.Empty:
                break
        
        self.after(100, self.update_logs)
