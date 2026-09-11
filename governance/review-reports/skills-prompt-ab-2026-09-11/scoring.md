# 六份代碼審查報告評分(skills-prompt-ab-2026-09-11)

評分依據:`design.md` 的標準答案 K1–K7;查證用程式樹 `/Users/enzo/.claude/jobs/9d19b273/tmp/r1-tree`;所有「其他真問題」與「假問題」都用實際跑過的 repro script(路徑 `/tmp/roundless_repro/repro*.py`)或直接讀程式碼核對過,不是憑印象判。

標準答案摘要(供對照):
- K1:資安席「涵蓋最後一版」只比檔名集合、不比內容(`_disposal_security_step` 用檔名差集)。
- K2:loop 編號 `code` 開頭無連字號時 `_roster_kind` 回 None,`_gated_seats_for` 用 `!= "code"` 整步 skip;同檔 `_disposal_clause_step` 對同型編號卻是 fail-closed 當設計審。
- K3:`_git_unquote_path` 用 `.strip()` 削尾端空白,含空白的檔名被誤判相同。
- K4:`_git_unquote_path` 手寫反解八進位跳脫,與 repo 其他地方一律 `-c core.quotePath=false` 的做法不一致。
- K5:`cmd_bound_tests` 的 `red` 分支沒印「另有 N 支沒跑」。
- K6:資安席不過時印的補救指令,`--loop {loop_id}` 沒加 shell 引號。
- K7:`code-loop pass` 不回頭驗問閘;分級由帳上第一筆 `--tier` 定死,跟推送時重算的分級不對帳。

六份報告都沒有找到 K3、K4、K6、K7(全文 grep `strip`/`quotePath`/`shlex`/`引號`/`分級`/`--tier`/`重新算` 等關鍵詞,只有 s1 X4 提到 `quotePath` 是作為別的理由帶過,不構成命中)。

---

## s1.md(6 條)

**X1** — 命中 **K1**。引句與機制(「涵蓋」只比檔名集合、資安席審過的檔內容事後被換成有害碼仍判過)與標準答案一字不差對上,並附了雙輪重現(r1 洗白、r2 加 SQLi、`--disposal` 仍 PASS)。

**X2** — **其他真問題**。主張:round-less(不帶 `--round`)帳列,`_disposal_security_step` 用 `r.get("round") == rid` 篩「判定輪」,但 round-less 帳的 `round` 欄本來就是 `None`、`rid` 是 `_loop_status_disposal` 內部合成的 `"__seqN"`,兩者永遠對不上,`judge` 恆空 → 資安席一步永遠印「材料放錯了」而 FAIL,即使資安席確實留痕正確。
查證:實跑 `/tmp/roundless_repro/repro.py`(對一個 code/high、round-less、資安席+正確性席都正確記帳、ts 設在生效日後的迴圈跑 `loop status --disposal`),輸出:
```
[disposal] 資安席: ✗ — 判定輪的凍結 patch 讀不到或抓不到任何檔名,沒辦法確認資安席看過的檔有沒有涵蓋最後一版;看不懂就不放行
⛔ DISPOSAL GATE FAIL (code-roundless-repro 輪 __seq1: 資安席)
rc= 1
```
確認為真、且訊息確實講錯原因(講成材料放錯,其實是分組鍵比對錯)。不在 K1–K7 之列,判定為真問題。

**X3** — 命中 **K5**。`cmd_bound_tests` 的 `red` 分支(`scripts/lumos:22600` 一帶)只印 `v["red"][:6]`,沒有讀 `v.get("not_run")`/`v["reason"]`,與新加的 `not_run` 資訊沒接上——機制與 K5 完全一致(只是 K5 標準答案沒特別點名這是 X1 s1 在既有未動分支上的缺口,but 這正是同一個問題)。

**X4** — **其他真問題**。`_patch_files_from_text` 對沒有 `+++`/`---`/`rename to` 行的段落(純 mode 變更等)退回用 `rest.rfind(" b/")` 猜檔名分界,檔名本身含字面 ` b/` 子字串時會切錯。
查證:
```
$ python3 -c "...; print(m._patch_files_from_text('diff --git a/scripts/foo.sh b/scripts/sub b/bar.sh\nold mode 100644\nnew mode 100755\n'))"
{'bar.sh'}   # 預期 {'scripts/sub b/bar.sh'}
```
在 r1-tree 上重現成功。屬於資安席涵蓋比對用到的解析函式的邊界 bug,不在 K1–K7 之列,命中機率低但確實存在。

