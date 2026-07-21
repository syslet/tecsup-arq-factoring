const API_BASE_URL = import.meta.env.PUBLIC_API_URL || "http://localhost:8000";

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getToken(): string | null {
    if (typeof window !== "undefined") {
      return localStorage.getItem("factoring_access_token");
    }
    return null;
  }

  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const url = endpoint.startsWith("http") ? endpoint : `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, { ...options, headers });

    const data: Record<string, unknown> = await response.json().catch(() => ({}));

    if (!response.ok) {
      if (response.status === 401 && typeof window !== "undefined") {
        localStorage.removeItem("factoring_access_token");
      }
      const errorMsg =
        (typeof data.error === "string" && data.error) ||
        (typeof data.details === "string" && data.details) ||
        `Error ${response.status}: ${response.statusText}`;
      throw new Error(errorMsg);
    }

    return data as T;
  }

  get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" });
  }

  post<T>(endpoint: string, body?: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    });
  }
}

export const apiClient = new ApiClient();
