"""
Orchestration layer for the application document generation pipeline.

This is the primary interface for teammates to call:
  - Streamlit UI teammate calls generate_application_document() or the specific variants.
  - Retrieval teammate's output (UserMaterials) feeds directly into these functions.

Pipeline:
  load preferences
    -> extract_job_requirements (shared_logic)
    -> rank_user_materials      (shared_logic)
    -> select_relevant_content  (shared_logic)
    -> generate_cv_content      (cv_logic)       [if document_type == "cv"]
    -> generate_cover_letter_content (cover_letter_logic) [if document_type == "cover_letter"]
    -> build_docx               (doc_builder)    [optional; returns GeneratedDocument if skipped]
"""

from typing import Dict, Literal, Optional

from . import cover_letter_logic, cv_logic, doc_builder, shared_logic
from .models.generated_document import GeneratedDocument
from .models.job_description import JobDescription
from .models.user_materials import UserMaterials
from .preferences import get_preferences

DocumentType = Literal["cv", "cover_letter"]


def generate_application_document(
    document_type: DocumentType,
    job: JobDescription,
    materials: UserMaterials,
    user_id: Optional[str] = None,
    session_overrides: Optional[Dict] = None,
    build_file: bool = False,
    output_path: Optional[str] = None,
) -> GeneratedDocument:
    """
    Top-level entry point: generate either a CV or cover letter for a job application.

    Args:
        document_type:     "cv" or "cover_letter"
        job:               Parsed job description (from UI or job description parser).
        materials:         Retrieved user materials from the retrieval teammate's pipeline.
        user_id:           Optional user identifier for loading saved preferences.
        session_overrides: Optional per-request preference overrides from the UI.
        build_file:        If True, also call doc_builder to produce a .docx file.
        output_path:       Path for the .docx output; required when build_file=True.

    Returns:
        GeneratedDocument containing structured output ready for rendering.

    Raises:
        ValueError: if document_type is not "cv" or "cover_letter".

    TODO: Add retry logic around LLM calls when shared_logic and generation modules
          are fully implemented.
    TODO: Consider returning both the GeneratedDocument and a path to the .docx
          when build_file=True, so the UI can offer both a preview and download.
    """
    prefs = get_preferences(user_id=user_id, session_overrides=session_overrides)

    requirements = shared_logic.extract_job_requirements(job)
    ranked_materials = shared_logic.rank_user_materials(materials, job)
    selected_chunks = shared_logic.select_relevant_content(ranked_materials, requirements)

    if document_type == "cv":
        doc = cv_logic.generate_cv_content(selected_chunks, job, prefs)
    elif document_type == "cover_letter":
        doc = cover_letter_logic.generate_cover_letter_content(selected_chunks, job, prefs)
    else:
        raise ValueError(f"Unknown document_type: {document_type!r}. Must be 'cv' or 'cover_letter'.")

    if build_file:
        doc_builder.build_docx(doc, output_path=output_path)

    return doc


def generate_cv(
    job: JobDescription,
    materials: UserMaterials,
    user_id: Optional[str] = None,
    session_overrides: Optional[Dict] = None,
    build_file: bool = False,
    output_path: Optional[str] = None,
) -> GeneratedDocument:
    """
    Convenience wrapper: generate a CV/resume only.

    Args:
        job:               Parsed job description.
        materials:         Retrieved user materials.
        user_id:           Optional user identifier.
        session_overrides: Optional per-request UI overrides.
        build_file:        If True, write a .docx file to output_path.
        output_path:       Output path for the .docx file.

    Returns:
        GeneratedDocument with document_type="cv".
    """
    return generate_application_document(
        document_type="cv",
        job=job,
        materials=materials,
        user_id=user_id,
        session_overrides=session_overrides,
        build_file=build_file,
        output_path=output_path,
    )


def generate_cover_letter(
    job: JobDescription,
    materials: UserMaterials,
    user_id: Optional[str] = None,
    session_overrides: Optional[Dict] = None,
    build_file: bool = False,
    output_path: Optional[str] = None,
) -> GeneratedDocument:
    """
    Convenience wrapper: generate a cover letter only.

    Args:
        job:               Parsed job description.
        materials:         Retrieved user materials.
        user_id:           Optional user identifier.
        session_overrides: Optional per-request UI overrides.
        build_file:        If True, write a .docx file to output_path.
        output_path:       Output path for the .docx file.

    Returns:
        GeneratedDocument with document_type="cover_letter".
    """
    return generate_application_document(
        document_type="cover_letter",
        job=job,
        materials=materials,
        user_id=user_id,
        session_overrides=session_overrides,
        build_file=build_file,
        output_path=output_path,
    )
