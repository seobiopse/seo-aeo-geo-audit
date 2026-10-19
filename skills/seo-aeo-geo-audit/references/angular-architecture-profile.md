# Angular Architecture Profile

Site-level audit patterns specific to Angular (v2+) applications. Read whenever the audit target is built with Angular, including Angular Universal (SSR), Angular standalone components, or Ionic (Angular-based mobile web).

**Critical context:** Angular is a client-side framework by default. An Angular app without Angular Universal (or an equivalent SSR/prerender setup) is completely invisible to non-JS crawlers — GPTBot, ClaudeBot, PerplexityBot, CCBot. Even Googlebot sees delayed, degraded content. SSR is not optional for a serious SEO strategy on Angular.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [Rendering modes — CSR vs SSR vs prerendering](#2-rendering-modes)
3. [Angular Universal — SSR setup audit](#3-angular-universal)
4. [Title and Meta service patterns](#4-title-and-meta-service)
5. [Route-level SEO configuration](#5-route-level-seo)
6. [Schema injection in Angular](#6-schema-injection)
7. [Lazy loading and crawlability](#7-lazy-loading)
8. [Transfer State — avoiding double data fetching](#8-transfer-state)
9. [Common anti-patterns](#9-anti-patterns)
10. [Audit checklist](#10-audit-checklist)

---

## 1. When to read this

Load this file when:
- The app uses `@angular/core` (check `package.json` or `angular.json`).
- The page source contains `ng-version="xx"` or `<app-root>` tags.
- The bundle files contain `chunk.js` or `main.*.js` patterns typical of Angular CLI.
- The app uses Ionic Framework (which is Angular-based).

---

## 2. Rendering modes — CSR vs SSR vs prerendering

| Mode | How it works | Crawler result |
|---|---|---|
| **CSR (default)** | Browser downloads a near-empty HTML shell, then Angular bootstraps and renders everything | Non-JS crawlers see `<app-root></app-root>` — empty. Googlebot sees content after delay. |
| **SSR (Angular Universal)** | Server renders the initial HTML response, Angular hydrates on client | All crawlers see full HTML immediately ✅ |
| **Static prerendering** | Angular Universal generates HTML files at build time for known routes | All crawlers see full HTML ✅ Fastest option for content-stable sites |
| **Partial hydration (Angular 17+)** | Islands architecture — some components hydrate, some stay static | Good for CWV; crawlability depends on which content is hydrated |

**Detecting the current mode:**

```bash
curl -s https://example.com/ | grep -o '<app-root>[^<]*</app-root>'
# If this returns <app-root></app-root> — pure CSR, no SSR.
# If this returns <app-root><h1>...</h1>...</app-root> — SSR is active.
```

---

## 3. Angular Universal — SSR setup audit

### Key files to check

```
src/
├── app/
│   ├── app.module.ts              # Client module
│   ├── app.server.module.ts       # Server module (Universal)
│   └── app-routing.module.ts      # Routes
├── server.ts                      # Express server for SSR
└── angular.json                   # Build config
```

### Verify SSR is actually rendering content

```bash
# Simulate a non-JS crawler
curl -H "User-Agent: Googlebot/2.1" https://example.com/ | head -100
# Critical content (H1, main text, nav) should be in this output.
```

### Common Universal misconfiguration

**Server module missing BrowserModule equivalent:**
```typescript
// app.server.module.ts — must import ServerModule
import { ServerModule } from '@angular/platform-server';
@NgModule({
  imports: [AppModule, ServerModule],
  bootstrap: [AppComponent],
})
export class AppServerModule {}
```

**Transfer State not configured (causes double API calls):**
See Section 8.

**Absolute URLs required in SSR:**
Any API calls in SSR context must use absolute URLs. `HttpClient` calls to `/api/data` fail in Node — they have no base URL.

```typescript
// app.module.ts — detect server vs browser
import { isPlatformServer } from '@angular/common';
import { PLATFORM_ID } from '@angular/core';

export function getBaseUrl(platformId: object): string {
  return isPlatformServer(platformId) ? 'http://localhost:4000' : '';
}
```

---

## 4. Title and Meta service patterns

Angular's `Title` and `Meta` services update the DOM — but in SSR, they must also update the server-rendered HTML.

### Correct pattern (Angular Universal compatible)

```typescript
import { Component, OnInit } from '@angular/core';
import { Title, Meta } from '@angular/platform-browser';

@Component({ ... })
export class ProductComponent implements OnInit {
  constructor(private title: Title, private meta: Meta) {}

  ngOnInit(): void {
    this.title.setTitle('Product Name | Site Name');
    this.meta.updateTag({ name: 'description', content: 'Description here.' });
    this.meta.updateTag({ property: 'og:title', content: 'Product Name' });
    this.meta.updateTag({ property: 'og:url', content: 'https://example.com/product/slug' });
    this.meta.updateTag({ rel: 'canonical', href: 'https://example.com/product/slug' });
  }
}
```

### Canonical tag — common Angular gotcha

Angular's `Meta` service does not natively handle `<link rel="canonical">`. Use `DOCUMENT` injection:

```typescript
import { Inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';

constructor(@Inject(DOCUMENT) private doc: Document) {}

setCanonical(url: string): void {
  let link: HTMLLinkElement = this.doc.querySelector("link[rel='canonical']") ||
    this.doc.createElement('link');
  link.setAttribute('rel', 'canonical');
  link.setAttribute('href', url);
  this.doc.head.appendChild(link);
}
```

Wrap this in a service and call it in every route's component `ngOnInit`.

### Route-based title via Angular Router (Angular 14+)

```typescript
// app-routing.module.ts
const routes: Routes = [
  {
    path: 'about',
    component: AboutComponent,
    title: 'About Us | Example',  // Static title
  },
  {
    path: 'products/:slug',
    component: ProductComponent,
    // Dynamic titles handled in the component
  }
];
```

For dynamic titles (based on API data), use a `Resolve` guard to pre-fetch data and set the title before the component renders.

---

## 5. Route-level SEO configuration

### Detecting route changes for SPA SEO

Angular Router is a SPA router — page navigations don't reload the browser, so the title/meta must update on each route change:

```typescript
// app.component.ts
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';

constructor(private router: Router) {
  this.router.events.pipe(
    filter(event => event instanceof NavigationEnd)
  ).subscribe(() => {
    // Trigger meta update for the new route
    // Each page's component handles its own title/meta via ngOnInit
  });
}
```

### Structured route metadata

For larger apps, define SEO metadata in the route data:

```typescript
const routes: Routes = [
  {
    path: 'about',
    component: AboutComponent,
    data: {
      seo: {
        title: 'About Us | Example',
        description: 'Learn about our company.',
        ogImage: '/assets/og/about.jpg'
      }
    }
  }
];
```

Then read it in a service that subscribes to route changes.

---

## 6. Schema injection in Angular

Schema JSON-LD should be in the initial server-rendered HTML. Injecting it client-side means non-JS crawlers don't see it.

### Server-safe schema injection

```typescript
// schema.service.ts
import { Injectable, Inject } from '@angular/core';
import { DOCUMENT } from '@angular/common';

@Injectable({ providedIn: 'root' })
export class SchemaService {
  constructor(@Inject(DOCUMENT) private doc: Document) {}

  addSchema(schema: object): void {
    const script = this.doc.createElement('script');
    script.type = 'application/ld+json';
    script.text = JSON.stringify(schema);
    this.doc.head.appendChild(script);
  }

  removeAllSchemas(): void {
    this.doc.querySelectorAll('script[type="application/ld+json"]')
      .forEach(el => el.remove());
  }
}
```

Call `addSchema()` in `ngOnInit` of each page component. In SSR context, this runs server-side and injects into the HTML response.

---

## 7. Lazy loading and crawlability

Angular's lazy loading splits the app into code chunks loaded on demand. This is good for performance but has SEO implications.

### The problem

Lazy-loaded routes have their content only available after the JS chunk downloads. For non-JS crawlers:
- The route is accessible (Angular Universal renders it)
- BUT if the component makes an API call for its data, that data must also render server-side

### Audit for lazy-loaded routes

```bash
# Check all routes in the app
cat src/app/app-routing.module.ts | grep -A 2 "loadChildren\|loadComponent"
```

For each lazy-loaded route, verify:
1. The route's component renders meaningful content in SSR (not just a loading spinner).
2. API calls in the component are executed server-side (use `TransferState` to pass data to client).

### Prerendering for known routes

For content-stable routes, prerendering is better than runtime SSR:

```json
// angular.json
"prerender": {
  "routes": [
    "/",
    "/about",
    "/services",
    "/contact"
  ],
  "discoverRoutes": true  // discovers routes from sitemap.xml
}
```

---

## 8. Transfer State — avoiding double data fetching

Without Transfer State, an Angular Universal app fetches API data twice: once on the server (for HTML rendering) and once on the client (because Angular doesn't know the server already fetched it). This causes flicker and doubles API load.

### Implementation

```typescript
// data.service.ts
import { TransferState, makeStateKey } from '@angular/platform-browser';
import { isPlatformServer } from '@angular/common';
import { PLATFORM_ID, Inject } from '@angular/core';

const DATA_KEY = makeStateKey<ProductData>('product-data');

@Injectable()
export class ProductService {
  constructor(
    private http: HttpClient,
    private state: TransferState,
    @Inject(PLATFORM_ID) private platformId: object
  ) {}

  getProduct(slug: string): Observable<ProductData> {
    const stateData = this.state.get(DATA_KEY, null);
    if (stateData) {
      this.state.remove(DATA_KEY);
      return of(stateData);  // Use server-fetched data
    }
    return this.http.get<ProductData>(`/api/products/${slug}`).pipe(
      tap(data => {
        if (isPlatformServer(this.platformId)) {
          this.state.set(DATA_KEY, data);  // Store for client pickup
        }
      })
    );
  }
}
```

---

## 9. Common anti-patterns

### 9.1 Pure CSR with no SSR/prerender
The most critical issue. `<app-root></app-root>` in raw HTML. Fix: implement Angular Universal.

### 9.2 `document` and `window` accessed directly
Angular Universal runs in Node — `document` and `window` don't exist server-side. Any component calling `document.querySelector()` directly will crash SSR.

```typescript
// ❌ Breaks SSR
document.querySelector('.hero').style.display = 'none';

// ✅ Safe
import { isPlatformBrowser } from '@angular/common';
if (isPlatformBrowser(this.platformId)) {
  document.querySelector('.hero').style.display = 'none';
}
```

### 9.3 setTimeout/setInterval in SSR context
These don't resolve in Node's event loop during SSR rendering. The server hangs waiting for them. Use `isPlatformBrowser` guard.

### 9.4 Meta tags only set on NavigationEnd (client-side)
If meta tags are only updated on the client-side router event, the initial server render has no page-specific meta. The HTML response has the default meta, not the page's meta.

### 9.5 Hardcoded `localhost` in SSR API calls
SSR runs on a Node server — relative URLs like `/api/data` don't work. All API calls in SSR must use absolute URLs.

### 9.6 Angular animations blocking hydration
Complex Angular animations can delay hydration and cause CLS (layout shifts). Audit animations on above-the-fold components.

### 9.7 Missing `provideClientHydration()` (Angular 17+)
Angular 17 introduced improved hydration. Without `provideClientHydration()` in `app.config.ts`, SSR HTML is destroyed and re-rendered by the client, causing flicker and wasted rendering.

---

## 10. Audit checklist

- **NG-1** Raw HTML check: `curl -s https://example.com/ | grep -o '<app-root>[^<]*'` returns content (not empty). If empty → pure CSR, no SSR. **Critical SEO gap.**
- **NG-2** SSR (Angular Universal) or static prerendering is active. Verify `server.ts` or prerender config exists.
- **NG-3** Canonical tag injected server-side. Check: `curl -s https://example.com/product/slug | grep canonical` returns the correct URL in the initial HTML.
- **NG-4** `<title>` is page-specific in the initial HTML response. Not the app default title on every page.
- **NG-5** `<meta name="description">` is page-specific in the initial HTML response.
- **NG-6** OpenGraph tags present in server-rendered HTML. `curl -s https://example.com/product/slug | grep og:`.
- **NG-7** Schema JSON-LD present in server-rendered HTML (not injected client-side). `curl -s https://example.com/ | grep "application/ld+json"`.
- **NG-8** No `document is not defined` or `window is not defined` errors in SSR logs.
- **NG-9** No hardcoded `localhost` URLs in SSR API calls. Check `server.ts` and any SSR-context service.
- **NG-10** TransferState implemented for data-fetching services to prevent double API calls.
- **NG-11** Lazy-loaded routes render meaningful content server-side (not just `<loading-spinner>`).
- **NG-12** `provideClientHydration()` included in `app.config.ts` (Angular 17+). Check: no full DOM tear-down visible in DevTools Elements panel on page load.
- **NG-13** Non-JS crawlers see full content. `curl -H "User-Agent: GPTBot" https://example.com/ | grep -c "<p>"` — paragraph count should be > 0.
- **NG-14** JS-disabled in Chrome: page renders meaningful content (tests SSR output without hydration).
- **NG-15** All routes have unique `<title>` tags in the server response. Spot-check 5 routes.
- **NG-16** `sitemap.xml` exists with all indexable routes. Routes with dynamic segments (`:slug`) resolve via prerendering or runtime SSR.
- **NG-17** HTTP → HTTPS redirect active. `curl -sIL http://example.com/ | head -4`.
- **NG-18** No Angular animations causing CLS on above-the-fold components. CLS < 0.1 in Lighthouse.
- **NG-19** LCP < 2.5s on mobile (Lighthouse). Primary blocker is usually the JS bundle size — check for large, non-lazy-loaded dependencies.
- **NG-20** `robots.txt` allows Googlebot and key AI crawlers. Does not accidentally disallow `/assets/` or Angular's compiled JS bundles.
