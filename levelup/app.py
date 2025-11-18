import json
import re
from typing import Any, cast

import google.generativeai as genai
import pandas as pd  # type: ignore[import-untyped]
import pdfplumber
import streamlit as st

from levelup import config
from levelup.prompts import get_resume_analysis_prompt

GEMINI_API_KEY = config.GEMINI_API_KEY
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "Missing GEMINI_API_KEY. "
        "Set it in your shell or add it to .env / Streamlit secrets."
    )
genai.configure(api_key=GEMINI_API_KEY)
Model = genai.GenerativeModel("gemini-2.0-flash-lite")


def extract_text_from_pdf(uploaded_file: Any) -> str | None:
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            parts = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(parts).strip()
        return text
    except Exception as e:
        st.error(f"PDF reading error: {e}")
        return None


def _extract_json_block(raw_text: str) -> str | None:
    fence = re.search(r"```(?:json)?\s*({[\s\S]*?})\s*```", raw_text, re.IGNORECASE)
    if fence:
        return fence.group(1)
    brace = re.search(r"\{[\s\S]*\}", raw_text)
    if brace:
        return brace.group(0)
    return None


def analyzecv_pdf_withllm(text: str, report_language: str) -> dict[str, Any] | None:
    prompt = get_resume_analysis_prompt(text, report_language)
    try:
        response = Model.generate_content(prompt)
        raw_text = (response.text or "").strip()
        if not (json_str := _extract_json_block(raw_text)):
            st.error(
                "Sorry, the analysis could not be completed. Please try again later or upload a different file."
            )
            return None

        if not isinstance(data := json.loads(json_str), dict):
            st.error("Invalid JSON object.")
            return None

        return cast(dict[str, Any], data)
    except Exception as e:
        st.error(
            f"An error occurred while processing your resume. Please try again or upload a different file. Details: {e}"
        )
        return None


def _safe_dict(obj: dict[str, Any], key: str) -> dict[str, Any]:
    val = obj.get(key, {})
    return val if isinstance(val, dict) else {}


def display_language_info(result: dict[str, Any]) -> None:
    st.subheader("Detected Language")
    st.write(result.get("language", "Not detected"))


def display_domain_scores(result: dict[str, Any]) -> None:
    st.subheader("Career Domain Fit Scores")
    domains: list[dict[str, Any]] = result.get("domain_scores", []) or []
    if domains:
        st.table(
            [
                {
                    "Domain": d.get("domain", ""),
                    "Score": d.get("score", ""),
                    "Justification": d.get("justification", ""),
                }
                for d in domains
            ]
        )


def display_competency_scores(result: dict[str, Any]) -> None:
    st.subheader("Competency Evaluation")
    comps: list[dict[str, Any]] = result.get("competency_scores", []) or []
    if comps:
        st.table(
            [
                {
                    "Category": c.get("category", ""),
                    "Score": c.get("score", ""),
                    "Strength": c.get("strength", ""),
                    "Observation": c.get("observation", ""),
                }
                for c in comps
            ]
        )


def display_strategic_insights(result: dict[str, Any]) -> None:
    st.subheader("Strategic Insights")
    st.write(result.get("strategic_insights", "N/A"))


def display_development_recommendations(result: dict[str, Any]) -> None:
    st.subheader("Development Recommendations")
    for rec in result.get("development_recommendations", []) or []:
        st.markdown(f"- {rec}")


def display_comparative_benchmarking(result: dict[str, Any]) -> None:
    st.subheader("Comparative Benchmarking")
    text = result.get("comparative_benchmarking", "N/A")
    st.write(text if isinstance(text, str) and text else "N/A")


def display_overall_summary(result: dict[str, Any]) -> None:
    st.subheader("Overall Summary")
    summary: dict[str, Any] = result.get("overall_summary", {}) or {}
    st.markdown(f"**Overall Score:** {summary.get('overall_score', 'N/A')}/100")
    st.markdown("**Key Strengths:**")
    for s in summary.get("key_strengths", []) or []:
        st.markdown(f"- {s}")
    st.markdown("**Areas to Improve:**")
    for a in summary.get("areas_to_improve", []) or []:
        st.markdown(f"- {a}")
    st.markdown(f"**Talent Potential:** {summary.get('talent_potential', 'N/A')}")


def display_analysis_results(result: dict[str, Any]) -> None:
    display_language_info(result)
    display_domain_scores(result)
    display_competency_scores(result)
    display_strategic_insights(result)
    display_development_recommendations(result)
    display_comparative_benchmarking(result)
    display_overall_summary(result)


