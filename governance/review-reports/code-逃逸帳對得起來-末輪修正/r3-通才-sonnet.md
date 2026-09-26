severity: major

## F1 讀帳時清洗把「截斷」也提前了,超過 200 字的不同規則名會被誤合併、且丟掉其中一筆的 desc
severity: major
blocking: yes
引句:「rid = _esc_clean(_raw.strip()) if isinstance(_raw, str) else ""」

問題:這次修正把清洗從「輸出時」搬到「讀帳時」,直接拿 `_esc_clean(_raw.strip())` 的結果當 `counts` 字典的 key。但 `_esc_clean` 預設 `limit=200`,超過就截斷成 200 字 + `…`。舊版是先用完整、未截斷的 `rid` 當 key 分開累計,只在「印出來」那一刻才各自截成 80 字顯示(截斷只影響畫面,不影響統計);新版把截斷提前到建 key 的階段,兩個**前 200 字相同、但後面不同**的規則名會被截成同一個字串,`counts.setdefault(rid, ...)` 因此把它們當成同一條規則,次數相加、且後寫入的那筆 desc 被靜默蓋掉/丟棄——這正好違反題目點名的兩個保證:「不同規則名不會因清洗而讓某筆消失」與「條數要一致」(這裡是規則名本身的身分消失,不是格式化文字重複)。

會不會真的發生:`--rule` 是使用者可填的自由文字,若不小心貼了較長的說明、或兩條規則名恰好共用長前綴(例如同一個模組路徑當前綴的兩條規則),就會撞在一起,且完全無感——不會報錯、不會警告,只是其中一條的計次悄悄併進另一條、desc 被吃掉。

重現步驟(已用當輪修正後的程式碼實跑,在 /private/tmp/…/exp3-通才/repo 這份唯讀複製上跑,repo 沒有被改動):
```
mkdir -p /tmp/rg2/docs && git -C /tmp/rg2 init -q
python3 - <<'EOF'
import json
r1 = "A"*200 + "-foo-rule"
r2 = "A"*200 + "-bar-rule"
rows = [
  {"ts":"2026-09-22T10:00:00+08:00","token":"E1","loop":"甲","stage":"CI","severity":"major","desc":"x1","rule":r1},
  {"ts":"2026-09-22T10:00:00+08:00","token":"E2","loop":"甲","stage":"CI","severity":"major","desc":"x2","rule":r2},
]
open("/tmp/rg2/docs/.escape-log.jsonl","w",encoding="utf-8").write(
    "\n".join(json.dumps(r) for r in rows) + "\n")
EOF
python3 scripts/lumos rule-gap --repo /tmp/rg2 --json
```
實際輸出(在 /private/tmp/…/exp3-通才/repo 下跑):
```
{"missing": {"AAAA...AAAA…": {"n": 2, "desc": "x1"}}, "covered": [], "unlabeled": 0}
```
兩筆語意上完全不同的規則(`...-foo-rule` 與 `...-bar-rule`)被合併成一筆 `n=2`,E2 的 desc `"x2"` 整個不見了。這不是原本要修的「同一規則名因控制字元不同而被誤判成兩筆」,而是新引進的「不同規則名因截斷而被誤判成一筆」。

建議方向(不要求本輪一定要照做,僅供參考):清洗(去控制字元)跟截斷(限長)分成兩步——建 `counts` 的 key 時只做前者(`_esc_clean` 傳一個不截斷或極大的 limit,如既有 `_esc_clean(nfc(...), 100000)` 那種用法),截斷留到印出來那一刻再做,這樣「撞名合併」只會發生在清洗後真的同名的情況,不會因為顯示長度限制而誤傷本來就不同的規則名。

已看,無:第二個 hunk(JSON 輸出不再對 `missing`/`covered` 的 key 重複呼叫 `_esc_clean(k, 80)`)本身沒問題——因為清洗已經在讀帳時對 `counts` 的 key 做過一次,`missing`/`covered` 都是從 `counts` 衍生,不需要再清洗一次,DEL/C1 不會透過這條路徑漏到終端(用既有測試 `-k rule_gap` 驗證仍過)。第三個 hunk(文字模式印 `rid` 不再另外呼叫 `_esc_clean(rid, 80)`)理由相同,也沒問題。`have` 集合(`_rules_declared_ids` / 規則索引)本身是開發者手寫的短識別字串,一般不會超過 200 字,所以「讀帳清洗會不會讓已寫成規則的比對誤判」在正常規則命名長度下不成立;只有在規則名本身異常長(> 200 字)時才會連動到 F1 同一個截斷根因,不另開一條。
