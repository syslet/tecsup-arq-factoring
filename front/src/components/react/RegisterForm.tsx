import React, { useState } from "react";
import { registerUser } from "../../application/use-cases/auth-use-cases";
import type { RegisterRequestDTO } from "../../adapters/dto/auth-dto";

export const RegisterForm: React.FC = () => {
  const [step, setStep] = useState<1 | 2>(1);

  // Step 1: Legal Representative
  const [fullName, setFullName] = useState("");
  const [dni, setDni] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Step 2: Company Data
  const [ruc, setRuc] = useState("");
  const [businessName, setBusinessName] = useState("");
  const [bankName, setBankName] = useState("BCP");
  const [bankAccountNumber, setBankAccountNumber] = useState("");
  const [cci, setCci] = useState("");
  const [currency, setCurrency] = useState<"PEN" | "USD">("PEN");

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const validateStep1 = (): boolean => {
    if (!fullName.trim() || fullName.trim().length < 2) {
      setError("Ingrese un nombre completo válido (mínimo 2 caracteres).");
      return false;
    }
    if (!/^\d{8}$/.test(dni)) {
      setError("El DNI del Representante Legal debe contener exactamente 8 dígitos numéricos.");
      return false;
    }
    const freeDomains = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com", "live.com"];
    const emailParts = email.trim().toLowerCase().split("@");
    if (!email.includes("@") || emailParts.length !== 2 || freeDomains.includes(emailParts[1])) {
      setError("Debe ingresar un correo electrónico corporativo (se rechazan dominios gratuitos como Gmail, Hotmail, Yahoo, etc.).");
      return false;
    }
    if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&._-]).{8,}$/.test(password)) {
      setError("La contraseña debe tener al menos 8 caracteres, al menos una mayúscula, una minúscula, un número y un carácter especial (@$!%*?&._-).");
      return false;
    }
    if (password !== confirmPassword) {
      setError("Las contraseñas no coinciden.");
      return false;
    }
    setError(null);
    return true;
  };

  const handleNextStep = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateStep1()) {
      setStep(2);
    }
  };

  const validateStep2 = (): boolean => {
    if (!/^(10|15|17|20)\d{9}$/.test(ruc)) {
      setError("El RUC debe tener 11 dígitos numéricos y comenzar con 10, 15, 17 o 20.");
      return false;
    }
    if (!businessName.trim() || businessName.trim().length < 3) {
      setError("La Razón Social debe tener al menos 3 caracteres.");
      return false;
    }
    if (!bankAccountNumber.trim()) {
      setError("Ingrese el número de cuenta bancaria.");
      return false;
    }
    if (!/^\d{20}$/.test(cci)) {
      setError("El CCI debe contener exactamente 20 dígitos numéricos.");
      return false;
    }
    setError(null);
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!validateStep2()) {
      return;
    }

    setIsLoading(true);

    const payload: RegisterRequestDTO = {
      email,
      password,
      full_name: fullName,
      dni,
      phone: phone.trim() || null,
      company: {
        ruc,
        business_name: businessName,
        bank_name: bankName,
        bank_account_number: bankAccountNumber,
        cci,
        currency,
      },
    };

    try {
      await registerUser(payload);
      setSuccess("¡Cuenta de empresa registrada exitosamente! Redirigiendo al inicio de sesión...");
      setTimeout(() => {
        window.location.href = "/login";
      }, 1500);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Error al registrar la cuenta";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-xl rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl shadow-slate-950/50 backdrop-blur-xl">
      {/* Header */}
      <div className="mb-6 text-center">
        <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-xl border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
          <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5m0 0h4m-4 0V11m0 0h4m-4 0H9"
            />
          </svg>
        </div>
        <h1 className="bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-2xl font-bold text-transparent">
          Onboarding Factoring B2B
        </h1>
        <p className="mt-1 text-xs text-slate-400">
          Registro de Representante Legal y Datos Empresariales
        </p>
      </div>

      {/* Step Indicator */}
      <div className="mb-6 flex items-center justify-center gap-4">
        <button
          type="button"
          onClick={() => setStep(1)}
          className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold transition-all ${
            step === 1
              ? "border border-cyan-500/40 bg-cyan-500/20 text-cyan-400"
              : "bg-slate-800/60 text-slate-400 hover:text-white"
          }`}
        >
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-cyan-500/20 text-[10px]">
            1
          </span>
          <span>Rep. Legal</span>
        </button>

        <div className="h-px w-8 bg-slate-800"></div>

        <button
          type="button"
          onClick={() => {
            if (validateStep1()) setStep(2);
          }}
          className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold transition-all ${
            step === 2
              ? "border border-cyan-500/40 bg-cyan-500/20 text-cyan-400"
              : "bg-slate-800/60 text-slate-400 hover:text-white"
          }`}
        >
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-cyan-500/20 text-[10px]">
            2
          </span>
          <span>Empresa & Banco</span>
        </button>
      </div>

      {/* Alerts */}
      {error && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-400">
          <svg
            className="mt-0.5 h-5 w-5 shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="mb-6 flex items-start gap-3 rounded-xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-400">
          <svg
            className="mt-0.5 h-5 w-5 shrink-0"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{success}</span>
        </div>
      )}

      {/* Step 1 Form */}
      {step === 1 && (
        <form onSubmit={handleNextStep} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Nombres Completos *
              </label>
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Juan Pérez"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                DNI (8 dígitos) *
              </label>
              <input
                type="text"
                required
                maxLength={8}
                value={dni}
                onChange={(e) => setDni(e.target.value.replace(/\D/g, ""))}
                placeholder="12345678"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 font-mono text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Correo Electrónico *
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="contacto@empresa.com"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Teléfono de Contacto
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="987654321"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Contraseña *
              </label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Mínimo 6 caracteres"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Confirmar Contraseña *
              </label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repite la contraseña"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          <button
            type="submit"
            className="mt-4 flex w-full cursor-pointer items-center justify-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 font-semibold text-slate-950 shadow-lg shadow-cyan-500/15 transition-all duration-200 hover:bg-cyan-400 hover:shadow-cyan-500/25"
          >
            <span>Continuar a Datos de la Empresa</span>
            <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M14 5l7 7m0 0l-7 7m7-7H3"
              />
            </svg>
          </button>
        </form>
      )}

      {/* Step 2 Form */}
      {step === 2 && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                RUC (11 dígitos) *
              </label>
              <input
                type="text"
                required
                maxLength={11}
                value={ruc}
                onChange={(e) => setRuc(e.target.value.replace(/\D/g, ""))}
                placeholder="20123456789"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 font-mono text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Razón Social *
              </label>
              <input
                type="text"
                required
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="Empresa Proveedora S.A.C."
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Banco *
              </label>
              <select
                value={bankName}
                onChange={(e) => setBankName(e.target.value)}
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              >
                <option value="BCP">BCP - Banco de Crédito</option>
                <option value="BBVA">BBVA Perú</option>
                <option value="Interbank">Interbank</option>
                <option value="Scotiabank">Scotiabank</option>
                <option value="BanBif">BanBif</option>
              </select>
            </div>

            <div>
              <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
                Moneda de Cuenta *
              </label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value as "PEN" | "USD")}
                className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 text-sm text-white transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
              >
                <option value="PEN">PEN (Soles)</option>
                <option value="USD">USD (Dólares)</option>
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Número de Cuenta Bancaria *
            </label>
            <input
              type="text"
              required
              value={bankAccountNumber}
              onChange={(e) => setBankAccountNumber(e.target.value)}
              placeholder="193-12345678-0-12"
              className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 font-mono text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold tracking-wider text-slate-400 uppercase">
              Código de Cuenta Interbancario (CCI - 20 dígitos) *
            </label>
            <input
              type="text"
              required
              maxLength={20}
              value={cci}
              onChange={(e) => setCci(e.target.value.replace(/\D/g, ""))}
              placeholder="00219300123456780112"
              className="w-full rounded-lg border border-slate-800 bg-slate-950/70 px-3.5 py-2.5 font-mono text-sm text-white placeholder-slate-600 transition-all outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500"
            />
          </div>

          <div className="flex items-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="w-1/3 cursor-pointer rounded-lg bg-slate-800 px-4 py-2.5 text-sm font-semibold text-slate-300 transition-all hover:bg-slate-700"
            >
              Atrás
            </button>

            <button
              type="submit"
              disabled={isLoading}
              className="flex w-2/3 cursor-pointer items-center justify-center gap-2 rounded-lg bg-cyan-500 px-4 py-2.5 text-sm font-semibold text-slate-950 shadow-lg shadow-cyan-500/15 transition-all duration-200 hover:bg-cyan-400 hover:shadow-cyan-500/25 active:scale-[0.99] disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <svg
                    className="h-4 w-4 animate-spin text-slate-950"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
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
                  <span>Registrando Empresa...</span>
                </>
              ) : (
                <span>Completar Registro B2B</span>
              )}
            </button>
          </div>
        </form>
      )}

      <div className="mt-6 border-t border-slate-800/60 pt-6 text-center text-xs text-slate-500">
        ¿Ya tienes una cuenta?{" "}
        <a
          href="/login"
          className="font-medium text-slate-300 underline underline-offset-4 hover:text-white"
        >
          Inicia sesión aquí
        </a>
      </div>
    </div>
  );
};
