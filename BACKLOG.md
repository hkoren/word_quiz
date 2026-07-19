# Spellaroo Backlog

Inventory of enhancements for the Spellaroo web app (spellaroo.com), grouped by
category and priority. Mirrored into the Todoist "Spellaroo" project (the source
of truth). P1 = do first, P2 = soon, P3 = nice-to-have.

**Status:** The entire original backlog (all Security, Cosmetic, Usability, and
Functionality items below) was completed and deployed on 2026-07-19, as was the
**Admin / User Management** plan (admin = henrykoren@gmail.com; /admin dashboard
with search/pagination, user detail, deactivate/reactivate, delete+cascade,
temp-password reset, promote/demote with last-admin guard, audit log, JSON
export, bulk actions). Also shipped same day: dark-mode toggle (persisted,
system-preference aware), mobile responsiveness pass (hamburger nav, tap
targets, iOS zoom fix), and a word-database audit (30 grade-level corrections,
57 new kindergarten words — K set now 73, total 1,930).

The only open work is the **Monetization** plan (17 tasks in Todoist).

Highlights shipped: SHA-1→PBKDF2 (rehash-on-login), CSRF, server-side quiz
state (answers off the cookie), SECRET_KEY hard-fail, rate limiting, email
normalization, HSTS, privacy page, Google OAuth (ProxyFix + PKCE fix),
character-diff feedback, spell-it-out, voice/speed controls, autoplay handling,
remembered settings, practice-missed mode, top-missed insights, profile
editing, streaks/badges, PWA manifest, kangaroo branding, and assorted bug
fixes (blank results definitions, dead date, stale word count, debug output).

## Security

- [x] ~~**P1 — Replace SHA-1 password hashing with PBKDF2**~~ ✅ 2026-07-19 — `hash_password()`/`verify_password()`
  in web_quiz.py use raw SHA-1. `werkzeug.security` (`generate_password_hash`/
  `check_password_hash`) is already imported. Rehash-on-login for any existing
  users; user table is currently empty in prod, so now is the cheap moment.
- [ ] **P1 — Add CSRF protection** — no CSRF tokens on any POST form (login,
  register, setup) or the `/submit_answer` JSON endpoint. Add Flask-WTF's
  CSRFProtect (with `X-CSRFToken` header for the AJAX call).
