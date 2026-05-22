# Zeolite Ring

Interactive 3D explorer for zeolite framework topologies — 263 IZA-style structures with 5-member and 6-member ring visualization. Built for materials research spanning molecular sieves, catalysis, and battery electrolyte design.

**Live site:** Deploy via [Cloudflare Pages](https://pages.cloudflare.com/) (see below).

## Features

- Landing page with molecular-sieve hero animation
- Supabase authentication (Google OAuth, email/password, magic link)
- Three.js viewer with ring highlighting, unit-cell expansion, and PNG export
- Precomputed static topology JSON — no backend required in production

## Project Structure

```
landing.html          Public landing + login
viewer.html           Authenticated 3D viewer
index.html            Redirects to landing.html
assets/
  css/landing.css     Landing page styles
  js/auth.js          Supabase auth helpers
  js/config.js        Supabase URL + anon key (edit this)
  js/landing.js       Landing interactions
data/topology/        Precomputed JSON per framework (264 files)
all-cif/              Source CIF files
scripts/
  build_topology.py   Batch-generate data/topology/*.json
  dev_server.py       Optional local dev server with POST /process
process_topology.py   Single-CIF topology processor
```

## Local Development

### Static preview (recommended)

Serve the repo root with any static file server:

```bash
python3 -m http.server 8080
# open http://localhost:8080/landing.html
```

Without Supabase configured, auth is skipped and the viewer opens directly.

### Regenerate topology JSON

Requires Python 3.11+ with pymatgen:

```bash
pip install -r scripts/requirements.txt
python3 scripts/build_topology.py
```

This writes one JSON file per CIF into `data/topology/`.

### Legacy dev server (optional)

```bash
python3 scripts/dev_server.py
```

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. **Authentication → Providers**
   - Enable **Google** (add OAuth client ID/secret from Google Cloud Console)
   - Enable **Email** (password + magic link)
3. **Authentication → URL Configuration**
   - Site URL: your Cloudflare Pages URL (e.g. `https://zeolite-ring.pages.dev`)
   - Redirect URLs: add `https://your-domain/viewer.html`
4. Copy **Project URL** and **anon public key** into `assets/js/config.js`:

```javascript
window.__SUPABASE_CONFIG__ = {
  url: "https://xxxx.supabase.co",
  anonKey: "eyJhbGciOi...",
};
```

## Cloudflare Workers Deployment (GitHub → auto deploy)

This repo uses **Cloudflare Workers static assets** via `wrangler.jsonc`. Each push to `main` triggers:

1. `npx wrangler deploy` (no Python build step)
2. Static files served from repo root (`landing.html`, `viewer.html`, `assets/`, `data/`, `paper/`)

**Build settings in Cloudflare Dashboard:**

- **Production branch:** `main`
- **Build command:** `npx wrangler deploy`
- **Python dependencies:** none at deploy time (`requirements.txt` lives under `scripts/` for local dev only)

5. Optional custom domain: Workers project → **Custom domains** → `zeolitering.com`

### Post-deploy checklist

- [ ] Update Supabase Site URL + redirect URLs with your Pages domain
- [ ] Update Google OAuth authorized redirect URIs in Google Cloud Console
- [ ] Fill in `assets/js/config.js` with real Supabase credentials
- [ ] Push to GitHub

## Google OAuth (for Supabase)

In [Google Cloud Console](https://console.cloud.google.com/):

1. Create OAuth 2.0 Client ID (Web application)
2. Authorized JavaScript origins: `https://your-pages-domain.pages.dev`
3. Authorized redirect URIs: `https://xxxx.supabase.co/auth/v1/callback`
4. Paste Client ID and Secret into Supabase → Authentication → Google

## License

Research and educational use. CIF data follows IZA framework conventions.
