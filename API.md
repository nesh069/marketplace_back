# Campus Marketplace API Documentation

## Base URL

```
http://localhost:8000/api/
```

---

## Authentication

Most endpoints require a JWT Bearer token. Follow these steps to authenticate:

### Step 1: Login to get tokens

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

Response:

```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Step 2: Use the access token

Include the access token in the Authorization header for all protected endpoints:

```bash
curl -X GET http://localhost:8000/api/listings/ \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Step 3: Refresh expired tokens

When the access token expires (after 1 hour), use the refresh token to get a new one:

```bash
curl -X POST http://localhost:8000/api/accounts/login/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}'
```

---

## Endpoints

### Auth

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/accounts/register/` | No | Create a new user account |
| POST | `/accounts/login/` | No | Get JWT access & refresh tokens |
| POST | `/accounts/login/refresh/` | No | Refresh an expired access token |

**Register Request:**

```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "phone": "254712345678"
}
```

### Listings

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/listings/` | No | Browse all listings |
| GET | `/listings/?search=phone&category=1` | No | Search & filter listings |
| POST | `/listings/` | Yes | Create a new listing |
| GET | `/listings/<id>/` | No | View a specific listing |
| PUT | `/listings/<id>/` | Yes | Update your listing |
| DELETE | `/listings/<id>/` | Yes | Delete your listing |

**Create Listing Request:**

```json
{
  "title": "iPhone 14 Pro",
  "description": "Brand new, sealed in box. 256GB. Color: Deep Purple.",
  "price": "999.99",
  "category": 1
}
```

### Categories

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/categories/` | No | Browse all categories |

### Favorites

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/favorites/` | Yes | View your saved listings |
| POST | `/favorites/` | Yes | Add a listing to favorites |
| DELETE | `/favorites/<id>/` | Yes | Remove from favorites |

**Add Favorite Request:**

```json
{
  "listing": 1
}
```

### Messages

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | `/messages/` | Yes | View your conversations |
| POST | `/messages/` | Yes | Send a message |

**Send Message Request:**

```json
{
  "recipient": 2,
  "listing": 1,
  "body": "Is this still available?"
}
```

### Payments (M-Pesa)

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/payments/pay/` | Yes | Initiate M-Pesa STK push |
| POST | `/payments/callback/` | No | M-Pesa callback URL (Safaricom calls this) |
| GET | `/payments/status/<id>/` | Yes | Check payment status |

**Initiate Payment Request:**

```json
{
  "listing_id": 1,
  "phone_number": "254708374149"
}
```

> **Note:** The phone_number must be in format `2547XXXXXXXX`. Safaricom's sandbox test number is `254708374149`.

---

## Auto-Generated API Docs

Once the server is running, you can also explore the API interactively:

| URL | Description |
|-----|-------------|
| `http://localhost:8000/api/schema/` | OpenAPI 3.0 JSON schema |
| `http://localhost:8000/api/docs/` | Swagger UI (interactive) |

---

## Complete Example: M-Pesa Payment Flow

```bash
# 1. Login and extract the access token
TOKEN=$(curl -s -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"

# 2. Initiate M-Pesa STK push
curl -X POST http://localhost:8000/api/payments/pay/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"listing_id":1,"phone_number":"254708374149"}'

# 3. Check payment status
curl -X GET http://localhost:8000/api/payments/status/1/ \
  -H "Authorization: Bearer $TOKEN"
```

---

## Environment Variables

Create a `.env` file in the project root:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=postgres://user:password@localhost:5432/marketplace

# CORS
FRONTEND_URL=http://localhost:5173

# M-Pesa Daraja API
MPESA_CONSUMER_KEY=your-daraja-consumer-key
MPESA_CONSUMER_SECRET=your-daraja-consumer-secret
MPESA_PASSKEY=your-passkey
MPESA_SHORTCODE=174379
MPESA_CALLBACK_URL=https://your-domain.com/api/payments/callback/
```

> **Never commit the `.env` file to Git.** It is already listed in `.gitignore`.

---

## Database Models (6 Schemas)

| Model | Description | Key Fields |
|-------|-------------|------------|
| User | Custom user account | username, email, phone, is_verified |
| Category | Product categories | name |
| Listing | Items for sale | seller, title, price, image, status |
| Favourite | Saved listings | user, listing |
| Message | User conversations | sender, recipient, listing, body |
| Transaction | Payment records | buyer, listing, amount, status, checkout_request_id |

---

## Testing

Run the test suite:

```bash
python manage.py test accounts.tests marketplace.tests payments.tests
```

Expected output:

```
Found 8 test(s).
.........
----------------------------------------------------------------------
Ran 8 tests in 2.4s

OK
```

---

## Docker

Build and run with Docker Compose:

```bash
docker compose up --build
```

This starts:
- PostgreSQL database on port 5432
- Django app on port 8000

---

## Tech Stack

- Python 3.14
- Django 6.0 / Django REST Framework
- JWT Authentication (`djangorestframework-simplejwt`)
- PostgreSQL (production) / SQLite (development)
- M-Pesa Daraja API (sandbox ready)
- `drf-spectacular` (OpenAPI docs / Swagger UI)
- Docker & Docker Compose
- GitHub Actions (CI)

---

## M-Pesa Integration Notes

The backend includes integration with the Safaricom M-Pesa Daraja API. To use the real M-Pesa API:

1. Register at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create a sandbox app
3. Copy your **Consumer Key** and **Consumer Secret** to `.env`
4. Update `MPESA_CALLBACK_URL` to a publicly accessible HTTPS URL (use ngrok for local testing)
5. Change `payments/mpesa.py` `BASE_URL` from sandbox to production when ready

**Safaricom Sandbox Test Number:** `254708374149`

---

## License

MIT
