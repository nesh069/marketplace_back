# Marketplace API Documentation

## Base URL

http://localhost:8000/api/

## Authentication

All endpoints require JWT token in header:
Authorization: Bearer <access_token>

## Endpoints

### Auth
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register/` | Create account | No |
| POST | `/auth/login/` | Get JWT tokens | No |
| POST | `/auth/refresh/` | Refresh token | No |

### Listings
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/listings/` | Browse all | No |
| GET | `/listings/?search=phone` | Search | No |
| POST | `/listings/` | Create | Yes |
| GET | `/listings/<id>/` | Detail | No |
| PUT | `/listings/<id>/` | Update | Yes |
| DELETE | `/listings/<id>/` | Delete | Yes |

### Favorites
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/favorites/` | My favorites | Yes |
| POST | `/favorites/` | Add | Yes |
| DELETE | `/favorites/<id>/` | Remove | Yes |

### Messages
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/messages/` | Conversations | Yes |
| POST | `/messages/` | Send | Yes |

### Payments
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/payments/initiate/` | Start M-Pesa | Yes |
| POST | `/payments/callback/` | Callback | No |
| GET | `/payments/status/<id>/` | Check status | Yes |

## Models (5+ Schemas)
1. **User** - email, phone, is_verified 
2. **Category** - name, slug
3. **Listings** - seller, title, price, image, status
4. **Favourite** - user, listing
5. **Message** - sender, recipient, listings, content
6. **Transaction** - buyer, listing, amount, status, mpesa_receipt
