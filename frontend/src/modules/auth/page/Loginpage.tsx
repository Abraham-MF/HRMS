import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { AlertCircle, Loader2, Sparkles } from "lucide-react";
import { useAuthStore } from "../store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Correo o contraseña incorrectos.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-[#18181b] flex items-center justify-center px-4 relative overflow-hidden">

      {/* Orbs de fondo */}
      <div className="absolute top-[-10%] left-[-5%] w-96 h-96 bg-purple-700/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-5%] w-80 h-80 bg-purple-500/15 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-purple-900/10 rounded-full blur-[140px] pointer-events-none" />

      <div className="w-full max-w-md relative z-10">

        {/* Logo */}
        <div className="text-center mb-8">
          <div
            className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl
            bg-primary shadow-glow-lg text-3xl"
          >
            🌊
          </div>

          <h1 className="text-4xl font-bold text-white tracking-tight">
            RH
          </h1>

          <p className="mt-2 text-zinc-400 text-sm">
            Gestion de Recursos Humanos
          </p>
        </div>

        {/* Card */}
        <div className="rounded-2xl border border-purple-900/50 bg-[#1c1c21]/90 backdrop-blur-xl shadow-2xl p-8">
          <h2 className="text-xl font-semibold text-white mb-1">Iniciar sesión</h2>
          <p className="text-sm text-zinc-500 mb-6">Accede con tu correo y contraseña</p>

          <form onSubmit={handleSubmit} className="space-y-5">

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Correo electrónico
              </label>
              <input
                type="email"
                required
                autoComplete="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="admin@empresa.com"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-900/80 px-4 py-3 text-white
                  placeholder-zinc-600 outline-none transition-all text-sm
                  focus:border-purple-500 focus:ring-2 focus:ring-purple-500/30"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-zinc-300 mb-2">
                Contraseña
              </label>
              <input
                type="password"
                required
                autoComplete="current-password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-xl border border-zinc-700 bg-zinc-900/80 px-4 py-3 text-white
                  placeholder-zinc-600 outline-none transition-all text-sm
                  focus:border-purple-500 focus:ring-2 focus:ring-purple-500/30"
              />
            </div>

            {error && (
              <div className="flex items-start gap-2 rounded-xl border border-red-800/60 bg-red-900/20 p-3 text-sm text-red-400">
                <AlertCircle className="mt-0.5 h-4 w-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center rounded-xl
                bg-gradient-to-r from-purple-600 to-purple-700
                py-3 font-semibold text-white text-sm
                transition-all hover:from-purple-500 hover:to-purple-600
                hover:shadow-glow disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {loading ? "Verificando..." : "Iniciar sesión"}
            </button>

          </form>
        </div>

        {/* Demo */}
        <div className="mt-4 rounded-xl border border-zinc-800 bg-zinc-900/60 p-4 backdrop-blur-sm">
          <p className="text-xs font-semibold uppercase tracking-widest text-zinc-500 mb-2">
            Cuenta de prueba
          </p>
          <button
            type="button"
            onClick={() => { setEmail("admin@hrms.com"); setPassword("Admin1234!"); }}
            className="text-sm font-medium text-purple-400 hover:text-purple-300 transition-colors"
          >
            ADMIN → admin@hrms.com
          </button>
          <p className="mt-1 text-xs text-zinc-600">Contraseña: Admin1234!</p>
        </div>

      </div>
    </div>
  );
}
