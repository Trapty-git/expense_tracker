from db import connect_db

def add_expense(amount, category, date, note=""):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
                   (amount, category, date, note))
    conn.commit()
    conn.close()

def view_expenses():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_expense(expense_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
