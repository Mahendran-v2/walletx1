import { useEffect, useState } from "react";
import { wallet as walletApi } from "../api";

const fmt = n => new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR"}).format(n||0);

export default function Transactions({ user }) {
  const [txs, setTxs] = useState([]);
  const [filter, setFilter] = useState("all");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    walletApi.transactions().then(setTxs).finally(() => setLoading(false));
  }, []);

  const filtered = txs.filter(t =>
    filter === "all" ? true : filter === "sent" ? t.sender_id === user?.id : t.receiver_id === user?.id
  );

  const totalSent = txs.filter(t=>t.sender_id===user?.id).reduce((s,t)=>s+parseFloat(t.amount),0);
  const totalRecv = txs.filter(t=>t.receiver_id===user?.id).reduce((s,t)=>s+parseFloat(t.amount),0);

  return (
    <div className="page">
      <h1 className="page-title">Transactions</h1>

      <div className="summary-row">
        <div className="summary-card recv">
          <span className="summary-label">Received</span>
          <span className="summary-amt">+{fmt(totalRecv)}</span>
        </div>
        <div className="summary-card sent">
          <span className="summary-label">Sent</span>
          <span className="summary-amt">−{fmt(totalSent)}</span>
        </div>
      </div>

      <div className="filter-tabs">
        {["all","sent","received"].map(f=>(
          <button key={f} className={`filter-tab ${filter===f?"filter-tab-active":""}`} onClick={()=>setFilter(f)}>
            {f.charAt(0).toUpperCase()+f.slice(1)}
          </button>
        ))}
      </div>

      {loading && <p className="state-msg">Loading…</p>}
      {!loading && filtered.length === 0 && <p className="state-msg">No transactions yet</p>}
      {filtered.map(tx => {
        const sent = tx.sender_id === user?.id;
        return (
          <div key={tx.id} className="tx-card">
            <div className={`tx-icon ${sent?"tx-sent":"tx-recv"}`}>{sent?"↑":"↓"}</div>
            <div className="tx-info">
              <span>{sent ? `To User #${tx.receiver_id}` : `From User #${tx.sender_id}`}</span>
              {tx.note && <span className="tx-note">{tx.note}</span>}
              <span className="tx-date">{new Date(tx.timestamp).toLocaleString("en-IN")}</span>
              {tx.is_flagged && <span className="fraud-badge">⚠ Flagged</span>}
            </div>
            <span className={`tx-amt ${sent?"tx-sent":"tx-recv"}`}>{sent?"-":"+"}{fmt(tx.amount)}</span>
          </div>
        );
      })}
    </div>
  );
}
