# Ecommerce Backend

A Django REST framework-based backend for an Ecommerce platform, featuring products, categories, orders, cart management, email notifications, caching, and background tasks with Celery.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Setup Instructions](#setup-instructions)
3. [Features](#features)
4. [API Documentation](#api-documentation)
5. [Testing](#testing)
6. [Deployment](#deployment)
7. [Technologies](#technologies)

---

## Project Overview

This project implements a complete backend for an ecommerce application with the following key components:

- User authentication (registration, login, password reset)
- Product & category CRUD operations
- User orders with checkout, payment, and cancellation
- Email notifications for order confirmation (via Celery)
- Redis caching for improved performance
- API documentation via Swagger/OpenAPI
- Unit and integration tests
- CI/CD pipeline with GitHub Actions

---

## Setup Instructions

### Prerequisites
- Docker & Docker Compose
- Python 3.11 (if running locally)
- Postman or a browser for API testing

### Clone the repository

```bash
git clone https://github.com/Lewis-Murimi/alx-project-nexus.git
cd ecommerce_backend
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=<your_django_secret_key>
DEBUG=True
DB_NAME=<your_db_name>
DB_USER=<your_db_user>
DB_PASSWORD=<your_db_password>
DB_HOST=localhost or <docker-compose service name>
DB_PORT=5432
EMAIL_HOST=<smtp_host>
EMAIL_PORT=<smtp_port>
EMAIL_HOST_USER=<email_user>
EMAIL_HOST_PASSWORD=<email_password>
```

### Start Docker containers

```bash
docker-compose up --build
```

- Django server: http://localhost:8000/
- Postgres: localhost:5432
- Redis: localhost:6379
- Celery worker logs: `docker-compose logs -f celery`

---

## Features

### User Authentication
- Registration, login, logout
- Password reset via email
- Profile management
- Token-based authentication (JWT)

### Products & Categories
- CRUD operations with admin-only permissions for create/update/delete
- Filtering, searching, and ordering
- Cached list/detail views for performance

### Orders
- Checkout with cart integration
- Payment simulation (mark as paid)
- Cancel pending orders
- Cached order lists & details

### Background Tasks
- Email notifications with Celery
- Asynchronous processing to avoid blocking requests

### Caching
- Redis caching for frequently accessed endpoints
- Cache invalidation after updates or deletes
- 10-minute TTL for cached data

### API Documentation
- Swagger UI and Redoc for interactive API docs

---

## API Documentation

Swagger/OpenAPI docs are automatically generated:

- Swagger UI: http://localhost:8000/swagger/
- Redoc: http://localhost:8000/redoc/
- JSON/YAML schema: http://localhost:8000/swagger.json

## API Reference

### User / Authentication Endpoints

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/auth/register/` | POST | Register a new user | `{"username":"john","email":"john@example.com","password":"strongpass123"}` | `{"id":1,"username":"john","email":"john@example.com"}` |
| `/api/auth/login/` | POST | Login user (returns JWT token or session info) | `{"username":"john","password":"strongpass123"}` | `{"access":"<jwt_token>","refresh":"<refresh_token>"}` |
| `/api/auth/logout/` | POST | Logout current user (invalidate token/session) | None | `204 No Content` |
| `/api/auth/user/` | GET | Get current authenticated user profile | None | `{"id":1,"username":"john","email":"john@example.com"}` |
| `/api/auth/user/` | PATCH | Update current user profile | `{"email":"newemail@example.com"}` | `{"id":1,"username":"john","email":"newemail@example.com"}` |
| `/api/auth/password/change/` | POST | Change user password | `{"old_password":"oldpass","new_password":"newpass123"}` | `204 No Content` |
| `/api/auth/password/reset/` | POST | Request password reset email | `{"email":"john@example.com"}` | `{"detail":"Password reset e-mail has been sent."}` |
| `/api/auth/password/reset/confirm/` | POST | Reset password using token | `{"uid":"<uid>","token":"<token>","new_password":"newpass123"}` | `204 No Content` |
 

### Category Endpoints
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/categories/` | GET | List all categories | None | `[{"id":1,"name":"Electronics"}]` |
| `/api/categories/` | POST | Create a new category (admin only) | `{"name": "Books"}` | `{"id":2,"name":"Books"}` |
| `/api/categories/{id}/` | GET | Retrieve a category by ID | None | `{"id":1,"name":"Electronics"}` |
| `/api/categories/{id}/` | PUT/PATCH | Update category (admin only) | `{"name":"Gadgets"}` | `{"id":1,"name":"Gadgets"}` |
| `/api/categories/{id}/` | DELETE | Delete category (admin only) | None | `204 No Content` |

### Product Endpoints
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/products/` | GET | List all products | None | `[{"id":1,"name":"Laptop","price":50000,"category":1}]` |
| `/api/products/` | POST | Create a new product (admin only) | `{"name":"Phone","price":30000,"category":1,"stock":50}` | `{"id":2,"name":"Phone","price":30000,"category":1,"stock":50}` |
| `/api/products/{id}/` | GET | Retrieve a product by ID | None | `{"id":1,"name":"Laptop","price":50000,"category":1,"stock":10}` |
| `/api/products/{id}/` | PUT/PATCH | Update product (admin only) | `{"price":45000}` | `{"id":1,"name":"Laptop","price":45000,"category":1,"stock":10}` |
| `/api/products/{id}/` | DELETE | Delete product (admin only) | None | `204 No Content` |

### Order Endpoints
| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `/api/orders/` | GET | List user orders | None | `[{"id":1,"total_price":2500,"status":"pending"}]` |
| `/api/orders/checkout/` | POST | Checkout cart and create order | `{"shipping_address":"123 Main St","payment_method":"credit_card"}` | `{"id":1,"total_price":2500,"status":"pending","items":[{"product":5,"quantity":2,"price":1250}]}` |
| `/api/orders/{id}/` | GET | Retrieve order by ID | None | `{"id":1,"total_price":2500,"status":"pending","items":[{"product":5,"quantity":2,"price":1250}]}` |
| `/api/orders/{id}/update/` | PATCH | Update order (partial, pending only) | `{"shipping_address":"456 New St"}` | `{"id":1,"total_price":2500,"status":"pending"}` |
| `/api/orders/{id}/cancel/` | POST | Cancel a pending order | None | `{"detail":"Order cancelled successfully."}` |
| `/api/orders/{id}/pay/` | POST | Pay a pending order | None | `{"detail":"Payment successful."}` |

## Notes

- All endpoints require authentication unless stated otherwise.  
- Use JWT tokens in `Authorization: Bearer <token>` header for protected endpoints.  
- Examples are simplified; actual responses may include nested objects (e.g., order items, product details).  
- Cached list/detail views improve performance (10 min TTL).


---

## Testing

Run unit and integration tests with pytest:

```bash
docker-compose exec web pytest
```

All tests use `pytest-django` and can be run inside Docker or locally.

Tests cover orders, products, caching, and permissions.

---

## Deployment

### Docker

Build and start containers:

```bash
docker-compose up --build -d
```

### Cloud Deployment

- Push Docker image to Render/Heroku/Docker Hub
- Configure environment variables
- Expose port 8000 for Django and `/swagger/` for API docs

---

## CI/CD

GitHub Actions automatically runs tests and linting on push and pull requests.

Pipeline defined in `.github/workflows/ci.yml`

---

## Technologies

- Django & Django REST Framework
- PostgreSQL
- Redis (caching & Celery broker)
- Celery & Flower (for background tasks)
- Swagger/OpenAPI (drf-yasg)
- Pytest (testing)
- Docker & Docker Compose
- GitHub Actions (CI/CD)
