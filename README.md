# Experiential Learning — staging

A migration of [experientiallearning.northeastern.edu](https://experientiallearning.northeastern.edu/) onto the Northeastern Design System (NUEAC-413), for review. Not the live site; every page is `noindex`.

- `build/build.py` renders each live section type with the system organism that fits it; content is the live site's (`build/content.json`). The page shell comes from `~/Projects/nu-site-kit`.
- `docs/` is the built output that GitHub Pages serves.

```bash
python3 build/build.py
```

## Decisions made on staging
- **Stories**: the six `/stories/` pages have no body on the live site (title and image only) and their card links are switched off, so they appear as cards on the home page and have no pages here.
- **Opportunities**: the 23 records are one filterable directory on Experiential opportunities (category, education level, duration). Each card links where the live card button links; the empty `/opportunities/` detail pages are not rebuilt.
- **Dropped**: hidden placeholder buttons ("Lorem ipsum", "Apply Now", "Plan Your visit"), the "Hello world!" post, the "test 1"/"test 2" category terms.
- **Corrected**: "WHat is experiential learning?" and "study at one our global network hubs"; the Co-op image alt text ("studnet"). Eyebrow labels set in caps are in sentence case.
- **Kept as published, needs an owner's check**: the partner count differs across pages (4,000+ / Over 3,800 / 3,900+, and the home page shows 4,000+ twice for two different figures); "Summer In" links to the Semester In page; "Experiential PhD" is tagged Undergraduate and Short term; the employer form's interest list includes student-only programs.
- **Employer form**: rebuilt with the system's Form organism; on staging it shows a notice instead of sending.
- **Search**: sends the query to the same Google Programmable Search engine the live site uses.
