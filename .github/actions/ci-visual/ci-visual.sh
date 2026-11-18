#!/usr/bin/env bash
# ci-visual.sh — Reusable visual helpers for GitHub Actions logs & summaries
# Source this file: source .github/scripts/ci-visual.sh
# All functions are safe: if they fail, they don't break the step.

# ─── Color palette (semantic, truecolor with 256/16 fallback) ───
# Usage: printf "${C_SUCCESS}message${C_RESET}\n"
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_DIM='\033[2m'
C_UNDER='\033[4m'

# 16-color (always works)
C_RED='\033[31m'
C_GREEN='\033[32m'
C_YELLOW='\033[33m'
C_BLUE='\033[34m'
C_MAGENTA='\033[35m'
C_CYAN='\033[36m'
C_GRAY='\033[90m'
C_WHITE='\033[97m'

# 256-color (richer)
C_RED_256='\033[38;5;196m'
C_GREEN_256='\033[38;5;46m'
C_YELLOW_256='\033[38;5;226m'
C_BLUE_256='\033[38;5;39m'
C_MAGENTA_256='\033[38;5;201m'
C_CYAN_256='\033[38;5;51m'
C_GRAY_256='\033[38;5;244m'

# Truecolor (24-bit) — GitHub Actions UI renders these
C_SUCCESS='\033[38;2;34;197;94m'      # green-500
C_ERROR='\033[38;2;239;68;68m'        # red-500
C_WARN='\033[38;2;234;179;8m'         # yellow-500
C_INFO='\033[38;2;59;130;246m'        # blue-500
C_HIGHLIGHT='\033[38;2;168;85;247m'   # purple-500
C_DETAIL='\033[38;2;148;163;184m'     # slate-400

# Background banners (truecolor)
BG_SUCCESS='\033[48;2;34;197;94m\033[38;2;255;255;255m'
BG_ERROR='\033[48;2;239;68;68m\033[38;2;255;255;255m'
BG_WARN='\033[48;2;234;179;8m\033[38;2;0;0;0m'
BG_INFO='\033[48;2;59;130;246m\033[38;2;255;255;255m'
BG_HIGHLIGHT='\033[48;2;168;85;247m\033[38;2;255;255;255m'

# ─── Helpers ───

