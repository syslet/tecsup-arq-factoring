import type {
  AuthLoginResponseDTO,
  RegisterRequestDTO,
  UserDTO,
  UserMeResponseDTO,
} from "../dto/auth-dto";

const API_BASE_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

export class AuthApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async login(identifier: string, password: string): Promise<AuthLoginResponseDTO> {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ identifier, password }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Authentication failed");
    }
    return data as AuthLoginResponseDTO;
  }

  async register(registerData: RegisterRequestDTO): Promise<{ message: string; user: UserDTO }> {
    const response = await fetch(`${this.baseUrl}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(registerData),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Registration failed");
    }
    return data;
  }

  async logout(token: string): Promise<void> {
    await fetch(`${this.baseUrl}/api/auth/logout`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
  }

  async getCurrentUser(token: string): Promise<UserDTO> {
    const response = await fetch(`${this.baseUrl}/api/auth/me`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Failed to fetch current user profile");
    }
    return (data as UserMeResponseDTO).user;
  }
}
