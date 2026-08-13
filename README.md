# narrately

Convert a web article into a spoken mp3 file, given its URL.

## Installation

```bash
pip install narrately
```

## Usage

```python
from narrately import text_to_audio

output_path = text_to_audio(
    "https://example.com/some-article",
    "article",
    lang="en",
)
print(f"Saved audio to {output_path}")
```

`text_to_audio(url, audio_file_name, lang="en")` downloads and extracts the
article text from `url` (using `newspaper3k`), converts it to speech (using
`gtts`), and saves it as `{audio_file_name}.mp3`. It returns the `Path` to the
generated file.

`audio_file_name` can be a plain name (saved in the current directory) or a
full path, e.g. `"output/my_article"` — either way, don't include the `.mp3`
extension, it's appended automatically.

`lang` is a two-letter language code (e.g. `"en"`, `"es"`, `"fr"`) passed
through to `gtts`.

## Notes

- Requires an internet connection: both article scraping and speech
  generation call external services.
- Some sites block automated scraping or require a paid subscription
  (paywalls); in those cases article extraction may fail or return partial
  content.

## License

MIT
