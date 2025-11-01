# ResumeX

## Description

ResumeX is an advanced AI-powered CV analysis application that provides comprehensive career evaluation and insights.
Users can upload their CVs in PDF format and receive detailed analysis through the Gemini API.
The application offers multi-language support and provides structured analysis covering career domain matching,
competency evaluation, strategic insights, and personalized development recommendations.

## Features

- **PDF CV Upload:** Users can easily upload their CVs in PDF format.
- **Multi-Language Support:** Analysis reports available in English, German, French, Italian, Russian, Turkish, and Spanish.
- **Gemini API Integration:** CVs are analyzed using AI with the Gemini API.
- **Comprehensive Analysis:**
  - Career domain matching with scoring
  - Competency evaluation across 10 dimensions
  - Strategic insights and career path recommendations
  - Development recommendations
  - Comparative benchmarking
- **Structured JSON Output:** Clean, parseable analysis results.
- **User-Friendly Interface:** The interface, built with Streamlit, provides easy and intuitive use.
- **Environment Configuration:** Secure API key management with `.env` support.

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd resumeX
   ```

2. Install dependencies (using `pyproject.toml`):

   ```bash
   uv sync or
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
   streamlit run src/resumex/app.py
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

## Contribution

Your contributions will help us make this project better. Please use GitHub issues for bug reports or feature requests.
