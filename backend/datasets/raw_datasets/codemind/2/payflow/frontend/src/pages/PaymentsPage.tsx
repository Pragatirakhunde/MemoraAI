import { useState } from "react";

import PaymentForm from "../components/PaymentForm";
import PaymentStatus from "../components/PaymentStatus";
import { createPayment } from "../services/paymentService";
import type {
  Payment,
  CreatePaymentRequest,
} from "../types/payment";

export default function PaymentsPage() {
  const [payment, setPayment] =
    useState<Payment | null>(null);

  const handlePayment = async (
    request: CreatePaymentRequest
  ) => {
    try {
      const paymentResult =
        await createPayment(request);

      setPayment(paymentResult);
    } catch (error) {
      console.error(
        "Payment failed:",
        error
      );
    }
  };

  return (
    <div>
      <h1>PayFlow Payments</h1>

      <PaymentForm
        onSubmit={handlePayment}
      />

      <PaymentStatus
        payment={payment}
      />
    </div>
  );
}