# Present Pickz

A premium gifting and collectibles e-commerce platform built with Django.

## Tech Stack

- **Backend:** Django 6.0, Python 3.12
- **Database:** PostgreSQL (production), SQLite (development)
- **Auth:** Django Allauth (Email + Google OAuth)
- **Payments:** Cashfree Integration
- **Static Files:** WhiteNoise

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## Environment Variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your-secret-key
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Project Structure

```
presentpickz/
├── core/           # Homepage, static assets
├── products/       # Product catalog, categories, reviews
├── orders/         # Order management, tracking
├── users/          # Authentication, profiles, wishlist
├── cart/           # Shopping cart
└── templates/      # Base templates
```

## License

All rights reserved © 2026 Present Pickz.
