severity: major

## F1 exam 的 current_state 題缺 note 欄位時,直接崩潰而不是略過

severity: major
blocking: 是 — 考卷是外部輸入(人寫或產生),同函式對其他缺欄位情況(缺 line、缺 invalidating_commits)都走 `.get()` 安全略過,唯獨這一分支用中括號直接取值,崩潰會讓整份考卷的重放全部中止,而不是照設計「略過:<原因>」那一題。
引句:「hit = any(f["path"] == q["note"] and f["line"] == line for f in _drift_state_findings(tenv))」

1. `_drift_exam_one`(r1-snapshot-code.patch 第 1223 行起)裡,`current_state` 分支直接用 `q["note"]`,而同一支函式其他地方(`note = q.get("note_at_event") or q.get("note")`、`line = q.get("line")`)全部用 `.get()`。
2. 只要當下的圖譜狀態「有至少一筆漂移發現」(`_drift_state_findings(tenv)` 非空),genexpr 就會真的求值到 `q["note"]`;考卷裡漏寫 `note` 的 `current_state` 題會讓整支 `lumos drift exam` 直接丟 `KeyError: 'note'`、rc 非 0 且沒有印出「擋下」之類的可讀訊息,其餘題目(包含正確寫的)也一起沒結果。
3. 已用乾淨臨時 repo 重現(不是凍結 diff 裡的材料,是我自己建的 mktemp repo,只用來跑指令,沒有碰任何審查用 repo):
   - 建一個含一篇 `type: project, status: done` 與一篇連到它的開著 Issue 的 repo(製造出至少一筆 c2 發現)。
   - `exam.json`: `[{"id": "MISSING_NOTE", "exam_event": "current_state", "line": 3}]`(缺 `note`)。
   - 執行 `python3 scripts/lumos drift exam <exam.json> --repo <repo>`,結果:
     ```
     File ".../scripts/lumos", line 25646, in _drift_exam_one
         hit = any(f["path"] == q["note"] and f["line"] == line for f in _drift_state_findings(tenv))
                                ~^^^^^^^^
     KeyError: 'note'
     ```
   - 若圖譜當下沒有任何發現(genexpr 空跑),同一份缺欄位考卷反而不會崩(`any()` 對空 iterable 直接短路),掩蓋了這個坑——這正是邊界輸入容易被漏測的地方:平時小規模試跑通常剛好沒有發現、看起來沒事。

## F2 `_drift_exam_load` 對考卷整體形狀沒做防呆,非「清單包字典」就崩潰

severity: major
blocking: 是 — 函式自己的docstring 承諾「讀不了或有不認得的考法回 None(已印原因)」,但只防住了 JSON 語法錯誤與 exam_event 不認得兩種情況,考卷整體形狀不對時反而是未捕捉的例外,行為跟函式自己宣稱的合約不一致。
引句:「bad = sorted({str(q.get("exam_event")) for q in qs if q.get("exam_event") not in known})」

1. `_drift_exam_load`(r1-snapshot-code.patch,`cmd_drift_exam` 之後那支)只處理了兩種壞輸入:JSON 語法錯(`json.loads` 拋例外,有擋)、`exam_event` 不認得(有擋);沒有檢查 `qs` 本身是不是「清單包字典」這個形狀。
2. 頂層 JSON 是純量(例如數字)時,`for q in qs` 對不可疊代物件直接 `TypeError: 'int' object is not iterable`;頂層是「清單但元素不是物件」(例如字串陣列)時,`q.get("exam_event")` 對字串呼叫 `.get` 直接 `AttributeError: 'str' object has no attribute 'get'`。兩種都會讓整個 `drift exam` 指令印出 Python traceback 而不是「擋下:…」。
3. 已用乾淨臨時 repo 重現(同上,自建 mktemp repo,只用來跑指令):
   - `echo '42' > exam.json` → `python3 scripts/lumos drift exam exam.json --repo <repo>`:
     ```
     File ".../scripts/lumos", line 25735, in _drift_exam_load
         bad = sorted({str(q.get("exam_event")) for q in qs if q.get("exam_event") not in known})
                                                        ^^
     TypeError: 'int' object is not iterable
     ```
   - `echo '["a","b"]' > exam.json` → 同一支指令:
     ```
     File ".../scripts/lumos", line 25735, in _drift_exam_load
         bad = sorted({str(q.get("exam_event")) for q in qs if q.get("exam_event") not in known})
                                                              ^^^^^
     AttributeError: 'str' object has no attribute 'get'
     ```
