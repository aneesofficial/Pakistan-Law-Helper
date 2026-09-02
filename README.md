# Pakistan Law Helper ⚖️

A Generative AI-powered legal research assistant designed to answer questions using an offline, indexed dataset of Pakistani law sources. The system processes legal queries, retrieves highly relevant local legal provisions, and synthesizes answers with strict citation validation in simple English or Urdu.

## 🌟 Project Overview

**Problem It Solves:** 
Navigating complex legal documents is traditionally tedious and inaccessible for the general public. While public LLMs (like ChatGPT or standard Gemini) can provide general answers, they frequently hallucinate legal sections or mix up jurisdictions (e.g., confusing federal law with provincial law). Pakistan Law Helper solves this by securely matching user queries strictly against an offline index of verified legal sections, using AI only for final answer synthesis and translation.

**Main Features:**
- 🏛️ **Jurisdiction Filtering:** Accurately separates Federal laws from Provincial laws (Punjab, Sindh, KPK, Balochistan).
- 🔍 **Hybrid Local Search:** Combines semantic (TF-IDF Cosine Similarity) and keyword search for high-accuracy retrieval without external API costs.
- 🛡️ **Anti-Hallucination Validation:** A strict validation layer intercepts the AI's response to ensure any cited sections actually exist in the retrieved local documents.
- 💬 **Multilingual Support:** Asks and answers questions seamlessly in English or Roman Urdu.
- 🖥️ **Professional UI:** A responsive, modern dashboard built with Streamlit.

---

## 🏗️ Architecture & Tech Stack

This project utilizes a **Retrieval-Augmented Generation (RAG)** architecture.

1. **Local Vector Retrieval Approach:** To completely bypass external embedding API limits and costs, the system uses `scikit-learn`'s `TfidfVectorizer` to build a local semantic space. It calculates the cosine similarity between the user's query and thousands of chunked legal sections.
2. **Hybrid Search:** The retrieval engine (`utils/search.py`) combines the TF-IDF semantic scores with a weighted keyword frequency algorithm (prioritizing matches in the Law Title) to fetch the top `K` most relevant sections.
3. **Gemini's Role:** Google's `gemini-3.6-flash` is strictly utilized as a generative reasoning engine. It does not search the internet; it is only fed the retrieved local context and asked to synthesize a human-readable answer.
4. **Source Validation:** The system parses the AI's output using Regex to extract cited section numbers. If the AI cites a section not present in the retrieved local context, the system injects a visible warning alerting the user of a potential hallucination.

**Tech Stack:**
- **Language:** Python 3.8+
- **Frontend:** Streamlit
- **AI/LLM:** Google GenAI SDK (`gemini-3.6-flash`)
- **Data Processing:** `pdfplumber`, Regex
- **Search Engine:** `scikit-learn` (TF-IDF), `numpy`

---

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-link>
   cd Pakistan-Law-Helper
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables (`.env` setup):**
   - Copy the provided template: `cp .env.example .env`
   - Open `.env` and add your Gemini API Key:
     ```env
     GEMINI_API_KEY=your_actual_api_key_here
     ```
   - *Note: Ensure your `.env` file is never committed to GitHub. It is already included in `.gitignore`.*

---

## ⚙️ How to Run the Application

Once dependencies are installed and the API key is configured, start the Streamlit dashboard:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

---

## ⚠️ Known Limitations

- **Dataset Scope:** The offline index provided in this repository is a curated subset of laws (e.g., Constitution, PECA, specific family laws) used for demonstration purposes. **It does not contain all Pakistani laws.** The AI can only answer questions related to the documents present in `data/clean_laws/`.
- **Lexical Limitations:** While TF-IDF is highly efficient and runs locally without API limits, it relies on lexical overlap and statistical frequency. Extremely complex semantic queries might require exact keyword matches compared to heavy dense-vector embedding models.

---

## ⚖️ Legal Disclaimer

This application is an educational software project and is **not intended to provide professional legal advice**. The answers generated are synthesized by AI based on a limited local dataset and may contain inaccuracies. Always consult a qualified, licensed attorney for legal matters and verified legal interpretations.
