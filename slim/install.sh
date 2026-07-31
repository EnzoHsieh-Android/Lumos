#!/usr/bin/env bash
# install.sh — 公開精簡版 機器層安裝器
#
# ★做三件事★:①全域 lumos 指令(附帶寫一份身分證 manifest,見下方①b,讓
#            uninstall.sh 有穩定比對基準)②實體複製 skill 到 ~/.claude/skills/
#            ③在執行時所在目錄(專案根)的 CLAUDE.md 裡放一塊策展過的精簡版
#            紀律區塊(sentinel `<!-- LUMOS-SLIM:START/END -->`)。
#
# ★裁定演進(spec [S3],三次)★:原裁定=絕不碰專案 CLAUDE.md;第二次=只准
# append-only 附加、sentinel 以外一個位元組都不動、完整版 `LUMOS:GRAPH-
# DISCIPLINE` 區塊(若有)原封不動留著;現在(2026-07-31 第三次,本次改動)=
# 若專案已有完整版區塊,**整段移除**它,換成這塊精簡版區塊——但移除前先把
# 完整版原文位元組級備份(base64 編碼藏進精簡版區塊自己的 HTML 註解裡,見
# `claude-block.md` 的 `FULL-BACKUP` 標記),`uninstall.sh` 能用它精確還原。
# 理由:完整版那段本身自稱「優先級最高/第一個工具呼叫必須是 lumos」,兩套
# 規則並存時接手者的 Claude 會先讀到它、照著撲空(它引用的 design-loop/
# code-loop/pitfalls 等 13 處指令本包都沒交付)。精簡版區塊已策展吸收完整版
# 裡仍然有效的部分(合約鏈/可逆性標記/regen 重生標記/frontmatter 欄位等),
# 只拿掉依賴已移除指令才有意義的段落。
# ★已知風險(使用者已知並接受)★:完整版區塊自稱「自動注入/更新」——若專案
# 還有其他人在用完整版、他跑更新指令會把完整版裝回來,兩邊來回覆蓋。
#
# 插入位置:①有完整版區塊 → 原位置整段換掉(不是搬到檔尾——那裡才顯眼)
#          ②沒有 → 插在檔首「# 標題」之後,沒有標題就插最前面
#          ③CLAUDE.md 不存在 → 建立,內容就是這個區塊
# ★冪等★:重跑只更新自己那塊(沿用既有備份標記,不重新編碼、不二次包裹)。
# ★仍明確不做★:不 scaffold 圖譜、不 vendor 工具進專案、不設 core.hooksPath、
#              不裝任何 Claude hook。
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

# ①b 身分證 manifest —— 讓 uninstall.sh 有穩定比對基準,★不依賴 ~/.lumos-slim
# 事後還存不存在★(README〈~/.lumos-slim 是什麼〉明講使用者可以刪掉它;而且
# 兩行版安裝——`git clone ... ~/.lumos-slim && ~/.lumos-slim/install.sh`——
# 之外,使用者也可能把包 clone 到別的路徑直接跑 install.sh,~/.lumos-slim
# 壓根不會存在)。放在 ~/.local/share/(不是使用者的專案目錄),不會污染任何
# 專案的 git status。內容只需回答一件事:「~/.local/bin/lumos 是不是我們裝
# 的那份」——記安裝當下對 DST_CLI 算出的 sha256 就夠。冪等:每次成功安裝都
# 覆寫,沿用最新那份。
MANIFEST_DIR="${HOME}/.local/share/lumos-slim"
MANIFEST="${MANIFEST_DIR}/manifest.json"
mkdir -p "$MANIFEST_DIR"
if command -v sha256sum >/dev/null 2>&1; then
  BIN_SHA="$(sha256sum "$DST_CLI" | awk '{print $1}')"
elif command -v shasum >/dev/null 2>&1; then
  BIN_SHA="$(shasum -a 256 "$DST_CLI" | awk '{print $1}')"
else
  BIN_SHA=""
fi
python3 - "$MANIFEST" "$BIN_SHA" "$PKG" <<'LUMOS_SLIM_MANIFEST_PY_EOF'
import json
import sys
import time
from pathlib import Path

