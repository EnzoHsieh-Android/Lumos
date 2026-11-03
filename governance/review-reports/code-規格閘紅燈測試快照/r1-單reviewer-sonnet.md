severity: major

審查範圍:diff 全文(1736 行)、`scripts/lumos` 對應真代碼、11 支測試。`python3.14 scripts/test_lumos.py -k redbase` 為 76 項全綠,另跑的子集 `tq_guard`、`spec_gate`、`gov_`、`lint_new`、`codeloop_record` 也全綠。破壞測試(mutation)是在我自己的副本上做的,原 repo 沒動。角色卡:派工寫了 `LUMOS-ROLE-CARDS: on`,但尾端沒附卡,略過。

## 發現

### F1 紅燈版收集只用測試名去重,不分平台;同名測試跨平台時,第二個平台的紅燈測試被靜默丟掉
severity: major
blocking: 是 — 會做出錯的行為:保護靜默缺席、條款被併到別人身上,違反 S1「沒存的都記原因並印一句」
引句:「for cid, plat, method, v, _why, detail in rows or []:」
- 位置:`scripts/lumos:14220`(`_redbase_collect`),`seen` 與 `caps` 都只用 `method` 當鍵(`scripts/lumos:14224`)。`_redbase_branch_state` 的 `greened` 也只存測試名。
- 場景:`.lumos/config.json` 有兩個平台,android 用 kotlin-junit、backend 用 java-junit,兩邊各有一支叫 `shouldCalc` 的綁定測試,規格閘跑出 S1(android)紅、S2(backend)紅。
  - 第二個平台那支走到 `if method in caps:`,只是把 `S2` 併進 android 那份的 `clauses`。紅燈版裡 backend 的測試根本沒存,`redbase_skipped` 與螢幕輸出也沒有這筆原因。之後 backend 的新測試被改成實作輸出,推送時完全沒保護。
  - 若 android 那支是綠的:`greens` 收了 `shouldCalc`,backend 的紅被 `seen` 擋掉。之後 backend 同名測試再跑紅,還會被判成「曾判綠」。
- 重現(`/tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet/exp/plat1.py`),輸出:
  - 兩個都紅:`[('android/app/src/test/java/x/ATest.kt', ['S1', 'S2'])] []`
  - android 綠在前:`[] [('shouldCalc', '判綠')] {'shouldCalc'}`
- 測試缺口:`t_spec_redbase_written_on_red` 只有單平台 fixture。

### F2 S3「兩份 ts 寫反時照行序判」的唯一斷言是 `any(...)`,改成照 ts 排序測試照綠
severity: major
blocking: 是 — 驗收條款 S3 的唯一驗證抓不到「改照 ts 排」,測試 docstring 宣稱的翻紅釘不成立
引句:「check("S3 兩份 ts 寫反照行序判,照樣列", any(c["rule"] == "tq/redbase-weakened" for c in cs), cs)」
- 位置:`scripts/test_lumos.py:122632`(`t_tg_redbase_chain`)。docstring 寫「翻紅釘:只取最早一份、改照 ts 排、只比最後一份 → 紅」。
- 場景:`c5` 是 900、ts 12:00,`c6` 是 800、ts 09:00,終點是 800。
  - 照行序:`c5→c6` 命中,`c6→終點` 不命中。
  - 照 ts 排:`c6→c5` 與 `c5→終點` 兩步都命中。
  - 兩種排法都至少有一條 `tq/redbase-weakened`,`any` 都過。
- 重現:
  - 在副本的 `_tg_redbase_records` 回傳前加 `out.sort(key=lambda d: d.get('ts',''))`,跑 `-k redbase` 得 `76 passed, 0 failed`。
  - `exp/ts1.py` 直接比 token:行序 `['SPEC-c0000005']`,依 ts 排 `['SPEC-c0000005','SPEC-c0000006']`。
  - 另兩個翻紅釘有效:「只取最早一份」與「只比最後一份」會被其他斷言抓到。

