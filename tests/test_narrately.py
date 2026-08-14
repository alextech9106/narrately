from pathlib import Path

import pytest

import narrately


def _capture_create_audio_file(
    saved: dict[str, object],
) -> object:
    def fake_create_audio_file(text: str, output_path: Path, lang: str) -> None:
        saved["text"] = text
        saved["output_path"] = output_path
        saved["lang"] = lang

    return fake_create_audio_file


def test_article_to_audio_orchestrates_scrape_and_speech(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        narrately._internal, "get_article_text", lambda url: "hello world"
    )

    saved: dict[str, object] = {}
    monkeypatch.setattr(
        narrately._internal, "create_audio_file", _capture_create_audio_file(saved)
    )

    result = narrately.article_to_audio(
        "https://example.com/article", "my_article", lang="es"
    )

    assert result == Path("my_article.mp3")
    assert saved == {
        "text": "hello world",
        "output_path": Path("my_article.mp3"),
        "lang": "es",
    }


def test_text_to_audio_converts_text_directly(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)

    def fail_if_called(url: str) -> str:
        raise AssertionError("text_to_audio must not scrape an article")

    monkeypatch.setattr(narrately._internal, "get_article_text", fail_if_called)

    saved: dict[str, object] = {}
    monkeypatch.setattr(
        narrately._internal, "create_audio_file", _capture_create_audio_file(saved)
    )

    result = narrately.text_to_audio("hello world", "greeting", lang="es")

    assert result == Path("greeting.mp3")
    assert saved == {
        "text": "hello world",
        "output_path": Path("greeting.mp3"),
        "lang": "es",
    }
