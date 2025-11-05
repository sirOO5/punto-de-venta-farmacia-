import tkinter as tk
import customtkinter
from tkinter import ttk
import json
from PIL import Image, ImageTk
import pandas as pd
import speech_recognition as sr
import pyttsx3
import threading
import os

"""
###############################################################################################
echo por: Dr. Siro (Boris Lopez De la Cruz)
github:
###############################################################################################
"""

class PharmacyManagementSystem:
    def __init__(self, data_file):
        self.medicines = {}
        self.data_file = data_file
        self.sales_file = "sales_data.json"
        self.load_data()
        self.sales = []
        self.load_sales_data()

    def add_medicine(self, generic_name, name, cost, quantity, med_type, brand, location=""):
        self.medicines[name] = {
            "generic_name": generic_name,
            "cost": cost,
            "quantity": quantity,
            "type": med_type,
            "brand": brand,
            "location": location
        }
        self.save_data()

    def delete_medicine(self, name):
        if name in self.medicines:
            del self.medicines[name]
            self.save_data()

    def edit_medicine(self, generic_name, name, cost, quantity, med_type, brand, location=""):
        if name in self.medicines:
            self.medicines[name] = {
                "generic_name": generic_name,
                "cost": cost,
                "quantity": quantity,
                "type": med_type,
                "brand": brand,
                "location": location
            }
            self.save_data()

    def get_inventory(self):
        inventory = "Inventory:\n"
        for name, info in self.medicines.items():
            inventory += f"Generic Name: {info['generic_name']}, Name: {name}, Cost: {info['cost']}, Quantity: {info['quantity']}, Type: {info['type']}, Brand: {info['brand']}\n"
        return inventory

    def load_data(self):
        try:
            with open(self.data_file, "r") as file:
                self.medicines = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.medicines = {}

    def save_data(self):
        with open(self.data_file, "w") as file:
            json.dump(self.medicines, file, indent=4)

    def load_sales_data(self):
        try:
            with open(self.sales_file, "r") as file:
                self.sales = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            self.sales = []

    def save_sales_data(self):
        with open(self.sales_file, "w") as file:
            json.dump(self.sales, file, indent=4)

    def record_sale(self, medicine_name, quantity_sold, price_per_unit):
        import datetime
        sale_record = {
            "medicine": medicine_name,
            "quantity": quantity_sold,
            "price_per_unit": price_per_unit,
            "total_price": quantity_sold * price_per_unit,
            "date": datetime.datetime.now().isoformat()
        }
        self.sales.append(sale_record)
        self.save_sales_data()
            
