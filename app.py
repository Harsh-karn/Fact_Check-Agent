import streamlit as st
import pymupdf  # PyMuPDF
from duckduckgo_search import DDGS
import json
import time
import re

# --- Page Config ---
st.set_page_config(page_title="Fact-Check Agent", page_icon="🕵️", layout="wide")

# --- Sidebar: Provider Selection & API Key ---
with st.sidebar:
    st.title("⚙️ Configuration")

    provider = st.radio(
        "Choose AI Provider",
        ["Groq (Free & Fast ⚡)", "Gemini (Google)"],
        help="Groq is recommended — free, fast, and no daily quota issues."
    )

    if provider == "Groq (Free & Fast ⚡)":
        api_key = st.text_input(
            "Groq API Key:",
            type="password",
            placeholder="gsk_..."
        )
        st.markdown(
            "🔑 [Get a free Groq API Key](https://console.groq.com/keys) — sign up is instant, no billing needed.",
            unsafe_allow_html=False
        )
        GROQ_MODEL = "llama-3.3-70b-versatile"
    else:
        api_key = st.text_input(
            "Gemini API Key:",
            type="password",
            placeholder="AIza..."
        )
        st.markdown(
            "🔑 [Get a Gemini API Key](https://aistudio.google.com/app/apikey)",
            unsafe_allow_html=False
        )
        GEMINI_MODEL = "gemini-2.0-flash-lite"

    if not api_key:
        st.warning("Please enter an API key to continue.")
        st.stop()
    else:
        st.success("API Key accepted ✓")

    st.divider()
    st.markdown("**How it works:**")
    st.markdown("1. 📄 Upload a PDF")
    st.markdown("2. 🤖 AI extracts factual claims")
    st.markdown("3. 🌐 Web searches verify each claim")
    st.markdown("4. ✅ Results flagged as Verified / Inaccurate / False")

# --- LLM Call Functions ---

def call_groq(api_key, prompt):
    """Call Groq LLM API."""
    from groq import Groq
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return response.choices[0].message.content

def call_gemini(api_key, prompt):
    """Call Gemini API with retry logic."""
    from google import genai
    client = genai.Client(api_key=api_key)
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text
        except Exception as e:
            error_str = str(e)
            if "429" in error_str:
                delay_match = re.search(r"retryDelay.*?(\d+)s", error_str)
                wait_secs = int(delay_match.group(1)) if delay_match else 30
                if attempt < 2:
                    st.info(f"⏳ Rate limit hit. Waiting {wait_secs}s before retry {attempt + 2}/3...")
                    time.sleep(wait_secs + 2)
                    continue
            raise e
    return None

def call_llm(prompt):
    """Route the LLM call to the selected provider."""
    if provider == "Groq (Free & Fast ⚡)":
        return call_groq(api_key, prompt)
    else:
        return call_gemini(api_key, prompt)

# --- Core Logic Functions ---

@st.cache_data
def extract_text_from_pdf(file_bytes):
    """Extract text from PDF bytes."""
    try:
        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        return "".join(page.get_text() for page in doc)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return None

def clean_json(text):
    """Strip markdown code fences from LLM output."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()

def extract_claims(text):
    """Use LLM to extract factual claims from document text."""
    # Truncate very long documents to avoid token limits
    truncated = text[:12000] if len(text) > 12000 else text

    prompt = f"""You are an expert fact-checker analyzing a document.
Extract all specific, verifiable factual claims from the text below.
Focus ONLY on concrete, checkable facts:
- Statistics and percentages
- Dates and years
- Named financial figures (revenue, market cap, funding)
- Technical specifications
- Record-breaking or superlative claims

Return a valid JSON array of strings. Each string should be a single, self-contained claim.
Do NOT include opinions, vague statements, or marketing language.
Output ONLY the JSON array with no other text.

Example output:
["Apple revenue was $394 billion in 2022.", "The Eiffel Tower is 330 meters tall.", "Bitcoin reached $69,000 in November 2021."]

Document text:
---
{truncated}
"""
    try:
        raw = call_llm(prompt)
        if not raw:
            return []
        return json.loads(clean_json(raw))
    except json.JSONDecodeError:
        st.error("⚠️ Could not parse claims as JSON. The model returned unexpected output.")
        return []
    except Exception as e:
        st.error(f"Error extracting claims: {e}")
        return []

def search_web(query):
    """Search DuckDuckGo for evidence about a claim."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=4))
            if not results:
                return "No search results found."
            return "\n\n".join(
                f"Source: {r.get('href', 'N/A')}\nSnippet: {r.get('body', '')}"
                for r in results
            )
    except Exception as e:
        return f"Search failed: {e}"

