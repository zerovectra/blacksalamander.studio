# blacksalamander.studio

Static marketing site for Black Salamander Studio. No build step, no dependencies,
no JavaScript. Everything served is exactly what is in `public/`.

```
public/
  index.html        landing page (the whole site)
  404.html          not-found page, styled from the same stylesheet
  assets/
    styles.css      all styling
    favicon.svg     placeholder salamander mark
  _headers          security + cache headers (Cloudflare Pages)
  _redirects        www -> apex redirect (Cloudflare Pages)
  robots.txt
  sitemap.xml
```

## Local preview

Any static file server works. From the repo root:

```powershell
py -m http.server 8080 --directory public
```

then open <http://localhost:8080>. Opening `public/index.html` straight from disk
mostly works, but the absolute `/assets/...` paths will not resolve, so use the
server.

## Deploy to Cloudflare Pages

### Option A, Git integration (recommended)

1. Push this folder to a GitHub repo.
2. Cloudflare dashboard > Workers & Pages > Create > Pages > Connect to Git.
3. Build settings:
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: **`public`**
   - Root directory: *(leave empty, unless the repo has this project in a subfolder)*
4. Deploy. Every push to the production branch redeploys; other branches get preview URLs.

### Option B, direct upload with Wrangler

```powershell
npm install -g wrangler
wrangler login
wrangler pages deploy public --project-name blacksalamander-studio
```

### Custom domain

In the Pages project > Custom domains, add `blacksalamander.studio` and
`www.blacksalamander.studio`. Cloudflare adds the DNS records automatically when
the domain is already in the same Cloudflare account. The `www` to apex redirect
in `_redirects` only fires once `www` is attached to the project.

## Things left to fill in

Search the HTML for `TODO(kj)`:

- **Discord invite** in the contact section is `https://discord.gg/REPLACE-ME`.
- **Email** is `hello@blacksalamander.studio`, which needs a mailbox (Cloudflare
  Email Routing can forward it) or swap in a different address.
- **Project copy** was drafted from the project files, not dictated, so read the
  three blurbs and correct anything that misstates the plan. The Bleak Isles entry
  in particular guesses at framing.
- **`assets/og.png`** is referenced by the Open Graph tags but does not exist yet.
  Add a 1200x630 image for link previews, or delete the `og:image` and
  `twitter:card` tags.
- **The salamander mark** in the header and favicon is a placeholder drawn in code.
  Replace with real art when there is some.

## Conventions

- No em dashes in any visible copy, matching the Bleak Isles content rule.
- Dark theme only, declared via `color-scheme: dark`. Colors live as custom
  properties at the top of `styles.css`.
- Layout is responsive down to 360px with a 20px gutter.
