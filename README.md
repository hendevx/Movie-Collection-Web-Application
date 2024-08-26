# Movie Collection Web Application

## Description

This Django web application allows users to create collections of movies they like, leveraging a third-party movie listing API. It includes functionalities for user registration, JWT authentication, and CRUD operations on movie collections. Additionally, a custom middleware tracks and counts the number of requests to the server, with APIs to view and reset the count.

## Features

- **User Registration and Authentication**: Users can register and authenticate using JWT tokens.
- **Movie Listing**: Integrates with a third-party API to list movies.
- **CRUD Operations**: Users can create, view, update, and delete collections of movies.
- **Request Counter Middleware**: A middleware to count and monitor the number of requests to the server, with APIs to view and reset the count.

## Setup

### Prerequisites

- Python 3.12.4
- Django 5.1
- `requests` library for API integration
- `djangorestframework` for building RESTful APIs
- `djangorestframework-simplejwt` for JWT authentication
- `mysqlclient` for database connectivity
- `django-environ` for os environment variables

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/movie-collection-app.git
    cd movie-collection-app
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following:

    ```env
    MOVIE_API_USERNAME=<username>
    MOVIE_API_PASSWORD=<password>
    ```

5. **Apply migrations:**

    ```bash
    python manage.py migrate
    ```

6. **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## API Endpoints

- **User Registration**: `POST /register/`
- **Movies List**: `GET /movies/`
- **Create Collection**: `POST /collection/`
- **View Collection**: `GET /collection/<collection_uuid>/`
- **Update Collection**: `PUT /collection/<collection_uuid>/`
- **Delete Collection**: `DELETE /collection/<collection_uuid>/`
- **Request Count**: `GET /request-count/`
- **Reset Request Count**: `POST /request-count/reset/`


## Acknowledgments

- [Django](https://www.djangoproject.com/) for the web framework.
- [djangorestframework](https://www.django-rest-framework.org/) for building RESTful APIs.
- [Requests](https://requests.readthedocs.io/en/latest/) for HTTP requests.
