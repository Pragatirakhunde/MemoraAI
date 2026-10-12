# PayFlow Architecture

## High-Level Flow

Customer
    ?
React Frontend
    ?
FastAPI API
    ?
Application Services
    ?
Repositories
    ?
PostgreSQL

Payment processing may also interact with:

FastAPI
    ?
Redis
    ?
Background notification / asynchronous jobs

## Core Backend Modules

- authentication
- users
- customers
- payments
- transactions
- refunds
- invoices
- notifications

## Core Relationships

Customer
    ?
Payment
    ?
Transaction

Payment
    ?
Refund

Customer
    ?
Invoice
