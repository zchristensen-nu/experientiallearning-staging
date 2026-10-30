"""Build the Experiential Learning staging site on the Northeastern Design System (NUEAC-413).

Content is the live experientiallearning.northeastern.edu content (scraped into build/content.json); each section type
the live site uses is rendered with the system organism that fits it. The page shell comes from ~/Projects/nu-site-kit.
    python3 build/build.py            # writes docs/
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / "Projects/nu-site-kit"))
from kit import (Site, band, card_grid, e, facet_chips, finder, hero_page, hero_title, href, i, img,  # noqa: E402
                 link_row, not_found, section_header)

ROOT = Path(__file__).resolve().parents[1]
C = json.loads((ROOT / "build/content.json").read_text())
LIVE = "https://experientiallearning.northeastern.edu/"
UNIT = "Experiential Learning"
# Logo names exist only inside the images; the crawl read them off.
LOGO_NAMES = {}
for p in C["pages"]:
    for s in p.get("sections", []):
        for it in s.get("items", []):
            if isinstance(it, dict) and it.get("textInImage"):
                LOGO_NAMES[it["file"]] = it["textInImage"]
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
        return u.split("#")[0] or ""
    return u


def file(img_rec):
    return img_rec["file"].split("/", 1)[1]


NAV = [("Overview", [("Experiential learning defined", "experiential-learning-defined/"),
                     ("Global experiential network", "experiential-learning-defined/global-experiential-network/")]),
       ("Experiential opportunities", [("All opportunities", "experiential-opportunities/"), ("Academic", "experiential-opportunities/academic/"),
                                       ("Professional", "experiential-opportunities/professional/"), ("Extracurricular", "experiential-opportunities/extracurricular/")]),
       ("Employer partnerships", [("Partnerships", "partnerships/"), ("Employer opportunities", "partnerships/employer/")]),
       ("Search", "search-experiential/")]
cols = C["site"]["localFooter"]["linkColumns"]
site = Site(ROOT, UNIT, "experientiallearning-staging", "experientiallearning.northeastern.edu", NAV,
            [("Experiential learning", [(sc(l["text"]) if l["text"].isupper() else l["text"], l["href"]) for l in cols[0]]),
             ("Research and PhD", [(l["text"], l["href"]) for l in cols[1]]),
             ("More at Northeastern", [(l["text"], l["href"]) for l in cols[2]])])


# ---------- one renderer per live section type ----------
def actions(buttons, primary=True):
    out = []
    for n, b in enumerate(b for b in (buttons or []) if b.get("href") and b.get("text", "").lower() != "load more"):
        t = local(b["href"])
        if n == 0 and primary:
            out.append(f'<a class="nu-button" href="{href(t)}">{e(sc(b["text"]))} {i("arrow")}</a>')
        else:
            out.append(f'<a class="nu-arrow-link" href="{href(t)}">{e(sc(b["text"]))} {i("arrow")}</a>')
    return "".join(out)


def r_text(s, n):
    heading, eyebrow = fix(s.get("heading") or ""), sc(s.get("eyebrow"))
    body = [fix(b) for b in s.get("body", [])]
    if eyebrow and heading and len(heading) > 80:  # a statement under a label: the label becomes the heading
        return band(section_header(eyebrow, heading, hid=f"s{n}"), "st-band--statement")
    if heading and not eyebrow and not body and len(heading) > 80:  # an opening statement: set wide, not in the heading column
        return band(f'<p class="st-statement">{heading}</p>', "st-band--statement")
    h2 = heading or eyebrow
    lead = body[0] if body else None
    more = "".join(f'<p class="nu-text">{b}</p>' for b in body[1:])
    items = [fix(x) for lst in s.get("lists", []) for x in lst["items"]]
    if items:
        more += '<ul class="st-bullets">' + "".join(f"<li>{x}</li>" for x in items) + "</ul>"
    a = actions(s.get("buttons"))
    return band(section_header(h2, lead, hid=f"s{n}", extra=more) + (f'<div class="st-actions">{a}</div>' if a else ""))


def r_quick(s, n):
    links = [x[0] for lst in s.get("lists", []) for x in lst["items"]]
    lis = "".join(f'<li><a class="nu-in-page-nav__link nu-nav-link" href="{href(local(l["href"]))}">{e(l["text"])}</a></li>' for l in links)
    return f'''<nav class="nu-in-page-nav st-quick" aria-label="Quick links">
  <div class="nu-in-page-nav__inner">
    <p class="nu-text nu-text--label nu-in-page-nav__label">Quick links</p>
    <ul class="nu-in-page-nav__list">{lis}</ul>
  </div>
</nav>'''


def story(card, link=True):
    meta = [sc(card["eyebrow"])] if card.get("eyebrow") else []
    url = (card.get("cta") or {}).get("href") or card.get("href")
    if card.get("buttons"):
        url = card["buttons"][0]["href"]
    if "title" not in card:  # an image with one line of copy
        return f'''<li><figure class="nu-figure">{img(file(card["image"]), "")}<figcaption class="nu-figure__caption">{fix(" ".join(card.get("body", [])))}</figcaption></figure></li>'''
    title = fix(card["title"])
    t = f'<a class="nu-story-card__link" href="{href(local(url))}">{title}</a>' if link and url and not card.get("linkDisabled") else title
    m = "".join(f"<li>{x}</li>" for x in meta)
    text = card.get("excerpt") or " ".join(card.get("body", []))
    ex = f'<p class="nu-text nu-text--small">{fix(text)}</p>' if text else ""
    return f'''<li><article class="nu-story-card">
  <span class="nu-story-card__media">{img(file(card["image"]), card["image"].get("alt", ""))}</span>
  <div class="nu-story-card__body">
    <h3 class="nu-heading nu-heading--h4 nu-story-card__title">{t}</h3>
    {f'<ul class="nu-meta-list nu-meta-list--inline">{m}</ul>' if m else ""}{ex}
  </div>
</article></li>'''


def r_carousel(s, n):
    head = section_header(fix(s["heading"]), fix(s["body"][0]) if s.get("body") else None, hid=f"s{n}")
    return band(head + card_grid([story(c) for c in s["cards"]]))


def program_card(c):
    cta = c.get("cta") or {"text": "Learn more", "href": c.get("href")}
    terms = [t for k in ("category", "educationLevel", "duration") for t in c.get(k, [])]
    tags = "".join(f'<span class="nu-tag">{e(t)}</span>' for t in terms)
    ext = not local(cta["href"]).startswith(("experiential", "partnerships")) and cta["href"].startswith("http")
    return f'''<li><article class="nu-program-card">
  <span class="nu-program-card__media">{img(file(c["image"]), c["image"].get("alt", "").replace("studnet", "student"))}</span>
  <div class="nu-program-card__body">
    <h3 class="nu-heading nu-heading--h4 nu-program-card__title"><a class="nu-program-card__link" href="{href(local(cta["href"]))}">{e(c["title"])}</a></h3>
    <p class="nu-text nu-text--small">{fix(c["excerpt"])}</p>
    <div class="nu-program-card__foot">
      {f'<div class="nu-program-card__tags">{tags}</div>' if tags else ""}
      <span class="nu-arrow-link nu-arrow-link--sm{" nu-arrow-link--external" if ext else ""} nu-program-card__cue" aria-hidden="true">{e(sc(cta["text"]))} {i("external" if ext else "arrow")}</span>
    </div>
  </div>
</article></li>'''


def r_cards(s, n):
    cards = s.get("cards", [])
    if not cards:
        return ""
    is_story = any(c.get("buttons") and "story" in c["buttons"][0].get("text", "").lower() for c in cards)
    if is_story:
        h = fix(s.get("heading") or "Student experiences to inspire your journey")
        return band(card_grid([story(c) for c in cards], h, f"s{n}"))
    own = fix(s.get("heading") or "")
    own_head = section_header(own, fix(s["body"][0]) if s.get("body") else None, hid=f"s{n}") if own and not s.get("eyebrow") else ""
    if all("image" not in c for c in cards):  # a list of short claims: hairline rows
        pts = "".join(f'<li><h3 class="nu-heading nu-heading--h3">{fix(c["title"])}</h3></li>' for c in cards)
        return band(own_head + f'<ul class="st-points" role="list">{pts}</ul>', "st-band--tight")
    if all("excerpt" not in c for c in cards):  # benefit tiles: title, image and their copy
        return band(own_head + card_grid([story(c, False) for c in cards]))
    h = sc(s.get("eyebrow") or s.get("heading") or "")
    head = section_header(h, fix(s["body"][0]) if s.get("body") else None, hid=f"s{n}") if h else ""
    return band(head + f'<ul class="st-program-grid" role="list">{"".join(program_card(c) for c in cards)}</ul>', "st-band--tight")


def r_stats(s, n, head=""):
    size = "md" if len(s["stats"]) > 4 else "xl"  # five figures at display size collide in one row
    stats = "".join(f'<div class="nu-stat nu-stat--column"><p class="nu-numeral nu-numeral--{size}">{e(x["value"])}</p><p class="nu-stat__text">{fix(x["label"])}</p></div>' for x in s["stats"])
    return band(head + f'<div class="nu-stat-band"><div class="nu-stat-band__stats">{stats}</div></div>')


def r_media(s, n, reverse=False):
    im = s["images"][0]
    paras = "".join(f'<p class="nu-text">{fix(b)}</p>' for b in s.get("body", []))
    items = "".join(f"<li>{fix(x)}</li>" for lst in s.get("lists", []) for x in lst["items"])
    lst = f'<div class="nu-prose st-list"><ul>{items}</ul></div>' if items else ""
    a = actions(s.get("buttons"))
    return f'''<section class="nu-media-text{" nu-media-text--reverse" if reverse else ""} st-tight" aria-labelledby="s{n}">
  <figure class="nu-media-text__media">{img(file(im), im.get("alt", ""))}</figure>
  <div class="nu-media-text__copy">
    <h2 class="nu-heading nu-heading--h2" id="s{n}">{fix(s["heading"])}</h2>
    {paras}{lst}
    {f'<div class="nu-media-text__actions">{a}</div>' if a else ""}
  </div>
</section>'''


def r_logos(s, n):
    tiles = "".join(f'<li><div class="nu-logo-tile"><img class="nu-logo-tile__mark" src="{{{{base}}}}assets/img/{file(im)}" alt="{e(LOGO_NAMES.get(im["file"], ""))}" loading="lazy"></div></li>' for im in s["images"])
    head = section_header(fix(s["heading"]), fix(s["body"][0]) if s.get("body") else None, hid=f"s{n}")
    return band(head + f'<ul class="nu-logo-wall st-logos">{tiles}</ul>' + (f'<div class="st-actions">{actions(s.get("buttons"))}</div>' if s.get("buttons") else ""))


def r_cta(s, n):
    if not s.get("heading"):
        return band(f'<div class="st-actions">{actions(s.get("buttons"))}</div>', "st-band--tight")
    a = "".join(f'<a class="nu-button" href="{href(local(b["href"]))}">{e(sc(b["text"]))}</a>' for b in s.get("buttons", []) if b.get("href"))
    return f'''<section class="nu-action-band" data-mode="dark" aria-labelledby="s{n}">
  <div class="nu-action-band__inner">
    <div class="nu-action-band__copy"><h2 class="nu-heading nu-heading--{"h3" if len(s["heading"]) > 80 else "h1"}" id="s{n}">{fix(s["heading"])}</h2></div>
    <div class="nu-action-band__actions">{a}</div>
  </div>
</section>'''


def r_finder(s, n):
    opps = [o for o in C["opportunities"] if o.get("excerpt")]
    keys = {"nu_category": "category", "nu_education-level": "educationLevel", "nu_duration": "duration"}
    facets = "".join(facet_chips(keys[f["taxonomy"]], sc(f["label"]), f["options"], lambda v, k=keys[f["taxonomy"]]: sum(v in x.get(k, []) for x in opps)) for f in s["filters"])
    cards = ""
    for o in sorted(opps, key=lambda o: o["title"].lower()):
        terms = json.dumps({k: o.get(k, []) for k in keys.values()})
        cards += program_card(o).replace("<li>", f"<li data-terms='{e(terms)}'>", 1)
    intro = next((x["body"][0] for x in C["pages"][3]["sections"] if x.get("heading") == "All experiential learning opportunities"), "")
    return finder("Filter opportunities", "opportunities", facets, cards,
                  head=section_header("All experiential learning opportunities", fix(intro), hid=f"s{n}"))


def r_form(s, n):
    f = C["forms"][0]
    sel = next(x for x in f["fields"] if x["type"] == "select")
    opts = "".join(f"<option>{e(o)}</option>" for o in sel.get("options", []) if o and not o.lower().startswith("select"))
    req = '<span class="nu-label__req">(required)</span>'
    return f'''<section class="st-band" id="employer-opportunity-form" aria-labelledby="s{n}">
<form class="nu-form nu-form--split" data-staging-form novalidate>
  <div class="nu-form__head">
    <h2 class="nu-heading nu-heading--h2" id="s{n}">{fix(s["heading"])}</h2>
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


def r_film(s, n):
    """A full-bleed film band on Night with a pause control (brand: autoplaying video must pause).
    The live film has its headline burned into the frames, so the heading is for screen readers only."""
    return f'''<section class="st-film" data-mode="dark" aria-labelledby="s{n}">
  <video class="nu-video nu-video--fill st-film__video" muted loop playsinline preload="metadata" data-film src="{{{{base}}}}assets/video/{s["video"]}" aria-hidden="true"></video>
  <span class="nu-scrim nu-scrim--grain"></span>
  <h2 class="u-vh" id="s{n}">{e(s["eyebrow"])}: {e(s["heading"])}</h2>
  <div class="nu-media-control st-film__control"><button class="nu-icon-button nu-icon-button--outline nu-media-control__toggle" type="button" aria-label="Pause the film" aria-pressed="false" data-film-toggle>{i("pause")}{i("play")}</button></div>
</section>'''


RENDER = {"film": r_film, "text": r_text, "quick-links": r_quick, "cards-carousel": r_carousel, "cards": r_cards, "stats": r_stats,
          "media-text": r_media, "text+list": r_media, "logos": r_logos, "cta": r_cta, "finder": r_finder, "form": r_form}


def live_text(sec):
    """Every piece of visible live copy in a section: headings, paragraphs, list items, card titles and copy, stats."""
    out = [sec.get("heading"), *sec.get("body", [])]
    out += [x for lst in sec.get("lists", []) for x in lst.get("items", []) if isinstance(x, str)]
    for c in sec.get("cards", []):
        out += [c.get("title"), c.get("excerpt"), *c.get("body", [])]
    out += [x.get("label") for x in sec.get("stats", [])]
    return [fix(t) for t in out if t]


def flat(markup):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", markup))).strip().lower()


def check_rendered(slug, sections, body):
    """Fail the build when live copy didn't make it onto the page, instead of dropping it silently."""
    seen = flat(body)
    missing = [t for sec in sections if sec["type"] not in ("finder", "search", "form") for t in live_text(sec) if flat(t)[:60] not in seen]
    if missing:
        sys.exit(f"{slug}: {len(missing)} piece(s) of live copy not rendered:\n  " + "\n  ".join(m[:90] for m in missing))