4. `{"items": 42}`、`{"items": ["a"]}` 這兩種帶 `items` 鍵但值不對的字典也是同一條路,理由相同,不重複列。`{}`(沒有 `items` 鍵)則安全(`.get("items") or []` 落回空清單),已看,無 finding。

## 其餘邊界輸入:逐項已看,無 finding(理由與重現方式)

1. **空圖譜 / 空 texts**:`_drift_tree_env` 在 `paths=[]` 時 `blobs=[]`(不是 None),`Env.from_texts(..., {})` 建出空 `notes` dict;`_drift_state_findings`/`build_index`/`make_resolver` 對空 dict 都能跑。已在 clone-ns 對真實圖譜跑 `drift scan --at HEAD`,以及對只有兩篇筆記的最小 repo 跑 `drift exam --history 3`,兩次都 rc0、沒有例外。

2. **沒有開頭欄位 / 開頭欄位沒收尾的筆記**:`_drift_fm_end`(新函式)在 `lines[0].strip() != "---"` 或找不到收尾 `---` 時回 `0`,`_drift_field_line`/`_drift_set_status_text` 對 `fm_end==0` 都有 `if not e: return text` 這類早退,不會崩;真正會寫檔的 `guard settle`/`guard plan`/`guard abandon` 仍然经过既有的 `load_raw_for_edit`(`file: \`scripts/lumos:14332\``),對同樣兩種壞筆記主動擋下並印清楚原因(「這篇筆記開頭沒有欄位區塊」「開頭欄位區塊沒收尾」),這條路沒被這次改動動到。已在自建 repo 放一篇完全沒有開頭欄位、一篇開頭欄位沒收尾的筆記,對 vault 跑 `drift scan`,rc0、無例外(輸出全 0 筆,符合預期——這兩篇筆記沒有 type/status,自然不會產生任何一種發現)。

3. **CRLF / BOM 筆記**:讀側(`env_text`/`_drift_tree_env`)一律用 `utf-8-sig` decode,BOM 天然被吃掉;CRLF 情況下 `text.split("\n")` 會在每行留下尾端 `\r`,但用到逐行內容的比對(`_guard_planned_prose`、`_guard_formal_line`、`INVARIANT_RE.match`)都先 `.strip()`,`\r` 不影響比對結果。寫側(`guard settle` 等)仍走 `load_raw_for_edit`(`file: \`scripts/lumos:14338\``),BOM/CRLF 直接擋下並印修法,這次改動沒有繞過這條既有防線。抑噪原則下沒有具體翻紅場景,不進一步展開。

4. **中文與含空白的檔名**:新函式一律吃 `env`/`Env.from_texts` 已解析好的 `rel`(相對路徑字串),沒有另外用位元組長度或 ASCII 假設去切檔名(唯一新增的檔名相關運算是 `_note_from_text` 的 `rel.rsplit("/", 1)[-1][:-3]` 這種去掉尾端 3 個字元的寫法,對中文、空白字元都是安全的字元級切法,不是位元組切法)。測試材料本身也已經在用中文檔名與資料夾(`Projects/退款_計劃`、`Verification/長檔名守衛.md`),沒有另外找到會炸的具體場景。

5. **guards 欄是字串不是清單**:`_guard_home_of_fields`(`isinstance(g, list) and g` 才取 `g[0]`,否則整個當字串處理)在 `_drift_state_findings`/`_drift_c3_hit`/`_drift_guard_findings` 都是唯一入口,兩種形狀都覆蓋到,沿用既有寫法。

6. **plan_refs 寫成單值或空 / valid_under 是清單**:兩處都經過既有的 `as_list()`(`file: \`scripts/lumos:399\``),`None`→`[]`、純量→單元素清單、清單→原樣轉字串,`_drift_c3_hit`、c4 的 `valid_under` 判斷都吃得下這三種形狀。

