#!/usr/bin/env bash
# PreToolUse(Bash) hook. Runs on every Bash tool call; acts only when the command
# contains a `git commit`. Resolves the repository the commit actually targets
# (`git -C <repo> commit`, `cd <repo> && git commit`, plain `git commit`) and
# blocks (exit 2) when a .env-type file is staged there. Fails closed (exit 2)
# when the target repository cannot be determined safely.
# Wired in .claude/settings.json. Guarantees and limits: .claude/rules/common.md.
set -uo pipefail

deny() {
  printf 'Blocked: %s\n' "$1" >&2
  exit 2
}

# Heuristic used only to decide whether an unparsable payload must fail closed.
raw_looks_like_commit() {
  case "$1" in
    *git*commit*) return 0 ;;
    *) return 1 ;;
  esac
}

# Decode a JSON string body (the escapes JSON can produce). Fails on \u and on
# any escape it does not understand, so unknown input is never silently trusted.
json_unescape() {
  local s=$1 out='' c
  while [ -n "$s" ]; do
    c=${s%"${s#?}"}
    s=${s#?}
    if [ "$c" = '\' ]; then
      [ -n "$s" ] || return 1
      c=${s%"${s#?}"}
      s=${s#?}
      case "$c" in
        n) out="$out"$'\n' ;;
        t) out="$out"$'\t' ;;
        r) out="$out"$'\r' ;;
        b) out="$out"$'\b' ;;
        f) out="$out"$'\f' ;;
        '"') out="$out"'"' ;;
        '\') out="$out"'\' ;;
        '/') out="$out"'/' ;;
        *) return 1 ;;
      esac
    else
      out="$out$c"
    fi
  done
  printf '%s' "$out"
}

