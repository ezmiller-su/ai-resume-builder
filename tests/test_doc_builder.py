"""
Placeholder tests for doc_builder.py.
"""

from src.application_generator.doc_builder import build_cv_docx, build_cover_letter_docx, build_docx
from src.application_generator.models.generated_document import DocumentSection, GeneratedDocument


def _make_cv_doc():
    return GeneratedDocument(
        document_type="cv",
        header={"name": "Jane Doe", "email": "jane@example.com"},
        sections=[DocumentSection(heading="Experience", lines=["Worked at Acme."])],
        job_title="Engineer",
        company="Acme",
    )


def _make_cl_doc():
    return GeneratedDocument(
        document_type="cover_letter",
        header={"name": "Jane Doe"},
        sections=[
            DocumentSection(heading="Opening", lines=["I am excited to apply."]),
            DocumentSection(heading="Body", lines=["I have relevant experience."]),
            DocumentSection(heading="Closing Paragraph", lines=["Thank you for your consideration."]),
        ],
        closing="Sincerely,\nJane Doe",
        job_title="Engineer",
        company="Acme",
    )


def test_build_docx_dispatches_cv(capsys):
    result = build_docx(_make_cv_doc(), output_path="test_cv.docx")
    assert result == "test_cv.docx"


def test_build_docx_dispatches_cover_letter(capsys):
    result = build_docx(_make_cl_doc(), output_path="test_cl.docx")
    assert result == "test_cl.docx"


def test_build_docx_raises_on_unknown_type():
    doc = GeneratedDocument(document_type="memo")
    try:
        build_docx(doc)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_build_cv_docx_returns_path():
    path = build_cv_docx(_make_cv_doc(), output_path="out.docx")
    assert path == "out.docx"


def test_build_cover_letter_docx_returns_path():
    path = build_cover_letter_docx(_make_cl_doc(), output_path="out.docx")
    assert path == "out.docx"
