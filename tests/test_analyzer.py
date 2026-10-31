"""Tests run without an API key: the Anthropic client is replaced by a fake."""

from types import SimpleNamespace

import pytest

from jobmatch.analyzer import MatchResult, analyze_match, build_user_prompt
from jobmatch.cv_reader import CVReadError, read_cv

SAMPLE = {
    "score": 72,
    "summary": "Good junior fit.",
    "matched_skills": ["Python", "Git"],
    "missing_skills": ["Docker"],
    "cv_tips": ["Add a link to GitHub"],
    "cover_letter": "Dzień dobry...",
}


class FakeClient:
    def __init__(self, payload):
        self.calls = []
        block = SimpleNamespace(type="tool_use", name="report_match", input=payload)
        self.messages = SimpleNamespace(create=self._create)
        self._response = SimpleNamespace(content=[block])

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return self._response


def test_analyze_returns_structured_result():
    client = FakeClient(SAMPLE)
    result = analyze_match("Python developer CV " * 5, "We need Python and Docker", "pl", client=client)

    assert isinstance(result, MatchResult)
    assert result.score == 72
    assert result.missing_skills == ["Docker"]
    assert client.calls[0]["tool_choice"] == {"type": "tool", "name": "report_match"}
    assert "Polish" in client.calls[0]["messages"][0]["content"]


def test_score_is_clamped():
    assert MatchResult.from_dict({**SAMPLE, "score": 150}).score == 100
    assert MatchResult.from_dict({**SAMPLE, "score": -5}).score == 0


@pytest.mark.parametrize("score,word", [(80, "Strong"), (60, "Partial"), (20, "Weak")])
def test_verdict(score, word):
    assert MatchResult.from_dict({**SAMPLE, "score": score}).verdict.startswith(word)


def test_empty_inputs_rejected():
    with pytest.raises(ValueError):
        analyze_match("", "job", client=FakeClient(SAMPLE))
    with pytest.raises(ValueError):
        analyze_match("cv", "   ", client=FakeClient(SAMPLE))


def test_missing_tool_call_raises():
    client = FakeClient(SAMPLE)
    client._response = SimpleNamespace(content=[SimpleNamespace(type="text", text="hi")])
    with pytest.raises(RuntimeError):
        analyze_match("cv text", "job text", client=client)


def test_prompt_truncates_long_input():
    prompt = build_user_prompt("x" * 50_000, "job", "en")
    assert len(prompt) < 25_000


def test_markdown_report_contains_sections():
    md = MatchResult.from_dict(SAMPLE).to_markdown()
    assert "72/100" in md and "## Missing skills" in md and "- Docker" in md


def test_read_txt_cv(tmp_path):
    cv = tmp_path / "cv.txt"
    cv.write_text("Jan Kowalski\nPython, SQL, Git\n" * 5, encoding="utf-8")
    assert "Python" in read_cv(cv)


def test_unsupported_file(tmp_path):
    bad = tmp_path / "cv.png"
    bad.write_bytes(b"123")
    with pytest.raises(CVReadError):
        read_cv(bad)


def test_empty_cv(tmp_path):
    empty = tmp_path / "cv.txt"
    empty.write_text("hi", encoding="utf-8")
    with pytest.raises(CVReadError):
        read_cv(empty)
