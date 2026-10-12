from decimal import Decimal

import pytest

from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService


def create_service():
    repository = PaymentRepository()
    return PaymentService(repository)


def test_successful_payment():
    service = create_service()

    payment = service.create_payment(
        payment_id=1,
        customer_id=101,
        invoice_id=5001,
        amount=Decimal("1499.00"),
        method="upi",
    )

    assert payment.status == "success"
    assert payment.transaction_id == "TXN-000001"


def test_invalid_payment_amount():
    service = create_service()

    with pytest.raises(ValueError):
        service.create_payment(
            payment_id=2,
            customer_id=101,
            invoice_id=5002,
            amount=Decimal("0"),
            method="upi",
        )


def test_invalid_payment_method():
    service = create_service()

    with pytest.raises(ValueError):
        service.create_payment(
            payment_id=3,
            customer_id=101,
            invoice_id=5003,
            amount=Decimal("500"),
            method="cash",
        )


def test_failed_payment():
    service = create_service()

    service.create_payment(
        payment_id=4,
        customer_id=102,
        invoice_id=5004,
        amount=Decimal("800"),
        method="card",
    )

    payment = service.mark_failed(4)

    assert payment.status == "failed"