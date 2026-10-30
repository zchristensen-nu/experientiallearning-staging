# Experiential Learning — staging

A migration of [experientiallearning.northeastern.edu](https://experientiallearning.northeastern.edu/) onto the Northeastern Design System (NUEAC-413), for review. Not the live site; every page is `noindex`.

- `build/build.py` builds each page to a band plan from the system's Unit home and Section hub templates (a Night opener, Canvas chapters, at most one Night feature); content is the live site's (`build/content.json`). The page shell comes from `~/Projects/nu-site-kit`. The build fails if any live heading, paragraph, list item or card copy is missing from its page.
- `docs/` is the built output that GitHub Pages serves.

```bash
python3 build/build.py
```

## Decisions made on staging
- **Stories**: the six `/stories/` pages have no body on the live site (title and image only) and their card links are switched off, so they appear as cards on the home page and have no pages here.
- **Opportunities**: the 23 records are one filterable directory on Experiential opportunities (category, education level, duration), as rows with a thumbnail, eight at a time. Each row links where the live card button links; the empty `/opportunities/` detail pages are not rebuilt. The Academic, Professional and Extracurricular pages list their own opportunities as rows without photos.
- **First-year filter**: the live records spell "Undergraduate - 1st year" with a hyphen and the filter spells it with an en dash, so the live filter finds nothing. Staging matches them, so the filter finds its three programs.
- **Statement cut**: the Employer partnerships opening line is shortened to "We help organizations of all sizes discover solutions that fill skills gaps." (words removed, none added, as in the design system's Statement spec); the rest of the paragraph follows in full. Needs the owner's OK.
- **Global experiential network**: the film has its own lettering, so it sits beside the page's intro sentence rather than under a second headline. Campuses are a map with an index grouped by region; the live "Explore our campuses" link sits under the intro.
- **Dropped images**: the photo beside "How experiential learning benefits you" (the seven benefits are a numbered list now) and the eyebrow labels on the six differentiators.
- **Dropped**: hidden placeholder buttons ("Lorem ipsum", "Apply Now", "Plan Your visit"), the "Hello world!" post, the "test 1"/"test 2" category terms.
- **Corrected**: "WHat is experiential learning?" and "study at one our global network hubs"; the Co-op image alt text ("studnet"). Eyebrow labels set in caps are in sentence case.
- **Kept as published, needs an owner's check**: the partner count differs across pages (4,000+ / Over 3,800 / 3,900+, and the home page shows 4,000+ twice for two different figures); "Summer In" links to the Semester In page; "Experiential PhD" is tagged Undergraduate and Short term; the employer form's interest list includes student-only programs.
- **Employer form**: rebuilt with the system's Form organism; on staging it shows a notice instead of sending.
- **Search**: sends the query to the same Google Programmable Search engine the live site uses.
