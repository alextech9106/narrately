from pathlib import Path

from gtts import gTTS
from newspaper import Article, Config

_config = Config()
_config.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
_config.request_timeout = 10


def get_article_text(url: str) -> str:
    article = Article(url, config=_config)
    article.download()
    article.parse()
    return article.text


def create_audio_file(text: str, output_path: Path, lang: str) -> None:
    tts = gTTS(text=text, lang=lang)
    tts.save(str(output_path))


def export_audio_file(audio_file_name: str, text: str, lang: str) -> Path:
    output_path = Path(f"{audio_file_name}.mp3")
    create_audio_file(text, output_path, lang)
    return output_path
