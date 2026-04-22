"""
Dataclasses for structured user source materials.

These are populated by the retrieval teammate's ChromaDB pipeline and passed into
shared_logic.rank_user_materials() and select_relevant_content().

The retrieval teammate should produce a list of UserMaterialChunk objects (or the
broader UserMaterials container) ranked/filtered by relevance to the job description.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Experience:
    """A single professional or volunteer experience entry."""

    title: str = ""
    organization: str = ""
    start_date: str = ""
    end_date: str = ""          # "Present" is fine
    description: List[str] = field(default_factory=list)   # bullet points


@dataclass
class Project:
    """A portfolio or academic project entry."""

    name: str = ""
    description: str = ""
    technologies: List[str] = field(default_factory=list)
    outcome: str = ""


@dataclass
class Coursework:
    """Relevant coursework or academic credential."""

    course_name: str = ""
    institution: str = ""
    year: str = ""
    description: str = ""


@dataclass
class PriorDocument:
    """A previously written resume or cover letter used as source material."""

    document_type: str = ""     # "resume" | "cover_letter"
    raw_text: str = ""
    source_label: str = ""      # e.g. "Resume_2024_SWE.pdf"


@dataclass
class UserMaterialChunk:
    """
    A single retrieved chunk of user content as returned by the retrieval module.

    The retrieval teammate populates retrieval_score from ChromaDB similarity search.
    source_type indicates which category this chunk came from so generation modules
    can apply type-specific formatting rules.
    """

    content: str = ""
    source_type: str = ""           # "experience" | "project" | "coursework" | "prior_resume" | "prior_cover_letter"
    source_label: str = ""          # human-readable provenance
    retrieval_score: Optional[float] = None  # cosine similarity or equivalent; None if not yet ranked

    # TODO: add chunk_id if retrieval teammate assigns stable IDs to chunks


@dataclass
class UserMaterials:
    """
    Container for all user source content fed into the generation pipeline.

    The retrieval teammate may populate ranked_chunks directly from ChromaDB results.
    The structured fields (experiences, projects, etc.) are optional richer forms
    that generation logic can use when available.
    """

    # Raw retrieved chunks from ChromaDB (primary interface with retrieval teammate)
    ranked_chunks: List[UserMaterialChunk] = field(default_factory=list)

    # Optionally structured entries (may be populated by UI or a future parser)
    experiences: List[Experience] = field(default_factory=list)
    projects: List[Project] = field(default_factory=list)
    coursework: List[Coursework] = field(default_factory=list)
    prior_documents: List[PriorDocument] = field(default_factory=list)

    # TODO: add skills, certifications, education as structured fields when needed
