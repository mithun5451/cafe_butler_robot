import tkinter as tk
from tkinter import ttk
import requests
import json
import sys

class ChefApp(tk.Tk):
    def __init__(self, order=None):
        super().__init__()
        self.title("Chef Orders")
        self.geometry("600x400")
        self.configure(bg="#f0f0f0")

        self.create_widgets()
        if order:
            self.display_order(order)

    def create_widgets(self):
        self.title_label = tk.Label(self, text="Order for the Chef", font=("Helvetica", 16))
        self.title_label.pack(pady=10)

        self.order_text = tk.Text(self, width=80, height=20, bg="#ffffff")
        self.order_text.pack(pady=10)

    def display_order(self, order):
        self.order_text.insert(tk.END, f"Table {order['table_number']}:\n{order['order_summary']}\n")

if __name__ == "__main__":
    # Parse command-line arguments
    if len(sys.argv) > 1:
        order = json.loads(sys.argv[1])
    else:
        order = None

    app = ChefApp(order)
    app.mainloop()
