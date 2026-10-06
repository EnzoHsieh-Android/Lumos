severity: minor

總評:結構大致對齊(留在 scripts/lumos 單檔、同層加判定輔助、有效性重用 `_codeloop_record_valid`、不碰既有讀帳函式、放寬只在條件齊時成立)。沒有跨層直呼、沒有另一套有效性判斷。以下三條是時間預算、讀帳細節與淺 clone 上跟鄰居不一致。

四問逐答:
1. 分層與依賴方向:一致。鄰居 `_codeloop_guard_verdict`(`scripts/lumos:46927`)先 `_codeloop_read`(`scripts/lumos:45504`)、再 `_codeloop_record_valid`(`scripts/lumos:46521`);表態在 `_dispositions_verdict`(`scripts/lumos:46756`)內讀 `_codeloop_read_dispositions`(`scripts/lumos:46486`)後驗有效。計劃把「合進來那側」做成被這兩處呼叫的共用輔助函式,方向相同,「回 None 附原因」也同 `_lens_push_base` 回 (值, 原因) 的做法。
2. 命名與錯誤處理:大方向對(放寬類的失敗照舊擋,不 fail-open;`_gate_failopen`(`scripts/lumos:46287`)是「放行」時才記帳,此處是放寬,語意相反,計劃選照舊擋合理)。細節見 F2、F3。
3. 第二種做法:新讀帳函式見 F1(可接受但要明講共用);未另起有效性判斷;時間預算見 F2。
4. 落點:合理。`Systems/pitfalls-code-loop` 的 about_code 列了 `scripts/lumos`,內容講 pitfalls 三模式與 code-loop 守衛,留痕判定本來就歸這裡;`related` 掛 bound-tests-gate 也不衝突。

## F1 新讀帳函式沒講明共用既有的帳本讀法與留痕種類篩選
severity: minor
blocking: 否
引句:「新寫一支讀帳函式,不改既有 `_codeloop_read`/`_codeloop_read_from_ledger`」
說明:既有 `_codeloop_read_from_ledger`(`scripts/lumos:45517`)與 `_codeloop_read_dispositions`(`scripts/lumos:46486`)都用 `_ledger_lines`(`scripts/lumos:12008`)讀 `docs/.governance-log.jsonl`,並有「只認 kind=passed/skipped、blocked/fail-open 絕不算留痕」的第二道防線(`scripts/lumos:45528` 附近的註解)與表態獨立 kind 的重建規則。計劃只說「任何分支的 pass/skip」,沒寫要沿用同一套 kind 篩選與行序規則,新函式若自己篩,就會多出第二套「哪些事件算留痕」。建議明寫:共用 `_ledger_lines` 與同一個 kind 判斷(最好抽成與 `_codeloop_read_from_ledger` 共用的內層),表態同理。⚠ 這條是「沒寫」而非「寫了不同」,是否算偏離交編排者。

## F2 時間預算與單次 git 逾時的接法跟鄰居不同(沒傳剩餘預算)
severity: minor
blocking: 否
引句:「整段給一個總預算(照表態閘既有的時間預算),超過就停、照舊擋並講原因」
說明:表態閘預算是 `_DISP_BUDGET`(`scripts/lumos:46314`)搭配 `deadline` 參數(`scripts/lumos:46756`、呼叫處 `scripts/lumos:47054`),單次 git 逾時是 `_disp_git_timeout()`(`scripts/lumos:46647`,預設 8 秒)。但計劃同時說有效性判斷用 `_codeloop_record_valid(紀錄, 第二個母)`,該函式(`scripts/lumos:46521`)不收 timeout/deadline;能收剩餘預算的是 `_codeloop_record_valid_ex(..., timeout=)`(`scripts/lumos:46538`,註解明寫「算背書時傳剩餘預算」,且回第三值「判不了」)。50 筆乘約 2 次 git、每次 8 秒,不傳剩餘預算就攔不住總預算。另 merge-tree、取樹要走哪個 git 輔助(`_sp.run`+`_disp_git_timeout` 或 `_lens_git`(`scripts/lumos:43821`,預設 timeout=20))計劃沒指定,兩者逾時預設不同。建議:改用 `_codeloop_record_valid_ex` 並每筆傳 `min(_disp_git_timeout(), 剩餘)`,「判不了(逾時)」一律照舊擋並講原因;merge-tree 同用 `_disp_git_timeout`。⚠ 請編排者確認要不要指定新輔助函式用哪個 git 呼叫入口。

## F3 淺 clone 沒被點名,只混在「git 出錯」裡
severity: minor
blocking: 否
引句:「git 出錯或逾時)→ 回 None 並附一句原因」
說明:既有做法把淺 clone 當成獨立的「判不了」情形:`_git_is_shallow`(`scripts/lumos:6016`)在 `_codeloop_missing_commit`(`scripts/lumos:46533` 附近)區分「淺 clone 找不到提交→判不了」與「完整歷史找不到→確定無效」,其他閘也各自寫「skipped-env / shallow clone」(`scripts/lumos:32144`、`scripts/lumos:32805`)。CI 的 checkout 常是淺的,第二個母可能不在本地;計劃的訊息清單(手改/衝突、沒有有效紀錄、git 不支援)沒有「淺 clone 缺歷史」這一類,使用者會被講成「沒有有效紀錄」而非「歷史不全」。建議在擋下訊息加第四類,並用 `_git_is_shallow` 判斷,與 `_codeloop_missing_commit` 同口徑。

不對齊共 3 條,其中 major 0 條
