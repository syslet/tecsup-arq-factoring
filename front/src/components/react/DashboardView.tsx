import React, { useEffect, useState } from "react";
import { getCurrentUser } from "../../application/use-cases/auth-use-cases";
import type { User } from "../../domain/models/user";

export const DashboardView: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((u) => {
        if (!u) {
          window.location.href = "/login";
        } else {
          setUser(u);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex items-center gap-3 text-slate-400">
          <svg className="h-6 w-6 animate-spin text-emerald-400" fill="none" viewBox="0 0 24 24">
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            ></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          <span>Verificando sesión activa...</span>
        </div>
      </div>
    );
  }

  if (!user) return null;

  const isPending = user.verificationStatus === "PENDING_VERIFICATION";

  return (
    <div className="mx-auto max-w-6xl space-y-8 px-6 py-10">
      {/* Welcome Hero */}
      <div className="relative overflow-hidden rounded-2xl border border-slate-800 bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-950 p-8 shadow-xl">
        <div className="pointer-events-none absolute top-0 right-0 h-80 w-80 rounded-full bg-emerald-500/10 blur-[100px]"></div>
        <div className="relative z-10 space-y-3">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-400">
              ● Sesión JWT Activa
            </span>

            {/* Verification Status Badge */}
            {isPending ? (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1 text-xs font-bold text-amber-400">
                <span className="h-2 w-2 animate-pulse rounded-full bg-amber-400"></span>
                PENDING_VERIFICATION
              </span>
            ) : (
              <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs font-bold text-emerald-400">
                <span className="h-2 w-2 rounded-full bg-emerald-400"></span>
                APPROVED
              </span>
            )}
          </div>

          <h1 className="text-3xl font-bold tracking-tight text-white">
            Bienvenido, {user.fullName}
          </h1>
          <p className="max-w-2xl text-sm text-slate-400">
            Representante Legal (DNI: <span className="font-mono text-slate-200">{user.dni}</span>)
            | Panel de gestión y control del sistema de Factoring B2B.
          </p>
        </div>
      </div>

      {/* Verification Warning Alert for PENDING_VERIFICATION */}
      {isPending && (
        <div className="flex flex-col items-start gap-4 rounded-2xl border border-amber-500/30 bg-amber-500/10 p-6 text-amber-300 md:flex-row md:items-center">
          <div className="shrink-0 rounded-xl bg-amber-500/20 p-3">
            <svg
              className="h-6 w-6 text-amber-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <div className="space-y-1">
            <h4 className="text-base font-bold text-amber-200">
              Cuenta en Proceso de Verificación Legal
            </h4>
            <p className="text-xs leading-relaxed text-amber-300/90">
              Tu cuenta se encuentra actualmente en revisión por nuestro equipo legal (validación
              RENIEC y SUNARP). Las operaciones financieras (descuento de facturas y desembolsos)
              están temporalmente restringidas hasta recibir la aprobación final.
            </p>
          </div>
        </div>
      )}

      {/* Company Info Grid */}
      <div className="space-y-4">
        <h2 className="flex items-center gap-2 text-lg font-bold tracking-tight text-white">
          <svg
            className="h-5 w-5 text-cyan-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0h4m-4 0V11m0 0h4m-4 0H9"
            />
          </svg>
          Información de la Empresa Registrada
        </h2>

        {user.company ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="space-y-1 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
              <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Razón Social
              </span>
              <div
                className="truncate text-base font-bold text-white"
                title={user.company.businessName}
              >
                {user.company.businessName}
              </div>
              <p className="text-[11px] text-slate-500">Empresa Titular</p>
            </div>

            <div className="space-y-1 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
              <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
                RUC
              </span>
              <div className="font-mono text-base font-bold text-cyan-400">{user.company.ruc}</div>
              <p className="text-[11px] text-slate-500">11 dígitos SUNAT</p>
            </div>

            <div className="space-y-1 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
              <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Entidad Bancaria
              </span>
              <div className="text-base font-bold text-emerald-400">{user.company.bankName}</div>
              <p className="text-[11px] text-slate-500">Banco Registrado</p>
            </div>

            <div className="space-y-1 rounded-xl border border-slate-800 bg-slate-900/80 p-5">
              <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
                Moneda de Operación
              </span>
              <div className="text-base font-bold text-amber-400">{user.company.currency}</div>
              <p className="text-[11px] text-slate-500">Cuenta Bancaria</p>
            </div>
          </div>
        ) : (
          <div className="rounded-xl border border-slate-800 bg-slate-900/40 p-6 text-center text-xs text-slate-500">
            Sin información de empresa asociada.
          </div>
        )}
      </div>

      {/* User Info Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <div className="space-y-2 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Representante Legal
          </span>
          <div className="text-lg font-bold text-white">{user.fullName}</div>
          <p className="text-xs text-slate-400">Email: {user.email}</p>
        </div>

        <div className="space-y-2 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Rol en Sistema
          </span>
          <div className="text-lg font-bold text-emerald-400">{user.role}</div>
          <p className="text-xs text-slate-400">Permisos asignados en Factoring B2B</p>
        </div>

        <div className="space-y-2 rounded-xl border border-slate-800 bg-slate-900/80 p-6">
          <span className="text-xs font-semibold tracking-wider text-slate-500 uppercase">
            Estado de Acceso
          </span>
          <div className="text-lg font-bold text-cyan-400">
            {user.isLocked ? "BLOQUEADO" : user.isActive ? "ACTIVO" : "INACTIVO"}
          </div>
          <p className="text-xs text-slate-400">Persistencia JWT verificada</p>
        </div>
      </div>
    </div>
  );
};
