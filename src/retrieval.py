# Rag Pipeline - Dax Nguyen

import hashlib
import json
import os
import streamlit as st
import chromadb
from openai import OpenAI

from src.application_generator.models.user_materials import (
    UserMaterialChunk,
    UserMaterials
)

CHROMA_DIR = "data/chroma"
EMBED_MODEL = "text-embedding-3-small"
RERANK_MODEL = "gpt-4.1-nano"
CANDIDATES = 30   # stage 1 fetch size


def _client():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_DIR)


def _openai():
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


def _coll(user_id):
    return _client().get_or_create_collection(name=f"user_{user_id}")


def _embed(texts):
    resp = _openai().embeddings.create(model=EMBED_MODEL, input=texts)
    return [d.embedding for d in resp.data]


def _split(text):
    """Blank-line paragraphs. Crude but fine for v1."""
    return [p.strip() for p in text.split("\n\n") if p.strip()]


def _chunk_id(user_id, source_label, content):
    h = hashlib.sha1(f"{source_label}|{content}".encode()).hexdigest()[:12]
    return f"{user_id}:{h}"


def ingest(user_id, text, source_type, source_label):
    """Split → embed → upsert into the user's collection. Returns chunks added."""
    chunks = _split(text)
    if not chunks:
        return 0
    coll = _coll(user_id)
    coll.upsert(
        ids        = [_chunk_id(user_id, source_label, c) for c in chunks],
        documents  = chunks,
        embeddings = _embed(chunks),
        metadatas  = [
            {"source_type": source_type, "source_label": source_label, "chunk_index": i}
            for i, _ in enumerate(chunks)
        ],
    )
    return len(chunks)


def clear(user_id):
    try:
        _client().delete_collection(name=f"user_{user_id}")
    except Exception:
        pass


def _rerank_with_llm(query, candidates, n):
    """Ask the LLM to score each candidate 0–10 against the query, return top N."""
    numbered = "\n\n".join(
        f"[{i}] {c['document']}" for i, c in enumerate(candidates)
    )
    prompt = (
        f"Query (job description):\n{query}\n\n"
        f"Candidate chunks:\n{numbered}\n\n"
        f"Score each chunk 0–10 for how relevant it is to this job. "
        f"Return only a JSON list of {{\"index\": int, \"score\": float}} objects, "
        f"one per candidate, no commentary."
    )
    try:
        resp = _openai().chat.completions.create(
            model=RERANK_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )
        scored = json.loads(resp.choices[0].message.content)
        scored.sort(key=lambda x: x["score"], reverse=True)
        return [(candidates[s["index"]], s["score"] / 10.0) for s in scored[:n]]
    except Exception:
        # Fallback: keep stage-1 cosine ordering
        return [(c, c["sim"]) for c in candidates[:n]]


def _query_text(job):
    parts = [job.title, job.company,
             *job.responsibilities, *job.qualifications, *job.keywords]
    joined = "\n".join(p for p in parts if p)
    return joined or job.raw_text


def retrieve_for_job(user_id, job, n=10):
    coll = _coll(user_id)
    if coll.count() == 0:
        return UserMaterials()

    q_emb = _embed([_query_text(job)])[0]
    raw = coll.query(query_embeddings=[q_emb], n_results=CANDIDATES)

    # Flatten Chroma's nested-list shape into one dict per candidate
    candidates = [
        {"document": d, "metadata": m, "sim": 1.0 - dist}
        for d, m, dist in zip(
            raw["documents"][0], raw["metadatas"][0], raw["distances"][0]
        )
    ]

    reranked = _rerank_with_llm(_query_text(job), candidates, n)

    chunks = [
        UserMaterialChunk(
            content=c["document"],
            source_type=c["metadata"].get("source_type", ""),
            source_label=c["metadata"].get("source_label", ""),
            retrieval_score=score,
        )
        for c, score in reranked
    ]
    return UserMaterials(ranked_chunks=chunks)