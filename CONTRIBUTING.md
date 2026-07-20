# Contributing

Thanks for helping build the IRONMAN 70.3 Tracker! This is a small, dependency-free
project, so getting set up is quick.

## Getting access

- **Code:** ask the owner ([@mformanas](https://github.com/mformanas)) to add you as
  a collaborator, or fork the repo and open pull requests.
- **Backend (Supabase):** the app talks to a shared Supabase project. To test
  features that touch auth/sync/leaderboard against the real backend, ask the owner
  to invite you to the Supabase project, **or** spin up your own (see below).

## Local development

```bash
git clone https://github.com/mformanas/ironman-703-2027-tracker.git
cd ironman-703-2027-tracker
python3 build.py            # regenerate index.html
python3 -m http.server 8080 # serve at http://localhost:8080
```

Only **Python 3** (standard library) is required to build. Node is only needed for
the optional native iOS wrapper.

## How the app is structured

Everything ships as one self-contained `index.html`. You don't edit that file
directly — you edit the source and rebuild:

- `src/app_template.html` — all markup, CSS, and app logic. Contains a
  `/*PLAN_DATA*/` placeholder where the plan JSON is injected at build time.
- `src/build_data.py` — generates the 77-week periodized plan into
  `src/plan_data.json`. Edit this if you change plan structure, phases, or volumes.
- `build.py` — runs the data step, injects into the template, writes `index.html`,
  and syncs `ios-app/www/`.

## Workflow

1. Create a branch: `git checkout -b feature/short-name`.
2. Edit files under `src/` (and/or `build.py`, assets).
3. Run `python3 build.py` and test in the browser.
4. Commit your `src/` changes **and** the regenerated `index.html` together.
5. Push and open a PR with a short description and, ideally, before/after notes or
   screenshots for UI changes.

## Validating your build

The app's JS is large; a quick sanity check before committing:

```bash
python3 build.py
# extract the main inline <script> and syntax-check it
python3 - <<'PY'
import re
html=open("index.html").read()
big=max(re.findall(r"<script(?![^>]*src=)[^>]*>(.*?)</script>", html, re.S), key=len)
open("/tmp/app.js","w").write(big)
PY
node --check /tmp/app.js && echo "JS OK"
```

## Code conventions

- Vanilla JS, no framework, no build-time bundler. Keep it dependency-light.
- `$("#id")` is the in-app shorthand for `document.querySelector`.
- State persists to `localStorage` (key `im703_tracker_v1`) and syncs to Supabase
  when signed in.
- Keep styling within the existing CSS variables / palette at the top of the
  template.
- Don't commit secrets. The only key in the client is the Supabase **publishable**
  key, which is safe by design (RLS).

## Running against your own Supabase (optional)

If you'd rather not share the production backend:

1. Create a free project at supabase.com.
2. In `src/app_template.html`, set `SUPABASE_URL` and `SUPABASE_KEY` to your
   project's URL and publishable/anon key.
3. Enable email auth and create a `leaderboard` table:
   ```sql
   create table public.leaderboard (
     id text primary key,
     username text,
     stats jsonb,
     updated_at timestamptz default now()
   );
   alter table public.leaderboard enable row level security;
   create policy "read all"  on public.leaderboard for select to authenticated using (true);
   create policy "own write" on public.leaderboard for insert to authenticated with check (auth.uid()::text = id);
   create policy "own update" on public.leaderboard for update to authenticated using (auth.uid()::text = id);
   ```
4. Add your local/preview URL to the project's allowed redirect URLs.

## Questions

Open an issue or ping the owner. Keep PRs focused and small where you can — easier
to review, faster to merge.
