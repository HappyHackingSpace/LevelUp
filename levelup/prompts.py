def get_resume_analysis_prompt(
    text: str, report_language: str, target_role: str | None = None
) -> str:
    """Builds the full LLM prompt for resume analysis, with optional strong target-role conditioning."""

    notes = {
        "domain": "",
        "competency": "",
        "insights": "",
        "recommendations": "",
        "missing_skills": "",
        "benchmarking": "",
        "summary": "",
        "strengths": "",
    }

    target_role_block = ""
    if target_role is not None:
        target_role_block = f"""
        TARGET ROLE FOCUS:
        - The candidate explicitly targets the role: "{target_role}".
        - All scores, justifications, insights, and recommendations must be evaluated relative to global expectations for "{target_role}" at the candidate’s apparent seniority level.
        - Every numeric score (domain_scores, competency_scores, overall_score, role_suitability scores) must reflect how strong the candidate is for "{target_role}" (not for their past or current role).
        - Every justification, strength, observation, insight, recommendation, and benchmarking comment must explicitly refer to the candidate’s fit for "{target_role}".
        - You may mention other suitable roles or domains, but always describe them in relation to the candidate’s primary fit for "{target_role}".

        CONSISTENCY REQUIREMENTS FOR SCORES:
        - The "overall_score" MUST always represent the candidate’s overall fit for "{target_role}" only.
        - In "overall_summary.role_suitability":
          - The FIRST item MUST have "role": "{target_role}".
          - Its "score" MUST be EXACTLY equal to "overall_score".
        - NO other role_suitability entry may have a score higher than "overall_score".
        - When evaluating suitability for "{target_role}", heavily weight core role-specific capabilities.
        - If the candidate’s experience is primarily in a different domain than "{target_role}" (e.g., Data Science vs Software Engineering), 
          and there is limited direct evidence of core "{target_role}" responsibilities (such as algorithms/data structures, software design, testing, CI/CD, scalable services), then:
          - The "{target_role}" role_suitability score (and thus "overall_score") MUST NOT exceed 70.
        - Scores of 80 or above for "{target_role}" require clear, explicit, repeated evidence of strong performance in core "{target_role}" responsibilities, not just adjacent or related work.
"""
        notes["domain"] = f"""
- For each domain, interpret the score as: "How strong is this candidate in this domain while working as "{target_role}"?".
- At least one domain must clearly correspond to "{target_role}" (or a closely related domain label), and the justification must reference "{target_role}" explicitly.
"""
        notes["competency"] = f"""
- Each competency score must be benchmarked against typical expectations for "{target_role}" at the candidate’s current level.
- Strengths and observations must clearly explain how they support or limit performance as "{target_role}".
"""
        notes["insights"] = f"""
- Explicitly classify the candidate’s current fit for "{target_role}" as strong, moderate, or weak, with clear reasoning.
- State whether "{target_role}" is realistic in the short to medium term and under which conditions.
"""
        notes["recommendations"] = f"""
- All recommendations must be framed as concrete actions that increase the candidate’s competitiveness for "{target_role}".
"""
        notes["missing_skills"] = f"""
- When identifying missing skills, prioritize gaps that are most important for succeeding as "{target_role}" in the global market at this level.
"""
        notes["benchmarking"] = f"""
- Compare the candidate specifically with typical professionals working as "{target_role}" at a similar career level, and state whether they are above, at, or below this benchmark.
"""
        notes["summary"] = f"""
- Clearly state overall fit for "{target_role}", the main gaps that limit performance in this role, and whether the target is realistic now or requires significant upskilling.
"""
        notes["strengths"] = f"""
-  Only list the person's strengths that align with the {target_role} role. Do not list strengths that are unrelated to the {target_role} role.
- In all strength-related sections (including "overall_summary.key_strengths"), list strengths that directly support success as "{target_role}" or clearly demonstrate transferable potential toward becoming a stronger "{target_role}" candidate.
- Avoid listing strengths that are only relevant to the candidate’s original role and do not materially contribute to performance as "{target_role}".
- If a skill is strongly domain-specific to the candidate’s original role (e.g., ML/AI/LLM tooling for a Data Scientist), DO NOT list it as a strength for the target role unless it directly supports core responsibilities of "{target_role}" (such as scalable software development, software architecture, performance, reliability, system design, or production engineering).
- Focus on strengths that are clearly relevant to "{target_role}". Do not mention strengths that are not suitable for the target role.
"""
    else:
        notes["strengths"] = """
- In all strength-related sections (including "overall_summary.key_strengths"), list strengths that best summarize the candidate’s value across their top likely roles inferred from the CV.
- Focus on strengths that are robust and transferable across multiple plausible career paths (e.g., strong programming fundamentals, problem solving, ownership, communication).
- Avoid overly narrow, niche strengths that are locked into a single, highly specific role unless that role is clearly dominant in the CV.
"""

    primary_role_for_json = (
        target_role if target_role is not None else "Primary Likely Role"
    )

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

