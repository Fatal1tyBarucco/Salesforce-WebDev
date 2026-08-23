#!/usr/bin/env bash
# spinner.sh — animated progress for GitHub Actions run steps.
#
# Usage:  long_command & spin $! "Working on X…"
#         wait $!; RC=$?
#
# The spinner frames are written to stderr with a carriage return, so they
# animate in the LIVE run log (GitHub Actions renders \r). In the saved log
# they collapse to a single line — that is a GitHub limitation, not a bug.
# The wrapped command's own stdout/stderr stay untouched.

spin() {
  local pid="$1"
  local label="$2"
  # Braille spinner frames.
  local frames="⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
  local i=0
  printf '\033[?25l' >&2
  while kill -0 "$pid" 2>/dev/null; do
    printf '\r\033[36m%s\033[0m %s' "${frames:i++ % 10:1}" "$label" >&2
    sleep 0.15
  done
  printf '\r\033[2K\033[?25h' >&2
}
