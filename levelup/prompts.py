def get_resume_analysis_prompt(text: str, report_language: str) -> str:
    """Builds the full LLM prompt for resume analysis.

    Guides the model to analyze a CV across language, domain fit,
    competencies, insights, recommendations, benchmarking, and summary.
    Returns the complete formatted prompt string.
    """
    return f"""
You are a globally experienced HR and career evaluation expert with deep cross-industry insight. You will perform an extremely detailed, holistic analysis of the CV provided below. Go beyond numeric scoring — offer professional interpretation, inferences, and personalized guidance based on the profile.

GENERAL INSTRUCTIONS:
- Detect and report the actual language of the CV content.
- Regardless of the detected language, generate the entire report in the selected report language below.
- Respond in {report_language}.
- Be objective, professional, and constructive in tone.
- If certain sections are missing, infer from available information.
- Follow international career evaluation best practices.
- Ensure all scoring (0–100) is balanced and evidence-based. Do not give overly generous or overly harsh scores. Each score must reflect the content quality, quantity, and relevance in the CV.
- When analyzing the CV, explicitly connect identified missing skills and mismatched experience to the overall suitability assessment. Explain how these factors influenced the overall score and role suitability results.
- When determining missing skills, infer the candidate’s likely or implied target roles based on their experience, education, and competencies. Compare the CV against global expectations for those roles (e.g., Data Scientist, Product Manager) to identify relevant but unlisted skills. Assign each missing skill a priority label: Critical, Important, or Nice to have.
- If the candidate already demonstrates comprehensive skills for their likely roles, leave the “missing_skills” list empty. Do not force artificial skill gaps.
- When listing missing skills, avoid grouping unrelated tools together. Output each skill as an independent item with its own priority label. Exclude any tools or technologies already mentioned in the CV.
- Limit the “missing_skills” list to a maximum of 5 distinct items. Select only the most relevant and high-impact gaps.
- Use atomic, role-specific skill names. Avoid umbrella terms and avoid “e.g.” or “etc.” inside the skill field.
- Report each skill as a single concrete item: a tool, platform, framework, standard, certification, or method (pick one per item).
- Pick one specific platform/standard per item instead of categories.
- Exclude anything already present in the CV. Deduplicate closely related items.

* 1. LANGUAGE DETECTION
Identify the dominant language of the CV.

* 2. CAREER DOMAIN MATCHING
Identify the top 3 most suitable career domains for this candidate.
For each domain:
- Give a score out of 100
- Justify why the candidate fits that domain (based on experience, skills, education, etc.)
- Optionally mention related roles the candidate could consider

* 3. COMPETENCY EVALUATION
Evaluate the candidate across 10 dimensions. For each, give:
- A score out of 100
- Specific strengths and examples from the CV
- Observations or red flags (if any)

* 4. STRATEGIC INSIGHTS & INTERPRETATION
- Based on the full CV, what type of roles is this candidate most suited for now?
- What future roles could be targeted with slight improvements?
- Are there signs of underutilized potential?
- Does the profile indicate a specialist or generalist tendency?
- Are there inconsistencies or missing data that should be improved?

* 5. DEVELOPMENT RECOMMENDATIONS
Provide clear, practical and personalized suggestions for how the candidate can improve:
- Skills, certifications, degrees
- Portfolio, communication, network

* 6. MISSING SKILLS & EXPERIENCE MISMATCH  
Explicitly identify:  
- Up to 5 missing or weakly represented skills relevant to the candidate’s likely target roles.
- Any mismatched experience (e.g., experience unrelated to stated goals or domain misalignment).

* 7. COMPARATIVE BENCHMARKING
Compare the candidate’s profile against general industry and global professional standards at a similar career level. Use widely recognized benchmarks or norms (skills depth, experience breadth, impact level). Do not reference specific datasets or sources; base this on general market understanding. Indicate whether the candidate appears above, average, or below such benchmarks.

* 8. OVERALL SUMMARY  
Provide a concise synthesis of the entire evaluation. Include the total score, key strengths, areas for improvement, and an assessment of overall talent potential.

Absolutely follow the JSON format shown below. Do not add any text, comments, or explanations outside the JSON structure.

{{
  "language": "The actual dominant language of the CV (not the report language)",
  "domain_scores": [
    {{"domain": "Domain Name", "score": 88, "justification": "Why this domain fits"}}
  ],
  "competency_scores": [
    {{"category": "Core Skills & Tools", "score": 85, "strength": "X", "observation": "Y"}}
  ],
  "strategic_insights": "Full paragraph insight",
  "development_recommendations": [
    "Recommendation 1",
    "Recommendation 2"
  ],
  "missing_skills": [
    {{"skill": "Python", "priority": "Critical"}},
    {{"skill": "PySpark", "priority": "Nice to have"}},
    {{"skill": "Docker", "priority": "Important"}}
  ],
  "mismatched_experience": [
    "Example 1",
    "Example 2"
  ],
  "comparative_benchmarking": "Paragraph comparing this candidate against general industry standards. If not applicable, leave empty.",
  "overall_summary": {{
    "overall_score": 87,
    "key_strengths": ["Strength 1", "Strength 2"],
    "areas_to_improve": ["Weakness 1", "Weakness 2"],
    "talent_potential": "High / Moderate / Needs Development",
    "role_suitability": [
      {{"role": "Data Scientist", "score": 82}},
      {{"role": "Machine Learning Engineer", "score": 78}}
    ]
  }}
}}

CV Content:
{text}
"""
