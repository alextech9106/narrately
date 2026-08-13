from gtts import gTTS
from newspaper import Article, Config

config = Config()
config.browser_user_agent = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "                                                       
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
config.request_timeout = 10

def get_article_text(url_path: str) -> str:
    article = Article(url_path, config=config)
    article.download()
    article.parse()
    return article.text

def create_audio_file(text: str, output_path: str, lang: str = "en") -> None:
    tts = gTTS(text=text, lang=lang)
    tts.save(str(output_path))

def text_to_voice(url: str, audio_file_name: str, lang: str = "en") -> None:
    if __name__ == "__main__":
        text = get_article_text(url)
        create_audio_file(text, f"{audio_file_name}.mp3", lang)