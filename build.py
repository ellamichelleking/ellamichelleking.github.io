#!/usr/bin/env python3
"""Build ellaking.org from the YAML files in content/.

Usage:  python3 build.py        # rewrites the .html pages at the repo root
Edit the files in content/ to change the site, then run this script.
Needs only PyYAML (pip install pyyaml).
"""
import datetime, html, json, os, re, yaml

ROOT    = os.path.dirname(os.path.abspath(__file__))
CONTENT = os.path.join(ROOT, "content")

def load(name):
    with open(os.path.join(CONTENT, name), encoding="utf-8") as fh:
        return yaml.safe_load(fh) or []

SITE  = load("site.yml")
TODAY = datetime.date.today()
PAGES = [("index.html", "Home"), ("bio.html", "Bio"),
         ("publications.html", "Publications"), ("news.html", "News & Events")]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def esc(s):    return html.escape(str(s), quote=False)
def escurl(u): return html.escape(str(u), quote=True)
def ext(u):    return ' rel="noopener"' if str(u).startswith("http") else ""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?'
         'family=Fraunces:ital,opsz,wght@0,9..144,400..600;1,9..144,400..500&'
         'family=Hanken+Grotesk:wght@400;500;600;700&'
         'family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">')

def scholar_url():
    for l in SITE["links"]:
        if "scholar" in l["url"]:
            return l["url"]
    return ""

# ---------------------------------------------------------------- SHELL
def head(title, desc, active, fname, extra=""):
    on = ' class="active" aria-current="page"'
    nav = "\n".join(
        f'    <li><a href="{f}"{on if n == active else ""}>{esc(n)}</a></li>'
        for f, n in PAGES)
    canonical = SITE["url"].rstrip("/") + "/" + ("" if fname == "index.html" else fname)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{escurl(desc)}">
<link rel="canonical" href="{escurl(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{escurl(title)}">
<meta property="og:description" content="{escurl(desc)}">
<meta property="og:url" content="{escurl(canonical)}">
<meta property="og:image" content="{escurl(SITE['url'].rstrip('/') + '/' + SITE['headshot'])}">
{FONTS}
<link rel="stylesheet" href="assets/css/style.css">
<link rel="icon" type="image/svg+xml" href="assets/img/favicon.svg">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<nav class="nav"><div class="nav-in">
  <a class="brand" href="index.html">{esc(SITE['name'])}</a>
  <button class="nav-toggle" aria-expanded="false" aria-controls="navlinks">Menu</button>
  <ul class="nav-links" id="navlinks">
{nav}
    <li><a href="{escurl(SITE['cv'])}">CV</a></li>
    <li><a class="nav-group" href="{escurl(SITE['group_url'])}">{esc(SITE['group_name'])} <span aria-hidden="true">&nearr;</span></a></li>
  </ul>
</div></nav>
<main id="main">
"""

def footer():
    links = "\n    ".join(
        f'<a href="{escurl(l["url"])}"{ext(l["url"])}>{esc(l["name"])}</a>'
        for l in SITE["links"])
    return f"""</main>
<footer class="footer"><div class="wrap footer-in">
  <div>
    <p class="brand">{esc(SITE['name'])}</p>
    <p>{esc(SITE['role'])}, {esc(SITE['institution'])}</p>
    <p><a href="mailto:{esc(SITE['email'])}">{esc(SITE['email'])}</a></p>
    <p>{esc(SITE['address'])}</p>
  </div>
  <div class="fcol">
    <a href="{escurl(SITE['group_url'])}">{esc(SITE['group_name'])} website</a>
    {links}
  </div>
