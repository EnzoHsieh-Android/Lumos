severity: minor

範圍:讀修補差異(修前 960cd3e6 → 修後 5f8f8e48),在 `/tmp/lumos-seat-work/code-測試名收自由字串/資源-sonnet/` 用大輸入實測。載入的是 web-gaps 工作樹的 `scripts/lumos`,它的 `scripts/lumos` 與 5f8f8e48 沒有差異。實測用 python3.14,基準記憶體約 300MB(模組載入本身)。

## 三個問題的答案

①**逾時與 Ctrl-C**:沒有問題。`git grep` 仍是同一個 `_sp.run(..., timeout=timeout)`,只是多帶幾個 `-e`,不是多開呼叫。逾時由 `subprocess.run` 殺掉子程序。呼叫端 `_tree` 接 `TimeoutExpired`,`_disp_git_timeout` 預設 8 秒,表態驗證那條由呼叫端接。名字上限 200 字(`_TEST_NAME_MAX`),所以引數總長有界(最多約 13 個 pattern)。

②**大 repo 正常推送會不會慢到被擋**:不會。
- `git grep`:本 repo 有 14740 個檔,單 `-e` 約 0.05 秒,七個 `-e` 約 0.05 秒,幾乎沒差。
- `_raw_test_titles`:3000 個測試檔、33000 個標題,掃一次 0.33 秒。
- 撞名比對:500 支綁定方法呼叫 `_name_collision_reason` 共 2.3 秒,約 4ms 一支。快取以(平台根, profile 名)為鍵,`_run_bound_tests` 與 guard kill 各一份,每平台只掃一次。若有 5000 支綁定,比對約 20 秒,可接受。

③**新正規式有沒有回溯爆炸或二次方**:沒有,都是線性。
- `_RAW_TITLE_RE`:我試了 8 種對抗輸入,19MB 內全部不超過約 2.2 秒。包括 `it(` 後接 399 字元重複、`it(` 後接大量 `(a)` 或 `(a` 重複、`it(x)(` 重複 17MB、`test.a.a…(` 重複、5MB 空白。
- `_C_STRIP_RE`:全是未閉合的 `'`(4MB)、未閉合的 `/*`(1MB)、未閉合反引號(2MB)、Kotlin 原始字串(9MB)、minified 20MB,都在 0.5 秒內。
- 沒改的 java 兩段式 `/\*.*?\*/` 遇到 200k 個 `/*` 也是 0.00 秒。

**32MB 字串記憶體問題:修好了。** 修前的 `_JS_STRIP_RE` 在 8MB 單一字串上用掉 970MB,約每字元 120 位元組,32MB 外推約 4GB。修後同一輸入只用 53MB(`new plain`)。32MB 單一字串跑完 strip 加 raw 的峰值是 335MB,只比基準多約 35MB。

## Findings

**1.**
severity: minor
blocking: 否

`_C_STRIP_RE` 展開式只修掉普通字元的記憶體,跳脫字元與註解體還是每個迭代佔一格狀態,線性但常數大。
- 8MB 單字串全是 `a\'`(約 4M 個跳脫):修前 970MB,修後 512MB,約 64 位元組一個跳脫。
- 45MB 全是 `a\'` 的單一字串:`strip` 峰值 2.3GB,接著 `_RAW_TITLE_RE.finditer` 峰值 5.5GB。
- 19MB 的 `'` 加 `\\` 重複:1.5GB。
- 未閉合 `/*` 後接 9MB 的 `* ` 重複:1.2GB,因為 `(?:\*+[^*/][^*]*)*` 每個迭代一格。

這需要單一測試檔裡有幾十 MB 的跳脫字串,真實測試檔到不了。這是修前同形狀問題的殘留,修後減半,不是回歸。若要連跳脫也壓平,跳脫要改成 `\\.` 與普通字元合進同一個 `[^…]` 之後的 possessive 或手寫掃描,現在不必做。

引句:「展開式寫法(普通字元一段一段吃、跳脫一個一個吃):群組加星號的寫法每走一個字元就多推一格狀態,」
歸因:有證據的原有漏查(修前同一類輸入 970MB,修後 512MB,方向是改善)
重現:`python3.14 /tmp/lumos-seat-work/code-測試名收自由字串/資源-sonnet/o.py old esc`(970MB),`... new esc`(512MB)

**2.**
severity: minor
blocking: 否

`_anchor_migration_hint` 在 doctor 的 test_ref 迴圈裡,每個沒找到的綁定都完整重掃一次整棵樹,沒有快取。
- 呼叫點在 `run_doctor`(`scripts/lumos`約 2158 行):在判 fake 或 dangling 之前,對每個 `name not in methods_for(plat)` 的綁定都呼叫。
- 函式內用 `loose = {**prof, "file_name_match": None}` 讀並剝註解所有同副檔名的檔,也就是整個專案的 `.ts/.js` 原始碼,不只是測試檔。
- 實測:node-jest profile,3000 個 `.ts` 非測試檔共 35MB,一次呼叫 1.00 秒。依此外推,100 條懸空或偽證據的綁定約 100 秒。
- 影響:只有 `file_name_match` 非空的 profile 會觸發(playwright、dart、python、node-jest、node-vitest)。綁定都健康時 0 次呼叫,所以不影響正常推送。懸空綁定很多的專案跑 doctor 會線性變慢。
- 修法:這一輪把 `{名字: 檔}` 的對照表依(root, profile)掃一次後快取,而不是每個綁定各掃一次。

引句:「for m in prof["method_re"].finditer(_strip_test_comments(txt, prof.get("comment_strip", "c-style"))):」
歸因:有證據的修復回歸(修前沒有 `_anchor_migration_hint`,這項成本是修補新增的;修前版本沒有該函式,故修前成本為 0)
重現:`python3.14 /tmp/lumos-seat-work/code-測試名收自由字串/資源-sonnet/a.py`,需先造 3000 個非測試檔 `.ts`(我已刪除,腳本原樣可重建)

## 已驗主張與未驗範圍
- 已驗:`git grep` 次數與逾時、`_raw_test_titles` 與撞名快取的規模、兩個新正規式的線性、32MB 單字串修復、引數長度上限。
- 未驗:Windows 的 `git grep` 命令列長度;真實超過上千檔的 Playwright 專案端到端推送時間(用合成資料代替);Ctrl-C 的實機中斷(只讀程式,依 `subprocess.run` 的標準行為判定)。
- 零 blocker、零 major。

最嚴重 severity:minor,blocking 共 0 條。
