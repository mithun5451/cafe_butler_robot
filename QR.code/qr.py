import tkinter as tk
from tkinter import ttk
from tkinter import font as tkFont
from PIL import Image, ImageTk
from flask import Flask, request, jsonify
import threading
import requests
import json
import subprocess
import sys

# Sample food menu data
food_menu = {
    "Pizza": 10,
    "Burger": 7,
    "Pasta": 8,
    "Salad": 5
}

# Table data
tables = {
    1: {"status": "Available"},
    2: {"status": "Available"},
    3: {"status": "Available"}
}

# Flask server setup within Tkinter
class HotelManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hotel Management System")
        self.geometry("700x500")
        self.configure(bg="#1d1d1d")

        # Custom Styles
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TButton", font=("Helvetica", 12), padding=10, background="#444444", foreground="white", borderwidth=0)
        style.configure("TLabel", background="#1d1d1d", foreground="white", font=("Helvetica", 12))
        style.map("TButton", background=[("active", "#555555")], relief=[("pressed", "flat")])

        # Create Frames for different sections
        self.main_frame = tk.Frame(self, bg="#1d1d1d")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.order_frame = tk.Frame(self, bg="#1d1d1d")
        self.summary_frame = tk.Frame(self, bg="#1d1d1d")
        self.payment_frame = tk.Frame(self, bg="#1d1d1d")

        # Display table selection screen
        self.show_table_selection()

        # Flask server setup
        self.orders = []
        self.app = Flask(__name__)
        self.setup_flask_routes()

        # Start Flask server in a separate thread
        self.flask_thread = threading.Thread(target=self.run_flask_server, daemon=True)
        self.flask_thread.start()

    def setup_flask_routes(self):
        @self.app.route('/order', methods=['POST'])
        def receive_order():
            order_data = request.get_json()
            self.orders.append(order_data)
            print(f"Received order from Table {order_data['table_number']}:\n{order_data['order_summary']}")
            return jsonify({"status": "success"}), 200

        @self.app.route('/orders', methods=['GET'])
        def get_orders():
            return jsonify(self.orders), 200

        @self.app.route('/notify', methods=['POST'])
        def notify_chef():
            # Optionally, you can add some logic to notify the chef app, like sending a message or pushing a notification
            return jsonify({"status": "notified"}), 200

    def run_flask_server(self):
        self.app.run(host='0.0.0.0', port=5000, debug=False)

    def show_table_selection(self):
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.order_frame.pack_forget()
        self.summary_frame.pack_forget()
        self.payment_frame.pack_forget()

        # Title Label
        title_font = tkFont.Font(family="Helvetica", size=20, weight="bold")
        self.label = ttk.Label(self.main_frame, text="Select Your Table", font=title_font, style="TLabel")
        self.label.pack(pady=20)
        
        # Table selection UI
        self.table_buttons = []
        for table_number in tables.keys():
            button = ttk.Button(
                self.main_frame, 
                text=f"Table {table_number}", 
                style="TButton",
                command=lambda t=table_number: self.show_food_menu(t)
            )
            button.pack(pady=10, fill=tk.X, padx=20)
            self.table_buttons.append(button)

    def show_food_menu(self, table_number):
        self.main_frame.pack_forget()
        self.order_frame.pack(fill=tk.BOTH, expand=True)

        order_label = ttk.Label(self.order_frame, text=f"Table {table_number} - Order Food", style="TLabel")
        order_label.pack(pady=10)

        self.food_quantities = {}
        for food, price in food_menu.items():
            frame = tk.Frame(self.order_frame, bg="#1d1d1d")
            frame.pack(pady=5, padx=20, anchor="w")
            
            label = ttk.Label(frame, text=f"{food} - ${price}", style="TLabel")
            label.pack(side=tk.LEFT)
            
            quantity_var = tk.IntVar(value=0)
            self.food_quantities[food] = quantity_var

            # Add quantity adjustment buttons
            minus_button = ttk.Button(frame, text="-", command=lambda f=food: self.adjust_quantity(f, -1), width=2)
            minus_button.pack(side=tk.LEFT, padx=5)
            
            quantity_label = ttk.Label(frame, textvariable=quantity_var, width=3, style="TLabel")
            quantity_label.pack(side=tk.LEFT)

            plus_button = ttk.Button(frame, text="+", command=lambda f=food: self.adjust_quantity(f, 1), width=2)
            plus_button.pack(side=tk.LEFT, padx=5)
        
        order_button = ttk.Button(
            self.order_frame, 
            text="Place Order", 
            style="TButton",
            command=lambda: self.send_order_to_server(table_number)
        )
        order_button.pack(pady=20)
    
    def adjust_quantity(self, food, delta):
        current_quantity = self.food_quantities[food].get()
        new_quantity = max(0, current_quantity + delta)  # Ensure quantity doesn't go below 0
        self.food_quantities[food].set(new_quantity)

    def send_order_to_server(self, table_number):
        order_summary = ""
        total_cost = 0
        order_details = {
            "table_number": table_number,
            "order_summary": ""
        }

        for food, quantity_var in self.food_quantities.items():
            quantity = quantity_var.get()
            if quantity > 0:
                cost = food_menu[food] * quantity
                total_cost += cost
                order_summary += f"{food} x {quantity} = ${cost}\n"
        
        order_summary += f"Total Cost: ${total_cost}"
        order_details["order_summary"] = order_summary
        
        # Send order details to the Flask server
        try:
            response = requests.post("http://localhost:5000/order", json=order_details)
            if response.status_code == 200:
                self.show_order_summary(table_number)
                # Notify the chef and open the ChefApp
                self.notify_chef(order_details)
            else:
                print(f"Failed to send order. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error sending order: {e}")

    def notify_chef(self, order_details):
        # Optionally, you can add some logic to notify the chef app, like sending a message or pushing a notification
        try:
            # Open the ChefApp with the order details
            subprocess.Popen([sys.executable, '/home/mithun/Desktop/QR.code/mithun/chef.py', json.dumps(order_details)])
        except Exception as e:
            print(f"Error opening chef app: {e}")

    def show_order_summary(self, table_number):
        self.order_frame.pack_forget()
        self.summary_frame.pack(fill=tk.BOTH, expand=True)
        
        order_summary = ""
        total_cost = 0
        
        for food, quantity_var in self.food_quantities.items():
            quantity = quantity_var.get()
            if quantity > 0:
                cost = food_menu[food] * quantity
                total_cost += cost
                order_summary += f"{food} x {quantity} = ${cost}\n"
        
        order_summary += f"Total Cost: ${total_cost}"
        
        summary_label = ttk.Label(self.summary_frame, text=order_summary, style="TLabel")
        summary_label.pack(pady=20)
        
        payment_button = ttk.Button(
            self.summary_frame, 
            text="Pay Now", 
            style="TButton",
            command=self.show_upi_qr_code
        )
        payment_button.pack(pady=20)
    
    def show_upi_qr_code(self):
        self.summary_frame.pack_forget()
        self.payment_frame.pack(fill=tk.BOTH, expand=True)
        
        qr_label = ttk.Label(self.payment_frame, text="Scan the QR code below to pay with UPI:", style="TLabel")
        qr_label.pack(pady=10)
        
        # Load the provided UPI QR code image
        upi_qr_image = Image.open("/home/mithun/Desktop/QR.code/mithun/upi.jpeg")
        upi_qr_image = upi_qr_image.resize((200, 200), Image.LANCZOS)  # Use LANCZOS for resizing
        upi_qr_image_tk = ImageTk.PhotoImage(upi_qr_image)
        
        label = tk.Label(self.payment_frame, image=upi_qr_image_tk, bg="#1d1d1d")
        label.image = upi_qr_image_tk  # Keep a reference to avoid garbage collection
        label.pack(pady=10)

# Run the app
if __name__ == "__main__":
    app = HotelManagementApp()
    app.mainloop()
