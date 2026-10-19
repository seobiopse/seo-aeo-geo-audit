# PHP Architecture Profile

Site-level audit patterns for PHP-based sites — Laravel, Symfony, CodeIgniter, Slim, or custom PHP. Read whenever the audit target runs on PHP without WordPress (use `wordpress-architecture-profile.md` for WordPress specifically).

**Key advantage:** PHP is server-rendered by default. Unlike React or Angular, every PHP page serves full HTML on the first request. Crawlers see everything immediately. The SEO issues here are structural — URL routing, caching layers, duplicate content from query parameters, and session handling.

## Table of contents

1. [When to read this](#1-when-to-read-this)
2. [URL routing and clean URLs](#2-url-routing)
3. [Meta and schema injection patterns](#3-meta-and-schema)
4. [Caching layers and crawlability](#4-caching-layers)
5. [Session-based URLs — a critical SEO risk](#5-session-urls)
6. [Laravel-specific patterns](#6-laravel)
7. [Symfony-specific patterns](#7-symfony)
8. [Common anti-patterns](#8-anti-patterns)
9. [Audit checklist](#9-audit-checklist)

---

## 1. When to read this

Load this file when:
- `composer.json` is present in the repo.
- Response headers contain `X-Powered-By: PHP` or similar.
- URL patterns suggest a PHP framework (`/public/`, `/index.php?route=`, `artisan` commands).
- The site uses Laravel (check for `/storage/`, `App\Http\Controllers`), Symfony (`/var/`, `bin/console`), CodeIgniter (`/application/`, `/system/`), or custom PHP.

Do NOT use for WordPress (separate profile) or PHP sites running a Shopify-compatible setup.

---

## 2. URL routing and clean URLs

PHP sites commonly expose URLs with query parameters or `index.php` in the path — both are SEO anti-patterns.

### Check for index.php in URLs

```bash
curl -sI https://example.com/index.php/about | head -5
# Should 301 to https://example.com/about — not serve the page directly
```

### .htaccess for Apache (remove index.php)

```apache
# .htaccess
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ index.php?$1 [L,QSA]

# Redirect index.php URLs to clean versions
RewriteCond %{THE_REQUEST} \s/.*index\.php[/\s]
RewriteRule ^index\.php/?(.*)$ /$1 [R=301,L]
```

### Nginx configuration (clean URLs)

```nginx
location / {
    try_files $uri $uri/ /index.php?$query_string;
}

# Redirect index.php to clean URL
location ~ ^/index\.php/(.*)$ {
    return 301 /$1;
}
```

### URL structure best practices for PHP frameworks

- Use slugs, not IDs: `/blog/post-title` not `/blog?id=123`
- Lowercase, hyphen-separated: `/product-category/item-name`
- No file extensions: `/about` not `/about.php`
- Consistent trailing slash: pick one and redirect the other

---

## 3. Meta and schema injection patterns

PHP is server-rendered, so meta and schema injection is straightforward — no hydration concerns.

### Laravel Blade — meta injection

```blade
{{-- layouts/app.blade.php --}}
<!DOCTYPE html>
<html lang="{{ app()->getLocale() }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', config('app.name'))</title>
    <meta name="description" content="@yield('description', config('seo.default_description'))">
    <link rel="canonical" href="@yield('canonical', url()->current())">
    <meta property="og:title" content="@yield('og_title', @yield('title'))">
    <meta property="og:description" content="@yield('og_description', @yield('description'))">
    <meta property="og:url" content="@yield('canonical', url()->current())">
    <meta property="og:image" content="@yield('og_image', asset('images/og-default.jpg'))">
    @yield('schema')
</head>
```

In a child view:
```blade
@extends('layouts.app')
@section('title', $product->name . ' | ' . config('app.name'))
@section('description', Str::limit($product->description, 160))
@section('canonical', route('products.show', $product->slug))
@section('og_image', Storage::url($product->og_image ?? 'defaults/og.jpg'))
@section('schema')
<script type="application/ld+json">
{!! json_encode([
    '@context' => 'https://schema.org',
    '@type' => 'Product',
    'name' => $product->name,
    'description' => $product->description,
    'offers' => [
        '@type' => 'Offer',
        'price' => $product->price,
        'priceCurrency' => 'USD',
        'availability' => $product->in_stock
            ? 'https://schema.org/InStock'
            : 'https://schema.org/OutOfStock',
    ],
], JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) !!}
</script>
@endsection
```

### Symfony Twig — meta injection

```twig
{# templates/base.html.twig #}
<!DOCTYPE html>
<html lang="{{ app.request.locale }}">
<head>
    <title>{% block title %}{{ site_name }}{% endblock %}</title>
    <meta name="description" content="{% block description %}{{ site_description }}{% endblock %}">
    <link rel="canonical" href="{% block canonical %}{{ app.request.uri }}{% endblock %}">
    {% block schema %}{% endblock %}
</head>
```

---

## 4. Caching layers and crawlability

PHP sites commonly use Varnish, Nginx FastCGI cache, or application-level caches (Redis, Memcached). Misconfigurations can serve stale, wrong, or no content to crawlers.

### Verify correct cache behaviour for crawlers

```bash
# First hit — should be MISS or BYPASS
curl -sI https://example.com/ | grep -i "x-cache\|x-varnish"

# Second hit — should be HIT
curl -sI https://example.com/ | grep -i "x-cache\|x-varnish"
```

### Common caching SEO issues

**1. Vary header not set for user-agent based content:**
If your site serves different content to mobile vs desktop (separate templates), the cache must vary on `User-Agent`. Missing this causes crawlers to get the cached desktop response with mobile meta tags (or vice versa):

```apache
Header always set Vary "User-Agent"
```

**2. Session-based cache bypass:**
PHP sessions can cause every request to bypass the cache (because each session is unique). See Section 5.

**3. Cache serving 404 pages as 200:**
After deleting content, the cache may still serve the old page. Set short TTLs on pages that might be deleted, or add a cache purge on deletion.

**4. Cache headers for crawlers:**

```php
// Laravel — set proper cache headers for public pages
Route::middleware(['cache.headers:public;max_age=3600;etag'])->group(function () {
    Route::get('/products/{slug}', [ProductController::class, 'show']);
});
```

---

## 5. Session-based URLs — a critical SEO risk

PHP's default session handling can append session IDs to URLs or store them in cookies. Session IDs in URLs create infinite duplicate content:

```
# Same page, infinite URL variants:
/products/widget?PHPSESSID=abc123
/products/widget?PHPSESSID=def456
/products/widget  ← canonical
```

### Check if session IDs appear in URLs

```bash
curl -c /tmp/cookies.txt -s https://example.com/ > /dev/null
curl -b /tmp/cookies.txt -s https://example.com/products/widget -v 2>&1 | grep "Location\|PHPSESSID"
```

### Fix: use cookies only, never URL sessions

```ini
# php.ini
session.use_only_cookies = 1
session.use_trans_sid = 0
```

Or in PHP code:
```php
ini_set('session.use_only_cookies', 1);
ini_set('session.use_trans_sid', 0);
session_start();
```

---

## 6. Laravel-specific patterns

### Route model binding and canonical URLs

Laravel's route model binding automatically resolves slugs:

```php
// routes/web.php
Route::get('/products/{product:slug}', [ProductController::class, 'show'])
    ->name('products.show');
```

Always generate canonical URLs using named routes:
```php
// In the controller/view
$canonical = route('products.show', $product->slug);
```

Never hardcode URLs — they break on environment changes.

### Sitemap generation

Use `spatie/laravel-sitemap`:

```php
// SitemapController.php
use Spatie\Sitemap\Sitemap;
use Spatie\Sitemap\Tags\Url;

Sitemap::create()
    ->add(Url::create('/')->setChangeFrequency('monthly')->setPriority(1.0))
    ->add(Product::all()->map(fn($p) => Url::create("/products/{$p->slug}")
        ->setLastModificationDate($p->updated_at)
        ->setPriority(0.8)
    ))
    ->writeToFile(public_path('sitemap.xml'));
```

Schedule this to regenerate on content changes, not on every request.

### N+1 query issue affecting TTFB

Laravel's Eloquent ORM is susceptible to N+1 queries that slow page response times, directly hurting TTFB and thus Core Web Vitals. Audit:

```php
// Use Laravel Debugbar or Telescope to count queries per page
// Or in production, log slow queries:
DB::listen(function($query) {
    if ($query->time > 100) {
        Log::warning("Slow query: {$query->sql} ({$query->time}ms)");
    }
});
```

Fix with eager loading: `Product::with(['category', 'images', 'reviews'])->where(...)`.

---

## 7. Symfony-specific patterns

### Route generation for canonical URLs

Always use Symfony's Router for URL generation:

```php
// In a controller
use Symfony\Component\Routing\Generator\UrlGeneratorInterface;

$canonical = $this->generateUrl('product_show', ['slug' => $product->getSlug()],
    UrlGeneratorInterface::ABSOLUTE_URL);
```

### Symfony HTTP cache

Symfony has a built-in reverse proxy (HttpCache). Configure cache headers on responses:

```php
// ProductController.php
public function show(Product $product): Response
{
    $response = new Response();
    $response->setPublic();
    $response->setMaxAge(3600);
    $response->setLastModified($product->getUpdatedAt());
    $response->setEtag(md5($product->getUpdatedAt()->format('U')));

    if ($response->isNotModified($this->container->get('request_stack')->getCurrentRequest())) {
        return $response;  // 304 Not Modified — fast for returning crawlers
    }
    // ... render
}
```

---

## 8. Common anti-patterns

### 8.1 `index.php` visible in URLs
`https://example.com/index.php/about` should 301 to `/about`. Indicates mod_rewrite is not configured.

### 8.2 Query string parameters creating duplicate content
`/products?sort=price&page=1` and `/products?sort=name&page=1` are different URLs but the same semantic page. Canonicalise all filter/sort/pagination variants to the base URL.

### 8.3 Session IDs in URLs
`PHPSESSID=abc123` in any public URL. Covered in Section 5.

### 8.4 Error pages returning wrong HTTP status codes
A custom "404 page" that returns HTTP 200 causes Googlebot to index it. Always return the correct status.

```php
// Laravel
abort(404);  // Returns HTTP 404

// Symfony
throw $this->createNotFoundException('Product not found');  // Returns HTTP 404
```

### 8.5 Mixed HTTP/HTTPS URLs in page source
Any `http://` URL in `href`, `src`, or schema properties is a mixed-content warning that browsers suppress. Check:

```bash
curl -s https://example.com/products/widget | grep -oP 'src="http://[^"]*"'
```

### 8.6 Missing `X-Robots-Tag` on API endpoints
PHP APIs (`/api/products.json`, `/api/data`) should return `X-Robots-Tag: noindex`:

```php
// Laravel API controller
return response()->json($data)->header('X-Robots-Tag', 'noindex, nofollow');
```

### 8.7 Debug mode enabled in production
`APP_DEBUG=true` in Laravel or `APP_ENV=dev` in Symfony exposes stack traces, error messages, and sometimes partial HTML that Googlebot can index. Always `false` in production.

### 8.8 Direct database queries in views
N+1 queries in Blade/Twig templates slow TTFB significantly. Move all queries to controllers and pass data to views.

---

## 9. Audit checklist

- **PHP-1** No `index.php` visible in URLs. `curl -sI https://example.com/index.php/page` returns 301.
- **PHP-2** No `PHPSESSID` or session identifiers in any public URL. `curl -c /tmp/c.txt -b /tmp/c.txt -v https://example.com/ 2>&1 | grep -i "phpsessid\|session"` in URL.
- **PHP-3** HTTP → HTTPS redirect active. `curl -sIL http://example.com/ | head -4` shows 301 to `https://`.
- **PHP-4** `www` / non-www redirect consistent. `curl -sIL http://www.example.com/ | head -4`.
- **PHP-5** Query-string filtered URLs (`?sort=`, `?page=`, `?filter=`) have canonical pointing to base URL.
- **PHP-6** `<title>`, `<meta name="description">`, and canonical are page-specific (not default values on every page). Spot-check 5 different pages.
- **PHP-7** Schema JSON-LD present and correct for page type. Run 2 pages through Rich Results Test.
- **PHP-8** 404 pages return HTTP 404. `curl -sI https://example.com/this-does-not-exist | head -1`.
- **PHP-9** Error pages don't expose stack traces or debug info. `curl -s https://example.com/this-does-not-exist | grep -i "exception\|laravel\|symfony\|stack trace"`.
- **PHP-10** No `http://` URLs in page source. `curl -s https://example.com/ | grep -oP 'href="http://' | wc -l` returns 0.
- **PHP-11** API endpoints return `X-Robots-Tag: noindex`. `curl -sI https://example.com/api/data | grep -i "x-robots"`.
- **PHP-12** Sitemap at `/sitemap.xml` HTTP 200. All URLs return HTTP 200 (spot-check 10).
- **PHP-13** `<lastmod>` in sitemap reflects `updated_at` database field, not build/deploy date.
- **PHP-14** Cache headers correct for public pages. `curl -sI https://example.com/products/widget | grep -i "cache-control"` — should include `public` and `max-age`.
- **PHP-15** TTFB < 500ms for non-cached requests. `curl -w "%{time_starttransfer}" -s https://example.com/ -o /dev/null`.
- **PHP-16** N+1 queries not present on key landing pages. Check via query log or Debugbar.
- **PHP-17** `APP_DEBUG=false` / debug mode off in production. `curl -s https://example.com/non-existent` does not show stack traces.
- **PHP-18** `robots.txt` HTTP 200, contains `Sitemap:` directive, does not `Disallow: /`.
- **PHP-19** HSTS header present. `curl -sI https://example.com/ | grep -i "strict-transport"`.
- **PHP-20** `/api/` paths or any non-HTML endpoints blocked in robots.txt or returning `X-Robots-Tag: noindex`.