trim() {
  local s=$1
  s="${s#"${s%%[![:space:]]*}"}"
  s="${s%"${s##*[![:space:]]}"}"
  printf '%s' "$s"
}

# Resolve $2 (possibly relative) against directory $1. Prints the absolute path.
resolve_dir() {
  local base=$1 target=$2 candidate
  case "$target" in
    /*) candidate=$target ;;
    *) candidate="$base/$target" ;;
  esac
  [ -d "$candidate" ] || return 1
  (CDPATH= cd -- "$candidate" >/dev/null 2>&1 && pwd -P) || return 1
}

# A path argument we can reason about statically: no expansion, no globbing,
# no quoting artifacts left over from naive word splitting.
path_is_static() {
  case "$1" in
    ''|-|*'$'*|*'`'*|*'*'*|*'?'*|*'['*|*'~'*|*'"'*|*"'"*) return 1 ;;
    *) return 0 ;;
  esac
}

# Block when a .env-type file is staged in the repository at $1.
# $2 = 1 when the commit also auto-stages tracked modifications (-a/--all).
check_repo() {
  local dir=$1 auto_stage=$2 files
  git -C "$dir" rev-parse --git-dir >/dev/null 2>&1 \
    || deny "'$dir' is not a Git repository; cannot verify the commit target."
  files=$(git -C "$dir" diff --cached --name-only 2>/dev/null) \
    || deny "cannot read the staged index of '$dir'."
  if [ "$auto_stage" = 1 ]; then
    files="$files
$(git -C "$dir" diff --name-only 2>/dev/null || true)"
  fi
  if printf '%s\n' "$files" | grep -qE '(^|/)\.env($|\.)'; then
    deny "a .env-type file is staged in '$dir'. Commit is not allowed."
  fi
}

input=$(cat 2>/dev/null || true)

# Extract tool_input.command from the hook payload.
flat=$(printf '%s' "$input" | tr '\n\r' '  ')
field=$(printf '%s' "$flat" | grep -oE '"command"[[:space:]]*:[[:space:]]*"([^"\\]|\\.)*"' | head -n 1)
if [ -z "$field" ]; then
  raw_looks_like_commit "$input" \
    && deny "cannot read the command from the hook payload; refusing a possible commit."
  exit 0
fi

body=${field#*:}
body=$(trim "$body")
body=${body#\"}
body=${body%\"}

if ! command_line=$(json_unescape "$body"); then
  raw_looks_like_commit "$input" \
    && deny "cannot decode the command from the hook payload; refusing a possible commit."
  exit 0
fi

case "$command_line" in
  *commit*) ;;
  *) exit 0 ;;
esac

base_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
cwd=$base_dir
cwd_known=1
[ -d "$cwd" ] || cwd_known=0

# Split the command line into segments on &&, ||, |, ; and newlines.
segments=${command_line//&&/$'\001'}
segments=${segments//||/$'\001'}
segments=${segments//|/$'\001'}
segments=${segments//;/$'\001'}
segments=${segments//$'\n'/$'\001'}
segments=${segments//$'\001'/$'\n'}

while IFS= read -r segment; do
  segment=$(trim "$segment")
  # Strip subshell / group wrappers: ( cd repo && git commit )
  while :; do
    case "$segment" in
      '('*|'{'*) segment=$(trim "${segment#?}") ;;
      *')'|*'}') segment=$(trim "${segment%?}") ;;
      *) break ;;
    esac
  done
  [ -n "$segment" ] || continue

  read -r -a tokens <<<"$segment"
  [ "${#tokens[@]}" -gt 0 ] || continue

  # Skip (but remember) leading environment assignments.
  idx=0
  has_env_prefix=0
  while [ "$idx" -lt "${#tokens[@]}" ]; do
    case "${tokens[$idx]}" in
      [A-Za-z_]*=*) has_env_prefix=1; idx=$((idx + 1)) ;;
      *) break ;;
    esac
  done
  [ "$idx" -lt "${#tokens[@]}" ] || continue

  case "${tokens[$idx]}" in
    cd)
      target=${tokens[$((idx + 1))]:-}
      if [ -z "$target" ]; then
        # bare `cd` goes to $HOME
        if [ -n "${HOME:-}" ] && [ -d "$HOME" ]; then
          cwd=$HOME
          cwd_known=1
        else
          cwd_known=0
        fi
      elif ! path_is_static "$target"; then
        cwd_known=0
      elif [ "$cwd_known" != 1 ]; then
        : # already unknown; a relative cd cannot make it known again
        case "$target" in
          /*)
            if resolved=$(resolve_dir / "$target"); then
              cwd=$resolved
              cwd_known=1
            fi
            ;;
        esac
      elif resolved=$(resolve_dir "$cwd" "$target"); then
        cwd=$resolved
      else
        cwd_known=0
      fi
      ;;
    git)
      git_dir=$cwd
      git_dir_known=$cwd_known
      subcommand=''
      unsafe_prefix=0
      i=$((idx + 1))
      while [ "$i" -lt "${#tokens[@]}" ]; do
        token=${tokens[$i]}
        path_is_static "$token" || unsafe_prefix=1
        case "$token" in
          -C)
            i=$((i + 1))
            value=${tokens[$i]:-}
            if ! path_is_static "$value"; then
              git_dir_known=0
              unsafe_prefix=1
            elif [ "$git_dir_known" = 1 ] && resolved=$(resolve_dir "$git_dir" "$value"); then
              git_dir=$resolved
            elif [ "$git_dir_known" != 1 ] && case "$value" in /*) true ;; *) false ;; esac \
              && resolved=$(resolve_dir / "$value"); then
              git_dir=$resolved
              git_dir_known=1
            else
              git_dir_known=0
            fi
            ;;
          -C*)
            value=${token#-C}
            if ! path_is_static "$value"; then
              git_dir_known=0
              unsafe_prefix=1
            elif [ "$git_dir_known" = 1 ] && resolved=$(resolve_dir "$git_dir" "$value"); then
              git_dir=$resolved
            else
              git_dir_known=0
            fi
            ;;
          --git-dir|--work-tree|--namespace|--git-dir=*|--work-tree=*|--namespace=*)
            # These relocate the index/worktree; do not guess.
            git_dir_known=0
            ;;
          -c|--exec-path)
            i=$((i + 1))
            path_is_static "${tokens[$i]:-}" || unsafe_prefix=1
            ;;
          -*)
            ;;
          *)
            subcommand=$token
            break
            ;;
        esac
        i=$((i + 1))
      done

      if [ "$subcommand" != commit ]; then
        # A non-static token before the subcommand (expansion, quoting, glob)
        # means the parse is untrustworthy: refuse anything that mentions commit.
        if [ "$unsafe_prefix" = 1 ]; then
          case "$segment" in
            *commit*) deny "cannot parse '$segment' well enough to locate the commit target; refusing." ;;
          esac
        fi
        continue
      fi

      if [ "$has_env_prefix" = 1 ]; then
        deny "the commit command sets environment variables that can relocate the index; refusing."
      fi
      if [ "$git_dir_known" != 1 ]; then
        deny "cannot determine the repository targeted by '$segment'; refusing the commit."
      fi

      auto_stage=0
      j=$((i + 1))
      while [ "$j" -lt "${#tokens[@]}" ]; do
        case "${tokens[$j]}" in
          --all|-a) auto_stage=1 ;;
          -[a-zA-Z]*)
            case "${tokens[$j]}" in
              --*) ;;
              *a*) auto_stage=1 ;;
            esac
            ;;
        esac
        j=$((j + 1))
      done

      check_repo "$git_dir" "$auto_stage"
      ;;
  esac
done <<<"$segments"

exit 0
