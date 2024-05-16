"""
This is chocshop.py, a script for managing a chocolate shop.

This script connects to a MySQL database hosted on AWS RDS and provides full functionality for CRUD.

Author: Jason Fearnall
Date: 5/16/2024
Filename: chocshop.py
"""

import mysql.connector
from mysql.connector import Error
import datetime
from prettytable import PrettyTable
from tabulate import tabulate

db =  None

# Function to login to the database
def login():

    global db
    while True:
        email = input("Enter your email (or 'q' to quit): ") 
        if email.lower() == 'q':
            print("Exiting program.")
            exit(0)

        password = input("Enter your password: ")

        try:
            db = mysql.connector.connect(
                host='choc-shop.cjmc0e4yormu.us-east-1.rds.amazonaws.com',
                user=email,
                password=password,
                database='chocshop'
            )
        except Error as e:
            print("Invalid email or password. Please try again.")
            continue

        if db.is_connected():
            print("Login successful!\n")
            return 

# define function to view all chocolates
def view_chocolates():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM chocolate")
    chocolates = cursor.fetchall()
    table = PrettyTable(['Chocolate ID', 'Name', 'Price'])
    for chocolate in chocolates:
        table.add_row([chocolate[0], chocolate[1], chocolate[2]])
    print(table)

# define function to view all items in an order
def view_order_items(order_id):
    cursor = db.cursor()
    query = """
        SELECT order_items.choc_id, order_items.order_id, chocolate.type, order_items.quantity
        FROM order_items
        INNER JOIN chocolate ON order_items.choc_id = chocolate.choc_id
        WHERE order_items.order_id = %s
    """
    cursor.execute(query, (order_id,))
    items = cursor.fetchall()

    if not items:
        print("No items found for this order.")

    table = PrettyTable(['Item ID', 'Order ID', 'Chocolate Type', 'Quantity'])
    for item in items:
        table.add_row([item[0], item[1], item[2], item[3]])

    print(table)

# define function to view all orders by a customer
def orders_by_cust(cust_id):
    
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    customer = cursor.fetchone()
    print(f"\nCustomer ID: {customer[0]}, Name: {customer[1]}")
   
    query = "SELECT * FROM orders WHERE cust_id = %s"
    cursor.execute(query, (cust_id,))
    orders = cursor.fetchall()

    if not orders:
        print("No orders found.")
        return False
    
    table = PrettyTable(['Order ID', 'Customer', 'Order Date', 'Subtotal'])
    for order in orders:
        table.add_row([order[0], customer[1], order[2], order[3]])

    print(table)

    if len(orders) == 1:
        while True:
            print("\n1. View order")
            print("2. Delete order")
            print("q. Return")
            choice = input("Enter your choice: ")
            if choice == '1':
                view_order_items(orders[0][0]) 
            elif choice == '2':
                result = delete_order(orders[0][0]) 
                if result=='deleted':
                    break
            elif choice.lower() == 'q':
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        order_id = input("Multiple orders found. Please enter the order ID: ")
        orders_by_order(order_id)
    return True

# define function to view all orders by a customer
def orders_by_order(order_id):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
    order = cursor.fetchone()

    if not order:
        print("No order found.")
        return
    
    query = "SELECT * FROM customer WHERE cust_id = %s"
    cursor.execute(query, (order[1],))  
    customer = cursor.fetchone()

    if not customer:
        print("No customer found for the given order.")
        return


    print(f"\nOrder Date: {order[2]}, \nOrder ID: {order[0]}, \nCustomer Name: {customer[1]}, \nSubtotal: {order[3]}")

    query = """
        SELECT order_items.choc_id, order_items.order_id, chocolate.type, order_items.quantity
        FROM order_items
        INNER JOIN chocolate ON order_items.choc_id = chocolate.choc_id
        WHERE order_items.order_id = %s
    """
    cursor.execute(query, (order_id,))
    items = cursor.fetchall()

    if not items:
        print("No items found for this order.")

    table = PrettyTable(['Item ID', 'Order ID', 'Product Name', 'Quantity'])
    for item in items:
        table.add_row([item[0], item[1], item[2], item[3]])

    print(table)

    while True:
        print("d. Delete order")
        print("q. Return")
        choice = input("Enter your choice: ")
        if choice.lower() == 'd':
            result=delete_order(order[0])
            if result=='deleted':
                break       
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid choice. Please try again.")

