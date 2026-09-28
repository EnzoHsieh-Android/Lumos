severity: major

## F1 strict 模式仍把單筆歷史解碼失敗吞成普通狀態

severity: major  
blocking: 是 — 會讓本應 fail-closed 的 c1 推送閘漏掉狀態翻轉

引句:「strict 時批次讀失敗、改名對照失敗也回 None(不能當成沒有狀態翻轉,代碼審 r2、r3 外家席),不嚴格時照舊當成讀不到。」

file: `scripts/lumos:24556`

1. 輸入：守衛紀錄起點為 `pending`，中間版本不是 UTF-8，終點為可讀的 `pass` 且仍保留預告句。
2. 批次讀取本身成功時，strict 只檢查整批結果是否為 `None`；單一壞 blob 經 `_note_audit_status_of` 變成狀態 `None`。
3. 序列成為 `pending → None → pass`，找不到相鄰的 `pending → pass`；`_notes_status_flipped` 回空清單，c1 不進 `must`。
4. 最小重現：`python3 -B -c 'import runpy; m=runpy.run_path("scripts/lumos",run_name="review"); g=m["_note_status_seq"].__globals__; p="docs/kg-knowledge/Verification/G.md"; a="a"*40; b="b"*40; pb=b"---\nstatus: pass\n---\n"; qb=b"---\nstatus: pending\n---\n"; g["_ns_git"]=lambda root,*args:(a+"\0\n"+p+"\0"+b+"\0\n"+p+"\0").encode() if "--follow" in args else bytes(); g["_nodehome_cat_blobs"]=lambda root,specs,**kw:[pb,bytes([255])] if len(specs)==2 else [qb]; s=m["_note_status_seq"](".","BASE","TIP","docs/kg-knowledge",p,strict=True); print(s, any(x=="pending" and y=="pass" for x,y in zip(s,s[1:])))'`
   輸出：`['pending', None, 'pass'] False`

## F2 空 wikilink 沒有落進 c3 的無效項目清單

severity: minor  
blocking: 否 — c3 只列出不擋，影響是錯誤待辦與掃描噪音

引句:「每一項都要有落點:只要有一項落在解不出(ghosts)、猜不準(ambiguous)或不是連結(scalars),就不算」

file: `scripts/lumos:25288`

1. 輸入：`plan_refs` 同時包含 `[[Projects/P]]` 與 `[[ ]]`，而 `Projects/P` 已收尾。
2. `build_typed_index` 對空 target 直接跳過，沒有放進 `ghosts`、`ambiguous` 或 `scalars`。
3. `_drift_c3_hit` 因此仍回 `['Projects/P.md']`，把明明有一項沒有落點的驗證紀錄列為 c3；這違反本 hunk 宣告的逐項判準。

## F3 doctor 的新條件仍與計劃硬條款及函式說明相反

severity: minor  
blocking: 否 — 執行方向明確，但規格與說明會讓後續驗收得出相反答案

引句:「開關不是 block 時講一聲——只在專案自己寫了開關、或已經接線時」

file: `scripts/lumos:25804`

file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:60`

file: `docs/lumos-toolchain-knowledge/Projects/存量漂移防線_計劃.md:144`

1. 沒寫設定、沒接線時，預設 gate 是 `warn`；新程式與新增測試要求 doctor 靜默。
2. 同一函式 docstring 仍寫「開關不是 block 就講、不管接線沒」，計劃做法與 `[S14]` 也仍要求 gate 非 block 時印一行。
3. 計劃、函式說明及測試必須改成同一判準。

已看,無 finding：guard 正式行使用 `INV_TAG_RE`、測試清單拆分、預告索引清單及 half-done 補完。

已看,無 finding：非 strict 的筆記內容審退回批次讀取與改名對照失敗不拖垮整道內容審。

已看,無 finding：unreadable 筆記在磁碟與提交樹共用 `Note.lint`、scan 不寫治理帳。

已看,無 finding：每次 git 呼叫前的預算檢查、doctor 死參數移除及相關測試 hunk。

已看,無 finding：指定 rtb 考卷結果為擋到 3、點到 3、漏 0，與計劃紀錄一致。

驗證限制：完整 `-k drift_code_review_r3_regressions` 在進入測試前因唯讀沙盒沒有可寫暫存目錄而終止；F1 已用不落檔函式級命令當場翻紅。

總結：最嚴重等級 major，blocking 共 1 條。