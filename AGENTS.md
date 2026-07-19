# AGENTS.md

Guidance for AI agents and developers working in this repository.

## Purpose

**Word Quiz** is a spelling-practice application for students (kindergarten
through grade 12). A word is pronounced aloud together with its definition, the
learner types the spelling, and the app scores the attempt, plays a
reward/penalty sound, and — when wrong — shows a character-by-character diff of
what was misspelled. Progress is tracked across sessions.

The project ships **two independent front ends over one shared word list**:

| App | Entry point | Audience | Audio | Persistence |
|-----|-------------|----------|-------|-------------|
| **CLI quiz** | [word_quiz.py](word_quiz.py) | Terminal, single local user | Google Cloud TTS (cached) → `espeak` fallback, played via `pygame` | `sessions.json`, `defaults.json` |
| **Web quiz** | [web_quiz.py](web_quiz.py) | Browser, multi-user with accounts | Browser Web Speech API (client-side) | SQLite `quiz_sessions.db` |

Both import the same `word_dictionary` from [word_lists.py](word_lists.py), so
the two apps always quiz from an identical vocabulary.

## Architecture

### Shared data — [word_lists.py](word_lists.py)
A single module-level dict, `word_dictionary`, maps each word to its metadata.
This is the source of truth for both apps.

```python
"newword": {
    "grade_levels": ["k", 3, 4],   # "k" for kindergarten, ints 1–12 for grades
    "sight_word": False,           # True = high-frequency sight word
    "definition": "definition here"
}
```

- ~1,800+ entries. A word may belong to multiple grade levels.
- `build_word_pool(grades, word_type)` (duplicated in both apps) filters this
  dict by selected grades and word type, where `word_type` is one of:
  `'s'` sight words only, `'o'` non-sight words only, `'f'` 50/50 mix,
  `'r'` random mix.

### CLI app — [word_quiz.py](word_quiz.py)
- `main_game_loop()` → prompts for grade levels and word type (remembered in
  `defaults.json`), then repeatedly runs `run_single_quiz()` (10 words/round).
- **Text-to-speech** is the bulk of this file. `say()` calls
  `_synthesize_speech_google()`, which splits a phrase into cacheable
  components (individual letters and words are cached to `voice_files/*.wav`
  keyed by an md5 hash of the text) and falls back to the `espeak` CLI when
  Google Cloud TTS is unavailable. Audio plays through `pygame.mixer`.
- Sound effects: `ding.wav` (correct), `buzzer.wav` (incorrect).
- `compare_spellings()` runs an edit-distance (DP) alignment so correctly
  placed characters render lowercase and wrong/missing ones UPPERCASE.
- Sessions are appended to `sessions.json`; `show_play_statistics()` reports
  accuracy and the top-10 most-misspelled words.
- Google credentials come from a service-account JSON (`service-account-key.json`,
  `google-credentials.json`, or `$GOOGLE_APPLICATION_CREDENTIALS`); `voiceAPI.json`
  holds OAuth client info. See [GOOGLE_TTS_SETUP.md](GOOGLE_TTS_SETUP.md).

### Web app — [web_quiz.py](web_quiz.py)
Flask application. Key pieces:
- **`init_db()`** creates/migrates the SQLite schema in `quiz_sessions.db`:
  - `users` — accounts (`name`, `email`, `password_hash`, `google_id`,
    `birth_year`, `birth_month`, `auth_provider`).
  - `sessions` — one row per completed quiz (grades, word type, counts,
    percentage, JSON list of incorrect words, `user_id` FK).
- **Auth**: local email/password *and* Google OAuth 2.0. `login_required`
  decorator gates the quiz routes. See [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md).
- **Quiz flow** (server-driven, state in the Flask session cookie):
  `/setup` (POST builds the word pool + picks words) → `/quiz` (renders one
  word) → `/submit_answer` (POST JSON; scores, advances, returns the *next*
  word for automatic progression) → `/results`. `/statistics` shows history.
- **Audio** is entirely client-side via the browser Web Speech API in the
  templates — the server sends no audio.
- Templates in [templates/](templates/) extend `base.html`; styles in
  [static/style.css](static/style.css).
- Dev server: `python web_quiz.py` runs on **port 5557** (note: WEB_README
  examples say 5000). Production runs under WSGI.

### Deployment
- [wsgi.py](wsgi.py) is the WSGI entry point (calls `init_db()`, exposes
  `application`).
- [deploy.sh](deploy.sh) + [apache-vhost.conf](apache-vhost.conf) deploy under
  Apache `mod_wsgi`. Gunicorn is an alternative (`gunicorn wsgi:application`).
  See [WEB_README.md](WEB_README.md) for the full deployment guide.

### Support code & docs
- [utils/](utils/) — standalone scripts for exercising/analyzing the CLI's TTS
  caching (`cache_words.py`, `analyze_cache.py`, and many `test_*.py`). Not
  imported by the apps; run directly.
- Root `test_api.py`, `debug_test.py`, `validate_web.py` — ad-hoc web/API checks.
- `word_quiz/` subdirectory is an **older nested copy** of the CLI project
  (untracked in git) — ignore it; edit the top-level files.

## Conventions & gotchas

- **Two copies of `build_word_pool` and `save_session_data`** exist (CLI vs
  web). Changing quiz-selection logic means editing both.
- **Password hashing is SHA-1** in the web app (`hash_password`), despite
  `werkzeug.security` being imported. This is weak; if asked to touch auth,
  flag it — don't silently assume bcrypt/PBKDF2.
- `quiz_sessions.db` and `quiz_sessions_backup.db` are committed to the repo and
  contain real session/user rows — be careful editing or regenerating them.
- Secrets: `voiceAPI.json`, `sessions.json`, and `defaults.json` are
  git-ignored. Never commit real Google credentials or `SECRET_KEY`.
- Grade levels are **mixed types**: the string `"k"` plus integers `1`–`12`.
  Preserve this when filtering.

## Debugging

- **CLI audio/TTS fails**: check that `pygame` is installed and that
  `ding.wav`/`buzzer.wav` exist in the repo root (a missing sound file prints a
  warning rather than crashing). If Google Cloud TTS is misconfigured the app
  silently falls back to `espeak` — confirm `espeak` is on the `PATH`. The CLI
  prints diagnostic info about the TTS path it chose.
- **Web audio fails**: audio is the browser's Web Speech API — check the browser
  console and note many browsers require HTTPS for speech in production.

> Note: [.github/copilot-instructions.md](.github/copilot-instructions.md) is
> **outdated** — it predates the module split, the Google-TTS/`espeak` pipeline,
> and the entire web app (it still references `pyttsx3` and a hardcoded
> `word_list`). Prefer this file.

## Common commands

```bash
# CLI quiz
python word_quiz.py

# Web quiz (dev, http://localhost:5557)
pip install -r requirements.txt
python web_quiz.py

# Web quiz (prod)
gunicorn --bind 0.0.0.0:8000 wsgi:application
./deploy.sh            # Apache mod_wsgi deployment
```

Set `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` (web OAuth) and `SECRET_KEY`
(Flask) via environment variables for production.
