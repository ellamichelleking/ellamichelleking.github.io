# ellaking.org

Personal website of Ella King. Content lives in `content/` as YAML and is
built into static pages by `build.py`. Research detail and recruiting live on
the [King Group site](https://kinggroup.northwestern.edu/); this site is the
personal profile (bio, CV, publications, news and events).

- `content/` - everything editable (see `UPDATING.md`)
- `assets/` - CSS, JS, images, CV
- `build.py` - regenerates the pages at the repo root
- `scholar_sync.py` - adds new papers from Google Scholar
- `*.html`, `sitemap.xml`, `robots.txt` - generated; don't edit by hand
- `.github/workflows/update.yml` - syncs, rebuilds and commits every Monday
  and on every push
- `images/` - files from the old site, no longer used; safe to delete

To edit the site, see **`UPDATING.md`**.
