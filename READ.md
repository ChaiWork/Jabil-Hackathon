# Jabil Trade AI Assistant (JTAA)

JTAA is an enterprise-grade, AI-powered trade compliance desktop application designed to scrape, structure, and audit import tariff rates, ensuring trade rules adhere to Free Trade Agreements (FTAs) like ACFTA and USMCA.

---

## 🔍 What JTAA Does (System Overview)

In global logistics, shipping components across international borders requires matching every imported part with the correct government-mandated **Harmonized System (HS) tariff code**. Manual classification is extremely slow (taking 30–40 minutes per invoice) and carries high risks of human error, leading to customs delays or severe financial penalties.

**JTAA solves this by automating the audit process:**

1. **Extracts Invoice Data**: A compliance officer drags and drops a supplier invoice PDF. JTAA automatically extracts all part numbers, descriptions, values, and origin details.
2. **Finds Matching Rules**: It semantically searches a local vector knowledge base (updated automatically by web crawlers scraping trade portals like MITI, WTO, and ASEAN) for relevant trade laws and Free Trade Agreements.
3. **Recommends & Calculates**: Using Google Gemini, it matches the imported part to its correct HS Code, explains its reasoning step-by-step, and computes the exact customs duties and landed costs.
4. **Human Review & SAP Sync**: The auditor reviews the AI's suggestions on a desktop dashboard, makes adjustments if needed, and exports the approved records directly into an SAP-compatible Excel spreadsheet.

---

## 💡 Key Features (Proposed Solution)

JTAA leverages AI to automate complex trade compliance activities through five key features:

*   **Intelligent Ingestion (IDP)**: Uses a hybrid fallback parser combining `pdfplumber` (for digital text PDFs) and `EasyOCR` (for scanned invoice documents) to instantly extract supplier names, part numbers, product descriptions, declared values, and country of origin from raw invoice PDFs.
*   **Dynamic Knowledge Base**: Automatically crawls trade portals (like MITI, WTO, ASEAN) for real-time tariff rules, storing and indexing them in a **ChromaDB** vector store. It utilizes semantic search to automatically find applicable Free Trade Agreements (FTAs) and historical customs classifications.
*   **Reasoning Engine (Google Gemini)**: Uses Retrieval-Augmented Generation (RAG) to generate recommended HS codes, tariff percentages, and a transparent, step-by-step reasoning trace based only on validated, retrieved regulations to prevent AI hallucinations.
*   **Financial Calculation Engine**: Computes estimated import duties, tax savings, and total landed costs dynamically based on the active trade agreements.
*   **Human-in-the-Loop Compliance Dashboard**: Provides a premium dark-themed **PySide6** desktop interface for compliance managers to review the AI's reasoning, manually override classifications, log audit activities in a history ledger, and export audited records directly to SAP-compatible Excel files (`SAP_Export.xlsx`).

---

## 🏗️ System Architecture

The application is built on a **layered, micro-services-supported desktop architecture** using PySide6 (PyQt), Google Gemini 1.5/2.0 API, MongoDB, PostgreSQL, and ChromaDB.

```mermaid
graph TD
    subgraph UI ["1. Presentation Layer (PySide6 UI)"]
        UI_Main[MainWindow]
        UI_Dash[Dashboard Page]
        UI_Ship[Shipments List / Audit Workbench]
        UI_Crawl[Crawler Console]
    end

    subgraph Crawler ["2. Integration & Ingestion Layer"]
        Scraper[Crawl4AI Web Scraper]
        OCR[PDF Extractor / OCR Parser]
    end

    subgraph Storage ["3. Storage Layer (Dockerized Cluster)"]
        Mongo[(MongoDB: Raw Ingestion Landing Zone)]
        Postgres[(PostgreSQL: Clean Relational DB)]
        Chroma[(ChromaDB: Vector Search Store)]
    end

    subgraph AI ["4. RAG & AI Reasoning Layer"]
        Gemini[Google Gemini API]
        RAG[RAG Semantic Matcher]
    end

    subgraph Integration ["5. Business Integration Service"]
        Calc[Duty Calculator]
        Export[Excel SAP Exporter]
        Approve[Approval Engine]
    end

    %% Data Ingestion Flows
    Scraper -->|Raw HTML/JSON| Mongo
    OCR -->|Raw Text| Mongo
    
    %% ETL Pipeline
    Mongo -->|Raw Docs| ETL[ETL Pipeline]
    ETL -->|Clean & Structure| Gemini
    Gemini -->|Structured Rules JSON| Postgres
    Postgres -->|Tariff Records| Embed[Chroma Embedder]
    Embed --> Chroma

    %% Auditing Flows
    UI_Ship -->|Requests Audit| RAG
    RAG -->|Semantic Query| Chroma
    Chroma -->|Legal Context| RAG
    RAG -->|Enriched Prompt| Gemini
    Gemini -->|Compliance Recs JSON| UI_Ship
    
    %% Approval Flows
    UI_Ship -->|Review & Action| Approve
    Approve -->|Execute Math| Calc
    Approve -->|Export spreadsheet| Export
    Approve -->|Log Transaction| Postgres
    Postgres -->|Refresh Metrics| UI_Dash
```

