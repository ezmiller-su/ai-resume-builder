"""
CV / resume-specific generation logic.

This module is the core deliverable for the CV Generator Bot milestone.

Pipeline position:
  shared_logic.select_relevant_content()  -->  [this module]  -->  GeneratedDocument

Input contract:
  - selected_chunks: List[UserMaterialChunk] from shared_logic
  - job:             JobDescription
  - preferences:     merged preference dict from preferences.merge_preferences()

Output contract:
  - GeneratedDocument with document_type="cv" and structured sections
    ready for doc_builder.build_cv_docx()
"""

from typing import Dict, List

from .models.generated_document import DocumentSection, GeneratedDocument
from .models.job_description import JobDescription
from .models.user_materials import UserMaterialChunk


# Standard CV section order; can be overridden via preferences
DEFAULT_CV_SECTIONS = [
    "Summary",
    "Experience",
    "Projects",
    "Education",
    "Skills",
    "Coursework",
]


def build_cv_sections(
    selected_chunks: List[UserMaterialChunk],
    job: JobDescription,
    preferences: Dict,
) -> List[DocumentSection]:
    """
    Assemble raw document sections from selected user material chunks.

    Groups chunks by source_type into named sections and produces a list of
    DocumentSection objects that preserve the standard CV structure.

    Args:
        selected_chunks: Relevant chunks returned by shared_logic.select_relevant_content().
        job:             Parsed job description for context-aware section ordering.
        preferences:     Merged user preferences (tone, section order, etc.).

    Returns:
        List of DocumentSection objects in presentation order.

    TODO: Group chunks by source_type ("experience", "project", "coursework", etc.)
          and map each group to the corresponding CV section heading.
    TODO: Apply preferences["section_order"] if present to reorder sections.
    TODO: Apply preferences["max_bullets_per_section"] to trim long entries.
    """
    # Placeholder: return a single stub section so the pipeline is callable end-to-end
    return [
        DocumentSection(
            heading="Experience",
            lines=["[TODO: populate from selected_chunks via LLM call]"],
        )
    ]


def generate_cv_content(
    selected_chunks: List[UserMaterialChunk],
    job: JobDescription,
    preferences: Dict,
) -> GeneratedDocument:
    """
    Orchestrate the full CV generation step for one job application.

    This is the primary entry point for cv_logic called by service.generate_cv().

    Args:
        selected_chunks: Relevant user material chunks.
        job:             Parsed job description.
        preferences:     Merged user + session preferences.

    Returns:
        GeneratedDocument ready for doc_builder.build_cv_docx().

    TODO: Build the LLM prompt using prompts.CV_GENERATION_PROMPT, injecting
          selected_chunks and job requirements.
    TODO: Parse the LLM response into structured DocumentSection objects.
    TODO: Call shared_logic.validate_no_fabrication() on the generated text
          before returning; raise or warn if validation fails.
    """
    sections = build_cv_sections(selected_chunks, job, preferences)

    return GeneratedDocument(
        document_type="cv",
        header={
            "name": "[TODO: pull from user profile or preferences]",
            "email": "",
            "phone": "",
            "linkedin": "",
        },
        sections=sections,
        closing="",
        job_title=job.title,
        company=job.company,
    )
