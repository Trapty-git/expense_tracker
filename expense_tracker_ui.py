import tkinter as tk
from tkinter import messagebox, ttk
from expenses import add_expense, view_expenses, delete_expense
from db import create_table

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        python expense_tracker_ui.py        self.root.geometry("800x450")
        self.root.configure(bg="#f0f4f8")
        create_table()
        self.setup_ui()
        self.refresh_expenses()

    def setup_ui(self):
        # Input fields
        frame = tk.Frame(self.root, bg="#e3eaf2")
        frame.pack(pady=10, fill=tk.X)
        label_font = ("Arial", 11, "bold")
        entry_font = ("Arial", 11)
        tk.Label(frame, text="Amount:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(frame, font=entry_font)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Category:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=0, column=2, padx=5, pady=5)
        self.category_entry = tk.Entry(frame, font=entry_font)
        self.category_entry.grid(row=0, column=3, padx=5, pady=5)
        tk.Label(frame, text="Date (YYYY-MM-DD):", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = tk.Entry(frame, font=entry_font)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Note:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=1, column=2, padx=5, pady=5)
        self.note_entry = tk.Entry(frame, font=entry_font)
        self.note_entry.grid(row=1, column=3, padx=5, pady=5)
        tk.Button(frame, text="Add Expense", command=self.add_expense, bg="#3aafa9", fg="white", font=label_font, relief=tk.RAISED).grid(row=2, column=0, columnspan=4, pady=8)

        # Expense list with horizontal scrollbar
        tree_frame = tk.Frame(self.root, bg="#f0f4f8")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        x_scroll = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        x_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        y_scroll = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Amount", "Category", "Date", "Note"), show="headings", xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set, height=10)
        for col in ("ID", "Amount", "Category", "Date", "Note"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)
        x_scroll.config(command=self.tree.xview)
        y_scroll.config(command=self.tree.yview)

        # Delete button
        tk.Button(self.root, text="Delete Selected", command=self.delete_selected, bg="#fc5185", fg="white", font=label_font, relief=tk.RAISED).pack(pady=8)

    def add_expense(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            date = self.date_entry.get()
            note = self.note_entry.get()
            add_expense(amount, category, date, note)
            self.refresh_expenses()
            self.amount_entry.delete(0, tk.END)
            self.category_entry.delete(0, tk.END)
            self.date_entry.delete(0, tk.END)
            self.note_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for exp in view_expenses():
            self.tree.insert("", tk.END, values=exp)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No expense selected.")
            return
        for item in selected:
            expense_id = self.tree.item(item)["values"][0]
            delete_expense(expense_id)
        self.refresh_expenses()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
