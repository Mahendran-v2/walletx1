import { useEffect, useState } from "react";
import { wallet as walletApi } from "../api";

export default function Wallet() {
  const [balance, setBalance] = useState(null);
  const [amount, setAmount] = useState("");
  const [mode, setMode] = useState("add");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const load = () => walletApi.get().then(w => setBalance(w.balance));
  useEffect(() => { load(); }, []);

  async function submit(e) {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      mode === "add"
        ? await walletApi.add(parseFloat(amount))
        : await walletApi.withdraw(parseFloat(amount));
      setAmount("");
      await load();
      setToast(`✅ ₹${amount} ${mode === "add" ? "added" : "withdrawn"}`);
      setTimeout(() => setToast(""), 3000);
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  const fmt = n => new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR"}).format(n||0);

  return (
    <div className="page">
      <h1 className="page-title">Wallet</h1>
      <div className="wallet-card">
        <p className="wc-label">Balance</p>
        <div className="wc-amount">{balance === null ? "—" : fmt(balance)}</div>
      </div>

      <div className="filter-tabs" style={{marginBottom:20}}>
        <button className={`filter-tab ${mode==="add"?"filter-tab-active":""}`} onClick={()=>setMode("add")}>Add Money</button>
        <button className={`filter-tab ${mode==="withdraw"?"filter-tab-active":""}`} onClick={()=>setMode("withdraw")}>Withdraw</button>
      </div>

      <div className="card">
        <div className="quick-amounts">
          {[500,1000,2000,5000].map(q=>(
            <button key={q} className={`quick-chip ${amount==q?"quick-chip-active":""}`} onClick={()=>setAmount(String(q))}>₹{q.toLocaleString("en-IN")}</button>
          ))}
        </div>
        <form onSubmit={submit} style={{marginTop:16,display:"flex",flexDirection:"column",gap:12}}>
          <div className="amount-field">
            <span className="amount-prefix">₹</span>
            <input type="number" min="1" step="0.01" value={amount} onChange={e=>setAmount(e.target.value)} placeholder="0.00" required />
          </div>
          {error && <p className="form-error">{error}</p>}
          <button className="btn-primary btn-full" disabled={loading||!amount}>
            {loading ? "Processing…" : mode==="add" ? `Add ₹${amount||0}` : `Withdraw ₹${amount||0}`}
          </button>
        </form>
      </div>
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}
