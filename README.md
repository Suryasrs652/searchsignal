# SearchSignal ⚡
### Multi-Site SEO, GEO & AEO Intelligence and Growth Platform

SearchSignal is a production-grade website intelligence platform that crawls, audits, validates, scores, explains, and prioritizes website improvements across:
- **SEO**: Conventional search discoverability, crawlability, indexability, metadata, content hierarchy, internal links, structured data, performance, and canonical architecture.
- **GEO**: Visibility and answerability for Generative / AI search experiences (model version `GEO-2026.1`).
- **AEO**: Ability of content to directly answer user questions in extractable, structured, citation-friendly form (model version `AEO-2026.2`).

---

## 💎 The Central Product Principle

> **"Never present a heuristic as an observed fact."**

Every finding and score in SearchSignal is classified into an explicit evidence class:

| Evidence Class | Meaning | Examples |
| :--- | :--- | :--- |
| **`EXACT`** | Directly measured from HTTP, HTML, DOM, or DNS | HTTP 404, missing `<title>`, canonical target, word count |
| **`DERIVED`** | Deterministically calculated from exact observations | Duplicate-title percentage, internal link depth, orphan pages |
| **`VALIDATED`** | Tested against an external specification or tool | Schema.org validation, sitemap XML validation, price truthfulness |
| **`OBSERVED`** | Obtained from an external data source or API | Google Search Console clicks, CrUX field data |
| **`HEURISTIC`** | Model or rule-based readiness estimate | AEO answerability, GEO citation readiness *(explicitly labeled)* |
| **`PREDICTIVE`** | Model-generated forecast or prioritization estimate | Opportunity score, estimated growth potential |
| **`UNKNOWN`** | Cannot be established with available evidence | Ranking guarantees or subjective search engine claims |

---

## 🏗️ Architecture

```
                   ┌────────────────────┐
                   │  Web Application   │
                   │  React + Tailwind  │
                   └─────────┬──────────┘
                             │ REST / JSON
                   ┌─────────▼──────────┐
                   │     FastAPI Layer  │
                   └─────────┬──────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
┌──────▼──────┐       ┌──────▼──────┐       ┌──────▼──────┐
│  Database   │       │ Redis/Queue │       │ Object/FS   │
│  PostgreSQL │       │ Task state  │       │ Raw Evidence│
│  or SQLite  │       │             │       │ Store       │
└─────────────┘       └──────┬──────┘       └─────────────┘
                             │
                      ┌──────▼──────┐
                      │ Crawl Engine│
                      └──────┬──────┘
                             │
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
 ┌──────▼──────┐      ┌──────▼──────┐      ┌──────▼──────┐
 │ HTTP Crawler│      │ SSRF Guard  │      │ Rules Engine│
 │ RFC 9309    │      │ OWASP IP/   │      │ SEO, Schema,│
 │ Robots/XML  │      │ DNS filter  │      │ AEO, GEO    │
 └─────────────┘      └─────────────┘      └─────────────┘
```

---

## 🚀 Quick Start (Local Development)

### 1. Backend (FastAPI)
```bash
# From workspace root:
pip install -r apps/api/requirements.txt

# Start backend server:
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```
- API is live at: `http://localhost:8000`
- Interactive Swagger docs: `http://localhost:8000/docs`

### 2. Frontend (React + Vite + Tailwind)
```bash
cd apps/web
npm install
npm run dev
```
- Web Dashboard is live at: `http://localhost:3000`

---

## 🧪 Running the Test Suite & Golden Benchmark Audit

The repository includes a permanent synthetic benchmark website (`tests/fixtures/synthetic_site.py`) featuring regression routes for:
- `/200`, `/404`, `/301`, `/missing-title`, `/duplicate-title-1`, `/duplicate-title-2`, `/noindex`, `/canonical-mismatch`, `/schema-valid`, `/schema-invalid`, `/schema-price-conflict`, `/robots-blocked`, `/aeo-faq`.

Run all automated pytest suites:
```bash
python -m pytest tests/ -v
```

---

## 🔒 Security & SSRF Protection
The engine implements strict OWASP SSRF protections before fetching any URL or following any redirect:
- Blocks IPv4/IPv6 loopback (`127.0.0.1`, `::1`).
- Blocks RFC 1918 private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- Blocks link-local and cloud metadata endpoints (`169.254.169.254`, `metadata.google.internal`).
- Rejects non-HTTP schemes and credential-bearing URLs (`user:pass@host`).

---

## 📈 Growth Roadmap Prioritization Formula
Recommendations are prioritized into **Now**, **Next**, **Later**, and **Experiments** using:
$$\text{Opportunity Score} = \frac{\text{Impact} \times \text{Reach} \times \text{Confidence} \times \text{Strategic Value}}{\text{Effort} \times 10}$$
Normalized 0–100, paired with concrete **Pros**, **Cons**, and deterministic **Validation Tests**.
