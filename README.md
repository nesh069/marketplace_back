# Campus Marketplace — Backend

Django REST API for a student marketplace with M-Pesa STK push payments.

## Stack

- Python 3.14, Django 6.0, DRF 3.17
- PostgreSQL (production) / SQLite (development)
- JWT auth via `djangorestframework-simplejwt`
- M-Pesa Daraja API (sandbox)
- API docs via `drf-spectacular` (OpenAPI 3 + Swagger UI)
- Docker & docker-compose

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your M-Pesa sandbox creds
python manage.py migrate
python manage.py runserver
```

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/accounts/register/` | POST | No | Create account |
| `/api/accounts/login/` | POST | No | Get JWT tokens |
| `/api/accounts/login/refresh/` | POST | No | Refresh JWT |
| `/api/listings/` | GET/POST | Read-only/Yes | Browse & create listings |
| `/api/listings/<id>/` | GET/PUT/DELETE | Yes | Listing detail, update, delete |
| `/api/categories/` | GET | No | List categories |
| `/api/favorites/` | GET/POST | Yes | List & add favorites |
| `/api/favorites/<id>/` | DELETE | Yes | Remove favorite |
| `/api/messages/` | GET/POST | Yes | Messages |
| `/api/payments/pay/` | POST | Yes | Initiate M-Pesa STK push |
| `/api/payments/status/<id>/` | GET | Yes | Check payment status |
| `/api/schema/` | GET | No | OpenAPI schema |
| `/api/docs/` | GET | No | Swagger UI docs |

## Testing

```bash
python manage.py test accounts.tests marketplace.tests payments.tests -v 2
```

## Docker

```bash
docker compose up --build
```

## CI

GitHub Actions workflow at `.github/workflows/django.yml` runs tests on push/PR to `main` and `dev`.