def verify_claim(claim, search_context):
    """Use LLM to evaluate a claim against web evidence."""
    prompt = f"""You are a strict, impartial fact-checker.

Given the claim and web search results below, evaluate the claim's accuracy.

CLAIM: "{claim}"

WEB SEARCH RESULTS:
---
{search_context}
---

Classify the claim as ONE of:
- "Verified": Search results clearly confirm the claim is accurate.
- "Inaccurate": The claim has some basis but contains wrong numbers, outdated info, or misleading details.
- "False": The claim directly contradicts the evidence, or is fabricated with no basis.
- "Unverified": Insufficient evidence to confirm or deny.

Respond ONLY with a JSON object in this exact format:
{{
  "status": "Verified" | "Inaccurate" | "False" | "Unverified",
  "explanation": "One sentence explaining your verdict.",
  "correct_facts": "The accurate information if the claim is wrong, otherwise leave empty."
}}"""
    try:
        raw = call_llm(prompt)
        if not raw:
            return {"status": "Error", "explanation": "No response from model.", "correct_facts": ""}
        return json.loads(clean_json(raw))
    except Exception as e:
        return {"status": "Error", "explanation": str(e), "correct_facts": ""}

# --- Main App UI ---

st.title("🕵️ Fact-Checking Agent")
st.markdown(
    "Upload any PDF — the AI will extract specific factual claims, search the web to verify them, "
    "and flag each one as **✅ Verified**, **⚠️ Inaccurate**, or **❌ False**."
)

uploaded_file = st.file_uploader("📄 Upload PDF", type=["pdf"], label_visibility="collapsed")

if uploaded_file:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info(f"**File:** {uploaded_file.name} ({uploaded_file.size // 1024} KB)")
    with col2:
        analyze = st.button("🔍 Analyze Document", use_container_width=True, type="primary")

    if analyze:
        # Step 1: Extract text
        with st.spinner("📖 Reading PDF..."):
            file_bytes = uploaded_file.read()
            pdf_text = extract_text_from_pdf(file_bytes)

        if not pdf_text or len(pdf_text.strip()) < 50:
            st.error("Could not extract meaningful text from this PDF. Please try another file.")
            st.stop()

        # Step 2: Extract claims
        with st.spinner("🤖 Extracting factual claims with AI..."):
            claims = extract_claims(pdf_text)

        if not claims:
            st.warning("No specific, verifiable claims were found in this document.")
            st.stop()

        st.success(f"Found **{len(claims)} claims** to verify!")

        # Step 3: Verify each claim
        st.subheader("📋 Verification Report")
        progress = st.progress(0, text="Starting verification...")
        results = []

        for i, claim in enumerate(claims):
            progress.progress(
                (i + 1) / len(claims),
                text=f"Verifying claim {i + 1} of {len(claims)}..."
            )

            # Web search
            search_ctx = search_web(claim)

            # LLM verification
            verdict = verify_claim(claim, search_ctx)
            verdict["claim"] = claim
            results.append(verdict)

            # Delay to avoid rate limits (Groq is generous but still has RPM limits)
            if i < len(claims) - 1:
                time.sleep(2)

        progress.empty()

        # Step 4: Display results
        verified = sum(1 for r in results if r["status"] == "Verified")
        inaccurate = sum(1 for r in results if r["status"] == "Inaccurate")
        false_count = sum(1 for r in results if r["status"] == "False")
        unverified = sum(1 for r in results if r["status"] not in ["Verified", "Inaccurate", "False"])

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ Verified", verified)
        m2.metric("⚠️ Inaccurate", inaccurate)
        m3.metric("❌ False", false_count)
        m4.metric("❓ Unverified", unverified)

        st.divider()

        # Detailed results
        for res in results:
            status = res.get("status", "Unknown")
            claim_text = res.get("claim", "")
            explanation = res.get("explanation", "")
            correct_facts = res.get("correct_facts", "")

            if status == "Verified":
                container = st.success
                icon = "✅"
            elif status == "Inaccurate":
                container = st.warning
                icon = "⚠️"
            elif status == "False":
                container = st.error
                icon = "❌"
            else:
                container = st.info
                icon = "❓"

            with st.expander(f"{icon} **{status}** — {claim_text[:90]}{'...' if len(claim_text) > 90 else ''}", expanded=True):
                st.markdown(f"**Full Claim:** {claim_text}")
                st.markdown(f"**Verdict:** {explanation}")
                if correct_facts:
                    st.markdown(f"**✔ Correct Facts:** {correct_facts}")
