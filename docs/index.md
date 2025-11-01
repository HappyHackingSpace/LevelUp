# ResumeX Documentation

Welcome to ResumeX - an advanced AI-powered CV analysis application.

## Overview

ResumeX is a comprehensive career evaluation platform that uses Google's Gemini AI to analyze CVs and resumes.
The application provides detailed insights into career domain matching,
competency evaluation, and personalized development recommendations.

## Key Features

### 🤖 AI-Powered Analysis

- Google Gemini API integration for intelligent CV analysis
- Multi-language report generation (English, German, French, Italian, Russian, Turkish, Spanish)

### 📊 Comprehensive Evaluation

- **Career Domain Matching**: Score how well your CV fits different career domains
- **Competency Assessment**: Evaluate skills across 10 dimensions
- **Strategic Insights**: Get actionable career path recommendations
- **Development Recommendations**: Personalized improvement suggestions
- **Benchmarking**: Compare your profile against industry standards

### 🚀 Easy to Use

- Simple PDF upload interface
- Fast, accurate analysis
- Structured JSON output
- Beautiful, user-friendly reports

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/HappyHackingSpace/resumex
cd resumex

# Install dependencies
uv sync
```

### Configuration

Create a `.env` file with your Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
```

### Running the Application

```bash
# Streamlit UI
streamlit run resumex/app.py

# FastAPI Backend
uvicorn resumex.main:app --reload
```

## Architecture

ResumeX is built with:

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **AI**: Google Gemini API
- **Frontend**: Streamlit (optional)
- **Documentation**: MkDocs

## Next Steps

- [User Guide](user-guide.md) - Learn how to use ResumeX effectively
- [API Reference](api.md) - Explore the REST API
- [Contributing](contributing.md) - Help improve ResumeX

## Support

- GitHub: [HappyHackingSpace/resumex](https://github.com/HappyHackingSpace/resumex)
- Discord: [Happy Hacking Space](https://discord.gg/happyhackingspace)
