"""Request and response models for the /search and /ask endpoints.
Pydantic enforces type safety at the API boundary - same pattern as Module 0.

SearchRequest/SearchResult/SearchResponse carried forward from Week 2's /search
endpoint. AskRequest/SourceInfo/AskResponse are new this week, for /ask.
"""
from __future__ import annotations
from typing import List

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    k: int = Field(default=3, ge=1, le=20)


class SearchResult(BaseModel):
    score: float
    source: str
    section: str
    text: str


class SearchResponse(BaseModel):
    results: List[SearchResult]


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class SourceInfo(BaseModel):
    source: str
    chunk_id: str


class AskResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    confidence: str  # "high" or "low"
