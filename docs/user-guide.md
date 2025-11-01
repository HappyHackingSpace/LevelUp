# User Guide

This guide will help you get started with LevelUP and make the most of its features.

## Getting Started

### 1. Setting Up Your Environment

First, ensure you have the required dependencies:

```bash
# Install dependencies
uv sync

# Configure your API key
echo "GEMINI_API_KEY=your_key_here" > .env
```

### 2. Running LevelUP

You can use LevelUP in two ways:

#### Option A: Web Interface (Streamlit)

```bash
streamlit run levelup/app.py
```

This starts a web interface at `http://localhost:8501` where you can:

- Upload your CV (PDF format)
- Select report language
- View analysis results

#### Option B: REST API

```bash
uvicorn levelup.main:app --reload
```

This starts the API server at `http://localhost:8000` where you can:

- Access interactive API docs at `/docs`
- Make programmatic API calls
- Integrate with other applications

## Using the Web Interface

### Step-by-Step Process

1. **Upload Your CV**
   - Click "Upload your Resume (PDF)"
   - Select your CV file
   - Wait for text extraction

2. **Choose Report Language**
   - Select from available languages
   - Languages supported: English, German, French, Italian, Russian, Turkish, Spanish

3. **Analyze**
   - Click "Analyze Resume"
   - Wait for AI processing (typically 30-60 seconds)
   - Review results

### Understanding the Results

The analysis provides several sections:

#### **Detected Language**

Shows the primary language detected in your CV.

#### **Career Domain Fit Scores**

Each domain receives:

- **Score**: Fit percentage (0-100)
- **Domain**: Career area (e.g., "Software Development", "Data Science")
- **Justification**: Why this score was given

#### **Competency Evaluation**

For each skill category:

- **Category**: Skill area
- **Score**: Strength rating
- **Strength**: Key abilities
- **Observation**: Areas for improvement

#### **Strategic Insights**

High-level career recommendations and market positioning advice.

#### **Development Recommendations**

Actionable steps to improve your CV and career prospects.

#### **Overall Summary**

- Overall score out of 100
- Key strengths
- Areas to improve
- Talent potential assessment

## Using the REST API

### Authentication

Currently, the API doesn't require authentication for testing. For production, you should implement proper authentication.

### Example API Call

```python
import requests

# Upload and analyze a CV
with open("your_cv.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        files={"file": f},
        data={"language": "English"}
    )

results = response.json()
print(results)
```

### Available Endpoints

- `GET /api/v1/` - API information
- `POST /api/v1/analyze` - Analyze CV
- `GET /health` - Health check

See [API Reference](api.md) for complete documentation.

## Tips for Best Results

### CV Preparation

1. **Clear Formatting**: Use well-structured layouts
2. **Complete Information**: Include all relevant experiences and skills
3. **Consistent Dates**: Use standard date formats
4. **Keywords**: Include industry-relevant terminology
5. **Proper Grammar**: Ensure professional language

### Language Selection

- Choose the language you want for the **report**, not necessarily the CV language
- The AI automatically detects the CV's primary language
- You can generate reports in different languages for international opportunities

### Interpreting Scores

- **80-100**: Excellent fit, highlight as primary strength
- **60-79**: Good fit, show as competency
- **40-59**: Moderate fit, can develop further
- **0-39**: Limited fit, focus on other areas

## Troubleshooting

### Common Issues

**"PDF reading error"**

- Ensure the file is a valid PDF
- Try converting from another format
- Check if the PDF is password-protected

**"Analysis could not be completed"**

- Check your internet connection
- Verify your Gemini API key is valid
- Try uploading again

**"API connection error"**

- Ensure the server is running
- Check API endpoint URL
- Verify network connectivity

## Advanced Usage

### Batch Processing

For analyzing multiple CVs:

```python
import os
from pathlib import Path

cv_directory = Path("cvs")
for cv_file in cv_directory.glob("*.pdf"):
    # Process each CV
    analyze_cv(cv_file)
```

### Custom Analysis

Extend the base prompts to include additional analysis dimensions:

```python
from levelup.prompts import get_resume_analysis_prompt

custom_prompt = get_resume_analysis_prompt(
    text=cv_text,
    report_language="English",
    # Add custom instructions
)
```

## Next Steps

- [API Reference](api.md) - Detailed API documentation
- [Contributing](contributing.md) - Help improve LevelUP
- [Changelog](changelog.md) - See what's new
