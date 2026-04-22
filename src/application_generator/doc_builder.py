"""
Build .docx documents from structured GeneratedDocument output.

Requires python-docx:
  pip install python-docx

TODO: Add python-docx to requirements.txt once the team confirms the dependency.
      Until then all functions are stubs that raise NotImplementedError or log a warning.

NOTE: python-docx is only imported inside the build functions so that the rest of
the module (models, logic, preferences) can be imported and tested without it installed.
"""

from typing import Optional

from .formatting import (
    apply_body_style,
    apply_heading_style,
    apply_section_spacing,
    format_signature_block,
)
from .models.generated_document import GeneratedDocument


def build_docx(
    document: GeneratedDocument,
    output_path: Optional[str] = None,
) -> Optional[str]:
    """
    Dispatch to the correct .docx builder based on document.document_type.

    Args:
        document:    Structured generated document from cv_logic or cover_letter_logic.
        output_path: File path for the .docx output. If None, a default name is chosen.

    Returns:
        The path to the written .docx file, or None if writing was skipped.

    Raises:
        ValueError: if document.document_type is not recognized.
    """
    if document.document_type == "cv":
        return build_cv_docx(document, output_path=output_path)
    elif document.document_type == "cover_letter":
        return build_cover_letter_docx(document, output_path=output_path)
    else:
        raise ValueError(f"Unknown document_type: {document.document_type!r}")


def build_cv_docx(
    document: GeneratedDocument,
    output_path: Optional[str] = None,
) -> Optional[str]:
    """
    Render a CV/resume GeneratedDocument to a .docx file.

    Args:
        document:    GeneratedDocument with document_type="cv".
        output_path: Destination path. Defaults to "output_cv.docx" if not provided.

    Returns:
        Path to the written .docx file.

    TODO: Implement using python-docx:
          from docx import Document
          doc = Document()
          # Write header (name, contact info)
          # For each section in document.sections:
          #   apply_heading_style(doc, section.heading)
          #   For each line: apply_body_style(doc, line)
          #   apply_section_spacing(doc)
          # doc.save(output_path)
    TODO: Support a Word template (.dotx) file for brand-consistent styling.
    TODO: Add page margin configuration via preferences.
    """
    path = output_path or "output_cv.docx"
    # Placeholder: log intent rather than raise so the pipeline stays testable
    print(f"[doc_builder] build_cv_docx: would write CV to {path}")
    print(f"  Sections: {[s.heading for s in document.sections]}")
    return path


def build_cover_letter_docx(
    document: GeneratedDocument,
    output_path: Optional[str] = None,
) -> Optional[str]:
    """
    Render a cover letter GeneratedDocument to a .docx file.

    Args:
        document:    GeneratedDocument with document_type="cover_letter".
        output_path: Destination path. Defaults to "output_cover_letter.docx".

    Returns:
        Path to the written .docx file.

    TODO: Implement using python-docx:
          from docx import Document
          doc = Document()
          # Write header block (applicant name, date, recipient)
          # For each section (opening, body paragraphs, closing paragraph):
          #   apply_body_style(doc, paragraph_text)
          #   apply_section_spacing(doc)
          # Write signature block: format_signature_block(doc, document.closing)
          # doc.save(output_path)
    TODO: Support letterhead/logo insertion via preferences.
    """
    path = output_path or "output_cover_letter.docx"
    print(f"[doc_builder] build_cover_letter_docx: would write cover letter to {path}")
    print(f"  Sections: {[s.heading for s in document.sections]}")
    return path