### F3 寫入端的 5 MB 檢查量的是原文長度,不是 JSON 長度;寫得出讀端必擋的檔
severity: minor
blocking: 否 — 只在接近 5 MB 的病態測試檔才發生,且是可放行候選,不會漏判
引句:「if why is None and size + add + 256 > _TG_MAX_BYTES:」
- 位置:`scripts/lumos:14350`(寫入),讀端 `_tg_rb_doc` 的 `if size > _TG_MAX_BYTES:`。
- 場景:一支 4,789,005 位元組的合法 `.kt`(單檔上限內),換行與引號密度一般。
  - JSON 逸脫(`\n`、`\"`)後檔案是 5,089,219 位元組。寫入端放行,推送時讀端回「紅燈版檔超過 5 MB」。
  - 結果是整份紅燈版不可用,被擋下後只能放行。
- 重現:`exp/size1.py`,輸出 `json bytes 5089219 >5MB? True`。
- 該條款(S1「加進去會超過 5 MB」)沒有測試:拿掉整段檢查,76 項仍全綠(見 F8)。

### F4 讀端與寫端每筆測試都重新切一次整檔,耗時是測試數乘以檔大小;迴圈裡沒看截止時間
severity: minor
blocking: 否 — 單檔上千支紅燈測試才明顯,是慢不是錯
引句:「got = _tg_rb_entry(t, doc["files"])」
- 位置:`scripts/lumos:49655`,`_tg_rb_entry`(`scripts/lumos:49688`)內有 `_tg_functions(text...)`。寫端 `_redbase_read_one` 同樣每支重切。`_tg_rb_load` 的迴圈沒有 `deadline` 檢查。
- 場景:單檔 N 支紅燈測試。
  - `_tg_functions` 切一次:1000 支約 0.018 秒、2000 支約 0.037 秒。
  - 實測 `_tg_analyze`:300 支 1.9 秒、1200 支 28.7 秒(關掉紅燈版段只要 0.1 秒)、1500 支 44.7 秒。寫端 1000 支約 17 秒。
- 重現:`exp/perf2.py 1200`。
- 建議:同一路徑的內嵌文字切一次,各測試共用。

### F5 寫入端檢查了測試檔有沒有被 git 忽略,沒檢查紅燈版目標路徑;擋下訊息教的「git add」在這種情況救不回
severity: minor
blocking: 否 — 需要消費專案自己的 `.gitignore` 蓋到 `governance/`,且有 `-f` 可救
引句:「ign = _sp.run(["git", "-C", str(rr), "check-ignore", "-q", "--", rel], capture_output=True, timeout=30)」
- 位置:`scripts/lumos:14279` 只查測試檔;`_redbase_write` 對 `governance/redbase/...` 完全沒查。訊息在 `scripts/lumos:49269`。
- 場景:專案 `.gitignore` 有 `governance/`(`lumos init` 預設只忽略 `code-loop/` 與 `runtime/`,所以要專案自己加)。
  - 規格閘寫了檔、留痕帶 `redbase`;`git add -A` 靜默略過這個檔。
  - 推送時回「還沒提交,請 git add」。照做得到 `The following paths are ignored ... Use -f`。
  - 訊息也沒說 `git add` 之後還得提交(或 amend),只 add 不提交,終點那一版仍然沒有這個檔。
- 重現:`exp/ign1.py`,`git add rc 1`。
- 孤兒檔的原因文字套用同一句 `verify`(「沒提交就 git add、被改就還原」),對孤兒檔無意義,正確動作是刪檔。

### F6 「判綠」也算進 `redbase_skipped` 並占滿 20 筆上限,真正重要的不存原因被擠掉
severity: minor
blocking: 否 — 要綁定測試有 20 支以上判綠才會擠掉
引句:「rec["redbase_skipped"] = [{"name": n, "reason": r_} for n, r_ in skipped[:20]]」
- 位置:`scripts/lumos:14427`(`_redbase_attach`)。`skipped` 按列順序累加,每支判綠的 Kotlin/Java 測試(含所有 keeps)都先進去。
- 場景:25 支判綠、1 支判紅但「判紅後檔案又被改」。`skipped` 共 26 筆,記錄與螢幕只留前 20 筆,全是「判綠」,紅的那支的原因既不印也不記。S1 要求每種都印一句。
- 重現:`exp/skip1.py`,輸出 `brand_new reason printed? False | in record? False`。
- 順帶:`redbase_skipped_n` 是新欄位名,計劃和 `Systems/規格閘` 都沒寫它,S1 測試也沒檢查它。

