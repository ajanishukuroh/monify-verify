# Monify Verify 🔐✅

> **Verify Before You Deliver.**
>
> A merchant trust layer built on the Monnify Payment Gateway. Enables businesses to verify payments in real time, access a secure QR-based verification page, and maintain an auditable payment history.

---

## Quick Start

### 1. Clone / Open the project

```
cd monify-verify
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy `.env.example` to `.env` (already pre-filled with sandbox credentials):

```bash
cp .env.example .env
```

Edit `.env` and add your Monnify credentials:

```
MONNIFY_API_KEY=MK_TEST_VAXBHVL9W2
MONNIFY_SECRET_KEY=DQZRCKYX8EPV9X25LV5Y7DL8KULV0FAR
MONNIFY_CONTRACT_CODE=0175904349
MONNIFY_BASE_URL=https://sandbox.monnify.com
```

### 5. Run the server

```bash
python run.py
```

Visit: **http://localhost:5000/landing**

---

## Pages

| URL | Description |
|---|---|
| `/landing` | Public landing page |
| `/register` | Create a merchant account |
| `/login` | Merchant login |
| `/dashboard` | Merchant dashboard |
| `/payment/create` | Create a new payment |
| `/payment/history` | Payment history with filters |
| `/payment/<ref>/audit` | Audit timeline for a payment |
| `/payment/dev/simulate-webhook` | 🧪 Simulate Monnify webhook (dev only) |
| `/verify/<reference>` | **Public QR verification page** |

---

## Testing the Full Flow (No ngrok needed)

1. Register a merchant account at `/register`
2. Create a payment at `/payment/create` → redirects to Monnify checkout
3. (Skip actual payment OR complete it in sandbox)
4. Go to **Dev Simulator** at `/payment/dev/simulate-webhook`
5. The reference is auto-filled — click "Simulate Webhook"
6. Payment status updates to PAID → QR code generated
7. In Payment History, click **QR** to download the QR code
8. Scan the QR or go to `/verify/<reference>` to see the verification page

---

## Monnify Webhook Setup (Production)

For real webhooks, set your webhook URL in the Monnify dashboard to:

```
https://your-domain.com/payment/webhook
```

For local testing, use [ngrok](https://ngrok.com):

```bash
ngrok http 5000
# Then set: https://xxxx.ngrok.io/payment/webhook
```

---

## Tech Stack

- **Backend**: Flask + SQLAlchemy
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Frontend**: HTML + Tailwind CSS (CDN) + Vanilla JS
- **Payments**: Monnify Sandbox API
- **QR Codes**: Python `qrcode` library

---

## Folder Structure

```
monify-verify/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Environment config
│   ├── database.py         # SQLAlchemy instance
│   ├── models/             # User, Payment, AuditLog
│   ├── routes/             # auth, dashboard, payment, verify
│   ├── services/           # monnify, qr, audit
│   └── utils/              # auth helpers, formatters
├── frontend/
│   ├── templates/          # Jinja2 templates
│   └── static/             # CSS + JS
├── qr_codes/               # Generated QR PNGs
├── uploads/                # Reserved for future use
├── .env                    # Environment variables
├── requirements.txt
├── run.py                  # Entry point
└── README.md
```

---

## Deployment (Render)

1. Push to GitHub
2. Create a new Web Service on [Render](https://render.com)
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn run:app`
5. Add environment variables from `.env`

---

Built for **Hackathon 2024** · Powered by **Monnify**
