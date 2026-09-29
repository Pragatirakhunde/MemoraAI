import { useState } from "react";
import type {
  CreatePaymentRequest,
  PaymentMethod,
} from "../types/payment";

interface PaymentFormProps {
  onSubmit: (data: CreatePaymentRequest) => Promise<void>;
}

export default function PaymentForm({
  onSubmit,
}: PaymentFormProps) {
  const [customerId, setCustomerId] = useState("");
  const [invoiceId, setInvoiceId] = useState("");
  const [amount, setAmount] = useState("");
  const [method, setMethod] =
    useState<PaymentMethod>("upi");

  const handleSubmit = async (
    event: React.FormEvent
  ) => {
    event.preventDefault();

    await onSubmit({
      customerId: Number(customerId),
      invoiceId: Number(invoiceId),
      amount: Number(amount),
      method,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Create Payment</h2>

      <input
        type="number"
        placeholder="Customer ID"
        value={customerId}
        onChange={(event) =>
          setCustomerId(event.target.value)
        }
      />

      <input
        type="number"
        placeholder="Invoice ID"
        value={invoiceId}
        onChange={(event) =>
          setInvoiceId(event.target.value)
        }
      />

      <input
        type="number"
        placeholder="Amount"
        value={amount}
        onChange={(event) =>
          setAmount(event.target.value)
        }
      />

      <select
        value={method}
        onChange={(event) =>
          setMethod(
            event.target.value as PaymentMethod
          )
        }
      >
        <option value="upi">UPI</option>
        <option value="card">Card</option>
        <option value="netbanking">
          Net Banking
        </option>
        <option value="wallet">Wallet</option>
      </select>

      <button type="submit">
        Pay Now
      </button>
    </form>
  );
}