**X5** — **其他真問題**(報告自己標「未能重現」,但我實際查證後確認為真)。主張:`jfiles`(「最後一版」該有的檔案全集)是判定輪**全部**帳列的 `snapshot_path` 聯集,不是只認 carrier;同輪某一席的 `snapshot_path` 若意外指到別的 patch,`jfiles` 會被灌水。
查證:`/tmp/roundless_repro/repro2.py`——同一輪兩席,資安席 `--snapshot` 指向真正的凍結 patch(1 個檔),另一席 `--snapshot` 誤指到一份多帶一個不相干檔案的 patch(2 個檔),跑 `--disposal`:
```
[disposal] 資安席: ✗ — 最後一版改到的檔有 1 支資安席沒看過:app/unrelated_extra_file.py
⛔ DISPOSAL GATE FAIL
```
即使資安席正確審過真正的最後一版,仍被不相干的雜訊 patch 拖累判 FAIL。方向上是「誤判過嚴」不是「安全繞過」,但邏輯確實不一致(quote-check 只信 carrier,這一步卻聯集全部)。真問題,不在 K1–K7 之列。

**X6** — **其他真問題**(極輕微)。`_config_has_top_run_cmd` 每次呼叫重新讀一次 `.lumos/config.json`,而同一次 `bound-tests`/`code-loop check` 呼叫裡 `load_platforms` 已經讀過同一份檔。查證:讀 `scripts/lumos` 的 `_run_bound_tests`/`_bound_tests_check`/`_no_run_cmd_reason` 呼叫鏈,確認是多讀一次、非功能性 bug,純效能瑣事,判為真但價值極低。

**s1 小計**:6 條;命中 K 集合 = {K1, K5}(2 個相異);其他真問題 4;假問題 0;判不出 0。

---

## s2.md(4 條)

**X1** — 命中 **K1**。主張與標準答案的具體示例不同(不是「同一支檔內容事後被換掉」,而是同一輪裡 `--snapshot` 記得比真正的 `--spec`/G3 驗過的內容小,函式完全不讀 `spec`/`result_sha256` 只信 `snapshot_path`),但打的是同一個根因:「涵蓋」判斷只對未經交叉驗證的檔名集合做差集,不驗真實內容。查證:實跑其附的 repro script(在本機用 r1-tree 的 `scripts/lumos` 執行,`patchA`=1 檔、`patchAB`=2 檔,兩席都用 `--snapshot patchA --spec patchAB` 記帳)得到
```
[disposal] 資安席: ✓ — r1 資安-sonnet(看過的檔涵蓋最後一版 1 個)
✅ DISPOSAL GATE PASS
```
而 G3 已認證最後一版是 2 個檔的 patchAB——`app/extra.py` 資安席從沒看過卻判過。機制與 K1「只比檔名集合、不比內容」同源(`jfiles`/`sfiles` 都是從未交叉驗證的欄位算出的檔名集合),判命中 K1(比標準答案給的例子更犀利的同一漏洞的另一種觸發路徑)。

**X2** — **其他真問題**。`_git_unquote_path` 用 `codecs.escape_decode`,這是 CPython 內部給 `unicode_escape`/`string_escape` codec 用、未列入官方 `codecs` 文件的私有 API。查證:`python3 -c "import codecs; help(codecs.escape_decode)"` 確實查不到官方文件條目,且該用法在原始碼裡沒有走 `-c core.quotePath=false` 這條路(那是 K4 講的「架構不一致」問題),這條講的是「依賴未公開介面」的脆弱性,是另一個面向,不是 K4 本身(K4 沒被任何報告命中)。真但輕微、未翻紅(自陳)。

**X3** — **其他真問題**。`_gated_seats_for` 的生效日判斷只納入「有 `ts` 欄」的帳列;若整個迴圈所有帳列都沒有 `ts`(理論上可能,如手改帳),`keys` 為空,`any(k is None ...)` 對空 list 恆 False(不會走 fail-closed)、`if keys and ...` 也因為空 list 是 falsy 被跳過,直接落到 `return "apply"`。
查證(讀碼確認邏輯路徑,正常操作下 `canary record` 一定會自動蓋 ts,此路徑打不到,報告自己也承認未實際重現):邏輯上確實成立,但方向是「更嚴」不是「繞過」,屬於真的邏輯不一致但非安全漏洞,列為真問題。

