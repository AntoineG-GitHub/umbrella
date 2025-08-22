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



admin: antoine
pwd: 123456



to connect to EC instance:  ssh -i umbrella-key-ec2.pem ec2-user@51.21.224.128

python .\manage.py createsuperuser
ssh -i umbrella-key-ec2.pem ec2-user@51.21.224.128

docker build --rm -t umbrella-app:latest .

docker run -d --name umbrella-app-container -p 8000:8000   --env-file /home/ec2-user/umbrella_app/umbrella/.env   -v /home/ec2-user/umbrella_app/umbrella/database/db.sqlite3:/database/db.sqlite3   umbrella-app:latest
