from db import create_table
from expenses import add_expense, view_expenses, delete_expense

def menu():
    print("\nExpense Tracker")
    print("1. Add Expense")
    print("2. View Expenses")
    print("3. Delete Expense")
    print("4. Exit")

def main():
    create_table()
    while True:
        menu()
        choice = input("Enter choice: ")
        if choice == "1":
            amount = float(input("Amount: "))
            category = input("Category: ")
            date = input("Date (YYYY-MM-DD): ")
            note = input("Note (optional): ")
            add_expense(amount, category, date, note)
        elif choice == "2":
            expenses = view_expenses()
            for exp in expenses:
                print(exp)
        elif choice == "3":
            expense_id = int(input("Enter Expense ID to delete: "))
            delete_expense(expense_id)
        elif choice == "4":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()
