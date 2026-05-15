import json
import re
from pathlib import Path
from typing import Optional

import google.generativeai as genai
import pdfplumber
import typer

from levelup import config
from levelup.prompts import get_resume_analysis_prompt

app = typer.Typer(name="levelup", help="AI-powered CV analysis from the command line.")

LANGUAGES = [
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


def _extract_text(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        parts = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(parts).strip()


def _extract_json(raw: str) -> dict | None:
    fence = re.search(r"```(?:json)?\s*({[\s\S]*?})\s*```", raw, re.IGNORECASE)
    if fence:
        block = fence.group(1)
    else:
        match = re.search(r"\{[\s\S]*\}", raw)
        block = match.group(0) if match else None
    if not block:
        return None
    try:
        result = json.loads(block)
        return result if isinstance(result, dict) else None
    except json.JSONDecodeError:
        return None


@app.command()
def analyze(
    resume: Path = typer.Argument(..., help="Path to the PDF resume file."),
    language: str = typer.Option(
        "English", "--language", "-l", help="Report language."
    ),
    role: Optional[str] = typer.Option(
        None, "--role", "-r", help="Target role for the analysis."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Save JSON output to a file."
    ),
) -> None:
    if not resume.exists():
        typer.echo(f"Error: file not found: {resume}", err=True)
        raise typer.Exit(1)

    if language not in LANGUAGES:
        typer.echo(
            f"Error: unsupported language '{language}'.\nAvailable: {', '.join(LANGUAGES)}",
            err=True,
        )
        raise typer.Exit(1)

    if not config.GEMINI_API_KEY:
        typer.echo("Error: GEMINI_API_KEY is not set.", err=True)
        raise typer.Exit(1)

    typer.echo("Extracting text from PDF...")
    try:
        text = _extract_text(resume)
    except Exception as e:
        typer.echo(f"Error reading PDF: {e}", err=True)
        raise typer.Exit(1)

    if not text:
        typer.echo("Error: could not extract text from the PDF.", err=True)
        raise typer.Exit(1)

    typer.echo("Analyzing resume...")
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-2.0-flash-lite")
    prompt = get_resume_analysis_prompt(text, language, role)

    try:
        response = model.generate_content(prompt)
        raw = (response.text or "").strip()
    except Exception as e:
        typer.echo(f"Error calling LLM: {e}", err=True)
        raise typer.Exit(1)

    result = _extract_json(raw)
    if not result:
        typer.echo("Error: could not parse the analysis response.", err=True)
        raise typer.Exit(1)

    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if output:
        output.write_text(output_json, encoding="utf-8")
        typer.echo(f"Results saved to {output}")
    else:
        typer.echo(output_json)


def main() -> None:
    app()
