"use client";

import { FormEvent, useState } from "react";
import { API_BASE_URL } from "@/lib/config";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      });

      if (response.ok) {
        setMessage("Authenticated — you can now access the dashboard.");
      } else {
        setMessage("Login failed. Please verify your credentials.");
      }
    } catch (error) {
      console.error(error);
      setMessage("Unable to reach the API gateway.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="w-full max-w-md rounded-3xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl ring-1 ring-emerald-500/20">
        <h1 className="text-2xl font-bold text-white">SOD Command Center Login</h1>
        <p className="mt-1 text-sm text-slate-400">Authenticate to monitor and issue commands.</p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="space-y-2">
            <label className="text-sm text-slate-300" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/70 p-3 text-sm text-white placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
              placeholder="ops@sodmaster.online"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm text-slate-300" htmlFor="password">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950/70 p-3 text-sm text-white placeholder:text-slate-500 focus:border-emerald-400 focus:outline-none"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-full bg-emerald-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-emerald-400"
          >
            Login
          </button>
        </form>

        {message && <p className="mt-4 text-center text-sm text-emerald-200">{message}</p>}
      </div>
    </div>
  );
}
