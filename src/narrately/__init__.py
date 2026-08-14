from pathlib import Path

from narrately import _internal


def article_to_audio(url: str, audio_file_name: str, lang: str = "en") -> Path:
    """Scrape the article at `url` and save it as an mp3 file named `audio_file_name`."""
    text = _internal.get_article_text(url)
    return _internal.export_audio_file(audio_file_name, text, lang)


def text_to_audio(text: str, audio_file_name: str, lang: str = "en") -> Path:
    """Select a text and save it as an mp3 file named `audio_file_name`."""
    return _internal.export_audio_file(audio_file_name, text, lang)


__all__ = ["article_to_audio", "text_to_audio"]