7. **家筆記找不到**:`_drift_guard_findings` 算 c5 時 `home` 解析不到就整段跳過(不產生 c5 發現,不崩);真正會寫檔的 `_guard_settle_locked` 已有明確擋下訊息「守衛節點指名的功能節點 … 找不到」,這次改動只是把原本內嵌的邏輯搬進 `_guard_settle_home` 沒有改變行為。

8. **ack 行號超出範圍(含 0 與負數)**:`cmd_drift_ack` 有 `if not (1 <= line <= len(lines)) or not lines[line - 1].strip(): 擋下`,已在自建 repo 對一篇 5 行筆記分別跑 `drift ack ... 999`、`... 0`、`... -1`,三次都印出清楚的「沒有第 N 行」並 rc2,沒有例外。

9. **範圍終點全 0(刪分支)/ 第一次推送沒有起點**:兩者都吃既有共用的 `_note_audit_resolve`/`_lens_push_base`,這次改動只是多傳 `gate`/`mark` 參數,沒有改判斷邏輯本身。已在自建 repo 分別跑 `drift check --diff <HEAD>..0000...000` 與 `drift check --diff 0000...000..<HEAD>`,前者印「範圍終點是全 0(刪除分支),沒有要審的東西」rc0,後者印「新分支首推:找不到主線,從空樹算」rc0,均無例外。

10. **淺層 clone**:同樣走 `_note_audit_resolve` 裡既有的 `git rev-parse --is-shallow-repository` 分支(這次改動沒有碰),沒有另外重現,信心來自邏輯共用且未被改動,不是純臆測。

11. **`--history` 比提交數大 / 為 0**:`git rev-list --max-count=N` 本身在 N 超過實際提交數時只會回傳實際有的提交、不報錯,`_drift_exam_history` 對每個 `par=None`(沒有上一版,例如根提交)的情況也用 `continue` 跳過,不會崩;已用 `--history 3`(repo 只有 1 個提交)實際跑過,rc0 正常印出「最近 3 個主線提交裡,有要處理的 0 個」。`--history 0` 因為 Python 的 `if not args.dr_history` 把 0 當成「沒給」,會退回要求給考卷檔——這是可預期的行為變形(0 個提交沒有意義),不是崩潰,抑噪原則下不單獨列 finding。

12. **exam 的 `--at` 找不到**:`cmd_drift_exam` 一開始就 `at_sha = _lens_full_sha(...); if at_sha is None: 擋下`,順序在讀考卷檔之前,已用程式碼路徑確認(未另外重跑,邏輯直接可讀)。

## 圖譜鏡頭:LUMOS-IMPACT 逐節點判讀(3ba5eef5..b9ca00bb)

用 `lumos impact --diff 3ba5eef5f17b5ffe8700bb9904966145ac2eea0c..b9ca00bbda322504c612f9301afe9c903086cabb`(在 clone-ns 唯讀跑)拉出的固定席 27 篇 + top 8,逐篇核對這次 diff 有沒有動到它宣稱的行為:

