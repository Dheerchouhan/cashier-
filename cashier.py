import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import datetime

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Replace with your MySQL username
        password="hanumanu9",  # Replace with your MySQL password
        database="cash_counter_db"
    )

# Add transaction to the database
def add_transaction(transaction_type, amount, reason):
    db = connect_db()
    cursor = db.cursor()
    now = datetime.now()
    date = now.date()
    time = now.time()
    cursor.execute("INSERT INTO transactions (transaction_type, amount, date, time, reason) VALUES (%s, %s, %s, %s, %s)", (transaction_type, amount, date, time, reason))
    db.commit()
    db.close()

# Fetch transactions from the database
def fetch_transactions():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM transactions")
    transactions = cursor.fetchall()
    db.close()
    return transactions

# Calculate the current balance
def calculate_balance():
    transactions = fetch_transactions()
    balance = 0
    for transaction in transactions:
        if transaction[1] == "add":
            balance += float(transaction[2])
        elif transaction[1] == "withdraw":
            balance -= float(transaction[2])
    return balance

# Fetch user from the database
def fetch_user(username, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()
    db.close()
    return user

# Login Window
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.create_widgets()

    def create_widgets(self):
        # Username entry
        self.username_label = tk.Label(self.root, text="Username:")
        self.username_label.grid(row=0, column=0, padx=10, pady=10)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        # Password entry
        self.password_label = tk.Label(self.root, text="Password:")
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        # Login button
        self.login_button = tk.Button(self.root, text="Login", command=self.login)
        self.login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        user = fetch_user(username, password)
        if user:
            role = user[3]
            self.root.destroy()
            if role == "admin":
                root = tk.Tk()
                AdminPanel(root)
            else:
                root = tk.Tk()
                EmployeePanel(root)
        else:
            messagebox.showwarning("Login Failed", "Invalid username or password")

# Employee Panel
class EmployeePanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Panel")
        self.create_widgets()

    def create_widgets(self):
        # Amount entry
        self.amount_label = tk.Label(self.root, text="Amount:")
        self.amount_label.grid(row=0, column=0, padx=10, pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)

        # Reason entry
        self.reason_label = tk.Label(self.root, text="Reason:")
        self.reason_label.grid(row=1, column=0, padx=10, pady=10)
        self.reason_entry = tk.Entry(self.root)
        self.reason_entry.grid(row=1, column=1, padx=10, pady=10)

        # Add cash button
        self.add_cash_button = tk.Button(self.root, text="Add Cash", command=self.add_cash)
        self.add_cash_button.grid(row=2, column=0, padx=10, pady=10)

        # Withdraw cash button
        self.withdraw_cash_button = tk.Button(self.root, text="Withdraw Cash", command=self.withdraw_cash)
        self.withdraw_cash_button.grid(row=2, column=1, padx=10, pady=10)

        # Balance label
        self.balance_label = tk.Label(self.root, text=f"Current Balance: {calculate_balance()}")
        self.balance_label.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def update_balance_label(self):
        self.balance_label.config(text=f"Current Balance: {calculate_balance()}")

    def add_cash(self):
        amount = self.amount_entry.get()
        reason = self.reason_entry.get()
        if amount and reason:
            add_transaction("add", amount, reason)
            messagebox.showinfo("Success", "Cash added successfully")
            self.amount_entry.delete(0, tk.END)
            self.reason_entry.delete(0, tk.END)
            self.update_balance_label()
        else:
            messagebox.showwarning("Input Error", "Please enter an amount and reason")

    def withdraw_cash(self):
        amount = self.amount_entry.get()
        reason = self.reason_entry.get()
        if amount and reason:
            if float(amount) <= calculate_balance():
                add_transaction("withdraw", amount, reason)
                messagebox.showinfo("Success", "Cash withdrawn successfully")
                self.amount_entry.delete(0, tk.END)
                self.reason_entry.delete(0, tk.END)
                self.update_balance_label()
            else:
                messagebox.showwarning("Insufficient Funds", "Withdrawal amount exceeds current balance")
        else:
            messagebox.showwarning("Input Error", "Please enter an amount and reason")

# Admin Panel
class AdminPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Admin Panel")
        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Type", "Amount", "Date", "Time", "Reason"), show='headings')
        self.tree.heading("ID", text="ID")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Reason", text="Reason")
        self.tree.grid(row=0, column=0, padx=10, pady=10)

        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_transactions, bg="orange", fg="black")
        self.refresh_button.grid(row=1, column=0, padx=10, pady=10)

        self.balance_label = tk.Label(self.root, text=f"Total Cash in Bank: {calculate_balance()}", bg="blue", fg="white")
        self.balance_label.grid(row=2, column=0, padx=10, pady=10)

        self.add_button = tk.Button(self.root, text="Add Transaction", command=self.add_transaction_ui, bg="green", fg="white")
        self.add_button.grid(row=3, column=0, padx=10, pady=10)

        self.update_button = tk.Button(self.root, text="Update Transaction", command=self.update_transaction_ui, bg="yellow", fg="black")
        self.update_button.grid(row=4, column=0, padx=10, pady=10)

        self.delete_button = tk.Button(self.root, text="Delete Transaction", command=self.delete_transaction_ui, bg="red", fg="white")
        self.delete_button.grid(row=5, column=0, padx=10, pady=10)

        self.refresh_transactions()

    def refresh_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        transactions = fetch_transactions()
        for transaction in transactions:
            self.tree.insert("", "end", values=transaction)
        self.balance_label.config(text=f"Total Cash in Bank: {calculate_balance()}")

    def add_transaction_ui(self):
        def add_transaction_handler():
            transaction_type = type_entry.get()
            amount = float(amount_entry.get())
            reason = reason_entry.get()
            add_transaction(transaction_type, amount, reason)
            add_window.destroy()
            self.refresh_transactions()

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Transaction")

        tk.Label(add_window, text="Transaction Type (add/withdraw)").grid(row=0, column=0, padx=10, pady=10)
        type_entry = tk.Entry(add_window)
        type_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Amount").grid(row=1, column=0, padx=10, pady=10)
        amount_entry = tk.Entry(add_window)
        amount_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(add_window, text="Reason").grid(row=2, column=0, padx=10, pady=10)
        reason_entry = tk.Entry(add_window)
        reason_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Button(add_window, text="Add", command=add_transaction_handler).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def update_transaction_ui(self):
        selected_item = self.tree.selection()
        if selected_item:
            transaction = self.tree.item(selected_item)["values"]

            def update_transaction_handler():
                transaction_id = transaction[0]
                transaction_type = type_entry.get()
                amount = float(amount_entry.get())
                reason = reason_entry.get()
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("UPDATE transactions SET transaction_type = %s, amount = %s, reason = %s WHERE id = %s", (transaction_type, amount, reason, transaction_id))
                db.commit()
                db.close()
                update_window.destroy()
                self.refresh_transactions()

            update_window = tk.Toplevel(self.root)
            update_window.title("Update Transaction")

            tk.Label(update_window, text="Transaction Type (add/withdraw)").grid(row=0, column=0, padx=10, pady=10)
            type_entry = tk.Entry(update_window)
            type_entry.insert(0, transaction[1])
            type_entry.grid(row=0, column=1, padx=10, pady=10)

            tk.Label(update_window, text="Amount").grid(row=1, column=0, padx=10, pady=10)
            amount_entry = tk.Entry(update_window)
            amount_entry.insert(0, transaction[2])
            amount_entry.grid(row=1, column=1, padx=10, pady=10)

            tk.Label(update_window, text="Reason").grid(row=2, column=0, padx=10, pady=10)
            reason_entry = tk.Entry(update_window)
            reason_entry.insert(0, transaction[5])
            reason_entry.grid(row=2, column=1, padx=10, pady=10)

            tk.Button(update_window, text="Update", command=update_transaction_handler).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    def delete_transaction_ui(self):
        selected_item = self.tree.selection()
        if selected_item:
            transaction = self.tree.item(selected_item)["values"]

            def delete_transaction_handler():
                transaction_id = transaction[0]
                db = connect_db()
                cursor = db.cursor()
                cursor.execute("DELETE FROM transactions WHERE id = %s", (transaction_id,))
                db.commit()
                db.close()
                delete_window.destroy()
                self.refresh_transactions()

            delete_window = tk.Toplevel(self.root)
            delete_window.title("Delete Transaction")

            tk.Label(delete_window, text="Are you sure you want to delete this transaction?").grid(row=0, column=0, columnspan=2, padx=10, pady=10)
            tk.Button(delete_window, text="Yes", command=delete_transaction_handler).grid(row=1, column=0, padx=10, pady=10)
            tk.Button(delete_window, text="No", command=delete_window.destroy).grid(row=1, column=1, padx=10, pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    login_app = LoginWindow(root)
    root.mainloop()
