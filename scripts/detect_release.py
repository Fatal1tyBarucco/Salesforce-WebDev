#!/usr/bin/env python3
"""Detect new Salesforce release - used by scheduled-pipeline workflow."""

import os
import sys
import traceback

sys.path.insert(0, ".")

import asyncio

from src.release_discovery import ReleaseDiscoveryService
from src.scraper import SalesforceReleaseScraper


async def main() -> int:
    try:
        scraper = SalesforceReleaseScraper()
        disco = ReleaseDiscoveryService(scraper)
        releases = await disco.discover()
    except Exception as e:
        # On any error (network, rate limit, parsing), assume no new release
        # This prevents scheduled pipeline from failing due to transient issues
        print(f"[detect_release] Error during discovery: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("has-new-release=false")
        return 0

    # Check if specific release_slug was provided via env var
    target_slug = os.environ.get("TARGET_SLUG", "")
    if target_slug:
        for r in releases:
            if r.slug == target_slug:
                print("has-new-release=true")
                print(f"release-slug={r.slug}")
                print(f"release-name={r.name}")
                return 0
        print("has-new-release=false")
        return 0

    # Normal: return first release
    if releases:
        r = releases[0]
        print("has-new-release=true")
        print(f"release-slug={r.slug}")
        print(f"release-name={r.name}")
    else:
        print("has-new-release=false")

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
