severity: blocker

（來源：設計審 r1 接手席／整合與知識同步鏡頭，sonnet，2026-09-14）

## 1. lands_in 漏掉三道守衛的權威節點，其中一篇的 revalidate_when 已經預言了今天這一步

severity: blocker
blocking: 是 — 圖譜是本專案唯一真相來源，遺留的說謊節點會誤導後續每一次查詢，且此路徑無機械閘攔截，屬於靜默失效。

程式碼兩處註解都寫死「見 Projects/狀態標籤同步守衛_計劃」當作這套機制的唯一說明去處，但 spec 的 lands_in 只列三篇 Systems 節點，沒提那篇計劃節點、也沒提它的驗證紀錄。更關鍵的是該驗證紀錄的 revalidate_when 原文就寫「若做『砍標籤徹底去重』遷移 → S1 同步與 Check M 皆應退場」——正是本次要做的事，而 `lumos stale --candidate --match` 存在的理由就是抓這種情況，spec 沒有一條要求跑它或處理命中結果。三個月後的人會讀到一篇 status: pass 卻描述著已被砍掉機制的驗證紀錄，以及一篇說「去重遷移不做」的計劃節點，兩篇都在說謊。

引句:「三處一起拿掉——S1 之後漂移在定義上影響不了任何判斷」
file: `scripts/lumos:1194`
file: `scripts/lumos:4447`
file: `docs/lumos-toolchain-knowledge/Verification/2026-07-20_狀態標籤同步守衛.md:12`

## 2. 既有兩支測試沒被交代退場，會直接跟 S3 的新測試打架

severity: major
blocking: 是 — 會讓全套測試出現兩支互相矛盾的斷言，擋下推送前的閘，是可預期但未被規劃的返工。

一支斷言「set status 會同步改寫 status/* 標籤」，另一支斷言「lint 對漂移報 rc1、doctor 把漂移計入 issues」——正是 S3 要拿掉的行為。spec 只列了新測試名，完全沒提舊的兩支要刪除或改寫，照描述實作下去舊測試會直接翻紅。

引句:「改狀態時的標籤同步、單篇快檢的漂移檢查、全圖健檢的那一道」
file: `scripts/test_lumos.py:1845`
file: `scripts/test_lumos.py:1871`

## 3. 讀時合成只在 lumos CLI 內生效，Obsidian 原生標籤瀏覽不會經過這個 helper

severity: major
blocking: 是 — Obsidian 是本圖譜文件裡明講、非歷史段落的現行操作介面，標籤瀏覽功能性喪失且無人被告知。

規範文件多處教了直接操作 Obsidian 的指令，而 Obsidian 自己的 tag 索引與搜尋讀的是實體 frontmatter，不會呼叫合成 helper。S4/S5 把實體標籤拿掉後，這些節點在 Obsidian 原生標籤瀏覽或 dataview 查詢裡會直接消失，但 lumos 查得到——典型的工具間不同步，spec 完全沒提這條路徑。

引句:「消費專案不遷移也不會被過期的舊值誤導,遷移變成純美觀而非必要」
file: `skills/lumos-project-notes/reference.md:384`
file: `skills/lumos-project-notes/reference.md:918`

## 4. 規範文件的 Obsidian 建檔範本仍手刻鏡像標籤，S4 的範本修正不會碰到它

severity: major
blocking: 是 — 具體、可指行號的教學缺口，直接違反 S4 想達成的效果，且不會被任何測試攔下（那段是文件字串不是程式）。

S4 指名的落點是程式裡的四個範本。但規範文件有一段完全獨立、寫死在文件裡的 Obsidian 建檔指令字串，內容仍是鏡像標籤寫法，跟程式範本是兩條不同路徑，S4 不會觸及它。照文件手動建檔的人會繼續產生本案要消滅的鏡像標籤。

引句:「新建節點的四種範本（機制 system／計劃 project／驗證 verification／問題 issue）開頭只留真正有值的標籤」
file: `skills/lumos-project-notes/reference.md:918`
file: `scripts/lumos:12486`

## 5. S6 凍結兩個家族，但沒指示同步規範文件的家族對照表——而同一張表在上次凍結時就是既定落點

severity: major
blocking: 是 — 同一份文件同一張表有明確前例，這次漏做等於製造跟前例不一致的雙重標準，且沒有機械檢查會抓到。

那張表在 2026-08-05 凍結 feature/ 與 area/ 時就同步更新過，現在還寫著那兩個已凍結，證明這張表是這類決定的既定落點。這次 S6 凍結另外兩個家族，spec 九條條款裡沒有一條提到要比照更新這張表，讀者（包括 AI）會繼續照表把這兩個家族當現行在用。

引句:「語意警示（`flag/`）與優先級（`priority/`）兩個家族凍結退場」
file: `skills/lumos-project-notes/reference.md:378`

## 查證後排除、不構成 finding 的項目

- CLAUDE.md、AGENTS.md、指令參考中英兩份、README 中英兩份、紀律範本全部零鏡像標籤教學內容，不受影響。
- doctor 的 Check 字母本來就非連續、非位置索引，拿掉其中一道不會讓其他字母位移，也找不到任何文件用「第幾道」這種位置性說法引用它。
- slim 目錄雖也教了同樣寫法，但圖譜明寫該目錄自 2026-08-20 起已凍結、不再對外分發，不構成真實同步風險。
- dist 目錄被 gitignore 排除，非版控產物，非同步面。

總結：全篇最高 severity 為 blocker（第 1 條），blocking:是 共 5 條，blocking:否 0 條。
