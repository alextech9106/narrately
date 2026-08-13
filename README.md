# text-to-voice

Convierte el artículo de una URL en audio.

## Uso

```bash
PYTHONWARNINGS="ignore::SyntaxWarning" uv run text-to-voice
```

La variable `PYTHONWARNINGS` silencia los `SyntaxWarning` que emite internamente
`newspaper3k` (usa regex sin prefijo `r` en su propio código, algo ajeno a este
proyecto) sin afectar a otros warnings que sí puedan ser relevantes.
