from pathlib import Path

import pytest

import narrately


def test_text_to_audio_orchestrates_scrape_and_speech(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(narrately, "_get_article_text", lambda url: "hello world")

    saved: dict[str, object] = {}

    def fake_create_audio_file(text: str, output_path: Path, lang: str) -> None:
        saved["text"] = text
        saved["output_path"] = output_path
        saved["lang"] = lang

    monkeypatch.setattr(narrately, "_create_audio_file", fake_create_audio_file)

    result = narrately.text_to_audio(
        "https://example.com/article", "my_article", lang="es"
    )

    assert result == Path("my_article.mp3")
    assert saved == {
        "text": "hello world",
        "output_path": Path("my_article.mp3"),
        "lang": "es",
    }
