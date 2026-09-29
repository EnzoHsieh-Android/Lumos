severity: major

## F1 Python 字串範例被當成真實符號定義

severity: major

blocking: 是 — 會誤擋只新增文件範例的推送，並讓日後真正新增符號時因起點已成立而漏擋。

引句:「return re.compile(rf"^(?:[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+{n}\b|{n}[ \t]*(?::[^=\n]*)?=(?!=))", re.M)」

1. 輸入只有 Python 三引號字串中的 `def launch()`，沒有任何真實函式。
2. 正則逐行掃原始文字，仍把 `when-symbol:launch` 判成成立；這次先誤擋，未來真正定義 `launch` 時又因起點早已成立而不列。
3. 重現：`python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review"); C=m["_ProbeTree"]; t=C.__new__(C); t.ok=True; sample="DOC = \"\"\"\\ndef launch():\\n    pass\\n\"\"\"\\n"; t.corpus=lambda test:{"src/a.py":sample}; print("when-symbol launch =",t.one("symbol","launch"))'`
4. 輸出：`when-symbol launch = True`

file: `scripts/lumos:25769`

## F2 讀不懂的 status 目標被當成條件不成立

severity: major

blocking: 是 — 規格要求判不了時擋下，但此路徑把未知降成 false 而靜默放行。

引句:「return n is not None and _drift_str(n, "status") in {x.strip() for x in vals.split("|")}」

1. 新增一條 `when-status`，指向一篇既存但非 UTF-8、且本次未改動的筆記。
2. 頂層 unreadable 檢查只看本次 touched 筆記；條件目標未 touched，不會進 unknown。
3. `_ProbeTree.one` 找得到該 Note，卻直接以空 status 回 `False`，所以新條件不擋也不報判不了。
4. 重現：`python3 -c 'import runpy; from pathlib import Path; m=runpy.run_path("scripts/lumos",run_name="review"); env=m["Env"].from_texts(Path("."),{},unreadable=["Projects/P.md"]); C=m["_ProbeTree"]; t=C.__new__(C); t.ok=True; t.env=env; print("unreadable=",m["_note_unreadable"](env.notes["Projects/P.md"])); print("status_verdict=",t.one("status","Projects/P=done"))'`
5. 輸出：`unreadable= True`、`status_verdict= False`；正確結果應是 `None`。

file: `scripts/lumos:25822`

## F3 合法的點段相對路徑永遠不會成立

severity: major

blocking: 是 — 條件通過語法檢查，但實際檔案出現時候選篩選與判定都對不上，形成永久漏擋。

引句:「return (not p) or p.startswith("/") or ".." in p.split("/")」

1. `[when-file:./src/a.py]` 是 repo 內相對路徑，且現有驗證只禁止絕對路徑與 `..`，因此判為合法。
2. Git 路徑集合保存成 `src/a.py`；判定和候選篩選都直接用未正規化的 `./src/a.py` 比較。
3. 舊條件遇到新增檔案不會成為候選；新寫條件遇到已存在檔案也會判 false。
4. 重現：`python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review"); C=m["_ProbeTree"]; t=C.__new__(C); t.ok=True; t.files={"src/a.py"}; print("syntax_error=",m["_probe_value_err"]("file","./src/a.py")); print("file_exists_verdict=",t.one("file","./src/a.py"))'`
5. 輸出：`syntax_error= None`、`file_exists_verdict= False`。

file: `scripts/lumos:25699`

file: `scripts/lumos:25820`

## F4 範圍模式會把同文的舊欄位誤認成新行

severity: major

blocking: 是 — 合法的新正文行會因既存、同文字的開頭欄位被硬擋，違反舊行不管的規格。

引句:「if not ln.strip() or (regs[i - 1] == "other" and not keep_other):」

1. 起點的 `valid_under` 多行值已有一條條件文字；終點只在正文新增完全相同的合法 REVISIT 行。
2. 範圍模式用「去空白後的文字集合」辨認新增行，無法分辨出現位置。
3. `keep_other=True` 後，舊的 `valid_under` 行也被收進新行清單，隨即報「條件寫在不評估的地方」；提交前 staged 模式不報、推送範圍模式卻會擋。
4. 重現：`python3 -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review"); f=m["_notelines_new"]; g=f.__globals__; p="docs/kg-knowledge/Systems/A.md"; line="REVISIT:[when-file:x.py][by:2099-01-01] 待辦"; text="---\\ntype: system\\nstatus: doing\\nvalid_under: |-\\n  "+line+"\\n---\\n# A\\n"+line+"\\n"; g["_nodehome_golive"]=lambda *a:None; g["_notelines_range_added"]=lambda *a,**k:({p:{line}},[p],{}); rows=f(".",False,"B","T","docs/kg-knowledge",reader=lambda _p:text.encode(),mark="x",keep_other=True)[0][0][2]; print([(n,r,[v[0] for v in m["_ns_revisit_violations"](t,r,True)]) for n,t,r in rows])'`
5. 輸出：`[(5, 'other', ['條件寫在不評估的地方']), (8, 'body', [])]`；第 5 行其實是舊行。

file: `scripts/lumos:24008`

file: `scripts/lumos:24253`

