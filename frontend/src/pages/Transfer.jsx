import { useState } from "react";
import { wallet as walletApi } from "../api";

export default function Transfer({ user }) {
  const [receiverId, setReceiverId] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(""); setSuccess(null);
    if (parseInt(receiverId) === user?.id) { setError("Can't send to yourself"); return; }
    setLoading(true);
    try {
      const tx = await walletApi.transfer(parseInt(receiverId), parseFloat(amount), note);
      setSuccess(tx);
      setReceiverId(""); setAmount(""); setNote("");
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  }

  return (
    <div className="page">
      <h1 className="page-title">Send Money</h1>

      {success && (
        <div className="success-banner">
          <div className="success-icon">✓</div>
          <div>
            <p style={{fontWeight:600}}>Transfer complete!</p>
            <p style={{fontSize:"0.85rem",color:"var(--text-2)"}}>
              ₹{parseFloat(success.amount).toLocaleString("en-IN")} sent to User #{success.receiver_id}
            </p>
          </div>
          <button style={{marginLeft:"auto",color:"var(--text-3)"}} onClick={()=>setSuccess(null)}>✕</button>
        </div>
      )}

      <div className="card">
        <form onSubmit={submit} style={{display:"flex",flexDirection:"column",gap:16}}>
          <label className="field-label">Recipient User ID
            <input type="number" min="1" value={receiverId} onChange={e=>setReceiverId(e.target.value)}
              placeholder="Enter user ID" required />
          </label>
          <label className="field-label">Amount
            <div className="quick-amounts" style={{marginBottom:8}}>
              {[100,250,500,1000].map(q=>(
                <button key={q} type="button" className={`quick-chip ${amount==q?"quick-chip-active":""}`} onClick={()=>setAmount(String(q))}>₹{q}</button>
              ))}
            </div>
            <div className="amount-field">
              <span className="amount-prefix">₹</span>
              <input type="number" min="1" step="0.01" value={amount} onChange={e=>setAmount(e.target.value)} placeholder="0.00" required />
            </div>
          </label>
          <label className="field-label">Note (optional)
            <input value={note} onChange={e=>setNote(e.target.value)} placeholder="Lunch, rent, etc." maxLength={255} />
          </label>
          {error && <p className="form-error">{error}</p>}
          <button className="btn-primary btn-full" disabled={loading||!receiverId||!amount}>
            {loading ? "Sending…" : `Send ₹${amount||0}`}
          </button>
        </form>
      </div>
      <p className="info-text">🔒 Transfers are instant and fraud-monitored.</p>
    </div>
  );
}
