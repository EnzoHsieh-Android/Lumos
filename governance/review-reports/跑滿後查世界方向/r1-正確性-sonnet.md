severity: major

先講對照的結論。「最新一筆人裁」在程式裡只有一種取法:治理帳檔內順序的最後一筆 cap-decision。取法有三處:`cmd_loop_retro` 在 `scripts/lumos:22874`,`_cap_retro_status` 在 `scripts/lumos:22533-22537`,`_codeloop_pass_accept_risk` 在 `scripts/lumos:68506`。`--check` 與 `--record` 在同一次呼叫裡用同一個 `dec`。`--record` 之後 `_cap_retro_status` 會用最新人裁重驗一次。所以「先 accept-risk 後 extra-round」「反過來」「回顧記過後又記新人裁」這幾種帳面,都會被新判法正確判成「要重新回顧」,沒有判錯。「version 是 2 但人裁是 accept-risk」也沒問題:空骨架或省略都過,填一半擋下,符合 S3。

1. 作者新改的手冊順序(查 → 攤人裁 → 記 cap-decision)沒有同步到程式印出來的提示,第一步「查」實際上會被跳過。
   引句:「順序是查 → 攤人裁 → 記 cap-decision → 寫回顧」
   - 到頂時 AI 看到的第一句話是 `_cap_retro_next_lines` 印的「要破例再開一輪或接受剩下的風險,先記人裁:lumos loop cap-decision …」。它被 `[cap-hint]` 和 `loop next --json` 共用。
   - spec 的同步清單只列 SKILL.md、reference.md、templates.md 和 `Systems/loop-retro`,沒有這支提示,也沒有 `cmd_loop_cap_decision` 成功後印的「繼續之前先寫跑滿回顧」。
   - 結果:編排者照工具提示直接記人裁,事後才在 `--check` 被要求補 `world_check`。這時「查 → 攤人裁」已經沒機會發生,「讓結論影響得到要不要加開」只存在於手冊,工具完全不推。
   - file: `scripts/lumos:22781`
severity: major
   blocking: 是——spec 自己宣稱的新主幹順序,在 AI 實際讀到的指引中不存在,屬於會讓設計目的落空的缺漏。

2. `--record` 的提醒不看人裁種類,也不看人裁先後,在兩個情況下講出錯誤的話。
   引句:「世界查證認為要換方向:加開前先跟人確認新方向,別照原方向直接派下一輪」
   - 輸入一:人裁是 accept-risk,但回顧檔填了完整的 `world_check`,`verdict` 是 `change-direction`。`--record` 會印「加開前先跟人確認…」,可是這個迴圈已經不加開。這種情況更需要提醒的是「查到方向錯了,卻選擇接受風險」,不是「加開前」。
   - 輸入二:人裁是 extra-round。`cmd_loop_retro` 在 `dec` 為空時直接回 2(`scripts/lumos:22874-22878`),所以 `--record` 一定發生在 cap-decision 之後。「加開前先跟人確認」在人裁已記下之後才印,時序是反的。
   - `_cap_retro_check` 沒有任何比較 `world_check` 與人裁時間的機制,所以也分不出結論是在人裁前還是人裁後寫的。
   - file: `scripts/lumos:22874`
severity: minor
   blocking: 否——只印不擋,錯的是提示文字,不是放行或擋下。

3. S2 條款與 §2 內文對 `queries` 的寫法不一致,條款綁的測試抓不到「每條」寫成「有一條」的實作。
   引句:「queries 沒有一條夠 4 個字」
   - 內文寫「`queries` 至少一條、每條…至少 4 個字」。輸入 `["搜尋世界解法有沒有人走過", ""]`:按內文判不過(第二條是空的),按 S2 字面判得過(有一條夠長)。
   - 骨架發的是 `queries: [""]`,編排者多留一條空字串是很自然的輸入。
   - 若實作者用 `any(...)`,S2 綁的 `t_retro_check_world_check` 只要用「全部都短」的輸入,測試照綠。
   - 同類問題:`sources` 內文寫「兩項的 `url` 不能相同」。`[A, A, B]` 要判過還是判不過沒講清楚,是成對互異,還是至少兩個相異?
severity: minor
   blocking: 否——只影響邊界輸入的判法,不影響主路徑,可在條款裡補一句。

4. `_loop_ts_key` 遇到非字串 `ts` 會丟 `AttributeError`,和 spec 說的「解不開當成生效日之後」不符。
   引句:「解不開當成生效日之後。沒有人裁紀錄」
   - 我實測過:`_loop_ts_key(1730000000)`、`_loop_ts_key(["x"])`、`_loop_ts_key(True)` 都丟 `AttributeError`,因為 `ts.replace` 只被 `except ValueError` 包著。
   - 治理帳可手改,`_retro_gov_events` 只要求每行是 dict,不檢查 `ts` 型別。一筆 extra-round 人裁帶 `"ts": 1730000000`,`cmd_loop_retro --check/--record` 就會出堆疊。
   - 這個專案對這類帳面有一整組「不丟堆疊」測試,例如 `t_cap_retro_bad_file_no_traceback`。新增的 ts 判斷如果不先驗是字串,就是第一個破口。
   - file: `scripts/lumos:19357`
severity: minor
   blocking: 否——需要手改帳才觸發,而且是 fail-closed(崩而不是放行)。

