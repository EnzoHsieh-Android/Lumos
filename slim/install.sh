#!/usr/bin/env bash
# install.sh — 公開精簡版 機器層安裝器
#
# ★做三件事★:①全域 lumos 指令 ②實體複製 skill 到 ~/.claude/skills/
#            ③(★2026-07-31 使用者裁定,推翻原「不注入/更新任何 CLAUDE.md」★)
#            在執行時所在目錄(專案根)的 CLAUDE.md 檔尾,用專屬 sentinel
#            append-only 附加一段「怎麼解析圖譜標籤」教學。
#
# ★裁定範圍刀(別搞混)★:當初禁的是「覆蓋」——完整版 init/update 會用範本
# 整段換掉 sentinel 之間既有紀律區塊(會把 Landmark 那類專案既有的紀律段沖掉)。
# 現在開的是「附加」——只在檔尾加一塊教學句,sentinel 以外一個位元組都不動;
# ②sentinel 刻意取名 `<!-- LUMOS-SLIM:START/END -->`,與完整版的 sentinel 不
# 同名,不會被完整版 init/update 誤判成自己的區塊而覆蓋掉;③內容只教「標籤怎麼
# 讀」,design-loop/code-loop 那套機械紀律依舊不給(見 [S4-b])。
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

# ③ 專案層 CLAUDE.md —— append-only 附加圖譜標籤教學(見檔頭裁定變更說明)。
# 目標 = 執行本腳本時的當前目錄(新人在自己的專案根底下跑安裝器/一行安裝)。
# ★只准附加、絕不覆蓋★:sentinel 以外的既有內容一個位元組都不動;冪等——
# 重跑只更新自己那塊 sentinel 之間的內容,不會疊出第二塊;CLAUDE.md 不存在時
# 直接建立(只含這一塊)。合併邏輯用 python3 stdlib 做,不手滾 sed/awk 拼字串
# (block 內含反引號/中文/Markdown 表格,sed 逐行替換極易漏 escape)。
CLAUDE_MD="$(pwd)/CLAUDE.md"
BLOCK_FILE="$(mktemp)"
trap 'rm -f "$BLOCK_FILE"' EXIT
cat > "$BLOCK_FILE" <<'LUMOS_SLIM_BLOCK_EOF'
<!-- LUMOS-SLIM:START -->
## Lumos 圖譜標籤速查(精簡版接手教學;append-only,2026-07-31 由 lumos-slim 安裝器附加)

> 本區塊由 `lumos-slim` 的 `install.sh` 自動維護(只附加、不覆蓋既有內容;重跑只更新這一塊,`uninstall.sh` 可乾淨移除)。內容摘自 `lumos-project-notes` skill 的 `reference.md`〈summary 欄位〉節,教你怎麼讀既有專案知識圖譜(`docs/{project}-knowledge/`)的 frontmatter 標籤。

### A. summary 欄位符號(Systems/Issues 筆記的結構化摘要)

| 符號 | 用途 |
|------|------|
| `FLOW:` | 核心流程 |
| `KEY:` | 關鍵概念/欄位 |
| `DEP:` | 依賴模組(wikilink) |
| `TEST:` | 測試狀態 |
| `VERIFY:` | 驗證紀錄連結 |
| `DECISION:` | 重大決策,帶 `(valid)`/`(superseded)` |
| `FLAG:` | 語意標記(TECHNICAL/DECISION/ORIGIN) |
| `AUTH:` | 認證方式 |

分隔符:`→` 流程方向、`｜` 分隔同類、`,` 分隔同欄細項。

看哪幾行:Systems 看 `FLOW`+`KEY`+`DEP`+`TEST`;Issues 看 `FLAG`+`DECISION`+`KEY`;Verification 看 `TEST`+`VERIFY`。

### B. `KEY:` 行的前綴(最要命,別搞混)

- `★INVARIANT★` — 業務合約,**改動＝breaking**,動前先看它綁的 `[test:]`
- `★DEBT★` — 已知偶然行為,**可以改、不算 breaking**
- `★IRREVERSIBLE★`/`★CHECKPOINT★` — 不可逆,動前找 `[rollback:]`

把兩者搞混的兩種後果:把 `★DEBT★` 當合約 → 不敢動該動的;把 `★INVARIANT★` 當普通說明 → 動了就壞。

### C. 合約鏈括號

- `[test:]` — 綁定測試
- `[audit:]` — 獨立審計
- `[rollback:]` — 回滾路徑

### D. frontmatter 欄位

- `valid_under:` — 這條結論在什麼前提下成立,前提沒了結論就不算數
- `plan_refs:`/`verified_by:` — 追回「為什麼這樣設計」
- `decisions:` — ADR,含被取代的舊決策

### E. 進場三步(這是精簡版:只有 24 支指令)

```
lumos search <關鍵字>      # 定位
lumos context <節點>       # 掃脈絡
lumos contracts <節點>     # 查硬合約
```

只有 24 支指令;`init`/`update`/`self-audit`/`signoff` 不存在,`doctor` 若建議跑它們請忽略。
<!-- LUMOS-SLIM:END -->
LUMOS_SLIM_BLOCK_EOF

python3 - "$CLAUDE_MD" "$BLOCK_FILE" <<'LUMOS_SLIM_PY_EOF'
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])
block = Path(sys.argv[2]).read_text(encoding="utf-8")
START = "<!-- LUMOS-SLIM:START -->"
END = "<!-- LUMOS-SLIM:END -->"

original = target.read_text(encoding="utf-8") if target.exists() else ""
pattern = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.DOTALL)
matches = list(pattern.finditer(original))

if len(matches) > 1:
    print(f"ERROR: {target} 內有多個 LUMOS-SLIM sentinel 區塊,拒絕自動合併"
          "——請手動清理後重跑。", file=sys.stderr)
    sys.exit(2)

if matches:
    m = matches[0]
    new = original[:m.start()] + block + original[m.end():]
elif original == "":
    new = block
else:
    # ★固定分隔符★:非空既有內容一律只加一個 "\n" 再接區塊,不對既有內容做任何
    # trim/正規化(不管它原本結尾是 0 個、1 個還是多個換行,都不動它半個位元組)。
    # uninstall.sh 的移除邏輯與此對稱:只吃掉這一個我們自己加的 "\n",其餘還原。
    new = original + "\n" + block

target.write_text(new, encoding="utf-8")
LUMOS_SLIM_PY_EOF
echo "✓ CLAUDE.md 圖譜標籤教學已附加/更新: ${CLAUDE_MD}"

case ":${PATH}:" in
  *":${BIN}:"*) ;;
  *) echo "⚠ ${BIN} 不在 PATH,請自行加入 shell 設定檔" >&2 ;;
esac

echo
echo "裝好了。驗證: lumos --help"
echo "★這是凍結快照,不是發布通道——不會有更新。出問題請直接改 Python 原始碼。★"
