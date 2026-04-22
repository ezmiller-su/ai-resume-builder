"""
Lightweight document styling helpers.

Keeps styling concerns separate from document assembly in doc_builder.
All functions accept a python-docx Document (or paragraph/run) object and
apply in-place mutations — they do not return new objects.

TODO: These are all stubs. Implement once python-docx is confirmed as a dependency.
"""

from typing import Any, Optional


def apply_heading_style(
    doc: Any,
    heading_text: str,
    level: int = 1,
) -> None:
    """
    Add a styled heading paragraph to a python-docx Document.

    Args:
        doc:          python-docx Document instance.
        heading_text: Text content of the heading.
        level:        Heading level (1 = section title, 2 = subsection).

    TODO: doc.add_heading(heading_text, level=level)
    TODO: Apply custom font size and color matching the user's preferred template.
    """
    # Placeholder
    print(f"[formatting] apply_heading_style: '{heading_text}' (level {level})")


def apply_body_style(
    doc: Any,
    text: str,
    is_bullet: bool = False,
) -> None:
    """
    Add a styled body paragraph or bullet point to a python-docx Document.

    Args:
        doc:       python-docx Document instance.
        text:      Paragraph or bullet text.
        is_bullet: If True, apply list-bullet style instead of normal body style.

    TODO: p = doc.add_paragraph(text, style="List Bullet" if is_bullet else "Normal")
    TODO: Apply font face and size from preferences.
    """
    prefix = "  •" if is_bullet else "   "
    print(f"[formatting] apply_body_style: {prefix} {text}")


def format_signature_block(
    doc: Any,
    closing_text: str,
    name: Optional[str] = None,
) -> None:
    """
    Add a cover letter signature block to a python-docx Document.

    Args:
        doc:          python-docx Document instance.
        closing_text: Sign-off text (e.g. "Sincerely,").
        name:         Signer's name; appended after the closing if provided.

    TODO: doc.add_paragraph(closing_text)
    TODO: Add spacing for a physical signature gap if printing is expected.
    TODO: doc.add_paragraph(name or "")
    """
    print(f"[formatting] format_signature_block: {closing_text}")
    if name:
        print(f"[formatting]   {name}")


def apply_section_spacing(doc: Any, space_after_pt: int = 6) -> None:
    """
    Apply consistent vertical spacing after the last paragraph in a section.

    Args:
        doc:            python-docx Document instance.
        space_after_pt: Points of space to add after the last paragraph (default 6pt).

    TODO: para = doc.paragraphs[-1]
    TODO: para.paragraph_format.space_after = Pt(space_after_pt)
    """
    print(f"[formatting] apply_section_spacing: {space_after_pt}pt after section")
