import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ftplib import FTP, error_perm
import os

class FTPClientApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FTP Client")
        self.geometry("800x600")

        # Variables de conexión
        self.ftp = None
        self.current_path = "/"
        self.previous_path = "/"

        # Crear widgets
        self.create_widgets()

    def create_widgets(self):
        # Frame para los botones de conexión y operaciones
        frame = ttk.Frame(self)
        frame.pack(fill=tk.X, padx=10, pady=10)

        # Entradas para conexión
        self.host_entry = ttk.Entry(frame, width=15)
        self.host_entry.insert(0, "localhost")  # Cambia esto a tu IP
        self.host_entry.grid(row=0, column=0, padx=5)

        self.port_entry = ttk.Entry(frame, width=5)
        self.port_entry.insert(0, "21")  # Puerto FTP por defecto
        self.port_entry.grid(row=0, column=1, padx=5)

        self.user_entry = ttk.Entry(frame, width=15)
        self.user_entry.insert(0, "user")  # Cambia esto a tu usuario
        self.user_entry.grid(row=0, column=2, padx=5)

        self.pass_entry = ttk.Entry(frame, width=15, show="*")
        self.pass_entry.insert(0, "pass")  # Cambia esto a tu contraseña
        self.pass_entry.grid(row=0, column=3, padx=5)

        connect_button = ttk.Button(frame, text="Connect", command=self.connect)
        connect_button.grid(row=0, column=4, padx=5)

        # Botones de operaciones
        upload_button = ttk.Button(frame, text="Upload File", command=self.upload_file)
        upload_button.grid(row=0, column=5, padx=5)

        download_button = ttk.Button(frame, text="Download File", command=self.download_file)
        download_button.grid(row=0, column=6, padx=5)

        # Treeview para mostrar carpetas
        self.tree = ttk.Treeview(self, columns=("name"), show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self.on_item_double_click)

    def connect(self):
        host = self.host_entry.get()
        port = int(self.port_entry.get())
        user = self.user_entry.get()
        password = self.pass_entry.get()

        try:
            self.ftp = FTP()
            self.ftp.connect(host=host, port=port)
            self.ftp.login(user=user, passwd=password)
            self.load_directory("/")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def load_directory(self, path):
        if not self.ftp:
            messagebox.showerror("Connection Error", "Not connected to FTP server.")
            return

        self.tree.delete(*self.tree.get_children())

        # Añadir opción para ir a la carpeta superior
        if path != "/":
            parent_path = self.get_parent_path(path)
            self.tree.insert("", "end", iid="..", text="..", open=False, tags=("parent",))

        def add_items(parent, path):
            try:
                self.ftp.cwd(path)
                items = self.ftp.nlst()
                for item in items:
                    full_path = f"{path}/{item}" if path != "/" else f"/{item}"
                    if self.is_directory(full_path):
                        self.tree.insert(parent, "end", iid=full_path, text=item, open=False)
                    else:
                        self.tree.insert(parent, "end", iid=full_path, text=item, open=False, tags=("file",))
            except Exception as e:
                print(f"Failed to load directory {path}: {e}")

        add_items("", path)
        self.current_path = path

    def get_parent_path(self, path):
        if path == "/":
            return "/"
        else:
            return '/'.join(path.rstrip('/').split('/')[:-1]) or "/"

    def is_directory(self, path):
        try:
            self.ftp.cwd(path)
            self.ftp.cwd("..")
            return True
        except:
            return False

    def on_item_double_click(self, event):
        selected_items = self.tree.selection()
        if selected_items:
            selected_item = selected_items[0]
            if selected_item == "..":
                parent_path = self.get_parent_path(self.current_path)
                self.load_directory(parent_path)
            else:
                if self.tree.item(selected_item, "tags") == ("file",):
                    return  # Do not navigate if it's a file
                self.previous_path = self.current_path
                self.load_directory(selected_item)

    def upload_file(self):
        if not self.ftp:
            messagebox.showerror("Connection Error", "Not connected to FTP server.")
            return

        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        file_name = os.path.basename(file_path)
        upload_path = self.current_path + "/" + file_name

        try:
            with open(file_path, "rb") as file:
                self.ftp.storbinary(f"STOR {upload_path}", file)
            messagebox.showinfo("Success", "File uploaded successfully!")
        except Exception as e:
            messagebox.showerror("Upload Error", f"Failed to upload file: {e}")

    def download_file(self):
        if not self.ftp:
            messagebox.showerror("Connection Error", "Not connected to FTP server.")
            return

        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Selection Error", "No file selected.")
            return

        selected_item = selected_items[0]
        file_name = self.tree.item(selected_item, "text")
        local_path = filedialog.asksaveasfilename(initialfile=file_name)
        if not local_path:
            return

        try:
            with open(local_path, "wb") as file:
                self.ftp.retrbinary(f"RETR {selected_item}", file.write)
            messagebox.showinfo("Success", "File downloaded successfully!")
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download file: {e}")

    def close(self):
        if self.ftp:
            self.ftp.quit()

if __name__ == "__main__":
    app = FTPClientApp()
    app.protocol("WM_DELETE_WINDOW", app.close)
    app.mainloop()