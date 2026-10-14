severity: major

**Finding 1:有適用題的表態核對在沒給 deadline 時會崩**

severity: major
blocking: 是 — `_dispositions_verdict` 的 `deadline` 預設是 None,這次把 None 的判斷拿掉,現有測試實跑變紅。
引句:「-            if deadline is not None and _time.monotonic() > deadline:」

問題:簽名仍是 `deadline=None`,`_disp_record_for` 也照舊把 None 原樣傳回,所以 None 是合法輸入。修補把守衛拿掉後,逐題核對迴圈第一次比較就是 `float > None`。這個改動跟本次修補的主題無關,屬於順手清理,但弄壞了既有行為。唯一的正式呼叫端(`_codeloop_guard_verdict` 那段)有傳 deadline,所以線上推送路徑沒事。

具體失敗情境:
- 任何不帶 deadline、而且有適用題(`applicable` 為真)的直接呼叫,都會丟 `TypeError: '>' not supported between instances of 'float' and 'NoneType'`。
- 我在乾淨 clone 跑 `python3.14 scripts/test_lumos.py -k contract_evidence`,結果 `t_contract_evidence_warn_only EXCEPTION: '>' not supported between instances of 'float' and 'NoneType'`,2 passed、1 failed。
- `-k disposition` 全綠,因為那一批沒碰到這條路。作者若只挑名字相近的子集跑,抓不到這個紅燈。
- 修法:還原 `deadline is not None and`,或在函式開頭把 None 換成 `float("inf")`。

佐證:
- `scripts/lumos:51464`(簽名)
- `scripts/lumos:51579`(被改的比較)
- `scripts/lumos:51458`(`_disp_record_for` 保留 None)
- `scripts/test_lumos.py:78756`(沒帶 deadline 的呼叫)

**Finding 2:spec-freeze 的 `--out` 限制讓跨工作樹用法只能寫進計劃所在的工作樹**

severity: minor
blocking: 否 — 有替代做法(複製快照),也是修補故意收緊的,不弄壞既有測試。
引句:「+    if not segs or any(sg.lower() == ".git" for sg in segs):」

問題:`--out` 現在必須落在「執行 spec-freeze 那個工作樹」底下。spec-freeze 本來就是為「計劃在別的工作樹」設計的。

具體失敗情境:
- 實測:在 linked worktree `wt` 跑 `spec-freeze … --out ../r/gov/cross.md`(指向會談 repo 的 `governance/review-reports/<編號>/`)得到 `out_outside_repo`。
- 要成功只能寫進計劃所在的工作樹,`git status` 會多出 `?? gov/`。那個工作樹可能是別的會談的;全域規則要求不碰別人的未提交改動,記憶也記過別人的未追蹤檔會害 pre-push 紅。
- 之前寫 `/tmp/<編號>-rN.md` 或會談 repo 的卷證目錄都行,現在不行。
- `skills/lumos-design-loop/SKILL.md:20` 還寫「複製計劃筆記到工作副本 `/tmp/<編號>-rN.md`」。第 3 步和 templates 只說 `--out` 只收計劃所在 repo,沒說快照之後要自己複製到卷證目錄。
- 建議在文件補一句「寫在計劃所在工作樹後自行複製(位元組相同)並刪掉原檔」,或允許指向同一個物件庫的其他工作樹。

佐證:
- `scripts/lumos:49702`(`_spec_freeze_out_path`)
- `skills/lumos-design-loop/SKILL.md:20`
- `skills/lumos-design-loop/SKILL.md:26`

**Finding 3:入口改環境變數是行程層級,會漏進行程內呼叫 `main()` 的呼叫者和被叫起的子程式**

severity: minor
blocking: 否 — 現有測試沒有依賴這些變數,全綠。
引句:「+    os.environ["GIT_NO_REPLACE_OBJECTS"] = "1"」

問題:`main()` 直接改 `os.environ`,而 `scripts/test_lumos.py` 有十幾處行程內 `m.main()`(例如 8366、15879、16502 行),設定因此殘留在整個測試行程。

具體失敗情境:
- 之後同行程的測試用 `git replace` 或 grafts 造情境,會被默默改掉。新測試已自備 `_lr_clean_git_env` 來避開,但舊測試和未來測試沒有這個保護。
- `GIT_EXTERNAL_DIFF` 和 `GIT_DIFF_OPTS` 是永久移除。lumos 若叫起專案自己的測試或配方子行程,這幾個變數也被清掉。
- 修法:只在 `_lens_git` 和各 `subprocess` 的 env 注入,或在 `main()` 結尾還原;至少在筆記寫明這是行程層級副作用。
- 我實測 `GIT_GRAFT_FILE=/dev/null/lumos-no-grafts` 在 Apple git 2.39 下沒有警告,git 照常運作。

佐證:
- `scripts/lumos:53070`
- `scripts/lumos:53071`
- `scripts/test_lumos.py:43534`

**Finding 4:提交寫法的「計劃來源」行,路徑稍特殊就整段被替換**

severity: minor
blocking: 否 — 只影響顯示,不影響讀取。
引句:「+    shown_rel = f" {rd['rel']}" if _LENS_SPEC_NODE_NAME_RE.fullmatch(rd["rel"]) else "(路徑含不收的字元)"」

問題:`_LENS_SPEC_NODE_NAME_RE` 是節點名用的,限制 1 到 80 字,而且不含全形標點。

具體失敗情境:
- 計劃檔名含全形括號(例如 `…(第二版)_計劃.md`),或整條路徑超過 80 字,來源行就印「路徑含不收的字元」。我實測全形括號那條回 False。
- 「席位對得上 spec-freeze 那行」的用途因此失效,而且「含不收的字元」在長路徑上是誤導。
- 一般路徑(59 字)正常。

佐證:`scripts/lumos:49310` 一帶的 `_lens_spec_notes`。

已讀,無 finding:
- `_load_hook_file`:handoff 的三種錯誤句與模組名逐字不變,`-k handoff` 55 項全綠;spec-freeze 載入關了 bytecode,`.py` 副檔名也符合 `spec_from_file_location`。
- `_mark_event` 放寬為 `Exception`:`_hookevent.mark` 只設旗標,沒有依賴呼叫位置的推斷;三個內嵌區塊換成它語意相同,`-k hook_event` 18 項全綠。
- `_lens_git` 多接 `ValueError`:約 100 個呼叫點本來就要處理逾時和 `OSError` 造成的 `None`,含 NUL 的參數現在走同一條路,沒看到把 None 當成通過的新路徑。
- `_SPEC_FAIL_CODES` 由推導得到:`not_git` 保留在其中,測試已用 set 比較,`-k dispatch_lens` 270 項全綠。
- 刪掉 `_spec_commit_has`:全 repo grep 已無其他使用者。
- `_nodehome_landing_sizes`、`_lens_spec_code_files`、`_lens_spec_linked` 的回傳元數變了,但呼叫端只有 `cmd_dispatch_lens_spec` 一處,而且都已同步修改。
- `_write_bytes_atomic` 抽出:`-k write_lf` 5 項全綠。
- spec-freeze 的 `--out`:相對路徑、經 `/tmp` 與 `/private/tmp` 符號連結的絕對路徑、repo 外路徑都照預期,`-k spec_freeze` 44 項全綠。

清理:我的臨時 clone 和實驗目錄已刪,紅燈留下的 `gctl-run-__1o14ky` 也已刪。

最高等級 major,blocking 1 條。
