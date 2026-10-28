import tkinter as tk
from tkinter import ttk, messagebox
import json, os
import numpy as np
import matplotlib.pyplot as plt

FILE = "library_books.json"

class Book:
    def __init__(self, id, title, author, category, available=True):
        self.id, self.title, self.author = id, title, author
        self.category, self.available = category, available

class FictionBook(Book):
    def __init__(self, id, title, author, available=True):
        super().__init__(id, title, author, "Fiction", available)

class NonFictionBook(Book):
    def __init__(self, id, title, author, available=True):
        super().__init__(id, title, author, "Non-Fiction", available)

class ReferenceBook(Book):
    def __init__(self, id, title, author, available=True):
        super().__init__(id, title, author, "Reference", available)

class Library:
    types = {"Fiction": FictionBook, "Non-Fiction": NonFictionBook,
             "Reference": ReferenceBook}

    def __init__(self):
        samples = [
            ("101", "Harry Potter", "J.K. Rowling", "Fiction"),
            ("102", "The Alchemist", "Paulo Coelho", "Fiction"),
            ("103", "The Hobbit", "J.R.R. Tolkien", "Fiction"),
            ("104", "Pride and Prejudice", "Jane Austen", "Fiction"),
            ("105", "Atomic Habits", "James Clear", "Non-Fiction"),
            ("106", "Deep Work", "Cal Newport", "Non-Fiction"),
            ("107", "Think Like a Monk", "Jay Shetty", "Non-Fiction"),
            ("108", "Rich Dad Poor Dad", "Robert Kiyosaki", "Non-Fiction"),
            ("109", "Oxford Dictionary", "Oxford", "Reference"),
            ("110", "English Grammar", "Wren & Martin", "Reference"),
            ("111", "Computer Fundamentals", "P.K. Sinha", "Reference"),
            ("112", "Operating System Concepts", "Silberschatz", "Reference")]
        self.books = []

        if os.path.exists(FILE):
            try:
                with open(FILE) as f:
                    for b in json.load(f):
                        self.books.append(self.types[b["category"]](
                            b["id"], b["title"], b["author"], b["available"]))
                return
            except (ValueError, KeyError, TypeError):
                self.books = []

        self.books = [self.types[c](i, t, a) for i, t, a, c in samples]

    def save(self):
        with open(FILE, "w") as f:
            json.dump([vars(b) for b in self.books], f, indent=2)

