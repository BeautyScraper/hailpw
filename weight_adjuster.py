import os
import sys
import random
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class WeightedFileSelector:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.dir_weights = {}
        self.file_weights = {}
        self.scan_directories()

    def scan_directories(self):
        """Scan root directory for dirs and files"""
        self.dirs = [
            d for d in os.listdir(self.root_dir)
            if os.path.isdir(os.path.join(self.root_dir, d))
        ]
        self.files = {}
        for d in self.dirs:
            dir_path = os.path.join(self.root_dir, d)
            self.files[d] = [
                f for f in os.listdir(dir_path)
                if os.path.isfile(os.path.join(dir_path, f))
            ]

    def set_dir_weight(self, directory, weight):
        self.dir_weights[directory] = float(weight)

    def set_file_weight(self, directory, file, weight):
        self.file_weights[(directory, file)] = float(weight)

    def get_random_file(self):
        """Pick a random file based on weights"""
        if not self.dirs:
            return None

        dirs = self.dirs
        dir_weights = [self.dir_weights.get(d, 1.0) for d in dirs]
        chosen_dir = random.choices(dirs, weights=dir_weights, k=1)[0]

        files = self.files[chosen_dir]
        if not files:
            return None
        file_weights = [
            self.file_weights.get((chosen_dir, f), 1.0)
            for f in files
        ]
        chosen_file = random.choices(files, weights=file_weights, k=1)[0]
        return os.path.join(self.root_dir, chosen_dir, chosen_file)


class WeightedFileSelectorGUI:
    def __init__(self, root, root_dir=None):
        self.root = root
        self.root.title("Weighted File Selector")

        self.selector = None

        self.frame = ttk.Frame(root, padding=10)
        self.frame.grid(sticky="nsew")

        # Directory label
        self.root_dir_label = ttk.Label(self.frame, text="No directory selected")
        self.root_dir_label.grid(row=0, column=0, columnspan=2, sticky="w")

        # Treeview for dirs/files
        self.tree = ttk.Treeview(self.frame, columns=("Weight"), show="tree headings")
        self.tree.heading("#0", text="Directory / File")
        self.tree.heading("Weight", text="Weight")
        self.tree.column("Weight", width=100, anchor="center")
        self.tree.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Weight entry
        self.weight_entry = ttk.Entry(self.frame)
        self.weight_entry.grid(row=2, column=0, sticky="ew")
        ttk.Button(self.frame, text="Set Weight", command=self.set_weight).grid(row=2, column=1, sticky="ew")

        # Random select button
        ttk.Button(self.frame, text="Pick Random File", command=self.pick_file).grid(row=3, column=0, columnspan=2, sticky="ew")

        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

        # If directory is given from CLI → load directly
        if root_dir:
            self.load_directory(root_dir)
        else:
            self.ask_directory()

    def ask_directory(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.load_directory(dir_path)

    def load_directory(self, dir_path):
        self.root_dir_label.config(text=dir_path)
        self.selector = WeightedFileSelector(dir_path)

        # Populate tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        for d in self.selector.dirs:
            dir_id = self.tree.insert("", "end", text=d, values=(self.selector.dir_weights.get(d, 1.0),))
            for f in self.selector.files[d]:
                self.tree.insert(dir_id, "end", text=f, values=(self.selector.file_weights.get((d, f), 1.0),))

    def set_weight(self):
        selected = self.tree.selection()
        if not selected or not self.selector:
            return
        new_weight = self.weight_entry.get()
        try:
            new_weight = float(new_weight)
        except ValueError:
            messagebox.showerror("Error", "Weight must be a number")
            return
        for sel in selected:
            parent = self.tree.parent(sel)
            name = self.tree.item(sel, "text")
            if parent:  # it's a file
                dir_name = self.tree.item(parent, "text")
                self.selector.set_file_weight(dir_name, name, new_weight)
            else:  # it's a directory
                self.selector.set_dir_weight(name, new_weight)
            self.tree.set(sel, "Weight", new_weight)

    def pick_file(self):
        if not self.selector:
            return
        result = self.selector.get_random_file()
        if result:
            messagebox.showinfo("Random File", f"Selected:\n{result}")
        else:
            messagebox.showwarning("Warning", "No files available")


if __name__ == "__main__":
    root_dir = r"C:\Work\OneDrive - Creative Arts Education Society\Desktop\rarely\G1\to_video\wan"
    root = tk.Tk()
    app = WeightedFileSelectorGUI(root, root_dir)
    root.mainloop()
