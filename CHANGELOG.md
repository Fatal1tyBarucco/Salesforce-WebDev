# Changelog

<!-- gerado por IA em 2026-11-19T17:40:05+00:00 — revisar antes de publicar -->

## [0.6.0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.5.0...v0.6.0) (2026-11-20)


### Features

* **docs:** fechamento das lacunas da auditoria rigorosa (3.1/4.4/3.4/DoD5/2.4/3.6/4.2/1.4) ([#423](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/423)) ([da00ac8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/da00ac85c3eb0a262cb9c1635de5b9932e9a0528))


### Bug Fixes

* **docs:** full-history checkout + ledger pre-fetch + retry for mike push (shallow checkout rejected gh-pages updates) ([b8122b6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b8122b61ddcf99fd19c2ae01d935247202fde772))
* **docs:** mike ledger fetch — full-history checkout + retry ([#421](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/421)) ([b8122b6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b8122b61ddcf99fd19c2ae01d935247202fde772))


### Documentation

* **sync:** reconcile documentation — 2026-11-19 21:42 UTC [skip ci] ([23ffbac](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/23ffbac4af610c191cb65362f978f6eb11295774))

## [0.5.0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.4.2...v0.5.0) (2026-11-19)


### Features

* **docs:** Sincronia Absoluta da GitHub Pages — contrato verificável + publicação moderna (ADR-012) ([#418](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/418)) ([a7032c6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a7032c6f328666821e0920a1fdc8c67046a7c858))


### Bug Fixes

* **docs:** reconcile before contract gate in build — eliminate sync/build race on stale baseline ([a6fe95f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a6fe95fad7b1346096b95612e7903f4e95480967))
* **docs:** reconcile before contract gate in build (sync/build race) ([#420](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/420)) ([a6fe95f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a6fe95fad7b1346096b95612e7903f4e95480967))


### Documentation

* **sync:** reconcile documentation — 2026-11-19 18:48 UTC [skip ci] ([8397b61](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8397b61b9ab12e07b87f10572096163b410f97e6))
* **sync:** reconcile documentation — 2026-11-19 21:06 UTC [skip ci] ([7df455c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7df455c486a05f76381d3aff0a567ed7f6a955b6))

## [0.4.2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.4.1...v0.4.2) (2026-11-19)


### Bug Fixes

* **ci:** eliminate post-release uv.lock desync failure window ([91889b7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/91889b72741326c03863cf4524e87c3218725d37))


### Documentation

* **agents:** record post-release lock desync fix + skip-ci message pitfall ([753a2d5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/753a2d5b4d77a38e3e9e5eedd2c2d0c752e00ecb))
* **sync:** reconcile documentation — 2026-11-19 18:26 UTC [skip ci] ([b92fa5f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b92fa5fce76ed0d98e9d331b960ecf91bdedb0ac))

## [0.4.1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.4.0...v0.4.1) (2026-11-19)


### Bug Fixes

* **ci:** permanent stabilization — stop bot/release/hook volatility cascade ([36cc885](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/36cc885450d4ec2a71e9809cc076d44a6a78ac21))
* **docs:** ruff format SOURCE_SCHEMA.md code block + refresh manifest ([8364428](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8364428e6d391b3c9f6dad3dd9601ce8e25c0feb))


### Documentation

* **agents:** record permanent CI stabilization conventions ([7bf31a6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7bf31a6983e57886ba91943ddf6b6edb2b5b63f1))
* **sync:** reconcile documentation — 2026-11-19 17:47 UTC ([da223cc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/da223cc3fdbb9d208a0fdd8757d33b2893513559))

## [Unreleased]

### Fixed
- Fix `ai-docs` workflow summary generation: replaced invalid GHA expression `${PUBLISH_MODE == 'pr' && ...}` in bash with shell conditional using `HAS_CHANGES` env var (from publish step output) and explicit `PUBLISH_MODE` check, resolving "bad substitution" error.

### Documentation
- Reconcile documentation manifest (`docs/.documentation-manifest.json`) and drift report (`drift_report.json`): add mappings for new files (e.g., `.github/scripts/ci-visual.sh`), update SHAs for multiple files (AGENTS.md, CHANGELOG.md, docs/ai-generated/*), and fix `MANIFEST_STALE_SHA` drift entries.
- Record mkdocs plugin dependencies and `ruff-format-in-markdown` pitfalls in AGENTS.md for AI agents and developers.
- Automated AI documentation update (commit 33ccab3): likely updates `docs/ai-generated/release-notes.md`, `leadership.md`, `roadmap.md` — **requires human review** as diff is not available in provided data.

<!-- gerado por IA em 2026-11-19T17:26:25+00:00 — revisar antes de publicar -->

## [0.4.0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.3.2...v0.4.0) (2026-11-19)


### Features

* **cache:** harden cache layer — atomic writes, locks, integrity, fingerprints (ADR-011) ([#410](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/410)) ([8e7a3ee](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8e7a3eedeb57be8f12a55ee8cc6b4f3bf8feaedb))


### Bug Fixes

* **ci:** ai-docs rebase before push — avoid non-fast-forward race with Documentation Sync ([603799e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/603799e9c0a2297c51a99da1ffe35f96cb0e51a1))
* **ci:** ai-docs summary — replace GHA expression inside bash with shell conditional ([fb52904](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fb529047df062c4434479d2e35907efb5eb4987e))
* **docs:** repair Deploy Docs — missing mkdocs plugin deps + corrupted SOURCE_SCHEMA fences ([8d529fa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8d529fa93e7c6d5094091736a5956ee6ffcff48c))


### Documentation

* **agents:** record mkdocs plugin deps + ruff-format-in-markdown pitfalls ([5f506e5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5f506e5b31edd154a7b67fcf4cd482e3df1b9fe5))
* atualização automática via IA [skip ci] ([33ccab3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/33ccab373fb14148cce815133b7cd26f5dd518d6))
* **sync:** reconcile documentation — 2026-11-19 01:07 UTC ([271c925](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/271c92530061bae1a2f4c62622a94a4cca5b502b))
* **sync:** reconcile documentation — 2026-11-19 16:48 UTC ([7df34b8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7df34b8c7090f008f54f595a4b47e268cc9aea59))
* **sync:** reconcile documentation — 2026-11-19 17:17 UTC ([6cbbd12](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6cbbd1255f4c6b090e68e43427826b715388c361))
* **sync:** reconcile documentation — 2026-11-19 17:26 UTC ([12625dd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/12625ddc60e6942a12a4ad8bc1e3557597ec45e5))

## [Unreleased]

### Security
- Harden `ci-repair` workflow against `workflow_run` code-injection and untrusted-checkout (CodeQL critical/high alerts): jobs now run only for same-repository events, no fork payload fields are interpolated into `run:` blocks, and lock files / multiprocess test counters use owner-only (`0o600`) permissions.
- Fix gitleaks config to use proper RE2 regex instead of unsupported glob patterns, restoring effective secret detection.

### Added
- Harden cache layer (ADR-011): atomic writes (temp+fsync+os.replace), per-entry/namespace `FileLock` with fcntl/msvcrt fallback, canonical SHA-256 checksums, and quarantine with rotated backups.
- Add `processed_releases` store based on release fingerprints with single-flight locking; orchestrator integrates single-flight and per-run stats persistence.
- Add CI visual improvements across all workflows: reusable helpers, dynamic run-names, collapsible log groups, ANSI truecolor, and rich Job Summaries (no logic changes).

### Changed
- Migrate quality gate from Black to Ruff Format: remove the separate Black job, run lint + format in a single Ruff job, and update READMEs and pre-commit hooks accordingly.
- CacheManager now uses a v2 envelope (schema_version + checksum), per-namespace stats with eviction reasons, LRU budgets with stat-only pre-checks, and lazy `clear_expired`; MD5 removed entirely from `src/` with tolerant migration from existing MD5 hashes.

### Fixed
- Repair documentation build broken on main: add missing mkdocs-minify and mkdocs-htmlproofer plugin dependencies, correct the `validate_external_urls` option name, remove the non-existent mkdocs-sitemap plugin/dependency, and restore corrupted `docs/SOURCE_SCHEMA.md` fences.
- Harden link checker against transient GitHub errors (retry on 429/5xx) and fix the English README anchor.
- Fix ai-docs rebase before push to avoid non-fast-forward races with Documentation Sync.
- Skip `uv lock --check` on release-please branches using a branch-name pattern instead of commit-message matching.

<!-- gerado por IA em 2026-11-18T07:07:10+00:00 — revisar antes de publicar -->

## [0.3.2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.3.1...v0.3.2) (2026-11-18)


### Bug Fixes

* add missing mkdocs-sitemap dep + uv setup for release-please sync ([c49e6da](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c49e6da70191962b9cd6dff23367a3f51bc3c221))
* fix gitleaks config glob patterns to regex ([9b38cf9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9b38cf9e5b5025ea825f3c2107375b91941218d6))
* remove non-existent mkdocs-sitemap plugin and dependency ([f63d4a8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f63d4a85d563e42453a620049743eb27cd8a3b6e))


### Documentation

* **sync:** reconcile documentation — 2026-11-18 17:38 UTC ([3adb207](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3adb207f0b6ea874efaac5ff91cdc604f8f616ad))
* **sync:** reconcile documentation — 2026-11-18 18:07 UTC ([d33f004](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d33f00475539abb28092532d30d1a05ae350b078))

## [0.3.1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.3.0...v0.3.1) (2026-11-18)


### Documentation

* clean up README.md — remove test commit garbage and auto-generated index ([b21e9ac](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b21e9ac1c6b85560cd1dfe8b1be5b63540848f31))
* **sync:** reconcile documentation — 2026-11-18 11:30 UTC ([e20fae4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e20fae47d1df685db26ef4f2bbe432b216d53c12))
* **sync:** reconcile documentation — 2026-11-18 11:43 UTC ([c1cf01d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c1cf01d190878e3fea1472108b720bedce8cd47e))

## [0.3.0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.2.4...v0.3.0) (2026-11-18)


### Features

* **intelligence:** evoluir para Release Intelligence Hub (release=264) — defensivo ([23a3c83](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/23a3c83dc0aad4e081c059080298f4fdd5491f97))


### Bug Fixes

* markdown lint errors in docs/index.md (MD025, MD036, MD051) ([a7f2336](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a7f233616c3fbabd4ce5874c4e7ff503fe190449))


### Documentation

* atualização automática via IA [skip ci] ([#400](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/400)) ([63c23bf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/63c23bfc0b0567cce52ab8f03c2cd5aa1dbcb974))
* **sync:** reconcile documentation — 2026-11-18 05:55 UTC ([8c0e37e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8c0e37ebe952114c303d136267c7991d83046fd6))
* **sync:** reconcile documentation — 2026-11-18 06:34 UTC ([19306f0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/19306f07c0062d4b87bb786fb35c0fe9a7768458))
* **sync:** reconcile documentation — 2026-11-18 06:39 UTC ([5a4da63](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5a4da63ca2ba1f57555a15256e03c7d1f12d15db))
* **sync:** reconcile documentation — 2026-11-18 07:33 UTC ([844d946](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/844d946b38a2a950cf4f8010e3cbb341cbc7b8b7))

## [Unreleased]

### Security
- Protect CI workflows from executing on fork pull requests by adding repository origin checks to ai-pr-review, ai-triage, python-quality, and release_notes_pipeline workflows, preventing privileged jobs from running without access to secrets.

### Added
- Enable auto-merge and automatic uv.lock synchronization in release-please workflow using dedicated PAT token, streamlining the release process.

### Fixed
- Skip 'uv lock --check' on release-please and uv.lock sync commits to prevent false pipeline failures during automated releases.
- Update pytest command in release notes pipeline to include '--extra dev --extra healing' ensuring required test dependencies are installed.
- Fix markdown lint violations (MD025, MD036, MD051) in docs/index.md for consistent documentation formatting.
- Apply pre-commit style fixes: remove trailing whitespace and ensure final newline across workflow files.

### Changed
- Synchronize documentation manifest and drift report hashes to reflect current repository state.

<!-- gerado por IA em 2026-11-18T04:36:38+00:00 — revisar antes de publicar -->

## [0.2.4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.2.3...v0.2.4) (2026-11-18)


### Documentation

* **sync:** reconcile documentation — 2026-11-18 05:23 UTC ([40baab6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/40baab6ff99b64c1f8e2e5cb1b72a23bb5f44b9c))
* **sync:** reconcile documentation — 2026-11-18 05:24 UTC ([244d0f9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/244d0f991cbece9069dd7102202266932df91c20))
* **sync:** reconcile documentation — 2026-11-18 05:29 UTC ([185831f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/185831f93a2f0f335211039bfc2a5c32dcb7dfd7))
* **sync:** reconcile documentation — 2026-11-18 05:35 UTC ([d53d00a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d53d00a079e833ab1c16e59f7295888a4cf81edd))

## [0.2.3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.2.2...v0.2.3) (2026-11-18)


### Bug Fixes

* **ci:** auto-sync uv.lock on release-please bumps; skip lock check on release commits ([772b2e8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/772b2e8e30724fa3949697aa2a71466269e8029d))


### Documentation

* **sync:** reconcile documentation — 2026-11-18 05:05 UTC ([38223cd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/38223cd5a84b176117091af793f433ba38228e82))

## [0.2.2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.2.1...v0.2.2) (2026-11-18)


### Bug Fixes

* **ci:** resync uv.lock after release-please version bump to 0.2.1 ([f91f7b4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f91f7b48f26c1a368650c098416b893a16a76631))
* **ci:** sync uv.lock project version to 0.2.1 ([c895339](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c895339c7888dbbfb2de4c9992a3e2a1aa1c12c8))
* **ci:** sync uv.lock project version to 0.2.1 for uv lock --check gate ([ee148e0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ee148e03a78ca649064165e6a8ebf6663957c69d))
* **ci:** sync uv.lock with pyproject version 0.2.1 ([ac38c13](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ac38c133b2a4840a9dceb948691f5e17e2270803))


### Documentation

* **sync:** reconcile documentation — 2026-11-18 04:57 UTC ([855fcfd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/855fcfd9b4e8a44eadeb6c921753c0115da0e569))
* **sync:** reconcile documentation — 2026-11-18 04:58 UTC ([79ba119](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79ba119f5385dd1380257bbb0bba3d9b9729ffca))
* **sync:** reconcile documentation — 2026-11-18 05:01 UTC ([79df129](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79df129564e0c3359917b4941853d314caf3cdd3))

## [0.2.1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.2.0...v0.2.1) (2026-11-18)


### Documentation

* atualização automática via IA [skip ci] ([#358](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/358)) ([885ccbc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/885ccbccddbcd09e2ed62e5ae9446c012a173e87))
* **sync:** reconcile documentation — 2026-11-18 04:49 UTC ([413ccb1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/413ccb1c349df0a34251ce30392f38a03e04994d))

## [Unreleased]

### Added
- Release Intelligence Hub for release 264: manual deploy assets, org preparation guides, readiness reports, sandbox configuration, and HTML assets page
- Python-based hook system replacing shell hooks: pre-commit (ruff check, ruff format --check, mypy), pre-push (pytest -x), post-tool-use (ruff check --fix + ruff format), session-start (repo state and gate verification)
- Playwright installation in Scheduled Pipeline detect job with 'uv run python' execution

### Changed
- AI Triage workflow refactored from shell to dedicated Python script for robust multiline issue/PR body handling
- Workflow triggers: removed 'push' triggers from scheduled-pipeline, ai-triage, ci-repair, ai-pr-review, opencode; added event_name guards and branches filter 'no-push-trigger'; added dummy push-trigger jobs
- GitHub Actions permissions corrected: 'pull_requests'→'pull-requests', 'repository-projects' permission, 'projects' for GitHub Projects V2, real SHA v1.0.278 for anthropics/claude-code-action
- Intelligence Hub workflow: removed problematic GitHub Pages deploy, added 'git pull --rebase' before push, fixed README filename reference

### Fixed
- CI/CD failures: added missing 'requests' dependency, types-html5lib and types-webencodings for mypy completeness; made detect_release.py network-resilient
- uv.lock synchronization with project versions 0.1.2 through 0.1.7 after release-please bumps; documented manual post-release process in AGENTS.md
- Black formatting applied across 6 files to pass Python Quality gate (ruff/mypy already passing, 2370 tests passed, 95.55% coverage)
- Redundant allow rules removed from .claude/settings.json; 6 files reformatted with ruff

### Documentation
- Automated documentation reconciliation: multiple syncs regenerating documentation-manifest.json, drift_report.json, and docs/index.md
- Baseline updates for new uv.lock and docs blobs

<!-- gerado por IA em 2026-11-17T04:10:09+00:00 — revisar antes de publicar -->

## [0.2.0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.7...v0.2.0) (2026-11-18)


### Features

* **intelligence:** evoluir para Release Intelligence Hub (release=264) — defensivo ([22a498f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/22a498fceb1a2a67060cee8bda62feb377ee4640))


### Bug Fixes

* **ci:** add --extra healing to pytest in Release Notes Pipeline ([3301747](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3301747dfff156f1e33c53eefe2ba7d08997bcae))
* **ci:** add pull --rebase before push in Intelligence Hub workflow ([fc85b80](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fc85b80b6804efeca7db7d46d0e41f024e798b6d))
* **ci:** install Playwright in detect job for Scheduled Pipeline ([a97f6c6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a97f6c60bae11364e25fd0ee6fad19cf0d764509))
* **ci:** remove problematic GitHub Pages deploy from Intelligence Hub workflow ([3f122ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3f122ea35066177490fc284cc8a8737b32cd90cb))
* **ci:** repair failing workflows ([5acf905](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5acf905c68d4197e0faa026233850f7b773c7c7e))
* **ci:** use --extra dev for pytest in Release Notes Pipeline validation ([15fc5bb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/15fc5bb3716be699217dd627a139eb2856bbaa21))
* **ci:** use correct README filename in Intelligence Hub workflow ([976c926](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/976c9268554105b7e86a010039c9ddc62ed2d32d))
* **ci:** use uv run python in detect job for Scheduled Pipeline ([c7d7553](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c7d75535f3bc253b7619c014afab78adb32ee78a))


### Documentation

* **sync:** reconcile documentation — 2026-11-18 04:17 UTC ([33c1ca4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/33c1ca4731df6583ac954704323ed44724f50278))
* **sync:** reconcile documentation — 2026-11-18 04:18 UTC ([27e19db](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/27e19dbdc939a7f7cb4be109b1cbfc9216dc0ede))
* **sync:** reconcile documentation — 2026-11-18 04:21 UTC ([4bbd9fa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4bbd9fa5ffa1e7b86e29911abaeb2f91b64efbac))
* **sync:** reconcile documentation — 2026-11-18 04:23 UTC ([8bacdb6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8bacdb64eddcdb4d99984e2c1919d61e6a3f3066))
* **sync:** reconcile documentation — 2026-11-18 04:27 UTC ([c39353f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c39353f1634ffcd0480493a9d457901f66c6b7f1))
* **sync:** reconcile documentation — 2026-11-18 04:29 UTC ([6c5d340](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6c5d3408312f0562743c95df5bd1f088591e7e7c))
* **sync:** reconcile documentation — 2026-11-18 04:40 UTC ([2101510](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/21015108cd87e78aa1cdac03fe8549c3e66a6bba))

## [0.1.7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.6...v0.1.7) (2026-11-17)


### Bug Fixes

* **ci:** sync uv.lock project version to 0.1.5 after release-please bump ([9a873af](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9a873afd9fd9cee6d4a104d33ac85eaf5c283a32))


### Documentation

* **sync:** reconcile documentation — 2026-11-17 17:44 UTC ([535d78e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/535d78e3362442d5272b27b916f0eca91af0beba))
* **sync:** reconcile documentation — 2026-11-17 17:45 UTC ([79af329](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79af3290464106f8a44abda153b5a0c7eb1baeca))
* **sync:** reconcile documentation — 2026-11-17 17:49 UTC ([881e19a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/881e19a9cdca148e43ad9502217874af9b3140f4))

## [0.1.6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.5...v0.1.6) (2026-11-17)


### Bug Fixes

* **ci:** sync uv.lock with project version 0.1.5 ([d9dcc91](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d9dcc914eb10ff5dea941a9c1bc0c57d3fb06dbb))

## [0.1.5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.4...v0.1.5) (2026-11-17)


### Bug Fixes

* **workflows:** fetch issue/PR body from API in missing info step ([b58ae20](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b58ae2081352b278650d30a2918fc5946f427579))
* **workflows:** remove env vars for body/title, use files from analyze step ([4556657](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4556657ee271a0b97e34cb610ccd699b3abf7bdc))


### Documentation

* **sync:** reconcile documentation — 2026-11-17 11:13 UTC ([c82e9ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c82e9eaab6b7a36f74b559c614cf9a863d133019))
* **sync:** reconcile documentation — 2026-11-17 11:17 UTC ([3d14ff9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3d14ff9cac5fc0986d1754d1a045769973bcf060))

## [0.1.4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.3...v0.1.4) (2026-11-17)


### Bug Fixes

* **workflows:** use file-based approach for issue/PR body to handle newlines ([08b6764](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/08b6764035b26cbd82dbbf88ee9a515ee30b0e5f))

## [0.1.3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.2...v0.1.3) (2026-11-17)


### Bug Fixes

* **workflows:** correct pull_requests to pull-requests permission ([ecdf716](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ecdf716d2b1a693358d5ef11e46dc8535ba672d9))
* **workflows:** use correct 'projects' permission for GitHub Projects V2 ([181e7fd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/181e7fd854bbb3c99f5424b69e765cfc72182de8))
* **workflows:** use env vars for issue/PR body to handle newlines ([84e21ce](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/84e21ce6c8c710111ba90abec118ebecf2e8b476))
* **workflows:** use real SHA for anthropics/claude-code-action ([b7305ec](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b7305ecb9ee0f18e31c99241e2d426cd3309d733))
* **workflows:** use valid 'repository-projects' permission ([258ea1b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/258ea1b12a8eae2abbe97fde888601a1d85c3fc5))


### Documentation

* **sync:** reconcile documentation — 2026-11-17 10:39 UTC ([01bb717](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/01bb7175432f6897965c8a5a1fb830788d82a57a))
* **sync:** reconcile documentation — 2026-11-17 10:45 UTC ([771cfb7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/771cfb7c61bdfa3955643ffd657a7580d7a808d9))
* **sync:** reconcile documentation — 2026-11-17 10:50 UTC ([5675c97](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5675c977a0efcd8aa907b891120640275ecfd18b))
* **sync:** reconcile documentation — 2026-11-17 10:52 UTC ([2964ecc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2964ecc79851d1c8a31e66fea52d1509cb32beca))
* **sync:** reconcile documentation — 2026-11-17 10:55 UTC ([7130629](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/71306297ccba9f7ff1ef11117de596206fc176bc))

## [0.1.2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.1...v0.1.2) (2026-11-17)


### Bug Fixes

* add event_name guard to scheduled-pipeline jobs to skip ghost push runs ([344cb42](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/344cb42d3918466fba77e9f1ea6b6e61a37593fd))
* **ci:** prevent empty workflow runs on push ([9b24ab2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9b24ab258df6d71351e384d45caddc60a654cb70))
* **ci:** prevent empty workflow runs on push ([#325](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/325)) ([6ebb098](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6ebb09861e525594857f81eb68a27122f89c7239))
* **ci:** remove Black Format job from Python Quality workflow ([9b033f9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9b033f981f845274f71e9ae2c98ca67ca124d752))
* **ci:** resolve all GitHub Actions failures ([e629386](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e629386f5d61f5d37c06f37b8d1a1531cba6dcdb))
* **ci:** resolve all GitHub Actions failures ([#317](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/317)) ([79acfea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79acfea7288a39592af8b9490d6c127de3651263))
* **ci:** sync uv.lock project version with pyproject 0.1.1 ([65385c6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/65385c64d1b5336cda78c27450770bd4c7b8ada3))
* **ci:** use branches filter to prevent empty workflow runs ([4b80866](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4b80866d1750b811b8b2db4d67d3417fdef12cfa))
* **hooks:** merge PR [#326](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/326) - resolve redundant allow rules and broken hook commands ([ba35131](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ba3513126756a1105dcdc3b6fe0f6e20fe70c566))
* **hooks:** resolve redundant allow rules and broken hook commands ([44a1fe9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/44a1fe9bc44191778173e4049e5d43b27b692ca5))
* **quality:** apply black formatting to pass Python Quality gate ([37dc2a1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/37dc2a19fff5db393c4262260e047336bf0fc976))
* **quality:** merge PR [#321](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/321) - Black formatting fixes ([6fd73c6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6fd73c642cc4b59f42cf30aa1731cec0fa03b412))
* remove workflow_dispatch from scheduled-pipeline to test push trigger ([d44c366](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d44c3665fd51911af23a0aad484da5733c9bb56b))
* restore scheduled-pipeline with only schedule trigger ([c5fa520](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c5fa520e4af8ccc4b053321e01c153a3ec7256a0))
* restore scheduled-pipeline with workflow_dispatch ([825b23e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/825b23e5620cb968c973bbe628a574eb3a9e296d))
* **ruff:** move imports to top of file in test_infrastructure_llm_coverage.py ([9c51877](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c51877ab576045be78eb946fdfcdff500a970e5))
* **workflows:** add push-trigger dummy job to prevent empty runs on push ([82cd56b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/82cd56b97a1fd569cf21e390624766b2872d90be))
* **workflows:** remove push triggers to prevent bot loops (re-apply after merge conflict loss) ([9a7d5e9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9a7d5e9873122a264108b6c7bfd1b096afff87b5))
* **workflows:** remove push triggers to prevent bot loops and fix CI failures ([#328](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/328)) ([e91d64d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e91d64db8e6cf9185420da96b26d36913d4dc37b))


### Reverts

* restore Black Format job in Python Quality workflow ([6f976ba](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6f976ba16d1109ffc186127fcdf8ddeaacd58d95))


### Documentation

* atualização automática via IA [skip ci] ([478249f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/478249f9e0e88c455fd50088926b3b4fb34caadc))
* **sync:** reconcile documentation — 2026-11-17 01:46 UTC ([3f88818](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3f8881890acc3cc5cd0556cd7cf3acf2eb172c5f))
* **sync:** reconcile documentation — 2026-11-17 01:53 UTC ([db5ad42](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/db5ad42c03691bb3ca35fba018229542b3223779))
* **sync:** reconcile documentation — 2026-11-17 01:58 UTC ([1350213](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1350213199272e865728ac68a0b76c03b4d60985))
* **sync:** reconcile documentation — 2026-11-17 02:42 UTC ([9425564](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/94255647d6f713f07b2e7f7c559cd566797735e8))
* **sync:** reconcile documentation — 2026-11-17 02:58 UTC ([e81a4b0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e81a4b0dc32843b98f3caf8e199969d68c085acd))
* **sync:** reconcile documentation — 2026-11-17 03:01 UTC ([b79388d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b79388d57ca60ab9e371f9e4727fb6f5e0a9793c))
* **sync:** reconcile documentation — 2026-11-17 03:10 UTC ([b565617](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b565617efcf37cb2cc659757ed68b4ea35320303))
* **sync:** reconcile documentation — 2026-11-17 04:19 UTC ([99af09e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/99af09e4d86e5234406fa55b56c2816aa42ff7d1))
* **sync:** reconcile documentation — 2026-11-17 04:25 UTC ([dc95e9a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dc95e9a0fb8debfc75c3ad765339afb76bbd399d))
* **sync:** reconcile documentation — 2026-11-17 04:27 UTC ([e4669a5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e4669a5f945f38ae1416a30cbd49c5b0822732f2))
* **sync:** reconcile documentation — 2026-11-17 04:40 UTC ([f7c405e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f7c405ed85a6dd248a9a4c4ac90e1b64175c41d2))
* **sync:** reconcile documentation — 2026-11-17 06:26 UTC ([f657850](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f6578509a0675b1abc261572a87ac93fda6ed6e2))
* **sync:** reconcile documentation — 2026-11-17 07:52 UTC ([4989155](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/498915553a92ca3dee1c67fe0a97b1b89c926921))
* **sync:** reconcile documentation — 2026-11-17 07:58 UTC ([33db581](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/33db58190fccc0aa3de933a8b14c11a3273e8cdf))
* **sync:** reconcile documentation — 2026-11-17 08:04 UTC ([3c1c1f1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3c1c1f1c0b949a40c1b48097be42c546180634d1))
* **sync:** reconcile documentation — 2026-11-17 08:07 UTC ([5812066](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5812066fdf92853c90afa02c7fd7604af5364842))
* **sync:** reconcile documentation — 2026-11-17 09:49 UTC ([8747185](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8747185a0923265ead64f4df7fc5e2b6cd4ebb10))
* **sync:** reconcile documentation — 2026-11-17 09:56 UTC ([c06e3a4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c06e3a4346d8dbf46be762789109ed8a3cd33d2b))
* **sync:** reconcile documentation — 2026-11-17 10:05 UTC ([0ce534e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0ce534ea63538fa46f350c6a75ebddb180cd9a4f))
* **sync:** reconcile documentation — 2026-11-17 10:07 UTC ([2e6a370](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2e6a37052e6a4998323d580e14e4f69d2c5e3035))
* **sync:** reconcile documentation — 2026-11-17 10:08 UTC ([e0bcf04](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e0bcf04d60fc4427a0036f9f0a248e190e685c93))
* **sync:** reconcile documentation — 2026-11-17 10:09 UTC ([984d364](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/984d3640e23797a3dd028d3adf1b3e01f0faa64a))
* **sync:** reconcile documentation — 2026-11-17 10:12 UTC ([46cbb55](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/46cbb55fcbf716732ffa7114068a0dfa9fe609c7))
* **sync:** reconcile documentation — 2026-11-17 10:13 UTC ([3816ea7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3816ea74441bdbebfbb824465e218d23259bcda3))
* **sync:** reconcile documentation — 2026-11-17 10:15 UTC ([4549098](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/454909802b30a786f8e7972cf87c7c706abcdfc3))
* **sync:** reconcile documentation — 2026-11-17 10:17 UTC ([8238d29](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8238d2966e86a2f72c1059cab8747704de49b7e8))
* **sync:** reconcile documentation — 2026-11-17 10:21 UTC ([f365d0a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f365d0a3c04b9193450a42fcbcbc85068337837e))
* **sync:** reconcile documentation — 2026-11-17 10:33 UTC ([c51553f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c51553faeba4043cf0e0ee9f8a28514cc5029500))

## [0.1.2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.1...v0.1.2) (2026-11-17)


### Bug Fixes

* **ci:** prevent empty workflow runs on push ([9b24ab2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9b24ab258df6d71351e384d45caddc60a654cb70))
* **ci:** prevent empty workflow runs on push ([#325](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/325)) ([6ebb098](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6ebb09861e525594857f81eb68a27122f89c7239))
* **ci:** remove Black Format job from Python Quality workflow ([9b033f9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9b033f981f845274f71e9ae2c98ca67ca124d752))
* **ci:** resolve all GitHub Actions failures ([e629386](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e629386f5d61f5d37c06f37b8d1a1531cba6dcdb))
* **ci:** resolve all GitHub Actions failures ([#317](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/317)) ([79acfea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79acfea7288a39592af8b9490d6c127de3651263))
* **ci:** use branches filter to prevent empty workflow runs ([4b80866](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4b80866d1750b811b8b2db4d67d3417fdef12cfa))
* **ruff:** move imports to top of file in test_infrastructure_llm_coverage.py ([9c51877](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c51877ab576045be78eb946fdfcdff500a970e5))
* **workflows:** add push-trigger dummy job to prevent empty runs on push ([82cd56b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/82cd56b97a1fd569cf21e390624766b2872d90be))
* **workflows:** remove push triggers to prevent bot loops and fix CI failures ([#328](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/328)) ([e91d64d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e91d64db8e6cf9185420da96b26d36913d4dc37b))


### Reverts

* restore Black Format job in Python Quality workflow ([6f976ba](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6f976ba16d1109ffc186127fcdf8ddeaacd58d95))


### Documentation

* atualização automática via IA [skip ci] ([478249f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/478249f9e0e88c455fd50088926b3b4fb34caadc))
* **sync:** reconcile documentation — 2026-11-17 01:53 UTC ([db5ad42](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/db5ad42c03691bb3ca35fba018229542b3223779))
* **sync:** reconcile documentation — 2026-11-17 02:42 UTC ([9425564](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/94255647d6f713f07b2e7f7c559cd566797735e8))
* **sync:** reconcile documentation — 2026-11-17 04:19 UTC ([99af09e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/99af09e4d86e5234406fa55b56c2816aa42ff7d1))
* **sync:** reconcile documentation — 2026-11-17 04:25 UTC ([dc95e9a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dc95e9a0fb8debfc75c3ad765339afb76bbd399d))
* **sync:** reconcile documentation — 2026-11-17 04:27 UTC ([e4669a5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e4669a5f945f38ae1416a30cbd49c5b0822732f2))
* **sync:** reconcile documentation — 2026-11-17 04:40 UTC ([f7c405e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f7c405ed85a6dd248a9a4c4ac90e1b64175c41d2))
* **sync:** reconcile documentation — 2026-11-17 07:52 UTC ([4989155](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/498915553a92ca3dee1c67fe0a97b1b89c926921))

## [Unreleased]

### Changed
- Migrated the MCP knowledge server to the FastMCP API and pinned the `mcp` package to 1.30.0, regenerating characterization test golden files; integrations relying on the previous MCP server API may require updates.
- Reconciled generated documentation and refreshed `docs/.documentation-manifest.json` hashes, the drift report and the documentation sync scripts.
- Updated quality gate configuration for Black and Ruff and added `.ruffignore` to exclude non-Python files from linting.
- Applied Black formatting and resolved Ruff findings (module-level import placement, unused imports and related rules) across source and test files.
- Marked the 0.1.1 release and synchronized `uv.lock` with the declared project version.

### Fixed
- Fixed GitHub Actions failures across the documentation sync, documentation build and Python quality workflows, including staging of all modified files during documentation sync.
- Installed the package in editable mode and added `src/domain/__init__.py` so mkdocstrings can resolve `src.domain.llm` during documentation builds.

<!-- gerado por IA em 2026-11-16T16:44:36+00:00 — revisar antes de publicar -->

## [0.1.1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/compare/v0.1.0...v0.1.1) (2026-11-16)


### Bug Fixes

* correct badge label color default and add missing emoji keys ([e4917f9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e4917f9f51ab8160fcee51a2fdfa18bdd06d04eb))
* **docs:** install package in editable mode for mkdocstrings ([2a676b7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2a676b7b64a79222b9600ebed1f2b29241daa16c))
* migrate MCP server to FastMCP API; fix characterization test golden files ([3e78019](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3e7801998ed1a09adc4b15bb4c2eb23e8fde17e4))
* **quality:** restore characterization goldens and scope docs engine off tests/ ([e07dd12](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e07dd12c3765176e47caeb34077816cda17ee75a))
* **quality:** sync uv.lock, restore README block format, align MCP tests with FastMCP ([74f86d8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/74f86d84c17faad9c8f10d455ae346af78e68b6d))
* resolve all quality gate failures and MCP 1.30.0 compatibility ([900b8a6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/900b8a69fd5feadec05b522a0f77ec64519abfe3))
* resolve Python Quality gate failures ([bf45058](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/bf450585d6865be9cbbe47da353a06ded1fdd764))
* **tests:** regenerate corrupted summarizer golden files ([aefc8cd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/aefc8cdb93735915f8cabe22ce6c1084a8fbd83a))
* update MCP server to FastMCP API v2 ([e0c3f3e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e0c3f3e13ae196c75c7dbfa024b351f38672f2f9))


### Documentation

* atualização automática via IA [skip ci] ([1775e78](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1775e782da7aa07440813afcfe6c742fb3708f0d))
* atualização automática via IA [skip ci] ([ddc3be8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ddc3be810262d58198bd138372ac591d15f27926))
* atualização automática via IA [skip ci] ([94b0cc9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/94b0cc9a7a013e789c662dea214e87d17723f4c4))
* atualização automática via IA [skip ci] ([b81797c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b81797cc1d9da7afc27df53b8356482fe9b6fdee))
* atualização automática via IA [skip ci] ([8ccfecb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8ccfecb58917c8062a39c3b401fa6ceeb14531b7))
* final reconcile navigation and inventory ([dad5a49](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dad5a49d3866257fc97788c8bc0d794cef0e4e27))
* fix broken links in test golden files and update manifest ([e359b1d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e359b1d0dae4956f5c1c1d4d9292c43a2f995c79))
* fix broken links in test golden files with correct relative paths and update manifest ([70084fb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/70084fb7af3b8489076ac4522f92bf93be8cb2da))
* resolve manifest merge conflict ([47b91e5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/47b91e55fbb92dbc788ed41774f094be6e18c7cd))
* resolve merge conflicts in manifest ([544edf1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/544edf1a93b4d16536ffab3a3c9512800dcfee64))
* sync with remote reconcile ([9cd8d75](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9cd8d75b6a897a27077d5e134ea96ec09d653209))
* **sync:** final reconcile and manifest update ([7878008](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/78780086fde6e0fb964486a7c19560c2b367e487))
* **sync:** reconcile documentation — 2026-11-16 14:38 UTC ([0475ad5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0475ad519efa25fde347f530ef5216de45807436))
* **sync:** reconcile documentation — 2026-11-16 14:43 UTC ([80e4181](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/80e4181bcc32b31230f9d5f7a9d201f7f9e2cf71))
* **sync:** reconcile documentation — 2026-11-16 14:51 UTC ([54187db](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/54187db07708192d339f38d40d7e7dbede7995a4))
* **sync:** reconcile documentation — 2026-11-16 15:39 UTC ([a1c4fb8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a1c4fb815f247d80a61196ddfb97758c49b6bcbf))
* **sync:** reconcile documentation — 2026-11-16 16:41 UTC ([71594a6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/71594a654e5077e35c466dd07fb5815a73a54a60))
* **sync:** reconcile documentation — 2026-11-16 17:51 UTC ([e8114ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e8114ea3e49916ac70a9701f3c5e45da2876b7af))
* **sync:** reconcile documentation — 2026-11-16 18:53 UTC ([3f56320](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3f56320c8c6a2b58fe440b2eb8cdd665563b23b6))
* **sync:** reconcile documentation and fix test links ([1fe0fca](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1fe0fcabfe97f9c5001b255d1e796e83a2a4ac6c))

## [Unreleased]

### Changed
- Sincronização do manifesto de documentação com novas referências, hashes e metadados de geração.
- Correção na inicialização de linhas do bloco de release docs, ajustando formatação esperada.
- Adaptação de testes do servidor MCP de release notes para API atual.

### Fixed
- Ajuste de inicialização de linhas no bloco de release docs para restaurar formatação esperada.

<!-- gerado por IA em 2026-11-16T16:27:57+00:00 — revisar antes de publicar -->

## [Unreleased]

### Breaking Changes
- Migrated the MCP server from FastMCP to the MCP Server API v2, replacing decorators with request handlers (`Server`, `CallToolRequest`, `ListToolsRequest`, `CallToolResult`). Consumers relying on the previous FastMCP API may require updates.

### Changed
- Refactored MCP server tests to use a `_decode` helper for extracting JSON payloads, removing direct `call_tool` integration tests in favor of low-level tests for internal methods (`_search_release_notes`, `_get_release_summary`, `_list_releases`, `_compare_releases`).

### Fixed
- Fixed link generation in `release_docs.py` by correcting the order of operations, ensuring English category slugs are applied before building the link, preventing broken links to nonexistent Portuguese slugs.

<!-- gerado por IA em 2026-11-16T16:13:25+00:00 — revisar antes de publicar -->

## [Unreleased]

### Fixed
- Fixed release link generation for English documentation by using English category slugs for the en_US locale and building the link before the display block, preventing links to nonexistent Portuguese slugs.

### Changed
- Updated MCP knowledge server tests to use the low-level SDK Server, registering handlers for ListToolsRequest and CallToolRequest and calling internal methods such as _build_tools, _search_release_notes, _get_release_summary, _list_releases, and _compare_releases; assertions were updated for result format and dictionary-based queries.

<!-- gerado por IA em 2026-11-16T16:10:03+00:00 — revisar antes de publicar -->

## [Unreleased]

### Breaking Changes
- Reverted project version from 3.1.0 to 0.1.0 in pyproject.toml, a breaking change that may affect consumers relying on semantic versioning.
- Migrated MCP knowledge server to FastMCP v2 API, replacing Server.on_list_tools/on_call_tool with @tool decorators; consumers using the old API may need updates.

### Changed
- Updated MCP server tests to the asynchronous FastMCP API and removed unused imports.
- Restricted documentation engine rewriting to `docs/` and `DOC_ROOT_FILES` to avoid modifying test fixtures.
- Updated `docs/.documentation-manifest.json` hashes and references, adding CHANGELOG.md and docs/ai-generated/ entries.

### Fixed
- Fixed invisible badge label text by setting default label color to white, added impact emojis, and replaced hardcoded colors with constants.
- Restored golden characterization test files that were manually edited and breaking tests.
- Fixed broken relative links in golden test files.
- Fixed Python Quality gate failures: synchronized uv.lock, applied Black formatting, and resolved mypy errors in the migrated `knowledge_server.py`.
- Restored proper formatting of README blocks in `release_docs.py` and regenerated corrupted golden files for summarizer tests.
- Documented automatic documentation update via IA commit without functional changes.

<!-- gerado por IA em 2026-11-16T15:42:52+00:00 — revisar antes de publicar -->

## [Unreleased]

### Breaking Changes

- Migrated the MCP knowledge server to the FastMCP v2 API, replacing the previous `Server.on_list_tools`/`on_call_tool` interface with `@tool` decorators; consumers relying on the old API may require updates.
- Bumped the `mcp` dependency to `>=2.0.0,<3`.
- Project version in `pyproject.toml` was reverted from 3.1.0 to 0.1.0; flagged for human review to confirm intent.

### Changed

- Updated MCP server tests to the asynchronous API and removed unused imports.
- Restricted documentation engine rewriting (`strip_dead_refs` and broken-link audit) to `docs/` and `DOC_ROOT_FILES` so test fixtures are no longer modified.
- Updated `docs/.documentation-manifest.json` hashes and references, adding CHANGELOG.md and docs/ai-generated/ entries.

### Fixed

- Fixed invisible badge label text by setting the default label color to white, added impact emojis (high/medium/low), and replaced hardcoded colors with constants, including `labelColor` and `logo` parameters in `to_markdown()`.
- Restored golden characterization test files that had been manually edited and were breaking tests.
- Fixed broken relative links in golden test files.
- Fixed Python Quality gate failures: `uv.lock` sync, Black formatting, and mypy errors in the migrated `knowledge_server.py`.

<!-- gerado por IA em 2026-11-16T14:22:48+00:00 — revisar antes de publicar -->

## 0.1.0 (2026-11-16)


### Features

* **agents:** add custom agent profile for Copilot cloud agent ([048892c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/048892c4afc5526ba506b6c500034e706882b4ef))
* **ai-docs:** add OpenRouter free documentation pipeline ([c88626d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c88626dfd93b551ef316bda8d4dff3324af0ea84))
* **ai-docs:** complete change context and rate-limit handling ([825cd48](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/825cd482c46fe84529c0d8025ed488642baf0e6b))
* **ai-docs:** pipeline dinâmico de documentação por IA via GitHub Actions ([b8dcf77](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b8dcf77621c2adaaba12f769b2fd0c87eeb2147d))
* **ai-docs:** pipeline dinâmico de documentação por IA via GitHub Actions ([e44dedb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e44dedb89e617e3ad1a9a9d6b7db28ad1fc2cf3f))
* **architect:** executa 6 passos auditoria 360 - defensivo, SoC, CI, docs ([cc8d6e2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cc8d6e2d1810e7fe7f7ac02ae512dd70704d7c7b))
* **automation:** changelog automático para atualizações de grande impacto ([4f88fd6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4f88fd6c70a8dfa15683cab0ffcb60debfc1840a))
* **automation:** incluir comentario /oc fix no Python Quality (plano executado) ([e4febcd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e4febcd1f1d4f425ea8d560037fbdfa28ced18d7))
* **ci:** add Copilot cloud agent setup workflow and instructions ([38e0e64](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/38e0e64329b4415f06f87622e856d6ff48692711))
* **ci:** add live animated progress to auto-healing steps ([1b3e2f3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1b3e2f3fefbd5ce1fb1b4792131ffd5ba8846ed2))
* **ci:** add OpenRouter free models as second LLM provider tier ([d2c8ad0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d2c8ad0d23afffa5375da66bcbb64f1a00bab304))
* **ci:** diagnostic issue with action plan on release pipeline failure ([8d28e14](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8d28e14ccb6ccc1d4119f7fc768031e2cbf0c4aa))
* **ci:** documentation sync obrigatório (reconcile) para qualquer alteração ([c9f69a0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c9f69a074840c76941fe7fc892f48510027ad170))
* **ci:** documentation sync obrigatório (reconcile) para qualquer alteração no repositório ([c9f69a0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c9f69a074840c76941fe7fc892f48510027ad170))
* **ci:** make auto-heal incremental — one test class per run, persisted progress ([431d525](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/431d52577748379240b72b0dc18ab6db0a5a12ce))
* **ci:** reorder LLM fallback to try Ox Alpha Free before Hy3 Free and Gemini ([0fa3166](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0fa31663687841b00ab955032cc2bbb2648800a3))
* commit cobertura + changelog ([5a92fed](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5a92fed5da91a74dd78b7ab24a0d9c833d27dcf0))
* complete Fase 5 - mutation testing, devcontainer, README/ADRs, final verification ([#240](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/240)) ([ad0376c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ad0376c0f9aa37bb3f32ed90c8633e8afc1e8ebe))
* **design-system:** extract and apply design system to dashboard ([eab530d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/eab530d2da7d19d46fc5c6716ff7ed6c60e9b168))
* **docs-sync:** auto-fix markdown lint errors before validation ([87ac7af](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/87ac7af004bb04a58aa11ba9dc6a4176bf446ca7))
* **docs-sync:** pin black &lt;26 for mkdocstrings-python, auto-fix markdown lint, remove stale artifacts ([51528de](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/51528dea66121006d6e43c6b96dab7d5b3addab8))
* **docs:** add dual-banner with random selection on MkDocs ([9a718bc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9a718bcbdde776a6f5a54dec65fd194e954df5e1))
* **docs:** continuous documentation reconciliation pipeline (ADR-005) ([55c5f6a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/55c5f6a9db2776855d13b692a5c4a4c6fa28a81d))
* **docs:** remove auto-healing and fix documentation issues ([7905a2b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7905a2b3e8af65a3863dd09bb741e21a4c331b1b))
* **gaps:** implement 4 of 5 gaps from newPrompt.md ([f184259](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f1842598723f17fbbd053b0da7f62d732be77381))
* **impact-propagation:** RIPE — Impact Propagation & Dependency Graph Engine ([5031d00](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5031d00373294ab2b4898eaa0b392b09f9ef37f8))
* **intelligence:** Salesforce Release Intelligence Hub — defensivo ([#172](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/172)) ([581ceef](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/581ceefbdc1ed0953a34ff80fbcee339af1f7f6d))
* **intelligence:** Salesforce Release Intelligence Hub defensivo — ruff pass, cobertura exec direta (release=264), SoC, nomes completos ([581ceef](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/581ceefbdc1ed0953a34ff80fbcee339af1f7f6d))
* **ledger:** Salesforce Feature Evolution Ledger — rastreamento cross-release de features individuais ([1e4b78e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1e4b78ec49511998d238c62c16d5a0cb2815d592))
* **llm_service:** add Groq provider + nested model loop + expand OpenRouter ([bae40dc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/bae40dcb81074f434528effdd617395c987ac814))
* **llm:** replace groq with gemini-3.6-flash as third provider ([5db2b81](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5db2b814a5f2a5f71d00ad236dca35b6c1873970))
* **newPrompt:** incluir especificação de referência, adicionar snapshot scraper e atualizar plano ([6abbac0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6abbac06a7ad479346799a1f1f2f8ae977f0a073))
* **opencode:** incluir mypy no /oc fix do Python Quality ([#175](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/175)) ([72b1fc4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/72b1fc4dc3ce89def7f240b31769d661e6b532f5))
* **phase1:** add comprehensive test coverage for 95% target ([24c46ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/24c46eabb6aa6b5f683d1aa4bb26285ee2ebcd0a))
* **phase1:** comprehensive test coverage for 95% target ([#229](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/229)) ([24c46ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/24c46eabb6aa6b5f683d1aa4bb26285ee2ebcd0a))
* **readme:** swap banners, limit to 3 latest, add releases archive ([cfac68c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cfac68c8d70180623e4917603e1b7a2e489af147))
* **refactor:** extract ReleaseDiscoveryService and DocumentationService ([8f8684f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8f8684f08a6e3966b5245af7400de55c201f7719))
* **search:** add Salesforce synonyms (clouds, platform, api, apex, security) ([2522bee](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2522beee73fed17a0760e43fd2a97a30617c8422))
* **sync:** add obsolete_content audit + reconcile to docs_sync_engine ([07f6206](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/07f62069fa129003619cb8120e408d8bbac977da))
* update OpenCode provider to hy3-free with x-preview-f-free in fallback pool ([33a02b9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/33a02b92f236d4999d894f0bd65d4cb1cc03f0b9))
* **workflows:** remove Agent Validation workflow and all related content ([4a8288d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4a8288d41431511dcff0a28688a698850474f5e2))
* **workflows:** remove redundant Auto-Format with Black and Ruff ([47c7237](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/47c72377e7f5d36c395ed022eb83fb92ee26fde2))


### Bug Fixes

* achieve ≥95% test coverage and close Issue [#103](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/103) ([b0ea787](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b0ea7870ccb888d222a8d06738a663f77eec70ac))
* add repository context to LLM prompt for auto-healing file identification ([95a8977](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/95a8977ea59cc3ede188017cd7bd9a2cfe068880))
* **agent-validation:** fix YAML indentation in comment block ([22c96ae](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/22c96ae083941d00c0e05adc888d35d10ecc4c59))
* **agent-validation:** handle push triggers and empty head_ref ([0626af5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0626af534c9f84e9eee4b4a83eb69221529036f7))
* **agent-validation:** skip cleanly when no PR context (push trigger) ([7dbc4b6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7dbc4b66ddd501ad8127f60e78699cae7f893f5b))
* **ai-docs:** black format + ruff 0.17.1 apt documentado ([c07e25b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c07e25b1dcb7fcb9d2ab9df1f58dfa3149aec171))
* **ai-docs:** corrige change_reviewer (import + logger), change_classifier (retorno), e prompts path ([9c9848b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c9848b08252c67d18dfbe899066b059db0ee97d))
* **ai-docs:** corrige SHAs dos actions no workflow (checkout/setup-python/upload-artifact) ([9e52167](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9e52167a51a1b06eff09df98645b038f13a7432a))
* **ai-docs:** corrige tests async + black + SHAs; 40 testes passam; mypy OK ([b13270e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b13270ed73f21670f618305df85a93832de0eb58))
* **ai-docs:** cria .github/ai-docs-ignore para evitar erro 'pathspec' no workflow ([c9e2cd2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c9e2cd25a484c8191850af2d79d4efab42976f9e))
* **ai-docs:** docs/.ai-logs/ criado + upload-artifact if-no-files-found=ignore ([b64eca7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b64eca738a8d62ba7a026ad2b6394b7976567710))
* **ai-docs:** include current docs in generation context ([744a271](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/744a2712d50d894eadd33a96bf91ac9e6650d5b8))
* **ai-docs:** ruff I001/ASYNC230 corrigido; black formatado; 4 testes + 40 total OK ([ad8c69b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ad8c69ba6160206ed2f40e05edcb32bd3eb6ffa1))
* **ai-docs:** use OpenRouter free router alias ([77b964d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/77b964d0445da4c03489105e90e9e83df32f15a8))
* **api:** corrigir stub HTTPException para evitar mypy failure (dict[str,str]) ([7fcc49c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7fcc49ca24dce5c7952d0482e30e653cc375f151))
* **api:** make fastapi import optional for pipeline lint job ([1d05281](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1d05281d8cbe9fc6351e9a603c738b48d3e5841f))
* black formatting + coverage for LLM provider chain ([01e32b9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/01e32b93b91fe187479c9a93dfce2512c83635a3))
* Black formatting + Documentation Sync workflow fixes ([2412e9b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2412e9b8c7d84ce0a2c0bda5ddf071e3504ee29e))
* black formatting in release_docs.py ([96442e5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/96442e59e757b41459f0f34db82a551d5c5e1d57))
* **ci:** adicionar actions:read e melhorar error handling no auto-healing ([2d62043](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2d62043431d1ef0a1a855b6027f971d477380347))
* **ci:** bound auto-healing runtime and make it converge on all gates ([55a4433](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/55a443347d1cfa6de2f300bbd97233a9bf0935ae))
* **ci:** check PR author instead of event actor in dependabot-lock-refresh ([555be7d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/555be7d3f99fe8c32d002d1e2afabc38b7c1935d))
* **ci:** correct OpenCode base URL (405 Method Not Allowed) ([49352e7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/49352e7995ce2fcbbb41a11aa1074ea2a1897323))
* **ci:** deterministically extract failing files from log in auto-heal ([ad3e9c8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ad3e9c8ec1b0195c8e61bb4863007292778dc709))
* **ci:** documentation-sync pipeline uses workspace paths not /tmp ([4b8ffff](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4b8ffff32ab97e6e9782c4bc111c1ea90a1463e2))
* **ci:** escape newlines in auto-healing prompt so workflow parses and targets correct file ([e388a94](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e388a94b13f70a3867caa81ed3a581696737c9f4))
* **ci:** fall back to OpenCode hy3-free when Gemini LLM fails ([08cdeaf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/08cdeaff4a7196e55ed242709375716e66845a94))
* **ci:** fix all Python Quality error files in one auto-heal PR ([97ea0a2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/97ea0a2f2afc790aa47c7a78774ffb65c231f594))
* **ci:** fix import detection for multi-line imports and add missing stubs ([7cc62ac](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7cc62ac4feb9d130ade77e560f35114c474c5623))
* **ci:** install syrupy in release notes pipeline ([b954060](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b95406068798d88ae455bed10d63f207790f462c))
* **ci:** install syrupy in tests job for snapshot fixture ([677a703](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/677a703dfa833fbadb84920266d16243ac50e12f))
* **ci:** llm_fallback now detects pytest import errors and missing stubs ([286387f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/286387fdac8be6e8bca1ea0fedcb2db8ba11f2aa))
* **ci:** make auto-heal extract all failing files and retry on bad fixes ([f4f7ee4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f4f7ee44c8f48c36f7e55da6951fea3a65211053))
* **ci:** make create-issue reliable on any gate failure ([aad4f63](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/aad4f6372cf00ed2d818ab8c51020a2ada900d28))
* **ci:** pin all third-party actions to immutable commit SHAs ([5230774](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/523077416b16a39b036da402589e29bd75e54c79))
* **ci:** point OpenCode fallback at real Zen endpoint (hy3-free) ([5968798](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/596879863ede84328c1049360c60a1a7f26fd6e7))
* **ci:** quote version constraint to avoid shell redirect error ([9c60d8b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c60d8bd874ebfe6ce886b9d687c40a5a647fb14))
* **ci:** refactor auto-healing for incremental repair and post-fix verification ([42b1a45](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/42b1a4573221b6db12466cf01b7ccc1a4d968ff5))
* **ci:** remove unsupported optional chaining in concurrency group ([8b29bd3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8b29bd3d1ee67a116e434b14a3820804a757e883))
* **ci:** resolve ruff E741, black, and mkdocs strict-mode griffe warnings ([1ebf777](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1ebf777a5f093d79c0364de8a6f366330eeac681)), closes [#137](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/137)
* **ci:** resolve ruff, black, mypy, tests, and mkdocs build issues ([#233](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/233)) ([1a0d04f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1a0d04fa0166186470ae0fb736f61eb20598e636))
* **ci:** rewrite auto-healing with deterministic repair + LLM fallback ([3bd6fac](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3bd6fac8f66af9a20c85b63408d63c7acd14f206))
* **ci:** roll back LLM regressions and stop duplicate stub generation ([32c6058](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/32c6058b61af742c69d3b5e0739411309f10e1f6))
* **ci:** stop auto-heal from burning its whole budget on dead LLM providers ([802483a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/802483a7120628206d6373d3374295915cab8829))
* **ci:** stop auto-heal repair step from timing out after 35 minutes ([acc0922](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/acc0922ca0bf909547f1b0ff17e05690d600584f))
* **ci:** substituir gh api por curl para download de logs ([784dc3b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/784dc3bc79be8943d6fd45595bf2fbf665a5fb1b))
* **ci:** surface OpenCode HTTP error body in auto-heal LLM fallback ([90df51e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/90df51e200cb472e772be6aa5144af9f0dc90e63))
* **ci:** sweep free OpenCode model pool when primary models stall ([acc79b0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/acc79b085f5086eea8acd4dd569bfc0c6d83a871))
* **ci:** target source module instead of test file in auto-healing ([e8c81c7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e8c81c7ae76d3018bec68f37e84fa2b608ac900f))
* **ci:** update Gemini model from gemini-2.5-flash to gemini-3.6-flash ([c77c59c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c77c59ca369335405ff48372fb5b4fc80aaa0c99))
* **config:** add Winter '27 to KNOWN_RELEASES + handle immutable GitHub Releases ([55854a8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/55854a8fb6f32e65110e4f6d128c11dcfa4cce88))
* detect existing releases by .meta.json instead of .md files ([0d3951a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0d3951a64e70dd1c5d9e8c824f3c5df1900234d3))
* **docs-sync:** content-based manifest idempotency (ignore repository_sha churn) ([c44a7a9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c44a7a940cec9447472306b8b1f7a7eeeda7e7c7))
* **docs-sync:** corrigir SHA inválido do actions/cache@v4.2.0 ([8f27aa7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8f27aa7403f55d11fff39d06b17a24b787cfa3f2))
* **docs-sync:** exclude manifest self-reference from inventory (idempotent self-baseline) ([9664676](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9664676b08f48f5d548d48fb4522e002f5e6487b))
* **docs-sync:** idempotent manifest baseline; restore dict contract for write_manifest ([c955ef8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c955ef8fbe0a115bf3ebe7a6a7096936c8abb0a3))
* **docs-sync:** make audit read-only and report outcomes ([#187](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/187)) ([ef55ed6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ef55ed6e69baa12f589e26bbadb9e72399a6077c))
* **docs-sync:** remover hashFiles do bloco env para corrigir parser do GitHub Actions ([242aec7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/242aec7b05aab9f72085aaa1027b57d09a128a39))
* **docs-sync:** resolve ruff/black lint errors in sync engine ([7749f12](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7749f12e672e92a5d9414e91243c2c20640e3642))
* **docs-sync:** usar npx para markdown-link-check e markdownlint-cli2 ([2cfa69e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2cfa69e189b0c9b69852388b5db9a50ad637ffa7))
* **docs-sync:** use --autostash on git pull --rebase to avoid staged-changes error ([ada0d09](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ada0d0908e0a2233677f4e0d18595d9eacbe6736))
* **docs:** banner assets path and missing banner2.png ([e24e91b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e24e91b0a9fb24a093e99dd3fddef8fd742b524a))
* **docs:** banner load before listener, handle cached images ([18afe4a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/18afe4a956ac84760255e44c767b1c0393baabd3))
* **docs:** corrige mkdocs strict — AGENT_DIRECTIVE no nav, ai-collectors sem mkdocstrings, __init__ nos pacotes ([609caf0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/609caf07f0f2aeb9bcc8ba5ee630a69ac5daf252))
* **docs:** prevent duplicate automated changelog headings ([53e4721](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/53e47211b9505a1d62daa0bac5297b08b1a03a90))
* **engine:** ignore MANIFEST_REL in stale_manifest — prevents infinite docs(sync) loop ([b1e382f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b1e382f5fc3185a14d64a980c86c61584fe65a02))
* escape newlines in Python prompt strings to fix YAML syntax error ([7e3ed77](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7e3ed774df6646a41f550c74281c770a21173878))
* **gates:** format test_release_docs.py with black ([5dde6aa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5dde6aa5f87d3c1b2a4288edbcf6d862c80ca8e6))
* **gates:** include 'groq' in provider fallback assertion ([ff4204f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ff4204fcbf068334cf20518e821f3ffac333393d))
* **gates:** make _ensure_browser tests deterministic + remove broken minimax model ([458e051](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/458e0511c892a4cccb9f8bc4a2bbb3f74c5fd05c))
* generate repo_files.txt before analysis to provide LLM context ([3cddaaf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3cddaafd9c0948e472ea0d32867a7679357f7194))
* **healing:** prevent pytest-asyncio hang and silent failures ([9c5275e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c5275e94eb3e92d46ff86b722c524f16192d08a))
* improve LLM prompt to extract exact failing file from workflow log ([d0e09ce](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d0e09ce0fa63c517895e986e3be257b0cdb03200))
* **llm+docs:** use working OpenCode default + register index.md in nav ([e871e8a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e871e8a386ec72d8a9f094862cb6081bdde71cf5))
* **llm:** Groq free tier retired; reorder provider chain ([dca5e54](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dca5e543d4d166b2e8730063a47fd39a7f2cab8a))
* **llm:** openrouter/free default model ([55d37f0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/55d37f0ddf74a6fe258885478568938f45e8c0dc))
* **llm:** point OpenCode provider to opencode.ai/zen endpoint with hy3-free and fallback pool ([fdcb756](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fdcb7566d5b53ae3bfa96d817ff1e988057a3e64))
* **llm:** refresh dead OpenRouter free slugs, hard timeouts, full provider cascade and blacklist reset ([ce2ecba](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ce2ecba46aa0d3389614000f50e896c6276ec515))
* **llm:** remove unavailable opencode free models deepseek-v4/mimo, add confirmed zen free fallback list ([c46f9d4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c46f9d4e4c0f5433605f191424f651a2e1b3ca16))
* **llm:** reorder providers openrouter/opencode/gemini ([#126](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/126)) ([62cdb62](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/62cdb627e48fa580735d0a38aaef976b2cc9c4d6))
* **llm:** skip Groq in auto-detect + optimize test runtime ([bef4ced](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/bef4ced4e2074e1c15ba667883cdefc8956dd0da))
* **llm:** update tests for openrouter-first chain without gemini ([2cd167a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2cd167a69ce0898e3f58d5ed28d9b25cba3dda64))
* make auto-healing fail when LLM misses affected_file_path ([2ee4a8b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2ee4a8bbae45c71e00f262509ccaa97160599295))
* **mkdocs:** remove deleted doc refs from nav (refatoracao, improvements, audit, internal) ([de16889](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/de16889cfd9583bcb484163294bcad8dd9e5f25c))
* **mypy:** add openai type stub to satisfy strict checking ([109d706](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/109d70618e03623f705d68c7077a13bd01e03137))
* **opencode:** adicionar GITHUB_TOKEN ao env (necessario para PR/branch) ([c189595](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c189595d3604539521bb2e0025a8bf694dfcad7a))
* **opencode:** atualizar modelo para mimo-v2.6-flash-free (v2.5 removido) ([fe9af7b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fe9af7bc4fb660488cd44950b557ef45ee7cf376))
* pass all 4 quality gates (ruff, black, mypy, pytest ≥95%) ([13118fa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/13118fa96fba32d24d967bcabcf456aceeaf4aa8))
* **pipeline:** add type:ignore for FastAPI decorators with --disallow-untyped-defs ([dc1ce00](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dc1ce00f17db88f5ba6bc32bae298bcef38ac25f))
* **pipeline:** delete git tag alongside release to prevent 422 on recreate ([d089d24](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d089d24bdde028dd872945cfc7727d0b8d6afdce))
* **pipeline:** handle empty commits gracefully + add all generated files ([0e5fc09](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0e5fc0936579de1d46a285f521e64a287c79d6aa))
* **pipeline:** handle immutable releases gracefully in release creation ([f723611](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f72361182334e20c4f2a86f0731d40ac22656464))
* **pipeline:** install Playwright system deps with --with-deps ([3d2ee63](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3d2ee63dfd8c9d1c6ea1c0e0e4745ca719b34886))
* **pipeline:** log stderr for failed release creation attempts ([e06a621](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e06a6212a1cdab5a12806fd234ae845aac9a4905))
* **pipeline:** pass llm to process_single_release + enrich README + fix tag format ([d675cd9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d675cd9856e4e5da45afbb7859ac88e75921a050))
* **pipeline:** pre-detect immutable releases + handle 422 from tag protection rules ([08333e1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/08333e1c3afeb9614196a756788c0211a9613b64))
* **pipeline:** support RELEASE_TOKEN PAT fallback for gh release create ([9e23c58](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9e23c580c21b58fecc59a6959c96609b01c51a5a))
* **pipeline:** use git stash to avoid local changes conflict on pull ([6e3c5d8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6e3c5d809a3ad50fa3d5a1e21747d1fd06fa7e46)), closes [#111](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/111)
* **plano:** limpar artefatos, corrigir coroutine await, atualizar PLANO_DE_ACAO.md ([57e3f00](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/57e3f00fc827a90895cf274387151aee592d1282))
* prevent PR creation error when GITHUB_OUTPUT is not set ([3cdd88a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3cdd88a196e651466cc42142d812e562b1d26cc9))
* **python-quality:** capturar NUMBER robustamente + comentario /oc fix com fallback workspace ([b53c070](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b53c070e01172d5894a248a84bb17aa843f6fc1d))
* **python-quality:** corrigir captura de issue (remover --json, extrair URL) ([e35bca3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e35bca3f3fb463a590c5b36c236089b28a899bb4))
* **python-quality:** fallback busca pelo titulo + limpar erro src ([bd0e348](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/bd0e3483fb4cca116a8f9dd10e5dcfd808fb844e))
* **python-quality:** incluir testes no escopo do /oc fix automático ([78f33d9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/78f33d94fd57cbda8e920b92aee84a042e4aebcb))
* **python-quality:** simplificar persistencia para /tmp/issue_number.txt ([8e560d0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8e560d0c0a6877c7e6eb5da34d058a8dda699bd4))
* **python-quality:** usar GITHUB_WORKSPACE para persistencia do issue_number ([9e3e5a4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9e3e5a48afce4a6bb28b240892b7ad7fb0ac54fc))
* **quality:** add missing newline at EOF in src/infrastructure/api/__init__.py ([53efe5e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/53efe5e7ab889b082a70e1e1230f915d81bdff7b))
* **quality:** apply black py314 formatting (PEP 758 except clauses) ([8f25bea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8f25bea308b4f462cab67cf9f0ce874613c32623))
* **quality:** corrigir ruff/black e limpar artefatos ([#141](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/141) [#142](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/142) [#143](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/143)) ([110adaa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/110adaae6b6b2624f5ccbf2e2ed4a7a23e3b62af))
* **quality:** format codebase with black 26.10 (PEP 758 except-unparenthesize for py314) ([e06c05f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e06c05ffc7d862ec946644362ea77ea6f0af6bf6))
* **quality:** remove unused json import in llm_service ([2a45cfc](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2a45cfc6754ca5e1717c2c13a72a6a9441fc4ef7))
* **quality:** resolve ruff, black, mypy, tests, and docs sync issues (Phase 1 Modernization) ([#228](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/228)) ([f6e284b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f6e284b17eb606c75846e25b232b5971a9d46cfb))
* **readme:** eliminate nested details truncation bug in release blocks ([934a9ec](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/934a9eca9bed495ebd127e6341933712dfa2b16a))
* **readme:** regenerate empty Winter '27 blocks + reject fallback caches ([f408593](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f40859390725cf80c0bc11fef4260e616655198b))
* recover browser when playwright instance is None ([4511a1c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4511a1c94e7e5f79ccec335ea560eb891f694ad0))
* **release_docs:** fix README empty block detection + update AI summaries ([79e16e7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/79e16e73e15ee29634115f0f217d0523494d6091))
* **release_docs:** preserve all existing releases, only regen latest expanded ([74a4eb1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/74a4eb1e70cd718899879d6041d07c1ac1bac147))
* remove markdown code fences from YAML workflow to fix syntax error ([8b462e5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8b462e5e1e30c635f2d06e4e1025ad9b4f7ccdd6))
* resolve merge conflicts in knowledge_server and test files ([8abf54a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8abf54aee69c818fd808743394940d405229d070))
* **security,quality:** corrigir alertas CodeQL 91/92 + gates (ruff/black/mypy/teste) ([63cbf69](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/63cbf69e2a50d78d640864668b8c0c2df921a743))
* **security:** resolve CodeQL path injection and URL sanitization alerts ([fd3016f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fd3016f1b3536921eaeb7c5bfb67a125fb601747))
* **sync:** black formatting docs_sync_engine.py (issue [#141](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/141)) ([37274da](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/37274da399545dc6a16e550b7632330bbf61a017))
* **tests:** isolate ambient LLM provider keys from the test session ([b53dbbe](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b53dbbea0799ce9d42d9f30b77837ef4b2e5f293))
* **tests:** resolve Python Quality gate failures ([033a8a8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/033a8a8986a1a1fe455837f4e07e3c15c12fe33a))
* **types:** add prometheus_client stub (resolves mypy errors in src/health.py) ([a69fe52](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a69fe5263b5569de2ed975ea2ee4e1647aab4cf0))
* **workflow:** usar PAT (COMMENT_TOKEN) para comentário /oc fix e acionar OpenCode ([0e63e4e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0e63e4e5c814ec6397abdc08b2421adf9d205d89))


### Dependencies

* add structlog and mcp to fix test collection errors ([ba39364](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ba393648cd6e4805a7649e7a02b9c5e30924eef4))
* add structlog and mcp to fix test collection errors ([b19d9b1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b19d9b1e1d5e9897a8bb9160d33f705dd5744c3c))
* **deps-dev:** bump black from 26.10.0 to 26.10.1 in the dev-dependencies group ([#210](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/210)) ([4e76705](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4e76705f32ca2e169584c1edd56e5a2b9eb0f310))
* **deps-dev:** bump black from 26.3.1 to 26.5.1 in the dev-dependencies group ([#138](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/138)) ([cb00cda](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cb00cdaee650024bb76ffb923c5300dd0a256455))
* **deps-dev:** bump black from 26.5.1 to 26.10.0 in the dev-dependencies group ([#183](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/183)) ([525e688](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/525e688db3794ed5703b2f2e12718c3f62370485))
* **deps-dev:** update black requirement from &lt;26,&gt;=24.0.0 to &gt;=24.0.0,&lt;27 in the dev-dependencies group ([#132](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/132)) ([5b81205](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5b81205088b9bcf665dc06889dd7ba45a8f49f82))
* **deps-dev:** update black requirement in the dev-dependencies group ([e8463f1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e8463f191401c6c51167c08b571e5d87522cb6b7))


### Documentation

* add banner2.png at the end of both READMEs ([da8ed31](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/da8ed31fc2568b7762f71d6dde03f7bddc5dd515))
* add dynamic release badge via shields.io with RELEASE_BADGE marker ([ceb4b0f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ceb4b0f86860bcb36d23f721083752c3e1cb8f80))
* add GitHub topics plan (salesforce, etl, fastapi, etc) ([edfd714](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/edfd7146d3d016ae785124f92fbc6200ff125371))
* **agents:** add quality issue fix convention ([#141](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/141) [#142](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/142) [#143](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/143)) ([8b29db6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8b29db6da6d29e21e3bdfe75a3c30f9d1c588e89))
* **agents:** comprehensive rewrite with all context from 31/08-01/09 ([fd1798a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fd1798a079d5a4277d15ccbd96827ddd8034fce1))
* **agents:** correct stale claims (i18n, auto_healing dirs, newPrompt) + document sync engine ([51170f0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/51170f063bf496004bdf5ecd1cc9761678d13ce9))
* **agents:** document GitHub Project integration for issue tracking ([f4219cd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f4219cdb0174ef546600ed236f60ae5a07ad89bf))
* **agents:** registrar feature opencode /oc fix (mimo-v2.6, GITHUB_TOKEN, permissoes write) ([a6a8259](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a6a8259b51f9696d6a13cb2f620adb4c5b92fc4f))
* **agents:** rewrite with verified state after deep analysis ([1ee0684](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1ee06840970f7dadece3fd8e237a7bdd928ab0cf))
* **agents:** update AGENTS.md audit entry and .gitignore ([56d8555](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/56d85559d4acbf48af54a94f577026fd75e71d0c))
* **ai-docs:** documenta ruff 0.17.1 via apt vs bloqueio &gt;=0.5 Termux ([f95928a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f95928abe7fc3fcc3c922ceffd35e77f61bd481d))
* align Python 3.14 references ([195b48f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/195b48fe8c7833327865bd1e4e9005be5da24fbc))
* align Python version refs to 3.13+; remove tmp prompt ([21a565b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/21a565bddbfab5a7c6f5251a50e99e98dec536ff))
* align README feature table and directory comment to 3.14 ([f511f0c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f511f0cf7a4a8e2943b9742338f9c141f01e21a8))
* atualização automática via IA [skip ci] ([a2ab337](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a2ab3378406863c32d16d225a1055a61b492dc86))
* atualização automática via IA [skip ci] ([7a51bb2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7a51bb2a63bd28c40877d1679e5b3a5857f25669))
* atualização automática via IA [skip ci] ([3b5b0a7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3b5b0a774709654af060cbee99e558582a342064))
* atualização automática via IA [skip ci] ([e851980](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e8519804b7c7a48f197bc66d2d5fc70a7b5b4563))
* atualização automática via IA [skip ci] ([0b96e13](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0b96e13a9159a6862ab24c86ff1183cb09704180))
* atualização automática via IA [skip ci] ([e86f121](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e86f1213989c7dfd6f16438bea6b3eed0096cab2))
* atualização automática via IA [skip ci] ([a6e945c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a6e945ceb4d8723810fdb1bf54bf1716e444257a))
* atualização automática via IA [skip ci] ([5288e02](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5288e02c47bb45c46c28ce9512c9366251906264))
* **audit:** consolidated 8-phase diagnostic report (2026-09-02) ([e657020](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e65702042caeff62db8e81ac4ee25bdc12d9cfa1))
* **audit:** corrigir linting e link-check no workflow de sync ([6be0f54](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6be0f54fef82b7eff16142e99708976651e14dbc))
* **audit:** migrar lint config para JSON e commit final ([7e2566d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7e2566d74d42dfb8d0888bb4346fd130ba28f6f1))
* **audit:** refatoração da documentação e workflow de sync ([b186463](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b1864639e1d76fb69be199ee422406c884e70bf0))
* **audit:** refatoração da documentação e workflow de sync ([#129](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/129)) ([b55efd0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b55efd0ac7f39736eb3bb5b6bb798cd39c301b13))
* **changelog:** fix markdown lint errors (MD022/MD032) ([f722d2c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f722d2ce45eb615568fbdec248cad5d07a5ee0d3))
* **changelog:** fix MD001/MD025/MD024/MD032 lint errors ([160aede](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/160aedef61d1afeb9697defc0290fbbdef0661c2))
* **changelog:** fundir raiz (CHANGELOG.md) + melhorias grandes ([b8a594e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b8a594edd181431dcf22b3983b1f661a70dc4793))
* **changelog:** inclui todas as melhorias grandes — refatorações e features ([54d4696](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/54d46964d50e436f713b88fee5f7236915d06d1e))
* **ci:** document pull_request_target GitHub policy caveat (Nov 2, 2026) ([8143fe4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8143fe4c1ca37bf0ca29acb2761d522a72d30620))
* **ci:** harden documentation-sync workflow — deterministic engine, LLM-free reconcile, remove secret injection, soft mkdocs gate ([9a18cc9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9a18cc9c225d073e6c0f84168f034ab4be17bb7c))
* final reconcile and manifest update ([365ef25](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/365ef2531fa2175231ecca4f4b41e5a28796fe14))
* final reconcile navigation and inventory ([e8e9987](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e8e99875e40f7faad18a92657c2b3c4e7b48cf7a))
* final reconcile navigation and inventory ([0d98de1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0d98de1f72026dc49840480047536dfc8d3dc38b))
* final reconcile navigation and inventory ([4cc3b91](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4cc3b9140dc350fe3440889deb6852d9dad37550))
* final reconcile navigation and inventory ([6d54fde](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6d54fdef391298c9e8bb31ad75a15341e2b46fe5))
* final reconcile navigation and inventory ([7930b0f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7930b0faed56cee58adc62b72c28cb1a78181365))
* final reconcile navigation and inventory ([3f64363](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3f64363b723e1c4e61050de4dacfe187f37d5d3b))
* final reconcile navigation and inventory ([2762747](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/27627472060a5a400482293034d79fe4f18b42d8))
* fix broken links in test files and update index ([d9ddc85](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d9ddc85d31857d91408e786241cd4e3c3ae83fc4))
* fix markdown lint errors in DEBITO_TECNICO.md ([34c8c19](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/34c8c1990205af1242f86c90e9f3dd34281ff158))
* fix MD024 duplicate headings in AI-generated docs ([c698ab5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c698ab54e6382c73db4d97a687b87a780212d11e))
* **lint:** corrigir MD022/MD024/MD032/MD040/MD047 ([7ae453d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7ae453d669de879dce69b5255b8ae63dcf8dea78))
* **lint:** corrigir MD022/MD031/MD032/MD024/MD040 em 4 arquivos ([3556c1c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3556c1cfbf8c5237efeb7bbdd836c9ca9e46ffe9))
* **lint:** corrigir MD024/MD031/MD040 restantes ([4c433ba](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4c433ba948c134281b61ed127031d7310a7786bd))
* lock manifest baseline (56 doc-map entries, content-stable) ([237e93d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/237e93d34272f50ecfddec1aa779ba645f55db0a))
* lock manifest baseline (post-workflow hardening, content-stable) ([9c7842c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9c7842c7dde13606420884ece3bf7de11bc6fe79))
* pin documentation manifest to reconciled baseline ([98b6e77](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/98b6e774fd242d59a6404d82e0f1c6bc935a7d73))
* pin manifest baseline (content-stable idempotency) ([49b9878](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/49b98786f7bbb905a144ca75e1e41d876ae19275))
* pipeline AI-docs — revisão (free tier LLMService) ([#199](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/issues/199)) ([b2708d1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b2708d1fa67796341061fbe2cf02a9c397131e5b))
* reconcile documentation manifest ([a9ae928](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a9ae928282b31f56e1773a7a97edf69f17755698))
* reconcile navigation and inventory ([ee2537e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ee2537efc62753808e641fc1201ecafe490fc617))
* reconcile navigation and inventory ([4846445](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4846445aed3a2138f02c172fd430c6b0945a3bbd))
* reconcile navigation and inventory ([10683ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/10683ea8605ed70e0d5edc095e13a68349297caa))
* reconcile navigation and inventory ([06edc96](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/06edc9607d4d5ff14a044de83a6c4b44e33f927b))
* reconcile navigation and inventory ([f5b32fb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f5b32fb7a6e556cc80738cd8a6ca091bf624edee))
* reconcile navigation and inventory ([5f59e28](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5f59e28bf588b243aea219029e8d00c651a39bef))
* reconcile navigation and inventory (final) ([1ab89c1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1ab89c15e9961370df47c3de39f0b54a1aec10a7))
* reconcile pt-BR + en documentation drift ([7f0b7bb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7f0b7bbd8d08ba0fecde834f56e9cff56d6c2cf8))
* remove banner2 from table at top, keep only banner1 ([a65163b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a65163b3041799216da3057db04addcbe6189ffc))
* remove random banner legend from top banner ([32d22a5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/32d22a5f2365aac4fcaf4626f0bbd1b398dc41f8))
* remove section title for banner2 ([5a4fd6c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5a4fd6c43c7e8df6e6f6c9a0df3df9cc3b8da5e4))
* resolve manifest merge conflict ([6024cdf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6024cdf01ca3e6315a54a82f8c15ebd4ce0718a0))
* resolve manifest merge conflict ([20341a9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/20341a97add733e932dabb0c74fd528ec0b460b0))
* resolve manifest merge conflict ([b183939](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b1839395b312eb952749582f04921352c67d8e19))
* resolve merge conflict in documentation manifest ([c6589d1](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c6589d10ae37c7cf5e102d5c45766489f9bfe36a))
* **roadmap:** corrigir MD022/MD031/MD032 em v4.md ([e29e481](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e29e4817d5d162999d7b239e782bad4876bf5fa5))
* **security:** add repository security policy (SECURITY.md) ([cae5caa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cae5caa103fbfd05d05a7129035fc7596c86e695))
* **sfel:** ADR-006 Feature Evolution Ledger — decisão de arquitetura completada ([07ec5eb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/07ec5eba2c20891795dccef5162b66f5b69c6a45))
* **sfel:** documentação do Salesforce Feature Evolution Ledger (ADR-006, README e docs/index.md) ([fa000e8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fa000e8859fe9756b6c0bf9ab6b54aefd398fade))
* sync documentation and fix markdown ([dfb6631](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dfb66315f597b23ad58345c31b591a5cf1d139f2))
* sync documentation and fix markdown - final reconcile ([2dca201](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2dca2010547c124b676c739f0d1629a556955303))
* **sync:** manifest repo_sha to 4f4d953abfcfbf7bfd9bc20cd51ad28ec392102b ([6f20e69](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6f20e691e9fa2fe174769a47039b92b01e0793a0))
* **sync:** manifest repo_sha to 67f67d0bed8b08707516fafb162b143c49340e24 ([03bb4a4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/03bb4a4dbacb97d9e9d57b68aeda4044e8af5a51))
* **sync:** manifest repo_sha to HEAD ([67f67d0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/67f67d0bed8b08707516fafb162b143c49340e24))
* **sync:** realign manifest repo_sha to HEAD (c25992e) post-reconcile ([60e034a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/60e034a25326b8a47869bd1c3123aa994e97fbf2))
* **sync:** reconcile docs — fix nav (ADR-006, auto-opencode), refresh manifest, directory tree ([ef64d71](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ef64d71f71aeb97ea4300ef67ba2a49db0aa5860))
* **sync:** reconcile documentation — 2026-08-26 04:41 UTC ([6d18cdf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6d18cdfea759685520c1add7c64fe4b2571368ad))
* **sync:** reconcile documentation — 2026-08-29 16:43 UTC ([d01e8ee](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d01e8eeb3adf1795e7d754205e4a41c7d71bd872))
* **sync:** reconcile documentation — 2026-08-30 20:24 UTC ([96401aa](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/96401aa489d335a1dde3d0fc632f67295972b793))
* **sync:** reconcile documentation — 2026-08-30 22:59 UTC ([056b09b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/056b09b1894100031f74fc9d8e88bfc1ddafc35a))
* **sync:** reconcile documentation — 2026-09-04 11:19 UTC ([ef829f2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ef829f2bf2d5b4f5d43b67576b06d7d92f4ac0a3))
* **sync:** reconcile documentation — 2026-09-09 20:56 UTC ([4b789c6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4b789c64aabfd15f0563a67245c01abd77889ed7))
* **sync:** reconcile documentation — 2026-09-14 02:58 UTC ([ac5af8c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ac5af8c3e3e39db9a64d91b02bb755895b0929dd))
* **sync:** reconcile documentation — 2026-09-16 21:43 UTC ([cdc5eb2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cdc5eb28eab32f06992c110148654cbbfe94123b))
* **sync:** reconcile documentation — 2026-09-17 01:40 UTC ([c5d5083](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c5d50835664f33d6fd8f138cb7476384b480e442))
* **sync:** reconcile documentation — 2026-09-17 05:01 UTC ([6d70638](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/6d70638bd4932b3f2f2495ba95dfc34bf784d7a7))
* **sync:** reconcile documentation — 2026-09-17 05:30 UTC ([d0719f3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d0719f32578981bc896b3a44cc1e0a650484468b))
* **sync:** reconcile documentation — 2026-09-18 21:03 UTC ([881ebec](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/881ebecad80c04ab9b94339b8f24b48a9e60e126))
* **sync:** reconcile documentation — 2026-09-19 01:39 UTC ([eb275de](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/eb275de410babaa99357244379779ec368bdfc67))
* **sync:** reconcile documentation — 2026-09-19 14:08 UTC ([a18c149](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a18c1499d64c5028d069f99b6f36b9b1b82b3b70))
* **sync:** reconcile documentation — 2026-09-21 22:00 UTC ([96b8a22](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/96b8a2280159ebacfdfad4d02425dd80e9f5b4c5))
* **sync:** reconcile documentation — 2026-09-22 02:22 UTC ([443cd89](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/443cd89c0e6119d1c22db875be9aa59a8d1051f1))
* **sync:** reconcile documentation — 2026-09-22 12:28 UTC ([45f2453](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/45f2453b4382d78aba0e65bf475d71c12c0a28f3))
* **sync:** reconcile documentation — 2026-09-22 12:38 UTC ([57d7f57](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/57d7f579281b1125bf816292fa7b21d62eb3dc3d))
* **sync:** reconcile documentation — 2026-09-22 13:16 UTC ([37499ad](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/37499ad6661c0fe3226dc7d04cb2cf5fd0303a56))
* **sync:** reconcile documentation — 2026-09-22 13:23 UTC ([b3f023d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b3f023d02995d8ec9faead9853059aa4fa5a37ee))
* **sync:** reconcile documentation — 2026-09-22 13:55 UTC ([fce2add](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fce2addaa91411df662067631d16d8c91ed38eeb))
* **sync:** reconcile documentation — 2026-09-22 14:41 UTC ([dfe299f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dfe299f872342443ab35859d7150b9822c8733f5))
* **sync:** reconcile documentation — 2026-09-22 14:58 UTC ([c9134d3](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c9134d3827c94793b5a3ce637865e7aeb1e4d50c))
* **sync:** reconcile documentation — 2026-09-22 15:01 UTC ([0a99890](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0a99890c11b26fb0044ab7fe73c423bdd2b79e30))
* **sync:** reconcile documentation — 2026-09-22 15:04 UTC ([1341d89](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1341d89f684efc77b4e2d2350a686c9d1909236c))
* **sync:** reconcile documentation — 2026-09-22 16:20 UTC ([906bb0c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/906bb0cba9680c1c2b5f4a8d772fbb2519eeff69))
* **sync:** reconcile documentation — 2026-09-22 16:37 UTC ([68ac9ae](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/68ac9aec00429bb8b236ab1d4f4234a80ad5ce68))
* **sync:** reconcile documentation — 2026-09-22 16:43 UTC ([52b3025](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/52b302551fe36117df19af68f1910537babcd6db))
* **sync:** reconcile documentation — 2026-09-23 05:16 UTC ([b622e76](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b622e760437acf7d26d515a331daf991d46c176a))
* **sync:** reconcile documentation — 2026-09-23 05:42 UTC ([a92ccf0](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a92ccf028823d893519dbf2de095b4b54fb8ee48))
* **sync:** reconcile documentation — 2026-09-23 05:45 UTC ([2ec783d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2ec783d248f5dff0b42081e0419c7ed55b51e3a9))
* **sync:** reconcile documentation — 2026-09-23 05:48 UTC ([3857f8f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3857f8fcdfd3cad139c9af63cf2d3138638b4649))
* **sync:** reconcile documentation — 2026-09-23 05:54 UTC ([2c3711e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2c3711eafa48f340c9e4d638ab2597e8fc9a9121))
* **sync:** reconcile documentation — 2026-09-23 05:57 UTC ([847aedb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/847aedb6fb709aa4a5f776bc21edc3597e43ea22))
* **sync:** reconcile documentation — 2026-09-23 06:03 UTC ([5d54349](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5d54349b7bb88242de02ba5fa55f5a41fc4270df))
* **sync:** reconcile documentation — 2026-09-23 06:05 UTC ([69f5dda](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/69f5dda8bec9ee2c820c2dc8f6ff3686a5a49c16))
* **sync:** reconcile documentation — 2026-09-23 06:06 UTC ([68686a2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/68686a225dd0b839cd677af5ea4c3da6164c17da))
* **sync:** reconcile documentation — 2026-09-23 06:16 UTC ([3654f3e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3654f3e71f178288300410caa23ea6da8166be9c))
* **sync:** reconcile documentation — 2026-09-23 13:40 UTC ([dfb288a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dfb288a79c3f4be59c055c55013eecb6692c952d))
* **sync:** reconcile documentation — 2026-09-23 13:46 UTC ([25555af](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/25555af3a42871869dff6c2d81d0188ea6c88cdf))
* **sync:** reconcile documentation — 2026-09-26 01:37 UTC ([dee3462](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/dee3462cbf40ea581d7f21c05a024e3095feb62b))
* **sync:** reconcile documentation — 2026-09-26 01:48 UTC ([f708d2f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f708d2fb4a2e00e2daec01244a76d950c273d014))
* **sync:** reconcile documentation — 2026-09-26 01:55 UTC ([9f5d73c](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9f5d73c3ddc6267c4f9f80dcb00918d79621d0e7))
* **sync:** reconcile documentation — 2026-09-26 02:01 UTC ([7738736](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7738736e6ef8a5fac30069747dfa211800fc37e9))
* **sync:** reconcile documentation — 2026-09-26 02:45 UTC ([9359076](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9359076ccb6255956290f81b7bfcd57e94866e20))
* **sync:** reconcile documentation — 2026-09-26 02:51 UTC ([4e49ae8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4e49ae8ecd0f23baeb469175b73aced96be15ee8))
* **sync:** reconcile documentation — 2026-09-28 01:40 UTC ([462a898](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/462a898797e17454ef2a19bbedda549c43cdb521))
* **sync:** reconcile documentation — 2026-09-28 03:13 UTC ([45cda8b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/45cda8b05f39c2305774b7e046a7a4a2d94eb523))
* **sync:** reconcile documentation — 2026-09-28 03:16 UTC ([e7e1f66](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/e7e1f6643f32d3f97801213f59ae41419e494391))
* **sync:** reconcile documentation — 2026-09-28 03:23 UTC ([5420464](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/54204646e38a50be64c487bd908b0d2f99a5a434))
* **sync:** reconcile documentation — 2026-09-28 03:24 UTC ([d3f0e0e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d3f0e0e6233c885dcc190870aee19da588a4bfff))
* **sync:** reconcile documentation — 2026-09-28 03:44 UTC ([223edb8](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/223edb8f5601e198730693d6ba5e1f72cddc327e))
* **sync:** reconcile documentation — 2026-09-28 12:24 UTC ([f3af76a](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f3af76aa3378cc67258fd3504b6136a7da8319ec))
* **sync:** reconcile documentation — 2026-09-28 12:25 UTC ([5585bec](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5585becc8254637bac91a8b1eb08fe9352370244))
* **sync:** reconcile documentation — 2026-09-28 20:17 UTC ([b256b89](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b256b89f2240ba786ca40fecb0d1ccd075ec3bd3))
* **sync:** reconcile documentation — 2026-09-28 20:51 UTC ([28feabd](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/28feabd3d3caa6d12c85a890eaac9d9b23ed2155))
* **sync:** reconcile documentation — 2026-09-28 20:56 UTC ([f9bdb35](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f9bdb35fcba564ca9abe3f6c31ae1aaebd1d5803))
* **sync:** reconcile documentation — 2026-09-29 05:14 UTC ([cae9e41](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cae9e41e62726c378d811ea9b17a621662bfba65))
* **sync:** reconcile documentation — 2026-09-29 09:46 UTC ([ca01db4](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ca01db436fcc787f2fb769922b64afdc27e6fe26))
* **sync:** reconcile documentation — 2026-10-06 00:05 UTC ([3b02a53](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3b02a53b8ad3124cfa95771f54614a3cf9444814))
* **sync:** reconcile documentation — 2026-10-13 08:05 UTC ([9d90eb9](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9d90eb961b07c4821c6d1074b2556df18c7df5df))
* **sync:** reconcile documentation — 2026-10-13 14:16 UTC ([cbd8a61](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cbd8a6141037d347b49b403eb662a06cd0eddc83))
* **sync:** reconcile documentation — 2026-10-13 14:46 UTC ([a829831](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/a8298311f995479d703f1eb88efc463cb1025a59))
* **sync:** reconcile documentation — 2026-10-13 14:51 UTC ([fc77422](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/fc774221efc495330eb1705d00915b1b1ff8be60))
* **sync:** reconcile documentation — 2026-10-13 14:53 UTC ([907b628](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/907b6284fa46d0e3c9b3637f046ce90164e79e7e))
* **sync:** reconcile documentation — 2026-10-13 15:01 UTC ([7c1957e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7c1957e3c7c04e0d5595cf2d63a8fedc2792b141))
* **sync:** reconcile documentation — 2026-10-13 15:10 UTC ([560ad20](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/560ad2007d8ccec66d7c9a80bba5759bd997bfa5))
* **sync:** reconcile documentation — 2026-10-13 15:13 UTC ([5dc2732](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5dc27328cf165180e3f4021ac8b780bf755eb62d))
* **sync:** reconcile documentation — 2026-10-16 02:12 UTC ([5e6f6eb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5e6f6eb7aee84eed521048f786062945a54514ff))
* **sync:** reconcile documentation — 2026-10-17 04:01 UTC ([93cf8c2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/93cf8c25ca491c97ca785e225954dee588c15a4e))
* **sync:** reconcile documentation — 2026-10-17 04:41 UTC ([3006ef5](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3006ef582adc02d4215e1441adb044a592209ad0))
* **sync:** reconcile documentation — 2026-10-17 05:00 UTC ([2372ac7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/2372ac791ed5771a0c9149c6d4478530ef34590d))
* **sync:** reconcile documentation — 2026-10-17 13:48 UTC ([c25992e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/c25992edc1a559d3fd1d2fed0fb0b6c3e8769b6c))
* **sync:** reconcile documentation — 2026-10-17 13:51 UTC ([8d1e7db](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8d1e7dbdbb5e8dc9f6fced35d33cb41cc92e1276))
* **sync:** reconcile documentation — 2026-10-18 01:05 UTC ([487258b](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/487258bd4f6c51a68bf68cf89ca07e91eb54dc6a))
* **sync:** reconcile documentation — 2026-10-18 02:25 UTC ([5c6ed08](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5c6ed08e0c3de71f9b5bda7f5fe8fd11cef2e5c5))
* **sync:** reconcile documentation — 2026-10-18 03:30 UTC ([f09ca03](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/f09ca031a46bc5c98155ed3ffae95e4a6b8d5ebe))
* **sync:** reconcile documentation — 2026-10-18 03:34 UTC ([1814338](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1814338fcc844ee8e2c342a9de72f1e0267e0988))
* **sync:** reconcile documentation — 2026-10-18 03:47 UTC ([80b471d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/80b471dff80d73cbbf4c7a0443889432c5612eb0))
* **sync:** reconcile documentation — 2026-10-18 03:55 UTC ([3d61906](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3d619060ced8ff42c77c9011f831a91b00594cbb))
* **sync:** reconcile documentation — 2026-10-18 03:56 UTC ([ca98e04](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ca98e049dcd25c7bf90dfc298821d2209b2c1d7c))
* **sync:** reconcile documentation — 2026-10-18 03:59 UTC ([5bfd2eb](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5bfd2ebc9387b3bc067c3157cc3ee3bd99eba86c))
* **sync:** reconcile documentation — 2026-10-18 04:03 UTC ([ec58840](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/ec58840a56db5d1175abb744857ef32a075908dc))
* **sync:** reconcile documentation — 2026-10-18 04:06 UTC ([eb88886](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/eb888868ee442dd6d810269e65fb59f5fc10b046))
* **sync:** reconcile documentation — 2026-10-18 05:09 UTC ([4190b68](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4190b680d27e56b43f1d40a29c090912a42d2576))
* **sync:** reconcile documentation — 2026-10-18 05:15 UTC ([622ec83](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/622ec83ea0e7e18e1da44635777f999d091126e2))
* **sync:** reconcile documentation — 2026-10-18 05:38 UTC ([cad054f](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/cad054f96810a35e8db9b8225c9f5058dc150461))
* **sync:** reconcile documentation — 2026-10-18 05:51 UTC ([633fdce](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/633fdce03927fc7d661575d565bee3aa6c7c7f5e))
* **sync:** reconcile documentation — 2026-10-18 06:17 UTC ([d3eb885](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/d3eb885e35c7fc8b51f61c922c3afdda006ba11c))
* **sync:** reconcile documentation — 2026-10-18 06:22 UTC ([0b8070d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/0b8070db47b5d202ec63fc5ec406250c58b15d12))
* **sync:** reconcile documentation — 2026-10-18 22:46 UTC ([41d581e](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/41d581e27676b64585b15a4162effc9a63180cf4))
* **sync:** reconcile documentation — 2026-10-18 22:48 UTC ([822e92d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/822e92d056b9ded9080d76e2c3839c197ff9fe3b))
* **sync:** reconcile documentation — 2026-10-19 02:01 UTC ([7806097](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/7806097773d86f267997c4328243fa3578003724))
* **sync:** reconcile documentation — 2026-10-19 15:03 UTC ([43158d6](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/43158d632f6dc21ff23dbcd3faa410211a19926d))
* **sync:** reconcile documentation — 2026-10-19 22:23 UTC ([917cb93](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/917cb93999440c8ddc8c06d08ed1dbc2fa33b159))
* **sync:** reconcile documentation — 2026-10-30 07:23 UTC ([257c3ce](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/257c3ce2431dc60747c5d6aa4d680dff3eb453ff))
* **sync:** reconcile documentation — 2026-11-09 22:24 UTC ([102a443](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/102a443251dff9c4175db220643564ee28994f3e))
* **sync:** reconcile documentation — 2026-11-14 06:19 UTC ([8b77069](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/8b770695b415f87346c46d07f53afc0040e00f90))
* **sync:** reconcile documentation — 2026-11-15 15:23 UTC ([9a26524](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9a26524cec7cca3c4cbb37c00e3734ed7699f153))
* **sync:** reconcile documentation — 2026-11-16 12:36 UTC ([9f8a5d7](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/9f8a5d746aff643da29b37c3454ebd8c22127c3a))
* **sync:** reconcile documentation — 2026-11-16 12:49 UTC ([16f0833](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/16f0833709cb2109ddd56c025d883da07b6f2dc1))
* **sync:** reconcile documentation — 2026-11-16 13:21 UTC ([eca6b82](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/eca6b8221186013ae386853b2a8647c8eb35e5a8))
* **sync:** reconcile documentation — 2026-11-16 13:24 UTC ([28fb39d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/28fb39dc4480e74411fdf27657e1164bd0883663))
* **sync:** reconcile documentation — 2026-11-16 13:36 UTC ([350c5ea](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/350c5ea074fad9ce5bdf415d377aa96c5519e94a))
* **sync:** reconcile documentation — 2026-11-16 13:40 UTC ([1419044](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/1419044a63a4f48b83aaea3e7aab38e631ea19ba))
* **sync:** reconcile documentation — 2026-11-16 13:43 UTC ([b8355cf](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/b8355cf7f3c6402aac7fc80e88b922fd092fde90))
* **sync:** reconcile documentation — 2026-11-16 13:58 UTC ([3253a5d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3253a5d1e95e32def73da872f590ec52082f489d))
* **sync:** reconcile documentation — 2026-11-16 14:09 UTC ([00ab953](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/00ab953f649abe8dc6ca6f4ac54caddc513eef06))
* **sync:** reconcile documentation pipeline (audit + reconcile) ([5f7ca50](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/5f7ca50718dcca408523ea6cd83ac470e6dafedd))
* **sync:** reconcile manifest repo_sha to HEAD () ([4f4d953](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/4f4d953abfcfbf7bfd9bc20cd51ad28ec392102b))
* update manifest after reconcile ([3a203b2](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/3a203b2e4595cd83c3cd1c86f584981f3713e745))
* update manifest and nav after reconcile ([34dc53d](https://github.com/Fatal1tyBarucco/Salesforce-WebDev/commit/34dc53dd6cfe1048dede50781e4c9b28c002ba76))

## [Unreleased]

### Added
- Added `structlog` and `mcp` dependencies to `pyproject.toml`, required by infrastructure observability modules and the MCP knowledge server.
- Added `fix_md.py` script for markdown correction.

### Changed
- Reconciled the documentation manifest, MkDocs navigation, and documentation files (inventory, links, and generated content), including merge conflict resolution in documentation files.
- Expanded `markdownlint` exclusions for generated documentation directories and ADRs.

### Fixed
- Fixed test collection errors by adding the required `structlog` and `mcp` dependencies.
- Resolved merge conflicts in `src/infrastructure/mcp/knowledge_server.py` and `tests/infrastructure/mcp/test_knowledge_server.py`.

<!-- gerado por IA em 2026-11-16T11:35:56+00:00 — revisar antes de publicar -->

## [Unreleased]

### Changed
- Reformatted `unified_client` and related tests with Black 26.10.0, adjusting ternary expressions and multiline asserts to meet style standards and resolve the Python quality workflow failure; no logic or behavior changes.
- Updated documentation automatically via AI tooling (marked `[skip ci]`); no functional changes.

<!-- gerado por IA em 2026-11-16T10:57:34+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added complete Phase 5 setup with mutation testing, devcontainer, and documentation.
- Added five GitHub Actions workflows for AI PR Review, AI Triage, CI Repair, Scheduled Pipeline, and Release Please.
- Added MCP Knowledge Server for project knowledge.
- Added 28 new test files and golden fixtures for infrastructure components.

### Changed
- Refactored LLM integration and scraping into modular adapters.
- Updated development environment and quality tooling configuration.

### Fixed
- Fixed duplicate headings in AI-generated documentation.

### Breaking Changes
- Removed legacy scraping module in favor of new adapter architecture.

<!-- gerado por IA em 2026-11-15T14:30:24+00:00 — revisar antes de publicar -->

## [Unreleased]

### Changed
- Refactored `src/infrastructure/api/__init__.py` by adding the missing newline at end of file to satisfy the Black formatting gate; no logic or behavior changes were made.

<!-- gerado por IA em 2026-11-15T14:23:21+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added `syrupy` plugin registration in `conftest.py` to resolve fixture snapshot errors.

### Changed
- Updated `docs/.documentation-manifest.json` with new checksums for `pyproject.toml`, `src/infrastructure/api/__init__.py`, `uv.lock`, and added entry for `test_infrastructure_api_graphql.py`.

### Fixed
- Fixed `strawberry-graphql` import error that caused `ModuleNotFoundError` in 11 tests, restoring build capacity and increasing test coverage to 95.35%.

<!-- gerado por IA em 2026-11-15T12:47:38+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added comprehensive test coverage for core, infrastructure, models, and main modules.
- Added Strawberry GraphQL types using ChangeType and added strawberry-graphql dependency to resolve CI test failures.

### Changed
- Refactored the application into Clean Architecture layers in src/core and src/infrastructure, with core, infrastructure, and models modules.
- Updated the documentation manifest and mkdocs navigation for new API and architecture decision documents.

### Fixed
- Fixed the LLMService fallback chain.
- Fixed the GraphQL schema by replacing the generic dict type with ChangeType and corrected API module exports.

### Breaking Changes
- The Clean Architecture refactor may break imports referencing legacy modules.

<!-- gerado por IA em 2026-11-14T06:19:14+00:00 — revisar antes de publicar -->

## [Unreleased]

### Added
- Added design system to the dashboard with dark mode support and accessibility features (high impact).

### Fixed
- Fixed fence state tracking in fix_markdown.py to correctly distinguish opening and closing markdown fences.

### Changed
- Updated actions/setup-python to v7.1.0.
- Updated astral-sh/setup-uv to v10.3.3.
- Updated pyasn1 to 0.6.5.
- Updated uv group dependencies (certifi, filelock, langgraph-sdk, virtualenv).
- Updated aiohttp to 3.14.4.
- Updated black to 26.10.1.

<!-- gerado por IA em 2026-10-19T14:57:56+00:00 — revisar antes de publicar -->

## [Unreleased]

### Fixed
- Fixed GitHub Pages deployment by adding site build job, artifact upload, and separate deploy step, restoring publication of release artifacts.
- Adjusted Markdown headers for MD001/MD036 compliance in impact report generator.
- Changed ai-docs workflow to warn on missing files and include hidden files in AI log artifact upload.

### Added
- Added output token budget management in LLM client with environment variables and exponential max_tokens scaling on retries.
- Added coverage tests for AI and documentation modules.

### Changed
- Simplified exception handling in docs_sync_engine by replacing specific OSError/ValueError blocks with a generic Exception catch.
- Updated documentation manifest with references to new AI-generated artifacts.

### Breaking Changes
- None

### Security
- None

<!-- gerado por IA em 2026-10-19T03:48:57+00:00 — revisar antes de publicar -->

## [Unreleased]

### Fixed
- Fixed LLM completions returning empty responses, restoring documentation generation functionality.
- Prevented duplicate headings in automatic changelog updates.
- Corrected paths in documentation sync pipeline for CI consistency.

### Added
- Implemented new OpenRouter free-tier documentation pipeline with rate-limiting support.
- Expanded change collector with enhanced Git/GitHub change capture capabilities.
- Added failure diagnostics exposure with validated test coverage.

### Changed
- Aligned Black target-version to py314 for Python 3.14 compatibility.
- Updated documentation manifest with new files including README.en.md and ai-docs-audit-logs.md.

## 2026-10-17 — Python 3.14 upgrade

- Pinned `requires-python = ">=3.14,<3.15"` (pyproject.toml) and regenerated `uv.lock` (`==3.14.*`).
- Updated all CI workflows to `3.14` (python-quality, pipeline, docs-sync, docs-build, dependabot, copilot, intelligence-hub).
- Updated agent docs, copilot instructions, LLM fallback prompts, and guide prerequisites.
- Aligned Black `target-version` to `py314`; updated README/table references.
