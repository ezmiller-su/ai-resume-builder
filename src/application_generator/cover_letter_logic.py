"""
Cover-letter-specific generation logic.

Pipeline position:
  shared_logic.select_relevant_content()  -->  [this module]  -->  GeneratedDocument

Input contract:
  - selected_chunks: List[UserMaterialChunk] from shared_logic
  - job:             JobDescription
  - preferences:     merged preference dict from preferences.merge_preferences()

Output contract:
  - GeneratedDocument with document_type="cover_letter" and narrative paragraphs
    ready for doc_builder.build_cover_letter_docx()
"""

from typing import Dict, List, Optional

from .models.generated_document import DocumentSection, GeneratedDocument
from .models.job_description import JobDescription
from .models.user_materials import UserMaterialChunk


def choose_story_anchor(
    selected_chunks: List[UserMaterialChunk],
    job: JobDescription,
    preferences: Dict,
) -> Optional[UserMaterialChunk]:
    """
    Identify the single strongest user material chunk to anchor the cover letter narrative.

    A story anchor is the most compelling experience, project, or achievement that
    directly addresses the role's core requirement and gives the letter a concrete hook.

    Args:
        selected_chunks: Relevant chunks from shared_logic.select_relevant_content().
        job:             Parsed job description.
        preferences:     May contain hints like preferred_story_type or highlight_project.

    Returns:
        The best UserMaterialChunk to open or anchor the letter, or None if chunks
        are empty.

    TODO: Use prompts.STORY_ANCHOR_PROMPT with an LLM call to score each chunk
          on relevance, specificity, and narrative potential.
    TODO: Fall back to highest retrieval_score chunk if LLM call is unavailable.
    """
    if not selected_chunks:
        return None
    # Placeholder: use the first (highest-ranked) chunk as the anchor
    return selected_chunks[0]


def build_cover_letter_paragraphs(
    anchor: Optional[UserMaterialChunk],
    selected_chunks: List[UserMaterialChunk],
    job: JobDescription,
    preferences: Dict,
) -> List[DocumentSection]:
    """
    Build the paragraph structure for the cover letter body.

    Standard three-paragraph structure:
      1. Opening  — who you are, role you're applying for, story anchor hook
      2. Body     — 1-2 paragraphs expanding on relevant experience/projects
      3. Closing  — enthusiasm, call to action

    Args:
        anchor:          The story anchor chunk from choose_story_anchor().
        selected_chunks: All relevant chunks for body content.
        job:             Parsed job description for company/role references.
        preferences:     Tone and structure preferences.

    Returns:
        List of DocumentSection objects representing each paragraph group.

    TODO: Use prompts.COVER_LETTER_GENERATION_PROMPT injected with anchor content,
          selected_chunks, job.company, and job.title.
    TODO: Allow preferences["paragraph_count"] to expand or contract body length.
    """
    return [
        DocumentSection(
            heading="Opening",
            lines=["[TODO: generate opening paragraph via LLM]"],
        ),
        DocumentSection(
            heading="Body",
            lines=["[TODO: generate body paragraph(s) via LLM]"],
        ),
        DocumentSection(
            heading="Closing Paragraph",
            lines=["[TODO: generate closing paragraph via LLM]"],
        ),
    ]


def generate_cover_letter_content(
    selected_chunks: List[UserMaterialChunk],
    job: JobDescription,
    preferences: Dict,
) -> GeneratedDocument:
    """
    Orchestrate the full cover letter generation step for one job application.

    This is the primary entry point for cover_letter_logic called by
    service.generate_cover_letter().

    Args:
        selected_chunks: Relevant user material chunks.
        job:             Parsed job description.
        preferences:     Merged user + session preferences.

    Returns:
        GeneratedDocument ready for doc_builder.build_cover_letter_docx().

    TODO: Call shared_logic.validate_no_fabrication() on generated paragraphs
          before returning.
    TODO: Build signature block from user header info in preferences or user profile.
    """
    anchor = choose_story_anchor(selected_chunks, job, preferences)
    sections = build_cover_letter_paragraphs(anchor, selected_chunks, job, preferences)

    return GeneratedDocument(
        document_type="cover_letter",
        header={
            "name": "[TODO: pull from user profile or preferences]",
            "email": "",
            "phone": "",
            "date": "[TODO: today's date]",
            "recipient_name": "",
            "recipient_title": "",
            "company": job.company,
        },
        sections=sections,
        closing="Sincerely,\n[TODO: user name]",
        job_title=job.title,
        company=job.company,
    )