**X4** — **其他真問題**(弱,報告自承非本次新洞)。資安席出席只驗席名字串比對得上,完全不驗報告內容是否真的討論了那些檔。查證:讀 `_disposal_security_step`/`_prov_check` 全文,確認除了 sha256 存在性比對外沒有任何內容語意檢查。是真的觀察,但屬於「機制固有局限」而非這次 diff 特有的不一致,價值很低,仍算作真問題(非假問題,只是效力弱)。

**s2 小計**:4 條;命中 K 集合 = {K1}(1 個);其他真問題 3;假問題 0;判不出 0。

---

## s3.md(2 條)

**X1** — 命中 **K2**。精準指出 `_gated_seats_for` 用 `_roster_kind(loop_id) != "code"` 判斷,`_roster_kind` 對 `code` 開頭無連字號回 `None`,`None != "code"` 為真 → 整步 skip,與 `_disposal_clause_step`(對同一種編號故意 fail-closed 當設計審)方向相反。附 `loop_id="codestage9-bypass"`、`--tier high` 的完整重現,`--disposal` 回 rc0、印「資安席: —(設計審不要求資安席)」。與標準答案 K2 完全對上(含「同檔另一步驟是照最嚴方向判」這一半)。

**X2** — **其他真問題**。生效日判斷 `min(k for k, _ in keys)` 是對**整個迴圈**(`rounds`,不是判定輪)取最早 ts;只要這個 loop id 的第一筆帳早於生效日,不管之後過幾個月、判定輪本身多晚,永遠 skip 資安席要求。
查證:`/tmp/roundless_repro/repro3.py`——`code-longrun-repro` 的 r1 記在 2026-09-01(生效日前),判定輪 r2 記在 2026-10-01(生效日後整整一個月,兩支檔、全程無資安席),跑 `--disposal`:
```
[disposal] 資安席: —(迴圈首筆帳 2026-09-01T10:00:00 早於生效日 2026-09-12,不回溯)
✅ DISPOSAL GATE PASS
```
確認為真、且影響顯著(同一個 loop id 重跑是這套工具的既定用法,一旦某 loop id 曾在生效日前開過任何一輪,之後永久免資安席)。與 K7(tier 由首筆定死)同一種「錨定在首筆」的設計模式,但對象是生效日不是 tier,K7 沒有涵蓋這一點,判為不在 K1–K7 之列的真問題。

**s3 小計**:2 條;命中 K 集合 = {K2}(1 個);其他真問題 1;假問題 0;判不出 0。

---

## s4.md(2 條)

**X1** — **其他真問題**。與 s1 X4 同一機制(`rest.rfind(" b/")` fallback 對含字面 ` b/` 的檔名切錯),用的是純權限變更(`old mode`/`new mode`,無 `+++`/`---`)的例子。
查證:
```python
m._patch_files_from_text('diff --git a/docs/a b/c.png b/docs/a b/c.png\n')
# {'c.png'}  非預期 {'docs/a b/c.png'}
```
在 r1-tree 上重現成立。不在 K1–K7 之列。

**X2** — **其他真問題**。`_loop_status_disposal` 的 docstring 本次改成「六步合取」(含新加的⑤條款綁定、⑥資安席),但函式最後真正印的 PASS 橫幅文字沒有跟著改,仍寫死「G3 ∧ 處置全清 ∧ 留痕可重算 ∧ 引句全錨定」。
查證:讀 `scripts/lumos` 的 `_loop_status_disposal` 結尾(diff 第 496–499 行一帶,PASS 分支),確認橫幅字串確實沒有提到「條款綁定」或「資安席」,與更新後的 docstring 不一致。真、屬於這次 diff 自己引入的內部不一致,不在 K1–K7 之列。

**s4 小計**:2 條;命中 K 集合 = {}(0 個);其他真問題 2;假問題 0;判不出 0。

---

## s5.md(2 條)

**X1** — 命中 **K1**。與 s1 X1 同一手法(round r1 資安席審過 `app/login.py` 內容 A,round r2 同檔名換成 `os.system(...)`,涵蓋檢查仍判 ✓),另外附了一版不經 CLI、直接 import 呼叫 `_disposal_security_step` 的最小重現,機制與標準答案完全一致。

**X2** — 命中 **K5**。點出 `not_run` 資訊只接進 `green` 與 `no-config` 分支,既有的 `red` 分支完全沒讀,並附真跑 CLI 的重現(一個平台紅、一個平台沒指令,`bound-tests --diff` 輸出完全不提沒跑的平台;加 `--json` 才看得到 `not_run`)。與標準答案 K5 對上。

