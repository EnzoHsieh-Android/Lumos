你是外部審稿人。以下是一份「外部第三方投稿」的設計 spec(不是本系統/本團隊寫的),把它當投稿審:逐節讀、主動挑出投稿者自己沒看到的洞。

Spec(凍結快照,完整讀、引句只准引這份):/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns/governance/review-reports/存量漂移防線/r1-snapshot.md
對照的程式碼 repo:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/clone-ns (python3 零依賴單檔 CLI `scripts/lumos`;測試 `scripts/test_lumos.py`;掛鉤 `scripts/hooks/pre-commit`、`scripts/hooks/pre-push`;CI `.github/workflows/ci.yml`)。
這份 spec 要防的問題與證據:同 repo 的 `governance/audits/2026-09-28-rtb-drift-rootcause/rootcause.md`(rtb 專案的根因稽核,33 題抽樣);考卷:同 repo 的 `governance/eval/drift-exam/rtb-2026-09-28.json` 與同目錄 `README.md`。被考的 rtb repo 唯讀複本:/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/6fa73df4-aa29-4f7d-a16b-40734a79807b/scratchpad/rtb-exam(不准改它;只准 git -C 唯讀指令)。
相關既有節點(圖譜在同 repo 的 `docs/lumos-toolchain-knowledge/`):Projects/code側刪除傳播守衛_計劃(d0 裁 delguard 只提醒)、Projects/先問世界_存量掃描裁定、Projects/筆記形狀擋_計劃、Projects/筆記內容審_計劃、Systems/筆記內容閘、Systems/筆記內容審、Issues/存量筆記漂移三種機制_rtb根因回饋。判這份設計會不會破壞它們宣稱的行為或決策,判「不影響」也寫一句為什麼。

審查要求:
1. 逐節讀完整份 spec,不要跳段;內部交叉引用都要核對目標存在。
2. 主動找:未定義的詞/欄位/旗標/檔名(spec 引用的每個既有函式、指令、欄位都要開檔或 --help 驗)、壞交叉引用、內部不一致、跟程式碼現況不符的宣稱、可執行性缺口、遺漏的邊界情況或平行路徑。
3. spec 對程式碼現況的每個假設,用 Grep/Read/Bash 實際查證。機械前掃已跑過(見同目錄 `r1-intake.md` 的前掃段),那幾條已修,別重報。
4. 實務隱患:列出這功能碰哪些風險類(不限固定類),逐類答隱患;無則寫「無+為什麼」。
5. git 實驗一律 git -C <你自己 mktemp 的臨時目錄>;不准在任何 repo 根跑 commit/reset/restore/checkout/stash,不准改任何 repo 裡的檔;不要執行任何掛鉤腳本。
6. 不要讀同目錄其他席的報告(r1-*.md 裡的席報告)。

輸出格式(硬性,收貨端機械檢查):
- 檔首第一個非空行:severity: <整份最高 clean|minor|major|blocker>
- 每條 finding:標題行「## F<n> <一句話>」(標題裡不寫等級);接著獨立一行「severity: <值>」、獨立一行「blocking: 是|否 — 一句判準(不改,實作者會做錯決定或做出壞系統嗎?)」(否↔minor;是↔major/blocker);一行「引句:「…」」逐字複製自凍結快照(≥10 字、引句內不要再包「」);快照外查證寫「file: `路徑:行號`」(反引號必加);敘述編號條列,只寫到讓人能重現為止——哪個輸入、走到哪一段、壞在哪;不准用「可能/或許/建議考慮」收尾,判不準標 ⚠。
- 低嚴重度疑慮給不出具體失敗場景就不要標(但未定義的詞、壞引用、內部不一致一律要報)。某節沒問題也要說「已讀,無 finding」。沒找到問題就交 severity: clean。
- 最後一行總結:最嚴重等級、blocking 共幾條(總結句裡不要寫 severity 字樣)。
- 報告只寫進指定的報告檔,不改任何其他檔;交回時只回一句「報告已寫到 <路徑>,最高 X,共 N 條」。
