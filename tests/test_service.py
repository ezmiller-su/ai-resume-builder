"""
Placeholder tests for service.py orchestration layer.

These verify that the pipeline is importable and callable end-to-end with stub data.
Replace placeholder assertions with real business logic as functions are implemented.
"""

import pytest

from src.application_generator.models.job_description import JobDescription
from src.application_generator.models.user_materials import UserMaterialChunk, UserMaterials
from src.application_generator.service import (
    generate_application_document,
    generate_cover_letter,
    generate_cv,
)


@pytest.fixture
def sample_job():
    return JobDescription(
        raw_text="We need a software engineer.",
        title="Software Engineer",
        company="Acme Corp",
        responsibilities=["Write code", "Review PRs"],
        qualifications=["Python", "Git"],
        keywords=["Python", "backend"],
    )


@pytest.fixture
def sample_materials():
    return UserMaterials(
        ranked_chunks=[
            UserMaterialChunk(
                content="Built a REST API using Python and FastAPI.",
                source_type="project",
                source_label="FastAPI project",
                retrieval_score=0.92,
            )
        ]
    )


def test_generate_cv_returns_generated_document(sample_job, sample_materials):
    doc = generate_cv(sample_job, sample_materials)
    assert doc.document_type == "cv"
    assert doc.company == "Acme Corp"
    assert len(doc.sections) > 0


def test_generate_cover_letter_returns_generated_document(sample_job, sample_materials):
    doc = generate_cover_letter(sample_job, sample_materials)
    assert doc.document_type == "cover_letter"
    assert doc.company == "Acme Corp"
    assert len(doc.sections) > 0


def test_generate_application_document_dispatches_correctly(sample_job, sample_materials):
    cv_doc = generate_application_document("cv", sample_job, sample_materials)
    assert cv_doc.document_type == "cv"

    cl_doc = generate_application_document("cover_letter", sample_job, sample_materials)
    assert cl_doc.document_type == "cover_letter"


def test_generate_application_document_raises_on_unknown_type(sample_job, sample_materials):
    with pytest.raises(ValueError):
        generate_application_document("memo", sample_job, sample_materials)