def build_page(p):
    secs = p["sections"]
    hero_s, rest = secs[0], secs[1:]
    path = local(p["url"]).rstrip("/")
    current = (path + "/") if path else ""
    crumbs = None
    if path:
        parts = path.split("/")
        crumbs = [(UNIT, "")]
        if len(parts) > 1:
            parent = next(q for q in C["pages"] if local(q["url"]).rstrip("/") == parts[0])
            crumbs.append((parent["wpTitle"], parts[0] + "/"))
    if p["slug"] == "home":
        h1 = "Experience the world your way"
    else:
        h1 = fix(hero_s["heading"])
    ims = hero_s.get("images", [])
    if p["slug"] == "home" and len(ims) > 1:  # texture ground with the student cutout over it, as on the live site
        hero = hero_page(h1, file(ims[0]), figure=file(ims[1]), figure_alt="A Northeastern student")
    else:
        hero = hero_page(h1, file(ims[-1]), crumbs=crumbs) if ims else ""
    body, media_n = "", 0
    for n, s in enumerate(rest):
        nxt = rest[n + 1]["type"] if n + 1 < len(rest) else None
        if s["type"] == "text" and nxt in ("stats", "finder"):  # the heading belongs to the band that follows
            continue
        if s["type"] == "text" and nxt == "cards" and not s.get("body") and not s.get("buttons") and not (rest[n + 1].get("heading") or rest[n + 1].get("eyebrow")):
            rest[n + 1] = dict(rest[n + 1], heading=s.get("heading"))  # a lone heading over cards: one section
            continue
        if s["type"] == "stats" and n and rest[n - 1]["type"] == "text":
            prev = rest[n - 1]
            body += r_stats(s, n, section_header(fix(prev.get("heading") or sc(prev.get("eyebrow"))), hid=f"s{n}"))
            continue
        if s["type"] in ("media-text", "text+list") and s.get("images"):
            body += r_media(s, n, reverse=media_n % 2 == 1)
            media_n += 1
        elif s["type"] in ("media-text", "text+list"):
            body += r_text(s, n)
        else:
            body += RENDER[s["type"]](s, n)
    if not hero:
        body = hero_title(h1, crumbs=crumbs) + body
    check_rendered(p["slug"], rest, body)
    title = "Experiential Learning" if p["slug"] == "home" else h1
    site.page(path, title, p.get("metaDescription") or h1, body, current, hero)


def search():
    body = hero_title("Search experiential learning", "Results come from Google’s search of experientiallearning.northeastern.edu.", [(UNIT, "")]) + band(f'''
<form class="nu-search-field nu-search-field--lg" role="search" action="https://cse.google.com/cse" method="get">
  <label class="u-vh" for="q">Search experiential learning</label>
  <input type="hidden" name="cx" value="c380dc3d000df4096">
  <input class="nu-input" id="q" name="q" type="search" placeholder="Search co-op, research, study abroad…">
  <button class="nu-icon-button" type="submit" aria-label="Search">{i("search")}</button>
</form>''')
    site.page("search-experiential", "Search", "Search experiential learning at Northeastern.", body, "search-experiential/")


def main():
    for p in C["pages"]:
        if p["slug"] in ("search-experiential", "404"):
            continue
        build_page(p)
    search()
    not_found(site, [("Home", "", "Experiential learning at Northeastern."), ("Experiential opportunities", "experiential-opportunities/", "Every academic, professional and extracurricular opportunity, with filters."),
                     ("Employer partnerships", "partnerships/", "Hire Northeastern students and partner on projects."), ("Search", "search-experiential/", "Search the site.")])
    site.finish()


if __name__ == "__main__":
    main()
