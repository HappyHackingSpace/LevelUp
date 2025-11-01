# LevelUp

## Description

LevelUp is an AI-powered career companion that helps professionals understand, enhance, and present their skills with clarity.
It analyzes resumes, identifies competency gaps, matches users to ideal roles, and provides personalized recommendations for career growth.


## Features

* Resume Analysis: Evaluate strengths, weaknesses, and skill relevance.
* Competency Mapping: Compare user profiles against target roles.
* Company Suggestions: Recommend organizations that align with the user’s background and goals.
* Smart Resume Generation: Build optimized resumes from text input or uploaded documents.
* Social Insights: Integrate LinkedIn, GitHub, and other profiles for richer analysis.
* Career Notifications: Get alerts on opportunities, improvements, and new matches.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd LevelUp
   ```

2. Install dependencies (using `pyproject.toml`):
   ```bash
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
   streamlit run src/levelup/app.py
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
