import type { Payment } from "../types/payment";

interface PaymentStatusProps {
  payment: Payment | null;
}

export default function PaymentStatus({
  payment,
}: PaymentStatusProps) {
  if (!payment) {
    return <p>No payment selected.</p>;
  }

  return (
    <div>
      <h2>Payment Status</h2>

      <p>
        Payment ID: {payment.id}
      </p>

      <p>
        Amount: ₹{payment.amount}
      </p>

      <p>
        Method: {payment.method}
      </p>

      <p>
        Status: {payment.status}
      </p>

      {payment.transactionId && (
        <p>
          Transaction ID: {payment.transactionId}
        </p>
      )}
    </div>
  );
}