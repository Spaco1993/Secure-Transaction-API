# Secure Transactions API

A robust, secure RESTful API for managing user accounts and financial transactions, built with FastAPI.  
Implements modern authentication, role-based access control and strong input validation.

---

## Features

- **User Authentication:**  
  - Passwords securely hashed with bcrypt (`passlib`).
  - JWT-based login with OAuth2 bearer tokens and token expiry.

- **Role-Based Access Control (RBAC):**  
  - First registered user is `admin`; others are regular `user`.
  - Admins can view and manage all transactions; users can only access their own.

- **Transactions CRUD:**  
  - Create, read, update, and delete transactions.
  - Each transaction includes: amount, currency (ISO 4217, e.g., `USD`), and description.

- **Security:**  
  - SQL injection protection via SQLAlchemy ORM.
  - XSS mitigation: transaction descriptions sanitized with `bleach`.
  - Input validation with Pydantic (amount > 0, currency format, description length).

- **Error Handling:**  
  - Structured HTTP errors and a global exception handler.

- **CORS:**  
  - Middleware included; origins locked down by default.

- **Database:**  
  - SQLite for local development; easily switch to PostgreSQL for production.

---

## Quick Start

```sh
# Clone and enter the project directory
cd Part1_SecureAPI

# Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
set PYTHONPATH=%cd% && uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API documentation.

---

## Authentication Flow (Example)

```sh
# Register a new user (first user becomes admin)
curl -X POST http://127.0.0.1:8000/register \
     -H "Content-Type: application/json" \
     -d '{ "email": "admin@example.com", "password": "Str0ngPassw0rd!" }'

# Login and get a JWT token
curl -X POST http://127.0.0.1:8000/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d 'username=admin@example.com&password=Str0ngPassw0rd!'

# Use the token to create a transaction
curl -X POST http://127.0.0.1:8000/transactions \
     -H "Authorization: Bearer <ACCESS_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{ "amount": 120.5, "currency": "USD", "description": "Monthly subscription" }'

# List transactions
curl -H "Authorization: Bearer <ACCESS_TOKEN>" http://127.0.0.1:8000/transactions
```

---

## Security Highlights

- **Password Hashing:**  
  - Uses bcrypt to store passwords securely.

- **JWT Authentication:**  
  - Short-lived tokens; supports OAuth2 flows.

- **RBAC:**  
  - Admins have full access; users restricted to their own data.

- **SQL Injection Protection:**  
  - All queries use SQLAlchemy ORM.

- **Input Validation:**  
  - Pydantic enforces strict types and constraints.

- **XSS Mitigation:**  
  - All transaction descriptions are sanitized.

- **CORS:**  
  - Deny-all by default; configure trusted origins for production.

- **Transport Security:**  
  - Always use HTTPS in production.

---

## API Endpoints

- `POST /register` — Register a new user
- `POST /login` — Login and receive JWT token
- `GET /me` — Get current user info
- `POST /transactions` — Create a transaction
- `GET /transactions` — List transactions
- `GET /transactions/{tx_id}` — Get a transaction by ID
- `PUT /transactions/{tx_id}` — Update a transaction
- `DELETE /transactions/{tx_id}` — Delete a transaction

See [Swagger UI](http://127.0.0.1:8000/docs) for full details.

---

## License

MIT License

---

## 