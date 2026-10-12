# Deallens — Sales Intelligence Agent

**CAP 931 Capstone Project**

Deallens is a Streamlit web application that helps sales representatives research prospective accounts and prepare sales briefings. Enter a target company URL and Deallens retrieves the company's public website text, optionally pulls competitor websites for comparison, and generates a structured, evidence-backed sales briefing using a large language model.

What makes Deallens different is its **accuracy-first design**: every briefing is generated under strict evidence rules, and a deterministic **Briefing Compliance Audit** then verifies the output — checking that each cited statistic actually appears in the retrieved website text and flagging any banned claims.

---

## Features

- **Automated website retrieval** — pulls up to 6,000 characters of readable text from any public company URL (plus a manual-text backup option if retrieval fails).
- **Competitor comparison** — add competitor URLs to enrich the briefing with side-by-side context.
- **Structured AI briefings** — executive summary, evidence-backed findings with source citations, potential customer needs (labeled as assumptions), discovery questions, risks & unknowns, and recommended next steps.
- **Evidence-first prompting** — the model must quote statistics exactly as the source states them, never split or combine figures, never attribute one company's numbers to another, and distinguish supported facts from assumptions, recommendations, and unknowns.
- **Briefing Compliance Audit** — a deterministic post-generation check that runs after every briefing:
  - Verifies each cited statistic against the retrieved website text (e.g., "Statistics verified: 9/9").
  - Scans for banned claims (unverified capability promises, time-savings guarantees, "deeper insights," blanket "all facts verified" statements, etc.).

---

## Tech Stack

| Component | Technology |
|---|---|
| UI | Streamlit |
| LLM | `openai/gpt-oss-20b` via Groq API (OpenAI-compatible client) |
| Web retrieval | `requests` + `BeautifulSoup` |
| Config | `python-dotenv` (API key via `.env`) |

---

## Project Structure

```
CAP-931-Sales-Agent/
└── app/
    ├── streamlit_app.py        # Main application (UI, retrieval, briefing, audit)
    └── streamlit_app_backup    # Backup copy
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- A free [Groq API key](https://console.groq.com) (`GROQ_API_KEY`)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/CAP-931-Sales-Agent.git
cd CAP-931-Sales-Agent

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install streamlit requests beautifulsoup4 python-dotenv openai

# 4. Add your Groq API key
# Create a .env file in the project root containing:
# GROQ_API_KEY=your_key_here
```

### Running the App

```bash
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` in your browser, fill in the product and target-company details, and click **Generate Sales Briefing**.

---

## How It Works

1. **Input** — the user enters product information, a target company URL, optional competitor URLs, and the target customer.
2. **Retrieval** — the app fetches readable text from each website (scripts, styles, nav, and footers stripped), up to 6,000 characters per site.
3. **Generation** — the LLM produces a structured briefing under strict evidence rules: quote figures exactly, cite source URLs, label assumptions, and never claim unverified capabilities.
4. **Audit** — the deterministic compliance audit verifies every statistic against the retrieved text and scans for banned claims, displaying the results beneath the briefing.

---

## Example

**Input:** Product `deallens` · Target `https://stripe.com` · Competitor `https://www.adyen.com` · Customer `Patrick Collison, Co-founder & CEO`

**Output:** a complete briefing covering Stripe's positioning ("Financial infrastructure to grow your revenue"), key metrics ($1.9T volume, 99.999% uptime, 135+ currencies and payment methods), and Adyen competitive context — with the audit confirming **no banned claims** and **9/9 statistics verified** against the retrieved text.

---

## Accuracy & Limitations

- Briefings are only as good as the retrieved website text; figures reflect what the target company's public site states.
- The compliance audit checks statistics against retrieved text deterministically, but it cannot verify non-numeric factual claims.
- Deallens does not claim CRM integration, data enrichment, security certifications, or measured business outcomes — and the briefing will not assert them.

---

## Author

**Chauncey Rutledge** — CAP 931 Capstone, Per Scholas