manifest_path, bin_sha, pkg_dir = sys.argv[1], sys.argv[2], sys.argv[3]
data = {
    "format_version": 1,
    "bin_sha256": bin_sha,
    "installed_at_epoch": int(time.time()),
    "pkg_dir": pkg_dir,
}
Path(manifest_path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
LUMOS_SLIM_MANIFEST_PY_EOF
echo "✓ 身分證 manifest: ${MANIFEST}"

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

# ③ 專案層 CLAUDE.md —— 用策展後的精簡版紀律區塊取代完整版(若有)/附加(見
# 檔頭裁定演進說明)。目標 = 執行本腳本時的當前目錄(新人在自己的專案根底下
# 跑安裝器/一行安裝)。範本 = 本包隨附的 claude-block.md(靜態檔,不在腳本裡
# 手刻 heredoc)。合併邏輯用 python3 stdlib 做,不手滾 sed/awk 拼字串(block
# 內含反引號/中文/Markdown 表格,sed 逐行替換極易漏 escape)。
CLAUDE_MD="$(pwd)/CLAUDE.md"
BLOCK_TEMPLATE="${PKG}/claude-block.md"
[ -f "$BLOCK_TEMPLATE" ] || { echo "ERROR: 找不到 ${BLOCK_TEMPLATE}" >&2; exit 2; }

python3 - "$CLAUDE_MD" "$BLOCK_TEMPLATE" <<'LUMOS_SLIM_PY_EOF'
import base64
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])
template = Path(sys.argv[2]).read_text(encoding="utf-8")

SLIM_START = "<!-- LUMOS-SLIM:START -->"
SLIM_END = "<!-- LUMOS-SLIM:END -->"
# ★完整版 START 有版本號後綴(如 "...START v1.0 — 自動注入...-->"),不是固定
# 字面值★——只匹配前綴,與 scripts/lumos 的 _CLAUDE_START_PREFIX 同款做法。
FULL_START_PREFIX = "<!-- LUMOS:GRAPH-DISCIPLINE:START"
FULL_END = "<!-- LUMOS:GRAPH-DISCIPLINE:END -->"
BACKUP_NONE = "<!-- LUMOS-SLIM:FULL-BACKUP:NONE -->"
BACKUP_RE = re.compile(r"<!-- LUMOS-SLIM:FULL-BACKUP:(NONE|BASE64:[A-Za-z0-9+/=]*) -->")

slim_pat = re.compile(re.escape(SLIM_START) + r".*?" + re.escape(SLIM_END) + r"\n?", re.DOTALL)
full_pat = re.compile(re.escape(FULL_START_PREFIX) + r".*?" + re.escape(FULL_END) + r"\n?", re.DOTALL)

original = target.read_text(encoding="utf-8") if target.exists() else ""
slim_matches = list(slim_pat.finditer(original))
full_matches = list(full_pat.finditer(original))

if len(slim_matches) > 1:
    print(f"ERROR: {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動處理"
          "——請手動清理後重跑。", file=sys.stderr)
    sys.exit(2)
if len(full_matches) > 1:
    print(f"ERROR: {target} 內有多個 LUMOS:GRAPH-DISCIPLINE sentinel 區塊,"
          "拒絕自動處理——請手動清理後重跑。", file=sys.stderr)
    sys.exit(2)
if slim_matches and full_matches:
    print(f"ERROR: {target} 同時有 LUMOS-SLIM 與 LUMOS:GRAPH-DISCIPLINE 兩種"
          "sentinel 區塊並存,狀態不明確,拒絕自動處理——請手動清理後重跑。",
          file=sys.stderr)
    sys.exit(2)

if full_matches:
    # 情境①:有完整版區塊 —— 先把原文位元組級編碼進備份標記,再原位置整段
    # 換成精簡版區塊(不是搬到檔尾)。
    m = full_matches[0]
    full_text = m.group(0)
    encoded = base64.b64encode(full_text.encode("utf-8")).decode("ascii")
    backup_marker = f"<!-- LUMOS-SLIM:FULL-BACKUP:BASE64:{encoded} -->"
    start, end = m.start(), m.end()
elif slim_matches:
    # 情境②:冪等重跑 —— 精簡版區塊已存在,沿用它既有的備份標記(★不重新
    # 編碼、不因這次沒看到完整版區塊就誤判成「原本沒有」而把備份洗掉★)。
    m = slim_matches[0]
    bm = BACKUP_RE.search(m.group(0))
    backup_marker = bm.group(0) if bm else BACKUP_NONE
    start, end = m.start(), m.end()
else:
    # 情境③:兩種都沒有 —— 全新安裝,無備份;插入點是「檔首 # 標題之後」,
    # 沒有標題就插最前面,原檔不存在/空檔就直接整份是這個區塊。
    backup_marker = BACKUP_NONE
    if original.startswith("# "):
        nl = original.find("\n")
        pos = nl + 1 if nl != -1 else len(original)
    else:
        pos = 0
    start = end = pos

block_text = template.replace(BACKUP_NONE, backup_marker)
new = original[:start] + block_text + original[end:]
target.write_text(new, encoding="utf-8")
LUMOS_SLIM_PY_EOF
echo "✓ CLAUDE.md 精簡版紀律區塊已安裝/更新: ${CLAUDE_MD}"

case ":${PATH}:" in
  *":${BIN}:"*) ;;
  *) echo "⚠ ${BIN} 不在 PATH,請自行加入 shell 設定檔" >&2 ;;
esac

echo
echo "裝好了。驗證: lumos --help"
echo "★這是凍結快照,不是發布通道——不會有更新。出問題請直接改 Python 原始碼。★"
