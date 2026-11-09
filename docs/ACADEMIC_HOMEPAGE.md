# Academic homepage

The public homepage now uses a site-specific, single-page academic design inspired by the layout of https://heyuanmingong.github.io/. It retains the existing Jekyll build and GitHub Pages address.

## Editing content

- Biography: `_pages/about.md`.
- Research topics, education highlights, and service: `_includes/academic-home.liquid`.
- Papers, author order, contribution markers, venues, links, and thumbnails: `_bibliography/papers.bib` and `assets/img/publication_preview/`.
- News: `_news/`. The newest five items appear first; older items are expandable.
- CV and its existing PDF generator: `_data/cv.yml`.
- Contact and profile links: `_data/socials.yml`.
- Reading lists: `_includes/academic-resources.liquid`.
- Additional repositories: `_data/repositories.yml`.

The `/publications/`, `/news/`, `/cv/`, `/projects/`, and `/repositories/` URLs use the same visual design. Existing content files and downloadable assets remain available. The navigation shows only the sections relevant to this academic profile.

## Implementation

`_layouts/academic.liquid` is the page shell. `_layouts/academic-bib.liquid` is an explicit Jekyll Scholar bibliography template. Both are new, site-owned names; they do not shadow plugin-owned layouts. Their includes use the `academic-` prefix. Styles and progressive navigation behavior live under `assets/academic/`, separate from al-folio assets. The new design does not load external fonts, icon packages, analytics, or client-side rendering libraries.

No changes to the existing deployment workflow are required. Run the existing `bundle exec jekyll build` to generate the site. The browser receives complete HTML; publications, BibTeX disclosures, and the mobile menu also work without JavaScript.