</div>
<div class="wrap colophon">&copy; {TODAY.year} {esc(SITE['name'])}</div>
</footer>
<script src="assets/js/site.js"></script>
</body>
</html>
"""

def page(fname, title, desc, active, body, extra=""):
    with open(os.path.join(ROOT, fname), "w", encoding="utf-8") as fh:
        fh.write(head(title, desc, active, fname, extra) + body + footer())

# ---------------------------------------------------------------- PIECES
def highlight_authors(s):
    s = esc(s)
    for name in SITE.get("author_highlight", []):
        e = esc(name)
        s = s.replace(e, f'<span class="me">{e}</span>')
    return s

def venue_html(v):
    m = re.match(r"^(\D+?)\s*(\d.*)$", str(v))
    if m:
        return f'<span class="j">{esc(m.group(1).strip())}</span> {esc(m.group(2))}'
    return f'<span class="j">{esc(v)}</span>'

def pub_row(p):
    link = p.get("link")
    title = (f'<a class="pub-title" href="{escurl(link)}"{ext(link)}>{esc(p["title"])}</a>'
             if link else f'<p class="pub-title">{esc(p["title"])}</p>')
    badge = ('<span class="badge">Editor&rsquo;s Suggestion</span>'
             if p.get("editor_suggestion") else "")
    venue = f'<p class="venue">{venue_html(p["venue"])} {badge}</p>' if p.get("venue") else ""
    return f"""    <li class="pub">
      <span class="y">{esc(p.get('year', ''))}</span>
      <div>
        {title}
        <p class="authors">{highlight_authors(p.get('authors', ''))}</p>
        {venue}
      </div>
    </li>"""

def card(h):
    return f"""    <a class="card" href="{escurl(h['url'])}"{ext(h['url'])}>
      <div class="card-img"><img src="{escurl(h['image'])}" alt="" loading="lazy"></div>
      <div class="card-body">
        <p class="card-venue">{esc(h.get('venue', ''))}</p>
        <h3>{esc(h['title'])}</h3>
        <p>{esc(h['desc'])}</p>
      </div>
    </a>"""

def news_date(n):
    """Return (sortable date, display string) for a news item."""
    parts = [int(x) for x in str(n["date"]).split("-")]
    y, m = parts[0], (parts[1] if len(parts) > 1 else 1)
    d = parts[2] if len(parts) > 2 else None
    label = f"{MONTHS[m - 1]} {d}, {y}" if d else f"{MONTHS[m - 1]} {y}"
    # A month-only date stops counting as upcoming once its month begins.
    last = d or 1
    return datetime.date(y, m, d or 1), datetime.date(y, m, last), label

KIND = {"talk": "Talk", "press": "Press", "award": "Award", "news": "News", "service": "Service"}

def news_row(n):
    _, _, label = news_date(n)
    kind = n.get("kind", "news")
    title = esc(n["title"])
    if n.get("url"):
        title = f'<a href="{escurl(n["url"])}"{ext(n["url"])}>{title}</a>'
    where = f'<p class="where">{esc(n["where"])}</p>' if n.get("where") else ""
    return f"""    <li class="news-item">
      <span class="d">{esc(label)}</span>
      <div>
        <p class="t"><span class="kind kind-{esc(kind)}">{KIND.get(kind, 'News')}</span>{title}</p>
        {where}
      </div>
    </li>"""

def sorted_news():
    news = sorted(load("news.yml"), key=lambda n: news_date(n)[0], reverse=True)
    upcoming = [n for n in news if news_date(n)[1] >= TODAY]
    past     = [n for n in news if news_date(n)[1] < TODAY]
    return upcoming[::-1], past      # upcoming soonest-first, past newest-first

# ---------------------------------------------------------------- HOME
def build_home():
    research = "\n".join(f"    <p>{esc(' '.join(p.split()))}</p>" for p in SITE["research"])
    pubs = load("publications.yml")[:int(SITE.get("home_papers", 4))]
    upcoming, past = sorted_news()
    news = (upcoming + past)[:int(SITE.get("home_news", 4))]
    depts = " and ".join(esc(d) for d in SITE["departments"])
    links = "\n      ".join(
        f'<a class="btn ghost small" href="{escurl(l["url"])}"{ext(l["url"])}>{esc(l["name"])}</a>'
        for l in SITE["links"])
    person = {
        "@context": "https://schema.org", "@type": "Person",
        "name": SITE["name"], "url": SITE["url"], "email": SITE["email"],
        "jobTitle": SITE["role"],
        "affiliation": {"@type": "CollegeOrUniversity", "name": SITE["institution"]},
        "image": SITE["url"].rstrip("/") + "/" + SITE["headshot"],
        "sameAs": [SITE["group_url"]] + [l["url"] for l in SITE["links"]],
    }
    extra = f'<script type="application/ld+json">{json.dumps(person)}</script>\n'
    body = f"""
