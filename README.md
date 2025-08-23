# Umbrella project
This project aims to create the backend of the Umbrella project which is a software build to follow our investments over time. 
This backend is build on the django framework where you have a folder apps that contains all the services that make the backend work as it should. 

Here are the different apps: 
- Data Ingestion: Apps that serves the purpose of ingesting the data into tables. 
- Portfolio Vluation: All the logic to value the portfolio.
- Transactions: All the logic to handle transactions of the fund (buy, sells, deposits, withdrawals, etc) 
- Users: All the logic to handle users (login, signup, permissions, etc)

## Set up
Before running the project, you need to activate the environement specified in the pyproject.toml file. 

## How to run the project? 

Once the poetry environement is ready, you can run the django server.

- python manage.py makemigrations: Creates migration files based on model changes.
- python manage.py migrate: Applies migration files to update the database schema.
- python manage.py runserver: Starts the local development server.

## Needed commands
### Django commands

Create a super user: python .\manage.py createsuperuser

### EC2 commands
To connect to EC instance:  ssh -i umbrella-key-ec2.pem ec2-user@51.21.224.128
Build the image: docker compose build
Start in background: docker compose up -d
View logs: docker compose logs -f
Restart after updating code: docker compose up -d --build
Stop the containers: docker compose down
