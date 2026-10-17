"""Request and response models for the /ask endpoint.
Pydantic enforces type safety at the API boundary - same pattern as Module 0.
"""
from __future__ import annotations
from typing import List

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    role: str = Field(
        "public",
        description=(
            "Who is asking - public/reporter/editor. Defaults to public, the "
            "least access, not the most. In a real system this comes from an "
            "authenticated session, never trusted as a raw client-supplied "
            "field the way this teaching demo simplifies it to."
        ),
    )


class SourceInfo(BaseModel):
    source: str
    chunk_id: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: str  # "high" or "low"
