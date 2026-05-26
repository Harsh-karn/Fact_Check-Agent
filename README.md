# Fact-Checking Web App

A tool to automate claim verification from PDF documents. It acts as a "Truth Layer," reading a PDF, cross-referencing claims against live web data, and flagging inaccuracies.

## Features
- **Extract**: Identifies specific factual claims (stats, dates, financial/technical figures) from any uploaded PDF.
- **Verify**: Automatically searches the live web to confirm the accuracy of each claim.
- **Report**: Flags claims as **Verified**, **Inaccurate**, or **False**, and provides the correct facts.

## Technologies Used
- **Frontend**: [Streamlit](https://streamlit.io/)
- **PDF Extraction**: `PyMuPDF`
- **LLM/Intelligence**: Google Gemini API (`google-generativeai`)
- **Web Search**: DuckDuckGo Search API (`duckduckgo-search`)

## Local Setup

1. **Clone the repository** (if downloaded from GitHub).
2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the app**:
   ```bash
   streamlit run app.py
   ```
4. Open the provided URL (usually `http://localhost:8501`) in your browser.
5. Provide your Gemini API key in the sidebar and upload a PDF to test!

## Deployment (Streamlit Community Cloud)

1. Push this code to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with your GitHub account.
3. Click **New app** and select your repository, branch, and the `app.py` file.
4. Click **Deploy!**
5. (Optional) If you want to hardcode an API key for the deployed version, you can add it to the Streamlit Community Cloud "Secrets" as `GEMINI_API_KEY = "your_key_here"` and modify the app to read `st.secrets["GEMINI_API_KEY"]`.

## License
MIT
