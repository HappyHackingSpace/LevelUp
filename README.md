# LevelUp

## Description

LevelUp is a professional resume analysis platform that evaluates CVs with advanced language models.
It provides a structured, objective, and multilingual assessment of a candidate’s experience, skills, and career potential.
The system delivers clear insights across multiple dimensions, helping professionals understand their current positioning and growth opportunities.

## Features

- **PDF CV Upload:** Users can easily upload their CVs in PDF format.
- **Multi-Language Support:** Analysis reports available in English, German, French, Italian, Russian, Turkish, and Spanish.
- **Language Detection:** Detects the dominant language of the CV content.
- **Career Domain Matching:** Identifies top career domains with scores and justifications.
- **Competency Evaluation:** Rates core and transferable skills with detailed observations.
- **Strategic Insights:** Summarizes professional trajectory, role suitability, and potential growth areas.
- **Development Recommendations:** Provides targeted suggestions for skill and career improvement.
- **Missing Skills & Experience Mismatch:** Highlights weak or absent skills and misalignments.
- **Comparative Benchmarking:** Benchmarks the profile against global professional standards.
- **Overall Summary:** Consolidates results into total score, strengths, and improvement areas.
- **Structured JSON Output:** Clean, parseable analysis results.
- **User-Friendly Interface:** The interface, built with Streamlit, provides easy and intuitive use.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd LevelUp
   ```

2. Install dependencies (recommended via uv or pip):

   ```bash
   # Option 1: use uv
   uv sync
   
   # Option 2: use pip
   pip install -e .[dev]
   ```

   Or with `requirements.txt` (legacy):

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your Gemini API key:

   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. Run the application:

   ```bash
   streamlit run levelup/app.py
   ```

2. Upload your CV in PDF format.

3. Select your preferred language for the analysis report.

4. Click "Analyze Resume" and wait for the comprehensive analysis.

5. Review the detailed results including:
   - Career domain fit scores
   - Competency evaluation
   - Strategic insights
   - Development recommendations
   - Overall summary with talent potential assessment

## Development

Run code checks before committing:

```bash
uv run ruff check .
uv run mypy .
pytest -q
```

## Contribution

Your contributions will help us make this project better. Please use GitHub issues for bug reports or feature requests.
