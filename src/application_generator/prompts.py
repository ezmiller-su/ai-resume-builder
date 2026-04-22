"""
Prompt templates and builder functions for LLM calls.

All prompts live here so they can be reviewed, versioned, and edited in one place
without touching generation logic. Builder functions accept structured inputs and
return fully formatted prompt strings ready to pass to the LLM client.

Convention:
  - Template constants are UPPER_SNAKE_CASE strings with {placeholder} slots.
  - Builder functions are lower_snake_case and return str.
"""

from typing import Dict, List

from .models.job_description import JobDescription
from .models.user_materials import UserMaterialChunk


# ---------------------------------------------------------------------------
# Job requirement extraction
# ---------------------------------------------------------------------------

JOB_REQUIREMENTS_PROMPT = """
You are a job description analyst. Extract the key requirements from the job posting below.

Return a JSON object with three keys:
  - "responsibilities": list of core job responsibilities (bullet-point level)
  - "qualifications": list of required or preferred qualifications
  - "keywords": list of important skills, tools, or domain terms

Job Posting:
{raw_text}

Return only valid JSON. Do not add commentary outside the JSON object.
""".strip()


def build_job_requirements_prompt(job: JobDescription) -> str:
    """Build the prompt for extracting structured requirements from a job posting."""
    return JOB_REQUIREMENTS_PROMPT.format(raw_text=job.raw_text)


# ---------------------------------------------------------------------------
# Material-to-role matching / ranking
# ---------------------------------------------------------------------------

MATERIAL_MATCH_PROMPT = """
You are a career coach. Score how well each user material chunk matches the job requirements below.

Job Title: {job_title}
Key Requirements:
{requirements_block}

User Material Chunks:
{chunks_block}

For each chunk, respond with a JSON list of objects:
  {{"chunk_index": <int>, "relevance_score": <float 0.0-1.0>, "reason": "<brief reason>"}}

Return only valid JSON. Do not add commentary outside the JSON array.
""".strip()


def build_material_match_prompt(
    job: JobDescription,
    requirements: Dict[str, List[str]],
    chunks: List[UserMaterialChunk],
) -> str:
    """Build the prompt for scoring user material chunks against job requirements."""
    reqs_lines = []
    for category, items in requirements.items():
        for item in items:
            reqs_lines.append(f"- [{category}] {item}")
    requirements_block = "\n".join(reqs_lines) or "(none extracted)"

    chunks_block = "\n\n".join(
        f"Chunk {i}:\n  source_type: {c.source_type}\n  content: {c.content}"
        for i, c in enumerate(chunks)
    )

    return MATERIAL_MATCH_PROMPT.format(
        job_title=job.title,
        requirements_block=requirements_block,
        chunks_block=chunks_block,
    )


# ---------------------------------------------------------------------------
# CV / resume generation
# ---------------------------------------------------------------------------

CV_GENERATION_PROMPT = """
You are an expert resume writer. Write tailored resume content for the role below.

Role: {job_title} at {company}
Key Requirements:
{requirements_block}

User's Source Material (use only what is provided — do not invent or embellish):
{chunks_block}

Preferences:
- Tone: {tone}
- Truthfulness: {truthfulness_note}
- Language style: {language_style}

Instructions:
1. Produce resume sections in this order: {section_order}
2. For each section, write concise bullet points grounded strictly in the source material.
3. Use strong action verbs.
4. Do not fabricate any skills, experience, or achievements not present in the source material.

Return a JSON object where each key is a section heading and each value is a list of bullet strings.
""".strip()


def build_cv_generation_prompt(
    job: JobDescription,
    requirements: Dict[str, List[str]],
    chunks: List[UserMaterialChunk],
    preferences: Dict,
) -> str:
    """Build the full prompt for CV/resume content generation."""
    reqs_block = "\n".join(
        f"- [{cat}] {item}"
        for cat, items in requirements.items()
        for item in items
    ) or "(none extracted)"

    chunks_block = "\n\n".join(
        f"[{c.source_type}] {c.content}" for c in chunks
    ) or "(no source material provided)"

    section_order = ", ".join(
        preferences.get("section_order", ["Summary", "Experience", "Projects", "Education", "Skills"])
    )

    return CV_GENERATION_PROMPT.format(
        job_title=job.title,
        company=job.company,
        requirements_block=reqs_block,
        chunks_block=chunks_block,
        tone=preferences.get("tone", "professional"),
        truthfulness_note=preferences.get("truthfulness_note", "All content must be factual and grounded in provided source material."),
        language_style=preferences.get("language_style", "clear and specific"),
        section_order=section_order,
    )


# ---------------------------------------------------------------------------
# Cover letter generation
# ---------------------------------------------------------------------------

COVER_LETTER_GENERATION_PROMPT = """
You are an expert cover letter writer. Write a tailored cover letter for the role below.

Role: {job_title} at {company}
Key Requirements:
{requirements_block}

Story Anchor (the strongest relevant experience to highlight):
{anchor_content}

Additional Source Material (use only what is provided — do not invent):
{chunks_block}

Preferences:
- Tone: {tone}
- Paragraph count: {paragraph_count}
- Truthfulness: {truthfulness_note}

Instructions:
1. Write an engaging opening paragraph referencing the role and the story anchor.
2. Write {paragraph_count} body paragraph(s) that connect the user's background to the role requirements.
3. Write a closing paragraph expressing enthusiasm and a call to action.
4. Do not fabricate anything not present in the source material.

Return a JSON object with keys "opening", "body" (list of paragraphs), and "closing_paragraph".
""".strip()


def build_cover_letter_generation_prompt(
    job: JobDescription,
    requirements: Dict[str, List[str]],
    anchor: UserMaterialChunk,
    chunks: List[UserMaterialChunk],
    preferences: Dict,
) -> str:
    """Build the full prompt for cover letter content generation."""
    reqs_block = "\n".join(
        f"- [{cat}] {item}"
        for cat, items in requirements.items()
        for item in items
    ) or "(none extracted)"

    anchor_content = anchor.content if anchor else "(no anchor selected)"

    chunks_block = "\n\n".join(
        f"[{c.source_type}] {c.content}" for c in chunks
    ) or "(no additional source material)"

    return COVER_LETTER_GENERATION_PROMPT.format(
        job_title=job.title,
        company=job.company,
        requirements_block=reqs_block,
        anchor_content=anchor_content,
        chunks_block=chunks_block,
        tone=preferences.get("tone", "professional"),
        paragraph_count=preferences.get("cover_letter_body_paragraphs", 2),
        truthfulness_note=preferences.get("truthfulness_note", "All content must be factual."),
    )


# ---------------------------------------------------------------------------
# Fabrication check
# ---------------------------------------------------------------------------

FABRICATION_CHECK_PROMPT = """
You are a fact-checker for job application documents. Your job is to detect fabricated claims.

Source Material (ground truth — only these facts may appear in the document):
{source_block}

Generated Document Text:
{generated_text}

Identify any claims in the generated text that are NOT supported by the source material.
Return a JSON object:
  {{"is_valid": <bool>, "flagged_items": [<list of problematic strings or empty list>]}}

Return only valid JSON.
""".strip()


def build_fabrication_check_prompt(
    chunks: List[UserMaterialChunk],
    generated_text: str,
) -> str:
    """Build the prompt for validating that generated text contains no fabricated content."""
    source_block = "\n\n".join(
        f"[{c.source_type}] {c.content}" for c in chunks
    ) or "(no source material)"

    return FABRICATION_CHECK_PROMPT.format(
        source_block=source_block,
        generated_text=generated_text,
    )
