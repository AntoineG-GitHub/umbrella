# Transaction App Documentation

## Overview
The `transactions` app is a core component of the Umbrella project, responsible for managing portfolio transactions. It provides APIs and utilities for creating, updating, querying, and reporting on transactions within the system.

The transactions can be of all types being fees, dividends, buy and sell of stocks, deposits and withdrawals. 

## Features
- **Add a transaction:** Add new transactions with details such as amount, date, type, and description. It's impotrtant to have users in the system before add deposits for them as it's a requirement for the transaction to have a user_id.
- **Get a transaction:** Retrieve lists of transactions with filtering and sorting options.
- **Delete a transaction:** Remove transactions from the system.

## Models 
### Transaction
Represents a financial transaction with fields for amount, date, type (e.g., buy, sell, fee, dividends, deposit, withdrawal), user_id, shares, ticker, currency. 


## API Endpoints
### Add a Transaction
- **POST** `/add_transaction/`
  - Adds a new transaction to the system.
  - Request body should include `amount`, `date`, `type`, `description`, and optional fields like `shares`, `ticker`, and `currency`.
### Get Transactions
- **GET** `/get_transaction/`
  - Retrieves a list of transactions.
  - Supports filtering by `type`, `date`, and `ticker`.
  - Supports pagination and sorting.
### Delete a Transaction
- **DELETE** `/delete_transaction/<int:id>/`
  - Deletes a transaction by its ID.


