"""
application_generator — AI-powered job application document generation module.

Public surface:
  from application_generator.service import generate_cv, generate_cover_letter, generate_application_document
  from application_generator.models import JobDescription, UserMaterials, GeneratedDocument
"""

from .models import (
    GeneratedDocument,
    JobDescription,
    UserMaterials,
)
from .service import (
    generate_application_document,
    generate_cover_letter,
    generate_cv,
)

__all__ = [
    "JobDescription",
    "UserMaterials",
    "GeneratedDocument",
    "generate_application_document",
    "generate_cv",
    "generate_cover_letter",
]
