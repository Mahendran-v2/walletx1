import { useEffect, useState } from "react";
import { admin as adminApi, auth } from "../api";

const fmt = n => new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR"}).format(n||0);

export default function AdminDashboard({ onLogout }) {
  const [tab, setTab] = useState("stats");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [txs, setTxs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadAll(); }, []);

  async function loadAll() {
    setLoading(true);
    try {
      const [s, u, a, t] = await Promise.all([
        adminApi.stats(), adminApi.users(), adminApi.fraudAlerts(), adminApi.transactions()
      ]);
      setStats(s); setUsers(u); setAlerts(a); setTxs(t);
    } catch(e) { console.error(e); }
    finally { setLoading(false); }
  }

  async function deactivate(id) {
    if (!confirm("Deactivate this user?")) return;
    try {
      await adminApi.deactivate(id);
      setUsers(u => u.map(x => x.id === id ? {...x, is_active: false} : x));
    } catch(e) {
      alert(e.message || "Failed to deactivate user");
    }
  }

  async function logout() {
    try { await auth.logout(); } catch(_) {}
    localStorage.clear(); onLogout();
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p style={{color:"var(--text-2)",fontSize:"0.8rem"}}>ADMIN PANEL</p>
          <h1 className="page-title">WalletX</h1>
        </div>
        <button className="btn-danger" style={{padding:"8px 16px",borderRadius:8,fontSize:"0.85rem"}} onClick={logout}>Sign Out</button>
      </header>

      {loading && <p className="state-msg">Loading…</p>}

      {!loading && stats && (
        <div className="stats-grid">
          {[
            ["Users",        stats.total_users,        "◯"],
            ["Transactions", stats.total_transactions, "⇄"],
            ["Volume",       fmt(stats.total_volume),  "₹"],
            ["Fraud Alerts", stats.fraud_alerts,       "⚠"],
            ["Active Sessions", stats.active_sessions, "●"],
          ].map(([label, val, icon]) => (
            <div key={label} className="stat-card">
              <span className="stat-icon">{icon}</span>
              <span className="stat-val">{val}</span>
              <span className="stat-label">{label}</span>
            </div>
          ))}
        </div>
      )}

      <div className="filter-tabs" style={{marginBottom:20}}>
        {["Users","Fraud Alerts","Transactions"].map(t=>(
          <button key={t} className={`filter-tab ${tab===t.toLowerCase().replace(" ","-")?"filter-tab-active":""}`}
            onClick={()=>setTab(t.toLowerCase().replace(" ","-"))}>
            {t}
          </button>
        ))}
      </div>

      {tab === "users" && (
        <div>
          {users.map(u => (
            <div key={u.id} className="admin-row">
              <div className="profile-avatar" style={{width:36,height:36,fontSize:"0.95rem"}}>{u.name[0]}</div>
              <div style={{flex:1}}>
                <p style={{fontWeight:500}}>{u.name}</p>
                <p style={{fontSize:"0.8rem",color:"var(--text-2)"}}>{u.email} · ID #{u.id}</p>
              </div>
              <span className={`status-badge ${u.is_active?"badge-active":"badge-inactive"}`}>
                {u.is_active ? "Active" : "Inactive"}
              </span>
              {u.is_active && (
                <button className="btn-danger" style={{padding:"4px 10px",fontSize:"0.78rem",borderRadius:6}} onClick={()=>deactivate(u.id)}>
                  Deactivate
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {tab === "fraud-alerts" && (
        <div>
          {alerts.length === 0 && <p className="state-msg">No fraud alerts 🎉</p>}
          {alerts.map(a => (
            <div key={a.id} className="admin-row">
              <span className={`severity-badge sev-${a.severity}`}>{a.severity.toUpperCase()}</span>
              <div style={{flex:1}}>
                <p style={{fontWeight:500}}>{a.rule_triggered}</p>
                <p style={{fontSize:"0.8rem",color:"var(--text-2)"}}>Transaction #{a.transaction_id} · {new Date(a.created_at).toLocaleString("en-IN")}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {tab === "transactions" && (
        <div>
          {txs.map(t => (
            <div key={t.id} className="admin-row">
              <div className={`tx-icon ${t.flagged?"tx-sent":"tx-recv"}`} style={{fontSize:"0.8rem"}}>{t.flagged?"⚠":"✓"}</div>
              <div style={{flex:1}}>
                <p style={{fontWeight:500}}>#{t.sender_id} → #{t.receiver_id}</p>
                <p style={{fontSize:"0.8rem",color:"var(--text-2)"}}>{new Date(t.timestamp).toLocaleString("en-IN")}</p>
              </div>
              <span style={{fontFamily:"var(--mono)",fontWeight:600}}>{fmt(t.amount)}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