class PharmacyManagementSystemGUI:
    def __init__(self, root):
        self.root = root
        self.data_file = "pharmacy_data.json"
        self.pharmacy_system = PharmacyManagementSystem(self.data_file)

        # Load background image using PIL
        # Load background image using PIL and store it as an instance variable
        # self.pil_bg_image = Image.open("Background.png")
        # self.bg_image = customtkinter.CTkImage(self.pil_bg_image, size=(1200, 700))
        # self.bg_label = customtkinter.CTkLabel(self.root, image=self.bg_image, text="")
        # self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Configure grid layout (2x2)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0) # Notification frame row
        self.root.grid_columnconfigure(1, weight=1)

        # Inicializar motor de texto a voz
        self.tts_engine = pyttsx3.init()
        # Cargar base de datos del vademécum
        self.vademecum_data = []
        if os.path.exists("vademecum_data.json"):
            try:
                with open("vademecum_data.json", "r", encoding="utf-8") as f:
                    self.vademecum_data = json.load(f)
                print(f"Vademécum cargado con {len(self.vademecum_data)} medicamentos.")
            except json.JSONDecodeError:
                print("Error al cargar vademecum_data.json: JSON inválido.")
        else:
            print("Advertencia: vademecum_data.json no encontrado. La búsqueda por voz de detalles no funcionará.")

        self.create_main_frames()
        self.create_widgets()

    def create_main_frames(self):
        # Left frame for navigation buttons
        self.navigation_frame = customtkinter.CTkFrame(self.root, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = customtkinter.CTkLabel(self.navigation_frame, text="Menú",
                                                                compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Main content frame
        self.main_content_frame = customtkinter.CTkFrame(self.root, corner_radius=0)
        self.main_content_frame.grid(row=0, column=1, sticky="nsew")
        self.main_content_frame.grid_rowconfigure(0, weight=1)
        self.main_content_frame.grid_columnconfigure(0, weight=1)

        # Notification frame
        self.notification_frame = customtkinter.CTkFrame(self.root, corner_radius=0, fg_color="transparent", height=1)
        self.notification_frame.grid(row=1, column=1, columnspan=2, sticky="ew")
        self.notification_frame.grid_columnconfigure(0, weight=1)
        self.notification_label = None

        # AI Assistant frame (right side)
        self.ai_assistant_frame = customtkinter.CTkFrame(self.root, corner_radius=0, width=200)
        self.ai_assistant_frame.grid(row=0, column=2, sticky="nsew")
        self.ai_assistant_frame.grid_rowconfigure(0, weight=1)
        self.ai_assistant_frame.grid_columnconfigure(0, weight=1)

        self.ai_assistant_label = customtkinter.CTkLabel(self.ai_assistant_frame, text="Asistente IA",
                                                            compound="left", font=customtkinter.CTkFont(size=15, weight="bold"))
        self.ai_assistant_label.grid(row=0, column=0, padx=20, pady=20)

    def show_notification(self, message, color):
        if self.notification_label is not None:
            self.notification_label.destroy()

        self.notification_label = customtkinter.CTkLabel(self.notification_frame, text=message, text_color=color)
        self.notification_label.pack(pady=2, padx=10, fill="x")

    def create_widgets(self):
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Consolidated Inventory Management Button
        self.manage_inventory_button = customtkinter.CTkButton(self.navigation_frame, text="Gestionar Inventario",
                                                                command=self.show_manage_inventory_form)
        self.manage_inventory_button.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.sell_button = customtkinter.CTkButton(self.navigation_frame, text="Vender Medicamento",
                                                    command=self.show_sell_medicine_form)
        self.sell_button.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.display_button = customtkinter.CTkButton(self.navigation_frame, text="Mostrar Inventario",
                                                        command=self.display_inventory)
        self.display_button.grid(row=3, column=0, sticky="ew", padx=20, pady=10)

        self.manage_sales_button = customtkinter.CTkButton(self.navigation_frame, text="Gestionar Ventas",
                                                            command=self.show_manage_sales_form)
        self.manage_sales_button.grid(row=4, column=0, sticky="ew", padx=20, pady=10)

        self.voice_search_button = customtkinter.CTkButton(self.navigation_frame, text="Búsqueda por Voz",
                                                            command=lambda: threading.Thread(target=self._listen_and_process_voice).start())
        self.voice_search_button.grid(row=5, column=0, sticky="ew", padx=20, pady=10)

        self.quit_button = customtkinter.CTkButton(self.navigation_frame, text="Salir",
                                                    command=self.root.quit)
        self.quit_button.grid(row=6, column=0, sticky="ew", padx=20, pady=10)

    def show_manage_sales_form(self):
        self.clear_main_frame()

        manage_frame = customtkinter.CTkFrame(self.main_content_frame)
        manage_frame.pack(pady=20, padx=20, fill="both", expand=True)

        title_label = customtkinter.CTkLabel(manage_frame, text="Gestionar Ventas", font=customtkinter.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=10)

        tree_frame = customtkinter.CTkFrame(manage_frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        columns = ("Medicamento", "Cantidad", "Precio Unitario", "Precio Total", "Fecha")
        self.sales_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.sales_tree.heading("Medicamento", text="Medicamento")
        self.sales_tree.heading("Cantidad", text="Cantidad")
        self.sales_tree.heading("Precio Unitario", text="Precio Unitario")
        self.sales_tree.heading("Precio Total", text="Precio Total")
        self.sales_tree.heading("Fecha", text="Fecha")

        self.sales_tree.column("Medicamento", width=150, anchor="w")
        self.sales_tree.column("Cantidad", width=80, anchor="e")
        self.sales_tree.column("Precio Unitario", width=100, anchor="e")
        self.sales_tree.column("Precio Total", width=100, anchor="e")
        self.sales_tree.column("Fecha", width=150, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sales_tree.yview)
        self.sales_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sales_tree.pack(side="left", fill="both", expand=True)

        action_buttons_frame = customtkinter.CTkFrame(manage_frame)
        action_buttons_frame.pack(pady=10, padx=10, fill="x")

        export_sales_button = customtkinter.CTkButton(action_buttons_frame, text="Exportar Ventas a Excel", command=self.export_sales_to_excel)
        export_sales_button.pack(side="left", padx=5, expand=True)

        self._populate_sales_tree()

    def _populate_sales_tree(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)

        self.pharmacy_system.load_sales_data()
        for sale in self.pharmacy_system.sales:
            self.sales_tree.insert("", "end", values=(
                sale['medicine'],
                sale['quantity'],
                f"{sale['price_per_unit']:.2f}",
                f"{sale['total_price']:.2f}",
                sale['date']
            ))



    def clear_main_frame(self):
        for widget in self.main_content_frame.winfo_children():
            widget.destroy()

    def show_add_medicine_form(self):
        self.clear_main_frame()

        form_frame = customtkinter.CTkFrame(self.main_content_frame)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        title_label = customtkinter.CTkLabel(form_frame, text="Añadir Nuevo Medicamento", font=customtkinter.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Medicine Name
        name_label = customtkinter.CTkLabel(form_frame, text="Nombre del Medicamento:")
        name_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.name_entry = customtkinter.CTkEntry(form_frame)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Cost
        cost_label = customtkinter.CTkLabel(form_frame, text="Costo:")
        cost_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.cost_entry = customtkinter.CTkEntry(form_frame)
        self.cost_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        # Quantity
        quantity_label = customtkinter.CTkLabel(form_frame, text="Cantidad:")
        quantity_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.quantity_entry = customtkinter.CTkEntry(form_frame)
        self.quantity_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        # Type
        type_label = customtkinter.CTkLabel(form_frame, text="Tipo:")
        type_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.type_entry = customtkinter.CTkEntry(form_frame)
        self.type_entry.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        # Brand
        brand_label = customtkinter.CTkLabel(form_frame, text="Marca:")
        brand_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.brand_entry = customtkinter.CTkEntry(form_frame)
        self.brand_entry.grid(row=5, column=1, padx=10, pady=5, sticky="ew")

        # Add Button
        add_button = customtkinter.CTkButton(form_frame, text="Añadir Medicamento",
                                                command=lambda: self.add_medicine_to_file(
                                                    self.name_entry.get(),
                                                    self.cost_entry.get(),
                                                    self.quantity_entry.get(),
                                                    self.type_entry.get(),
                                                    self.brand_entry.get()
                                                ))
        add_button.grid(row=6, column=0, columnspan=2, pady=20)

        # Configure column weights for responsiveness
        form_frame.grid_columnconfigure(1, weight=1)

    def show_manage_inventory_form(self):
        self.clear_main_frame()

        # Main frame for inventory management
        manage_frame = customtkinter.CTkFrame(self.main_content_frame)
        manage_frame.pack(pady=20, padx=20, fill="both", expand=True)

        manage_frame.grid_rowconfigure(2, weight=1) # Allow treeview to expand
        manage_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = customtkinter.CTkLabel(manage_frame, text="Gestionar Inventario de Medicamentos", font=customtkinter.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, pady=10, sticky="ew")

        # Search Bar
        search_frame = customtkinter.CTkFrame(manage_frame)
        search_frame.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        self.manage_search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Buscar medicamento...")
        self.manage_search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.manage_search_entry.bind("<Return>", lambda event: self.search_manage_inventory())
        search_button = customtkinter.CTkButton(search_frame, text="Buscar", command=self.search_manage_inventory)
        search_button.pack(side="left", padx=5, pady=5)

        # Treeview for inventory display
        tree_frame = customtkinter.CTkFrame(manage_frame)
        tree_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("Medicamento", "Nombre", "Tipo", "Marca", "Costo", "Cantidad", "Ubicacion")
        self.manage_inventory_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.manage_inventory_tree.heading("Medicamento", text="Medicamento")
        self.manage_inventory_tree.heading("Nombre", text="Nombre")
        self.manage_inventory_tree.heading("Tipo", text="Tipo")
        self.manage_inventory_tree.heading("Marca", text="Marca")
        self.manage_inventory_tree.heading("Costo", text="Costo")
        self.manage_inventory_tree.heading("Cantidad", text="Cantidad")
        self.manage_inventory_tree.heading("Ubicacion", text="Ubicacion")

        self.manage_inventory_tree.column("Medicamento", width=150, anchor="w")
        self.manage_inventory_tree.column("Nombre", width=150, anchor="w")
        self.manage_inventory_tree.column("Tipo", width=100, anchor="w")
        self.manage_inventory_tree.column("Marca", width=100, anchor="w")
        self.manage_inventory_tree.column("Costo", width=80, anchor="e")
        self.manage_inventory_tree.column("Cantidad", width=80, anchor="e")
        self.manage_inventory_tree.column("Ubicacion", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.manage_inventory_tree.yview)
        self.manage_inventory_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.manage_inventory_tree.grid(row=0, column=0, sticky="nsew")

        # Bind selection event
        self.manage_inventory_tree.bind("<<TreeviewSelect>>", self.load_selected_medicine_to_form)

        # Input form for Add/Edit
        input_form_frame = customtkinter.CTkFrame(manage_frame)
        input_form_frame.grid(row=3, column=0, pady=10, padx=10, sticky="ew")

        # Generic Name
        generic_name_label = customtkinter.CTkLabel(input_form_frame, text="Medicamento:")
        generic_name_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.manage_generic_name_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_generic_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        # Commercial Name
        name_label = customtkinter.CTkLabel(input_form_frame, text="Nombre:")
        name_label.grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.manage_name_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_name_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        # Cost
        cost_label = customtkinter.CTkLabel(input_form_frame, text="Costo:")
        cost_label.grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.manage_cost_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_cost_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        # Quantity
        quantity_label = customtkinter.CTkLabel(input_form_frame, text="Cantidad:")
        quantity_label.grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.manage_quantity_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_quantity_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        # Type
        type_label = customtkinter.CTkLabel(input_form_frame, text="Tipo:")
        type_label.grid(row=0, column=2, padx=5, pady=2, sticky="w")
        self.manage_type_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_type_entry.grid(row=0, column=3, padx=5, pady=2, sticky="ew")

        # Brand
        brand_label = customtkinter.CTkLabel(input_form_frame, text="Marca:")
        brand_label.grid(row=1, column=2, padx=5, pady=2, sticky="w")
        self.manage_brand_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_brand_entry.grid(row=1, column=3, padx=5, pady=2, sticky="ew")

        # Location
        location_label = customtkinter.CTkLabel(input_form_frame, text="Ubicacion:")
        location_label.grid(row=2, column=2, padx=5, pady=2, sticky="w")
        self.manage_location_entry = customtkinter.CTkEntry(input_form_frame)
        self.manage_location_entry.grid(row=2, column=3, padx=5, pady=2, sticky="ew")

        input_form_frame.grid_columnconfigure(1, weight=1)
        input_form_frame.grid_columnconfigure(3, weight=1)

        # Action buttons
        action_buttons_frame = customtkinter.CTkFrame(manage_frame)
        action_buttons_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        add_new_button = customtkinter.CTkButton(action_buttons_frame, text="Añadir Nuevo", command=self.add_medicine_from_manage_form)
        add_new_button.pack(side="left", padx=5, expand=True)

        update_button = customtkinter.CTkButton(action_buttons_frame, text="Actualizar Seleccionado", command=self.update_medicine_from_manage_form)
        update_button.pack(side="left", padx=5, expand=True)

        delete_button = customtkinter.CTkButton(action_buttons_frame, text="Eliminar Seleccionado", command=self.delete_medicine_from_manage_form)
        delete_button.pack(side="left", padx=5, expand=True)

        export_inventory_button = customtkinter.CTkButton(action_buttons_frame, text="Exportar Inventario a Excel", command=self.export_inventory_to_excel)
        export_inventory_button.pack(side="left", padx=5, expand=True)

        import_inventory_button = customtkinter.CTkButton(action_buttons_frame, text="Importar Inventario desde Excel", command=self.import_inventory_from_excel)
        import_inventory_button.pack(side="left", padx=5, expand=True)

        # Populate the treeview
        self._populate_manage_inventory_tree()

    def _populate_manage_inventory_tree(self, data=None):
        for item in self.manage_inventory_tree.get_children():
            self.manage_inventory_tree.delete(item)

        if data is None:
            data = self.pharmacy_system.medicines

        for name, info in data.items():
            self.manage_inventory_tree.insert("", "end", values=(
                info.get('generic_name', '').capitalize(),
                name.capitalize(),
                info.get('type', ''),
                info.get('brand', ''),
                f"{info.get('cost', 0):.2f}",
                info.get('quantity', 0),
                info.get('location', '')
            ), iid=name) # Use name as iid for easy lookup

    def search_manage_inventory(self):
        search_term = self.manage_search_entry.get().lower()
        filtered_medicines = {}
        for name, info in self.pharmacy_system.medicines.items():
            if search_term in name.lower() or \
               search_term in info['generic_name'].lower() or \
               search_term in info['type'].lower() or \
               search_term in info['brand'].lower():
                filtered_medicines[name] = info
        self._populate_manage_inventory_tree(filtered_medicines)

    def load_selected_medicine_to_form(self, event):
        selected_item = self.manage_inventory_tree.focus()
        if selected_item:
            values = self.manage_inventory_tree.item(selected_item, "values")
            # Assuming order: Medicamento, Nombre, Tipo, Marca, Costo, Cantidad
            self.manage_generic_name_entry.delete(0, tk.END)
            self.manage_generic_name_entry.insert(0, values[0])
            self.manage_name_entry.delete(0, tk.END)
            self.manage_name_entry.insert(0, values[1])
            self.manage_type_entry.delete(0, tk.END)
            self.manage_type_entry.insert(0, values[2])
            self.manage_brand_entry.delete(0, tk.END)
            self.manage_brand_entry.insert(0, values[3])
            self.manage_cost_entry.delete(0, tk.END)
            self.manage_cost_entry.insert(0, values[4])
            self.manage_quantity_entry.delete(0, tk.END)
            self.manage_quantity_entry.insert(0, values[5])
            self.manage_location_entry.delete(0, tk.END)
            self.manage_location_entry.insert(0, values[6])

    def add_medicine_from_manage_form(self):
        generic_name = self.manage_generic_name_entry.get()
        name = self.manage_name_entry.get()
        cost_str = self.manage_cost_entry.get()
        quantity_str = self.manage_quantity_entry.get()
        med_type = self.manage_type_entry.get()
        brand = self.manage_brand_entry.get()
        location = self.manage_location_entry.get()

        try:
            cost = float(cost_str)
            quantity = int(quantity_str)

            if not generic_name or not name or not med_type or not brand:
                self.show_notification("Todos los campos (Medicamento, Nombre, Tipo, Marca) son obligatorios.", "red")
                return
            if cost <= 0 or quantity <= 0:
                self.show_notification("Costo y Cantidad deben ser números positivos.", "red")
                return

            self.pharmacy_system.add_medicine(generic_name, name, cost, quantity, med_type, brand, location)
            self._populate_manage_inventory_tree() # Refresh treeview
            self.clear_manage_form_entries() # Clear form
            self.show_notification(f"Medicamento '{name}' añadido/actualizado con éxito.", "green")
        except ValueError:
            self.show_notification("Error: Costo y Cantidad deben ser números válidos.", "red")
        except Exception as e:
            self.show_notification(f"Error al añadir medicamento: {e}", "red")

    def update_medicine_from_manage_form(self):
        selected_item_iid = self.manage_inventory_tree.focus() # Get the iid (original name)
        if not selected_item_iid:
            self.show_notification("Selecciona un medicamento para actualizar.", "orange")
            return

        original_name = selected_item_iid # Assuming iid is the original name
        generic_name = self.manage_generic_name_entry.get()
        new_name = self.manage_name_entry.get()
        cost_str = self.manage_cost_entry.get()
        quantity_str = self.manage_quantity_entry.get()
        med_type = self.manage_type_entry.get()
        brand = self.manage_brand_entry.get()
        location = self.manage_location_entry.get()

        try:
            cost = float(cost_str)
            quantity = int(quantity_str)

            if not generic_name or not new_name or not med_type or not brand:
                self.show_notification("Todos los campos (Medicamento, Nombre, Tipo, Marca) son obligatorios.", "red")
                return
            if cost <= 0 or quantity <= 0:
                self.show_notification("Costo y Cantidad deben ser números positivos.", "red")
                return

            # If name changed, delete old and add new
            if original_name != new_name:
                self.pharmacy_system.delete_medicine(original_name)

            self.pharmacy_system.add_medicine(generic_name, new_name, cost, quantity, med_type, brand, location) # add_medicine handles both add and update
            self._populate_manage_inventory_tree() # Refresh treeview
            self.clear_manage_form_entries() # Clear form
            self.show_notification(f"Medicamento '{new_name}' actualizado con éxito.", "green")
        except ValueError:
            self.show_notification("Error: Costo y Cantidad deben ser números válidos.", "red")
        except Exception as e:
            self.show_notification(f"Error al actualizar medicamento: {e}", "red")

    def delete_medicine_from_manage_form(self):
        selected_item_iid = self.manage_inventory_tree.focus()
        if not selected_item_iid:
            self.show_notification("Selecciona un medicamento para eliminar.", "orange")
            return

        name_to_delete = selected_item_iid # Assuming iid is the original name
        try:
            self.pharmacy_system.delete_medicine(name_to_delete)
            self._populate_manage_inventory_tree() # Refresh treeview
            self.clear_manage_form_entries() # Clear form
            self.show_notification(f"Medicamento '{name_to_delete}' eliminado con éxito.", "green")
        except Exception as e:
            self.show_notification(f"Error al eliminar medicamento: {e}", "red")

    def clear_manage_form_entries(self):
        self.manage_generic_name_entry.delete(0, tk.END)
        self.manage_name_entry.delete(0, tk.END)
        self.manage_cost_entry.delete(0, tk.END)
        self.manage_quantity_entry.delete(0, tk.END)
        self.manage_type_entry.delete(0, tk.END)
        self.manage_brand_entry.delete(0, tk.END)
        self.manage_location_entry.delete(0, tk.END)

    def show_sell_medicine_form(self):
        self.clear_main_frame()

        form_frame = customtkinter.CTkFrame(self.main_content_frame)
        form_frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title
        title_label = customtkinter.CTkLabel(form_frame, text="Vender Medicamento", font=customtkinter.CTkFont(size=18, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)

        # Search Bar
        search_frame = customtkinter.CTkFrame(form_frame)
        search_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")

        self.sell_search_entry = customtkinter.CTkEntry(search_frame, placeholder_text="Buscar medicamento...")
        self.sell_search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.sell_search_entry.bind("<Return>", lambda event: self.search_medicine_for_sell())
        search_button = customtkinter.CTkButton(search_frame, text="Buscar", command=self.search_medicine_for_sell)
        search_button.pack(side="left", padx=5, pady=5)

        # Treeview for inventory display
        tree_frame = customtkinter.CTkFrame(form_frame)
        tree_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")
        form_frame.grid_rowconfigure(2, weight=1)

        columns = ("Medicamento", "Nombre", "Tipo", "Marca", "Costo", "Cantidad", "Ubicacion")
        self.sell_inventory_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        self.sell_inventory_tree.heading("Medicamento", text="Medicamento")
        self.sell_inventory_tree.heading("Nombre", text="Nombre")
        self.sell_inventory_tree.heading("Tipo", text="Tipo")
        self.sell_inventory_tree.heading("Marca", text="Marca")
        self.sell_inventory_tree.heading("Costo", text="Costo")
        self.sell_inventory_tree.heading("Cantidad", text="Cantidad")
        self.sell_inventory_tree.heading("Ubicacion", text="Ubicacion")

        self.sell_inventory_tree.column("Medicamento", width=150, anchor="w")
        self.sell_inventory_tree.column("Nombre", width=150, anchor="w")
        self.sell_inventory_tree.column("Tipo", width=100, anchor="w")
        self.sell_inventory_tree.column("Marca", width=100, anchor="w")
        self.sell_inventory_tree.column("Costo", width=80, anchor="e")
        self.sell_inventory_tree.column("Cantidad", width=80, anchor="e")
        self.sell_inventory_tree.column("Ubicacion", width=100, anchor="w")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sell_inventory_tree.yview)
        self.sell_inventory_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.sell_inventory_tree.pack(side="left", fill="both", expand=True)

        self.sell_inventory_tree.bind("<<TreeviewSelect>>", self.load_selected_medicine_to_sell_form)

        # Medicine Name
        name_label = customtkinter.CTkLabel(form_frame, text="Nombre del Medicamento:")
        name_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.sell_name_entry = customtkinter.CTkEntry(form_frame)
        self.sell_name_entry.grid(row=3, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Quantity Sold
        quantity_label = customtkinter.CTkLabel(form_frame, text="Cantidad a Vender:")
        quantity_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.sell_quantity_entry = customtkinter.CTkEntry(form_frame)
        self.sell_quantity_entry.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky="ew")

        # Sell Button
        sell_button = customtkinter.CTkButton(form_frame, text="Vender",
                                                command=lambda: self.sell_medicine_from_inventory(
                                                    self.sell_name_entry.get(),
                                                    self.sell_quantity_entry.get()
                                                ))
        sell_button.grid(row=5, column=0, columnspan=3, pady=20)

        # Configure column weights for responsiveness
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_columnconfigure(2, weight=1)

        self._populate_sell_medicine_tree()

    def _populate_sell_medicine_tree(self):
        for item in self.sell_inventory_tree.get_children():
            self.sell_inventory_tree.delete(item)

        for name, info in self.pharmacy_system.medicines.items():
            self.sell_inventory_tree.insert("", "end", values=(
                info.get('generic_name', '').capitalize(),
                name.capitalize(),
                info.get('type', ''),
                info.get('brand', ''),
                f"{info.get('cost', 0):.2f}",
                info.get('quantity', 0),
                info.get('location', '')
            ), iid=name)

    def search_medicine_for_sell(self):
        search_term = self.sell_search_entry.get().lower()
        found_medicine = None
        for name, info in self.pharmacy_system.medicines.items():
            if search_term in name.lower() or search_term in info['generic_name'].lower():
                found_medicine = name
                break
        
        if found_medicine:
            self.sell_inventory_tree.selection_set(found_medicine)
            self.sell_inventory_tree.focus(found_medicine)
            self.sell_name_entry.delete(0, tk.END)
            self.sell_name_entry.insert(0, found_medicine.capitalize())
        else:
            self.show_notification("Medicamento no encontrado.", "red")

    def load_selected_medicine_to_sell_form(self, event):
        selected_item = self.sell_inventory_tree.focus()
        if selected_item:
            values = self.sell_inventory_tree.item(selected_item, "values")
            self.sell_name_entry.delete(0, tk.END)
            self.sell_name_entry.insert(0, values[1])

    def sell_medicine_from_inventory(self, name, quantity_str):
        try:
            quantity_sold = int(quantity_str)
            if quantity_sold <= 0:
                self.show_notification("La cantidad debe ser un número positivo.", "red")
                return

            name = name.upper() # Convertir a mayúsculas para que coincida con el inventario

            if name in self.pharmacy_system.medicines:
                if self.pharmacy_system.medicines[name]["quantity"] >= quantity_sold:
                    # Update quantity
                    self.pharmacy_system.medicines[name]["quantity"] -= quantity_sold
                    
                    # Record sale
                    price_per_unit = self.pharmacy_system.medicines[name]["cost"]
                    self.pharmacy_system.record_sale(name, quantity_sold, price_per_unit)

                    # Save data
                    self.pharmacy_system.save_data()

                    # Refresh treeview
                    self._populate_sell_medicine_tree()

                    self.show_notification(f"Venta de {quantity_sold} de '{name.capitalize()}' registrada con éxito.", "green")
                else:
                    self.show_notification(f"No hay suficiente stock de '{name.capitalize()}'.", "red")
            else:
                self.show_notification(f"Medicamento '{name.capitalize()}' no encontrado.", "red")

        except ValueError:
            self.show_notification("Error: La cantidad debe ser un número entero válido.", "red")
        except Exception as e:
            self.show_notification(f"Error al vender medicamento: {e}", "red")


    def export_sales_to_excel(self):
        try:
            self.pharmacy_system.load_sales_data() # Ensure latest sales data is loaded
            if not self.pharmacy_system.sales:
                self.show_notification("No hay datos de ventas para exportar.", "orange")
                return

            df = pd.DataFrame(self.pharmacy_system.sales)
            output_file = "sales_history.xlsx"
            df.to_excel(output_file, index=False)
            self.show_notification(f"Historial de ventas exportado a {output_file}", "green")
        except Exception as e:
            self.show_notification(f"Error al exportar historial de ventas: {e}", "red")

    def display_inventory(self):
        self.clear_main_frame()

        # Title
        title_label = customtkinter.CTkLabel(self.main_content_frame, text="Inventario de Medicamentos", font=customtkinter.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=10)

        # Search and Sort frame
        search_sort_frame = customtkinter.CTkFrame(self.main_content_frame)
        search_sort_frame.pack(pady=5, padx=10, fill="x")

        self.search_entry = customtkinter.CTkEntry(search_sort_frame, placeholder_text="Buscar medicamento...")
        self.search_entry.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        self.search_entry.bind("<Return>", lambda event: self.search_inventory())
        search_button = customtkinter.CTkButton(search_sort_frame, text="Buscar", command=self.search_inventory)
        search_button.pack(side="left", padx=5, pady=5)

        alpha_sort_button = customtkinter.CTkButton(search_sort_frame, text="Ordenar Alfabéticamente", command=self.sort_alphabetically)
        alpha_sort_button.pack(side="left", padx=5, pady=5)

        last_added_sort_button = customtkinter.CTkButton(search_sort_frame, text="Ordenar por Último Añadido", command=self.sort_by_last_added)
        last_added_sort_button.pack(side="left", padx=5, pady=5)

        # Treeview for inventory display
        tree_frame = customtkinter.CTkFrame(self.main_content_frame)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Define columns
        columns = ("Medicamento", "Nombre", "Tipo", "Marca", "Costo", "Cantidad", "Ubicacion")
        self.inventory_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        # Configure column headings
        self.inventory_tree.heading("Medicamento", text="Medicamento")
        self.inventory_tree.heading("Nombre", text="Nombre")
        self.inventory_tree.heading("Tipo", text="Tipo")
        self.inventory_tree.heading("Marca", text="Marca")
        self.inventory_tree.heading("Costo", text="Costo")
        self.inventory_tree.heading("Cantidad", text="Cantidad")
        self.inventory_tree.heading("Ubicacion", text="Ubicacion")

        # Configure column widths
        self.inventory_tree.column("Medicamento", width=150, anchor="w")
        self.inventory_tree.column("Nombre", width=150, anchor="w")
        self.inventory_tree.column("Tipo", width=100, anchor="w")
        self.inventory_tree.column("Marca", width=100, anchor="w")
        self.inventory_tree.column("Costo", width=80, anchor="e") # 'e' for east (right) alignment
        self.inventory_tree.column("Cantidad", width=80, anchor="e")
        self.inventory_tree.column("Ubicacion", width=100, anchor="w")

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.inventory_tree.yview)
        self.inventory_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.inventory_tree.pack(side="left", fill="both", expand=True)

        self.display_inventory_with_data(self.pharmacy_system.medicines)

    def display_inventory_with_data(self, data):
        # Clear existing items in the treeview
        for item in self.inventory_tree.get_children():
            self.inventory_tree.delete(item)

        if not data:
            # Display a message if no data, perhaps in a separate label or the treeview itself
            # For now, just return, as the treeview will be empty
            return

        for name, info in data.items():
            self.inventory_tree.insert("", "end", values=(
                info.get('generic_name', '').capitalize(),
                name.capitalize(),
                info.get('type', ''),
                info.get('brand', ''),
                f"{info.get('cost', 0):.2f}", # Format cost to 2 decimal places
                info.get('quantity', 0),
                info.get('location', '')
            ))

    def search_inventory(self):
        search_text = self.search_entry.get().lower()
        filtered_medicines = {}
        for name, info in self.pharmacy_system.medicines.items():
            if search_text in name.lower() or \
               search_text in info['type'].lower() or \
               search_text in info['brand'].lower():
                filtered_medicines[name] = info
        self.display_inventory_with_data(filtered_medicines)

    def sort_alphabetically(self):
        sorted_medicines = dict(sorted(self.pharmacy_system.medicines.items(), key=lambda item: item[0].lower()))
        self.display_inventory_with_data(sorted_medicines)

    def sort_by_last_added(self):
        # For a simple JSON file, 'last added' is effectively the original order of keys
        # if the file is not re-written in a sorted manner. We'll just display current order.
        self.display_inventory_with_data(self.pharmacy_system.medicines)

    def export_inventory_to_excel(self):
        try:
            self.pharmacy_system.load_data() # Ensure latest inventory data is loaded
            if not self.pharmacy_system.medicines:
                self.show_notification("No hay datos de inventario para exportar.", "orange")
                return

            # Convert dictionary of medicines to a list of dictionaries for DataFrame
            inventory_list = []
            for name, info in self.pharmacy_system.medicines.items():
                item = {
                    "Medicamento": info.get('generic_name', ''),
                    "Nombre": name,
                    "Costo": info.get("cost", 0),
                    "Cantidad": info.get("quantity", 0),
                    "Tipo": info.get("type", ''),
                    "Marca": info.get("brand", ''),
                    "Ubicacion": info.get("location", '')
                }
                inventory_list.append(item)

            df = pd.DataFrame(inventory_list)
            output_file = "inventory.xlsx"
            df.to_excel(output_file, index=False)
            self.show_notification(f"Inventario exportado a {output_file}", "green")
        except Exception as e:
            self.show_notification(f"Error al exportar inventario: {e}", "red")

    def import_inventory_from_excel(self):
        file_path = tk.filedialog.askopenfilename(
            title="Seleccionar archivo Excel de inventario",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if not file_path:
            return

        try:
            df = pd.read_excel(file_path)
            imported_count = 0
            for index, row in df.iterrows():
                try:
                    generic_name = str(row["Medicamento"]).strip()
                    name = str(row["Nombre"]).strip()
                    cost = float(row["Costo"])
                    quantity = int(row["Cantidad"])
                    med_type = str(row["Tipo"]).strip()
                    brand = str(row["Marca"]).strip()
                    location = str(row.get("Ubicacion", '')).strip()

                    if generic_name and name and cost > 0 and quantity > 0 and med_type and brand:
                        self.pharmacy_system.add_medicine(generic_name, name, cost, quantity, med_type, brand, location)
                        imported_count += 1
                    else:
                        print(f"Advertencia: Fila {index + 2} contiene datos inválidos y fue omitida: {row.to_dict()}")
                except KeyError as ke:
                    print(f"Error: Columna faltante en el archivo Excel: {ke}. Asegúrese de que las columnas 'Medicamento', 'Nombre', 'Costo', 'Cantidad', 'Tipo', 'Marca' existan.")
                    self.show_notification(f"Error: Columna faltante en el archivo Excel: {ke}.", "red")
                    return
                except ValueError as ve:
                    print(f"Advertencia: Error de valor en la fila {index + 2}: {ve}. Fila omitida: {row.to_dict()}")

            self.pharmacy_system.save_data()
            self.show_notification(f"Se importaron {imported_count} medicamentos del archivo Excel.", "green")
            self._populate_manage_inventory_tree()
        except Exception as e:
            self.show_notification(f"Error al importar inventario desde Excel: {e}", "red")

    def _listen_and_process_voice(self):
        self.show_notification("Escuchando... por favor, hable.", "blue")
        self.tts_engine.say("Escuchando. Por favor, hable.")
        self.tts_engine.runAndWait()

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = recognizer.recognize_google(audio, language="es-ES").lower()
                self.show_notification(f"Comando reconocido: {command}", "blue")
                self._search_vademecum_by_voice_command(command)
            except sr.WaitTimeoutError:
                self.show_notification("No se detectó voz.", "orange")
                self.tts_engine.say("No se detectó voz.")
                self.tts_engine.runAndWait()
            except sr.UnknownValueError:
                self.show_notification("No se pudo entender el audio.", "red")
                self.tts_engine.say("No se pudo entender el audio.")
                self.tts_engine.runAndWait()
            except sr.RequestError as e:
                self.show_notification(f"Error de servicio de voz; {e}", "red")
                self.tts_engine.say(f"Error en el servicio de voz: {e}")
                self.tts_engine.runAndWait()

    def _search_vademecum_by_voice_command(self, command_text):
        if not self.vademecum_data:
            self.show_notification("Base de datos del vademécum no cargada o vacía.", "red")
            self.tts_engine.say("Base de datos del vademécum no cargada o vacía.")
            self.tts_engine.runAndWait()
            return

        found_medicine = None
        for medicine_info in self.vademecum_data:
            generic_name = medicine_info.get("nombre_generico", "").lower()
            # Check if the generic name is directly in the command
            if generic_name in command_text:
                found_medicine = medicine_info
                break
            # Also check if command contains any part of the generic name (more flexible search)
            if any(word in command_text for word in generic_name.split()):
                found_medicine = medicine_info
                break
            # Commercial names are not in this CSV, so this part is commented out
            # for commercial_name in medicine_info.get("nombres_comerciales", []):
            #     if commercial_name.lower() in command_text:
            #         found_medicine = medicine_info
            #         break
            if found_medicine:
                break

        if found_medicine:
            response_text = f"Medicamento {found_medicine['nombre_generico']}. "
            if found_medicine['dosis'] != "No especificado":
                response_text += f"Dosis: {found_medicine['dosis']}. "
            if found_medicine['indicaciones'] != "No especificadas":
                response_text += f"Indicaciones: {found_medicine['indicaciones']}."
            
            self.show_notification(response_text, "green")
            self.tts_engine.say(response_text)
            self.tts_engine.runAndWait()
        else:
            self.show_notification(f"No se encontró información para '{command_text}'.", "orange")
            self.tts_engine.say(f"No se encontró información para {command_text}.")
            self.tts_engine.runAndWait()

def main():
    customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "dark-blue", "green"

    root = customtkinter.CTk()
    root.geometry("1200x700")  # Set the width and height to your preferred values
    root.title("Sistema de Gestión de Farmacia")

    app = PharmacyManagementSystemGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()



"""
###############################################################################################
echo por: Dr. Siro (Boris Lopez De la Cruz)
github:
###############################################################################################
"""
