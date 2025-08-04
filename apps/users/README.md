# User App Documentation

## Overview

The User App is designed to manage user-related operations within the system. It provides functionalities for user registration, authentication, profile management, and user data retrieval. The app ensures secure handling of user credentials.

## Features

- **User Registration:** Allows new users to create accounts with necessary validations.
- **Get a User:** Retrieve users with all its information.
- **Authentication:** Supports secure login and logout mechanisms using industry-standard practices.

## Models
### User
Represents a user in the system with fields for username, email, password, and other profile information. The password is stored securely using hashing techniques to ensure user security.

## API Endpoints

- **POST** `/users/add_user` - Register a new user.
- **POST** `/users/login_user` - Authenticate a user by returning a token if credentials are valid, else returns an error.
- **GET** `/users/get_user/<int:id>` - Retrieve user information by ID.

## Security

The password management and authentication is done through Django framework features, ensuring that user credentials are stored securely and that authentication processes are robust against common vulnerabilities. 

