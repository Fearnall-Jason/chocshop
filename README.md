# ChocShop

This repository contains the `chocshop.py` and `chocshop.sql` files, scripts for setting up and managing a database for a chocolate shop.

## Author
Jason Fearnall

## Date
5/16/2024

## Files

### chocshop.py

This Python script is part of a system for managing a chocolate shop. It contains several functions for interacting with the shop's database.

- `login()`: This function prompts the user to enter their email and password, and attempts to connect to the database using these credentials. It loops until a successful connection is made or the user enters 'q' to quit.

- `main()`: This function displays a menu of options for the user to choose from, including viewing chocolates, placing an order, adding a new customer, searching/editing/deleting a customer, and viewing/editing/deleting orders. It loops until the user enters 'q' to quit.

### chocshop.sql

The `chocshop.sql` script is designed to create and populate a MySQL database for a chocolate shop. It includes the creation of tables and insertion of sample data.

- `customer`: This table contains information about the customers, including the customer ID, name, email, phone number, address, and zip code. The `cust_id` field is an auto-incrementing integer that serves as the primary key.

- The script inserts sample data into the `customer` table. This data includes information about four customers: Jack B Nimble, Jack B Quick, Kandelle Stik, and Jumpin J Flash.

- The script uses transactions to ensure that the insertion of sample data is atomic. This means that if an error occurs during the insertion of data, all changes made during the transaction are rolled back, and the database remains in a consistent state.

## Usage

To use these scripts, you need to have Python and MySQL installed on your machine. You can run the `chocshop.py` script using a Python interpreter, and the `chocshop.sql` script using the MySQL command-line client or a MySQL GUI tool like MySQL Workbench.
