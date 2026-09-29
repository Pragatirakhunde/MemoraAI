export type PaymentMethod =
  | "card"
  | "upi"
  | "netbanking"
  | "wallet";

export type PaymentStatus =
  | "pending"
  | "processing"
  | "success"
  | "failed"
  | "refunded";

export interface Payment {
  id: number;
  customerId: number;
  invoiceId: number;
  amount: number;
  method: PaymentMethod;
  status: PaymentStatus;
  transactionId?: string;
}

export interface CreatePaymentRequest {
  customerId: number;
  invoiceId: number;
  amount: number;
  method: PaymentMethod;
}