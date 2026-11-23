"""Orphan page guard — ADR-012, requisito 2.4.

MkDocs strict mode treats pages outside the nav as INFO (verified
empirically: exit 0).  This hook escalates orphan pages to WARNING so
``mkdocs build --strict`` itself aborts — documentation without navigation
is lost content.  Pages excluded via ``exclude_docs`` never reach ``files``
and virtual gen-files pages are part of the nav, so neither is flagged.
"""

from __future__ import annotations

import logging

log = logging.getLogger("mkdocs.plugins.orphan_guard")


def on_nav(nav, config, files):
    in_nav = {page.file.src_uri for page in nav.pages}
    for file in files:
        if not file.is_documentation_page():
            continue
        # exclude_docs surfaces stay in `files` flagged as EXCLUDED —
        # they are intentionally out of the public site, never orphans.
        if file.inclusion.is_excluded():
            continue
        if file.src_uri not in in_nav:
            log.warning("Orphan page not in nav: %s", file.src_uri)
    return nav