class LibraryApp:
    def __init__(self, root):
        self.root, self.lib = root, Library()
        root.title("Library Management System")
        root.geometry("1050x680")
        root.configure(bg="#F1F5F9")

        tk.Label(root, text="📚 LIBRARY MANAGEMENT SYSTEM", bg="#172554",
                 fg="white", font=("Arial", 21, "bold"), pady=18).pack(fill="x")

        cards = tk.Frame(root, bg="#F1F5F9")
        cards.pack(fill="x", padx=20, pady=15)
        self.stats = []

        for title, color in [("TOTAL BOOKS", "#2563EB"),
                             ("AVAILABLE", "#059669"), ("BORROWED", "#D97706")]:
            box = tk.Frame(cards, bg=color, pady=10)
            box.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(box, text=title, bg=color, fg="white").pack()
            label = tk.Label(box, text="0", bg=color, fg="white",
                             font=("Arial", 21, "bold"))
            label.pack()
            self.stats.append(label)

        top = tk.Frame(root, bg="#F1F5F9")
        top.pack(fill="x", padx=22, pady=5)
        self.search = tk.Entry(top, font=("Arial", 11))
        self.search.pack(side="left", fill="x", expand=True, ipady=7)
        self.search.insert(0, "Search books...")
        self.search.bind("<FocusIn>", self.clear_search)
        self.search.bind("<KeyRelease>", self.refresh)

        self.category = ttk.Combobox(top, values=["All Categories", *self.lib.types],
                                     state="readonly", width=18)
        self.category.set("All Categories")
        self.category.pack(side="left", padx=8, ipady=5)
        self.category.bind("<<ComboboxSelected>>", self.refresh)

        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True, padx=20, pady=12)
        self.table = ttk.Treeview(frame, columns=("ID", "Title", "Author", "Category", "Status"),
                                  show="headings")
        for col, width in zip(self.table["columns"], (70, 250, 220, 170, 120)):
            self.table.heading(col, text=col)
            self.table.column(col, width=width, anchor="center")

        scroll = ttk.Scrollbar(frame, command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"),
                        background="#DBEAFE")
        for tag, color in [("even", "white"), ("odd", "#EAF2FF")]:
            self.table.tag_configure(tag, background=color)

        bar = tk.Frame(root, bg="#F1F5F9")
        bar.pack(pady=12)
        actions = [("Add Book", self.add, "#2563EB"),
                   ("Remove", self.remove, "#DC2626"),
                   ("Borrow", lambda: self.status(False), "#D97706"),
                   ("Return", lambda: self.status(True), "#059669"),
                   ("Analytics", self.analytics, "#6D28D9")]

        for name, cmd, color in actions:
            tk.Button(bar, text=name, command=cmd, bg=color, fg="white",
                      font=("Arial", 10, "bold"), relief="flat",
                      padx=14, pady=9, cursor="hand2").pack(side="left", padx=5)

        self.refresh()

    def clear_search(self, event):
        if self.search.get() == "Search books...":
            self.search.delete(0, "end")

    def refresh(self, event=None):
        q, cat = self.search.get().lower(), self.category.get()
        if q == "search books...":
            q = ""
        self.table.delete(*self.table.get_children())

        for i, b in enumerate(self.lib.books):
            if q in f"{b.id} {b.title} {b.author}".lower() and (
                    cat == "All Categories" or b.category == cat):
                self.table.insert("", "end", iid=b.id,
                    values=(b.id, b.title, b.author, b.category,
                            "Available" if b.available else "Borrowed"),
                    tags=("even" if i % 2 == 0 else "odd",))

        total = len(self.lib.books)
        available = sum(b.available for b in self.lib.books)
        for label, value in zip(self.stats, (total, available, total - available)):
            label.config(text=value)

    def add(self):
        win = tk.Toplevel(self.root)
        win.title("Add New Book")
        win.geometry("350x340")
        win.configure(bg="#F1F5F9")
        win.transient(self.root)
        win.grab_set()
        fields = {}

        for name in ("Book ID", "Title", "Author"):
            tk.Label(win, text=name, bg="#F1F5F9").pack(pady=(10, 2))
            fields[name] = tk.Entry(win, width=32)
            fields[name].pack(ipady=4)

        tk.Label(win, text="Category", bg="#F1F5F9").pack(pady=(10, 2))
        category = ttk.Combobox(win, values=list(self.lib.types),
                                state="readonly", width=29)
        category.set("Fiction")
        category.pack()

        def save():
            id, title, author = [fields[x].get().strip()
                                 for x in ("Book ID", "Title", "Author")]
            if not all((id, title, author)):
                messagebox.showerror("Error", "Please fill in every field.", parent=win)
                return
            if any(b.id == id for b in self.lib.books):
                messagebox.showerror("Error", "Book ID already exists.", parent=win)
                return
            self.lib.books.append(self.lib.types[category.get()](id, title, author))
            self.lib.save()
            self.refresh()
            win.destroy()
            messagebox.showinfo("Success", "Book added successfully!")

        tk.Button(win, text="Add Book", command=save, bg="#2563EB",
                  fg="white", padx=20, pady=7).pack(pady=18)

    def selected(self):
        rows = self.table.selection()
        if not rows:
            messagebox.showwarning("Notice", "Please select a book.")
            return None
        return next((b for b in self.lib.books if b.id == rows[0]), None)

    def remove(self):
        b = self.selected()
        if b and messagebox.askyesno("Confirm", f"Remove '{b.title}'?"):
            self.lib.books.remove(b)
            self.lib.save()
            self.refresh()

    def status(self, available):
        b = self.selected()
        if not b:
            return
        if b.available == available:
            messagebox.showinfo("Status", "Book already has this status.")
            return
        b.available = available
        self.lib.save()
        self.refresh()

    def analytics(self):
        cats = list(self.lib.types)
        counts = np.array([sum(b.category == c for b in self.lib.books) for c in cats])
        available = sum(b.available for b in self.lib.books)
        borrowed = len(self.lib.books) - available
        fig, ax = plt.subplots(1, 2, figsize=(9, 4))
        ax[0].bar(cats, counts)
        ax[0].set_title("Books by Category")
        ax[1].pie([available, borrowed] if available + borrowed else [1, 0],
                  labels=["Available", "Borrowed"], autopct="%1.1f%%")
        ax[1].set_title("Book Availability")
        fig.tight_layout()
        plt.show()

root = tk.Tk()
LibraryApp(root)
root.mainloop()