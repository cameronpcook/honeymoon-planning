# Honeymoon Dossier

A static site with all 13 destination options, built for GitHub Pages. No build step, no dependencies — just HTML/CSS files.

## Deploy to GitHub Pages (about 5 minutes)

1. Create a new repository on GitHub (public repos get free Pages hosting; private repos need a paid plan for Pages).
2. Upload everything in this folder to the repo — `index.html`, `styles.css`, `.nojekyll`, and the `destinations/` folder — keeping the same structure. Easiest way: on the repo's GitHub page, click **Add file → Upload files**, drag in all of it, and commit.
3. Go to **Settings → Pages** in the repo.
4. Under **Build and deployment → Source**, choose **Deploy from a branch**.
5. Under **Branch**, choose `main` and `/ (root)`, then **Save**.
6. GitHub will give you a URL like `https://yourusername.github.io/repo-name/` within a minute or two — that's the link to share.

## Editing later

- All destination content lives in `build.py` as plain Python data (not included in this export — ask me to regenerate if you want an edit, or just hand-edit the HTML files directly, they're plain and unminified).
- `styles.css` controls the whole look — one file, easy to tweak colors/fonts.
- Each destination page is fully self-contained in `destinations/<slug>.html`.

## Photos

Photos are self-hosted under `images/<destination>/` instead of hotlinked, so
pages load fast and don't depend on an external site staying up.

Fetching is automatic — no terminal needed. Each destination has an
`images/<destination>/manifest.json` mapping local filename → source URL
(currently just `images/italy/manifest.json`). The
**Fetch destination images** GitHub Action (`.github/workflows/fetch-images.yml`)
reads every manifest, downloads each image, resizes it to a max of 1600px and
re-compresses it as an optimized progressive JPEG (`scripts/fetch_images.py`,
stripping EXIF data too), and commits the result straight to the branch:

- It runs automatically whenever a manifest (or the fetch script) changes and
  gets pushed.
- You can also trigger it by hand from the repo's **Actions** tab →
  **Fetch destination images** → **Run workflow** — this works fine from
  Safari on an iPad, no terminal required.

Adding photos to a new destination is just adding its
`images/<slug>/manifest.json` and pointing that page's `<img>` tags at
`../images/<slug>/<filename>` — the workflow picks up new manifests
automatically, no workflow changes needed.
