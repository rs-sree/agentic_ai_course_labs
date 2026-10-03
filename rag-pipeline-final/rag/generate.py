"""Grounded generation: turn retrieved chunks into a grounded, cited answer -
or an honest refusal when the sources don't support one.

Provider-agnostic wrapper. We use OpenAI here, but the same pattern - context
in, instructed to answer only from it - works with any chat-completion model.
"""
from __future__ import annotations
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def format_sources(chunks):
    """Label each chunk with a source number the model - and a reader - can cite."""
    lines = []
    for i, chunk in enumerate(chunks, start=1):
        meta = chunk["metadata"]
        lines.append(f"[Source {i}: {meta.get('source')}]\n{chunk['text']}")
    return "\n\n".join(lines)


NAIVE_PROMPT = """Answer the question using the following context if it's helpful.

{context}

Question: {question}
Answer:"""


GROUNDED_PROMPT = """Answer the question using ONLY the sources below. Cite the source number \
after every claim, like [1]. If the sources do not contain the answer, say exactly: \
"I can't verify that from the Daily Planet's sources." Do not use any outside knowledge, \
even if you are confident it's correct.

{context}

Question: {question}
Answer:"""


def generate_answer(question, chunks, prompt_template=GROUNDED_PROMPT):
    """Turn retrieved chunks + a question into an answer, using the given prompt."""
    context = format_sources(chunks)
    prompt = prompt_template.format(context=context, question=question)
    response = _get_client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content
