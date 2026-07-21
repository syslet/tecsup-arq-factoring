export interface CompanyDTO {
  id: number;
  ruc: string;
  business_name: string;
  bank_name: string;
  currency: string;
}

export interface UserDTO {
  id: number;
  email: string;
  full_name: string;
  dni: string;
  phone: string | null;
  role: "ADMIN" | "CLIENT" | "EXECUTIVE";
  verification_status: "PENDING_VERIFICATION" | "APPROVED";
  is_active: boolean;
  is_locked: boolean;
  company?: CompanyDTO | null;
  created_at?: string;
}

export interface CompanyRegisterDTO {
  ruc: string;
  business_name: string;
  bank_name: string;
  bank_account_number: string;
  cci: string;
  currency: string;
}

export interface RegisterRequestDTO {
  email: string;
  password: string;
  full_name: string;
  dni: string;
  phone?: string | null;
  company?: CompanyRegisterDTO | null;
}

export interface LoginRequestDTO {
  identifier: string;
  password: string;
}

export interface AuthLoginResponseDTO {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: UserDTO;
}

export interface UserMeResponseDTO {
  user: UserDTO;
}

export interface ApiErrorDTO {
  error: string;
  details?: Array<{ msg: string; loc: string[] }>;
}
