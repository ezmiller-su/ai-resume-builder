# application_generator — Module Notes

## What this module owns

This module is responsible for everything between **retrieved user materials** and **rendered .docx output**:

- Extracting and categorizing job requirements from a parsed job description
- Ranking and selecting the most relevant user material chunks
- Generating structured CV/resume content (core milestone deliverable)
- Generating structured cover letter content (extended scope)
- Building .docx files from structured output
- Loading, saving, and merging user generation preferences

It does **not** own:
- Streamlit UI (handled by UI teammate)
- Chunking, embedding, ChromaDB storage, or retrieval (handled by retrieval teammate)
- Job description parsing from raw HTML/PDF (currently assumed to be done upstream or in the UI)

---

## How it connects to other modules

```
[Streamlit UI]
    |
    | JobDescription (parsed job posting)
    | UserMaterials  (ranked chunks from ChromaDB)
    |
    v
[service.py]  <-- primary interface for teammates
    |
    |-- shared_logic.py  (extract requirements, rank/select content)
    |       |
    |       v
    |-- cv_logic.py            (CV/resume generation)
    |-- cover_letter_logic.py  (cover letter generation)
    |
    v
[doc_builder.py]  --> .docx output file
    |
[formatting.py]   (styling helpers, called by doc_builder)
```

**Retrieval teammate interface:**
The retrieval teammate should produce a `UserMaterials` object with `ranked_chunks` populated from ChromaDB similarity search. Each chunk should carry:
- `content` (str): the text chunk
- `source_type` (str): one of `"experience"`, `"project"`, `"coursework"`, `"prior_resume"`, `"prior_cover_letter"`
- `retrieval_score` (float): cosine similarity or equivalent

**Streamlit UI teammate interface:**
Call `service.generate_cv()` or `service.generate_cover_letter()` with a `JobDescription` and `UserMaterials`. Optionally pass `session_overrides` for runtime preference tweaks from UI sliders/selectors. Set `build_file=True` and `output_path=...` to get a `.docx` back.

---

## What is implemented vs placeholder

| File | Status |
|---|---|
| `models/` (all three dataclasses) | Complete skeleton — fields defined, importable |
| `shared_logic.py` | Skeleton — functions callable but no LLM logic yet |
| `cv_logic.py` | Skeleton — pipeline shape complete, LLM calls TODO |
| `cover_letter_logic.py` | Skeleton — pipeline shape complete, LLM calls TODO |
| `preferences.py` | Functional — load/save/merge works with real JSON files |
| `prompts.py` | Complete prompt templates — ready to wire to LLM client |
| `service.py` | Functional orchestration — dispatches correctly, end-to-end callable |
| `doc_builder.py` | Stub — prints intent; needs python-docx implementation |
| `formatting.py` | Stub — prints intent; needs python-docx implementation |

---

## How preferences are stored

Preferences are stored as **structured JSON files**, not vector memory.

- `data/preferences/default_preferences.json` — shipped defaults, committed to repo
- `data/preferences/<user_id>.json` — per-user overrides, created on first save

Merge order (lowest to highest priority):
```
defaults < per-user file < session overrides (from UI)
```

The `preferences.get_preferences(user_id, session_overrides)` function handles loading and merging in one call.

---

## How shared logic differs from CV and cover letter logic

**`shared_logic.py`** handles steps that are identical regardless of document type:
1. `extract_job_requirements` — parse responsibilities, qualifications, keywords from a job posting
2. `rank_user_materials` — confirm or refine chunk ordering against job requirements
3. `select_relevant_content` — trim to the top N chunks for the LLM prompt
4. `validate_no_fabrication` — post-generation truthfulness check

**`cv_logic.py`** uses the selected chunks to:
- Group content by type into named resume sections (Experience, Projects, Education, Skills, etc.)
- Apply action-verb and bullet-point formatting conventions
- Produce a `GeneratedDocument` with `document_type="cv"`

**`cover_letter_logic.py`** uses the selected chunks to:
- Choose a "story anchor" (the most compelling single experience to highlight)
- Build a narrative paragraph structure (opening, body, closing paragraph)
- Produce a `GeneratedDocument` with `document_type="cover_letter"` and a signature block

---

## Dependency notes

- **python-docx**: Required by `doc_builder.py` for `.docx` rendering. Not yet installed — add `python-docx` to `requirements.txt` when the team confirms.
- **LLM client**: `shared_logic`, `cv_logic`, `cover_letter_logic` will all need an LLM client (e.g. Anthropic SDK or OpenAI). Wire this in via a shared client module or inject through service.py. Prompt templates are ready in `prompts.py`.
- **pytest**: Required for running tests. Add to dev dependencies.

---

## Next steps for milestone completion

1. Wire an LLM client into `shared_logic.extract_job_requirements()` using `prompts.build_job_requirements_prompt()`
2. Implement `cv_logic.generate_cv_content()` — call LLM with `prompts.build_cv_generation_prompt()`, parse JSON response into `DocumentSection` objects
3. Implement `cover_letter_logic.generate_cover_letter_content()` — call LLM with `prompts.build_cover_letter_generation_prompt()`
4. Implement `shared_logic.validate_no_fabrication()` using `prompts.build_fabrication_check_prompt()`
5. Install python-docx and implement `doc_builder.build_cv_docx()` and `build_cover_letter_docx()`
6. Add `requirements.txt` with `python-docx`, `pytest`, and the LLM SDK
7. Expand tests from placeholder assertions to real output validation
8. Coordinate with retrieval teammate on the exact shape of `UserMaterials.ranked_chunks` to finalize the interface contract
