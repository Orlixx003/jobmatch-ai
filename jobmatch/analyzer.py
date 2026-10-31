"""Core logic: send CV + job offer to Claude and get a structured result back.

Claude is forced to answer through a tool call, so the response always
matches the JSON schema below — no fragile text parsing.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

DEFAULT_MODEL = "claude-sonnet-5-5"
MAX_INPUT_CHARS = 20_000

LANGUAGES = {"pl": "Polish", "en": "English", "uk": "Ukrainian"}

SYSTEM_PROMPT = """You are an experienced IT recruiter in Poland.
You compare a candidate's CV with a job offer honestly: never invent skills
or experience the CV does not show. Be specific and practical.
Junior candidates should get encouraging but realistic feedback."""

REPORT_TOOL: dict[str, Any] = {
    "name": "report_match",
    "description": "Report how well the CV matches the job offer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100,
                "description": "Overall fit, 0-100.",
            },
            "summary": {"type": "string", "description": "2-3 sentence verdict."},
            "matched_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Requirements from the offer that the CV clearly covers.",
            },
            "missing_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Requirements from the offer the CV does not show.",
            },
            "cv_tips": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-5 concrete edits to the CV for this offer.",
            },
            "cover_letter": {
                "type": "string",
                "description": "Short cover letter (150-220 words) in the requested language.",
            },
        },
        "required": [
            "score",
            "summary",
            "matched_skills",
            "missing_skills",
            "cv_tips",
            "cover_letter",
        ],
    },
}


@dataclass
class MatchResult:
    score: int
    summary: str
    matched_skills: list[str] = field(default_factory=list)
    missing_skills: list[str] = field(default_factory=list)
    cv_tips: list[str] = field(default_factory=list)
    cover_letter: str = ""

    @property
    def verdict(self) -> str:
        if self.score >= 75:
            return "Strong match — apply"
        if self.score >= 50:
            return "Partial match — worth applying with a tailored CV"
        return "Weak match — fill the gaps first"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MatchResult:
        score = max(0, min(100, int(data.get("score", 0))))
        return cls(
            score=score,
            summary=str(data.get("summary", "")).strip(),
            matched_skills=[str(s) for s in data.get("matched_skills", [])],
            missing_skills=[str(s) for s in data.get("missing_skills", [])],
            cv_tips=[str(s) for s in data.get("cv_tips", [])],
            cover_letter=str(data.get("cover_letter", "")).strip(),
        )

    def to_markdown(self) -> str:
        def bullets(items: list[str]) -> str:
            return "\n".join(f"- {i}" for i in items) or "- —"

        return (
            f"# JobMatch report\n\n**Score: {self.score}/100** — {self.verdict}\n\n"
            f"{self.summary}\n\n## Matched skills\n{bullets(self.matched_skills)}\n\n"
            f"## Missing skills\n{bullets(self.missing_skills)}\n\n"
            f"## How to improve the CV\n{bullets(self.cv_tips)}\n\n"
            f"## Cover letter\n\n{self.cover_letter}\n"
        )


def build_user_prompt(cv_text: str, job_text: str, language: str) -> str:
    lang = LANGUAGES.get(language, "English")
    return (
        f"<cv>\n{cv_text[:MAX_INPUT_CHARS]}\n</cv>\n\n"
        f"<job_offer>\n{job_text[:MAX_INPUT_CHARS]}\n</job_offer>\n\n"
        f"Analyse the fit and call report_match. "
        f"Write the summary, tips and cover letter in {lang}. "
        f"Skill names may stay in their original form."
    )


def analyze_match(
    cv_text: str,
    job_text: str,
    language: str = "en",
    *,
    api_key: str | None = None,
    model: str | None = None,
    client: Any = None,
) -> MatchResult:
    """Compare a CV with a job offer and return a MatchResult.

    `client` can be injected for testing; otherwise an Anthropic client is created.
    """
    if not cv_text.strip():
        raise ValueError("CV text is empty")
    if not job_text.strip():
        raise ValueError("Job offer text is empty")

    if client is None:
        from anthropic import Anthropic

        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("Set ANTHROPIC_API_KEY (see .env.example)")
        client = Anthropic(api_key=key)

    response = client.messages.create(
        model=model or os.getenv("JOBMATCH_MODEL", DEFAULT_MODEL),
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        tools=[REPORT_TOOL],
        tool_choice={"type": "tool", "name": "report_match"},
        messages=[{"role": "user", "content": build_user_prompt(cv_text, job_text, language)}],
    )

    for block in response.content:
        if getattr(block, "type", None) == "tool_use" and block.name == "report_match":
            return MatchResult.from_dict(block.input)

    raise RuntimeError("Model did not return a structured report")
