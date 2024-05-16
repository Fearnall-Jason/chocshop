# chocshop

# ChocShop SQL

This repository contains the `chocshop.sql` file, a script for setting up and populating a database for a chocolate shop.

## Author
Jason Fearnall

## Date
5/16/2024

## File
`chocshop.sql`

## Description

The `chocshop.sql` script is designed to create and populate a MySQL database for a chocolate shop. It includes the creation of tables and insertion of sample data.

### Database

The script first creates a database named `chocshop` if it does not already exist, and then sets it as the active database.

### Tables

The script creates the following table:

- `customer`: This table contains information about the customers, including the customer ID, name, email, phone number, address, and zip code. The `cust_id` field is an auto-incrementing integer that serves as the primary key.

### Sample Data

The script inserts sample data into the `customer` table. This data includes information about four customers: Jack B Nimble, Jack B Quick, Kandelle Stik, and Jumpin J Flash.

### Transactions

The script uses transactions to ensure that the insertion of sample data is atomic. This means that if an error occurs during the insertion of data, all changes made during the transaction are rolled back, and the database remains in a consistent state.

## Usage

To use this script, you need to have MySQL installed on your machine. You can then run the script using the MySQL command-line client or a MySQL GUI tool like MySQL Workbench.
