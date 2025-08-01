# Data Ingestion App

## Overview
The `data_ingestion` app is responsible for fetching, processing, and storing financial data, including stock prices, exchange rates, and company information. It integrates with external APIs (e.g., Alpha Vantage and Yahoo Finance) and provides a structured way to manage historical data for analysis and portfolio valuation.

## Features
- **Historical Price Management**: Fetch and store daily OHLCV (Open, High, Low, Close, Volume) data for financial instruments.
- **Exchange Rate Management**: Fetch and store daily exchange rates between currencies.
- **Company Information**: Store detailed company metadata, including sector, industry, and financial ratios.

# SRC folder
The source folder contains the main application logic divided into three modules:
1. The API client (Alpha Vantage and yFinance): It handles the API requests to fetch financial data based on the relevant API. 
2. The database_handler: It manages the database operations which is saving to the database and checking if the table already exists.
3. The stock_price_service: It handles the raw data from the API client and post process it to add euro values to save it to the final table. 

Note : The readers file are used to read the data from the database and return it in a structured format. This is for the get-prices, get-exchange-rates requests.

The logic is to instantiate the api client and the database handler to give it to the stock_price_service. The stock_price_service will then use the api client to fetch the data and the database_handler to save it to the database.

## Models
### HistoricalPrice
Tracks daily OHLCV data for financial instruments, including values in the original currency and EUR equivalent.

### BaseHistoricalExchangeRate
Stores daily exchange rate data between two currencies, including OHLC values.

### TickerInfo
Contains metadata about financial instruments, such as name, sector, industry, and various financial ratios.

## API Endpoints
### Stock Price Data
- **Fetch and Save Data**: `/fetch_and_save_data/<str:ticker>/`
- **Get Prices**: `/get_prices/<str:ticker>/`

### Exchange Rate Data
- **Fetch and Save Exchange Rates**: `/fetch_and_save_data_exchange_rate/<str:from_currency>/`
- **Get Exchange Rates**: `/get_exchange_rates/<str:from_currency>/`

### Company Information
- **Fetch and Save Stock Info**: `/fetch_and_save_stock_info/<str:ticker>/`
- **Get Company Info**: `/get_company_info/<str:ticker>/`

## Admin Panel
The app provides an admin interface for managing data:
- **HistoricalPriceAdmin**: View and filter historical price data.
- **BaseHistoricalExchangeRateAdmin**: Manage exchange rate data.
- **TickerInfoAdmin**: View and edit company metadata.

## Testing
The app includes unit tests for key functionalities:
- **TestStockPriceService**: Validates the saving of stock prices in different currencies.
- **TestExchangeRateService**: Ensures exchange rate data is fetched and stored correctly.

You can run the tests using the Django management command:
```bash
python manage.py test data_ingestion
```

## Dependencies
- Django
- Alpha Vantage API
- yFinance (optional for additional data sources)
