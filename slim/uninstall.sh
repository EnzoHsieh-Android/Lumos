#!/usr/bin/env bash
# uninstall.sh — 公開精簡版 一行卸載
#
# 用法(裝好之後,兩種都可):
#   ~/.lumos-slim/uninstall.sh
#   curl -fsSL https://raw.githubusercontent.com/citrus-android-developer/Citrus_Lumos/main/uninstall.sh | bash
#
# ★安全紀律是這支腳本的重點,比功能重要★——每一步都先判斷「這真的是我們裝的
# 東西嗎」,不確定就拒絕動、印清楚訊息,絕不用猜的去刪使用者的東西。
#
# ★絕不碰★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、
#          除了 lumos-project-notes 以外的任何 skill。
set -eu

BIN="${HOME}/.local/bin/lumos"
SKILL="${HOME}/.claude/skills/lumos-project-notes"
PKG="${HOME}/.lumos-slim"

FORCE=0
[ "${1:-}" = "--force" ] && FORCE=1

_sha256() {
  # macOS 常見 shasum、Linux 常見 sha256sum——挑存在的那支;兩者都沒有就中止
  # (內容比對是這支腳本安全性的核心,寧可拒絕動作也不要用未驗證的方式繼續)。
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    echo "ERROR: 找不到 sha256sum 或 shasum,無法安全比對內容——中止卸載。" >&2
    exit 2
  fi
}

echo "== 公開精簡版卸載 =="

# ① ~/.local/bin/lumos —— ★只在它確實是我們裝的那份時才移除★
#    判斷方式:與 ~/.lumos-slim/scripts/lumos 內容比對(sha256)。不符 = 可能是
#    使用者自己的東西 → 拒絕移除、印清楚訊息、rc=2(除非帶 --force)。
if [ -e "$BIN" ] || [ -L "$BIN" ]; then
  REF="${PKG}/scripts/lumos"
  if [ "$FORCE" -eq 1 ]; then
    rm -f "$BIN"
    echo "✓ 已移除(--force,跳過內容比對): ${BIN}"
  elif [ -f "$REF" ] && [ "$(_sha256 "$BIN")" = "$(_sha256 "$REF")" ]; then
    rm -f "$BIN"
    echo "✓ 已移除: ${BIN}"
  else
    echo "⚠ ${BIN} 內容與本包的 ${REF} 不一致(或 ${REF} 不存在)。" >&2
    echo "  這可能是你自己的東西,不是本包裝的那份 lumos——拒絕移除。" >&2
    echo "  確定要砍就加 --force 重跑:$0 --force" >&2
    exit 2
  fi
else
  echo "  (未安裝: ${BIN})"
fi

# ② skill 目錄 —— ★移除前先備份,不直接 rm -rf★(使用者可能在裡面塞過自己的檔)
if [ -d "$SKILL" ]; then
  BAK="${SKILL}.bak.$(date +%Y%m%d%H%M%S)"
  mv "$SKILL" "$BAK"
  echo "✓ 已備份並移除: ${SKILL} → ${BAK}"
else
  echo "  (未安裝: ${SKILL})"
fi

# ③ ~/.lumos-slim —— 可移除,但同樣先確認它長得像我們的包才刪
if [ -d "$PKG" ]; then
  if [ -f "$PKG/scripts/lumos" ] && [ -f "$PKG/install.sh" ]; then
    rm -rf "$PKG"
    echo "✓ 已移除: ${PKG}"
  else
    echo "⚠ ${PKG} 存在,但內容不像本包(缺 scripts/lumos 或 install.sh)——保留,不動。" >&2
  fi
else
  echo "  (未安裝: ${PKG})"
fi

echo
echo "卸載完成。"
echo "★未動★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、其他 skill。"
