"""
Placeholder tests for cv_logic.py.
"""

from src.application_generator.cv_logic import build_cv_sections, generate_cv_content
from src.application_generator.models.job_description import JobDescription
from src.application_generator.models.user_materials import UserMaterialChunk


def _make_job():
    return JobDescription(title="Data Engineer", company="DataCo")


def _make_chunks():
    return [
        UserMaterialChunk(content="Built ETL pipelines in Python.", source_type="experience"),
        UserMaterialChunk(content="Used Apache Spark for large-scale data processing.", source_type="project"),
    ]


def test_build_cv_sections_returns_list(_make_job=_make_job, _make_chunks=_make_chunks):
    sections = build_cv_sections(_make_chunks(), _make_job(), preferences={})
    assert isinstance(sections, list)
    assert len(sections) > 0


def test_generate_cv_content_document_type():
    doc = generate_cv_content(_make_chunks(), _make_job(), preferences={})
    assert doc.document_type == "cv"


def test_generate_cv_content_has_sections():
    doc = generate_cv_content(_make_chunks(), _make_job(), preferences={})
    assert isinstance(doc.sections, list)


def test_generate_cv_content_company():
    doc = generate_cv_content(_make_chunks(), _make_job(), preferences={})
    assert doc.company == "DataCo"
