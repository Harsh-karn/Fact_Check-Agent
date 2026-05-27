<div align="center">

# 🕵️ Fact-Check Agent

### *The AI-Powered Truth Layer for Any Document*

> ### 🚀 [**▶ Try the Live App → factcheck-agentz.streamlit.app**](https://factcheck-agentz.streamlit.app/)

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://factcheck-agentz.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-Harsh--karn-181717?style=for-the-badge&logo=github)](https://github.com/Harsh-karn/Fact_Check-Agent)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=for-the-badge)](https://groq.com)
[![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)

> Upload any PDF. The agent reads it, searches the live web, and tells you what's **true**, what's **outdated**, and what's outright **false** — in seconds.

---

</div>

## 🎯 What Problem Does This Solve?

Marketing decks, research reports, and whitepapers are full of statistics that can be **outdated, hallucinated, or fabricated**. Manual fact-checking is slow and error-prone. The Fact-Check Agent acts as an automated **"Truth Layer"** that reads documents and cross-references every claim against live web data.

---

## ⚙️ How It Works

```mermaid
flowchart TD
    A([👤 User Uploads PDF]) --> B[📖 Text Extraction\nPyMuPDF]
    B --> C[🤖 AI Claim Identification\nGroq / Gemini LLM]
    C --> D{Factual Claims\nExtracted}
    D --> E1[Claim 1]
    D --> E2[Claim 2]
    D --> E3[Claim N...]
    E1 --> F1[🌐 DuckDuckGo\nWeb Search]
    E2 --> F2[🌐 DuckDuckGo\nWeb Search]
    E3 --> F3[🌐 DuckDuckGo\nWeb Search]
    F1 --> G[🧠 AI Cross-Reference\n& Verdict]
    F2 --> G
    F3 --> G
    G --> H1[✅ Verified]
    G --> H2[⚠️ Inaccurate]
    G --> H3[❌ False]
    G --> H4[❓ Unverified]

    style A fill:#4CAF50,color:#fff
    style H1 fill:#4CAF50,color:#fff
    style H2 fill:#FF9800,color:#fff
    style H3 fill:#F44336,color:#fff
    style H4 fill:#2196F3,color:#fff
```

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 📄 **PDF Upload** | Upload any PDF and extract text automatically |
| 🤖 **Dual AI Provider** | Choose between **Groq (LLaMA 3.3 70B)** or **Google Gemini** |
| 🌐 **Live Web Search** | Uses DuckDuckGo to find real-time evidence for each claim |
| ✅ **Verdict Engine** | Each claim is judged: Verified, Inaccurate, False, or Unverified |
| 📊 **Summary Dashboard** | Instant metrics breakdown at a glance |
| ⚡ **Groq Free Tier** | No daily quota issues — blazing fast inference |
| 🔄 **Auto Retry** | Handles rate limits gracefully with exponential backoff |

---

## 🏗️ Tech Stack

```mermaid
graph LR
    subgraph Frontend
        A[🎈 Streamlit]
    end
    subgraph AI Providers
        B[⚡ Groq API\nLLaMA 3.3 70B]
        C[🔵 Gemini API\ngoogle-genai]
    end
    subgraph PDF Processing
        D[📄 PyMuPDF]
    end
    subgraph Web Search
        E[🦆 DuckDuckGo Search]
    end
    A --> B
    A --> C
    A --> D
    A --> E
```

---

## 🚀 Quick Start

### Option 1 — Use the Live App
👉 Visit **[factcheck-agentz.streamlit.app](https://factcheck-agentz.streamlit.app/)**
- Get a free Groq API key from [console.groq.com/keys](https://console.groq.com/keys)
- Upload your PDF → Click **Analyze Document**

### Option 2 — Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Harsh-karn/Fact_Check-Agent.git
cd Fact_Check-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python -m streamlit run app.py
```

Open your browser at `http://localhost:8501`

---

## 🔑 API Keys

| Provider | Where to Get | Cost |
|----------|-------------|------|
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | ✅ Free tier — very generous |
| **Gemini** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | ✅ Free tier available |

> 💡 **Recommendation:** Use **Groq** for testing — instant sign-up, no billing required, and no daily quota exhaustion.

---

## 📊 Verdict System

```
┌─────────────────────────────────────────────────────────────┐
│                    VERDICT CATEGORIES                        │
├──────────────┬───────────────────────────────────────────────┤
│  ✅ Verified  │ Web evidence confirms the claim is accurate   │
│  ⚠️ Inaccurate│ Partially true but with wrong/outdated data  │
│  ❌ False     │ Directly contradicts available evidence       │
│  ❓ Unverified│ Not enough data to confirm or deny           │
└──────────────┴───────────────────────────────────────────────┘
```

---

## 🧪 Testing with a "Trap Document"

The app is designed to catch intentional lies. For example, a document claiming:

> *"Apple's revenue in 2023 was $50 billion"* → ❌ **FALSE** — Apple's actual revenue was ~$383 billion

> *"The Eiffel Tower is 500 meters tall"* → ❌ **FALSE** — It is 330 meters tall

> *"Python was created in 1991"* → ✅ **VERIFIED** — Confirmed by multiple sources

---

## 📁 Project Structure

```
Fact_Check-Agent/
│
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md           # This file
└── .gitignore          # Git ignore rules
```

---

## 🌐 Deployment

This app is deployed on **Streamlit Community Cloud**:

1. Push code to GitHub
2. Connect repo at [share.streamlit.io](https://share.streamlit.io)
3. Set `app.py` as the main file
4. Click **Deploy!**

---

<div align="center">

Built with ❤️ using Streamlit, Groq, and DuckDuckGo Search

⭐ **Star this repo if you found it useful!** ⭐

</div>
