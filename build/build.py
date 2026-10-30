"""Build the Experiential Learning staging site on the Northeastern Design System (NUEAC-413).

Content is the live experientiallearning.northeastern.edu content (scraped into build/content.json). Each page follows a band plan
from the system's templates (Unit home, Section hub): a Night opener, Canvas chapters, at most one Night feature, then the footers.
The page shell comes from ~/Projects/nu-site-kit.
    python3 build/build.py            # writes docs/
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Projects/nu-site-kit"))
from kit import DS, Site, _block, breadcrumb, e, facet_chips, finder, hero_title, href, i, img, not_found, section_header  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "build/content.json").read_text())
LIVE = "https://experientiallearning.northeastern.edu/"
UNIT = "Experiential Learning"
IMG = ROOT / "docs/assets/img"
P = {p["slug"]: p for p in C["pages"]}
# Logo names exist only inside the images; the crawl read them off.
LOGO_NAMES = {}
for p in C["pages"]:
    for s in p.get("sections", []):
        for it in s.get("items", []):
            if isinstance(it, dict) and it.get("textInImage"):
                LOGO_NAMES[it["file"]] = it["textInImage"]
# Statement lines hold two lines at most (about 90 characters). Where a live opening sentence runs longer, staging shows the cut the
# design system's own Statement spec makes: words removed, none added. Listed in the README for the owner to approve.
CUTS = {"We help organizations of all sizes and across industries discover solutions that fill skills gaps and drive business decisions.":
        "We help organizations of all sizes discover solutions that fill skills gaps."}


def cut(s):
    return CUTS.get(s, s)


# Published typos corrected on staging (listed in the README).
FIXES = {"WHat is": "What is", "study at one our global": "study at one of our global"}


def fix(s):
    for a, b in FIXES.items():
        s = s.replace(a, b)
    return s


def sc(s):
    """Sentence case for labels the live site sets in caps or lowercase."""
    s = fix(s or "").strip()
    if s.isupper() or s.islower():
        s = s.lower()
        s = s[:1].upper() + s[1:]
    return s.replace("Ai ", "AI ")


def local(u):
    """Live URL → site-relative target; everything off-site stays absolute."""
    if not u:
        return "#"
    if u.startswith(LIVE):
        u = u[len(LIVE):]
        return u.split("#")[0] + ("#" + u.split("#")[1] if "#" in u and u.split("#")[1] else "") or ""
    return u


def external(u):
    return u.startswith("http") and not u.startswith(LIVE)


def file(img_rec):
    return img_rec["file"].split("/", 1)[1]


def secs(slug, kind=None, heading=None):
    out = [s for s in P[slug]["sections"] if (kind is None or s["type"] == kind)]
    if heading:
        out = [s for s in out if heading in (s.get("heading") or "") or heading in (s.get("eyebrow") or "")]
    return out


def sec(slug, kind=None, heading=None, n=0):
    return secs(slug, kind, heading)[n]


NAV = [("Overview", [("Experiential learning defined", "experiential-learning-defined/"),
                     ("Global experiential network", "experiential-learning-defined/global-experiential-network/")]),
       ("Experiential opportunities", [("All opportunities", "experiential-opportunities/"), ("Academic", "experiential-opportunities/academic/"),
                                       ("Professional", "experiential-opportunities/professional/"), ("Extracurricular", "experiential-opportunities/extracurricular/")]),
       ("Employer partnerships", [("Partnerships", "partnerships/"), ("Employer opportunities", "partnerships/employer/")]),
       ("Search", "search-experiential/")]
PATHWAYS = [("Academic", "experiential-opportunities/academic/"), ("Professional", "experiential-opportunities/professional/"),
            ("Extracurricular", "experiential-opportunities/extracurricular/")]
cols = C["site"]["localFooter"]["linkColumns"]
site = Site(ROOT, UNIT, "experientiallearning-staging", "experientiallearning.northeastern.edu", NAV,
            [("Experiential learning", [(sc(l["text"]) if l["text"].isupper() else l["text"], l["href"]) for l in cols[0]]),
             ("Research and PhD", [(l["text"], l["href"]) for l in cols[1]]),
             ("More at Northeastern", [(l["text"], l["href"]) for l in cols[2]])])
HOME = [(UNIT, "")]
VH_SITE = '<span class="u-vh">, on another site</span>'
VH_OTHER = '<span class="u-vh"> (on another site)</span>'
CURP = ' aria-current="page"'


def body_p(b):
    return f'<p class="nu-text nu-point-list__body">{b}</p>' if b else ""


# ---------- system compositions ----------
def arrow(text, url, cls="nu-arrow-link"):
    ext = external(url)
    return (f'<a class="{cls}{" nu-arrow-link--external" if ext else ""}" href="{href(local(url))}">{e(text)}'
            f'{VH_SITE if ext else ""} {i("external" if ext else "arrow")}</a>')


def actions(buttons):
    """One primary Button, then ArrowLinks (MediaText's rule: never two pills)."""
    out = []
    for n, b in enumerate(b for b in (buttons or []) if b.get("href") and not b.get("hiddenOnSite") and b.get("text", "").lower() != "load more"):
        if n == 0:
            out.append(f'<a class="nu-button" href="{href(local(b["href"]))}">{e(sc(b["text"]))} {i("arrow")}</a>')
        else:
            out.append(arrow(sc(b["text"]), b["href"]))
    return "".join(out)


def hero(h1, image, size="tall", focus="50% 50%", phone="50% 40%", crumbs=None, lead=None, button=None, figure=None, here=None):
    """HeroPage, stacked on phones (el-10): tall for hubs, medium for their children, display for the unit's home (el-05)."""
    mod = {"display": " nu-hero-page--display", "medium": " nu-hero-page--medium", "tall": ""}[size]
    hcls = {"display": "display-xl", "tall": "display", "medium": "h1"}[size]
    bc = breadcrumb(crumbs, here or h1) if crumbs else ""
    fig = f'<img class="st-hero__figure" src="{{{{base}}}}assets/img/{figure[0]}" alt="{e(figure[1])}">' if figure else ""
    btn = f'<a class="nu-button" href="{href(button[1])}">{e(button[0])} {i("arrow")}</a>' if button else ""
    return f'''<section class="nu-hero-page nu-hero-page--stack{mod} st-hero" data-mode="dark">
  <div class="nu-hero-page__media" style="--hero-page-focus:{focus};--hero-page-focus-phone:{phone}">
    {img(image, "", "fill")}{fig}
    <span class="nu-scrim nu-scrim--left"></span><span class="nu-scrim nu-scrim--scene"></span><span class="nu-scrim nu-scrim--grain"></span><span class="nu-scrim nu-scrim--full nu-hero-page__phone-scrim"></span>
  </div>
  <div class="nu-hero-page__copy">
    {bc}
    <h1 class="nu-heading nu-heading--{hcls}">{h1}</h1>
    {f'<p class="nu-text nu-text--lead">{lead}</p>' if lead else ""}
    {btn}
  </div>
</section>'''


def band(inner, label=None, cls=""):
    """A Canvas chapter (Section hub band): consecutive chapters share one seam."""
    lab = f' aria-labelledby="{label}"' if label else ""
    return f'<section class="nu-section-hub__band {cls}"{lab}>{inner}</section>'


def statement(line, lead=None, link=None):
    """Statement (el-12): the page's opening line, at most two lines; the rest of the thought as a lead from column 5."""
    body = (f'<p class="nu-text nu-text--lead">{lead}</p>' if lead else "") + (arrow(*link) if link else "")
    return f'''<div class="nu-section-hub__band nu-section-hub__statement"><div class="nu-statement">
  <p class="nu-heading nu-heading--h1 nu-statement__line">{line}</p>
  {f'<div class="nu-statement__body">{body}</div>' if body else ""}
</div></div>'''


def quick_links(slug):
    s = secs(slug, "quick-links")
    if not s:
        return ""
    links = [x[0] for lst in s[0].get("lists", []) for x in lst["items"]]
    lis = "".join(f'<li><a class="nu-in-page-nav__link nu-nav-link" href="{href(local(l["href"]))}">{e(l["text"])}</a></li>' for l in links)
    return f'''<nav class="nu-in-page-nav st-quick" aria-label="Quick links">
  <div class="nu-in-page-nav__inner">
    <p class="nu-text nu-text--label nu-in-page-nav__label">Quick links</p>
    <ul class="nu-in-page-nav__list">{lis}</ul>
  </div>
</nav>'''


def sibling_nav(current):
    """SiblingNav (el-07): the three pathways under the hero, the current one marked."""
    lis = "".join(f'<li><a class="nu-section-nav__link nu-nav-link" href="{href(u)}"{CURP if u == current else ""}>{l}</a></li>' for l, u in PATHWAYS)
    return f'''<div class="el-sibling"><nav class="nu-section-nav nu-section-nav--horizontal" aria-label="Experiential opportunities">
  <p class="nu-text nu-text--meta nu-section-nav__label">Experiential opportunities</p>
  <ul class="nu-section-nav__list">{lis}</ul>
</nav></div>'''


def point_list(items, heading=None, hid=None, numbered=False):
    """PointList (el-06, keep-01): claims as hairline rows on column 5; items are (claim, body or None)."""
    tag = "ol" if numbered else "ul"
    lis = "".join(f'<li class="nu-point-list__item"><h3 class="nu-heading nu-heading--h4 nu-point-list__claim">{c}</h3>'
                  f'{body_p(b)}</li>' for c, b in items)
    head = f'<div class="nu-point-list__head"><h2 class="nu-heading nu-heading--h2" id="{hid}">{heading}</h2></div>' if heading else ""
    el = "section" if heading else "div"
    lab = f' aria-labelledby="{hid}"' if heading else ""
    return f'<{el} class="nu-point-list{" nu-point-list--numbered" if numbered else ""}"{lab}>{head}<{tag} class="nu-point-list__items">{lis}</{tag}></{el}>'


def split_term(item):
    """'Term—Explanation' bullets become a claim and its sentence."""
    term, _, body = fix(item).partition("—")
    return term.strip(), body.strip() or None


def claims_grid(cards, label, four=False):
    """Captioned square photographs, no card chrome (el-08): picture, an h3 at h4 size when there is a title, one sentence."""
    lis = ""
    for c in cards:
        im = c["image"]
        t = f'<h3 class="nu-heading nu-heading--h4">{fix(c["title"])}</h3>' if c.get("title") else ""
        text = c.get("excerpt") or " ".join(c.get("body", []))
        lis += f'<li class="nu-unit-home__claim">{img(file(im), im.get("alt", "") if not im.get("alt", "").startswith(("image (", "Extracurricular 0", "Employer Ops")) else "", "1x1")}{t}<p class="nu-text">{fix(text)}</p></li>'
    return f'<ul class="nu-unit-home__claims-grid{" el-claims--4" if four else ""}" role="list" tabindex="0" aria-label="{e(label)}">{lis}</ul>'


def pathway_cards(cards):
    """PathwayCards (el-02): the hub's three doors, each tile one link, in the order the navigation uses."""
    order = {u: n for n, (_, u) in enumerate(PATHWAYS)}
    cards = sorted(cards, key=lambda c: order.get(local(c["buttons"][0]["href"]), 9))
    lis = "".join(f'''<li><a class="nu-poster-card" href="{href(local(c["buttons"][0]["href"]))}">
  <span class="nu-poster-card__frame" data-mode="dark">{img(file(c["image"]), "", "fill")}<span class="nu-scrim nu-scrim--poster"></span>
    <span class="nu-pathway-cards__body"><span class="nu-pathway-cards__text"><span class="nu-heading nu-heading--h3 nu-pathway-cards__title">{e(c["title"])}</span>
      <span class="nu-text nu-text--small nu-pathway-cards__desc">{fix(c["body"][0])}</span></span>
      <span class="nu-icon-button nu-icon-button--outline nu-pathway-cards__cue" aria-hidden="true">{i("arrow")}</span></span></span>
</a></li>''' for c in cards)
    return f'<nav class="nu-pathway-cards" aria-label="Experiential opportunities"><ul class="nu-pathway-cards__items">{lis}</ul></nav>'


# The live records spell the first-year level with a hyphen, its filter with an en dash, so the live filter matched nothing (el-03's
# "Undergraduate – 1st year 0"). Staging spells both the filter's way, which brings back its three programs.
for _o in C["opportunities"]:
    _o["educationLevel"] = [v.replace("Undergraduate - 1st year", "Undergraduate – 1st year") for v in _o.get("educationLevel", [])]


def opp_meta(o):
    return " · ".join(", ".join(o.get(k, [])) for k in ("category", "educationLevel", "duration") if o.get(k))


def opp_row(o):
    """LinkRow --media (el-03): the Finder's result, one meta line, no tag pills."""
    cta = o.get("cta") or {"text": "Learn more", "href": o.get("href")}
    ext = external(cta["href"])
    return f'''<article class="nu-link-row nu-link-row--media">
  <h3 class="nu-heading nu-heading--h3 nu-link-row__title"><a class="nu-link-row__link" href="{href(local(cta["href"]))}">{e(o["title"])}{VH_OTHER if ext else ""}</a></h3>
  <span class="nu-link-row__media">{img(file(o["image"]), "", "1x1")}</span>
  <div class="nu-link-row__body">
    <p class="nu-text">{fix(o["excerpt"])}</p>
    <p class="nu-text nu-text--meta nu-link-row__meta">{e(opp_meta(o))}</p>
    <span class="nu-arrow-link nu-arrow-link--sm{" nu-arrow-link--external" if ext else ""} nu-link-row__cue" aria-hidden="true">{e(sc(cta["text"]))} {i("external" if ext else "arrow")}</span>
  </div>
</article>'''


def plain_row(c, h="h3"):
    cta = c.get("cta") or {"text": "Learn more", "href": c.get("href")}
    ext = external(cta["href"])
    return f'''<article class="nu-link-row">
  <{h} class="nu-heading nu-heading--{"h3" if h == "h3" else "h4"} nu-link-row__title"><a class="nu-link-row__link" href="{href(local(cta["href"]))}">{e(c["title"])}{VH_OTHER if ext else ""}</a></{h}>
  <div class="nu-link-row__body"><p class="nu-text">{fix(c["excerpt"])}</p>
    <span class="nu-arrow-link nu-arrow-link--sm{" nu-arrow-link--external" if ext else ""} nu-link-row__cue" aria-hidden="true">{e(sc(cta["text"]))} {i("external" if ext else "arrow")}</span></div>
</article>'''


def grouped_rows(groups, hid):
    """Opportunity groups (el-11): one section heading; each group a label on a strong rule in columns 1–4 with its LinkRows from column 5
    (no photos: the finder has them). A single group needs no label: its rows sit straight under the SectionHeader."""
    if len(groups) == 1:
        return '<div class="el-rows">' + "".join(plain_row(c) for c in groups[0][1]) + "</div>"
    out = ""
    for n, (label, cards) in enumerate(groups):
        gid = f"{hid}-g{n}"
        out += f'''<section class="el-group" aria-labelledby="{gid}">
  <div class="el-group__head"><h3 class="nu-heading nu-heading--h3" id="{gid}">{e(label)}</h3><p class="el-group__count">{len(cards)} opportunities</p></div>
  <div class="el-group__rows">{"".join(plain_row(c, "h4") for c in cards)}</div>
</section>'''
    return f'<div class="el-groups">{out}</div>'


def stories_pair(cards, hid):
    """CardGrid --pair (el-14): the two stories as PosterCard links that say where they go."""
    lis = "".join(f'''<li><a class="nu-poster-card" href="{c["buttons"][0]["href"]}">
  <span class="nu-poster-card__frame" data-mode="dark">{img(file(c["image"]), "", "fill")}<span class="nu-scrim nu-scrim--poster"></span><span class="nu-poster-card__title">{fix(c["title"])}</span></span>
  <span class="nu-arrow-link nu-arrow-link--sm nu-arrow-link--external nu-poster-card__caption">Read on Northeastern Global News<span class="u-vh">, on another site</span> {i("external")}</span>
</a></li>''' for c in cards)
    return f'''<div class="nu-section-hub__band"><section class="nu-card-grid nu-card-grid--pair" aria-labelledby="{hid}">
  <div class="nu-card-grid__head"><div class="nu-card-grid__intro"><h2 class="nu-heading nu-heading--h2" id="{hid}">Student experiences to inspire your journey</h2></div></div>
  <ul class="nu-card-grid__items" role="list">{lis}</ul>
</section></div>'''


def story_cards(slug):
    return next(s["cards"] for s in secs(slug, "cards") if any(c.get("buttons") and "story" in c["buttons"][0].get("text", "").lower() for c in s.get("cards", [])))


def media_split(s, hid):
    """MediaText for Read chapters (el-15): five columns of photograph, the copy from column 7, the same side every time."""
    im = s["images"][0]
    paras = "".join(f'<p class="nu-text">{fix(b)}</p>' for b in s.get("body", []))
    a = actions(s.get("buttons"))
    return f'''<section class="nu-media-text nu-media-text--narrow" aria-labelledby="{hid}">
  <figure class="nu-media-text__media">{img(file(im), "", "3x2")}</figure>
  <div class="nu-media-text__copy">
    <h2 class="nu-heading nu-heading--h2" id="{hid}">{fix(s["heading"])}</h2>
    {paras}
    {f'<div class="nu-media-text__actions">{a}</div>' if a else ""}
  </div>
</section>'''


def media_overlay(s, hid, focus="50% 50%"):
    """MediaText --overlay (el-15, el-04): the page's one Night feature."""
    im = s["images"][0]
    paras = "".join(f'<p class="nu-text">{fix(b)}</p>' for b in s.get("body", []))
    a = actions(s.get("buttons"))
    return f'''<section class="nu-media-text nu-media-text--overlay" data-mode="dark" aria-labelledby="{hid}">
  <figure class="nu-media-text__media" style="--media-text-focus:{focus}">
    {img(file(im), "", "3x2")}
    <span class="nu-scrim nu-scrim--left"></span><span class="nu-scrim nu-scrim--scene"></span><span class="nu-scrim nu-scrim--grain"></span>
  </figure>
  <div class="nu-media-text__copy">
    <h2 class="nu-heading nu-heading--h2" id="{hid}">{fix(s["heading"])}</h2>
    {paras}
    {f'<div class="nu-media-text__actions">{a}</div>' if a else ""}
  </div>
</section>'''


def film_split(s, intro, hid):
    """The live film (el-01) as MediaText on Canvas: the page's Night budget goes to the opener and the campus map.
    The film carries its own lettering (the heading, then place names), so the heading is for screen readers and the copy beside the
    film is the page's intro sentence, at lead size."""
    return f'''<section class="nu-media-text nu-media-text--narrow" aria-labelledby="{hid}">
  <div class="nu-media-text__media">
    <video class="nu-video" muted loop playsinline preload="metadata" data-film poster="{{{{base}}}}assets/img/el-film-poster.jpg" src="{{{{base}}}}assets/video/{s["video"]}" aria-hidden="true"></video>
    <div class="nu-media-control"><button class="nu-icon-button nu-icon-button--media nu-media-control__toggle" type="button" aria-label="Pause the film" aria-pressed="false" data-film-toggle>{i("pause")}{i("play")}</button></div>
  </div>
  <div class="nu-media-text__copy">
    <h2 class="u-vh" id="{hid}">{e(s["heading"])}</h2>
    <p class="nu-text nu-text--lead">{fix(intro)}</p>
  </div>
</section>'''


def stat_band(s, h2, hid):
    size = "md" if len(s["stats"]) > 4 else "xl"
    stats = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--{size}">{e(x["value"])}</p><p class="nu-stat__text">{fix(x["label"])}</p></div>' for x in s["stats"])
    return band(section_header(h2, hid=hid) + f'<div class="nu-stat-band"><div class="nu-stat-band__stats">{stats}</div></div>', hid)


def mark(im_rec):
    """A partner mark trimmed to its artwork (the live files carry their own padding), with its width ÷ height for LogoWall --open."""
    from PIL import Image
    name = file(im_rec)
    out = IMG / "marks" / name
    im = Image.open(IMG / name).convert("RGBA")
    box = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    if not out.exists():
        out.parent.mkdir(exist_ok=True)
        im.crop(box).save(out)
    return f"marks/{name}", (box[2] - box[0]) / (box[3] - box[1])


def logo_wall(images, wid, show=12):
    """LogoWall --open (el-13): no cell lines, marks optically sized from their ratio; long walls show twelve, then Show all."""
    lis = ""
    for n, im in enumerate(images):
        src, ratio = mark(im)
        lis += (f'<li{" hidden data-more" if n >= show else ""}><div class="nu-logo-tile"><img class="nu-logo-tile__mark" src="{{{{base}}}}assets/img/{src}" '
                f'alt="{e(LOGO_NAMES.get(im["file"], ""))}" loading="lazy" style="--mark-ratio:{ratio:.2f}"></div></li>')
    foot = (f'<div class="nu-logo-wall__foot"><button class="nu-button nu-button--text" type="button" data-el-show-all="{wid}">'
            f'Show all {len(images)} partners</button></div>') if len(images) > show else ""
    return f'<ul class="nu-logo-wall nu-logo-wall--open nu-logo-wall--6" id="{wid}">{lis}</ul>{foot}'


def action_band(h2, button, hid):
    return f'''<section class="nu-action-band nu-action-band--center nu-section-hub__close" aria-labelledby="{hid}">
  <div class="nu-action-band__inner">
    <div class="nu-action-band__copy"><h2 class="nu-heading nu-heading--h1" id="{hid}">{fix(h2)}</h2></div>
    <div class="nu-action-band__actions"><a class="nu-button nu-button--accent" href="{href(local(button["href"]))}">{e(sc(button["text"]))}</a></div>
  </div>
</section>'''


# ---------- CampusMap --index (el-09) ----------
REGIONS = [("New England", ["Boston", "Burlington", "Nahant", "Portland"]), ("U.S. East", ["Arlington", "Charlotte", "Miami", "New York City"]),
           ("U.S. West", ["Oakland", "Seattle", "Silicon Valley"]), ("Canada", ["Toronto", "Vancouver"]), ("United Kingdom", ["London"])]
ABBR = {"Massachusetts": "MA", "Maine": "ME", "Virginia": "VA", "North Carolina": "NC", "Florida": "FL", "New York": "NY", "California": "CA", "Washington": "WA"}
PLACE = {"London": "United Kingdom", "Toronto": "Canada", "Vancouver": "Canada"}


def campus_map(s):
    cards = {c["title"]: c for c in s["cards"]}
    spec = (DS / "components/organisms/campus-map.html").read_text()
    m = _block(spec, '<section class="nu-campus-map nu-campus-map--index"', "section").replace("cmi-", "el-cm-")
    # Head: the live heading and intro, and the live link to every campus.
    m = re.sub(r'(<h2 class="nu-heading nu-heading--h1" id="el-cm-title">).*?(</h2>)', lambda x: x.group(1) + fix(s["heading"]) + x.group(2), m)
    m = re.sub(r'(<div class="nu-campus-map__intro">.*?<p class="nu-text nu-text--lead">).*?(</p>)',
               lambda x: x.group(1) + fix(s["body"][0]) + x.group(2) + arrow("Explore our campuses", s["buttons"][0]["href"]), m, flags=re.S)
    # The Select: one option per campus, its value the campus name.
    opts = "".join(f'<optgroup label="{g}">' + "".join(
        f'<option value="{n}"{" selected" if n == "London" else ""}>{n}{", " + ABBR[cards[n]["eyebrow"]] if cards[n].get("eyebrow") in ABBR else ""}</option>' for n in names) + "</optgroup>"
        for g, names in REGIONS)
    m = re.sub(r"<select ([^>]*)>.*?</select>", lambda x: f"<select {x.group(1)} data-el-campus>{opts}</select>", m, flags=re.S)
    # The panel starts on London, as the spec does, with the live card's photograph, sentence and link.
    lon = cards["London"]
    m = re.sub(r'<img class="nu-image nu-image--16x9"[^>]*>', img(file(lon["image"]), "", "16x9"), m)
    m = re.sub(r'(<p class="nu-text">)Our hub in Europe.*?(</p>)', lambda x: x.group(1) + fix(lon["excerpt"]) + x.group(2), m)
    m = re.sub(r'<span>England, United Kingdom</span>', "<span>United Kingdom</span>", m)
    m = m.replace('href="#">Explore London', f'href="{lon["href"]}">Explore London')
    # The index: every campus as a compact LinkRow, grouped by the Select's regions.
    idx = ""
    for n, (g, names) in enumerate(REGIONS):
        rows = ""
        for nm in names:
            c = cards[nm]
            rows += f'''<article class="nu-link-row">
        <h4 class="nu-heading nu-heading--h4 nu-link-row__title"><a class="nu-link-row__link" href="{c["href"]}">{nm}<span class="u-vh"> (on another site)</span></a>{i("external").replace("{{i:external}}", '<svg class="nu-icon nu-icon--sm nu-campus-map__external" aria-hidden="true"><use href="#i-external"></use></svg>')}</h4>
        <div class="nu-link-row__body"><p class="nu-text nu-text--meta">{e(c.get("eyebrow") or PLACE[nm])}</p><p class="nu-text">{fix(c["excerpt"])}</p></div>
      </article>'''
        idx += f'''<section class="nu-campus-map__region" aria-labelledby="el-cm-r{n}">
      <div class="nu-campus-map__region-head"><h3 class="nu-heading nu-heading--h3" id="el-cm-r{n}">{g}</h3><p class="nu-campus-map__count">{len(names)} campus{"es" if len(names) > 1 else ""}</p></div>
      <div class="nu-campus-map__campuses">{rows}</div>
    </section>'''
    m = re.sub(r'<div class="nu-campus-map__index">.*', f'<div class="nu-campus-map__index">{idx}</div>\n</section>', m, flags=re.S)
    data = {n: {"place": c.get("eyebrow") or PLACE[n], "text": fix(c["excerpt"]), "href": c["href"], "img": file(c["image"])} for n, c in cards.items()}
    return m + f'<script type="application/json" id="el-campuses">{json.dumps(data)}</script>'


# ---------- the employer form (kept: the review's model Operate surface) ----------
def employer_form(s, hid):
    f = C["forms"][0]
    sel = next(x for x in f["fields"] if x["type"] == "select")
    opts = "".join(f"<option>{e(o)}</option>" for o in sel.get("options", []) if o and not o.lower().startswith("select"))
    req = '<span class="nu-label__req">(required)</span>'
    return f'''<section class="nu-section-hub__band" id="employer-opportunity-form" aria-labelledby="{hid}">
<form class="nu-form nu-form--split" data-staging-form novalidate>
  <div class="nu-form__head">
    <h2 class="nu-heading nu-heading--h2" id="{hid}">{fix(s["heading"])}</h2>
    <p class="nu-form__note">Fields marked (required) must be filled in.</p>
  </div>
  <div class="nu-form__body">
    <div class="nu-notice" role="status" hidden data-staging-sent><p class="nu-text">This is the staging site, so nothing was sent. On the live site the partnerships team receives this form.</p></div>
    <fieldset class="nu-form__group">
      <legend>About you</legend>
      <div class="nu-form__row">
        <div class="nu-field"><label class="nu-label" for="ef-first">First name {req}</label><input class="nu-input" id="ef-first" autocomplete="given-name" required></div>
        <div class="nu-field"><label class="nu-label" for="ef-last">Last name {req}</label><input class="nu-input" id="ef-last" autocomplete="family-name" required></div>
      </div>
      <div class="nu-field"><label class="nu-label" for="ef-org">Organization {req}</label><input class="nu-input" id="ef-org" autocomplete="organization" required></div>
      <div class="nu-form__row">
        <div class="nu-field"><label class="nu-label" for="ef-email">Email {req}</label><input class="nu-input" id="ef-email" type="email" autocomplete="email" required></div>
        <div class="nu-field"><label class="nu-label" for="ef-phone">Phone</label><span class="nu-hint" id="ef-phone-hint">Include the country code outside the US.</span><input class="nu-input" id="ef-phone" type="tel" autocomplete="tel" aria-describedby="ef-phone-hint"></div>
      </div>
    </fieldset>
    <fieldset class="nu-form__group">
      <legend>Your inquiry</legend>
      <div class="nu-field"><label class="nu-label" for="ef-interest">I’d like information about {req}</label><span class="nu-select"><select id="ef-interest" required><option value="">Choose one</option>{opts}</select>{i("chevron-down")}</span></div>
      <div class="nu-field"><label class="nu-label" for="ef-needs">Share more about your staffing needs</label><textarea class="nu-input" id="ef-needs" rows="5"></textarea></div>
    </fieldset>
    <div class="nu-form__foot"><div class="nu-form__actions"><button class="nu-button nu-button--accent" type="submit">Submit</button></div></div>
  </div>
</form>
</section>'''


def finder_band():
    s = sec("experiential-opportunities", "finder")
    opps = [o for o in C["opportunities"] if o.get("excerpt")]
    keys = {"nu_category": "category", "nu_education-level": "educationLevel", "nu_duration": "duration"}
    # Facets show only options that have results.
    facets = "".join(facet_chips(keys[f["taxonomy"]], sc(f["label"]), f["options"], lambda v, k=keys[f["taxonomy"]]: sum(v in x.get(k, []) for x in opps)) for f in s["filters"])
    rows = ""
    for o in sorted(opps, key=lambda o: o["title"].lower()):
        terms = json.dumps({k: o.get(k, []) for k in keys.values()})
        rows += f"<li data-terms='{e(terms)}'>{opp_row(o)}</li>"
    head = sec("experiential-opportunities", "text", "All experiential learning opportunities")
    return finder("Filter opportunities", "opportunities", facets, rows, list_cls="nu-finder__results nu-finder__results--list el-results", page=8,
                  head=section_header(head["heading"], fix(head["body"][0]), hid="all-opportunities"))


# ---------- pages ----------
def page(slug, title, body, current, hero_html, desc=None):
    path = local(P[slug]["url"]).rstrip("/") if slug in P else slug
    check_rendered(slug, body)
    site.page(path, title, desc or P[slug].get("metaDescription") or title, f'<div class="nu-section-hub">{body}</div>', current, hero_html)


def home():
    s = "home"
    hs = sec(s, "hero")
    hero_html = hero("Experience the world your way", file(hs["images"][0]), "display", "50% 50%", "57% 50%",
                     button=("Find your opportunity", "experiential-opportunities/"), figure=(file(hs["images"][1]), "A Northeastern student"))
    st = sec(s, "text", "learning by doing")
    line, _, lead = fix(st["heading"]).partition("—")
    claims = sec(s, "cards-carousel")
    body = statement(line + ".", lead[:1].upper() + lead[1:], (fix(st["eyebrow"]).replace("What is", "What is").strip(), "experiential-learning-defined/"))
    body += quick_links(s)
    body += f'''<section class="nu-unit-home__band nu-unit-home__claims" data-mode="dark" aria-labelledby="claims">
{section_header(fix(claims["heading"]), fix(claims["body"][0]), hid="claims")}
{claims_grid(claims["cards"], "Six ways experiential learning is different here")}
</section>'''
    body += stat_band(sec(s, "stats"), fix(sec(s, "text", "Strength in numbers")["heading"]), "numbers")
    for n, m in enumerate(secs(s, "media-text")):
        body += media_split(m, f"m{n}")
    body += stories_pair(story_cards(s), "stories")
    lg = sec(s, "logos")
    body += band(section_header(fix(lg["heading"]), fix(lg["body"][0]), (sc(lg["buttons"][0]["text"]), local(lg["buttons"][0]["href"])), hid="partners")
                 + logo_wall(lg["images"], "partners-wall"), "partners")
    page(s, UNIT, body, "", hero_html)


def defined():
    s = "experiential-learning-defined"
    hs = sec(s, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "tall", "50% 22%", "34% 30%", HOME)
    st = sec(s, "text", "all about learning by doing")
    line, _, lead = fix(st["heading"]).partition("—")
    body = statement(line + ".", lead[:1].upper() + lead[1:])
    body += quick_links(s)
    ben = sec(s, "text+list")
    body += band(point_list([split_term(x) for x in ben["lists"][0]["items"]], fix(ben["heading"]), "benefits", numbered=True))
    why = sec(s, "text", "is different")
    cta = sec(s, "cta")["buttons"][0]
    claims = next(x for x in secs(s, "cards") if all("image" not in c for c in x["cards"]))
    body += band(section_header(fix(why["heading"]), fix(why["body"][0]), (cta["text"], local(cta["href"])), hid="different")
                 + point_list([(fix(c["title"]), None) for c in claims["cards"]]), "different")
    body += media_overlay(sec(s, "media-text"), "connections", "50% 60%")
    body += stories_pair(story_cards(s), "stories")
    page(s, fix(hs["heading"]), body, "experiential-learning-defined/", hero_html)


def network():
    s = "experiential-learning-defined--global-experiential-network"
    hs = sec(s, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "medium", "50% 62%", "40% 60%",
                     HOME + [("Experiential learning defined", "experiential-learning-defined/")])
    intro = sec(s, "text", "Our worldwide network")["heading"]
    body = quick_links(s)
    body += film_split(sec(s, "film"), intro, "film")
    pw = sec(s, "text+list")
    body += band(section_header(fix(pw["heading"]), fix(pw["body"][0]), hid="place") + point_list([(fix(x), None) for x in pw["lists"][0]["items"]]), "place")
    body += campus_map(sec(s, "cards-carousel"))
    body += media_split(sec(s, "media-text"), "destinations")
    page(s, fix(hs["heading"]), body, "experiential-learning-defined/global-experiential-network/", hero_html)


def opportunities():
    s = "experiential-opportunities"
    hs = sec(s, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "tall", "50% 40%", "50% 35%", HOME)
    find = sec(s, "text", "Find the right")
    body = quick_links(s)
    body += band(section_header(fix(find["heading"]), fix(find["body"][0]), hid="pathways") + pathway_cards(next(x for x in secs(s, "cards"))["cards"]), "pathways")
    body += finder_band()
    body += media_overlay(sec(s, "media-text"), "begin", "50% 30%")
    page(s, fix(hs["heading"]), body, "experiential-opportunities/", hero_html)


def child(slug, current, focus, phone):
    hs = sec(slug, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "medium", focus, phone, HOME + [("Experiential opportunities", "experiential-opportunities/")])
    intro = fix(P[slug]["sections"][1]["heading"])
    opp_head = next(x for x in secs(slug, "text") if x.get("eyebrow") and "more experiential" in x["eyebrow"])
    groups = [(sc(x["eyebrow"]), x["cards"]) for x in secs(slug, "cards") if x.get("eyebrow") and x["cards"] and "excerpt" in x["cards"][0]]
    body = sibling_nav(current)
    expand = [x for x in secs(slug, "cards") if x.get("heading", "").startswith("Expand")]
    if expand:  # Extracurricular: the intro leads the first chapter, the activities as captioned photographs
        x = expand[0]
        body += band(section_header(fix(x["heading"]), intro, hid="expand", extra=f'<p class="nu-text">{fix(x["body"][0])}</p>')
                     + claims_grid(x["cards"], "Student activities", four=True), "expand")
        body += band(section_header(fix(opp_head["heading"]), hid="opps") + grouped_rows(groups, "opps"), "opps")
    else:
        body += band(section_header(fix(opp_head["heading"]), intro, hid="opps") + grouped_rows(groups, "opps"), "opps")
    mt = secs(slug, "media-text")
    if mt:
        body += media_overlay(mt[0], "feature", "50% 45%")
    body += stories_pair(story_cards(slug), "stories")
    page(slug, fix(hs["heading"]), body, current, hero_html)


def partnerships():
    s = "partnerships"
    hs = sec(s, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "tall", "50% 40%", "50% 40%", HOME)
    intro = secs(s, "cta")[0]
    first, rest = re.match(r"(.+?\.)\s+(.*)", fix(intro["heading"])).groups()
    body = statement(cut(first), rest, (intro["buttons"][0]["text"], local(intro["buttons"][0]["href"])))
    body += quick_links(s)
    body += media_overlay(sec(s, "media-text"), "built", "60% 40%")
    lg = sec(s, "logos")
    body += band(section_header(fix(lg["heading"]), fix(lg["body"][0]), (sc(lg["buttons"][0]["text"]), local(lg["buttons"][0]["href"])), hid="partners")
                 + logo_wall(lg["images"], "partners-wall"), "partners")
    close = secs(s, "cta")[1]
    body += action_band(close["heading"], close["buttons"][0], "contact")
    page(s, fix(hs["heading"]), body, "partnerships/", hero_html)


def employer():
    s = "partnerships--employer"
    hs = sec(s, "hero")
    hero_html = hero(fix(hs["heading"]), file(hs["images"][0]), "medium", "50% 40%", "30% 40%", HOME + [("Employer partnerships", "partnerships/")])
    ben = sec(s, "text", "benefit employers")
    tiles = next(x for x in secs(s, "cards") if x["cards"] and "image" in x["cards"][0] and "excerpt" not in x["cards"][0])
    body = band(section_header(fix(ben["heading"]), fix(ben["body"][0]), hid="benefits") + claims_grid(tiles["cards"], "How partnerships benefit employers"), "benefits")
    head = sec(s, "text", "Experiential opportunities for employers")
    groups = [(sc(x["eyebrow"]), x["cards"]) for x in secs(s, "cards") if x.get("eyebrow")]
    body += band(section_header(fix(head["heading"]), fix(head["body"][0]), hid="opps") + grouped_rows(groups, "opps"), "opps")
    body += media_overlay(sec(s, "media-text"), "partner", "60% 40%")
    body += employer_form(sec(s, "form"), "form")
    page(s, fix(hs["heading"]), body, "partnerships/employer/", hero_html)


# ---------- nothing live goes missing (el-01) ----------
def live_text(sec_):
    out = [sec_.get("heading"), *sec_.get("body", [])]
    out += [x for lst in sec_.get("lists", []) for x in lst.get("items", []) if isinstance(x, str)]
    for c in sec_.get("cards", []):
        out += [c.get("title"), c.get("excerpt"), *c.get("body", [])]
    out += [x.get("label") for x in sec_.get("stats", [])]
    out = [fix(t) for t in out if t]
    for a, b in CUTS.items():
        out = [t.replace(a, b) for t in out]
    return out


def words(markup):
    """Text as a run of lowercase words: punctuation-blind, so a statement split at its dash still counts as rendered."""
    t = html.unescape(re.sub(r"<[^>]+>", " ", markup))
    return " ".join(re.findall(r"[a-z0-9]+", t.lower()))


def check_rendered(slug, body):
    """Fail the build when live copy didn't make it onto the page, instead of dropping it silently."""
    if slug not in P:
        return
    seen = words(body)
    missing = [t for s in P[slug]["sections"][1:] if s["type"] not in ("finder", "search", "form", "quick-links")
               for t in live_text(s) if words(t)[:60] not in seen]
    if missing:
        sys.exit(f"{slug}: {len(missing)} piece(s) of live copy not rendered:\n  " + "\n  ".join(m[:90] for m in missing))


def search():
    body = hero_title("Search experiential learning", "Results come from Google’s search of experientiallearning.northeastern.edu.", HOME) + f'''<section class="st-band">
<form class="nu-search-field nu-search-field--lg" role="search" action="https://cse.google.com/cse" method="get">
  <label class="u-vh" for="q">Search experiential learning</label>
  <input type="hidden" name="cx" value="c380dc3d000df4096">
  <input class="nu-input" id="q" name="q" type="search" placeholder="Search co-op, research, study abroad…">
  <button class="nu-icon-button" type="submit" aria-label="Search">{i("search")}</button>
</form></section>'''
    site.page("search-experiential", "Search", "Search experiential learning at Northeastern.", body, "search-experiential/")


def main():
    home()
    defined()
    network()
    opportunities()
    child("experiential-opportunities--academic", "experiential-opportunities/academic/", "60% 40%", "62% 40%")
    child("experiential-opportunities--professional", "experiential-opportunities/professional/", "40% 40%", "30% 40%")
    child("experiential-opportunities--extracurricular", "experiential-opportunities/extracurricular/", "55% 35%", "68% 30%")
    partnerships()
    employer()
    search()
    not_found(site, [("Home", "", "Experiential learning at Northeastern."), ("Experiential opportunities", "experiential-opportunities/", "Every academic, professional and extracurricular opportunity, with filters."),
                     ("Employer partnerships", "partnerships/", "Hire Northeastern students and partner on projects."), ("Search", "search-experiential/", "Search the site.")])
    site.finish()


if __name__ == "__main__":
    main()
