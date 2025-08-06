import tkinter as tk
from tkinter import messagebox, ttk
from expenses import add_expense, view_expenses, delete_expense
from db import create_table
try:
    from tkcalendar import DateEntry
    HAS_TKCALENDAR = True
except ImportError:
    HAS_TKCALENDAR = False
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("900x500")
        self.root.configure(bg="#f0f4f8")
        create_table()
        self.categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"]
        self.setup_ui()
        self.refresh_expenses()
        self.update_summary()

    def setup_ui(self):
        frame = tk.Frame(self.root, bg="#e3eaf2")
        frame.pack(pady=10, fill=tk.X)
        label_font = ("Arial", 11, "bold")
        entry_font = ("Arial", 11)
        tk.Label(frame, text="Amount:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = tk.Entry(frame, font=entry_font)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(frame, text="Category:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=0, column=2, padx=5, pady=5)
        self.category_combo = ttk.Combobox(frame, values=self.categories, font=entry_font, state="readonly")
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set(self.categories[0])
        tk.Label(frame, text="Date:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=1, column=0, padx=5, pady=5)
        if HAS_TKCALENDAR:
            self.date_entry = DateEntry(frame, font=entry_font, date_pattern="yyyy-mm-dd")
        else:
            self.date_entry = tk.Entry(frame, font=entry_font)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(frame, text="Note:", bg="#e3eaf2", fg="#2d4059", font=label_font).grid(row=1, column=2, padx=5, pady=5)
        self.note_entry = tk.Entry(frame, font=entry_font)
        self.note_entry.grid(row=1, column=3, padx=5, pady=5)
        tk.Button(frame, text="Add Expense", command=self.add_expense, bg="#3aafa9", fg="white", font=label_font, relief=tk.RAISED).grid(row=2, column=0, columnspan=4, pady=8)

        # Summary section
        self.summary_label = tk.Label(self.root, text="", bg="#f0f4f8", fg="#22223b", font=("Arial", 12, "bold"))
        self.summary_label.pack(pady=5)

        # Chart section (moved here for visibility)
        chart_frame = tk.Frame(self.root, bg="#f0f4f8")
        chart_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        self.chart_frame = chart_frame
        self.chart_type = tk.StringVar(value="Pie")
        chart_btn_frame = tk.Frame(chart_frame, bg="#f0f4f8")
        chart_btn_frame.pack(side=tk.TOP, fill=tk.X)
        tk.Button(chart_btn_frame, text="Pie Chart", command=lambda: self.show_chart("Pie"), bg="#3aafa9", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(chart_btn_frame, text="Bar Chart", command=lambda: self.show_chart("Bar"), bg="#3aafa9", fg="white").pack(side=tk.LEFT, padx=5)
        self.chart_canvas = None

        # Search/filter
        search_frame = tk.Frame(self.root, bg="#f0f4f8")
        search_frame.pack(fill=tk.X, padx=10)
        tk.Label(search_frame, text="Search:", bg="#f0f4f8", font=label_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", lambda *args: self.refresh_expenses())
        tk.Entry(search_frame, textvariable=self.search_var, font=entry_font, width=30).pack(side=tk.LEFT, padx=5)

        # Expense list with scrollbars
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
        self.tree.bind("<Double-1>", self.edit_expense)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#f0f4f8")
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected, bg="#fc5185", fg="white", font=label_font, relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Export to CSV", command=self.export_csv, bg="#3aafa9", fg="white", font=label_font, relief=tk.RAISED).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Toggle Theme", command=self.toggle_theme, bg="#22223b", fg="white", font=label_font, relief=tk.RAISED).pack(side=tk.LEFT, padx=5)

    def add_expense(self):
        try:
            amount = self.amount_entry.get()
            category = self.category_combo.get()
            date = self.date_entry.get()
            note = self.note_entry.get()
            if not amount or not category or not date:
                messagebox.showwarning("Input Error", "Amount, Category, and Date are required.")
                return
            try:
                amount = float(amount)
            except ValueError:
                messagebox.showwarning("Input Error", "Amount must be a number.")
                return
            if len(date) != 10 or date[4] != '-' or date[7] != '-':
                messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format.")
                return
            add_expense(amount, category, date, note)
            self.refresh_expenses()
            self.update_summary()
            self.amount_entry.delete(0, tk.END)
            self.category_combo.set(self.categories[0])
            if not HAS_TKCALENDAR:
                self.date_entry.delete(0, tk.END)
            self.note_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_expenses(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        search = self.search_var.get().lower()
        for exp in view_expenses():
            if search:
                if any(search in str(val).lower() for val in exp):
                    self.tree.insert("", tk.END, values=exp)
            else:
                self.tree.insert("", tk.END, values=exp)

    def show_chart(self, chart_type):
        expenses = view_expenses()
        by_cat = {}
        for exp in expenses:
            by_cat[exp[2]] = by_cat.get(exp[2], 0) + float(exp[1])
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()
        fig = plt.Figure(figsize=(4, 2.5), dpi=100)
        if chart_type == "Pie":
            ax = fig.add_subplot(111)
            categories = list(by_cat.keys())
            amounts = list(by_cat.values())
            ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
            ax.set_title("Expenses by Category")
        elif chart_type == "Bar":
            ax = fig.add_subplot(111)
            categories = list(by_cat.keys())
            amounts = list(by_cat.values())
            ax.bar(categories, amounts, color="#3aafa9")
            ax.set_ylabel("Amount")
            ax.set_title("Expenses by Category")
            for i, v in enumerate(amounts):
                ax.text(i, v + max(amounts)*0.01, f"₹{v:.2f}", ha='center', va='bottom', fontsize=8)
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.chart_canvas.draw()
        self.chart_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=False)
        self.chart_type.set(chart_type)

    def update_summary(self):
        expenses = view_expenses()
        total = sum(float(exp[1]) for exp in expenses)
        by_cat = {}
        for exp in expenses:
            by_cat[exp[2]] = by_cat.get(exp[2], 0) + float(exp[1])
        summary = f"Total: ₹{total:.2f}  |  " + "  |  ".join(f"{cat}: ₹{amt:.2f}" for cat, amt in by_cat.items())
        self.summary_label.config(text=summary)
        self.show_chart(self.chart_type.get())

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "No expense selected.")
            return
        if not messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected expense(s)?"):
            return
        for item in selected:
            expense_id = self.tree.item(item)["values"][0]
            delete_expense(expense_id)
        self.refresh_expenses()
        self.update_summary()

    def export_csv(self):
        import csv
        from tkinter import filedialog
        expenses = view_expenses()
        if not expenses:
            messagebox.showinfo("Export", "No expenses to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file:
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Amount", "Category", "Date", "Note"])
                writer.writerows(expenses)
            messagebox.showinfo("Export", f"Exported to {file}")

    def edit_expense(self, event):
        item = self.tree.selection()
        if not item:
            return
        item = item[0]
        values = self.tree.item(item)["values"]
        edit_win = tk.Toplevel(self.root)
        edit_win.title("Edit Expense")
        edit_win.geometry("400x250")
        tk.Label(edit_win, text="Amount:").grid(row=0, column=0, padx=5, pady=5)
        amount_entry = tk.Entry(edit_win)
        amount_entry.grid(row=0, column=1, padx=5, pady=5)
        amount_entry.insert(0, values[1])
        tk.Label(edit_win, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        category_combo = ttk.Combobox(edit_win, values=self.categories, state="readonly")
        category_combo.grid(row=1, column=1, padx=5, pady=5)
        category_combo.set(values[2])
        tk.Label(edit_win, text="Date:").grid(row=2, column=0, padx=5, pady=5)
        if HAS_TKCALENDAR:
            date_entry = DateEntry(edit_win, date_pattern="yyyy-mm-dd")
            date_entry.set_date(values[3])
        else:
            date_entry = tk.Entry(edit_win)
            date_entry.insert(0, values[3])
        date_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Label(edit_win, text="Note:").grid(row=3, column=0, padx=5, pady=5)
        note_entry = tk.Entry(edit_win)
        note_entry.grid(row=3, column=1, padx=5, pady=5)
        note_entry.insert(0, values[4])
        def save_edit():
            try:
                new_amount = float(amount_entry.get())
                new_category = category_combo.get()
                new_date = date_entry.get()
                new_note = note_entry.get()
                if not new_amount or not new_category or not new_date:
                    messagebox.showwarning("Input Error", "Amount, Category, and Date are required.")
                    return
                if len(new_date) != 10 or new_date[4] != '-' or new_date[7] != '-':
                    messagebox.showwarning("Input Error", "Date must be in YYYY-MM-DD format.")
                    return
                delete_expense(values[0])
                add_expense(new_amount, new_category, new_date, new_note)
                self.refresh_expenses()
                self.update_summary()
                edit_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        tk.Button(edit_win, text="Save", command=save_edit, bg="#3aafa9", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

    def toggle_theme(self):
        # Simple light/dark toggle
        if self.root.cget("bg") == "#f0f4f8":
            self.root.configure(bg="#22223b")
            self.summary_label.configure(bg="#22223b", fg="#f0f4f8")
        else:
            self.root.configure(bg="#f0f4f8")
            self.summary_label.configure(bg="#f0f4f8", fg="#22223b")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
