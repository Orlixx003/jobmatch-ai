"""Demo mode: a sample analysis of the files in examples/, so the app can be
tried without an API key. The result below is a fixed example, not a live call."""

from pathlib import Path

from .analyzer import MatchResult

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def demo_inputs() -> tuple[str, str]:
    """Return (cv_text, job_text) from the bundled examples."""
    cv = (EXAMPLES / "cv_example.txt").read_text(encoding="utf-8")
    job = (EXAMPLES / "job_example.txt").read_text(encoding="utf-8")
    return cv, job


DEMO_RESULT = MatchResult(
    score=68,
    summary=(
        "Solid junior profile for this role: Python, Git, SQL and hands-on work with LLM APIs "
        "cover most core requirements. The main gaps are Docker and cloud experience, "
        "which the offer lists as required."
    ),
    matched_skills=["Python", "Git", "LLM APIs (OpenAI / Anthropic)", "SQL (PostgreSQL)", "English B2"],
    missing_skills=["Docker", "AWS or GCP", "LangChain", "Vector databases"],
    cv_tips=[
        "Move the AI text tool to the top of Projects and describe the prompt-engineering work.",
        "Add a small Dockerfile to one project and mention it — it closes the biggest gap.",
        "Give each project one measurable result (users, time saved, response time).",
        "Add Polish B2 to the summary line — it is a nice-to-have in this offer.",
    ],
    cover_letter=(
        "Dzień dobry,\n\n"
        "z dużym zainteresowaniem przeczytałem ofertę na stanowisko Junior AI Developer. "
        "Studiuję Programowanie w WSB Merito w Warszawie i od kilku miesięcy buduję projekty "
        "oparte na modelach językowych — m.in. narzędzie tekstowe korzystające z Claude API "
        "oraz bota Telegram do rezerwacji wizyt w Pythonie.\n\n"
        "Na co dzień pracuję z Pythonem, Gitem i SQL, a integracja z API modeli językowych "
        "oraz projektowanie promptów to obszar, który rozwijam najintensywniej. "
        "Wiem, że brakuje mi jeszcze doświadczenia z Dockerem i chmurą — właśnie dlatego "
        "zależy mi na zespole, który oferuje mentoring i budżet szkoleniowy.\n\n"
        "Chętnie opowiem więcej podczas rozmowy.\n\n"
        "Z poważaniem,\nJan Kowalski"
    ),
)