# define function to place an order
def place_order(cust_id):
    cursor = db.cursor()

    while True:
        cursor.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
        customer = cursor.fetchone()
        if customer is None:
            print("\nNo customer with the given ID exists\n")
            cust_id = input("\nEnter customer ID (or 'q' to finish): ")
            if cust_id.lower() == 'q':
                return
            continue
        else:
            break

    cursor.execute("INSERT INTO orders (cust_id, order_date) VALUES (%s, NOW())", (cust_id,))
    order_id = cursor.lastrowid
    view_chocolates()

    order_items = []
    while True:
        choc_id = input("Enter chocolate ID (or 'q' to finish): ")
        if choc_id.lower() == 'q':
            break
        cursor.execute("SELECT * FROM chocolate WHERE choc_id = %s", (choc_id,))
        chocolate = cursor.fetchone()
        if chocolate is None:
            print("\nNo chocolate with the given ID exists, please reenter\n")
            continue

        while True:
            quantity = input("Enter quantity (or 'q' to finish): ")
            if quantity.lower() == 'q':
                break
            if int(quantity) > 0:
                order_items.append({'choc_id': choc_id, 'quantity': quantity, 'price': chocolate[2]})
                break
            print("\nQuantity must be more than zero\n")

        add_more = input("Would you like to add another product? (y/n): ")
        if add_more.lower() != 'y':
            break

    print("\n\nItems added to order:\n")
    for item in order_items:
        print(f"Chocolate ID: {item['choc_id']}, Quantity: {item['quantity']}, Price: {item['price']}")

    verify = input("Do you want to commit the order to the database? (y/n): ")
    if verify.lower() == 'y':
        for item in order_items:
            cursor.execute("INSERT INTO order_items (order_id, choc_id, quantity) VALUES (%s, %s, %s)", (order_id, item['choc_id'], item['quantity']))
            cursor.execute("""UPDATE orders SET subtotal = (SELECT SUM(chocolate.price * quantity) FROM order_items 
                                INNER JOIN chocolate ON order_items.choc_id = chocolate.choc_id WHERE order_id = %s) WHERE order_id = %s""", (order_id, order_id))
        db.commit()
        print("Order committed to the database.")
    else:
        print("Order not committed.")

# define function to view, edit, or delete orders  
def view_orders():
    
    cursor = db.cursor()

    search_option = input("Search by order number, Customer name, Order date or enter 'all' to see all orders: ")

    if search_option.lower() == 'q':
        return
    elif search_option.isdigit():
        orders_by_order(search_option)
    elif search_option == 'all':
        query = """SELECT orders.order_id, customer.name, orders.order_date, orders.subtotal FROM orders 
                        INNER JOIN customer ON orders.cust_id = customer.cust_id"""
        cursor.execute(query)
    else:
        try:
            datetime.datetime.strptime(search_option, '%Y-%m-%d')
            query = """SELECT orders.order_id, customer.name, orders.order_date, orders.subtotal FROM orders 
                            INNER JOIN customer ON orders.cust_id = customer.cust_id WHERE orders.order_date = %s"""
            cursor.execute(query, (search_option,))
        except ValueError:
            query = """SELECT orders.order_id, customer.name, orders.order_date, orders.subtotal FROM orders 
                            INNER JOIN customer ON orders.cust_id = customer.cust_id WHERE customer.name LIKE %s"""
            cursor.execute(query, ('%' + search_option + '%',))

    try:
        orders = cursor.fetchall()
    except mysql.connector.errors.InterfaceError:
        print("No orders found.")
        return

    if not orders:
        print("No orders found.")
        return

    table = PrettyTable(['Order ID', 'Customer', 'Order Date', 'Subtotal'])
    for order in orders:
        table.add_row([order[0], order[1], order[2], order[3]])

    print(table)

    order_id = input("Enter the ID of the order you want to view: ")
    orders_by_order(order_id)

