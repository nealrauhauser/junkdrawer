#!/usr/bin/env python3
# pip install requests beautifulsoup4
import csv
import sys
import time
import urllib.parse as up
from typing import List, Dict, Tuple

import requests
from bs4 import BeautifulSoup

TIMEOUT = 20
SLEEP   = 0.2  # polite throttle between requests
HEADERS = {"User-Agent": "PostLinkHarvester/1.0 (+https://example.com)"}


def norm_site(site: str) -> Tuple[str, str]:
    """Return (full_base_url, hostname)"""
    if not site.startswith(("http://", "https://")):
        site = "https://" + site
    parts = up.urlsplit(site)
    base = f"{parts.scheme}://{parts.netloc}"
    host = parts.netloc
    return base, host


def fetch_posts_via_wpcom_api(hostname: str) -> List[Dict]:
    """
    WordPress.com API:
      https://public-api.wordpress.com/wp/v2/sites/{site}/posts?per_page=100&page=N
    Works for sites hosted on WordPress.com (including custom mapped domains).
    """
    posts = []
    page = 1
    while True:
        url = f"https://public-api.wordpress.com/wp/v2/sites/{hostname}/posts"
        params = {"per_page": 100, "page": page, "_fields": "id,link,date"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 404:
            # Not a WP.com site or private
            return []
        if r.status_code == 401:
            # Private/protected
            return []
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        page += 1
        time.sleep(SLEEP)
    return posts


def fetch_posts_via_site_rest(base_url: str) -> List[Dict]:
    """
    Self-hosted (or WP.com sites with REST exposed at site domain):
      {base}/wp-json/wp/v2/posts?per_page=100&page=N
    """
    posts = []
    page = 1
    while True:
        url = f"{base_url}/wp-json/wp/v2/posts"
        params = {"per_page": 100, "page": page, "_fields": "id,link,date"}
        r = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code in (401, 403, 404):
            return []
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        posts.extend(batch)
        page += 1
        time.sleep(SLEEP)
    return posts


def scrape_posts_from_paged_lists(base_url: str, max_empty=2) -> List[str]:
    """
    Dumb but reliable fallback:
      crawl /page/N (and /?paged=N as a backup) until we hit consecutive empties.
    Extract permalinks from common theme selectors.
    """
    links = set()

    def extract_links(html: str):
        soup = BeautifulSoup(html, "html.parser")
        # Common WP theme patterns for post permalinks
        candidates = []
        candidates += [a.get("href") for a in soup.select("a[rel=bookmark]")]
        candidates += [a.get("href") for a in soup.select("h1.entry-title a, h2.entry-title a, h3.entry-title a")]
        candidates += [a.get("href") for a in soup.select("article a.permalink, article a.more-link")]
        # Deduplicate and keep only same-site absolute links
        for href in candidates:
            if not href:
                continue
            u = up.urlsplit(href)
            if not u.scheme:
                # make absolute
                href = up.urljoin(base_url, href)
                u = up.urlsplit(href)
            if f"{u.scheme}://{u.netloc}".rstrip("/") != base_url.rstrip("/"):
                continue
            links.add(href.split("#")[0].rstrip("/"))

    # Try the homepage first (some sites show many posts there)
    r = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
    if r.ok:
        extract_links(r.text)

    empty_streak = 0
    page = 1
    while empty_streak < max_empty:
        # Try /page/N
        url1 = f"{base_url}/page/{page}/"
        r1 = requests.get(url1, headers=HEADERS, timeout=TIMEOUT)
        got_any = False
        if r1.ok and r1.text:
            before = len(links)
            extract_links(r1.text)
            got_any = len(links) > before

        # If nothing from /page/N, try ?paged=N
        if not got_any:
            url2 = f"{base_url}/?paged={page}"
            r2 = requests.get(url2, headers=HEADERS, timeout=TIMEOUT)
            if r2.ok and r2.text:
                before = len(links)
                extract_links(r2.text)
                got_any = len(links) > before

        if got_any:
            empty_streak = 0
        else:
            empty_streak += 1

        page += 1
        time.sleep(SLEEP)

        # Safety valve: don’t loop forever on weird sites
        if page > 2000:
            break

    return sorted(links)


def harvest_all_post_links(site: str) -> List[str]:
    base_url, hostname = norm_site(site)

    # 1) Try WordPress.com REST (works for *.wordpress.com and custom domains hosted on WP.com)
    try:
        wpcom_posts = fetch_posts_via_wpcom_api(hostname)
        if wpcom_posts:
            return sorted({p["link"].split("#")[0].rstrip("/") for p in wpcom_posts})
    except Exception as e:
        print(f"[warn] WP.com API attempt failed: {e}", file=sys.stderr)

    # 2) Try site-local REST
    try:
        site_posts = fetch_posts_via_site_rest(base_url)
        if site_posts:
            return sorted({p["link"].split("#")[0].rstrip("/") for p in site_posts})
    except Exception as e:
        print(f"[warn] Site REST attempt failed: {e}", file=sys.stderr)

    # 3) Fallback: scrape paged archives
    print("[info] Falling back to HTML pagination scrape…", file=sys.stderr)
    return scrape_posts_from_paged_lists(base_url)


def write_csv(paths: List[str], out_path: str = "post_links.csv"):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["url"])
        for url in paths:
            w.writerow([url])


def main():
    if len(sys.argv) != 2:
        print("Usage: python get_wp_post_links.py <wordpress_site_url_or_hostname>", file=sys.stderr)
        print("Example: python get_wp_post_links.py myblog.wordpress.com", file=sys.stderr)
        print("         python get_wp_post_links.py https://example.com", file=sys.stderr)
        sys.exit(1)

    site = sys.argv[1]
    links = harvest_all_post_links(site)
    write_csv(links, "post_links.csv")
    print(f"Found {len(links)} posts. Wrote post_links.csv")


if __name__ == "__main__":
    main()

