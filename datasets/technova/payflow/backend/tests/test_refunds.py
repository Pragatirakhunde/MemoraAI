from decimal import Decimal

import pytest

from app.repositories.payment_repository import PaymentRepository
from app.repositories.refund_repository import RefundRepository
from app.services.payment_service import PaymentService
from app.services.refund_service import RefundService


def create_services():
    payment_repository = PaymentRepository()
    refund_repository = RefundRepository()

    payment_service = PaymentService(
        payment_repository
    )

    refund_service = RefundService(
        payment_repository,
        refund_repository,
    )

    return payment_service, refund_service


def test_successful_refund():
    payment_service, refund_service = create_services()

    payment_service.create_payment(
        payment_id=1,
        customer_id=101,
        invoice_id=5001,
        amount=Decimal("1000"),
        method="upi",
    )

    refund = refund_service.create_refund(
        refund_id=1,
        payment_id=1,
        amount=Decimal("400"),
        reason="Customer requested refund",
    )

    assert refund.status == "completed"
    assert refund.amount == Decimal("400")


def test_refund_cannot_exceed_payment():
    payment_service, refund_service = create_services()

    payment_service.create_payment(
        payment_id=2,
        customer_id=101,
        invoice_id=5002,
        amount=Decimal("1000"),
        method="card",
    )

    with pytest.raises(ValueError):
        refund_service.create_refund(
            refund_id=2,
            payment_id=2,
            amount=Decimal("1500"),
            reason="Invalid refund",
        )


def test_refund_requires_existing_payment():
    _, refund_service = create_services()

    with pytest.raises(ValueError):
        refund_service.create_refund(
            refund_id=3,
            payment_id=999,
            amount=Decimal("100"),
            reason="Payment missing",
        )