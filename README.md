# Personal Finance AI App

![Language](https://img.shields.io/badge/Language-Python-blue)
![Framework](https://img.shields.io/badge/Framework-Flask-black)
![Database](https://img.shields.io/badge/Database-MariaDB-orange)
![AI](https://img.shields.io/badge/LLM-phi3-green)
![Runtime](https://img.shields.io/badge/AI%20Runtime-Ollama-purple)
![Status](https://img.shields.io/badge/Status-Working-brightgreen)

---

## Overview

A full-stack web application that allows users to track expenses, manage budgets, and receive AI-powered financial insights using a local Large Language Model (LLM).

The system is designed as a personal financial assistant, combining traditional finance tracking with intelligent analysis.

---

## Features

- User authentication (login and signup)
- Transaction tracking (income and expenses)
- Category-based spending analysis
- Budget management with limit tracking
- Visual dashboard with charts
- Monthly filtering of transactions
- AI-powered financial analysis
- AI memory system (stores past insights)
- Modernized UI with improved layout and styling

---

## Technology Stack

### Backend
- Python (Flask)

### Database
- MariaDB

### Frontend
- HTML
- CSS
- JavaScript (Chart.js)

### AI / LLM
- Ollama (local inference server)
- Model: phi3

---

## AI Functionality

The AI assistant analyzes user spending data and provides:

- Overspending detection
- Budget warnings
- Spending prioritization
- Actionable financial advice
- Pattern recognition using stored past insights

All AI processing runs locally using Ollama.

---

## Styling and UI

The interface has been redesigned to follow modern UI principles:

- Improved spacing and layout
- Card-based structure
- Clean visual hierarchy
- Glassmorphism-inspired elements

Styling improvements were implemented with assistance from Anthropic Claude.

---

## Project Structure

    project/
    │
    ├── app.py
    ├── config.py
    ├── .env
    ├── database/
    ├── static/
    │   └── style.css
    ├── templates/
    │   ├── base.html
    │   ├── dashboard.html
    │   ├── login.html
    │   ├── budget.html
    │   ├── analysis.html
    │   └── chat.html
    └── README.md

---

## Setup Instructions

### 1. Clone repository

    git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
    cd YOUR_REPO

---

### 2. Create .env

    DB_HOST=localhost
    DB_USER=your_user
    DB_PASSWORD=your_password
    DB_NAME=personal_assistant

    SECRET_KEY=your_secret_key

    OLLAMA_URL=http://localhost:11434
    OLLAMA_MODEL=phi3

---

### 3. Install dependencies

    pip install -r requirements.txt

---

### 4. Start MariaDB

Ensure your database is running and configured.

---

### 5. Start Ollama

    ollama run phi3

---

### 6. Run the app

    python app.py

---

## Notes

- .env is ignored via .gitignore
- Do not expose credentials in code
- Ollama must be running locally for AI features
- For deployment, Ollama must also run on the server

---

## Future Improvements

- Real-time dashboard alerts
- Transaction editing functionality
- Advanced analytics and trend comparison