<section class="hero"><div class="wrap hero-grid">
  <div class="hero-copy">
    <p class="eyebrow">{esc(SITE['role'])} &middot; {esc(SITE['institution'])}</p>
    <h1>{esc(SITE['name'])}</h1>
    <p class="lead">{esc(SITE['pitch'])}</p>
    <p class="depts">{depts}</p>
    <div class="btn-row">
      <a class="btn" href="bio.html">Bio</a>
      <a class="btn ghost" href="{escurl(SITE['cv'])}">CV</a>
      <a class="btn ghost" href="mailto:{esc(SITE['email'])}">Email</a>
    </div>
    <div class="btn-row links">
      {links}
    </div>
  </div>
  <div class="hero-photo">
    <img src="{escurl(SITE['headshot'])}" width="900" height="990" alt="Portrait of {esc(SITE['name'])}">
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2>Research</h2></div>
  <div class="prose research">
{research}
  </div>
  <div class="btn-row">
    <a class="btn" href="{escurl(SITE['group_url'])}">{esc(SITE['group_name'])} <span class="arr">&rarr;</span></a>
  </div>
</div></section>

<section class="section"><div class="wrap two-col">
  <div>
    <div class="section-head"><h2>News &amp; events</h2>
      <a class="more" href="news.html">All &rarr;</a></div>
    <ul class="news compact">
{chr(10).join(news_row(n) for n in news)}
    </ul>
  </div>
  <div>
    <div class="section-head"><h2>Recent papers</h2>
      <a class="more" href="publications.html">All &rarr;</a></div>
    <ul class="pub-list compact">
{chr(10).join(pub_row(p) for p in pubs)}
    </ul>
  </div>
</div></section>
"""
    page("index.html", f"{SITE['name']} · {SITE['institution']}",
         " ".join(SITE["pitch"].split()), "Home", body, extra)

# ---------------------------------------------------------------- BIO
def build_bio():
    bio = load("bio.yml")
    def rows(items):
        out = []
        for i in items:
            what = esc(i["what"])
            if i.get("url"):
                what = f'<a href="{escurl(i["url"])}"{ext(i["url"])}>{what}</a>'
            when = f'<span class="d">{esc(i["when"])}</span>' if i.get("when") else ""
            detail = f'<p class="where">{esc(i["detail"])}</p>' if i.get("detail") else ""
            cls = "tl-item" if when else "tl-item nodate"
            out.append(f'    <li class="{cls}">{when}<div><p class="t">{what}</p>{detail}</div></li>')
        return "\n".join(out)
    paras = [esc(" ".join(p.split())) for p in bio["bio"]]
    bio_html = "\n".join(f"      <p>{p}</p>" for p in paras)
    body = f"""
<section class="page-head"><div class="wrap"><h1>Bio</h1></div></section>

<section class="section tight"><div class="wrap bio-grid">
  <div class="prose">
{bio_html}
  </div>
  <aside class="bio-side">
    <img src="{escurl(SITE['headshot'])}" width="900" height="990" alt="Portrait of {esc(SITE['name'])}">
    <a class="btn ghost" href="{escurl(SITE['cv'])}">Full CV</a>
  </aside>
</div></section>

