"""
Agent Teaser — Lab 3D finale
A minimal agent loop that uses our deployed AI Workbench API as a tool.
Demonstrates: think → act → observe — the foundation of all AI agents.

This is NOT a full agent — it's the conceptual bridge to Module 1.
It shows how the service we built becomes a "tool" an agent can call.
"""

import os
import sys
import requests
from dotenv import load_dotenv
from openai import OpenAI

# Ensure emoji/arrows render on Windows terminals (cp1252 default).
# Harmless on macOS/Linux, which are already UTF-8. Guarded for older Pythons.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def think(task_description: str) -> str:
    """Agent decides what action to take."""
    response = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4.1-mini"),
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a planning agent. Given a task, decide which tool to use. "
                    "Available tools: summarize, rewrite, keypoints, explain. "
                    "Respond with ONLY the tool name, nothing else."
                ),
            },
            {"role": "user", "content": task_description},
        ],
        temperature=0,
        max_tokens=20,
    )
    return response.choices[0].message.content.strip().lower()


def act(tool: str, text: str) -> str:
    """Agent calls our AI Workbench API as a tool."""
    response = requests.post(
        f"{API_URL}/{tool}",
        json={"text": text},
        timeout=30,
    )
    if response.status_code == 200:
        return response.json()["result"]
    return f"Error: {response.status_code}"


def observe(result: str) -> bool:
    """Agent evaluates whether the task is complete."""
    return len(result) > 0 and "Error" not in result


def main():
    print("=" * 50)
    print("AGENT TEASER: think → act → observe")
    print("=" * 50)
    print()

    task = "I have a long paragraph about AI ethics. Make it easier to understand."
    text = (
        "The deployment of artificial intelligence systems in critical domains such as "
        "healthcare, criminal justice, and financial services necessitates rigorous "
        "frameworks for ensuring algorithmic fairness, transparency, and accountability. "
        "Without such frameworks, there is substantial risk of perpetuating and amplifying "
        "existing societal biases through automated decision-making processes."
    )

    print(f"📋 Task: {task}")
    print(f"📄 Input: {text[:80]}...")
    print()

    # THE AGENT LOOP
    print("🔄 Agent Loop Starting...")
    print()

    # Step 1: THINK
    print("💭 THINK: Deciding which tool to use...")
    tool = think(task)
    print(f"   → Decision: use '{tool}'")
    print()

    # Step 2: ACT
    print(f"⚡ ACT: Calling {API_URL}/{tool}...")
    result = act(tool, text)
    print(f"   → Got response ({len(result)} chars)")
    print()

    # Step 3: OBSERVE
    print("👁️  OBSERVE: Evaluating result...")
    success = observe(result)
    print(f"   → Task complete: {success}")
    print()

    # Show result
    print("─" * 50)
    print("RESULT:")
    print("─" * 50)
    print(result)
    print("─" * 50)
    print()
    print("🎯 What just happened:")
    print("   1. The agent THOUGHT about which tool to use (LLM reasoning)")
    print("   2. The agent ACTED by calling our deployed API (tool use)")
    print("   3. The agent OBSERVED the result (evaluation)")
    print()
    print("   In Module 1, you'll build agents that loop this autonomously,")
    print("   use multiple tools, and handle failures — all on their own.")


if __name__ == "__main__":
    main()
