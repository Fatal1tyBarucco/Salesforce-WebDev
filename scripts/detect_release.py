#!/usr/bin/env python3
"""Detect new Salesforce release - used by scheduled-pipeline workflow."""

import os
import sys

sys.path.insert(0, ".")

import asyncio

from src.release_discovery import ReleaseDiscoveryService
from src.scraper import SalesforceReleaseScraper


async def main():
    scraper = SalesforceReleaseScraper()
    disco = ReleaseDiscoveryService(scraper)
    releases = await disco.discover()

    # Check if specific release_slug was provided via env var
    target_slug = os.environ.get("TARGET_SLUG", "")
    if target_slug:
        for r in releases:
            if r.slug == target_slug:
                print("has-new-release=true")
                print(f"release-slug={r.slug}")
                print(f"release-name={r.name}")
                return
        print("has-new-release=false")
        return

    # Normal: return first release
    if releases:
        r = releases[0]
        print("has-new-release=true")
        print(f"release-slug={r.slug}")
        print(f"release-name={r.name}")
    else:
        print("has-new-release=false")


if __name__ == "__main__":
    asyncio.run(main())