def display_summary_block(result: dict[str, Any]) -> None:
    st.subheader("Overall Summary")
    summary = _safe_dict(result, "overall_summary")
    c1, c2, c3 = st.columns(3)
    overall = summary.get("overall_score", None)
    c1.metric("Overall Score", f"{overall}/100" if overall is not None else "N/A")
    c2.metric("Talent Potential", summary.get("talent_potential", "N/A"))
    lang = result.get("language", "Not detected")
    c3.metric("Detected Language", lang)

    strengths = summary.get("key_strengths", []) or []
    areas = summary.get("areas_to_improve", []) or []
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Key Strengths")
        st.markdown("\n".join(f"- {s}" for s in strengths) if strengths else "—")
    with col_b:
        st.subheader("Areas to Improve")
        st.markdown("\n".join(f"- {a}" for a in areas) if areas else "—")

    role_suit = summary.get("role_suitability", []) or []
    if role_suit:
        st.markdown("**Role Suitability**")
        df = pd.DataFrame(
            [
                {"Role": r.get("role", ""), "Score": r.get("score", "")}
                for r in role_suit
            ]
        )
        st.dataframe(df, width="stretch")


def display_fit_and_gaps_tab(result: dict[str, Any]) -> None:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Missing Skills")
        ms: list[dict[str, Any]] = result.get("missing_skills", []) or []
        if ms:
            rows = [
                {
                    "Skill": i.get("skill", ""),
                    "Priority": str(i.get("priority", "")).strip(),
                }
                for i in ms
            ]
            st.dataframe(pd.DataFrame(rows), width="stretch")
        else:
            st.write("No missing skills.")
    with col2:
        st.markdown("### Mismatched Experience")
        mm = result.get("mismatched_experience", []) or []
        if mm:
            for ex in mm:
                st.markdown(f"- {ex}")
        else:
            st.write("No mismatches detected.")


def display_competencies_tab(result: dict[str, Any]) -> None:
    st.markdown("### Competency Evaluation")
    comps = result.get("competency_scores", []) or []
    if comps:

        def _score(x: dict[str, Any]) -> float:
            try:
                return float(x.get("score", 0))
            except Exception:
                return 0.0

        comps_sorted = sorted(comps, key=_score, reverse=True)
        df = pd.DataFrame(
            [
                {
                    "Category": c.get("category", ""),
                    "Score": c.get("score", ""),
                    "Strength": c.get("strength", ""),
                    "Observation": c.get("observation", ""),
                }
                for c in comps_sorted
            ]
        )
        st.dataframe(df, width="stretch")
    else:
        st.info("No competency scores returned.")


def display_domains_tab(result: dict[str, Any]) -> None:
    st.markdown("### Career Domain Fit Scores")
    domains = result.get("domain_scores", []) or []
    if domains:
        try:
            domains_sorted = sorted(
                domains, key=lambda d: float(d.get("score", 0)), reverse=True
            )
        except Exception:
            domains_sorted = domains
        df = pd.DataFrame(
            [
                {
                    "Domain": d.get("domain", ""),
                    "Score": d.get("score", ""),
                    "Justification": d.get("justification", ""),
                }
                for d in domains_sorted
            ]
        )
        st.dataframe(df, width="stretch")
    else:
        st.info("No domain scores returned.")


def display_insights_tab(result: dict[str, Any]) -> None:
    left, right = st.columns([3, 2])
    with left:
        st.markdown("### Strategic Insights")
        st.write(result.get("strategic_insights", "N/A"))
    with right:
        st.markdown("### Comparative Benchmarking")
        cb = result.get("comparative_benchmarking", "")
        st.write(cb if isinstance(cb, str) and cb.strip() else "Not provided.")


def display_recommendations_tab(result: dict[str, Any]) -> None:
    st.markdown("### Development Recommendations")
    recs = result.get("development_recommendations", []) or []
    if recs:
        for r in recs:
            st.markdown(f"- {r}")
    else:
        st.info("No recommendations returned.")


def display_analysis_tabs(result: dict[str, Any]) -> None:
    display_summary_block(result)
    tabs = st.tabs(
        [
            "Fit & Gaps",
            "Competencies",
            "Domains",
            "Insights",
            "Recommendations",
        ]
    )
    with tabs[0]:
        display_fit_and_gaps_tab(result)
    with tabs[1]:
        display_competencies_tab(result)
    with tabs[2]:
        display_domains_tab(result)
    with tabs[3]:
        display_insights_tab(result)
    with tabs[4]:
        display_recommendations_tab(result)


st.title("Advanced Resume Analysis Application")

uploaded_file = st.file_uploader("Upload your Resume (PDF)", type="pdf")
if uploaded_file:
    text = extract_text_from_pdf(uploaded_file)
    if text:
        st.subheader("Select report language")
        language_options = [
            "Czech",
            "Danish",
            "Dutch",
            "English",
            "Finnish",
            "French",
            "German",
            "Greek",
            "Italian",
            "Kurdish (Kurmanji)",
            "Polish",
            "Portuguese",
            "Russian",
            "Spanish",
            "Swedish",
            "Turkish",
            "Ukrainian",
        ]
        selected_language = st.selectbox(
            "Choose a language for the report",
            language_options,
            index=language_options.index("English"),
        )

        if st.button("Analyze Resume"):
            with st.spinner("Analyzing Resume..."):
                result = analyzecv_pdf_withllm(text, selected_language)
                if result:
                    display_analysis_tabs(result)
