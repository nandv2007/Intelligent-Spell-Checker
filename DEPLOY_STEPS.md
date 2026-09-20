# Deploy to Render — Exact Steps (no token needed)

## 1. Create GitHub repo (2 min)

On your laptop (or in this workspace):

```bash
cd spellchecker   # this folder
# already a git repo on main; just push it
```

1. Go to https://github.com/new
   - Repository name: `intelligent-spell-checker` (any name)
   - Visibility: Public
   - **Do NOT** check “Add a README” — leave empty
   - Click **Create repository**

2. GitHub will show a “push an existing repository” block. Copy the two lines and run:

```bash
git remote add origin https://github.com/<YOUR_USERNAME>/intelligent-spell-checker.git
git push -u origin main
```

Replace `<YOUR_USERNAME>` with your GitHub username.

> If `origin` already exists, run `git remote set-url origin https://github.com/<YOUR_USERNAME>/intelligent-spell-checker.git` then push.

## 2. Deploy on Render (3 min)

1. Go to https://dashboard.render.com
   - Sign in with GitHub (allows Render to see your repo)

2. Click **New +** → **Web Service** → **Connect** your `intelligent-spell-checker` repo.

3. Render auto-reads `render.yaml`. Verify these settings:
   - Name: `intelligent-spell-checker`
   - Environment: `Python 3`
   - Region: any (Singapore is closest to Chennai)
   - Branch: `main`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
   - Plan: `Free`

4. Click **Create Web Service**.
   - Build takes ~60 s, then **Live** with a URL like `https://intelligent-spell-checker.onrender.com`
   - Health check is `GET /api/health` — Render shows “Healthy” when ready.

5. Open the URL → demo same as local preview.

## 3. Update after changes

```bash
git add .
git commit -m "update"
git push
```
Render redeploys automatically (~60 s).

## Notes

- No database, no env vars, no API keys.
- Free plan sleeps after 15 min of inactivity; first request after sleep takes ~30 s to wake (normal on Render).
- If wake is slow during review, hit the URL 1 minute before presenting.

## Troubleshooting

- **Build failed → pip** — ensure `requirements.txt` has `Flask==3.1.0` and `gunicorn==23.0.0` (already set).
- **404 on refresh** — Flask serves `/` via `templates/index.html`, no extra config needed.
- **Dictionary not found** — Render runs from repo root, paths are `data/dictionary.txt` (already correct).

You’re done. Show ma’am the live Render URL + walk through `dsa/` code.