### F7 補讀紅燈版記到的測試檔時,200 MB 總量是另算的一份,與計劃「算進總量」不符
severity: minor
blocking: 否 — 只是預算記帳與文件不一致;沒有構成實際的資源失控
引句:「text = _tg_read(root, base, head, [(p, p) for p in need], deadline)」
- 位置:`scripts/lumos:49735`(`_tg_rb_fill`)。
- 場景:`_tg_read` 內部固定用完整的 `_TG_MAX_TOTAL`,沒帶 `consumed`。紅燈版 JSON 讀取是 `_TG_MAX_TOTAL - consumed`,補讀又是一份完整額度,最壞約 200 + (200 − consumed) + 200 MB。
- `tests[].path` 沒驗證副檔名與是否為測試檔,補讀會讀任意 repo 路徑的 base 與 head 兩版。這點依 lumos 威脅模型(單人、不防刻意偽造)不當缺陷,只記存在。

### F8 驗收條款有幾處沒有任何斷言守住(破壞測試存活)
severity: minor
blocking: 否 — 覆蓋面問題,被保護行為目前正確
引句:「翻紅釘:紅燈版沒當前一版、丟 no-assertion 的過濾拿掉、終點無斷言不跳過 → 紅。」
我在副本上逐一破壞,`-k redbase` 仍全綠(`76 passed, 0 failed`)的有:
- 拿掉寫入端 5 MB 檢查(S1 句子)。
- 讓 `_redbase_branch_rows` 忽略分岔點、改看整本帳(S6「這條分支上」)。實測分岔點相減本身是對的:`exp/fork1.py` 在 origin/main 有舊判綠列時,commit 後回 `[]`;只有「HEAD 就是 origin/main」時才會回 T1。
- 拿掉 `"tq/no-assertion"` 的過濾。該 docstring 說會翻紅,但終點無斷言時 `_tg_rb_chain` 早退,這個分支在終點永遠走不到。中間紅燈版無斷言的鏈沒有測試。
- `_tg_rb_path_ok` 整個改成 `return True`:只有 `docs/x.json` 這一個出界案例,`..`、反斜線、控制字元三個子條件沒測。
- 去掉 `redbase_skipped_n`。
- `t_tg_redbase_still_checks_new_rules`(S8)不需要新功能就會綠(分岔點比對那條沒被這個 diff 改過),只是回歸釘,不是新行為的證據。
- 有效的釘(確認抓得到):`catch-no-fail` 過濾、多載守衛、分岔點已有就跳過、孤兒檔、`greened`、空樹起點、內嵌超長行、搬家查找。

### F9 計劃與程式、文件不一致
severity: minor
blocking: 否 — 文件措辭與精度
引句:「簿記資料夾那行 KEY 加 `governance/redbase/`(新增),消費者數照程式寫」
- 計劃〈三、文件同步〉要在 `Systems/pitfalls-code-loop` 加這條 KEY,但 diff 只加了一行 `REVISIT:2026-12-15 ...`。該篇原有的 KEY 本來就寫「現在有哪些以程式為準」,所以不加不會誤導,只是計劃要改成與實際一致。
- 指紋身分:計劃寫「紅燈版 token + 子規則名 + 那條子規則原本的身分字串,同一身分第二次出現帶序號」。程式是 `tok\0rule\0c['ident']\0c['key']`,多帶了子候選的 `key`,沒有 `nth`。重複性實質等價,措辭要對齊。
- `redbase_skipped_n` 欄位未在 `Systems/規格閘` 格式說明出現(見 F6)。

## 圖譜鏡頭

