"""
Placeholder tests for cover_letter_logic.py.
"""

from src.application_generator.cover_letter_logic import (
    build_cover_letter_paragraphs,
    choose_story_anchor,
    generate_cover_letter_content,
)
from src.application_generator.models.job_description import JobDescription
from src.application_generator.models.user_materials import UserMaterialChunk


def _make_job():
    return JobDescription(title="Product Manager", company="PM Inc")


def _make_chunks():
    return [
        UserMaterialChunk(content="Led a cross-functional team to ship a new feature.", source_type="experience"),
        UserMaterialChunk(content="Conducted user research resulting in 20% retention improvement.", source_type="project"),
    ]


def test_choose_story_anchor_returns_first_chunk():
    chunks = _make_chunks()
    anchor = choose_story_anchor(chunks, _make_job(), preferences={})
    assert anchor is not None
    assert anchor.content == chunks[0].content


def test_choose_story_anchor_empty_returns_none():
    anchor = choose_story_anchor([], _make_job(), preferences={})
    assert anchor is None


def test_build_cover_letter_paragraphs_returns_list():
    chunks = _make_chunks()
    anchor = chunks[0]
    sections = build_cover_letter_paragraphs(anchor, chunks, _make_job(), preferences={})
    assert isinstance(sections, list)
    assert len(sections) >= 3  # opening, body, closing paragraph


def test_generate_cover_letter_content_document_type():
    doc = generate_cover_letter_content(_make_chunks(), _make_job(), preferences={})
    assert doc.document_type == "cover_letter"


def test_generate_cover_letter_content_company():
    doc = generate_cover_letter_content(_make_chunks(), _make_job(), preferences={})
    assert doc.company == "PM Inc"


def test_generate_cover_letter_content_has_closing():
    doc = generate_cover_letter_content(_make_chunks(), _make_job(), preferences={})
    assert isinstance(doc.closing, str)
