# Secure Transactions API — Security Overview

This API is designed with security best practices for user authentication and transaction management.

## Key Security Choices

Password Hashing: 
  User passwords are hashed using bcrypt via Passlib before storage, protecting against credential theft.

JWT Authentication: 
  Login returns a short-lived JWT token. All protected endpoints require a valid token, preventing unauthorized access.

Role-Based Access Control: 
  The first registered user is assigned the `admin` role, all others are `user`. Admins can access all transactions, while users can only access their own.

SQL Injection Protection:  
  All database operations use SQLAlchemy ORM, which automatically parameterizes queries and prevents SQL injection.

Input Validation:  
  Pydantic models enforce strict validation on all incoming data (e.g., email format, password length, currency code), reducing risk of malformed or malicious input.

XSS Mitigation:  
  Transaction descriptions are sanitized using the `bleach` library, removing any potentially harmful HTML or scripts.

CORS Policy:  
  CORS middleware is enabled but locked down by default, preventing cross-origin requests unless explicitly allowed.

Error Handling:  
  Structured HTTP errors and a global exception handler ensure that sensitive details are not leaked to clients.

---
Summary: 
These choices help protect user data, prevent common web vulnerabilities and ensure robust secure API