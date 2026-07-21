import React, { useEffect, useState } from "react";
import { getCurrentUser, logoutUser } from "../../application/use-cases/auth-use-cases";
import type { User } from "../../domain/models/user";

export const UserNavbar: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((u) => setUser(u))
      .finally(() => setIsLoading(false));
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    window.location.href = "/login";
  };

  if (isLoading) {
    return (
      <header className="flex w-full items-center justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-4 backdrop-blur-md">
        <div className="h-6 w-36 animate-pulse rounded bg-slate-800"></div>
        <div className="h-8 w-24 animate-pulse rounded bg-slate-800"></div>
      </header>
    );
  }

  return (
    <header className="sticky top-0 z-50 flex w-full items-center justify-between border-b border-slate-800 bg-slate-900/80 px-6 py-4 backdrop-blur-md">
      {/* Brand */}
      <div className="flex items-center gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-500/10 font-bold text-emerald-400">
          F
        </div>
        <span className="text-lg font-bold tracking-tight text-white">Factoring B2B</span>
      </div>

      {/* User Info & Actions */}
      {user ? (
        <div className="flex items-center gap-4">
          <div className="flex flex-col text-right">
            <div className="flex items-center justify-end gap-2">
              <span className="text-sm font-semibold text-slate-200">{user.fullName}</span>
              {user.verificationStatus === "PENDING_VERIFICATION" ? (
                <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-400">
                  PENDIENTE
                </span>
              ) : (
                <span className="rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-400">
                  APROBADO
                </span>
              )}
            </div>
            <div className="flex items-center justify-end gap-2">
              <span className="text-xs text-slate-400">{user.email}</span>
              <span
                className={`rounded-full border px-2 py-0.5 text-[10px] font-bold ${
                  user.role === "ADMIN"
                    ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-400"
                    : "border-cyan-500/30 bg-cyan-500/10 text-cyan-400"
                }`}
              >
                {user.role}
              </span>
            </div>
          </div>

          <button
            onClick={handleLogout}
            className="cursor-pointer rounded-lg border border-slate-700 bg-slate-800 px-3.5 py-1.5 text-xs font-semibold text-slate-300 transition-all duration-200 hover:border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-400"
          >
            Cerrar Sesión
          </button>
        </div>
      ) : (
        <div className="flex items-center gap-3">
          <a
            href="/login"
            className="px-3 py-1.5 text-xs font-semibold text-slate-300 transition-colors hover:text-white"
          >
            Iniciar Sesión
          </a>
          <a
            href="/register"
            className="rounded-lg bg-emerald-500 px-3.5 py-1.5 text-xs font-semibold text-slate-950 transition-all hover:bg-emerald-400"
          >
            Registrarse
          </a>
        </div>
      )}
    </header>
  );
};
