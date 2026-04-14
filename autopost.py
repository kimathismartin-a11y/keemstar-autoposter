#!/usr/bin/env python3
"""
Keemstar Office Solution Autoposter
Posts to Keemstar Office Solution Facebook page — 14 posts per day.
Focused on office supplies, printer products, ink, toners and office technology.
Triggered by GitHub Actions cron schedule.
"""
import os
import json
import requests
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────
PAGE_ACCESS_TOKEN = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
PAGE_ID           = "337806517458253"  # Keemstar Office Solution Facebook Page
POSTS_FILE        = os.path.join(os.path.dirname(__file__), "posts.json")

# ── Helpers ───────────────────────────────────────────────────────────────────
def load_posts(filepath: str) -> list:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def publish_to_facebook(page_id: str, token: str, message: str) -> dict:
    url     = f"https://graph.facebook.com/v19.0/{page_id}/feed"
    payload = {"message": message, "access_token": token}
    resp    = requests.post(url, data=payload, timeout=30)
    return resp.json()

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not PAGE_ACCESS_TOKEN:
        raise EnvironmentError("Missing secret: FACEBOOK_PAGE_ACCESS_TOKEN")

    posts = load_posts(POSTS_FILE)
    hour  = datetime.utcnow().hour

    print(f"[{datetime.utcnow().isoformat()}] Keemstar Office Solution Autoposter — UTC hour: {hour}")

    # 14 posts per day — map 14 posting hours to post indices
    # Posts go out every ~1.7 hours across the day (UTC 0 to 23)
    POSTING_HOURS = [0, 2, 4, 6, 8, 10, 12, 13, 14, 16, 18, 20, 21, 23]

    if hour not in POSTING_HOURS:
        print(f"UTC hour {hour} is not a posting hour. Skipping.")
        return

    post_index = POSTING_HOURS.index(hour)

    if post_index >= len(posts):
        print(f"No post at index {post_index}. Only {len(posts)} posts in file. Skipping.")
        return

    post = posts[post_index]

    print(f"Publishing post index {post_index} (UTC hour {hour})...")
    print(f"Preview: {str(post['content'])[:100]}...")

    result = publish_to_facebook(PAGE_ID, PAGE_ACCESS_TOKEN, post["content"])

    if "id" in result:
        print(f"SUCCESS — Post published. Facebook ID: {result['id']}")
    else:
        print(f"FAILED — API response: {result}")
        raise RuntimeError(f"Facebook API error: {result}")

if __name__ == "__main__":
    main()
