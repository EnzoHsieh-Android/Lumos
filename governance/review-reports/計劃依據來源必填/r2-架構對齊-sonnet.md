severity: minor

我先核對上一輪(r1)的 4 條:F1(第四套出處判法)已修,明寫了跟預期值表來源格、型錄、`[出處:]` 的關係,並要求寫成一支共用函式。F2(找節切表)已改成重用 `_h2_section_lines`、`_expected_table_lines`、`_expected_split_cells`。F3(訊息形狀)已寫齊標頭、逐條、範例、通過與舊計劃的行。F4(型錄計數的接口)大半已修:改成另開 `catalog_unverified`、不進 `catalog_problems`,但印在哪條路徑沒寫,見本輪 F2。r2 沒有第二種做法或跨層直呼。

**第一問 模組邊界**

規格閘新道、doctor 提醒、`check.py` 另開計數函式、紀律範本與兩份手冊各一句,落點都對。

引句:
「新開一支 `_spec_gate_sources_part(env, rel, text)`,在 `_spec_gate_front` 裡排在待決問題(`_spec_gate_pending`)之後、條款綁定(`_spec_gate_clause_part`)之前」

- 這個位置跟 `_spec_gate_front` 現有順序一致,見 `scripts/lumos:15474`。待決問題在前,接條款綁定,再接 `_spec_gate_expected_part`。
- 回傳形狀(擋回 1、沒事回 None)同 `_spec_gate_pending`(`scripts/lumos:15393`),也同 `_spec_gate_expected_part`(`scripts/lumos:15507`)。
- 計劃對「為什麼不能掛在預期值表後面」的說明站得住:`_spec_gate_clause_part` 零條款時提早回 0。

引句:
「型錄計數另開函式、只提醒不擋」

- `catalog_problems`(`configs/ast-grep/kotlin-android/check.py:129`)的回傳全是會擋的問題,另開 `catalog_unverified` 是對的邊界。
- 推送前重查走 `_expected_push_one` 同一個出口(`scripts/lumos:16556`、呼叫點 `scripts/lumos:16544`),放對層。

F1
severity: minor
blocking: 否
引句:
「跟它對預期值表簽核的既有做法同一個出口、同一種留帳」
- 既有的推送前出口是 `_expected_push_one`。它回傳以 `_EXPECTED_PUSH_TAG` 開頭的原因字串,並寫 `expected-unsigned`(`scripts/lumos:16589`)。
- `_spec_gate_push_bad_head`(`scripts/lumos:16596`)靠這個標籤分辨標題。
- 治理帳統計(`scripts/lumos:17181`)用 `expected-unsigned` 數「因為沒簽被擋」。
- 計劃沒說推送前重查擋下時:
  - 寫哪一種事件種類。S2 只涵蓋規格閘本身的 `sources-missing`。
  - 用不用自己的標籤與標題。
- 若沿用 `expected-unsigned`,會污染簽核統計;若另開,標題函式要跟著加一支分支。
- 結構方向是對的,只是缺命名決定。

**第二問 命名與錯誤處理**

引句:
「讀法另寫一支 `_plan_sources_since()` 照 `_expected_since`」

- 常數 `_PLAN_SOURCES_SINCE`、環境變數 `LUMOS_PLAN_SOURCES_SINCE`、測試總檔預設 9999-12-31,都對得上 `scripts/lumos:14221` 與 `scripts/lumos:14281` 的寫法。
- 新函式名 `_spec_gate_sources_part` 對應 `_spec_gate_expected_part`,命名一致。
- 治理帳事件用既有的 `_gate_event`(`scripts/lumos:1799`),閘 `spec-gate`、種類 `sources-missing`,跟 `spec-gate-record`、`expected-unsigned` 同型。
- 訊息形狀已逐項對齊 `scripts/lumos:15515` 的三塊:標頭、逐條、範例。通過那行 `✓ N 列` 也對應既有的 `✓ — N 列`。

F2
severity: minor
blocking: 否
引句:
「主程式在既有的問題清單之外另印一行數字與前 20 個編號」
- `check.py` 的 `main`(`configs/ast-grep/kotlin-android/check.py:368`)有兩條輸出路徑:`--catalog-only` 印「型錄問題 N 個」,完整路徑印「規則 N 條,問題 N 個」,兩條都 `return 1 if ... else 0`。
- 計劃沒說新的一行要加在哪條路徑、哪個位置。
- 只加一條會造成兩種入口行為不一致;兩條都加則測試 S5 要兩邊都綁。
- 結構對,缺入口落點。

**第三問 第二種做法**

引句:
「判法寫成一支共用函式,規格閘、推送前重查、健檢三處都呼叫它。」

- 出處判法已收成一支共用函式,不再是 r1 的三處各寫。
- 找節、切表重用 `_h2_section_lines`(`scripts/lumos:13783`)、`_expected_table_lines`(`scripts/lumos:14342`)、`_expected_split_cells`(`scripts/lumos:14318`)。
- 生效日與新舊判斷重用 `_plan_effective_day`(`scripts/lumos:14261`)。
- 實字判法重用 `_real_chars`(`scripts/lumos:13936`)。
- 擋下留帳重用 `_gate_event`。

F3
severity: minor
blocking: 否
引句:
「repo 內存在的檔案路徑:反引號包住,用 refcheck 現成的 `_refcheck_scan` 判存在」
- `_refcheck_scan(text, repo_root)`(`scripts/lumos:37571`)吃整段文字、回 `(claims, n_missing, n_oor, n_ok)`,有自己的 inline-code 抽取與頂層目錄過濾,不是「單一路徑存不存在」的判法。
- 計劃沒說怎麼從這四個回傳值取出「這一格裡有沒有至少一條存在的路徑」。
- 節點連結只說「用現成的連結正規式抽出、節點要存在」,沒指明用 `_SINGLE_WIKILINK_RE`(`scripts/lumos:509`)還是別的、也沒指明節點存在查哪個索引。
- 共用判法函式本身也沒命名。
- 這是命名與接口缺口;實作者若自己繞過 `_refcheck_scan` 另寫路徑判斷,才會變成第二種做法。建議計劃寫明函式名與這兩個取用點。

不對齊共 3 條,其中會擋的 0 條。
