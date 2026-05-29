# Cache Management

## Objective

Prevent duplicated release processing and maintain pipeline execution consistency.

## Cache Location

```text
cache/processed_releases.json
```

## Responsibilities

The cache layer is responsible for:

- tracking processed releases
- avoiding duplicated markdown generation
- maintaining release execution history
- enabling incremental processing
- supporting failure recovery

## Cache Lifecycle

### Initialization

The cache file is initialized automatically during the first pipeline execution.

### Update

After successful processing, the release metadata is persisted.

### Validation

Before processing a release, the pipeline validates whether the release already exists in cache.

## Recovery Procedure

If cache corruption occurs:

1. Remove corrupted cache file
2. Recreate empty cache structure
3. Re-execute pipeline
4. Validate generated markdown artifacts
5. Validate README regeneration

## Operational Recommendations

- Never manually edit cache during pipeline execution
- Keep cache under version control
- Validate cache consistency after workflow failures
- Validate duplicate release generation after parser updates

## Future Improvements

- release metadata hashing
- cache expiration strategy
- semantic diff validation
- release fingerprinting
- distributed cache support
