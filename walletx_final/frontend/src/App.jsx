import { useState } from "react";
import Login from "./pages/Login";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import Dashboard from "./pages/Dashboard";
import Wallet from "./pages/Wallet";
import Transfer from "./pages/Transfer";
import Transactions from "./pages/Transactions";
import Profile from "./pages/Profile";
import Navbar from "./components/Navbar";

export default function App() {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("wx_user")); } catch { return null; }
  });
  const [page, setPage] = useState("dashboard");

  // Detect /admin route
  const isAdminRoute = window.location.pathname === "/admin";

  function handleLogin(u) { setUser(u); setPage("dashboard"); }
  function handleLogout() { setUser(null); }

  if (isAdminRoute) {
    if (!user?.is_admin) return <AdminLogin onLogin={handleLogin} />;
    return <AdminDashboard onLogout={handleLogout} />;
  }

  if (!user) return <Login onLogin={handleLogin} />;

  const pages = {
    dashboard: <Dashboard user={user} setPage={setPage} />,
    wallet:    <Wallet />,
    transfer:  <Transfer user={user} />,
    transactions: <Transactions user={user} />,
    profile:   <Profile user={user} onLogout={handleLogout} />,
  };

  return (
    <div className="app-shell">
      <main className="app-main">{pages[page]}</main>
      <Navbar page={page} setPage={setPage} />
    </div>
  );
}