## F5 工作目錄 scan 實際讀的是 index

severity: major

blocking: 是 — 修復清單會漏掉未追蹤或未 staged 的現況，亦會把工作目錄已刪除的檔案當成仍存在。

引句:「lst = _nodehome_list(root, "index" if where == "disk" else where)」

1. `lumos drift scan` 宣稱預設掃工作目錄，筆記確實來自磁碟，但 `_ProbeTree("disk")` 的路徑集合取自 Git index。
2. 未追蹤檔已存在於磁碟時，`when-file` 仍回 false；未 staged 刪除則會反向誤判 true。
3. 重現：`python3 -c 'import runpy,pathlib; m=runpy.run_path("scripts/lumos",run_name="review"); p="governance/review-reports/code-存量漂移防線乙/r1-snapshot.patch"; t=m["_ProbeTree"](pathlib.Path("."),"disk",None); print("disk_exists=",pathlib.Path(p).is_file()); print("scan_when_file=",t.one("file",p))'`
4. 輸出：`disk_exists= True`、`scan_when_file= False`。

file: `scripts/lumos:25787`

file: `scripts/lumos:26227`

## F6 scan 的預算介面與總預算都未實作

severity: major

blocking: 是 — 設計明定的修復指令無法執行，且全圖譜評估沒有 60 秒總預算。

引句:「pfound, probs = _drift_probe_scan(tenv, _ProbeTree(root, sha or "disk", tenv))」

1. 規格公開 `lumos drift scan ... [--budget <秒>]`，預設總預算 60 秒並可放寬。
2. CLI 沒有 `--budget`，`cmd_drift_scan` 也沒有 deadline 參數；傳給 `_ProbeTree` 的 deadline 永遠是 `None`。
3. 重現：`python3 scripts/lumos drift scan --budget 1`
4. 輸出：`擋下:不認得這幾個參數:--budget 1。`，回傳碼 `2`。

file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:56`

file: `scripts/lumos:26210`

file: `scripts/lumos:35359`

## F7 probe 考試把不合法的改寫算成通過

severity: major

blocking: 是 — 乙的 5/5 驗收包含真實系統會由筆記形狀擋拒絕的輸入，無法證明有效文法能通過考試。

引句:「must, listed, unknown = _drift_check_core(root, par, c, vr, override=ov_tip, override_base=ov_base)」

1. 條件式回頭條件強制帶 `[by:]`，但正式改寫檔的 A7、B3、B4 都沒有期限。
2. `_drift_exam_probe` 未先走 `_probe_parse`/形狀驗證，直接注入記憶體並呼叫 check；check 為兼容舊行仍會評估缺期限條件，三題遂被算成「擋到」。
3. 解析重現輸出：`[('A7', None), ('B1', '2026-12-31'), ('B2', '2026-12-31'), ('B3', None), ('B4', None)]`。
4. 考試重現：`python3 scripts/lumos drift exam governance/eval/drift-exam/rtb-2026-09-28.json --repo <rtb-exam> --probes governance/eval/drift-exam/rtb-2026-09-28-probes.json --json`
5. 相關輸出：`[('A7', '擋到'), ('B3', '擋到'), ('B4', '擋到')]`。

file: `scripts/lumos:26350`

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:3`

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:15`

file: `governance/eval/drift-exam/rtb-2026-09-28-probes.json:19`

## F8 E5 與另外兩個消費者對雙反引號的可見性不同

severity: minor

blocking: 否 — 只會產生錯誤的 doctor 到期提醒，不會擋推送。

引句:「_kind5, _restv = _revisit_split(_pr5)」

1. 筆記中的 ``REVISIT:[when-file:x.py][by:2020-01-01] 範例`` 是行內程式碼，形狀擋與 `_probe_lines` 會用 `_strip_inline_markup` 排除。
2. E5 上游仍用只處理單反引號的 `_search_visible_lines`；雙反引號只剝掉兩端，內容反而留下，E5 會把範例報成到期。
3. 重現輸出：`E5_probe= REVISIT:[when-file:x.py][by:2020-01-01] 範例`、`E5_kind= cond`、`probe_lines= []`。

file: `scripts/lumos:2014`

file: `scripts/lumos:2017`

## F9 重複設定已收尾狀態仍宣稱條件是這次成立

severity: minor

blocking: 否 — 只多列錯誤的連帶待辦，但會讓冪等的 `lumos set ... done` 產生假事件。

引句:「and new_status in {x.strip() for x in v.partition("=")[2].split("|")}]」

1. `_drift_status_probe_followups` 只檢查新值，沒有比較舊 status。
2. 計劃本來就是 done，再設一次 done；或從 done 改成 superseded，而條件接受兩者時，仍輸出「因這次收尾成立」。
3. 重現輸出：`[('回頭條件', 'Issues/I.md', '第 6 行的 status 條件因這次收尾成立')]`，測試環境中的 `Projects/P.md` 起點已是 `status: done`。

file: `scripts/lumos:25514`

其餘未列 hunks，包括四鍵正常主路徑、AND 判定、改名對回、第二層條件式排除、doctor Z 計數及新增測試內容，已看,無 finding。

最嚴重 major，blocking 共 7 條。