# PayFlow API

Planned API groups:

## Authentication

POST /api/v1/auth/login
POST /api/v1/auth/register

## Customers

GET /api/v1/customers
GET /api/v1/customers/{customer_id}

## Payments

POST /api/v1/payments
GET /api/v1/payments/{payment_id}

## Transactions

GET /api/v1/transactions
GET /api/v1/transactions/{transaction_id}

## Refunds

POST /api/v1/refunds
GET /api/v1/refunds/{refund_id}

## Invoices

POST /api/v1/invoices
GET /api/v1/invoices/{invoice_id}

These endpoints are part of the planned project structure and
will be implemented incrementally.
