"""
Dataclass for structured generated output before rendering to .docx.

This intermediate representation is produced by cv_logic or cover_letter_logic
and consumed by doc_builder to produce the final file.
Keeping this model document-type-aware means doc_builder can dispatch correctly
without needing to inspect raw content.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DocumentSection:
    """A named section containing one or more content lines."""

    heading: str = ""
    lines: List[str] = field(default_factory=list)  # bullet points, sentences, or paragraphs


@dataclass
class GeneratedDocument:
    """
    Structured output from the generation pipeline.

    document_type drives doc_builder dispatch:
      "cv"           -> build_cv_docx()
      "cover_letter" -> build_cover_letter_docx()

    For a CV/resume:
      - sections holds named sections (Summary, Experience, Education, Skills, etc.)
      - closing is typically empty

    For a cover letter:
      - sections holds body paragraphs (Opening, Body, Closing Paragraph)
      - closing holds the sign-off block
    """

    document_type: str = ""             # "cv" | "cover_letter"
    header: Dict[str, str] = field(default_factory=dict)    # name, email, phone, linkedin, etc.
    sections: List[DocumentSection] = field(default_factory=list)
    closing: str = ""                   # signature block for cover letters; empty for CV

    # Metadata for traceability and UI display
    job_title: str = ""
    company: str = ""
    generated_at: Optional[str] = None  # ISO timestamp; set at generation time

    # TODO: add version/run_id for multi-draft comparison
    # TODO: add user_id to associate with saved preferences
