severity: major

**Finding 1**
severity: major
blocking: 是,「同一 repo 內不會有新舊版本混用」這句不成立,而且 C 的簿記名單和 d4 的保護都靠它,依賴它的設計會在消費專案上失效。
引句:「每個專案的 CLI 是提交進 repo 的同一份副本,同一 repo 內不會有新舊版本混用」
file: `/Users/enzo/.local/bin/lumos`(符號連結,指向來源 repo 的 `/Users/enzo/harness/lumos-toolchain/scripts/lumos`)。工作階段和 CLAUDE.md 裡敲的 `lumos` 走的是這支全域的新版。
file: `scripts/hooks/pre-push:106` 的 `GRAPHCTL="$REPO_ROOT/scripts/lumos"` 和 `.github/workflows/ci.yml` 跑的是消費專案已提交進 repo 的副本,那份在 `lumos update`(`scripts/lumos:22927`)之前一直是舊版。
失敗場景:消費專案還沒 update,有人用全域新版跑 `lumos evidence run`、提交了證據帳。舊副本的 `_BOOKKEEPING_FILES`(`scripts/lumos:27097`)沒有列這個帳檔,代碼審留痕在推送前掛鉤和 CI 上都會失效。文中「舊版只會忽略它」只講了舊版不認帳,沒講它會把帳檔當成程式改動。
修法:寫明升級順序是先 `lumos update` 再用 evidence,或讓 `evidence run` 偵測到 vendored 副本版本較舊就拒絕。Codex 那一家只讀 AGENTS.md,同樣走 PATH 上的 `lumos`,也要一併寫進去。

**Finding 2**
severity: major
blocking: 是,d4 靠這個忽略規則才能保證含秘密的原始檔不離開本機,而規則的落點寫不通。
引句:「`lumos init` 與 `lumos update` 把 `.lumos/evidence/` 加進忽略清單」
file: `scripts/lumos:23117`。現有的 `_ensure_docs_gitignore` 只改 `docs/.gitignore`,而且 `_LOCAL_LOG_IGNORE_LINES`(`scripts/lumos:1363`)只放兩個帳檔名。`.lumos/config.json` 本身是進版控的檔案。
`docs/.gitignore` 裡的樣式是相對 `docs/` 的,擋不到 repo 根目錄的 `.lumos/evidence/`。
這需要改根目錄的 `.gitignore`,是新的寫入面;spec 沒寫,S1 到 S13 也沒有任何一條驗證它。沒跑過 update 的專案用 `git add -A` 就會把原始輸出提交進去。

**Finding 3**
severity: minor
blocking: 否,文件同步清單漏列的項目,守衛測試紅了會當場抓到,但清單的完整性判準寫錯了。
引句:「文件同步(頂層指令數從 86 改 87:架構文件三處、子命令一句話說明表、指令索引;兩份技能裡條款標記的句子)」
file: `ARCHITECTURE.md:108,112,142` 三處和清單吻合,真值也確實是 86。
清單漏了 `skills/lumos-project-notes/reference.md:117`,那一行要同時補進 `evidence` 的指令名和數字。`reference.md:1249` 的「86 個指令」也要改,但那句不符合 `t_docs_command_count`(`scripts/test_lumos.py:27744`)的樣式,守衛抓不到,會悄悄漂移。
「指令索引」指的是哪一個檔案沒講清楚。
回退節也沒有把 87 改回 86:只回退 evidence、保留文件,`t_docs_command_count` 會紅。

**Finding 4**
severity: minor
blocking: 否,RETIRE-IF 的量法只有人工的退路,但對 ①③ 寫的接線沒有落點。
引句:「量法:REVISIT 那天在手上的消費專案跑 `lumos gov --stats`」
RETIRE-IF ① 要數的「待人→已決」是題目狀態的轉換,不在任何帳上;`gov --stats` 看不到,只能靠 git 歷史翻計劃筆記。
file: `scripts/lumos:8293`。`_KNOWN_GATES` 沒有交付檢查的閘名,`t_gov_stats_gate_drift` 會要求新增。
「證據帳與交付檢查事件接進統計」這件事不在 S4 到 S11 任何一條,也不在階段 3 的完成判準裡,實作時沒有東西逼它做。

**Finding 5**
severity: minor
blocking: 否,回退順序沒寫,單獨回退任一塊的承諾因此打了折扣。
引句:「證據擷取:回退指令與簿記名單那一項;證據帳與本機原始檔留著不刪」
交付檢查(D)讀的是證據帳。只回退證據擷取、保留交付檢查時,帳檔被移出版控,那些 `[evidence]` 條款會永遠判成沒過,而 `lumos set done` 也被同一套檢查擋住。
回退節只寫了交付檢查要先改條款的反向情況,沒寫先回退交付檢查再回退證據擷取這個順序。

其餘回退項我實際查過可行,不另標:
- `lumos decision-supersede` 對 `#d1` 的精確定址可用(`scripts/lumos:20334`)。
- 開發工作流總覽的舊決策已經是 `valid: false` 並指向本篇 d1(`docs/lumos-toolchain-knowledge/Systems/開發工作流總覽.md:30-36`),所以先 `decision-add` 再 supersede 這條路走得通。
- 「`[evidence]` 條款在同一個提交改成 `[manual:]`」這個步驟本身成立。

S13 的落點沒有問題:另一個乾淨的 clone 照 README 跑出同一測試的 PASS 證據列,是人工驗收,階段 6 有對應。

總結:最嚴重 major;blocking 共 2 條
