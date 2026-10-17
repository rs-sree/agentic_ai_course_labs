"""LLM-as-judge: score whether an answer is actually faithful to the sources
it was given, not just whether it looks plausible. A second, independent
model call, reading the answer and the sources together - the same "read it
yourself, don't just trust the citation number" discipline from Week 4,
now automated instead of done by hand.
"""
from __future__ import annotations
import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")

JUDGE_PROMPT = """You are a strict fact-checker. Read the ANSWER and the SOURCES it was
supposedly grounded in. Judge whether every factual claim in the answer is actually
supported by the sources - not whether the answer is well-written, not whether it's
plausible, only whether it's TRUE according to the sources given.

SOURCES:
{sources}

ANSWER:
{answer}

Respond with ONLY a JSON object, no other text:
{{"faithful": true or false, "reason": "one sentence explaining your judgment"}}

Mark faithful=false if the answer states anything not supported by the sources, even a
small detail, or if it hedges by citing a source that doesn't actually say the claim."""


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def judge_faithfulness(answer, sources_text):
    """Ask a second model call whether `answer` is actually supported by
    `sources_text`. Returns (faithful: bool, reason: str).

    Deliberately a separate call from the one that generated the answer -
    the same model grading its own homework in the same breath it wrote it
    is a much weaker check than a fresh call, reading critically, after the
    fact.
    """
    prompt = JUDGE_PROMPT.format(sources=sources_text, answer=answer)
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    try:
        result = json.loads(raw)
        return bool(result["faithful"]), result.get("reason", "")
    except (json.JSONDecodeError, KeyError):
        return False, f"Judge returned unparseable output: {raw[:200]}"
