#!/usr/bin/env bash
# install.sh — 公開精簡版 機器層安裝器
#
# ★只做兩件事★:①全域 lumos 指令 ②實體複製 skill 到 ~/.claude/skills/
# ★明確不做★:不 scaffold 圖譜、不注入/更新任何 CLAUDE.md、不 vendor 工具進專案、
#            不設 core.hooksPath、不裝任何 Claude hook。
#
# 包的位置 = 本腳本所在目錄(隨包走,不需要參數)。
set -eu

# 解析 $0 的 symlink 鏈(macOS 無 `readlink -f`,手捲迴圈逐層解;POSIX `readlink`
# 每次只吐一層目標,相對路徑目標要接回所在目錄再繼續判是否還是 symlink)
SOURCE="$0"
while [ -L "$SOURCE" ]; do
  DIR="$(cd "$(dirname "$SOURCE")" && pwd)"
  LINK="$(readlink "$SOURCE")"
  case "$LINK" in
    /*) SOURCE="$LINK" ;;
    *)  SOURCE="${DIR}/${LINK}" ;;
  esac
done
PKG="$(cd "$(dirname "$SOURCE")" && pwd)"
BIN="${HOME}/.local/bin"
SKILLS="${HOME}/.claude/skills"
SRC_CLI="${PKG}/scripts/lumos"
SRC_SKILL="${PKG}/skills/lumos-project-notes"

[ -f "$SRC_CLI" ]   || { echo "ERROR: 找不到 ${SRC_CLI}" >&2; exit 2; }
[ -d "$SRC_SKILL" ] || { echo "ERROR: 找不到 ${SRC_SKILL}" >&2; exit 2; }

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

mkdir -p "$BIN" "$SKILLS"

# ① 全域指令 —— 碰撞語意沿用完整版 cmd_install 的階梯
DST_CLI="${BIN}/lumos"
if [ -e "$DST_CLI" ] || [ -L "$DST_CLI" ]; then
  if [ "$FORCE" -eq 0 ]; then
    echo "⚠ ${DST_CLI} 已存在,加 --force 覆寫" >&2
    exit 2
  fi
  rm -f "$DST_CLI"
fi
cp "$SRC_CLI" "$DST_CLI"
chmod +x "$DST_CLI"
echo "✓ 全域指令: ${DST_CLI}"

# ② skill —— ★實體複製,不是 symlink★(來源=交付包,但複製後與包解耦)
DST_SKILL="${SKILLS}/lumos-project-notes"
if [ -e "$DST_SKILL" ] || [ -L "$DST_SKILL" ]; then
  if [ "$FORCE" -eq 0 ]; then
    echo "⚠ ${DST_SKILL} 已存在,加 --force 覆寫(★會先備份★)" >&2
    exit 2
  fi
  BAK="${DST_SKILL}.bak.$(date +%Y%m%d%H%M%S)"
  mv "$DST_SKILL" "$BAK"
  echo "  已備份既有 skill → ${BAK}"
fi
cp -R "$SRC_SKILL" "$DST_SKILL"
echo "✓ skill: ${DST_SKILL}"

case ":${PATH}:" in
  *":${BIN}:"*) ;;
  *) echo "⚠ ${BIN} 不在 PATH,請自行加入 shell 設定檔" >&2 ;;
esac

echo
echo "裝好了。驗證: lumos --help"
echo "★這是凍結快照,不是發布通道——不會有更新。出問題請直接改 Python 原始碼。★"
