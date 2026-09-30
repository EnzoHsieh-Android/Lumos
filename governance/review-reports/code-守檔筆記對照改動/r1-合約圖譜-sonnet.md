severity: minor

# 合約圖譜一致審(合約圖譜-sonnet,第 1 輪)

範圍:凍結 patch 的程式改動,對照 Systems/筆記內容審、Systems/存量漂移守衛、Systems/bound-tests-gate 三篇家筆記與計劃條款。查過的項目(都對得上、沒破壞):簿記豁免 `_BOOKKEEPING_DIRS` 加 `governance/reread-verdicts/`(五個消費者共用同一個元組,筆記寫的回退辦法與程式註解一致);`_KNOWN_GATES` 加 `note-reread`(`_gate_event` 對名單的檢查通過);`_VENDORED_TREE_FILES` 加新範本(家的 about_code 有列);推送前掛鉤與 CI 新段落不含 `note-audit check` 與 `drift check` 兩串上線字串(grep 實測:pre-push 的 `drift check` 仍 2 處、`note-audit check` 0 處),不會讓筆記內容審與存量漂移的上線點判斷漂移;`pp_stop_if_signaled` 呼叫數 6 行,跟 bound-tests-gate 筆記寫的一致;`_notes_touched_in_range` 抽出後 `_notes_status_flipped` 的截止時間、git 失敗回 None、不過濾頂端讀不到三點與筆記內容審筆記 WHY(嚴格模式只給存量漂移)一致;`_note_audit_resolve` 不給 reasons 時逐分支行為不變;`_note_audit_prompt` 改走共用填字後佔位字行為不變。

## F1 升版到 v1.2 但本 repo 自己的 CLAUDE.md、AGENTS.md 紀律區塊戳記沒跟著升
severity: minor
blocking: 否
引句:「所以升版,讓還沒更新的專案被提示跑 `lumos update`」
file: `CLAUDE.md:2`
1. 這次把 `LUMOS_VERSION` 由 v1.1 升到 v1.2,CHANGELOG 寫升版目的是讓消費專案被提示更新。前一次升版(commit fd6b2af4)同一個提交就把 `CLAUDE.md`、`AGENTS.md` 的區塊戳記一起重注入;這次 patch 沒動這兩支,兩者仍是 `LUMOS:GRAPH-DISCIPLINE:START v1.1`。
2. 重現(在 94e28375 的乾淨 clone 上):`LUMOS_HOME=$PWD python3 -c '…m._version_nudge(Path("."))'` 印出「本專案紀律區塊版本 v1.1 落後來源 v1.2, 可跑 lumos update 刷新」。doctor 的 vendored-cli 那一項(`lumos` 內 ⑦ vendored 版本)對本 repo 因此會判 degraded,工具鏈自己的健檢在自家 repo 上帶一條自我提示。
3. 不影響行為與閘;重跑 `lumos update` 重注入(內容無差,只換戳記)即可收掉。嚴重度 minor。

## F2 兩篇家筆記把「掛鉤與 CI 呼叫 reread-check 那一段」推給存量漂移守衛,但它的 responsibility 沒認領,且筆記內容審仍寫「四個子指令」
severity: minor
blocking: 否
引句:「排在存量漂移檢查之後;最多約 30 秒(工具自己的軟上限),逐 ref 各跑一次。」
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:6`
file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:59`
1. Systems/筆記內容審 的 responsibility 寫「不管推送前掛鉤與 CI 呼叫 reread-check 那一段(存量漂移守衛)」,Systems/bound-tests-gate 新段也寫「呼叫那段歸 [[Systems/存量漂移守衛]]」;但 Systems/存量漂移守衛 的 responsibility 仍只寫「推送前掛鉤與 CI 裡呼叫 drift check 的那一段」(本次只改了 `updated` 與一條內文 bullet)。三篇互相推給對方、責任欄卻沒有一篇認領這一段,日後改這段時「家是誰」的機械判讀會落空。
2. 同一篇筆記內容審的導讀 bullet 仍寫「`cmd_note_audit_*` 四個子指令」,而這次新增 `cmd_note_audit_reread_prepare/record/check` 三個同樣符合該樣式,實際是七個;該 bullet 沒更新,新段落又自稱「reread 三個子指令」,同篇內部數字對不上。
3. 改法:存量漂移守衛 responsibility 加上 reread-check 的呼叫段;筆記內容審該 bullet 改成「四個子指令加 reread 三個」。嚴重度 minor。

最高等級:minor