# define delete order function
def delete_order(order_id):
    cursor = db.cursor()

    print(f"Order ID: {order_id}")

    query = "SELECT * FROM orders WHERE order_id = %s"
    cursor.execute(query, (order_id,))
    order = cursor.fetchone()

    if not order:
        print("No order found with the given ID.")
        return

    print(f"\nOrder Information:\nID: {order[0]}\nDate: {order[1]}")
                                                                                          # Fetch order items
    query = """
    SELECT order_items.quantity, chocolate.type 
    FROM order_items  
    JOIN chocolate ON order_items.choc_id = chocolate.choc_id                               
    WHERE order_items.order_id = %s
    """
    cursor.execute(query, (order_id,))
    order_items = cursor.fetchall()

    if not order_items:
        print("No items found for this order.")
        return

    print("\nOrder Items:")
    for item in order_items:
        print(f"Product: {item[1]}, Quantity: {item[0]}")

    while True:
        confirm = input("\nAre you sure you want to delete this order? (y/n): ")
        if confirm.lower() == 'y':
            cursor.execute("DELETE FROM order_items WHERE order_id = %s", (order_id,))     # Delete order items
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))          # Delete order
            db.commit()
            print("Order deleted successfully.")
            return 'deleted'
        elif confirm.lower() == 'n':
            return
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

# Function to view all orders
def view_all_orders():
    cursor = db.cursor()

    query = """
    SELECT orders.order_id, customer.name, orders.order_date, orders.subtotal
    FROM orders
    INNER JOIN customer ON orders.cust_id = customer.cust_id
    """
    cursor.execute(query)
    orders = cursor.fetchall()

    if not orders:
        print("No orders found.")
        return

    table = PrettyTable(['Order ID', 'Customer', 'Order Date', 'Subtotal'])
    for order in orders:
        table.add_row([order[0], order[1], order[2], order[3]])

    print(table)
   
# Function to add a new customer
def add_customer():
    cursor = db.cursor()
    while True:
        try:
            name = input("Enter customer name: ")
            email = input("Enter customer email: ")
            phone = input("Enter customer phone: ")
            address = input("Enter customer address: ")
            zip_code = input("Enter customer zip code: ")

            # Check if the email is already in use
            cursor.execute(f"SELECT * FROM customer WHERE email = '{email}';")
            if cursor.fetchone() is not None:
                print("This email is already in use. Please try again with a different email.")
                continue

            query = "INSERT INTO customer (name, email, phone, address, zip_code) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, address, zip_code))
            db.commit()
            print("\nCustomer added successfully.")
            break
        except Exception as e:
            print("\nAn error occurred: ", str(e))
            print("Please try again.\n")

# Function to edit a customer
def edit_customer(cust_id):
    cursor = db.cursor()

    while True:
        cursor.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
        customer = cursor.fetchone()
        if customer is None:
            print("\nNo customer with the given ID exists\n")
            return
        else:
            print(f"\nAre you sure you want to edit the following customer?\n\nID: {customer[0]}\nName: {customer[1]}\nEmail: {customer[2]}")
            confirm = input("\nEnter 'y' to confirm, 'n' to cancel: ")
            if confirm.lower() != 'y':
                print("\nEdit cancelled.\n")
                return

            new_name = input("\nEnter new name: ")
            new_email = input("Enter new email: ")

            print(f"\nOld Information:\nID: {customer[0]}\nName: {customer[1]}\nEmail: {customer[2]}")
            print(f"\nNew Information:\nID: {customer[0]}\nName: {new_name}\nEmail: {new_email}")

            confirm = input("\nIs this information correct? Enter 'y' for yes, 'n' to re-enter information, 'q' to quit: ")
            if confirm.lower() == 'y':
                cursor.execute("UPDATE customer SET name = %s, email = %s WHERE cust_id = %s", (new_name, new_email, cust_id))
                db.commit()
                print("\nCustomer updated successfully.\n")
                return
            elif confirm.lower() == 'q':
                return
            