# Print a colored banner with background
# banner "TITLE" "color"  (color: success|error|warn|info|highlight)
banner() {
  local title="${1:-STEP}"
  local color="${2:-info}"
  local bg_var="BG_${color^^}"
  local bg="${!bg_var:-$BG_INFO}"
  local width=78
  local pad=$(( (width - ${#title}) / 2 ))
  printf "\n${bg}%*s%s%*s${C_RESET}\n" "$pad" "" "$title" "$((width - pad - ${#title}))" ""
}

# Print a section header (no background)
# header "TITLE" "color" [emoji]
header() {
  local title="${1:-STEP}"
  local color="${2:-info}"
  local emoji="${3:-}"
  local c_var="C_${color^^}"
  local c="${!c_var:-$C_INFO}"
  printf "\n${C_BOLD}${c}%s %s${C_RESET}\n" "${emoji}" "$title"
  printf "${c}%s${C_RESET}\n" "$(printf '━%.0s' $(seq 1 78))"
}

# Success message
ok() { printf "${C_SUCCESS}✅  %s${C_RESET}\n" "$*"; }

# Warning message
warn() { printf "${C_WARN}⚠️  %s${C_RESET}\n" "$*"; }

# Error message (does not fail the step)
fail() { printf "${C_ERROR}❌  %s${C_RESET}\n" "$*"; }

# Info message
info() { printf "${C_INFO}ℹ️  %s${C_RESET}\n" "$*"; }

# Detail (dim)
detail() { printf "${C_DETAIL}   %s${C_RESET}\n" "$*"; }

# Horizontal rule
hr() { printf "${C_GRAY}%s${C_RESET}\n" "$(printf '─%.0s' $(seq 1 78))"; }

# Rainbow gradient text (truecolor)
# rainbow "text"
rainbow() {
  local text="$*"
  local len=${#text}
  local i=0
  local r g b
  for ((i=0; i<len; i++)); do
    local ratio=$(awk -v i="$i" -v l="$len" 'BEGIN {print i/l}')
    r=$(awk -v r="$ratio" 'BEGIN {printf "%.0f", 168 + (34-168)*r}')
    g=$(awk -v r="$ratio" 'BEGIN {printf "%.0f", 85 + (197-85)*r}')
    b=$(awk -v r="$ratio" 'BEGIN {printf "%.0f", 247 + (94-247)*r}')
    printf '\033[38;2;%d;%d;%dm%s\033[0m' "$r" "$g" "$b" "${text:i:1}"
  done
  printf "\n"
}

# Group wrapper — wraps a command in ::group:: / ::endgroup::
# run_in_group "Group Title" command [args...]
run_in_group() {
  local title="$1"
  shift
  echo "::group::$title"
  "$@"
  local rc=$?
  echo "::endgroup::"
  return $rc
}

# Write a markdown table to GITHUB_STEP_SUMMARY
# summary_table "Title" "Header1,Header2,..." "Row1Col1|Row1Col2|..." ...
summary_table() {
  local title="$1"
  local headers="$2"
  shift 2
  {
    echo "## $title"
    echo ""
    echo "| $headers |"
    echo "|${headers//[^,]/-}|" | sed 's/,/---|/g; s/^/|---/; s/$/|/'
    for row in "$@"; do
      echo "| $row |" | sed 's/|/ | /g; s/||/|/g'
    done
    echo ""
  } >> "$GITHUB_STEP_SUMMARY"
}

# Write a GitHub alert to summary
# summary_alert "NOTE|TIP|IMPORTANT|WARNING|CAUTION" "Message"
summary_alert() {
  local type="$1"
  local msg="$2"
  echo "> [!$type]" >> "$GITHUB_STEP_SUMMARY"
  echo "> $msg" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
}

# Write a badge (shields.io) to summary
# summary_badge "label" "message" "color" [style]
summary_badge() {
  local label="$1"
  local message="$2"
  local color="$3"
  local style="${4:-flat}"
  echo "![${label}](https://img.shields.io/badge/${label// /%20}-${message// /%20}-${color}?style=${style})" >> "$GITHUB_STEP_SUMMARY"
}

# Write a mermaid diagram to summary
# summary_mermaid "diagram content"
summary_mermaid() {
  echo '```mermaid' >> "$GITHUB_STEP_SUMMARY"
  echo "$1" >> "$GITHUB_STEP_SUMMARY"
  echo '```' >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
}

# Start a collapsible <details> block in summary
# summary_details "Summary text" "Content"
summary_details() {
  local summary="$1"
  local content="$2"
  echo "<details>" >> "$GITHUB_STEP_SUMMARY"
  echo "<summary>$summary</summary>" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "$content" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
  echo "</details>" >> "$GITHUB_STEP_SUMMARY"
  echo "" >> "$GITHUB_STEP_SUMMARY"
}

# ─── Color activation for common tools ───
# Call this at the top of a job to enable colors for tools that respect env vars
activate_colors() {
  export FORCE_COLOR=3
  export CLICOLOR_FORCE=1
  export TERM=xterm-256color
  export CI=true
}

# Run a command with color flags where supported
# run_color cmd [args...]
run_color() {
  local cmd="$1"
  shift
  case "$cmd" in
    git)       git -c color.ui=always "$@" ;;
    grep)      grep --color=always "$@" ;;
    rg)        rg --color=always "$@" ;;
    fd)        fd --color=always "$@" ;;
    ls)        ls --color=always "$@" ;;
    pytest)    pytest --color=yes "$@" ;;
    cargo)     cargo --color=always "$@" ;;
    npm|yarn|pnpm|npx) FORCE_COLOR=3 "$cmd" "$@" ;;
    *)         "$cmd" "$@" ;;
  esac
}

# ─── Job theme color (call once per job to set a theme) ───
# job_theme "color"  (success|error|warn|info|highlight)
# Sets JOB_THEME_COLOR env var for use in summaries
job_theme() {
  local color="${1:-info}"
  local c_var="C_${color^^}"
  export JOB_THEME_COLOR="${!c_var:-$C_INFO}"
  export JOB_THEME_NAME="$color"
}

# ─── Main guard ───
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  echo "This script should be sourced: source .github/scripts/ci-visual.sh"
  exit 1
fi

# Auto-activate colors when sourced
activate_colors
