severity: major

## F1 --json 清洗後兩個不同規則名撞成同一個鍵,其中一個的漏過次數整筆消失
severity: major
blocking: yes
引句:「_esc_clean(k, 80): v for k, v in missing.items()」

這行把 `missing` 字典重建成 `{_esc_clean(k, 80): v ...}`。字典推導式碰到重複鍵只會留下最後一個,
不是合併計數。只要兩個原始 `rule` 欄位清洗後(去控制字元、或截到 80 字)變成同一個字串,
較早的那一筆連 `n`(漏過次數)帶 `desc` 整包被蓋掉,不是「計數算錯」而是「這條規則的存在本身從
JSON 輸出裡消失」。這正好打在這份修正想堵的洞上:`rule` 欄位是使用者可控的逃逸帳內容,攻擊者/
不小心的填表人只要讓一個規則名跟另一個規則名「清洗後撞同一個字串」,就能讓自己那筆漏網從
`--json` 消費端(下游腳本、閉環判斷「這條規則還沒寫」的自動化)眼中消失,而文字模式
(`--list` 的那個 for 迴圈,直接印 `_esc_clean(rid, 80)` 而不是重建 dict)不會有這個問題,兩種
輸出模式在「同一批資料」下會給出不一致的條數,更嚴重的是 JSON 這邊少算。

重現步驟(repo 唯讀,全部在 `/private/tmp/.../exp2-通才/collision` 下跑,套用凍結 patch 後的
`scripts/lumos`):
```
mkdir -p exp2-通才/collision/repo/docs
git -C exp2-通才/collision/repo init -q
python3 - <<'EOF'
import json
rows = [
    {"token":"E1","stage":"CI","kind":"escape","rule":"R\x7fA","desc":"d1"},
    {"token":"E2","stage":"CI","kind":"escape","rule":"R A","desc":"d2"},
]
with open("exp2-通才/collision/repo/docs/.escape-log.jsonl","w",encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")
EOF
python3 <打完 patch 的 scripts/lumos> rule-gap --repo exp2-通才/collision/repo --json
```
實跑輸出(已驗證,在套用凍結 patch 的 worktree 上跑):
```
{"missing": {"R A": {"n": 1, "desc": "d2"}}, "covered": [], "unlabeled": 0}
```
兩筆逃逸(E1 的 `R\x7fA`、E2 的 `R A`)清洗後都是 `"R A"`,JSON 只剩一筆 `n: 1`,E1 那筆(`desc: "d1"`)
完全看不見——總漏過次數該是 2,JSON 讀出來卻是 1。同一份資料跑文字模式(`rule-gap --repo ... `
不帶 `--json`)兩筆都在:
```
  R A(漏過 1 次)—— d1
  R A(漏過 1 次)—— d2
```
可見不是「清洗合理、本來就該視為同一條規則」的設計意圖,是 `--json` 這條路徑特有的資料遺失。

隨附的新測試(`r3 規則缺口 --json 也不讓 DEL/C1 控制碼穿透`)只餵了一筆規則名,只斷言沒有控制碼穿透
與 JSON 能解析,沒有覆蓋「兩筆撞鍵」的情況,所以沒抓到這個洞。

## F2 covered 用生成式塞進 sorted() 而非先去重,清洗後撞名會在清單裡重複印出同一個字串
severity: minor
blocking: no
引句:「"covered": sorted(_esc_clean(k, 80) for k in set(counts) & have)」

`covered` 本身只是規則名清單(不像 `missing` 帶 `n`/`desc`),所以撞鍵不會丟資料,但兩個原始
規則名清洗後變成同一個字串時,這個字串會在 `covered` 陣列裡出現兩次(因為是先各自清洗再丟進
`sorted()`,不是先去重再清洗)。下游如果拿 `covered` 的長度當「已覆蓋幾條規則」的計數,會比
實際多算。不影響本次修正要堵的資安洞(控制碼穿透),按嚴重度不到擋路線,附記讓作者知道。

已看,無:
- `missing = {k: v for k, v in counts.items() if k not in have}` 這行本身(清洗前的第一次建字典)
  用的是原始 `rid`,不會因為清洗撞鍵,問題只出在後面重建 JSON 輸出的那一步。
- `_esc_clean` 的清洗規則(control char → 空白、超過 `limit` 截斷加「…」)跟既有文字模式
  (`_esc_clean(rid, 80)` 印在 for 迴圈裡)用的是同一支函式、同樣的 `limit=80`,兩邊清洗行為
  一致,不是這次修正才引入的新規則。
- `unlabeled` 計數不受這次改動影響,沒有清洗、沒有鍵的問題。
- 對照 `python3 scripts/test_lumos.py -k escape_review_r3` 與 `-k rule_gap` 兩個關鍵字都在
  套用 patch 的 worktree 上全綠(9 passed / 6 passed),且把套用 patch 前的 `scripts/lumos`
  換上同一份新測試會在「DEL/C1 穿透」那一條精準翻紅(`r3 規則缺口 --json 也不讓 DEL/C1
  控制碼穿透`),其餘八條照樣綠——測試確實對症,不是空湊。
