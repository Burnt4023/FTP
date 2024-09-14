import tkinter as tk
from tkinter import messagebox
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import threading

class FTPServerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FTP Server")
        self.geometry("300x150")
        self.server = None
        self.server_thread = None
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self)
        frame.pack(pady=20)

        self.start_button = tk.Button(frame, text="Start Server", command=self.start_server)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(frame, text="Stop Server", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

    def start_server(self):
        if self.server is not None:
            messagebox.showwarning("Warning", "Server is already running!")
            return

        authorizer = DummyAuthorizer()
        ftp_directory = 'C:/Users/Burnt/Desktop'
        authorizer.add_user('user', 'pass', ftp_directory, perm='elradfmwMT')

        handler = FTPHandler
        handler.authorizer = authorizer

        self.server = FTPServer(('0.0.0.0', 2121), handler)

        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.start()

        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        messagebox.showinfo("Info", "FTP Server Started Successfully on port 2121")

    def stop_server(self):
        if self.server is None:
            messagebox.showwarning("Warning", "Server is not running!")
            return

        self.server.close_all()
        self.server_thread.join()
        self.server = None
        self.server_thread = None

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        messagebox.showinfo("Info", "FTP Server Stopped Successfully")

if __name__ == "__main__":
    app = FTPServerApp()
    app.mainloop()