<section class="section"><div class="wrap two-col">
  <div>
    <div class="section-head"><h2>Positions &amp; education</h2></div>
    <ul class="tl">
{rows(bio['positions'])}
    </ul>
  </div>
  <div>
    <div class="section-head"><h2>Honors</h2></div>
    <ul class="tl">
{rows(bio['honors'])}
    </ul>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2>Teaching</h2></div>
  <ul class="tl">
{rows(bio['teaching'])}
  </ul>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2>Service &amp; outreach</h2></div>
  <ul class="tl wide">
{rows(bio['service'])}
  </ul>
</div></section>
"""
    page("bio.html", f"Bio · {SITE['name']}",
         " ".join(bio["bio"][0].split()), "Bio", body)

# ---------------------------------------------------------------- PUBLICATIONS
def build_publications():
    pubs = load("publications.yml")
    highlights = sorted(load("highlights.yml"), key=lambda h: str(h.get("date", "")), reverse=True)
    body = f"""
<section class="page-head"><div class="wrap"><h1>Publications</h1>
  <p class="sub">Complete list of work can also be found at my <a href="{escurl(scholar_url())}" rel="noopener">Google Scholar page</a>.</p>
</div></section>

<section class="section tight"><div class="wrap">
  <div class="section-head"><h2>Selected work</h2></div>
  <div class="cards">
{chr(10).join(card(h) for h in highlights)}
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><h2>All publications and preprints</h2></div>
  <ul class="pub-list">
{chr(10).join(pub_row(p) for p in pubs)}
  </ul>
  <p class="legend">* co-first author &nbsp;&middot;&nbsp; &dagger; corresponding author</p>
</div></section>
"""
    page("publications.html", f"Publications · {SITE['name']}",
         f"Publications and preprints by {SITE['name']}.", "Publications", body)

# ---------------------------------------------------------------- NEWS
def build_news():
    upcoming, past = sorted_news()
    up_html = ""
    if upcoming:
        up_html = f"""
<section class="section tight"><div class="wrap">
  <div class="section-head"><h2>Upcoming</h2></div>
  <ul class="news">
{chr(10).join(news_row(n) for n in upcoming)}
  </ul>
</div></section>
"""
    years = {}
    for n in past:
        years.setdefault(news_date(n)[0].year, []).append(n)
    past_html = "\n".join(f"""  <div class="section-head"><h2>{y}</h2></div>
  <ul class="news">
{chr(10).join(news_row(n) for n in items)}
  </ul>""" for y, items in years.items())
    body = f"""
<section class="page-head"><div class="wrap"><h1>News &amp; Events</h1></div></section>
{up_html}
<section class="section{'' if upcoming else ' tight'}"><div class="wrap">
{past_html}
</div></section>
"""
    page("news.html", f"News & Events · {SITE['name']}",
         f"Talks, press, and recognition for {SITE['name']}.", "News & Events", body)

# ---------------------------------------------------------------- EXTRAS
def build_extras():
    base = SITE["url"].rstrip("/")
    urls = "\n".join(
        f"  <url><loc>{base}/{'' if f == 'index.html' else f}</loc>"
        f"<lastmod>{TODAY.isoformat()}</lastmod></url>" for f, _ in PAGES)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 f"{urls}\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n")
    body = """
<section class="page-head"><div class="wrap"><h1>Page not found</h1>
  <p class="sub">This page may have moved. Try the <a href="/">homepage</a>.</p>
</div></section>
"""
    html404 = head(f"Page not found · {SITE['name']}", "Page not found.", "", "404.html") \
        + body + footer()
    # The 404 page can be served from any path, so its links must be absolute.
    html404 = re.sub(r'(href|src)="(?!https?:|mailto:|/|#)', r'\1="/', html404)
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as fh:
        fh.write(html404)

def main():
    build_home(); build_bio(); build_publications(); build_news(); build_extras()
    print("Built:", ", ".join(f for f, _ in PAGES), "+ 404.html, sitemap.xml, robots.txt")

if __name__ == "__main__":
    main()