| 節點 | 判斷 |
|---|---|
| `lumos-cli-read`(search 預設排除 superseded) | 不影響。diff 沒碰 search 或 supersede 濾網。 |
| `測試假綠形態`(還原翻紅釘須配前置斷言) | 部分違反。F2 的 ts 測試沒有前置斷言證明現場能區分兩種排法,宣稱的釘是第④型(現場走不到被測分支)。其餘測試多有 ★前置★。 |
| `guard-kill` | 不影響。rc 優先序與 `--json` 純度的程式沒動。 |
| `pitfalls-code-loop`(RISK,簿記資料夾) | 行為成立,但有兩點要記:`_BOOKKEEPING_DIRS` 加 `governance/redbase/` 後,放進來的程式檔對小改動閘、風險掃描等只看前綴的消費者是簿記(計劃已承認,與既有簿記資料夾同一天花板);舊版 lumos 沒有這項豁免,計劃用 REVISIT 記下,可接受。S11 只測 `.py`,沒測 `.kt`/`.java`/`.sh`。 |
| `loop-convergence-recording` | 不影響。審查帳列 `kind=spec-gate` 本來就被輪次判定略過,多的欄位只是附加。 |
| `design-loop`(處置閘第五步,[SN] 條款須 [綁定測試:有]) | 不影響。S1–S11 各綁一支確實存在的測試。 |
| `reversibility-governance-ledger` | 不影響。治理帳仍是只追加;`spec-gate-green` 是新的追加事件。不可逆性(紅燈版提交即入歷史)計劃已寫。 |
| `lumos-cli-lifecycle`(re-inject 不動 sentinel 外內容) | 不影響。沒碰安裝或注入。 |
| 其餘「只列名」節點 | 未逐篇讀,以相關子集全綠(`spec_gate` 320 項、`gov_` 231 項、`lint_new` 82 項、`tq_guard` 256 項)作間接佐證。 |

## S1–S11 與「做法一/二」逐條核對

- **S1**:大致照寫。差異有 F1(跨平台同名靜默丟掉)、F3(5 MB 以原文量)、F6(原因被擠掉)。「同一支測試綁兩條條款只一列」「同一條款一紅一綠只存紅的」「再跑一次內容相同不重存」「判紅後檔案被改不存」都對,也都有測試。
- **S2**:照寫。終點無斷言時 `_tg_rb_chain` 早退,只剩 `tq/no-assertion` 一條。expected 與被測呼叫同時改不列,是明文的天花板。
- **S3**:實作照寫(行序、無 `ts` 比較);測試抓不到(F2)。
- **S4**:各子條件都在。「改動清單新增的紅燈版檔沒有留痕指到」用 `st == "A"` 判,被 `-M` 判成改名(R)的新檔不在偵測內,罕見。
- **S5**:搬家、多載、整檔先加後刪、分岔點已有都對,且有測試。「紅燈版的測試所在檔在分岔點已有同函式鍵」先於查找判斷。
- **S6**:照寫。判綠事件進版控帳(不在 `_GOV_LOCAL_PAIRS`),補跑步驟多一句也有。「只看本分支」靠分岔點相減,實測有效,但沒有測試(F8)。
- **S7**:改動清單觸發條件、空樹起點、讀終點不讀工作目錄(S10)、`_gov_rows_delta` 與舊 `_residual_ask_rows_delta` 語意一致(`keep(None)` 與舊的「讀不出當成是」同義)。
- **S8**:程式未動該路徑,測試是回歸釘(F8)。
- **S9**:指紋含 token、子規則與子候選 key,放一條不放掉另一條;放分岔點那條不放掉紅燈版這條。
- **S10**:`_tg_rb_doc` 與 `_tg_rb_load` 只用 `head:<path>`,不讀工作目錄;`reads_tip` 的暫存區與工作目錄換壞檔那段釘得住。
- **S11**:`_BOOKKEEPING_DIRS` 已加。
- **做法二補充**:`(None, err)` 在 `_tg_analyze`、`cmd_test_guard`(rc 2)、`_lint_new_guard`(寫入 `g["error"]`)三處都接得住,沒有漏。「中間份紅燈版壞掉」會列 `unreadable`,其餘紅燈版仍照鏈比。

最嚴重等級 major,blocking 共 2 條(F1、F2)。

主要相關檔案:
- `/Users/enzo/harness/lumos-spec-snapshot/scripts/lumos`
- `/Users/enzo/harness/lumos-spec-snapshot/scripts/test_lumos.py`
- 重現腳本都在 `/tmp/lumos-seat-work/code-規格閘紅燈測試快照/單reviewer-sonnet/exp/` 與 `mut/`,收貨後由編排者刪。
