# PayFlow Business Rules

## Payment Validation

A payment must pass validation before processing.

Validation may include:

- customer status
- payment amount
- supported payment method
- transaction status
- configured transaction limits

## Transaction

A successful payment creates a transaction record.

A failed payment must retain an appropriate failure state.

## Refund

A refund can only be processed for an eligible transaction.

Refund processing must not create a second successful refund
for the same refundable transaction.

## Invoice

Invoices are associated with customers and payment activity.

## Notifications

Important payment events may create notification jobs.
