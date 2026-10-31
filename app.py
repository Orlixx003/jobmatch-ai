"""Streamlit web UI for JobMatch AI.

Run:  streamlit run app.py
"""

import os

import streamlit as st
from dotenv import load_dotenv

from jobmatch import analyze_match, read_cv
from jobmatch.cv_reader import CVReadError
from jobmatch.demo import DEMO_RESULT, demo_inputs

load_dotenv()

st.set_page_config(page_title="JobMatch AI", page_icon="🎯", layout="centered")

st.title("🎯 JobMatch AI")
st.caption("Upload your CV, paste a job offer — get a match score, skill gaps and a cover letter.")

with st.sidebar:
    st.header("Settings")
    demo = st.toggle(
        "Demo mode",
        value=os.getenv("JOBMATCH_DEMO") == "1",
        help="Shows a sample analysis of the files in examples/. No API key needed.",
    )
    api_key = st.text_input(
        "Anthropic API key",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="Used only for this session. Never stored.",
    )
    language = st.selectbox(
        "Output language",
        options=["pl", "en", "uk"],
        format_func={"pl": "Polski", "en": "English", "uk": "Українська"}.get,
    )

if demo:
    demo_cv, demo_job = demo_inputs()
    st.info("Demo mode: sample CV and job offer from `examples/`, with a pre-made result.")
    with st.expander("Sample CV"):
        st.text(demo_cv)
    cv_file = None
    job_text = st.text_area("Job offer", demo_job, height=220)
else:
    cv_file = st.file_uploader("Your CV", type=["pdf", "docx", "txt", "md"])
    job_text = st.text_area("Job offer", height=220, placeholder="Paste the full job description here…")

if st.button("Analyse", type="primary", use_container_width=True):
    if demo:
        result = DEMO_RESULT
    else:
        if not api_key:
            st.error("Add your Anthropic API key in the sidebar, or turn on Demo mode.")
            st.stop()
        if cv_file is None or not job_text.strip():
            st.error("Upload a CV and paste a job offer.")
            st.stop()

        try:
            cv_text = read_cv(cv_file, filename=cv_file.name)
        except CVReadError as exc:
            st.error(str(exc))
            st.stop()

        with st.spinner("Analysing with Claude…"):
            try:
                result = analyze_match(cv_text, job_text, language, api_key=api_key)
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

    st.metric("Match score", f"{result.score}/100")
    st.progress(result.score / 100)
    st.subheader(result.verdict)
    st.write(result.summary)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**✅ Matched skills**")
        for skill in result.matched_skills:
            st.markdown(f"- {skill}")
    with col2:
        st.markdown("**⚠️ Missing skills**")
        for skill in result.missing_skills:
            st.markdown(f"- {skill}")

    st.markdown("**💡 How to improve your CV**")
    for tip in result.cv_tips:
        st.markdown(f"- {tip}")

    st.markdown("**✉️ Cover letter**")
    st.text_area("Cover letter", result.cover_letter, height=260, label_visibility="collapsed")

    st.download_button(
        "Download report (.md)",
        data=result.to_markdown(),
        file_name="jobmatch-report.md",
        mime="text/markdown",
    )
