import { AuthApiClient } from "../../adapters/api/auth-api-client";
import type { RegisterRequestDTO } from "../../adapters/dto/auth-dto";
import { mapAuthLoginDtoToDomain, mapUserDtoToDomain } from "../../adapters/mappers/auth-mapper";
import { tokenStorage } from "../../adapters/storage/token-storage";
import type { AuthSession } from "../../domain/models/auth";
import type { User } from "../../domain/models/user";

const apiClient = new AuthApiClient();

export async function loginUser(identifier: string, password: string): Promise<AuthSession> {
  const dto = await apiClient.login(identifier, password);
  const session = mapAuthLoginDtoToDomain(dto);
  tokenStorage.setToken(session.accessToken);
  tokenStorage.setUser(session.user);
  return session;
}

export async function registerUser(registerData: RegisterRequestDTO): Promise<User> {
  const result = await apiClient.register(registerData);
  return mapUserDtoToDomain(result.user);
}

export async function logoutUser(): Promise<void> {
  const token = tokenStorage.getToken();
  if (token) {
    try {
      await apiClient.logout(token);
    } catch {
      // Ignore network errors on logout
    }
  }
  tokenStorage.removeToken();
}

export async function getCurrentUser(): Promise<User | null> {
  const token = tokenStorage.getToken();
  if (!token) return null;

  try {
    const userDto = await apiClient.getCurrentUser(token);
    const user = mapUserDtoToDomain(userDto);
    tokenStorage.setUser(user);
    return user;
  } catch {
    tokenStorage.removeToken();
    return null;
  }
}
