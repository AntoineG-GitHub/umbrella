# Umbrella project
This project aims to create the backend of the Umbrella project which is a software build to follow our investments over time. 
This backend is build on the django framework where you have a folder apps that contains all the services that make the backend work as it should. 

Here are the different apps: 
- Data Ingestion: Apps that serves the purpose of ingesting the data into tables. The tables are hosted as SQLite databases.
The trigger to ingest those tables hsould never come from the front end. All endpoints triggered to feed the tables should be carefully deployed and scheduled
so the frontend can use the unedrlying tables to feed the dashboard. 

- Data Queries: All the get queries necessary for the front end. 

## Set up
Before running the project, you need to activate the environement specified in the pyprject.toml file. 
In my personal laptop, : conda activate umbrella

When install from poetry inside a conda env, poetry is usnig the conda env and doe not recreate an env on top. 

## How to run the project? 

python manage.py makemigrations: Creates migration files based on model changes.
python manage.py migrate: Applies migration files to update the database schema.
python manage.py runserver: Starts the local development server.

### Notes

Everytime I create a new app by runnning django startapp new_app, I have to regsiter it in the settings of my webapp. 
Otherwise it does not install that app.  In my case, my apps are histrical_prices, ticker_info.

Every data request goes by the views first. It takes the request and returns the response. It's a request handler. (views is missleading)
Every function in views should be mapped to a url. Inside your app, you should have a url file to edfine the route of the urls for your app.
Inside the general folder, you should mention the route of your app. 

So now, whenever you call a url, it basically a request for whatever should happen with that url. And whatver should happened is define in the function linked to that url. You can then send html data or just save data, fecth data, whatever. 

The function saves_daily_prices can't return data as it needs to be triggered every day without returning data, just for update. 
We need another function with the whole purpose of fetching and returning the data


### Unit based Accounting

What You Track:
- The total value of the portfolio at any given point.
- The units of the fund issued to each person when they deposit.
- The price per unit changes as the portfolio's total value changes.
- When someone withdraws, they “sell” units at the current unit price.

1. Initialize the portfolio
Let’s say:
 - Total portfolio value is €0.
 - No units exist.

2. First deposit
A adds 100€ in the portfolio
- set initial price of 1€/unit 
- A gets 1000 units in the portfolio 
    - Total portfolio value : 1000€
    - Total units: 1000

3. Second deposit
Value before the deposit:
- unit price : 1.10€
- total portfolio value: 1100€ 
- total units: 1000
Person B adds 500€ (after th portfolio grew to 1100€):
- total portfolio value: 1600€
- B gets 500€/1.10€ ~=454.55 units 
- total units: 1454.55
- price/units = 1.10€

4. Portfolio grows to 1800€
Value update:
- total units: 1454.55
- total value: 1800€ 
- unit price: 1800/1454.55 ~= 1.237€

5. Person A withdraws  618.50€
- unit price = 1.237€
- A wants 618.50€ -> 618.50/1.237 ~= 500 units 
- A owns 500 units and B 454.55 units
- new portfolio value: 1181.50€
- total units: 954.55

Your system is event-driven, but valuations are time-driven.

Even if no transaction happened that day (no buys, sells, deposits, etc.), the market prices could have changed → so portfolio value changes anyway.

You want to track:

the portfolio value daily 📈,

the units price daily 📊,

and thus the shares of each user daily 📅.

👉 So you must generate a new valuation snapshot every single day, even if there was no action.


admin: antoine
pwd: 123456


Next steps:
- review the gain loss function
- create test sets for withdrawal (can be created manually)
- NO NEGATIVE UNITS IN TRANSACTION TABLE