**s5 小計**:2 條;命中 K 集合 = {K1, K5}(2 個);其他真問題 0;假問題 0;判不出 0。

---

## s6.md(6 條)

**X1** — **其他真問題**。與 s1 X2 同一機制(round-less 帳列的 `round` 欄是 `None`,`_disposal_security_step` 內部 `rid` 是合成的 `__seqN`,`r.get("round") == rid` 永遠對不上,`judge` 恆空)。查證同 `/tmp/roundless_repro/repro.py` 的輸出,確認為真。不在 K1–K7 之列。

**X2** — **其他真問題**。`cmd_bound_tests`/`cmd_code_loop` 的新 `no-config` 分支把 `v['reason']` 包進「提醒:受波及合約測試沒有跑——」這句固定前綴,而單平台 `_no_run_cmd_reason` 回的字串本身已經包含「受波及合約的測試沒有跑」,兩句疊起來同一句話講兩遍。
查證:`/tmp/roundless_repro/repro4.py` 直接呼叫 `_no_run_cmd_reason("...", False, set())` 並組出完整訊息:
```
提醒:受波及合約測試沒有跑——這個專案沒設測試指令(.lumos/config.json 的 test.run_cmd),受波及合約的測試沒有跑——合約測試閘等於沒開
```
確認重複。真、屬於這次 diff 新增分支的訊息瑕疵,不在 K1–K7 之列。

**X3** — 命中 **K1**。同一機制(檔名沿用、內容被大幅改寫,`missing` 集合仍空,判 ✓),並指出既有測試 `t_disposal_security_seat_required` 第④案本身就在驗這個「子集 → PASS」行為,證明是刻意設計而非失手——這正是標準答案 K1 描述的「只比檔名集合、不比內容」。

**X4** — **其他真問題**(弱,與 s2 X4 同一觀察)。「資安」席出席只靠 `--auditor` 欄位字串比對,不驗那份報告是不是真的照資安 framing 審。真、但非新洞、價值低。

**X5** — **其他真問題**(與 s2 X3 同一機制)。`keys` 只收「有 `ts` 欄」的帳列,完全沒有 `ts` 欄的帳列被直接濾掉、不會觸發下面的 fail-closed 分支,`min(keys)` 可能漏看真正最早的那筆。讀碼確認邏輯成立,方向上是「更嚴」不是「繞過」,判真問題(價值低,正常寫入路徑打不到)。

**X6** — **其他真問題**(與 s2 X2 同一機制)。`codecs.escape_decode` 是未公開的 CPython 內部 API,依賴其存在的風險。真、輕微、未翻紅。

**s6 小計**:6 條;命中 K 集合 = {K1}(1 個);其他真問題 5;假問題 0;判不出 0。

---

## 總表

| 報告 | 總條數 | 命中的 K(去重) | 其他真問題 | 假問題 | 判不出 |
|---|---|---|---|---|---|
| s1.md | 6 | K1, K5(2) | 4 | 0 | 0 |
| s2.md | 4 | K1(1) | 3 | 0 | 0 |
| s3.md | 2 | K2(1) | 1 | 0 | 0 |
| s4.md | 2 | 無(0) | 2 | 0 | 0 |
| s5.md | 2 | K1, K5(2) | 0 | 0 | 0 |
| s6.md | 6 | K1(1) | 5 | 0 | 0 |

備註:
- 全部 22 條發現查證後都成立(0 假問題、0 判不出)——六份報告本身信心校準得不錯,沒有明顯瞎編。
- 標準答案 K3(strip 誤判空白檔名相同)、K4(`_git_unquote_path` 與全 repo `-c core.quotePath=false` 慣例不一致的架構問題)、K6(`canary record none` 補救指令 `--loop {loop_id}` 沒加 shell 引號)、K7(`code-loop pass` 不回頭驗問閘 + 分級由首筆 `--tier` 定死)——六份報告**全部沒找到**。
- K1(資安席涵蓋檢查只比檔名不比內容)最多人找到:s1、s2、s5、s6 都命中(4/6);K5(bound-tests 紅分支漏印未跑平台)被 s1、s5 命中(2/6);K2(loop id 無連字號時資安席被繞過)只有 s3 命中(1/6),但 s3 是唯一一份同時抓到 K2 的報告。
- 沒有任何一份報告同時命中 K1、K2、K5 三個以上;最全面的是 s1(命中 2 個 K + 4 條獨立真問題,含 round-less 帳列比對錯這個影響面不小的獨立 bug)。
