severity: major

## F1 rule-gap 的 --json 輸出沒過 _esc_clean,規則 id 裡的控制字元(DEL/C1)原樣流出終端
severity: major
blocking: yes
引句:「counts.setdefault(rid, {"n": 0, "desc": _esc_clean(ev.get("desc", ""), 60)})」

修法只把**印出來的那一行**(文字模式,`print("  " + _esc_clean(rid, 80) + ...)`)過了 `_esc_clean`,但 `missing` 這個 dict 的 **key 本身**(`rid = _raw.strip()`,直接來自使用者可控的逃逸帳 `rule` 欄)從頭到尾沒被清洗,`counts.setdefault(rid, ...)` 是用未消毒的 `rid` 當鍵。`--json` 分支是 `json.dumps({"missing": missing, ...}, ensure_ascii=False)`,直接把這個未清洗的 key 印到 stdout。

`_esc_clean` 的既有理由(它自己的 docstring)寫得很清楚:「ANSI 逃逸碼進終端=帳本可信度風險」「含 8 位元 C1 控制碼(r2 資安席)」——但這條防線只蓋到文字模式的顯示,`--json` 模式是另一條沒被想到的輸出路徑,而且 `json.dumps(..., ensure_ascii=False)` **不會**幫你擋:JSON 規範只強制轉義 U+0000–U+001F(所以 ESC `\x1b` 會變成安全的 `\u001b`),但 DEL(`\x7f`)與 C1 控制碼(U+0080–U+009F,這支程式自己認定要擋的範圍)不在強制轉義之列、`ensure_ascii=False` 又關掉了非 ASCII 的轉義,兩者疊加的結果就是 DEL 位元組原樣穿透。

同一批修正裡另外三個地方(F 缺口清單以外的 `--list` 顯示)都是靠 `_esc_clean` 統一擋,唯獨 `rule-gap --json` 這條路徑漏接——跟這次修正本身要補的洞(「rule-gap 把逃逸帳的 desc 與 rule 原樣印到終端,可藏控制字元」)是同一類問題,只是換了個輸出模式就繞過去了。新增的測試 `t_escape_review_r3_fixes` 只驗了文字模式(`"HIDDEN" in r.stdout`),完全沒測 `--json`,所以這個回歸沒被抓到。

重現(在實驗目錄跑,不動正式 repo):
```
EXP=/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/ba2fc358-b2c4-4fe8-b8cf-9883c1468562/scratchpad/r3fix/exp-通才
rm -rf "$EXP/repo3" && mkdir -p "$EXP/repo3/docs"
git -C "$EXP/repo3" init -q
python3 - <<'PY'
import json
row = {"token":"E9","loop":"甲","desc":"d","rule":"R\x7fC1\x9bTEST"}
open("EXPPATH/repo3/docs/.escape-log.jsonl","w",encoding="utf-8").write(json.dumps(row, ensure_ascii=False)+"\n")
PY
python3 /Users/enzo/harness/lumos-toolchain/scripts/lumos rule-gap --repo "$EXP/repo3" --json | python3 -c "import sys;d=sys.stdin.buffer.read();print(repr(d));assert b'\x7f' in d or b'\xc2\x9b' in d, '應該含原始控制字元,證明沒被清洗'"
```
(上面 `EXPPATH` 換成 `$EXP` 實際路徑;我在本機已跑過,`--json` 輸出的原始 bytes 是
`b'{"missing": {"R\x7fC1\xc2\x9bTEST": {"n": 1, "desc": "d"}}, ...}'`——`\x7f`(DEL)與 `\xc2\x9b`(UTF-8 編碼的 U+009B,即 C1 控制碼)都原樣穿透,`\x1b`(ESC)則因為 JSON 規範強制轉義而變成安全的 `\u001b`,兩種輸出模式因此不一致。)

補充(非阻斷,同一段程式碼的次要不一致):文字模式對 `rid` 有截斷(`_esc_clean(rid, 80)`),`--json` 模式的 key 完全不截斷——同一份資料兩種輸出的長度上限也不一致,只是危害遠小於控制字元穿透,一併寫在這裡不另開一條。

---

已看,無:
①同族讀帳點——已對 `_escape_raw_rows`(逃逸清單/統計)、`_jsonl_append_verified`(共用寫完讀回自驗)、`_door_for_loop`(判門,兩處 try)、`_auto_escape`(自動記帳讀已知迴圈)、`cmd_loop_escape` 的 `--list` 與記帳驗證兩處 try、`_escape_review_rows_by_loop`(讀 `.canary-log.jsonl`)、`_escape_released_loops`(讀 `.governance-log.jsonl`)逐一對過超深巢狀行,全部改接 `(ValueError, RecursionError)` 或 `(ValueError, AttributeError, RecursionError)`,範圍與 PITFALL 筆記寫的「8 處」對得上;另外實測 `loop escape --withdraw`(撤回路徑,走 `_escape_raw_rows` + `_jsonl_append_verified`,兩者都已補)帶超深巢狀行不崩、rc=0,這條沒被 PITFALL 明講但也是安全的,因為它復用同一批已修的共用函式。`rule-gap` 本身的 `json.loads` 是既有的 `except Exception`,本來就接得住 `RecursionError`,這次沒改也沒事。
②加寬例外的範圍——全部只包住單一行的 `json.loads(...)`(或緊接著的 `.get()`),沒有把後續處理邏輯一起包進 try,不會意外吞掉巢狀行以外的真錯誤;新加的 `RecursionError`/`AttributeError` 都是精確對應「這行資料本身解析失敗」的情境,沒有用 bare except 或 `except Exception` 擴大化。
④測試對症性——把修正還原成 `except ValueError:`(以及把 `_esc_clean` 換回裸接字串)之後,在實驗目錄重跑 `t_escape_review_r3_fixes`,6 個子斷言全部翻紅(`RecursionError: Stack overflow` 直接冒出未捕例外),修正套回去後在正式 repo 跑 `python3 scripts/test_lumos.py -k escape_review_r3` 是 8 passed / 0 failed——測試對這批修正是真的會翻紅、不是擺著好看。
