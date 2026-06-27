import { useState } from "react";
import { auth } from "../api";

export default function Login({ onLogin }) {
  const [step, setStep] = useState(1);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");

  async function handleStep1(e) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      if (isRegister) {
        await auth.register(name, email, password);
      }
      await auth.requestOtp(email, password);
      setStep(2);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  async function handleStep2(e) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const data = await auth.verifyOtp(email, otp);
      localStorage.setItem("wx_token", data.access_token);
      localStorage.setItem("wx_user", JSON.stringify(data.user));
      onLogin(data.user);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo">W</div>
          <h1>WalletX</h1>
          <p>Your money, secured</p>
        </div>

        {step === 1 ? (
          <form onSubmit={handleStep1} className="auth-form">
            {isRegister && (
              <label>Full Name
                <input value={name} onChange={e=>setName(e.target.value)} placeholder="Mahendran" required autoFocus />
              </label>
            )}
            <label>Email
              <input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@gmail.com" required autoFocus={!isRegister} />
            </label>
            <label>Password
              <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Min 8 chars, 1 uppercase, 1 number" required />
            </label>
            {error && <p className="form-error">{error}</p>}
            <button className="btn-primary" disabled={loading}>
              {loading ? "Please wait…" : isRegister ? "Create Account" : "Continue →"}
            </button>
            <button type="button" className="btn-ghost" onClick={() => { setIsRegister(!isRegister); setError(""); }}>
              {isRegister ? "Already have an account? Sign in" : "New here? Create account"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleStep2} className="auth-form">
            <div className="otp-hint">
              <span>📬</span>
              <p>Code sent to <strong>{email}</strong></p>
            </div>
            <label>6-digit code
              <input className="otp-input" inputMode="numeric" maxLength={6}
                value={otp} onChange={e=>setOtp(e.target.value.replace(/\D/g,""))} placeholder="000000" autoFocus required />
            </label>
            {error && <p className="form-error">{error}</p>}
            <button className="btn-primary" disabled={loading || otp.length < 6}>
              {loading ? "Verifying…" : "Sign In"}
            </button>
            <button type="button" className="btn-ghost" onClick={() => { setStep(1); setOtp(""); setError(""); }}>
              ← Back
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
