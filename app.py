import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import PyPDF2 as pdf

# --------------------------
# Custom CSS loader
# --------------------------
def load_local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------
# Page Configuration
# --------------------------
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")

# Load CSS safely
try:
    load_local_css("style.css")
except FileNotFoundError:
    st.warning("⚠️ style.css not found. Using default Streamlit theme.")

# --------------------------
# Load environment variables
# --------------------------
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY not found. Please add it to your .env file.")
else:
    genai.configure(api_key=api_key)

# --------------------------
# Header
# --------------------------
st.title(" AI Resume Analyzer")
st.markdown("""
Welcome! Get a competitive edge in your job search.  
Upload your resume and paste a job description below to see how well you match the role.  
Our AI will provide an ATS score and actionable feedback to help you land your dream job.
""")

try:
    st.divider()
except AttributeError:  # For Streamlit < 1.22
    st.markdown("---")

# --------------------------
# Helper function: Extract PDF text
# --------------------------
def get_pdf_text(pdf_file):
    """Extracts text from an uploaded PDF file."""
    try:
        reader = pdf.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return None

# --------------------------
# Gemini API call
# --------------------------
def get_gemini_response(input_text):
    """Calls the Gemini API to analyze the resume and job description."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(input_text)
        # Safer response handling
        return getattr(response, "text", response.candidates[0].content.parts[0].text if response.candidates else "")
    except Exception as e:
        st.error(f"Error calling Gemini API: {e}")
        return None

# --------------------------
# Application UI
# --------------------------
col1, col2 = st.columns([2, 1])

with col1:
    jd = st.text_area("📌 Paste the Job Description here", height=200)

with col2:
    uploaded_file = st.file_uploader("📂 Upload your resume (PDF)...", type="pdf")
    if uploaded_file is not None:
        st.success("✅ PDF Uploaded Successfully!")

# Add Analyze button
analyze_button = st.button("🚀 Analyze Resume")

# --------------------------
# Analysis Logic
# --------------------------
if analyze_button:
    if not api_key:
        st.warning("Please set your GOOGLE_API_KEY in the .env file before analyzing.")
    elif uploaded_file is None:
        st.warning("Please upload your resume.")
    elif not jd.strip():
        st.warning("Please paste the job description.")
    else:
        with st.spinner("Analyzing... Our AI is reviewing your documents."):
            resume_text = get_pdf_text(uploaded_file)
            if resume_text:
                # Input prompt for Gemini
                input_prompt = f"""
Act as a very experienced ATS (Applicant Tracking System) with a deep understanding of tech roles,
especially in software engineering, data science, and data analysis.
Your task is to evaluate the provided resume against the given job description with high accuracy.

You must perform a detailed analysis and provide the following in a structured format:
1. **ATS Match Score:** A percentage representing how well the resume matches the job description.
2. **Missing Keywords:** A list of critical keywords from the job description that are missing from the resume.
3. **Profile Summary:** A brief, professional summary of the candidate's profile based on the resume.
4. **Improvement Suggestions:** Actionable, bullet-pointed advice on how to improve the resume to better match this specific job description.

Resume Text:
{resume_text}

Job Description:
{jd}
                """
                analysis_result = get_gemini_response(input_prompt)

                if analysis_result:
                    st.subheader("📊 Analysis Report")
                    st.markdown(
                        f"""
                        <div class="report-card">
                            <div class="report-header">AI-Powered Resume Analysis</div>
                            <div class="report-content">
                                {analysis_result}
                        """,
                        unsafe_allow_html=True,
                    )

# --------------------------
# Footer
# --------------------------
try:
    st.divider()
except AttributeError:
    st.markdown("---")

st.markdown("""
---
*Built with Python, Streamlit, and the Google Gemini API.*
""")