- [x] ~~**P1 — Harden session cookie flags**~~ ✅ 2026-07-19 — set `SESSION_COOKIE_SECURE=True`,
  `SESSION_COOKIE_SAMESITE='Lax'` (HttpOnly is Flask's default). Site is
  HTTPS-only in prod so Secure is safe.
- [ ] **P1 — Quiz answers are readable in the session cookie** — the full
  `selected_words` list is stored in the Flask session cookie, which is signed
  but *not encrypted*; any student can base64-decode it and read the answers.
  Move quiz state server-side (SQLite table keyed by a session token).
- [x] ~~**P1 — Remove `OAUTHLIB_INSECURE_TRANSPORT=1`**~~ ✅ 2026-07-19 — hardcoded at import time
  in web_quiz.py; disables HTTPS enforcement in the OAuth flow in production.
  Make it conditional on a DEV env var.
- [ ] **P2 — Fail hard on missing SECRET_KEY** — falls back to the literal
  `'your-secret-key-change-this-in-production'`; forge-able sessions if ever
  launched without the env var. Raise at startup instead when not in debug.
- [ ] **P2 — Rate-limit login/register** — no brute-force protection. Flask-Limiter
  on `/login`, `/register` (e.g. 5/min per IP).
- [ ] **P2 — Fix requirements.txt** — missing `google-auth`, `google-auth-oauthlib`,
  `requests` (imported unconditionally at web_quiz.py top; installed manually on
  the server). Also consider bumping the 2023-era Flask 2.3.3 / Werkzeug 2.3.7 pins.
- [ ] **P2 — Normalize emails** — register/login compare emails case-sensitively;
  `Kid@x.com` and `kid@x.com` become two accounts. Lowercase+strip on both paths.
- [ ] **P3 — Kids' data & COPPA posture** — registration collects birth year/month
  of children. Add a privacy policy page, consider making DOB optional, and
  minimize what's stored.
- [ ] **P3 — Add HSTS header** in the Apache vhost.

## Cosmetic

- [ ] **P1 — Kangaroo branding** — the name is Spellaroo but there's no kangaroo
  anywhere: add a logo/mascot, favicon (currently browser default), and swap the
  generic `fa-spell-check` icon. Consider a warmer kid-friendly palette than the
  current gray-on-purple.
- [ ] **P2 — Fix stale "860+ Words" claim on home page** — dictionary has 1,873
  words; render the real count from `len(word_dictionary)`.
- [ ] **P2 — Results page date is dead code** — `moment().format(...)` references
  an undefined `moment`, so it always shows "Just completed". Render the server
  timestamp instead.
- [ ] **P3 — Strip debug leftovers** — `console.log` in setup.html/statistics.html,
  `API DEBUG` prints in `/api/available_words`.
- [ ] **P3 — Register page birth-year list hardcoded to 2024** — generate from
  current year server-side.
- [ ] **P3 — Navbar shows Home/New Quiz/Statistics on the login page** — hide nav
  links (and show Login/Logout appropriately) based on session state; add
  Logout/Profile to the navbar instead of only on index/profile pages.

## Usability

- [ ] **P1 — Port the CLI's character-diff feedback to the web** — the CLI's
  `compare_spellings()` (lowercase = right, UPPERCASE = wrong/missing) is the
  app's best teaching feature and the web version doesn't have it. Return the
  diff from `/submit_answer` and render it in the feedback card.
- [ ] **P2 — "Spell it out" playback** — CLI spells the word letter-by-letter
  after a miss; add the same via Web Speech on the feedback card and results page.
- [ ] **P2 — Remember last quiz settings per user** — CLI persists defaults.json;
  web setup page resets every time. Store last grades/word-type/count on the
  user row and preselect.
- [ ] **P2 — Handle browser autoplay blocking** — the quiz auto-speaks the word
  0.5 s after load; browsers block speech before user interaction, which reads
  as "audio is broken." Detect and show a "tap to hear your word" prompt.
- [ ] **P3 — Voice/rate controls** — let users pick a voice and speaking rate;
  quality of default Web Speech voices varies wildly across devices.
- [ ] **P3 — Abandon/restart quiz affordance** — navigating away mid-quiz leaves
  stale `quiz_config` in the session; add an explicit "quit quiz" and handle
  resuming sensibly.
- [ ] **P3 — Accessibility pass** — aria-live on the feedback region, focus
  management after submit, labels on icon-only buttons.

## Functionality

- [x] ~~**P1 — Statistics page leaks all users' data**~~ ✅ 2026-07-19 — `/statistics` queries the
  sessions table with **no user_id filter**: every user sees everyone's quiz
  history and aggregate stats. Filter by `session['user_id']` (also a privacy
  issue).
- [ ] **P2 — Fix empty definitions on results page** — results.html references
  `word_dictionary`, which the route never passes; "Words to Review" definitions
  are always blank.
- [ ] **P2 — Top-misspelled-words insights** — CLI shows a top-10 misspelled
  list; the web stores `incorrect_words` per session but never surfaces them.
  Add to statistics page.
- [ ] **P2 — Practice-missed-words mode** — one-click quiz built from the user's
  historical misses (spaced-repetition-lite).
- [ ] **P3 — session_id column is always 'anonymous'** — `save_session_data`
  reads `session.get('session_id')` which is never set. Drop the column or set
  a real value.
- [x] ~~**P3 — Enable Google OAuth in production**~~ ✅ 2026-07-19 (register redirect URI in Google Console to finish) — code path exists; needs real
  GOOGLE_CLIENT_ID/SECRET in `/vhosts/spellaroo/spellaroo.env` plus the
  insecure-transport fix above.
- [ ] **P3 — Profile management** — edit name, change password; no email
  verification or password reset exists (reset likely wants an SMTP story first).
- [ ] **P3 — Gamification for kids** — streaks, badges, per-grade progress bars.
- [ ] **P3 — PWA manifest** — home-screen install + offline shell for tablets.
