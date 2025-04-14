import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from db_config import DatabaseManager

class ContactManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Contact Manager")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Apply a modern style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Define custom colors
        primary_bg = "#f4f4f4"
        accent_color = "#1E90FF"
        button_bg = "#1E90FF"
        button_fg = "#ffffff"

        # Configure general window background
        self.root.configure(bg=primary_bg)

        # Apply style for ttk widgets
        self.style.configure("TFrame", background=primary_bg)
        self.style.configure("TLabel", background=primary_bg, font=("Segoe UI", 10))
        self.style.configure("TButton",
                             font=("Segoe UI", 10),
                             padding=6,
                             background=button_bg,
                             foreground=button_fg)
        self.style.map("TButton",
                       background=[("active", "#0f78d1")],
                       foreground=[("active", "#ffffff")])

        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background=accent_color, foreground="white")
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)

        # Initialize database
        try:
            self.db = DatabaseManager()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to database:\n{str(e)}")
            root.destroy()
            return

        self.current_contact_id = None

        self._create_menu()
        self._create_search_bar()
        self._create_contact_form()
        self._create_contact_list()

        self.load_contacts()

    def _create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New Contact", command=self.new_contact)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    def _create_search_bar(self):
        search_frame = ttk.Frame(self.root, padding="10 5 10 5")
        search_frame.pack(fill=tk.X)

        ttk.Label(search_frame, text="🔍 Search:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(search_frame, text="Search", command=self.search_contacts).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT)

    def _create_contact_form(self):
        form_frame = ttk.LabelFrame(self.root, text="Contact Details", padding=10)
        form_frame.pack(padx=10, pady=5, fill=tk.X)

        grid = ttk.Frame(form_frame)
        grid.pack()

        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()

        fields = [
            ("Name:", self.name_var),
            ("Email:", self.email_var),
            ("Phone:", self.phone_var),
            ("Address:", self.address_var),
        ]

        for i, (label_text, var) in enumerate(fields):
            ttk.Label(grid, text=label_text).grid(row=i, column=0, sticky=tk.W, pady=2, padx=5)
            ttk.Entry(grid, textvariable=var, width=40).grid(row=i, column=1, sticky=tk.W, pady=2, padx=5)

        ttk.Label(grid, text="Notes:").grid(row=4, column=0, sticky=tk.NW, pady=2, padx=5)
        self.notes_text = scrolledtext.ScrolledText(grid, width=38, height=4)
        self.notes_text.grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)

        button_frame = ttk.Frame(form_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="💾 Save", command=self.save_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧹 Clear", command=self.clear_form).pack(side=tk.LEFT, padx=5)

    def _create_contact_list(self):
        list_frame = ttk.LabelFrame(self.root, text="Contacts", padding=10)
        list_frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        columns = ("id", "name", "email", "phone")
        self.contact_tree = ttk.Treeview(list_frame, columns=columns, show="headings")

        self.contact_tree.heading("id", text="ID")
        self.contact_tree.heading("name", text="Name")
        self.contact_tree.heading("email", text="Email")
        self.contact_tree.heading("phone", text="Phone")

        self.contact_tree.column("id", width=50, anchor=tk.CENTER)
        self.contact_tree.column("name", width=200)
        self.contact_tree.column("email", width=200)
        self.contact_tree.column("phone", width=150)

        y_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.contact_tree.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.contact_tree.xview)
        self.contact_tree.configure(yscroll=y_scroll.set, xscroll=x_scroll.set)

        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.contact_tree.pack(fill=tk.BOTH, expand=True)

        self.contact_tree.bind("<<TreeviewSelect>>", self.on_contact_select)

        button_frame = ttk.Frame(list_frame)
        button_frame.pack(pady=5)

        ttk.Button(button_frame, text="➕ New", command=self.new_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Edit", command=self.edit_selected_contact).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Delete", command=self.delete_selected_contact).pack(side=tk.LEFT, padx=5)

    def load_contacts(self):
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
        contacts = self.db.get_all_contacts()
        for contact in contacts:
            self.contact_tree.insert("", tk.END, values=(
                contact["id"], contact["name"], contact["email"] or "", contact["phone"] or ""
            ))

    def search_contacts(self):
        search_term = self.search_var.get().strip()
        if not search_term:
            self.load_contacts()
            return
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)
        contacts = self.db.search_contacts(search_term)
        for contact in contacts:
            self.contact_tree.insert("", tk.END, values=(
                contact["id"], contact["name"], contact["email"] or "", contact["phone"] or ""
            ))

    def clear_search(self):
        self.search_var.set("")
        self.load_contacts()

    def on_contact_select(self, event):
        selected_items = self.contact_tree.selection()
        if not selected_items:
            return
        selected_item = selected_items[0]
        contact_id = self.contact_tree.item(selected_item)["values"][0]
        contact = self.db.get_contact_by_id(contact_id)
        if contact:
            self.current_contact_id = contact["id"]
            self.name_var.set(contact["name"])
            self.email_var.set(contact["email"] or "")
            self.phone_var.set(contact["phone"] or "")
            self.address_var.set(contact["address"] or "")
            self.notes_text.delete(1.0, tk.END)
            self.notes_text.insert(tk.END, contact["notes"] or "")

    def save_contact(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Validation Error", "Name is required.")
            return
        try:
            email = self.email_var.get().strip()
            phone = self.phone_var.get().strip()
            address = self.address_var.get().strip()
            notes = self.notes_text.get(1.0, tk.END).strip()
            if self.current_contact_id:
                success = self.db.update_contact(
                    self.current_contact_id, name, email, phone, address, notes
                )
                msg = "Contact updated successfully." if success else "Failed to update contact."
            else:
                contact_id = self.db.create_contact(name, email, phone, address, notes)
                msg = "Contact created successfully." if contact_id else "Failed to create contact."
                self.current_contact_id = contact_id
            self.load_contacts()
            messagebox.showinfo("Status", msg)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def new_contact(self):
        self.current_contact_id = None
        self.clear_form()

    def clear_form(self):
        self.name_var.set("")
        self.email_var.set("")
        self.phone_var.set("")
        self.address_var.set("")
        self.notes_text.delete(1.0, tk.END)

    def edit_selected_contact(self):
        if not self.contact_tree.selection():
            messagebox.showinfo("Info", "Select a contact to edit.")
        # Selection already triggers `on_contact_select`

    def delete_selected_contact(self):
        selected_items = self.contact_tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Select a contact to delete.")
            return
        contact_id = self.contact_tree.item(selected_items[0])["values"][0]
        contact_name = self.contact_tree.item(selected_items[0])["values"][1]
        if messagebox.askyesno("Confirm Deletion", f"Delete '{contact_name}'?"):
            if self.db.delete_contact(contact_id):
                if self.current_contact_id == contact_id:
                    self.clear_form()
                    self.current_contact_id = None
                self.load_contacts()
                messagebox.showinfo("Deleted", "Contact deleted.")
            else:
                messagebox.showerror("Error", "Could not delete contact.")

    def show_about(self):
        messagebox.showinfo(
            "About Contact Manager",
            "Contact Manager v1.0\n\nA stylish contact management app.\nBuilt with Python & Tkinter."
        )

    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
