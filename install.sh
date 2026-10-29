#!/usr/bin/env bash
# Reelsmith installer for macOS, Linux and Git Bash on Windows.
#
#   ./install.sh                      install deps + skills for every agent found on this machine
#   ./install.sh --agents=claude,cursor
#   ./install.sh --agents=all --project   install into the current project folder instead of your home
#   curl -fsSL https://raw.githubusercontent.com/EmirhanYAZICI/reelsmith/main/install.sh | bash
#
# Options:
#   --agents=auto|all|claude,codex,opencode,cursor,antigravity   (default: auto = agents found on this machine)
#   --project        install skills into ./.claude/skills, ./.cursor/skills ... of the current folder
#   --om=<path>      OpenMontage folder (default: $OPENMONTAGE_DIR or ~/Projects/OpenMontage)
#   --skills-only    copy the skills, skip dependencies
#   --no-hf-skills   skip "npx hyperframes skills"
#   --dry-run        show what would happen, change nothing
set -euo pipefail

REPO_URL="https://github.com/EmirhanYAZICI/reelsmith"
OM_URL="https://github.com/calesthio/OpenMontage"
SKILLS=(reelsmith whisper-tr)
ALL_AGENTS=(claude codex opencode cursor antigravity)

AGENTS="auto"; PROJECT=0; OM="${OPENMONTAGE_DIR:-$HOME/Projects/OpenMontage}"
DEPS=1; HF_SKILLS=1; DRY=0
for a in "$@"; do
  case "$a" in
    --agents=*) AGENTS="${a#*=}" ;;
    --project) PROJECT=1 ;;
    --om=*) OM="${a#*=}" ;;
    --skills-only) DEPS=0 ;;
    --no-hf-skills) HF_SKILLS=0 ;;
    --dry-run) DRY=1 ;;
    -h|--help) sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Unknown option: $a" >&2; exit 2 ;;
  esac
done

say()  { printf '\n== %s\n' "$*"; }
ok()   { printf '   ok    %s\n' "$*"; }
warn() { printf '   WARN  %s\n' "$*"; }
run()  { if [ "$DRY" = 1 ]; then printf '   would run: %s\n' "$*"; else "$@"; fi; }
has()  { command -v "$1" >/dev/null 2>&1; }

# Repo source: the folder this script is in, or a fresh clone when piped from curl.
SRC="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || pwd)"
if [ ! -f "$SRC/skills/reelsmith/SKILL.md" ]; then
  SRC="${REELSMITH_HOME:-$HOME/.reelsmith}"
  say "Getting Reelsmith into $SRC"
  if [ -d "$SRC/.git" ]; then run git -C "$SRC" pull --ff-only; else run git clone --depth 1 "$REPO_URL" "$SRC"; fi
fi

agent_dir() {  # $1 = agent, prints its skills folder
  if [ "$PROJECT" = 1 ]; then
    case "$1" in
      claude) echo "$PWD/.claude/skills" ;;   codex) echo "$PWD/.codex/skills" ;;
      opencode) echo "$PWD/.opencode/skills" ;; cursor) echo "$PWD/.cursor/skills" ;;
      antigravity) echo "$PWD/.agent/skills" ;;
    esac
  else
    case "$1" in
      claude) echo "$HOME/.claude/skills" ;;   codex) echo "$HOME/.codex/skills" ;;
      opencode) echo "$HOME/.config/opencode/skills" ;; cursor) echo "$HOME/.cursor/skills" ;;
      antigravity) echo "$HOME/.gemini/antigravity/skills" ;;
    esac
  fi
}
agent_found() {  # is this agent installed on the machine?
  case "$1" in
    claude) [ -d "$HOME/.claude" ] || has claude ;;
    codex) [ -d "$HOME/.codex" ] || has codex ;;
    opencode) [ -d "$HOME/.config/opencode" ] || has opencode ;;
    cursor) [ -d "$HOME/.cursor" ] || has cursor ;;
    antigravity) [ -d "$HOME/.gemini/antigravity" ] ;;
  esac
}

case "$AGENTS" in
  all) LIST=("${ALL_AGENTS[@]}") ;;
  auto) LIST=(); for ag in "${ALL_AGENTS[@]}"; do agent_found "$ag" && LIST+=("$ag"); done
        [ ${#LIST[@]} -eq 0 ] && LIST=(claude) ;;
  *) IFS=',' read -r -a LIST <<< "$AGENTS" ;;
esac

# 1. Dependencies
if [ "$DEPS" = 1 ]; then
  say "Checking tools"
  MISSING=0
  for t in git node npm ffmpeg ffprobe; do
    if has "$t"; then ok "$t"; else warn "$t not found"; MISSING=1; fi
  done
  if [ "$MISSING" = 1 ]; then
    echo "   Install the missing tools, then run this again:"
    echo "     Windows: winget install Git.Git OpenJS.NodeJS.LTS Gyan.FFmpeg"
    echo "     macOS:   brew install git node ffmpeg"
    echo "     Linux:   sudo apt install git nodejs npm ffmpeg"
    exit 1
  fi

  say "OpenMontage: $OM"
  if [ -f "$OM/AGENT_GUIDE.md" ]; then ok "found"; else run git clone --depth 1 "$OM_URL" "$OM"; fi

  if [ -x "$OM/.venv/Scripts/python.exe" ]; then VPY="$OM/.venv/Scripts/python.exe"
  elif [ -x "$OM/.venv/bin/python" ]; then VPY="$OM/.venv/bin/python"
  else
    # faster-whisper needs Python 3.10 - 3.12
    BASE=""
    if has py && py -3.12 --version >/dev/null 2>&1; then BASE="py -3.12"
    else for p in python3.12 python3.11 python3.10 python3 python; do has "$p" && { BASE="$p"; break; }; done; fi
    [ -z "$BASE" ] && { warn "Python 3.12 not found. Install it and run again."; exit 1; }
    say "Creating $OM/.venv with $BASE"
    run $BASE -m venv "$OM/.venv"
    if [ -e "$OM/.venv/Scripts/python.exe" ]; then VPY="$OM/.venv/Scripts/python.exe"; else VPY="$OM/.venv/bin/python"; fi
  fi
  say "Python packages ($VPY)"
  run "$VPY" -m pip install -q -r "$SRC/requirements.txt"

  say "HyperFrames"
  if has hyperframes; then ok "hyperframes $(hyperframes --version 2>/dev/null || true)"; else run npm i -g hyperframes; fi
  if [ "$HF_SKILLS" = 1 ]; then run npx -y hyperframes skills || warn "npx hyperframes skills failed; run it by hand later"; fi

  case "$OM" in "$HOME/Projects/OpenMontage") ;; *)
    warn "OpenMontage is not in ~/Projects/OpenMontage. Add this to your shell profile:"
    echo "     export OPENMONTAGE_DIR=\"$OM\"" ;;
  esac
fi

# 2. Skills
say "Installing skills for: ${LIST[*]}"
for ag in "${LIST[@]}"; do
  dir="$(agent_dir "$ag")"
  [ -z "$dir" ] && { warn "unknown agent: $ag"; continue; }
  run mkdir -p "$dir"
  for s in "${SKILLS[@]}"; do
    run rm -rf "${dir:?}/$s"
    run cp -R "$SRC/skills/$s" "$dir/$s"
  done
  ok "$ag  ->  $dir"
done

say "Done"
echo "   Open your agent and type: /reelsmith <folder>"
echo "   Tools without skill support read AGENTS.md in this repo."
