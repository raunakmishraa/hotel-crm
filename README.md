# Hotel Platform + CRM — Django Prototype

A working hotel booking + CRM prototype built with Python/Django and SQLite.

## Architecture

```text
Browser
  ├── Hotel Website (Django templates + CSS/JS)
  │     ├── Sign up / Login
  │     ├── Room search
  │     └── Booking
  │
  └── CRM (protected Django views)
        ├── Dashboard
        ├── Reservations
        ├── Guests
        └── Rooms

Django
  ├── HTML pages
  ├── Session authentication
  ├── JSON API (/api/v1/)
  └── SQLite database
```

The UI is intentionally restrained and hotel-specific: operational tables, clear status colors, minimal decorative cards, and no AI-style gradients.

## Run locally

Requirements: Python 3.11+ recommended.

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Demo accounts

- Staff / CRM: `admin@harborhouse.test` / `Admin123!`
- Guest: `guest@example.com` / `Guest123!`

The demo seed is safe to run repeatedly.

## Main routes

- `/` — hotel home
- `/rooms/` — room availability/search
- `/signup/` — guest registration
- `/login/` — login
- `/bookings/` — signed-in guest bookings
- `/crm/` — CRM dashboard
- `/api/v1/hotel/` — hotel configuration JSON
- `/api/v1/rooms/` — rooms JSON
- `/api/v1/bookings/` — authenticated booking API
- `/api/v1/guests/` — CRM guest API

## Data configuration

Hotel identity/contact/about details are centralized in `backend/hotel/fixtures/hotel_data.json` and loaded into the `HotelProfile` database record by `seed_demo`.

That means HTML does not need to contain the hotel's business contact details. Change the fixture and rerun:

```bash
python manage.py seed_demo
```

For production, the same `HotelProfile` record can be managed from the Django admin or replaced by a separate CRM API.

## Production direction

For the final deployment, split the public website and CRM into separate deployable services:

```text
hotel-web
   -> HTTPS /api/v1
hotel-api
   -> PostgreSQL
   -> CRM / PMS integrations
```

This prototype keeps them in one repository so it can be run immediately.
