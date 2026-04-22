"""
Dataclass representing a parsed job description.

Populated upstream by the job description parsing step (UI or a dedicated parser).
This model is passed into shared_logic and downstream generation modules.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class JobDescription:
    """Structured representation of a job posting."""

    raw_text: str = ""
    title: str = ""
    company: str = ""
    responsibilities: List[str] = field(default_factory=list)
    qualifications: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    # TODO: add location, employment_type, salary_range if needed later
    # TODO: consider adding a parsed_at timestamp for caching/versioning
