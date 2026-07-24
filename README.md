# Campus Marketplace — Backend

Django REST API for a student marketplace with Pesapal payment integration.

## Stack

- Python 3.14, Django 6.0, DRF 3.17
- PostgreSQL (production) / SQLite (development)
- JWT auth via `djangorestframework-simplejwt`
- Pesapal API (sandbox / production)
- Cloudinary (optional — image upload)
- API docs via `drf-spectacular` (OpenAPI 3 + Swagger UI)
- Whitenoise (serves admin static files in production)

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Pesapal sandbox creds
python manage.py migrate
python manage.py runserver
```

## API Endpoints

### Auth
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/accounts/register/` | POST | No | Create account |
| `/api/accounts/login/` | POST | No | Get JWT tokens |
| `/api/accounts/login/refresh/` | POST | No | Refresh JWT |

### Marketplace
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/listings/` | GET/POST | Read-only/No | Browse (public) & create listings |
| `/api/listings/<id>/` | GET/PUT/DELETE | Read-only/No | Listing detail (public), update, delete |
| `/api/listings/<id>/mark_sold/` | PATCH | Yes | Seller marks item as sold |
| `/api/listings/<id>/report/` | POST | Yes | Report a listing |
| `/api/listings/favourites/` | GET | Yes | User's favourited listings |
| `/api/categories/` | GET | No | List categories |
| `/api/favorites/` | GET/POST | Yes | List & add favourites (blocks self-favourite, duplicate) |
| `/api/favorites/<id>/` | DELETE | Yes | Remove favourite |
| `/api/messages/` | GET/POST | Yes | Messages (blocks self-message) |
| `/api/reports/` | GET/POST | Yes | List & create reports (staff sees all, blocks self-report) |

### Payments
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/payments/pay/` | POST | Yes | Initiate Pesapal payment (blocks self-buy, sold listings) |
| `/api/payments/callback/` | GET/POST | No | Pesapal IPN callback + browser redirect |
| `/api/payments/status/<id>/` | GET | Yes | Check payment status (syncs cancelled/failed from Pesapal) |

### Docs
| `/api/schema/` | GET | No | OpenAPI schema |
| `/api/docs/` | GET | No | Swagger UI docs |

## Database Schema

**7 Models:**
1. **User** — Custom auth with email, phone (unique email, username)
2. **Category** — Product categories
3. **Listing** — Items for sale (FK: seller, category), title 3–120 chars, price ≥ 1
4. **Favourite** — Saved listings (FK: user, listing, unique together)
5. **Message** — Conversations (FK: sender, recipient, listing), body ≥ 1 char
6. **Report** — Listing reports (FK: reporter, listing, reason choices)
7. **Transaction** — Payments (FK: listing, buyer), phone normalized to 254XXXXXXXXX

## Key Validations

- **Phone numbers:** accepts `07XXXXXXXX`, `01XXXXXXXX`, `2547XXXXXXXX`, `+2547XXXXXXXX`, `2541XXXXXXXX`, `+2541XXXXXXXX`; stored as `254XXXXXXXXX` (normalized)
- **Self-actions blocked:** cannot buy own listing, message self, favourite own, report own
- **Duplicate favourite:** prevented server-side
- **Sold listings:** cannot be purchased

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SECRET_KEY` | Yes | Django secret key |
| `DATABASE_URL` | No | Defaults to SQLite |
| `PESAPAL_CONSUMER_KEY` | Yes | Pesapal API key |
| `PESAPAL_CONSUMER_SECRET` | Yes | Pesapal API secret |
| `PESAPAL_CALLBACK_URL` | Yes | Backend callback URL |
| `PESAPAL_IPN_ID` | Yes | Pesapal IPN registration ID |
| `FRONTEND_URL` | Yes | Frontend URL for redirect |
| `CLOUDINARY_CLOUD_NAME` | No | Cloudinary (image upload) |
| `CLOUDINARY_API_KEY` | No | Cloudinary (image upload) |
| `CLOUDINARY_API_SECRET` | No | Cloudinary (image upload) |

## Testing

```bash
python manage.py test -v 2
```

## CI

GitHub Actions workflow at `.github/workflows/django.yml` runs tests on push/PR to `main` and `dev`.
