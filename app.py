import streamlit as st
import pymupdf  # PyMuPDF
import google.generativeai as genai
from duckduckgo_search import DDGS
import json
import time

# --- Configuration & Setup ---
st.set_page_config(page_title="Fact-Check Agent", page_icon="🕵️", layout="wide")

st.title("🕵️ The Fact-Checking Web App")
st.markdown("Upload a PDF to automatically extract factual claims, cross-reference them against live web data, and verify their accuracy.")

# --- Sidebar for API Key ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("[Get a Gemini API Key](https://aistudio.google.com/app/apikey)")
    if not api_key:
        st.warning("Please enter a Gemini API Key to continue.")
        st.stop()
    else:
        try:
            genai.configure(api_key=api_key)
            # Test if the API key works
            model = genai.GenerativeModel('gemini-1.5-flash')
        except Exception as e:
            st.error(f"Error configuring Gemini API: {e}")
            st.stop()

# --- Helper Functions ---

@st.cache_data
def extract_text_from_pdf(uploaded_file):
    """Extracts text from an uploaded PDF file."""
    text = ""
    try:
        # read() gets the bytes
        doc = pymupdf.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def extract_claims(text):
    """Uses Gemini to extract factual claims from the text."""
    prompt = """
    You are an expert fact-checker. I will provide you with text extracted from a document.
    Your task is to identify and extract specific factual claims made in the text.
    Focus on:
    - Statistics and numbers
    - Dates and historical events
    - Financial figures
    - Technical or scientific claims
    
    Output the claims as a valid JSON list of strings. Do not include any other text or markdown formatting.
    Example:
    [
        "The Eiffel Tower is 5 feet tall.",
        "The company revenue grew by 200% in 2023.",
        "Water boils at 90 degrees Celsius."
    ]
    
    Text to analyze:
    ---
    {text}
    """
    try:
        response = model.generate_content(prompt.format(text=text))
        
        # Clean up potential markdown formatting in response
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        claims = json.loads(response_text.strip())
        return claims
    except json.JSONDecodeError:
        st.error("Failed to parse claims. The model did not return valid JSON.")
        return []
    except Exception as e:
        st.error(f"Error extracting claims: {e}")
        return []

def search_web(query):
    """Searches the web using DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            search_context = "\n\n".join([f"Source: {res.get('href')}\nSnippet: {res.get('body')}" for res in results])
            return search_context
    except Exception as e:
        st.warning(f"Web search failed for query '{query}': {e}")
        return "No search results found."

def verify_claim(claim, search_context):
    """Uses Gemini to evaluate a claim against search results."""
    prompt = """
    You are an expert fact-checker. I will provide you with a 'Claim' and 'Web Search Results' related to that claim.
    Your task is to cross-reference the claim against the search results and determine its accuracy.
    
    Categorize the claim into exactly one of these statuses:
    - "Verified": The search results confirm the claim is true.
    - "Inaccurate": The claim has some truth but contains outdated, misleading, or incorrect specific details.
    - "False": The claim is entirely wrong or contradicts the search results.
    - "Unverified": There is not enough information in the search results to determine.

    You must output a JSON object with the following keys:
    - "status": The categorization (Verified, Inaccurate, False, Unverified).
    - "explanation": A brief explanation of why you gave this status.
    - "correct_facts": The actual correct facts based on the search results (if the claim is Inaccurate or False). If Verified or Unverified, you can leave this empty or provide a confirming note.

    Claim to verify: "{claim}"
    
    Web Search Results:
    ---
    {search_context}
    """
    try:
        response = model.generate_content(prompt.format(claim=claim, search_context=search_context))
        
        # Clean up JSON
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        verification_result = json.loads(response_text.strip())
        return verification_result
    except Exception as e:
        return {
            "status": "Error",
            "explanation": f"Failed to verify claim due to an error: {e}",
            "correct_facts": "N/A"
        }

# --- Main App UI ---

uploaded_file = st.file_uploader("Upload a PDF document to analyze", type=["pdf"])

if uploaded_file is not None:
    if st.button("Analyze Document"):
        with st.spinner("Extracting text from PDF..."):
            pdf_text = extract_text_from_pdf(uploaded_file)
            
        if pdf_text:
            st.success("Text extracted successfully!")
            
            with st.spinner("Extracting factual claims..."):
                claims = extract_claims(pdf_text)
                
            if claims:
                st.write(f"Found **{len(claims)}** claims to verify. Commencing web search and verification...")
                
                # Progress bar for verification
                progress_bar = st.progress(0)
                
                results_data = []
                for i, claim in enumerate(claims):
                    # Search web
                    search_context = search_web(claim)
                    
                    # Verify
                    verification = verify_claim(claim, search_context)
                    
                    # Store
                    results_data.append({
                        "claim": claim,
                        "status": verification.get("status", "Unknown"),
                        "explanation": verification.get("explanation", ""),
                        "correct_facts": verification.get("correct_facts", "")
                    })
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(claims))
                    
                    # Small delay to respect rate limits if needed (DDGS can be picky)
                    time.sleep(1)
                
                # Display Results
                st.header("Verification Report")
                
                for res in results_data:
                    status = res['status']
                    if status == "Verified":
                        st.success(f"**Claim:** {res['claim']}")
                    elif status == "Inaccurate":
                        st.warning(f"**Claim:** {res['claim']}")
                    elif status == "False":
                        st.error(f"**Claim:** {res['claim']}")
                    else:
                        st.info(f"**Claim:** {res['claim']}")
                        
                    st.markdown(f"**Status:** {status}")
                    st.markdown(f"**Explanation:** {res['explanation']}")
                    if res['correct_facts']:
                        st.markdown(f"**Correct Facts:** {res['correct_facts']}")
                    st.divider()
                    
            else:
                st.warning("No clear factual claims could be extracted from this document.")
