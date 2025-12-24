
# E-Waste Management System ♻️

[![Built with Flask](https://img.shields.io/badge/Flask-2.x-blue.svg)]()
[![SQLite](https://img.shields.io/badge/DB-SQLite-green.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

A web-based system for **E-Waste collection, categorization, tracking, and analytics**.
It connects **citizens, recyclers, and administrators** for transparent waste management.

---

## ✨ Features

* 👤 **User/Auth**: Register/Login (Email/Password) + Google OAuth
* 🔐 **Roles**: `user`, `recycler`, `admin`
* 🗺️ **Pickup Requests**: Raise e-waste pickup requests with location
* 🧾 **Inventory & Tracking**: Item type, weight, status, recycler assignment
* 📊 **Analytics Dashboard**: Charts by type/area/time period
* 🧠 **GPT-Powered Chatbot**: AI chatbot for FAQs and assistance
* 🆘 **Report & Feedback**: File complaints, give feedback
* 🗂️ **Admin Panel**: Manage users, pickups, recyclers, and reports
* 📨 **Email/OTP**: Forgot Password with OTP verification
* 🗺️ **Maps Integration**: Pickup locations shown on Google Maps
* 📥 **CSV Import/Export**: Data export/import for admins

---

## 🏗️ Tech Stack

* **Backend**: Python, Flask (Blueprints, Jinja2)
* **Database**: SQLite (`ewaste.db`) / SQLAlchemy (optional)
* **Frontend**: HTML5, Bootstrap 5, JavaScript
* **Auth**: Flask-Login, Google OAuth 2.0
* **Charts**: Chart.js / Recharts
* **Maps**: Google Maps JS API
* **AI**:  (Chatbot)
* **Deploy**: Gunicorn + Render/Heroku/Local

---

## 📁 Project Structure

```
e_waste_portal/
├─ app.py
├─ db.py
├─ models.py              # (optional) SQLAlchemy models
├─ auth.py                # login/register/Google OAuth, OTP
├─ admin.py               # admin routes
├─ analytics.py           # charts/data APIs
├─ utils.py               # helpers: email, otp, validators
├─ data/
│  └─ ewaste.db
├─ static/
│  ├─ css/  ├─ js/  └─ images/
├─ templates/
│  ├─ base.html  ├─ index.html  ├─ register.html  ├─ login.html
│  ├─ dashboard.html  ├─ admin.html  ├─ analytics.html
│  ├─ contact.html  ├─ forgot_password.html  ├─ reset_password.html
│  └─ chatbot.html
└─ README.md
```

---

## 🧮 Database Schema (SQLite – Suggested)

**users**

* id (PK), name, email (unique), password\_hash, role, provider, created\_at

**pickup\_requests**

* id (PK), user\_id (FK), item\_type, weight\_kg, address, latitude, longitude, status(`pending/assigned/picked/recycled`), recycler\_id(FK), created\_at

**recyclers**

* id (PK), name, contact, service\_areas, rating

**tickets**

* id (PK), user\_id, subject, message, status, created\_at, closed\_at

**activity\_logs**

* id (PK), actor\_id, action, entity, entity\_id, meta\_json, created\_at

---

## 🔐 .env Configuration

```
FLASK_SECRET_KEY=change_me
DATABASE_URL=sqlite:///data/ewaste.db
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
OAUTH_REDIRECT_URI=http://localhost:5000/auth/google/callback
OPENAI_API_KEY=your_openai_key
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=app_password
MAPS_API_KEY=your_google_maps_key
```

---

## ▶️ Local Setup

```bash
# 1) Clone repo
git clone https://github.com/yourname/e_waste_portal.git
cd e_waste_portal

# 2) Create virtualenv
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Setup env
cp .env.example .env   # or add manually

# 5) Initialize DB
python db.py init   # or as per your script

# 6) Run server
python app.py
# visit: http://localhost:5000
```

---

## 🔌 API / Routes

* `GET /` → Home Page
* `GET|POST /register`, `/login`, `/logout`
* `GET /auth/google` → Google OAuth flow
* `GET /dashboard` → User dashboard
* `GET|POST /pickup/new` → Create pickup request
* `GET /pickup/<id>` → Pickup details
* `POST /pickup/<id>/assign` → Admin assigns recycler
* `GET /analytics` → Charts & filters (date, area, item\_type, role)
* `GET|POST /forgot-password` → Email OTP
* `GET|POST /reset-password` → Reset password
* `GET /chatbot` → GPT chatbot widget
* `GET /admin` → Admin panel
* `GET /export.csv` / `POST /import.csv`

---

## 🧭 User Flow

1. User registers/logs in (or via Google OAuth)
2. Creates a pickup request with address/location + e-waste details
3. Admin assigns the request to a recycler
4. Status updates: `pending → assigned → picked → recycled`
5. Analytics dashboard shows reports by type, area, timeline

---

## 🗺️ Maps Integration

* Google Maps JS API used in `dashboard.html`
* Pickup requests displayed as map markers
* Default viewport example: Govind Nagar, Nashik

---

## 🤖 Chatbot (In-App)

* Embedded in `base.html` as a widget
* Backend `/chatbot` route connects 
* Handles FAQs, location help, process queries

---

## 🔒 Security

* Passwords hashed with `werkzeug.security`
* CSRF protection with Flask-WTF (optional)
* Role-based access decorators
* Sensitive keys stored in `.env`

---

## 🧪 Testing

```bash
pytest -q
# or
python -m unittest
```

```MD

## 🧩 Contributing

1. Open an Issue / Feature Request
2. Fork → Create feature branch (`feat/<name>`)
3. Submit a PR (with screenshots/demo)

---

## 📜 License

MIT License — see `LICENSE` file.

---

## 🙌 Acknowledgements

* Thanks to **Nashik local administration & open datasets** for guidance
* Libraries: Flask, Bootstrap, Chart.js, Google APIs
* **Project Team Roles**: Backend, Frontend, Data/Analytics, Admin Ops

