# LitRevue - Book Review Platform

LitRevue is a Django-based web application that allows users to create and share book reviews. Users can follow each other, create tickets for book review requests, and write reviews.

## Prerequisites

- Python 3.x
- Django 5.0.2
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup Commands

### 1. Create Admin User
To create a superuser (admin) account:
```bash
python manage.py createsuperuser
```
Follow the prompts to set username, email, and password.

### 2. Run Migrations
To set up or update the database schema:
```bash
python manage.py migrate
```

### 3. Populate Sample Data
To populate the database with sample data (users, tickets, and reviews):
```bash
python manage.py generate_sample_data
```
This will create:
- Test users (alice, bob, charlie, david) with password: password123
- Sample book tickets
- Sample reviews
- User follow relationships

## Development Server

To run the development server:
```bash
python manage.py runserver
```
The application will be available at `http://127.0.0.1:8000`

## Project Structure

- `litrevu/` - Main application directory
  - `models.py` - Database models (User, Ticket, Review, UserFollows)
  - `views.py` - View logic
  - `forms.py` - Form definitions
  - `urls.py` - URL routing
  - `management/commands/` - Custom management commands
- `config/` - Project configuration
  - `settings.py` - Django settings
  - `urls.py` - Project URL configuration

## Features

- User authentication and registration
- Create and manage book review tickets
- Write reviews for tickets
- Follow other users
- Feed showing followed users' activity
- Admin interface for content management

## Admin Interface

Access the admin interface at `http://127.0.0.1:8000/admin` using your superuser credentials.

## Important Settings

- Debug mode is enabled by default (disable in production)
- Uses SQLite as the default database
- Media files are stored in `media/`
- Static files are stored in `static/`
- French localization is enabled by default

## Security Notes

- Debug mode should be disabled in production
- `SECRET_KEY` should be changed in production
- CSRF and session settings should be reviewed for production deployment 