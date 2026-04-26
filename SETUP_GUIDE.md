# Authentication Integration Guide

This guide documents the new auth system with role-based users for this project.

## 1) What was implemented

- Full pages:
  - `/login/`
  - `/register/`
  - `/courier-dashboard/` (placeholder)
- Navbar auth state:
  - Logged out: shows `Register` and `Login`
  - Logged in: shows `Logout`
- Role-aware registration:
  - `Customer` and `Courier` supported from the frontend
- API endpoints:
  - `POST /api/register/`
  - `POST /api/login/`
  - `POST /api/logout/`
- Existing versioned API is still available:
  - `/api/v1/users/register/`
  - `/api/v1/users/login/`
  - `/api/v1/users/logout/`

## 2) Backend details

### Register

Endpoint: `POST /api/register/`

Request:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "StrongPass123",
  "confirm_password": "StrongPass123",
  "role": "customer"
}
```

Notes:
- `role` can be `customer` or `courier` from UI.
- `customer` is normalized to the internal `user` role.
- Response includes `user`, `access`, and `refresh` tokens.

### Login

Endpoint: `POST /api/login/`

Request supports username/email/phone through one field:

```json
{
  "identifier": "john_doe",
  "password": "StrongPass123"
}
```

You can pass email or phone in `identifier` as well.

### Logout

Endpoint: `POST /api/logout/`

Headers:
- `Authorization: Bearer <access_token>`

Body:

```json
{
  "refresh": "<refresh_token>"
}
```

Refresh token is blacklisted when provided.

## 3) Frontend behavior

- `static/js/auth.js` handles:
  - login submit
  - register submit
  - token storage in `localStorage`
  - logout request and local token cleanup
  - navbar auth toggling
  - role-based redirect:
    - `courier` -> `/courier-dashboard/`
    - others -> `/`
- Unauthorized access guard:
  - `/courier-dashboard/` redirects to `/login/` if not authenticated
  - non-courier users are redirected to `/`

## 4) Files changed

- Backend:
  - `apps/users/models.py`
  - `apps/users/serializers/v1.py`
  - `apps/users/views/v1.py`
  - `apps/users/urls/v1.py`
  - `core/urls.py`
- Frontend:
  - `templates/index.html`
  - `templates/login.html`
  - `templates/register.html`
  - `templates/courier_dashboard.html`
  - `static/js/auth.js`
  - `static/css/styles.css`

## 5) Run and verify

1. Run server:
   - `python manage.py runserver`
2. Open:
   - `http://127.0.0.1:8000/register/`
3. Register as `Customer` and login.
4. Confirm navbar switches to `Logout`.
5. Logout and login again as `Courier`.
6. Confirm redirect goes to `/courier-dashboard/`.
7. Test API directly (optional) with Postman/curl using `/api/register/`, `/api/login/`, `/api/logout/`.

## 6) Production notes

- JWT is already configured with SimpleJWT.
- For stricter production security, consider:
  - moving tokens to secure HTTP-only cookies,
  - tightening CORS,
  - shorter access token lifetime,
  - rate-limiting login/register endpoints.
