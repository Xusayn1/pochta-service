## 🏗️ Project Architecture
```
pochta-service/
├── .github/ # GitHub workflows (CI/CD)
│ └── workflows/
│ ├── deploy.yml
│ └── tests.yml
│
├── backend/ # Django backend
│ ├── apps/
│ │ ├── users/ # Foydalanuvchilar (auth, profil)
│ │ ├── orders/ # Buyurtmalar
│ │ ├── shipments/ # Yetkazib berishlar
│ │ ├── locations/ # Shahar/viloyatlar, filiallar
│ │ ├── payments/ # To‘lov tizimi
│ │ ├── tracking/ # Trek-nomerlar, kuzatuv
│ │ ├── notifications/ # SMS, email, push bildirishnomalar
│ │ ├── reports/ # Hisobotlar
│ │ └── api/ # API v1/v2 (REST + WebSocket)
│ ├── core/ # Asosiy sozlamalar
│ │ ├── settings.py
│ │ ├── urls.py
│ │ └── wsgi.py
│ ├── static/ # Statik fayllar
│ ├── media/ # Yuklangan fayllar
│ ├── templates/ # HTML template-lar
│ ├── requirements.txt
│ └── manage.py
│
├── frontend/ # React/Vue.js frontend
│ ├── public/
│ │ └── index.html
│ ├── src/
│ │ ├── components/ # React komponentlari
│ │ ├── pages/ # Sahifalar
│ │ ├── services/ # API call'lar
│ │ └── utils/ # Yordamchi funksiyalar
│ └── package.json
│
├── telegram_bot/ # Telegram bot
│ ├── handlers/ # Message handlerlar
│ ├── keyboards/ # Klaviatura tugmalari
│ ├── utils/ # Yordamchi funksiyalar
│ └── bot.py # Bot asosiy fayli
│
├── docker/ # Docker konfiguratsiyalar
│ ├── Dockerfile.backend
│ ├── Dockerfile.frontend
│ └── docker-compose.yml
│
├── docs/ # Hujjatlar
│ ├── api.md
│ ├── database.md
│ └── deployment.md
│
├── scripts/ # Yordamchi skriptlar
│ ├── backup.sh
│ └── seed_data.py
│
├── .env.example # Environment o'zgaruvchilar namunasi
├── .gitignore
└── README.md
```
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------
---------------------------------------------------------------------------------------

# 📮 Pochta Service - Intelligent Delivery Platform

[![Django](https://img.shields.io/badge/Django-5.0-green)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue)](https://core.telegram.org/bots)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## 🚀 About the Project

**Pochta Service** is a modern, 24/7 delivery platform connecting cities and regions across Uzbekistan. It enables users to send various items quickly, track shipments in real-time, and manage deliveries through both a web interface and Telegram bot.

### ✨ Key Features

- 🌍 **Intercity & Regional Delivery** - Seamless shipping between cities and districts
- 📦 **Multi-item Support** - Documents, packages, fragile items, and more
- 🔍 **Real-time Tracking** - Track shipments with unique tracking numbers
- 🤖 **Telegram Bot Integration** - Full functionality via Telegram mini-app
- 💳 **Multiple Payment Options** - Click, Payme, cash, bank transfers
- 📱 **Responsive Web App** - React-based modern dashboard
- 🔔 **Smart Notifications** - SMS, email, and push notifications
- 📊 **Analytics Dashboard** - Real-time delivery statistics
- 👥 **Role-based Access** - User, courier, admin, and partner roles

### 🎯 Target Audience

- **Individual Users** - Send personal packages to family/friends
- **Businesses** - Regular shipping needs, B2B logistics
- **E-commerce Platforms** - Integration with online stores
- **Couriers** - Real-time delivery management

## 🏗️ System Architecture
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Web App │ │ Telegram Bot│ │ Mobile App │
│ (React) │ │ (Python) │ │ (Future) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘
│ │ │
└───────────────────┼───────────────────┘
│
┌──────▼──────┐
│ REST API │
│ (Django) │
└──────┬──────┘
│
┌───────────────────┼───────────────────┐
│ │ │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
│ PostgreSQL │ │ Redis │ │ Celery │
│ (Main DB) │ │ (Cache) │ │ (Tasks) │
└─────────────┘ └─────────────┘ └─────────────┘

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (main), Redis (cache)
- **Task Queue**: Celery + Redis
- **Real-time**: Django Channels + WebSockets
- **Storage**: AWS S3 / Local storage for media

### Frontend
- **Framework**: React 18 + TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI / Tailwind CSS
- **Maps Integration**: Yandex/Google Maps API

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx + Gunicorn
- **Cloud**: DigitalOcean / AWS
- **CI/CD**: GitHub Actions

### Additional Services
- **Telegram Bot**: python-telegram-bot v20+
- **SMS Service**: Twilio / local SMS providers
- **Payments**: Click, Payme, Stripe API
- **Email**: SMTP / SendGrid

## 📦 Core Modules

### 1. User Management (`users`)
- Registration/authentication (JWT)
- Profile management with addresses
- Role-based permissions (user, courier, admin)
- KYC verification for businesses

### 2. Order Management (`orders`)
- Create/edit/cancel orders
- Calculate delivery cost dynamically
- Package specifications (weight, dimensions)
- Special handling instructions

### 3. Shipment Tracking (`shipments`)
- Unique tracking number generation
- Real-time status updates
- Location history with timestamps
- Estimated delivery time (EDT)

### 4. Locations (`locations`)
- Region/city/district hierarchy
- Pickup/drop-off points
- Distance and time matrix
- Serviceable area validation

### 5. Payment System (`payments`)
- Multiple payment gateways
- Invoice generation
- Refund handling
- Transaction history

### 6. Notifications (`notifications`)
- Email notifications
- SMS alerts
- Telegram messages
- Push notifications (web/mobile)

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+
- Docker (optional)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pochta-service.git
cd pochta-service

--------------------------------------------------
Backend setup
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
cd backend
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
----------------------------------
Frontend setup

bash
cd frontend
npm install
npm start
Telegram Bot setup
---------------------------------
Telegram Bot setup
bash
cd telegram_bot
pip install -r requirements.txt
python bot.py
--------------------------------
Run with Docker
bash
docker-compose up -d
