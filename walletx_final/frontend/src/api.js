// VITE_API_URL must be set in Vercel environment variables.
// In local dev, the Vite proxy (vite.config.js) routes /auth, /wallet etc to
// localhost:8000, so BASE is unused locally when going through the proxy.
const BASE = import.meta.env.VITE_API_URL ?? "";

function token() {
  return localStorage.getItem("wx_token");
}

async function req(method, path, body = null) {
  const headers = { "Content-Type": "application/json" };
  if (token()) headers["Authorization"] = `Bearer ${token()}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data?.detail || "Request failed");
  return data;
}

export const auth = {
  requestOtp: (email, password) => req("POST", "/auth/login/request-otp", { email, password }),
  verifyOtp: (email, code) => req("POST", "/auth/login/verify-otp", { email, code }),
  register: (name, email, password) => req("POST", "/auth/register", { name, email, password }),
  logout: () => req("POST", "/auth/logout"),
  adminLogin: (email, password) => req("POST", "/admin/login", { email, password }),
};

export const wallet = {
  get: () => req("GET", "/wallet"),
  add: (amount) => req("POST", "/wallet/add", { amount }),
  withdraw: (amount) => req("POST", "/wallet/withdraw", { amount }),
  transfer: (receiver_id, amount, note) =>
    req("POST", "/wallet/transfer", { receiver_id, amount, note }),
  transactions: () => req("GET", "/wallet/transactions"),
};

export const profile = {
  get: () => req("GET", "/profile"),
  update: (data) => req("PUT", "/profile", data),
};

export const admin = {
  stats: () => req("GET", "/admin/stats"),
  users: () => req("GET", "/admin/users"),
  fraudAlerts: () => req("GET", "/admin/fraud-alerts"),
  transactions: () => req("GET", "/admin/transactions"),
  deactivate: (id) => req("PUT", `/admin/users/${id}/deactivate`),
};
