import { useState } from "react";
import { auth, profile as profileApi } from "../api";

export default function Profile({ user, onLogout }) {
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  async function save(e) {
    e.preventDefault(); setError("");
    const payload = { name, email };
    if (password) { if (password.length < 8) { setError("Password min 8 chars"); return; } payload.password = password; }
    setLoading(true);
    try {
      await profileApi.update(payload);
      setPassword("");
      setToast("✅ Saved"); setTimeout(() => setToast(""), 3000);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  async function logout() {
    try { await auth.logout(); } catch (_) {}
    localStorage.clear();
    onLogout();
  }

  return (
    <div className="page">
      <h1 className="page-title">Profile</h1>

      <div className="profile-block">
        <div className="profile-avatar">{user?.name?.[0]}</div>
        <div>
          <p style={{fontWeight:600,fontSize:"1.05rem"}}>{user?.name}</p>
          <p style={{color:"var(--text-2)",fontSize:"0.85rem"}}>{user?.email}</p>
          <p style={{color:"var(--text-3)",fontSize:"0.8rem",fontFamily:"var(--mono)"}}>ID #{user?.id}</p>
        </div>
      </div>

      <div className="card">
        <form onSubmit={save} style={{display:"flex",flexDirection:"column",gap:14}}>
          <label className="field-label">Full Name
            <input value={name} onChange={e=>setName(e.target.value)} required />
          </label>
          <label className="field-label">Email
            <input type="email" value={email} onChange={e=>setEmail(e.target.value)} required />
          </label>
          <label className="field-label">New Password <span style={{color:"var(--text-3)",fontWeight:400}}>(optional)</span>
            <input type="password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Leave blank to keep current" />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="btn-primary btn-full" disabled={loading}>{loading?"Saving…":"Save Changes"}</button>
        </form>
      </div>

      <div style={{marginTop:16}}>
        <button className="btn-danger btn-full" onClick={logout}>Sign Out</button>
      </div>

      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
