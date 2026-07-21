export type UserRole = "ADMIN" | "CLIENT" | "EXECUTIVE";
export type VerificationStatus = "PENDING_VERIFICATION" | "APPROVED";

export interface Company {
  id: number;
  ruc: string;
  businessName: string;
  bankName: string;
  currency: string;
}

export interface User {
  id: number;
  email: string;
  fullName: string;
  dni: string;
  phone: string | null;
  role: UserRole;
  verificationStatus: VerificationStatus;
  isActive: boolean;
  isLocked: boolean;
  company?: Company | null;
  createdAt?: string;
}
