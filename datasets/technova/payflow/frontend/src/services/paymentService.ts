import type {
  CreatePaymentRequest,
  Payment,
} from "../types/payment";

const API_BASE_URL = "http://localhost:8000/api";

export async function createPayment(
  request: CreatePaymentRequest
): Promise<Payment> {
  const response = await fetch(`${API_BASE_URL}/payments`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error("Failed to create payment");
  }

  return response.json();
}

export async function getPayment(
  paymentId: number
): Promise<Payment> {
  const response = await fetch(
    `${API_BASE_URL}/payments/${paymentId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch payment");
  }

  return response.json();
}