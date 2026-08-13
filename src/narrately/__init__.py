from pathlib import Path

from gtts import gTTS
from newspaper import Article, Config

_config = Config()
_config.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_config.request_timeout = 10


def _get_article_text(url: str) -> str:
    article = Article(url, config=_config)
    article.download()
    article.parse()
    return article.text


def _create_audio_file(text: str, output_path: Path, lang: str) -> None:
    tts = gTTS(text=text, lang=lang)
    tts.save(str(output_path))


def _export_audio_file(audio_file_name: str, text: str, lang: str) -> Path:
    output_path = Path(f"{audio_file_name}.mp3")
    _create_audio_file(text, output_path, lang)
    return output_path


def article_to_audio(url: str, audio_file_name: str, lang: str = "en") -> Path:
    """Scrape the article at `url` and save it as an mp3 file named `audio_file_name`."""
    text = _get_article_text(url)
    return _export_audio_file(audio_file_name, text, lang)


def text_to_audio(text: str, audio_file_name: str, lang: str = "en") -> Path:
    """Select a text and save it as an mp3 file named `audio_file_name`."""
    return _export_audio_file(audio_file_name, text, lang)


__all__ = ["text_to_audio"]
