import { useEffect, useState } from "react";
import { wallet as walletApi } from "../api";

const fmt = (n) => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR" }).format(n || 0);

export default function Dashboard({ user, setPage }) {
  const [balance, setBalance] = useState(null);
  const [txs, setTxs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([walletApi.get(), walletApi.transactions()])
      .then(([w, t]) => { setBalance(w.balance); setTxs(t.slice(0, 5)); })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="greeting">Good {hour()}</p>
          <h1 className="username">{user?.name?.split(" ")[0]} 👋</h1>
        </div>
        <button className="avatar" onClick={() => setPage("profile")}>{user?.name?.[0]}</button>
      </header>

      <div className="wallet-card">
        <div className="wc-top">
          <span className="wc-label">Total Balance</span>
          <span className="wc-live">● Live</span>
        </div>
        <div className="wc-amount">{loading ? "—" : fmt(balance)}</div>
        <div className="wc-bottom">
          <button className="btn-accent" onClick={() => setPage("wallet")}>+ Add Money</button>
        </div>
      </div>

      <div className="action-grid">
        {[
          ["↑","Send",      "transfer"],
          ["↓","Withdraw",  "wallet"],
          ["≡","History",   "transactions"],
          ["◯","Profile",   "profile"],
        ].map(([icon, label, page]) => (
          <button key={label} className="action-btn" onClick={() => setPage(page)}>
            <span className="action-icon">{icon}</span>
            <span>{label}</span>
          </button>
        ))}
      </div>

      {txs.length > 0 && (
        <section>
          <div className="section-row">
            <h2 className="section-title">Recent</h2>
            <button className="see-all" onClick={() => setPage("transactions")}>See all →</button>
          </div>
          {txs.map(tx => <TxRow key={tx.id} tx={tx} uid={user?.id} />)}
        </section>
      )}
    </div>
  );
}

function TxRow({ tx, uid }) {
  const sent = tx.sender_id === uid;
  return (
    <div className="tx-card">
      <div className={`tx-icon ${sent ? "tx-sent" : "tx-recv"}`}>{sent ? "↑" : "↓"}</div>
      <div className="tx-info">
        <span>{sent ? `Sent to #${tx.receiver_id}` : `From #${tx.sender_id}`}</span>
        <span className="tx-date">{new Date(tx.timestamp).toLocaleDateString("en-IN")}</span>
        {tx.is_flagged && <span className="fraud-badge">⚠ Flagged</span>}
      </div>
      <span className={`tx-amt ${sent ? "tx-sent" : "tx-recv"}`}>
        {sent ? "-" : "+"}{new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR"}).format(tx.amount)}
      </span>
    </div>
  );
}

function hour() {
  const h = new Date().getHours();
  return h < 12 ? "morning" : h < 17 ? "afternoon" : "evening";
}