### 🗄️ Polyglot Persistence Strategy (Why We Use 3 Databases)
To guarantee enterprise reliability and performance, we run a containerized database cluster separating operations, ingestion, and AI reasoning:
1.  **MongoDB**: Acts as our schema-free raw data landing zone. Web scraping formats change frequently; saving raw HTML/JSON directly to Mongo prevents crawler errors from breaking down downstream processes.
2.  **PostgreSQL**: Handles operational system state, role permissions, transaction histories, and approved shipment records with 100% ACID compliance and security.
3.  **ChromaDB**: Acts as our high-speed semantic search index, converting legal text into vector embeddings. This allows us to perform conceptual matching on part descriptions in milliseconds.

---

## 📁 Repository Structure

```text
Jabil-Hackathon/
│
├── JTCA/
│   ├── crawler/
│   │   └── crawl4ai_service.py     # Web crawler (WTO, MITI, custom portals)
│   │
│   ├── database/
│   │   ├── db.py                   # PostgreSQL queries & SQLite fallbacks
│   │   ├── etl_pipeline.py         # MongoDB -> Gemini extraction -> PostgreSQL
│   │   ├── mongo_db.py             # MongoDB connection & ingestion utilities
│   │   ├── postgres_db.py          # PostgreSQL schema initialization & connection
│   │   └── schema_postgres.sql     # PostgreSQL relational table definitions
│   │
│   ├── llm/
│   │   └── gemini_service.py       # Gemini API client & Pydantic structured output mapping
│   │
│   ├── ocr/
│   │   └── pdf_extractor.py        # PDF parser & OCR text extraction
│   │
│   ├── rag/
│   │   ├── embeddings.py           # Text embedding generator for ChromaDB
│   │   ├── retrieval.py            # RAG queries combining Semantic search + LLM
│   │   └── vector_store.py         # ChromaDB client & vector index refresh pipeline
│   │
│   ├── services/
│   │   ├── approval_engine.py      # Automated compliance validation algorithms
│   │   └── session.py              # User authentication state & role permission manager
│   │
│   ├── ui/
│   │   ├── main_window.py          # Application container, sidebar layout, themes
│   │   ├── dashboard.py            # KPI widgets, shipment stats, interactive charts
│   │   ├── crawler_page.py         # Crawler controls, log window, parsing rules grid
│   │   ├── shipments_list.py       # Grid of imported parts & audit queues
│   │   ├── shipment_view.py        # Compliance assessment panel & reasoning visualizer
│   │   ├── reports_page.py         # Audit export & dashboard report utilities
│   │   └── login_dialog.py         # Role-based user authentication modal
│   │
│   ├── main.py                     # Main application entry point & splash screen
│   ├── docker-compose.yml          # Container configuration (Postgres, Mongo, pgAdmin)
│   └── requirements.txt            # Python dependencies
│
└── READ.md                         # Project documentation (this file)
```

---

## ⚙️ Getting Started

### 1. Start the Docker Services
Navigate to the `JTCA` directory and spin up the database cluster:
```bash
cd JTCA
docker-compose up -d
```
This launches:
*   **MongoDB** at `localhost:27017`
*   **PostgreSQL** at `localhost:5432`
*   **Mongo Express** (Web UI) at `http://localhost:8081`
*   **pgAdmin** (Web UI) at `http://localhost:5050`

### 2. Configure Environment Variables
Copy `.env.example` to `.env` inside the `JTCA` folder and add your Gemini API key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
MONGO_URI=mongodb://jtca_user:jtca_pass@localhost:27017/
PG_URI=postgresql://jtca_user:jtca_pass@localhost:5432/jtca
```

### 3. Install Python Dependencies
Install the required packages:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the desktop application:
```bash
python main.py
```

> [!NOTE]
> Ensure that you have Docker running locally before launching `docker-compose`. If running on Windows, WSL2 backend is recommended.

> [!IMPORTANT]
> To run the OCR pipeline on scanned documents, ensure you have system-level dependencies for EasyOCR/PyTorch configured, or use the pre-built fallback modes inside the application.
