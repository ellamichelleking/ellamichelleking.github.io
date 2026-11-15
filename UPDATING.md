# Updating ellaking.org

You don't edit HTML. Everything comes from the plain-text files in
**`content/`**. Edit those (on GitHub or locally) and push; a GitHub Action
rebuilds the pages and publishes them within a couple of minutes.

## Where things live

| To change… | Edit this file |
|---|---|
| Name, title, homepage pitch and research description, links, contact | `content/site.yml` |
| Bio, positions, honors, teaching, outreach | `content/bio.yml` |
| Talks, press, awards, news | `content/news.yml` |
| Selected work (the image cards) | `content/highlights.yml` |
| The publication list | `content/publications.yml` (new papers arrive automatically) |
| CV | replace `assets/king-cv.pdf` (keep the file name) |
| Headshot | replace `assets/img/ella-king.jpg` |
| Colours | the `:root` block at the top of `assets/css/style.css` |

## Publications: automatic from Google Scholar

Every Monday the Action checks your Google Scholar profile and adds any paper
that isn't in `content/publications.yml` yet to the top of that file.
Existing entries are never touched, so your co-first-author marks, Editor's
Suggestion badges and journal links are safe.

**One-time setup** (about two minutes):
1. Create a free key at <https://serpapi.com/> and copy your API key.
2. In this repo on GitHub: **Settings → Secrets and variables → Actions → New
   repository secret**. Name it `SERPAPI_KEY`, paste the key, save.

Until the key is added, the site keeps the current list and nothing breaks.

Things to know:
- Scholar gives abbreviated authors ("EM King, …") and links to its own page.
  A new paper shows up that way first; tidy the entry in `publications.yml`
  whenever you like:
  ```yaml
  - authors: "King, E. M.*, Coauthor, A. B."
    title: The title of the paper
    venue: Journal Name 1, 234567
    year: 2026
    editor_suggestion: true     # optional badge
    link: https://doi.org/...    # optional
  ```
  (`*` marks co-first authors, `†` corresponding; your name is bolded
  automatically.)
- To keep something on Scholar off the site (a thesis, a duplicate), add its
  title to `scholar_exclude:` in `content/site.yml`. Deleting it from
  `publications.yml` alone isn't enough; it would be added back.
- To run the sync right now: **Actions → Update site → Run workflow**.

## Common tasks

**Add a talk, press item or award** - anywhere in `content/news.yml`:
```yaml
- date: 2027-03-15          # or just 2027-03
  kind: talk                # talk | press | award | news | service
  title: Title of the talk
  where: APS March Meeting, Denver, CO (invited talk)
  url: https://...          # optional
```
Future dates are listed under "Upcoming" and move down by themselves once
they have passed.

**Feature a paper with an image** - add to `content/highlights.yml` and put
the image in `assets/img/work/`.

## Working locally (optional)

The Action commits rebuilt pages back to the repo, so run `git pull` before
you start editing.

```bash
pip install pyyaml
python3 build.py
python3 -m http.server 8000     # then open http://localhost:8000
```
