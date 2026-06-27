const TABS = [
  ["⊞","Home","dashboard"],
  ["◈","Wallet","wallet"],
  ["⇄","Send","transfer"],
  ["≡","History","transactions"],
  ["◯","Profile","profile"],
];

export default function Navbar({ page, setPage }) {
  return (
    <nav className="bottom-nav">
      {TABS.map(([icon, label, id]) => (
        <button key={id} className={`nav-item ${page===id?"nav-active":""}`} onClick={() => setPage(id)}>
          <span className="nav-icon">{icon}</span>
          <span className="nav-label">{label}</span>
        </button>
      ))}
    </nav>
  );
}
