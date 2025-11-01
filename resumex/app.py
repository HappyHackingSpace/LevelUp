import io
import json
import re
from typing import Any

import google.generativeai as genai
import pypdf
import streamlit as st

from resumex import config
from resumex.prompts import get_resume_analysis_prompt

GEMINI_API_KEY = config.GEMINI_API_KEY
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "Missing GEMINI_API_KEY. "
        "Set it in your shell or add it to .env / Streamlit secrets."
    )
genai.configure(api_key=GEMINI_API_KEY)

Model = genai.GenerativeModel("gemini-2.0-flash-lite")


def extract_text_from_pdf(uploaded_file: Any) -> str | None:
    """Extract text content from an uploaded PDF file.

    Args:
        uploaded_file: A file-like object containing the PDF to be processed.

    Returns:
        The extracted text content from all pages of the PDF.
        If an error occurs during PDF extraction.
    """
    try:
        pdf_reader = pypdf.PdfReader(io.BytesIO(uploaded_file.read()))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return None


def display_language_info(result: dict[str, Any]) -> None:
    """Display the detected language of the CV.

    Args:
        result: The analysis result dictionary containing language information.
    """
    st.subheader("Detected Language")
    st.write(result.get("language", "Not detected"))


def display_domain_scores(result: dict[str, Any]) -> None:
    """Display career domain fit scores as a table.

    Args:
        result: The analysis result dictionary containing domain scores.
    """
    st.subheader("Career Domain Fit Scores")
    if domain_results := result.get("domain_scores", []):
        st.table(
            [
                {
                    "Domain": domain_result["domain"],
                    "Score": domain_result["score"],
                    "Justification": domain_result["justification"],
                }
                for domain_result in domain_results
            ]
        )


def display_competency_scores(result: dict[str, Any]) -> None:
    """Display competency evaluation scores as a table.

    Args:
        result: The analysis result dictionary containing competency scores.
    """
    st.subheader("Competency Evaluation")
    if competency_results := result.get("competency_scores", []):
        st.table(
            [
                {
                    "Category": competency_result["category"],
                    "Score": competency_result["score"],
                    "Strength": competency_result["strength"],
                    "Observation": competency_result["observation"],
                }
                for competency_result in competency_results
            ]
        )


def display_strategic_insights(result: dict[str, Any]) -> None:
    """Display strategic insights section.

    Args:
        result: The analysis result dictionary containing strategic insights.
    """
    st.subheader("Strategic Insights")
    st.write(result.get("strategic_insights", "N/A"))


def display_development_recommendations(result: dict[str, Any]) -> None:
    """Display development recommendations as a bulleted list.

    Args:
        result: The analysis result dictionary containing development recommendations.
    """
    st.subheader("Development Recommendations")
    for rec in result.get("development_recommendations", []):
        st.markdown(f"- {rec}")


def display_comparative_benchmarking(result: dict[str, Any]) -> None:
    """Display comparative benchmarking information.

    Args:
        result: The analysis result dictionary containing benchmarking data.
    """
    st.subheader("Comparative Benchmarking")
    st.write(result.get("comparative_benchmarking", "N/A"))


def display_overall_summary(result: dict[str, Any]) -> None:
    """Display overall summary including score, strengths, areas to improve, and talent potential.

    Args:
        result: The analysis result dictionary containing summary information.
    """
    st.subheader("Overall Summary")
    summary = result.get("overall_summary", {})

    st.markdown(f"**Overall Score:** {summary.get('overall_score', 'N/A')}/100")

    st.markdown("**Key Strengths:**")
    for strength in summary.get("key_strengths", []):
        st.markdown(f"- {strength}")

    st.markdown("**Areas to Improve:**")
    for area in summary.get("areas_to_improve", []):
        st.markdown(f"- {area}")

    st.markdown(f"**Talent Potential:** {summary.get('talent_potential', 'N/A')}")


def display_analysis_results(result: dict[str, Any]) -> None:
    """Display all sections of the resume analysis result.

    This function orchestrates the display of all analysis sections in a logical order.

    Args:
        result: The complete analysis result dictionary from the LLM.
    """
    display_language_info(result)
    display_domain_scores(result)
    display_competency_scores(result)
    display_strategic_insights(result)
    display_development_recommendations(result)
    display_comparative_benchmarking(result)
    display_overall_summary(result)


def analyzecv_pdf_withllm(text: str, report_language: str) -> dict[str, Any] | None:
    """Analyze CV/resume text using LLM and generate structured analysis report.

    This function processes the text extracted from a resume, sends it to the LLM with a
    specialized prompt, and parses the response into a structured format. The analysis includes
    language detection, domain matching, competency evaluation, strategic insights, and
    development recommendations.

    Args:
        text: The text content extracted from the resume/CV.
        report_language: The language in which to generate the analysis report.

    Returns:
        A structured dictionary containing the complete resume analysis with various sections.
        If an error occurs during the analysis process or JSON parsing.
    """
    prompt = get_resume_analysis_prompt(text, report_language)
    try:
        response = Model.generate_content(prompt)
        raw_text = response.text
        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not match:
            st.error(
                "Sorry, the analysis could not be completed. Please try again later or upload a different file."
            )
            return None
        json_str = match.group(0)
        return json.loads(json_str)  # type: ignore[no-any-return]
    except Exception:
        st.error(
            "An error occurred while processing your resume. Please try again or upload a different file."
        )
        return None


st.title("Advanced Resume Analysis Application")

if uploaded_file := st.file_uploader("Upload your Resume (PDF)", type="pdf"):
    if text := extract_text_from_pdf(uploaded_file):
        # Language selector after PDF
        st.subheader("Select report language")
        language_options = [
            "English",
            "German",
            "French",
            "Italian",
            "Russian",
            "Turkish",
            "Spanish",
        ]
        selected_language = st.selectbox(
            "Choose a language for the report", language_options
        )

        # Trigger analysis
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing Resume..."):
                if result := analyzecv_pdf_withllm(text, selected_language):
                    display_analysis_results(result)
