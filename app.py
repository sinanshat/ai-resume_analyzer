import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import PyPDF2 as pdf

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get response from Gemini
def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(input_prompt)
    return response.text

# Function to extract text from a PDF
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in range(len(reader.pages)):
        page_content = reader.pages[page]
        text += str(page_content.extract_text())
    return text

# --- Streamlit App ---
st.set_page_config(page_title="AI Resume Analyzer")
st.header("AI Resume Analyzer")

jd = st.text_area("Paste the Job Description here", height=150)
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"])

if uploaded_file is not None:
    st.success("PDF Uploaded Successfully!")

submit = st.button("Analyze My Resume")

if submit:
    if uploaded_file is not None and jd:
        with st.spinner("Analyzing..."):
            resume_text = input_pdf_text(uploaded_file)
            input_prompt = f"""
            Act as an experienced Applicant Tracking System (ATS) and a highly skilled tech recruiter.
            Your task is to evaluate the provided resume against the given job description.

            Job Description:
            {jd}

            Resume:
            {resume_text}

            Please provide a detailed analysis with the following structure:
            1.  **ATS Match Score:** Give a percentage score of how well the resume matches the job description.
            2.  **Missing Keywords:** List the critical keywords and skills from the job description that are missing from the resume.
            3.  **Profile Summary Analysis:** Evaluate the resume's summary. Is it impactful? Does it align with the job role?
            4.  **Suggestions for Improvement:** Provide specific, actionable advice on how to improve the resume to better match this job description and pass through an ATS. Format this as a bulleted list.
            """
            response = get_gemini_response(input_prompt)
            st.subheader("Analysis Report")
            st.markdown(response)
    else:
        st.warning("Please upload a resume and paste a job description.")