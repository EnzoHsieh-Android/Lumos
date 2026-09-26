severity: major

## F1 撤回紀錄本身會被現有讀者當成假逃逸列算進統計,spec 沒交代要排除
severity: major
blocking: 是 —— 不改,`lumos gov --stats`、S14 撤除條件漏斗、`lumos rule-gap` 這三個既有讀者會把「撤回」這種 meta 紀錄當成一筆逃逸算進數字,做出錯的統計結果。
引句:「統計類讀者(問閘尾漏斗、治理帳統計、escape-stats)用預設,**不算**被撤的列。」
說明:這句(以及整段三)只規定「不算**被撤的列**」(即已經被撤回的那筆原始逃逸列),完全沒提「撤回紀錄自己這一列」該不該被 `_escape_rows_for` 吐出來。撤回紀錄的形狀(第 48 行)是 `{"kind":"withdraw","target":...,"reason":...,"by":...,"ts":...,"token":...}`,沒有 `loop`/`stage`/`severity`/`plan` 欄位。`_escape_rows_for`(`scripts/lumos:7397-7415`)目前是逐行 `json.loads` 後原樣塞進 `out`,不看 `kind`;如果 `include_withdrawn` 的實作只是「濾掉『目標 token 曾被撤回』的原始逃逸列」,撤回紀錄這一列本身仍會被吐出來,混進以下讀者:
- `scripts/lumos:6743-6745`(`_render_gov_stats`,gov --stats 的治理帳統計):`len(escapes)` 會把撤回紀錄也算進「逃逸帳 N 筆」,`max(e.get("severity","minor")...)` 對撤回紀錄套用預設值 `"minor"` 算進「最重」。
- `scripts/lumos:2300-2309`(S14 撤除條件漏斗):撤回紀錄的 `stage` 缺欄位,`_by.setdefault(_dr, {}).setdefault(str(_e.get("stage") or "?"), 0)` 會把它算進 `?` 階段桶,污染「按階段」統計。
- `scripts/lumos:20233-20240`(`cmd_rule_gap`):撤回紀錄沒有 `rule` 欄位,`ev.get("rule")` 為 None → `unlabeled += 1`,把撤回紀錄算成「一筆沒標規則的逃逸」,虛灌「未標規則」計數。
這三處都不是 `--list`,而是 spec 第四節明確點名要靠 `_escape_rows_for`/自己讀檔再套判斷函式的「統計類讀者」,所以照字面實作,`include_withdrawn=False` 這個預設不會真的把撤回紀錄擋在統計外面——它只擋了「被撤的原逃逸列」,漏了「撤回這一列本身」。escape-stats(新指令)大概率會被實作者順手處理對,但既有三個讀者未必會被同一份修改覆蓋到,因為 spec 沒有把它們列進「要排除 kind=withdraw」的清單。

## F2 撤回紀錄沒有 loop 欄位,`--list` 會把它分到獨立的「?」群組,不會跟它撤掉的那筆逃逸列擺在一起
severity: minor
blocking: 否 —— 不影響統計正確性、也沒有違反 S3 逐字要求(S3 只要求列出來、標理由,沒承諾要跟原列同組),只是讓巡帳的人比較難一眼看出某筆逃逸旁邊有沒有被撤;不改也不會讓實作者做出錯的行為或漏掉合約。
引句:「撤回紀錄本身也列。另加 `--withdrawn` 只列撤回過的,給人查。」
說明:現有 `--list` 是 `by_loop.setdefault(str(r.get("loop", "?")), []).append(r)`(`scripts/lumos:9459-9461`)照 `loop` 欄分組列印。撤回紀錄形狀(第 48 行)沒有 `loop` 欄,只有 `target`(被撤 token)——若照現有分組邏輯不做特殊處理,撤回紀錄會統一落在 `by_loop["?"]` 這個假迴圈群組,而不是出現在它撤掉的那一列所在的迴圈群組底下。想知道「某筆逃逸後來被撤了」,讀者得同時去看那筆逃逸列上的「已撤回」註記,以及另一個不相干的「?」群組裡的撤回紀錄列,才能拼出全貌——跟第 103 行「這一期不限制誰能撤……清單一定標出來」想達到的「一眼看得到」有落差。

