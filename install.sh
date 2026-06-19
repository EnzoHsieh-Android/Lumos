#!/usr/bin/env bash
# install.sh — 把 lumos skills 裝成 user-scope(symlink 進 ~/.claude/skills/)
#
# 用法(在本 repo root 跑):
#   ./install.sh              # symlink ~/.claude/skills/lumos-* → 本 repo/skills/lumos-*
#   ./install.sh --copy       # 改用複製(不想 symlink 時;但失去「git pull 即更新」)
#   ./install.sh --uninstall  # 移除 symlink
#
# 為什麼 symlink:本 repo 是 skills 的「唯一源」。symlink 後,日後 `git pull` 本 repo
# = ~/.claude/skills 立刻拿到最新,不必重裝。多專案共用同一份 user-scope skill,
# 規則不再散落、不在各 project 留副本。

set -u
MODE="symlink"; UNINSTALL=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --copy) MODE="copy"; shift ;;
    --symlink) MODE="symlink"; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,/^$/p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

if [[ -t 1 ]]; then G=$'\033[32m'; Y=$'\033[33m'; D=$'\033[2m'; R=$'\033[0m'; else G=''; Y=''; D=''; R=''; fi
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$HOME/.claude/skills"
SKILLS=(lumos-project-notes lumos-core-knowledge lumos-design-loop)

mkdir -p "$DEST"
for s in "${SKILLS[@]}"; do
  src="$REPO/skills/$s"; dst="$DEST/$s"
  if [[ "$UNINSTALL" == 1 ]]; then
    if [[ -L "$dst" || -e "$dst" ]]; then rm -rf "$dst"; echo "  ${Y}removed${R} ~/.claude/skills/$s"; fi
    continue
  fi
  [[ -d "$src" ]] || { echo "  ${Y}skip${R} 來源缺 skills/$s"; continue; }
  rm -rf "$dst"
  if [[ "$MODE" == "symlink" ]]; then
    ln -s "$src" "$dst"; echo "  ${G}✓${R} symlink ~/.claude/skills/$s → $src"
  else
    cp -R "$src" "$dst"; echo "  ${G}✓${R} copied ~/.claude/skills/$s"
  fi
done

[[ "$UNINSTALL" == 1 ]] && { echo "已移除 user-scope lumos skills。"; exit 0; }
echo
echo "${G}完成${R} — lumos skills 已裝為 user-scope(所有專案可見)。"
echo "  更新:在本 repo \`git pull\`$([[ "$MODE" == copy ]] && echo " 後再跑一次 ./install.sh")。"
