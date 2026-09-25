severity: blocker

## F1 lands_in 現存違規數少報超過一個數量級,gate=on 會擋掉所有跟這批舊筆記無關的未來推送

spec 說現存違規只有 9 篇計劃缺 `lands_in`,做法四只列了 9 篇來補,並要求本 repo 直接把 `note_lint.gate` 設成 `on`、且驗收條件 S12 要求「本 repo 圖譜的每一篇筆記都應通過 lint」。我對 `docs/lumos-toolchain-knowledge/Projects/*_計劃.md`(檔名以「_計劃」結尾,S10 管的範圍)逐篇檢查 frontmatter 有沒有非空的 `lands_in`,結果 162 篇裡有 144 篇沒有(其中 132 篇 `created` 早於 2026-09-11,「每支檔有家」這套慣例引入之前建的舊計劃,狀態分布是 done 86、doing 47、superseded 6、todo 5)。隨機挑三篇驗證都是完全沒有 `lands_in` 這個鍵,不是格式錯:`docs/lumos-toolchain-knowledge/Projects/CI回流閉環_計劃.md:1-27`(frontmatter 只到 27 行,無 lands_in)、`docs/lumos-toolchain-knowledge/Projects/Java補棧_計劃.md:1-44`(created 2026-09-12,晚於 cutoff 仍缺)、`docs/lumos-toolchain-knowledge/Projects/席位人格化_計劃.md:1-25`。S10 的條件文字本身沒有任何 cutoff 或 status 排除:

severity: blocker
blocking: yes

引句:「檔名以「_計劃」結尾卻沒寫落點 9 篇(r1 簡化席更正:原寫 14 混進了「_調研」筆記)」
引句:「若名稱以「_計劃」結尾的專案筆記沒有 lands_in,或其中一項不是 `Systems/<名稱>` 的純字串、或指到不存在的節點,則 lint 應報錯誤」
引句:「現存違規只有 10 篇,直接修掉比較簡單」
引句:「本 repo 在自己的 `.lumos/config.json` 設 `on`。」

而「一、推送前健檢加『筆記格式』段」是對整個圖譜重跑、不接碰到清單(不是只查這次改到的筆記):

引句:「對圖譜裡每一篇筆記跑 lint 的**錯誤等級**規則(提醒等級不跑,避免重複嘮叨);有錯的列出篇名與第一條錯誤。」

三件事合起來:①現存違規是 144 篇不是 9 篇;②S10 沒有 cutoff,舊的、已經 done/superseded 的計劃一樣算違規;③健檢段掃全圖不看碰到清單。結果是:這次改動照做法四只補 9 篇 + 1 篇 Issue 之後,本 repo 把 `note_lint.gate` 設成 `on` 送出去,下一次任何人推送(即便只改一支完全不相干的程式檔),`doctor` 全圖重跑 lint 會在那 132+ 篇既有的舊計劃上報錯,S1「有任何一篇錯 → 這段算問題、推送前與 CI 都擋」直接擋下——擋的是跟這次推送內容毫無關係的舊筆記,這正是「不該擋的擋下」。S12 的驗收條件(「本 repo 圖譜的每一篇筆記都應通過 lint,且本 repo 的 note_lint.gate 是 on」)在做法四目前列的補救範圍下也不成立。

## F2 valid 布林值的大小寫沒講清楚,跟現有 runtime 語意不一致時會誤判

S8 與做法二只寫「valid:只能是 true 或 false」,沒講是否大小寫不敏感。現有 runtime 對 `valid` 的判讀全部是先 `.lower()` 再比對(例如 `scripts/lumos:1816`、`scripts/lumos:1981`、`scripts/lumos:2276`、`scripts/lumos:2288` 皆為 `str(d.get("valid","true")).lower() != "false"` / `== "false"` 的寫法),也就是 `valid: False`(大寫)在現有系統裡本來就會被正確判讀成「已翻案」。若照 S8 字面實作成精確比對 `true`/`false` 兩個小寫字串,一條寫成 `valid: False` 的決策雖然語意正確、runtime 也讀得對,lint 卻會報錯,擋下一個本來沒有問題的筆記內容。

severity: minor
blocking: no

引句:「決策的 `valid`:只能是 true 或 false(現在寫成 no、0 會被當成有效)。」

`scripts/lumos:1816`、`scripts/lumos:1981`:現有 `valid` 讀取邏輯用 `.lower()` 做大小寫不敏感比對,S8 沒有講新規則要不要沿用同一口徑,兩種實作(精確比對 vs 大小寫不敏感)行為不同、其中一種會跟 runtime 語意不一致。

## 實務隱患(逐類覆核)

- 金流:無——lint/健檢只讀本機筆記檔案格式,不碰交易或計費路徑,查證 `scripts/lumos:4790`(cmd_lint)起的邏輯全是字串/frontmatter 檢查。
- 對外送出:無——健檢與 lint 都只讀本機檔案與 `git`,沒有任何網路呼叫,查證同上。
- 不可逆:無——擋的是提交/推送退出碼,開關可隨時調回 warn/off;F1 指出的是「會不會誤擋」而非「擋了回不去」,不影響此類判定。
- 守衛面:是,而且比 spec 自己的風險描述更嚴重。spec 只寫「消費專案預設只提醒、開關在各自設定檔、看不懂的值當 warn」這三道保險,但沒提到本 repo 自己把 `note_lint.gate` 設成 `on` 且驗收條件 S12 要求全圖零違規——F1 顯示這個組合在補救範圍不夠時,會讓本 repo 自己的推送閘被完全不相干的舊筆記卡死,是本案新增的擋點裡最大的實際風險。

最嚴重 severity: blocker;blocking 共 1 條。
