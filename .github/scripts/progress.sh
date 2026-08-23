#!/usr/bin/env bash
# progress.sh — stage-based progress logging for GitHub Actions run steps.
#
# Instead of a \r spinner (which only animates in the live log and collapses
# to one-line-per-frame in the saved log), this prints a clear header/footer
# around each long-running command so the run log always shows, at a glance,
# WHAT is executing at each moment. Renders identically live and saved.
#
# Usage:  stage <idx> <total> <label> -- <command> [args...]
# Example: stage 2 4 "Reparo determinístico" -- uv run python3 script.py

stage() {
  local idx="$1"; local total="$2"; local label="$3"; shift 3
  # Optional "--" separator before the command.
  if [ "$1" = "--" ]; then shift; fi
  local bar="────────────────────────────────────────────────────"
  printf '\n\033[1;36m%s\033[0m\n' "$bar"
  printf '\033[1;36m▶ [%s/%s] %s\033[0m\n' "$idx" "$total" "$label"
  printf '\033[2m  $ %s\033[0m\n' "$*"
  printf '\033[1;36m%s\033[0m\n' "$bar"
  "$@"
  local rc=$?
  if [ "$rc" -eq 0 ]; then
    printf '\033[1;32m✅ [%s/%s] %s — concluído\033[0m\n\n' "$idx" "$total" "$label"
  else
    printf '\033[1;31m❌ [%s/%s] %s — falhou (rc=%s)\033[0m\n\n' "$idx" "$total" "$label" "$rc"
  fi
  return $rc
}
