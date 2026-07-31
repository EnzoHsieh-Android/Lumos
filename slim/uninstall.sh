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
# ★唯一例外(★2026-07-31 使用者裁定第三次變更,與 install.sh 對稱★)★:執行
#          目錄下 CLAUDE.md 裡 `<!-- LUMOS-SLIM:START/END -->` sentinel 之間
#          的那一塊——找到就移除,並讀取區塊內建的 FULL-BACKUP 標記:若有
#          (代表 install.sh 當初取代掉了完整版 `LUMOS:GRAPH-DISCIPLINE` 區
#          塊),則位元組級還原該區塊原文回原位置;若無(當初本來就沒有完整版
#          區塊),單純移除精簡版區塊。sentinel(與還原的完整版區塊)以外的
#          內容一個位元組都不動;若移除後檔案變空,連同檔案本身一併刪除(還
#          原成「本來就沒這個檔案」的狀態)。
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

# ④ 執行目錄下 CLAUDE.md 的 LUMOS-SLIM sentinel 區塊 —— 與 install.sh 對稱
#    的移除/還原:找不到 sentinel 就當「本來就沒裝」放行(冪等);找到就讀出
#    區塊內建的 FULL-BACKUP 標記——有備份(BASE64)就位元組級還原完整版區塊
#    回原位置,沒有(NONE)就單純移除這塊;其餘內容原封不動;移除/還原完若
#    整個檔案變空,連檔案一起刪掉,回到「原本沒有這個檔案」的狀態。
CLAUDE_MD="$(pwd)/CLAUDE.md"
python3 - "$CLAUDE_MD" <<'LUMOS_SLIM_UNINST_PY_EOF'
import base64
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])
SLIM_START = "<!-- LUMOS-SLIM:START -->"
SLIM_END = "<!-- LUMOS-SLIM:END -->"
BACKUP_RE = re.compile(r"<!-- LUMOS-SLIM:FULL-BACKUP:(NONE|BASE64:[A-Za-z0-9+/=]*) -->")

if not target.exists():
    print(f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊 — 檔案不存在)")
    sys.exit(0)

current = target.read_text(encoding="utf-8")
pattern = re.compile(re.escape(SLIM_START) + r".*?" + re.escape(SLIM_END) + r"\n?", re.DOTALL)
matches = list(pattern.finditer(current))

if not matches:
    print(f"  (未安裝: {target} 的 LUMOS-SLIM 圖譜標籤區塊)")
    sys.exit(0)

if len(matches) > 1:
    print(f"⚠ {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動移除"
          "——請手動清理。", file=sys.stderr)
    sys.exit(2)

m = matches[0]
block = m.group(0)
bm = BACKUP_RE.search(block)

restore_text = ""
if bm and bm.group(1) != "NONE":
    encoded = bm.group(1)[len("BASE64:"):]
    try:
        restore_text = base64.b64decode(encoded).decode("utf-8")
    except Exception as e:
        print(f"ERROR: 完整版區塊備份還原失敗(base64/utf-8 解碼錯誤): {e}"
              "——拒絕破壞性移除,請手動處理。", file=sys.stderr)
        sys.exit(2)

new = current[:m.start()] + restore_text + current[m.end():]

if new == "":
    target.unlink()
    print(f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(內容變空,檔案本身一併移除)")
elif restore_text:
    target.write_text(new, encoding="utf-8")
    print(f"✓ 已還原: {target} 的完整版紀律區塊(位元組級還原自內建備份),LUMOS-SLIM 區塊已移除")
else:
    target.write_text(new, encoding="utf-8")
    print(f"✓ 已移除: {target} 的 LUMOS-SLIM 圖譜標籤區塊(其餘內容不變)")
LUMOS_SLIM_UNINST_PY_EOF

echo
echo "卸載完成。"
echo "★未動★:任何專案目錄、~/.claude/settings.json、~/.claude/hooks/、其他 skill;"
echo "        CLAUDE.md 除了上面那塊 LUMOS-SLIM sentinel 區塊(及它取代掉的完整版"
echo "        區塊,若有 — 已還原),其餘內容原封不動。"
