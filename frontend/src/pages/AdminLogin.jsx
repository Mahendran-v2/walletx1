import { useState } from "react";
import { auth } from "../api";

export default function AdminLogin({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault(); setError(""); setLoading(true);
    try {
      const data = await auth.adminLogin(email, password);
      localStorage.setItem("wx_token", data.access_token);
      localStorage.setItem("wx_user", JSON.stringify({...data.user, is_admin: true}));
      onLogin(data.user);
    } catch(err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="auth-shell">
      <div className="auth-card">
        <div className="auth-brand">
          <div className="auth-logo" style={{background:"linear-gradient(135deg,#F43F5E,#BE123C)"}}>⚙</div>
          <h1>Admin Panel</h1>
          <p>WalletX Administration</p>
        </div>
        <form onSubmit={submit} className="auth-form">
          <label>Admin Email
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required autoFocus />
          </label>
          <label>Password
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="btn-primary" disabled={loading}>{loading?"Signing in…":"Sign In as Admin"}</button>
        </form>
      </div>
    </div>
  );
}
