"""Tests for the retry/fallback logic and recommendation post-processing
in modules/ai_engine.py, using a fake client so nothing here makes a
real network call or needs an API key. time.sleep is patched to a
no-op so the retry/backoff paths run instantly instead of actually
waiting seconds per test.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules import ai_engine
from modules.ai_engine import call_gemini_with_retry, get_top3_recommendations, looks_like_gemini_key


class FakeResponse:
    def __init__(self, text):
        self.text = text


class FakeModels:
    """Records every (model, contents) call made and answers according
    to a scripted list of behaviors per model name."""

    def __init__(self, script):
        self.script = script  # {model_name: [Exception|str, ...]}
        self.calls = []

    def generate_content(self, model, contents):
        self.calls.append(model)
        behaviors = self.script.get(model, [])
        if not behaviors:
            raise RuntimeError(f"unscripted model called: {model}")
        behavior = behaviors.pop(0)
        if isinstance(behavior, Exception):
            raise behavior
        return FakeResponse(behavior)


class FakeClient:
    def __init__(self, script):
        self.models = FakeModels(script)


@pytest.fixture(autouse=True)
def no_real_sleep(monkeypatch):
    monkeypatch.setattr(ai_engine.time, "sleep", lambda *_: None)


# ---------------------------------------------------------------------
# looks_like_gemini_key
# ---------------------------------------------------------------------

def test_looks_like_gemini_key_rejects_placeholder_text():
    assert looks_like_gemini_key("paste-your-key-here") is False
    assert looks_like_gemini_key("") is False
    assert looks_like_gemini_key(None) is False


def test_looks_like_gemini_key_accepts_correctly_shaped_key():
    assert looks_like_gemini_key("AIza" + "x" * 35) is True


# ---------------------------------------------------------------------
# call_gemini_with_retry
# ---------------------------------------------------------------------

def test_succeeds_immediately_on_first_model():
    client = FakeClient({"gemini-2.5-flash": ["ok response"]})
    response = call_gemini_with_retry(client, "gemini-2.5-flash", "prompt")
    assert response.text == "ok response"
    assert client.models.calls == ["gemini-2.5-flash"]


def test_moves_to_next_model_immediately_on_not_found_no_wasted_retries():
    client = FakeClient({
        "gemini-2.5-flash": [RuntimeError("404 model not found")],
        "gemini-2.0-flash": ["fallback response"],
    })
    response = call_gemini_with_retry(client, "gemini-2.5-flash", "prompt")
    assert response.text == "fallback response"
    # Exactly one attempt on the dead model, then straight to the next.
    assert client.models.calls == ["gemini-2.5-flash", "gemini-2.0-flash"]


def test_retries_same_model_on_transient_error_before_succeeding():
    client = FakeClient({
        "gemini-2.5-flash": [RuntimeError("503 Service Unavailable"), "ok on second try"],
    })
    response = call_gemini_with_retry(client, "gemini-2.5-flash", "prompt")
    assert response.text == "ok on second try"
    assert client.models.calls == ["gemini-2.5-flash", "gemini-2.5-flash"]


def test_raises_immediately_on_non_transient_non_not_found_error():
    # A bad API key should not burn through every fallback model -
    # it should surface right away.
    client = FakeClient({"gemini-2.5-flash": [RuntimeError("400 API_KEY_INVALID")]})
    with pytest.raises(RuntimeError, match="API_KEY_INVALID"):
        call_gemini_with_retry(client, "gemini-2.5-flash", "prompt")
    assert client.models.calls == ["gemini-2.5-flash"]


def test_raises_last_error_after_exhausting_every_model():
    all_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash", "gemini-2.5-pro", "gemini-1.5-pro"]
    script = {m: [RuntimeError("503 overloaded")] * 3 for m in all_models}
    client = FakeClient(script)
    with pytest.raises(RuntimeError, match="overloaded"):
        call_gemini_with_retry(client, "gemini-2.5-flash", "prompt")


# ---------------------------------------------------------------------
# get_top3_recommendations post-processing (dedup + count capping)
# ---------------------------------------------------------------------

def test_get_top3_deduplicates_by_normalized_material_name():
    raw_json = """
    [
        {"MaterialName": "Ti-6Al-4V", "Confidence": 95, "Reasoning": "r", "Pros": [], "Cons": []},
        {"MaterialName": "ti-6al-4v", "Confidence": 90, "Reasoning": "dup", "Pros": [], "Cons": []},
        {"MaterialName": "Aluminum 6061", "Confidence": 80, "Reasoning": "r2", "Pros": [], "Cons": []}
    ]
    """
    client = FakeClient({"gemini-2.5-flash": [raw_json]})
    db_string = "Name\nTi-6Al-4V\nAluminum 6061\nSteel 1018"  # 3 candidates + header
    results = get_top3_recommendations(client, db_string, "query", "gemini-2.5-flash")
    names = [r["MaterialName"] for r in results]
    assert names == ["Ti-6Al-4V", "Aluminum 6061"]  # the lowercase dup is dropped


def test_get_top3_returns_empty_list_when_database_has_no_candidates():
    client = FakeClient({})  # never called
    results = get_top3_recommendations(client, "Name\n", "query", "gemini-2.5-flash")
    assert results == []
    assert client.models.calls == []


def test_get_top3_strips_markdown_fences_from_response():
    raw_json = '```json\n[{"MaterialName": "Steel", "Confidence": 70, "Reasoning": "r", "Pros": [], "Cons": []}]\n```'
    client = FakeClient({"gemini-2.5-flash": [raw_json]})
    db_string = "Name\nSteel"
    results = get_top3_recommendations(client, db_string, "query", "gemini-2.5-flash")
    assert results[0]["MaterialName"] == "Steel"