5. S4 的舊格式測試如果沿用 `_cr_decide`,會在生效日零點變成定時炸彈。
   引句:「人裁時間早於生效日的 version 1 回顧應照舊過」
   - `_cr_decide` 走 CLI 記人裁,`ts` 是當下時間(`scripts/test_lumos.py:103441`、`scripts/lumos:1597`)。
   - 生效日是合併日隔天零點,合併當天 `now` 一定早於它。用 `_cr_decide` 寫的「v1 照舊過」測試今天綠,生效日零點起全紅。
   - 反過來,S4 的前半「不早於生效日 + v1 → 擋」,在生效日之前用真實時鐘根本造不出來,測試必須自己寫帳或改 `ts`。
   - spec 只說「另寫一支舊格式的測試」,沒說怎麼造 `ts`。
   - file: `scripts/test_lumos.py:103441`
severity: minor
   blocking: 否——是測試脆弱而不是工具判錯,但會在特定日期讓推送前閘全紅。

6. 網址檢查只看前綴,「至少兩個來源」可以用同一頁或空網址湊出來。
   引句:「`url` 以 `http://` 或 `https://` 開頭」
   - 輸入 `https://` 加 `https://a`:前綴都對、字串不相同,兩項都過。
   - 輸入 `https://a.com/x` 加 `https://a.com/x/`(或加 `#frag`,或 http 對 https):是同一頁卻算兩個來源。
   - 反方向:`HTTPS://…` 大寫 scheme 是合法網址,卻被擋。前後空白要不要 strip 也沒講。
   - spec 的天花板只講「AI 可以編網址」,這幾個連編都不用編,是格式檢查本身比該有的寬。
severity: minor
   blocking: 否——這個欄位本來就只擋格式。

7. 新擋下訊息的指引「改用新骨架」,在有舊回顧檔的情況下會走進死路。
   引句:「生效日後人裁加開還拿舊骨架的,擋下訊息要講怎麼補」
   - 情境:生效日前人裁的 v1 回顧已記過,加開一輪後又到頂,生效日後再記一筆 extra-round。
   - 回顧檔只有一個固定路徑,`--template --write` 用 `O_EXCL`,檔已存在就不覆寫(`scripts/lumos:22916-22918`)。
   - 擋下訊息叫人「改用新骨架」,照做會得到「已經存在,不覆寫」。`_cap_retro_fix_cmd` 又回「回顧檔已在、還沒記:`--check` 過了再 `--record`」,繞回原點。
   - 能走通的只有 `--template` 印到 stdout 再手貼,或手改 `version`。訊息要明講這兩條,不能只講「新骨架」。
   - file: `scripts/lumos:22916`
severity: minor
   blocking: 否——不影響判定,只影響擋下後的出路。

8. ⚠ 版本號收緊後,尚未更新的舊版工具會把新回顧判成過期。
   引句:「收 1 或 2;其他值照舊擋」
   - 舊程式 `scripts/lumos:22431` 是 `v == 1`。在沒更新 lumos 的機器或舊分支上,一份 v2 回顧會被判「version: 要是 1」。
   - 效果是 `_cap_retro_status` 回 stale,`canary record` 和處置閘第八步都擋。
   - 〈回退〉只講了新工具讀舊檔、回退後新檔照收,沒講「新檔被尚未更新的工具讀」。
   - 我不確定使用者實際有多少台沒同步的機器,所以標 ⚠。
   - file: `scripts/lumos:22431`
severity: minor
   blocking: 否——取決於分發節奏,不是 spec 邏輯錯。

9. ⚠ accept-risk 的「空骨架」判定沒講型別檢查和空值判斷誰先。
   引句:「空骨架指 queries 每條、每個 source 的 url 與 point、verdict、note 去掉空白後全是空字串」
   - 輸入:`world_check` 是 `null`、`{}`、`{"queries":[5]}`、`{"sources":["x"]}`。
   - 內文寫「先驗型別再數字數」,但 accept-risk 那段先要判空。如果實作者先對每格呼叫 `.strip()`,遇到非字串會丟例外。如果先驗型別,`null`、`{}` 算「省略」還是「型別錯」沒定義。
   - `queries: []` 且其他格全空,依「每條全是空字串」的字面是空洞為真,當成空骨架放行。
severity: minor
   blocking: 否——只在 accept-risk 且 `world_check` 形狀異常時才碰到。

實務隱患逐類:
- 併發:無。`cap-decision` 與 `--record` 是兩次獨立的 CLI。若在驗到記之間有別的會談追加新的人裁,`_cap_retro_status` 會用新的最新人裁重驗,對不上就判 stale(`scripts/lumos:22569`)。治理帳是 append-only 且有路徑守衛。
- 效能:無。新增的是對 ≤256KB 檔的常數次欄位檢查,加一次 `_loop_ts_key` 解析。`_cap_retro_scan` 的迴圈數和每圈成本不變。
- 資源:無。沒有新的檔案、程序或網路。上網查是編排者在對話裡做,寫入的還是同一個回顧檔。
- 回滾:有風險,見第 8 條。本機回滾沒問題,「version 收 1 或 2」那段留著就能讀 v2。風險在尚未更新的舊工具讀 v2。
- 資料正確性與相容:已在上面看過。生效日前後以人裁事件 `ts` 判斷,和 `_SPEC_GATE_SINCE` 同一套 `_loop_ts_key`,時區處理沒問題。非字串 `ts` 是第 4 條。
- 資安與輸入:新欄位走同一個 `_fix_bad_strings` 和 `_esc_clean`。非字串數字數的例外已被 spec 的「先驗型別」覆蓋,只有 accept-risk 的判空順序沒定(第 9 條)。

已讀,無 finding 的節:〈問題與最小解〉、〈不做〉、〈回退〉(第 8 條除外)、〈實務隱患〉。

總結:最嚴重 severity 是 major,blocking 共 1 條(第 1 條),其餘 8 條 minor、blocking 否。
