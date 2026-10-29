# Adaptive Structures Lab website

This folder is the whole website. Text lives in `content/`, photos and videos in `assets/`.
`build.py` turns them into the finished site (you don't need to touch it).

---

## Editing the site

All text is in plain-text `.yaml` files. Open them in any text editor (or directly on GitHub, see below).

| To change… | Edit this file |
|---|---|
| Menu, footer, home page "About us", contact page | `content/site.yaml` |
| People (add / remove / bios / links) | `content/team.yaml` |
| Papers | `content/publications.yaml` |
| Research page intro, the two halves, bubbles, project order | `content/research.yaml` |
| One research project (card + its page) | `content/projects/<project>.yaml` |

**Formatting inside text:** `*italic*`, `**bold**`, `[link text](https://…)`.
Links to pages on this site start with `/`, e.g. `[Contact](/contact/)`.

**YAML tips:** keep the indentation (spaces, not tabs). If a line contains a colon followed by a space, put the text in quotes: `heading: "Kirigami d’Aria: exhibition"`.

### Common tasks
- **Add a paper:** copy a block in `publications.yaml` to the top of `papers:` and edit it. Your name is bolded automatically.
- **Add a person:** copy a block in `team.yaml`. Put a square photo in `assets/img/team/` and write its file name after `photo:`.
- **Move someone to alumni:** add `alum: true` to their block.
- **New research project:** copy `content/projects/_TEMPLATE.yaml` to `content/projects/my-project.yaml`, fill it in, put a square card image in `assets/img/cards/`, and add `my-project` to a group in `research.yaml`. Use `coming_soon: true` for a card without a page.
- **Change tags/bubbles:** edit `tags:` in the project file (keys are listed at the top of `research.yaml`).

### Photos & videos
- Photos: JPG, ideally under ~1 MB (about 1600 px wide is plenty).
- Videos: MP4, ideally under ~15 MB. Large videos can be shrunk with
  `python3 tools/prepare_media.py <original> assets/media/<project>/<name>` (needs ffmpeg) — or ask Claude.
- GitHub rejects single files over 100 MB.

---

## Publishing (GitHub Pages, free)

### One-time setup
1. Create a free account at github.com (if you don't have one).
2. Click **New repository** → name it e.g. `adaptivestructureslab` → **Public** → Create.
3. On the new repo page click **uploading an existing file**, then drag in **everything inside this `site` folder**
   (including the hidden `.github` folder — on a Mac press **Cmd+Shift+.** in Finder to show hidden files).
   Commit. (All files are under GitHub's 25 MB browser-upload limit; ~80 files total.)
   *(Alternative that handles hidden files and big uploads more easily: install **GitHub Desktop**, choose
   "Add existing repository" → this `site` folder → Publish.)*
4. Repo → **Settings → Pages** → under "Build and deployment", set **Source: GitHub Actions**.
5. Repo → **Actions** tab: you'll see "Build and deploy site" run (≈1 minute). When it's green, the site is live at
   `https://<your-username>.github.io/adaptivestructureslab/`. Check it there before switching the domain.

### Point adaptivestructureslab.com at it
6. Repo → **Settings → Pages → Custom domain**: type `adaptivestructureslab.com` → Save.
   (The `CNAME` file in this folder already contains it.)
7. At the company where you bought the domain (your registrar), open **DNS settings** and set:

   | Type | Name/Host | Value |
   |---|---|---|
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | `<your-username>.github.io` |

   Delete any old **A** or **CNAME** records for `@`/`www` that point to the WordPress host.
   **Don't touch MX/TXT records** (those are for email/verification).
8. Wait (minutes to a few hours). Back in **Settings → Pages**, tick **Enforce HTTPS** once it's offered.
9. When the new site is working on your domain, you can cancel the WordPress hosting
   (download anything you still want from it first).

### Making changes after launch
- **On GitHub:** open a file (e.g. `content/team.yaml`) → pencil icon → edit → **Commit changes**.
  The site rebuilds itself in about a minute. To add a photo: open the folder (e.g. `assets/img/team`) → **Add file → Upload files**.
- **Or with Claude:** ask Claude in a Cowork session on this Dropbox folder to make the change, then upload the changed files to GitHub
  (or, with GitHub Desktop, just click **Commit** and **Push**).

Old WordPress addresses keep working: `/team/`, `/research/`, `/publications/`, `/contact/`, and the project pages
(`/kirigami-for-urban-ventilation/`, `/interactive-shading/`, …). `/news-events/` redirects to the home page.

---

## Previewing on your computer (optional)
Needs Python 3 with PyYAML (`pip3 install pyyaml`):
```
cd site
python3 build.py --preview
open _site/index.html
```
`--preview` makes links work when opening files directly. (Videos/fonts may not load in some browsers from local files; they will online.)
