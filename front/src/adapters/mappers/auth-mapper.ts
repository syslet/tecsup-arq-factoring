import type { AuthLoginResponseDTO, CompanyDTO, UserDTO } from "../dto/auth-dto";
import type { AuthSession } from "../../domain/models/auth";
import type { Company, User } from "../../domain/models/user";

/**
 * Converts a backend CompanyDTO (snake_case) to a domain Company model (camelCase).
 */
export function mapCompanyDtoToDomain(dto: CompanyDTO): Company {
  return {
    id: dto.id,
    ruc: dto.ruc,
    businessName: dto.business_name,
    bankName: dto.bank_name,
    currency: dto.currency,
  };
}

/**
 * Converts a backend UserDTO (snake_case) to a domain User model (camelCase).
 */
export function mapUserDtoToDomain(dto: UserDTO): User {
  return {
    id: dto.id,
    email: dto.email,
    fullName: dto.full_name,
    dni: dto.dni,
    phone: dto.phone,
    role: dto.role,
    verificationStatus: dto.verification_status,
    isActive: dto.is_active,
    isLocked: dto.is_locked,
    company: dto.company ? mapCompanyDtoToDomain(dto.company) : null,
    createdAt: dto.created_at,
  };
}

/**
 * Converts a backend AuthLoginResponseDTO to a domain AuthSession model.
 */
export function mapAuthLoginDtoToDomain(dto: AuthLoginResponseDTO): AuthSession {
  return {
    accessToken: dto.access_token,
    tokenType: dto.token_type,
    expiresAt: dto.expires_at,
    user: mapUserDtoToDomain(dto.user),
  };
}