# define function to delete a customer
def delete_customer(cust_id):
    cursor = db.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE cust_id = %s", (cust_id,))
    orders = cursor.fetchall()
    if orders:
        print("Cannot delete customer because they have existing orders.")
        db.close()
        return

    cursor.execute("SELECT * FROM customer WHERE cust_id = %s", (cust_id,))
    customer = cursor.fetchone()
    if not customer:
        print("No customer found with the provided ID.")
        db.close()
        return

    print(f"Are you sure you want to delete the following customer?\nID: {customer[0]}\nName: {customer[1]}\nEmail: {customer[2]}")
    confirm = input("Enter 'y' to confirm, 'n' to cancel: ")
    if confirm.lower() != 'y':
        print("Deletion cancelled.")
        db.close()
        return

    query = "DELETE FROM customer WHERE cust_id = %s"
    cursor.execute(query, (cust_id,))
    db.commit()
    print("Customer deleted successfully.")

#define search customer function
def search_customer():
    cursor = db.cursor()
    search_term = input("Enter a name, email, or ID to search (or 'all' to view all customers): ")

    if search_term.lower() == 'all':
        query = "SELECT * FROM customer"
        params = ()
    elif search_term.isdigit():
        query = "SELECT * FROM customer WHERE cust_id = %s"
        params = (search_term,)
    else:
        query = "SELECT * FROM customer WHERE name LIKE %s OR email LIKE %s"
        params = ('%' + search_term + '%', '%' + search_term + '%')

    cursor.execute(query, params)
    results = cursor.fetchall()

    if not results:
        print("No customers found.")
        return

    table = PrettyTable(['Customer ID', 'Name', 'Email Address'])
    for customer in results:
        table.add_row([customer[0], customer[1], customer[2]])
    print(table)

    while True:
        cust_id = input("Enter a customer ID from the results (or 'q' to quit): ")
        if cust_id.lower() == 'q':
            return
        selected_customer = next((customer for customer in results if str(customer[0]) == cust_id), None)
        if selected_customer is None:
            print("Invalid ID. Please enter a customer ID from the results.")
            continue
        while True:
            print('\n\n\n\n' + '-' * 80)
            print(f"Customer Information:\nID: {selected_customer[0]}\nName: {selected_customer[1]}\nEmail: {selected_customer[2]}")
    
            cursor.execute("SELECT COUNT(*) FROM orders WHERE cust_id = %s", (selected_customer[0],))
            order_count = cursor.fetchone()[0]
            
            print('-' * 80)
            print(f"Number of Orders: {order_count}")
            print('-' * 80)
            print("\n1. Place Order\n2. View Orders\n3. Edit customer\n4. Delete customer\n5. Return to main menu")
            choice = input("Enter your choice: ")
            if choice == '1':
                place_order(selected_customer[0])
            elif choice == '2':
                if not orders_by_cust(selected_customer[0]):  
                    continue 
            elif choice == '3':
                edit_customer(selected_customer[0])
            elif choice == '4':
                delete_customer(selected_customer[0])
            elif choice == '5':
                return
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

def main():

    print("\n\nWelcome to the Choc Shop!\n\n")

    login()

    print("\n\nWelcome to the Choc Shop!\n\n")

    while True:
        print("\n1. View chocolates")
        print("2. Place order")
        print("3. Add new customer")
        print("4. Search/Edit/Delete customer")
        print("5. View/Edit/Delete Orders")
        choice = input("Enter your choice (or 'q' to quit): ")
        if choice == '1':
            view_chocolates()
        elif choice == '2':
            place_order()
        elif choice == '3':
            add_customer()
        elif choice == '4':
            search_customer()
        elif choice == '5':
            view_orders()
        elif choice.lower() == 'q':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()