{target_role_block}

* 1. LANGUAGE DETECTION
Identify the dominant language of the CV.

* 2. CAREER DOMAIN MATCHING
Identify the top 3 most suitable career domains for this candidate.
For each domain:
- Give a score out of 100.
- Justify why the candidate fits that domain (based on experience, skills, education, and impact).
- Optionally mention related roles the candidate could consider.
{notes["domain"]}

* 3. COMPETENCY EVALUATION
Evaluate the candidate across 10 dimensions (for example: Core Technical Skills, Tools & Technologies, Problem Solving, Business Impact, Communication, Leadership, Collaboration, Learning Agility, Domain Knowledge, Delivery & Reliability). For each dimension:
- Assign a score out of 100.
- Describe concrete strengths and examples from the CV.
- Note any observations or red flags (e.g., lack of scale, missing ownership, shallow impact).
{notes["competency"]}

* 4. STRATEGIC INSIGHTS & INTERPRETATION
Based on the full CV:
- Which types of roles is this candidate most suited for now?
- Which future roles could be realistic with incremental improvements?
- Are there signs of underutilized potential (e.g., skills that are not fully leveraged)?
- Does the profile suggest a specialist or generalist tendency?
- Are there any inconsistencies, gaps, or missing data that should be clarified or improved?
{notes["insights"]}

* 5. DEVELOPMENT RECOMMENDATIONS
Provide clear, practical, and personalized suggestions on how the candidate can strengthen their profile:
- Skills, tools, and methods to learn or deepen.
- Certifications or degrees that would be valuable.
- Portfolio, project, or publication ideas.
- Improvements in communication, stakeholder management, and professional networking.
{notes["recommendations"]}

* 6. MISSING SKILLS & EXPERIENCE MISMATCH
Explicitly identify:
- Up to 5 missing or weakly represented skills that are relevant to the candidate’s likely or explicit target roles.
- Any mismatched experience (e.g., long periods in unrelated domains, activities that do not support their stated or implied career direction) and how this affects perceived fit.
{notes["missing_skills"]}

* 7. COMPARATIVE BENCHMARKING
Compare the candidate’s profile against general industry and global professional standards at a similar career level. Consider:
- Depth and breadth of skills.
- Scope and impact of experience.
- Ownership, autonomy, and complexity of work.
Indicate whether the candidate appears above, at, or below typical benchmarks.
{notes["benchmarking"]}

* 8. KEY STRENGTHS INSIGHTS (key_strengths)
Provide 3–5 high-level strategic insights about the candidate’s profile, career trajectory, and market positioning.
- Focus on strengths that are most relevant to the candidate’s current and near-future roles.
{notes["strengths"]}

* 9. OVERALL SUMMARY
Provide a concise synthesis of the entire evaluation. Include:
- A single overall score (0–100) summarizing the profile.
- Key strengths.
- Priority areas for improvement.
- An overall view of talent potential (High / Moderate / Needs Development).
- A short assessment of the candidate’s role suitability across 2–3 key roles.
{notes["summary"]}

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
    {{"skill": "ExampleSkill1", "priority": "Critical"}},
    {{"skill": "ExampleSkill2", "priority": "Important"}}
  ],
  "mismatched_experience": [
    "Example of experience that does not fully align with the candidate’s direction"
  ],
  "comparative_benchmarking": "Paragraph comparing this candidate against general industry standards. If not applicable, leave empty.",
  "overall_summary": {{
    "overall_score": 87,
    "key_strengths": ["Strength 1", "Strength 2"],
    "areas_to_improve": ["Weakness 1", "Weakness 2"],
    "talent_potential": "High / Moderate / Needs Development",
    "role_suitability": [
      {{"role": "{primary_role_for_json}", "score": 82}},
      {{"role": "Secondary Likely or Related Role", "score": 78}}
    ]
  }}
}}

CV Content:
{text}
"""
