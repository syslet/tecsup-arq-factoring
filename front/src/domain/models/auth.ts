import type { User } from "./user";

export interface AuthSession {
  accessToken: string;
  tokenType: string;
  expiresAt: string;
  user: User;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
}
