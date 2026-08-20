import os

import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq


load_dotenv()

st.set_page_config(
    page_title="Blood Work Review",
    page_icon=":microscope:",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root { --ink: #17252d; --muted: #60717a; --line: #dce6e3; --mint: #e2f2ec; --coral: #f28b72; }
    .stApp { background: linear-gradient(135deg, #f7fbf8 0%, #edf5f3 52%, #fff8f2 100%); color: var(--ink); }
    .block-container { max-width: 1180px; padding-top: 3rem; padding-bottom: 4rem; }
    .hero { padding: 1.5rem 0 2rem; border-bottom: 1px solid var(--line); margin-bottom: 2rem; }
    .eyebrow { color: #22735d; font-size: .75rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    h1 { color: var(--ink); font-size: clamp(2.4rem, 6vw, 4.8rem); line-height: .95; letter-spacing: 0; max-width: 720px; margin: .65rem 0 1rem; }
    .hero-copy { color: var(--muted); font-size: 1.05rem; max-width: 650px; }
    .notice { background: rgba(255,255,255,.7); border: 1px solid var(--line); border-left: 4px solid var(--coral); padding: .9rem 1rem; color: var(--muted); margin: 1rem 0 1.5rem; }
    div[data-testid="stFileUploader"] { background: rgba(255,255,255,.62); border: 1px dashed #9fc6b8; padding: .5rem; }
    .result-label { color: #22735d; font-size: .75rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-top: 1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">Personal health workspace</div>
      <h1>Make your blood work easier to read.</h1>
      <div class="hero-copy">Upload a report or paste its text to organize results and generate practical food guidance.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="notice"><strong>For information only.</strong> This review does not diagnose conditions or replace advice from a qualified clinician.</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Report input")
    uploaded_file = st.file_uploader("Upload a text report", type=["txt"])
    pasted_report = st.text_area(
        "Or paste report text",
        height=260,
        placeholder="Paste blood-work results here...",
    )
    analyze = st.button("Analyze report", type="primary", use_container_width=True)


def get_report_text() -> str:
    if uploaded_file is not None:
        return uploaded_file.getvalue().decode("utf-8")
    return pasted_report.strip()


@st.cache_resource(show_spinner=False)
def get_llm() -> ChatGroq:
    return ChatGroq(model="qwen/qwen3.6-27b", temperature=0)


def analyze_report(report_text: str) -> tuple[str, str]:
    llm = get_llm()
    extraction_prompt = f"""
You are a helpful assistant that organizes blood work results. Identify each test as HIGH, LOW, or NORMAL using the reference range in the report.
Format every result as: - Test Name: value, Result: HIGH/LOW/NORMAL, Reference: range
Do not diagnose the patient.

Blood work content:
{report_text}
"""
    extracted_values = llm.invoke(extraction_prompt).text

    diet_prompt = f"""
You are a dietitian assistant providing general dietary education based on blood work results.
Review the extracted results below and provide practical recommendations based on abnormal results.
Include foods to eat more often and foods to limit. Do not diagnose or prescribe treatment.

Extracted results:
{extracted_values}
"""
    dietary_recommendations = llm.invoke(diet_prompt).text
    return extracted_values, dietary_recommendations


if analyze:
    report_text = get_report_text()
    if not report_text:
        st.warning("Add a report before analyzing it.")
    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is missing. Add it to your .env file, then restart Streamlit.")
    else:
        with st.spinner("Reading the report and preparing guidance..."):
            try:
                extracted_values, recommendations = analyze_report(report_text)
            except Exception as error:
                st.error(f"The report could not be analyzed: {error}")
            else:
                st.markdown('<div class="result-label">Organized results</div>', unsafe_allow_html=True)
                st.markdown(extracted_values)
                st.divider()
                st.markdown('<div class="result-label">Food guidance</div>', unsafe_allow_html=True)
                st.markdown(recommendations)

st.caption("Keep your original report and discuss any concerns or abnormal values with your healthcare professional.")