- **Issues/canary-record未落盤事件.md**(1.00,⚠事故):這篇的合約是「append 型帳本一律要走 `_jsonl_append_verified`(寫後獨立重開檔讀回驗證)」。`cmd_drift_ack` 寫 `governance/drift-acks.jsonl` 時確實呼叫 `_jsonl_append_verified(fp, rec, "id", token)`(patch 內可見),**遵守**而非破壞這條事故留下的規則。不影響/合規。
- **Systems/guard-kill.md**(0.88,★家★,兩條 ★INVARIANT★):兩條合約都是 `guard kill`(rc 優先序、`--json` 輸出純淨)的行為,這次 diff 完全沒有動 `cmd_guard_kill`/`_kill_run` 那條路徑,只動了 `guard plan`/`guard settle`/`guard abandon` 三支跟 kill 不相干的指令。不影響——這篇筆記本身也已經在這次 diff 裡新增了對應 settle/lock 改動的 WHY/PITFALL 說明(它是這次要寫回的「家」,不是被動波及的合約)。
- **Systems/lumos-cli-read.md**(0.82,★家★):唯一相關的 ★INVARIANT★ 是 `search` 預設排除 `status=superseded` 節點,跟 drift 無關;doctor 檢查字母清單(C/D/E1-E3/…)只是 KEY 不是 ★INVARIANT★,而且這行本身已經自承「以現碼為準」、不是固定清單的硬承諾,新增 Check Z 不算破壞。不影響。
- **Systems/授權與歸屬.md**(hop1,兩條 ★INVARIANT★):管的是 LICENSE/SPDX 標頭與 `_vendor_toolchain` 白名單,這次 diff 沒有新增檔案到 vendored 清單、沒有動 `scripts/lumos` 檔頭。不影響。
- **Systems/測試假綠形態.md**(hop1,★INVARIANT★):要求「還原翻紅釘」的測試要配前置斷言證明現場成立。新增測試(`t_guard_settle_rewrites_planned_prose` 等)都有「①前置:…」這種現場斷言在翻紅釘敘述之前,樣式對得上這條慣例。不影響/合規。
- **Systems/reversibility-governance-ledger.md**(0.64):這次只多一行 WHY 說明 `drift-check` 閘名放行不寫帳,以及在 `_KNOWN_GATES` 常數裡加 `"drift-check"`,沒有動 `extract_reversibility`/rollback/guard 那組 ★INVARIANT★ 邏輯本身(這篇的 ★INVARIANT★ 級合約都在 `Systems/reversibility-governance-ledger.md` 以外的 rollback/guard 標記機制,這篇是彙整器)。不影響。
- **Systems/存量漂移守衛.md**(0.73,hop1):這篇正是這次 diff 新增的家節點,內容(五種檢查共用一支、settle 改寫共用一支、doctor 只在接線後印開關提醒、考試誤報只算題目外的發現)跟我讀到的程式碼行為一致,沒有發現筆記講的跟程式碼對不上的地方。不影響/一致。
- **Systems/筆記內容審.md**(top,未列在上面前 27 但被牽動):`_note_audit_closed_plans` 被抽成共用的 `_notes_status_flipped`,這篇筆記已經在這次 diff 裡補了一行 WHY 說明「改這兩段要一起跑 `-k note_audit` 與 `-k drift`」,程式碼裡 `_note_audit_closed_plans` 呼叫 `_notes_status_flipped` 時傳入跟原本邏輯等價的 `tip_ok`/`flip` 判斷式(`ty == "project" and st in _NOTE_AUDIT_CLOSED`、`(a not in _NOTE_AUDIT_CLOSED) and (b in _NOTE_AUDIT_CLOSED)`),跟改之前的行為逐字對得上,是安全的抽取重構。不影響。
- 其餘(loop-convergence-recording、design-loop、pitfalls-code-loop、lumos-cli-lifecycle、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、doctor-irreversible-hint、check-r-guard、cochange-guard、lumos-refcheck、bound-tests-gate、canary-audit、slim-*、雙向門放行_計劃、規格落成可驗收條件_計劃、逃逸自動記_計劃、core-invariant-baseline、judge-severity-gate 等):在清單裡出現只是因為它們「家」在 `scripts/lumos`(整支檔案一改,所有以它為家的節點都會被 impact 掃到),逐篇核對後這次 diff 實際改到的函式(`load_vault`/`_note_from_text`/`Env.from_texts`/`env_text`、guard plan/settle/abandon 的鎖與預告句改寫、`_note_audit_resolve`/`_notes_status_flipped` 參數化、`cmd_set` 的 status 連帶待辦掛鉤、新增 `drift` 家族與 doctor Check Z)都不在這些節點宣稱的合約範圍內,沒有共用函式、沒有共用常數被動到。不影響——判斷依據是純粹的「這次改的函式集合」與「這些節點列出的 ★INVARIANT★/RULE 覆蓋的函式集合」沒有交集,逐篇都查過標題與合約行,沒有再展開列每一篇的推理過程以免報告過長。

## 總結

最高 major,blocking 共 2 條(F1、F2,兩者都在 `lumos drift exam` 讀考卷的路徑上,對缺欄位/形狀不對的考卷檔沒有做到函式自己承諾的「讀不了就回 None、印原因」)。
