# WalletX

Full-stack digital wallet — FastAPI + React + Supabase PostgreSQL.

## Quick Start

### Backend
```bash
# From the walletx/ root directory
pip install -r backend/requirements.txt
cp .env .env   # already in place
uvicorn backend.main:app --reload
```
API: http://localhost:8000  
Docs: http://localhost:8000/docs

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App: http://localhost:5173  
Admin: http://localhost:5173/admin

## Admin Login
Email: `admin@walletx.com`  
Password: `Admin@WalletX2024`  
(Set ADMIN_EMAIL and ADMIN_PASSWORD in .env to change)

## Deploy

### Backend → Railway (free)
1. Push `backend/` to GitHub
2. New project on railway.app → Deploy from GitHub
3. Add all env vars from `.env` in Railway dashboard
4. Copy the Railway URL

### Frontend → Vercel (free)
1. Push `frontend/` to GitHub
2. Import on vercel.com
3. Set `VITE_API_URL=https://your-railway-url.railway.app`
4. Also update `CORS_ORIGINS` in Railway env vars to include your Vercel URL

## Security Fixes Applied
- OTP uses `secrets` module (not `random`)
- `hmac.compare_digest` for timing-safe OTP and admin password comparison
- `SELECT FOR UPDATE` on all wallet operations (deadlock-safe)
- Explicit CORS origins (no wildcard)
- Rate limiting on all auth endpoints including `/admin/login` (5/min)
- SECRET_KEY generates ephemeral key if not set, warns loudly
- Admin accounts cannot be deactivated via API
- Fraud checks exclude current transaction to avoid false positives
- `get_transactions` capped at 200 rows with eager-loaded fraud alerts (no N+1)
- Password strength enforced on both register and profile update
- `DATABASE_URL` and `ADMIN_PASSWORD` required in production validation
- `.db` / `.env` files in `.gitignore`
- Deprecated `on_event` replaced with `lifespan`
- Fraud thresholds configurable via env vars

## ⚠️ Before Deploying
1. Rotate your Supabase DB password (old one was in source)
2. Generate a new Gmail App Password (old one was in source)
3. Set all env vars in Railway dashboard — never commit `.env`
4. Update `CORS_ORIGINS` in Railway to include your Vercel URL
