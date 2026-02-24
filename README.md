# datamind.

> **AI-powered data analyst.** Upload any file, get instant insights, charts, and answers — no analyst needed.

---

## What is DataMind?

DataMind is a full-stack SaaS application that replaces the manual work of a data analyst with AI. You upload a file in any format — CSV, Excel, PDF, or an image — and within seconds you get a live PostgreSQL database, auto-generated visualizations, AI-written insights, and a natural language chatbot that converts plain English into SQL queries.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     React Frontend                       │
│              (Vite + Tailwind + Recharts)                │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP (REST API)
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                        │
└──────┬─────────────────┬──────────────────┬─────────────┘
       │                 │                  │
┌──────▼──────┐  ┌───────▼──────┐  ┌───────▼──────┐
│   Layer 1   │  │   Layer 2    │  │   Layer 3    │
│  Ingestion  │  │  SQL Engine  │  │  Dashboard   │
│             │  │              │  │  + AI Insights│
│ CSV / Excel │  │  DataFrame → │  │              │
│ PDF / Image │  │  PostgreSQL  │  │  Gemini API  │
│ OCR / Parse │  │  (Supabase)  │  │              │
└─────────────┘  └──────────────┘  └──────────────┘
                         │
              ┌──────────▼──────────┐
              │  PostgreSQL Cloud   │
              │     (Supabase)      │
              │                     │
              │  • users            │
              │  • uploads          │
              │  • query_logs       │
              │  • dynamic tables   │
              └─────────────────────┘
```

---

## Features

### Layer 1 — Universal Data Ingestion
Accepts any file format and converts it into a clean, structured Pandas DataFrame. Handles messy real-world data including merged cells, multi-page PDFs, and low-resolution scanned images.

- **CSV / Excel** via Pandas
- **PDF tables** via pdfplumber
- **Images** via EasyOCR
- Automatic column name cleaning, type inference, and whitespace stripping

### Layer 2 — Dynamic SQL Engine
Pushes any DataFrame into a live PostgreSQL database with automatic schema inference. Every upload creates a uniquely named, isolated table. All uploads are logged with UUIDs for full traceability.

- Dynamic table creation via SQLAlchemy
- Correct type inference (TEXT, BIGINT, FLOAT, TIMESTAMP)
- Upload tracking in a `uploads` metadata table
- Schema inspection for LLM context

### Layer 3 — Auto Dashboard & AI Insights
Reads from the live PostgreSQL table and auto-generates a full visual dashboard — no hardcoding, works for any dataset. AI analysis is powered by Google Gemini.

- Auto bar charts, line charts, correlation heatmaps
- Key metric cards (sum, avg, min, max per numeric column)
- AI-written insights, trends, and business recommendations
- Raw data preview table

### Layer 4 — English to SQL Chatbot *(in progress)*
A natural language interface where users type plain English questions and get SQL-powered answers back in real time.

- English → SQL conversion via LLM
- Runs queries against the live PostgreSQL table
- Returns results as tables or charts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, Uvicorn |
| Database | PostgreSQL (Supabase) |
| ORM | SQLAlchemy |
| Data Processing | Pandas, NumPy |
| PDF Parsing | pdfplumber |
| OCR | EasyOCR |
| AI / LLM | Google Gemini API |
| Environment | Python 3.13, venv |

---

## Project Structure

```
datamind/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   └── routes/
│       ├── upload.py            # File upload endpoint
│       └── dashboard.py         # Dashboard data endpoint
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Home.jsx         # Landing page
│       │   └── Dashboard.jsx    # Dashboard page
│       ├── components/
│       │   ├── MetricCard.jsx
│       │   ├── BarChart.jsx
│       │   ├── LineChart.jsx
│       │   ├── DataTable.jsx
│       │   └── InsightsCard.jsx
│       └── api/
│           └── client.js        # Axios API client
├── layers/
│   ├── layer1_ingestion/
│   │   └── ingestion.py         # File parsers
│   ├── layer2_sql/
│   │   └── sql_engine.py        # PostgreSQL engine
│   ├── layer3_dashboard/
│   │   └── insights.py          # Gemini AI insights
│   └── layer4_chatbot/          # Coming soon
├── utils/
│   └── database.py              # DB connection test
├── uploads/                     # Temporary file storage
├── .env                         # Environment variables (not committed)
└── requirements.txt
```

---

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Supabase](https://supabase.com) account (free tier)
- A [Google AI Studio](https://aistudio.google.com) API key (free tier)

### 1. Clone the repo
```bash
git clone https://github.com/DefinitelyMrityunjay/datamind.git
cd datamind
```

### 2. Set up the backend
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a `.env` file in the root:
```
DATABASE_URL=your_supabase_postgresql_connection_string
GEMINI_API_KEY=your_google_gemini_api_key
```

### 4. Set up the database
Run this SQL in your Supabase SQL editor:
```sql
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    plan VARCHAR(50) DEFAULT 'free'
);

CREATE TABLE IF NOT EXISTS uploads (
    upload_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    table_name VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'processing'
);

CREATE TABLE IF NOT EXISTS query_logs (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    upload_id UUID REFERENCES uploads(upload_id),
    english_input TEXT,
    generated_sql TEXT,
    executed_at TIMESTAMP DEFAULT NOW(),
    success BOOLEAN
);
```

### 5. Start the backend
```bash
cd backend
uvicorn main:app --reload
```
API runs at `http://127.0.0.1:8000`
API docs at `http://127.0.0.1:8000/docs`

### 6. Start the frontend
```bash
cd frontend
npm install
npm run dev
```
App runs at `http://localhost:5173`

---

## Screenshots

<img width="1456" height="807" alt="image" src="https://github.com/user-attachments/assets/212b462e-0d79-4571-8818-f9a2bd554ac9" />
<img width="1456" height="807" alt="image" src="https://github.com/user-attachments/assets/e1eecc94-a692-40fa-927e-d65d40319c56" />
<img width="1456" height="807" alt="image" src="https://github.com/user-attachments/assets/d0939c07-5f61-4c9a-b92a-1fdccdc56457" />
<img width="1456" height="426" alt="image" src="https://github.com/user-attachments/assets/f3431273-cade-41af-986d-1f53559df9ff" />




---

## Roadmap

- [x] Layer 1 — Universal file ingestion (CSV, Excel, PDF, Image)
- [x] Layer 2 — Dynamic PostgreSQL table generation
- [x] Layer 3 — Auto dashboard with AI insights
- [x] React frontend with FastAPI backend
- [ ] Layer 4 — English to SQL chatbot
- [ ] User authentication (Supabase Auth)
- [ ] Upload history page
- [ ] Cloud deployment (Vercel + Railway)
- [ ] Multi-sheet Excel support
- [ ] Export dashboard as PDF

---

## Author

**Mrityunjay** — [github.com/DefinitelyMrityunjay](https://github.com/DefinitelyMrityunjay)

---

*Built as a portfolio project to demonstrate end-to-end data engineering, AI integration, and full-stack product development.*