## F3 回退段落對 `_plan_for_loop` 前綴/NFC 修正的影響描述有誤,也漏了它與 escape-stats 的回退連動
severity: major
blocking: 是 —— 這段話會讓實際執行回退的人誤判影響範圍:以為要保護一個其實從沒依賴過這項修正的既有呼叫者,卻沒被提醒真正會壞掉的是被歸類為「移除即可」的 escape-stats,若只回退 `_plan_for_loop` 這一項、保留 escape-stats(spec 把兩者列成可分開判斷的兩個回退項),code- 迴圈的範圍類分類會悄悄降級成「未分類」而沒有任何報錯或提示。
引句:「它讓其他呼叫者也找得到 `code-` 迴圈的計劃,回退會讓它們又找不到;回退時要跟著查這些呼叫者。」
說明:目前整支 `scripts/lumos` 裡呼叫 `_plan_for_loop` 的只有一處,`scripts/lumos:8005-8010`:
```
if loop and str(loop).startswith("code-") and _hit:
    derived = str(loop)[len("code-"):]
    _auto_escape(env, "code-loop", severity, ...,
                 [(derived, _plan_for_loop(env, derived))], ...)
```
呼叫端自己先把 `code-` 前綴剝掉(`derived`),再把**已經去掉前綴**的字串傳給 `_plan_for_loop`——也就是說這個既有呼叫者從來沒有依賴 `_plan_for_loop` 內建去前綴的邏輯,回退不會讓它「又找不到」。我實際執行驗證:
```
loop = "code-逃逸帳對得起來"; derived = loop[len("code-"):]
_plan_for_loop(env, derived) → "Projects/逃逸帳對得起來_計劃.md"
```
在完全沒套用 S10 修正的目前版本上就已經找得到,證明這條既有路徑不受影響。真正吃到 S10 修正的是「之後另開」段沒提但第四節第二個 bullet 點名的新呼叫者——`loop escape-stats` 算範圍類時直接傳原始(帶 `code-` 前綴)的迴圈編號給 `_plan_for_loop`(spec 第 68 行:「查計劃時先把 `code-` 前綴去掉、兩邊都做 NFC 正規化,再用 `_plan_for_loop`」)。回退段把「`_plan_for_loop` 的前綴與 NFC 修正」和「escape-stats」列成兩個獨立的回退項(第 95、97 行),但沒寫明兩者的依賴關係:單獨回退前者、留著後者,會讓 escape-stats 對所有 `code-` 開頭迴圈的範圍類查詢失敗、靜默落回「未分類」(第 68 行本身定義的 fallback),而回退段完全沒提到這個後果,也沒說回退 `_plan_for_loop` 時要連帶檢查/回退 escape-stats 裡對範圍類的處理。

已看,無:條款 S1(`loop_kind` 判法)、S2(`--no-defect-ref` 擋下條件)、S4(撤回驗證四種擋下情況與拿不到鎖時印擋下訊息)——現有 `set`/`append`/`decision-add`/`new` 等寫入指令的 dispatch 點全部是 `try: ... except (ValueError, RuntimeError) as e: print(f"擋下:{e}", ...); return 2`(如 `scripts/lumos:31742-31749`),`_vault_write_lock` 逾時本身丟的就是 `RuntimeError`(`scripts/lumos:13791`),新的 `--withdraw` 分派點沿用同一慣例即可轉成「擋下:」訊息,不需要 spec 另外交代。S4 也要求整段「讀帳確認目標→寫入」包在鎖裡;`_vault_write_lock` 支援同一程序巢狀拿鎖直接過(`scripts/lumos:13777-13783`),不會有自己卡自己的問題,設計可行。S10 描述的 `_plan_for_loop` 現況(直接查 `Projects/<id>_計劃.md`/`Projects/<id>.md`,不做前綴/NFC 處理)與程式碼(`scripts/lumos:9293-9298`)相符,S13 描述的 `rule-gap` standalone 佈局雙候選路徑判斷與程式碼(`scripts/lumos:20225-20226`)相符。「這一期不限制誰能撤(單人 repo)」的風險承認有配 `REVISIT:2026-10-26 看撤回用過幾次`(計劃節點第 15 行),符合鐵則四對回頭條件的要求,不算違規;repo 內沒找到任何會定期 grep `loop escape --list` 的既有腳本(僅在 `scripts/lumos:9250` 的註解裡提到「攔截/逃逸週報」是外部 grep 這份輸出的協議,不是本 repo 內的機制),所以撤回濫用目前完全沒有機械/週期性的提醒手段,但這點就是靠 REVISIT 條件延後裁決,不是 spec 沒想過,不算新洞。「舊版 lumos 讀到撤回紀錄」段落(第 56 行)對 `--list` 行為的描述(會被當成欄位不標準的可疑列、印出「?None」「[沒標該抓的規則]」等噪音,但不會壞)與現有 `--list` 程式碼(`scripts/lumos:9459-9474`)實際跑起來的效果相符,這條描述本身正確——只是如 F1 所述,它遺漏了非 `--list` 讀者的數字污染後果。

最嚴重 severity: major;blocking 共 2 條。
