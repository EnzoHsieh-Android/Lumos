severity: minor

資源席(sonnet)對 pkgA 的審查結果:我沒有找到 blocker 或 major。孤兒程序、時間預算和記憶體三條線上各有幾處 minor。以下全是讀程式推演,沒有在實機跑 Gradle 重現。

## 逐條回答三個問題

- **①子程序收尾:** 合併呼叫(合併基準與快篩)在逾時、第一個訊號、第二個訊號與 Ctrl-C 的路徑上都收得掉。
  - 逾時時 `_kill_run` 用 SIGKILL 砍整個程序群組。
  - 第一個訊號走 `on_signal`,`mg.interrupted` 在 `_kill_run` 回來後先於 `classify` 檢查。
  - 第二個訊號走 `_KILL_RUN_LIVE` 強制收,合併程序也在這張表裡。
  - 例外時 `finally` 會拿掉登記。
  - 但有兩個空窗(發現 1、4)。
- **②時間預算:** 開跑前量齊基準的估算是固定常數(發現 3),快篩逾時上限沒有受總時限約束(發現 2)。
- **③記憶體與二次方:** 結果檔先 `stat` 再讀,單檔 8MB、合計 64MB,`junit()` 是串流解析,所以大結果檔擋得住。
  - `_choice_merge_classify` 裡 `miss` 是 names × facts 的雙迴圈,但合併指令長度上限 32768 位元組把 names 限在約一千支內,量級是百萬次比對,不構成問題,不報。
  - 指令長度檢查用的是全部不重複名字,`lane` 是它的子集,所以擋得住;Windows 的 8191 字元上限也有算。
  - 逾時路徑上 `_kill_run` 的 `buf.read()` 仍整份讀進記憶體(發現 2 附帶)。

## pitfalls manifest 逐條判

- 第 1 條,`scripts/lumos:28996`:誤報。那是 `_kill_merge_apply` 的 `with open(target, encoding="utf-8") as fh`,有 with 收。
- 第 2 條,`scripts/lumos:29007`:誤報。那是同一函式的 `with open(target, "w", encoding="utf-8") as fh`,一樣有 with 收。

## 發現

### 1. 第一個訊號落在「看停止旗標」到「合併程序登記」之間會被漏掉,整支合併呼叫照跑完
severity: minor
blocking: 否
引句:「rc, tail, _el, to = _kill_run(mcmd, c.run_dir, max(m_el * 5, c.floor), merge=True)」
file: `scripts/lumos:29055`、`scripts/lumos:28175`

- **時序:** `_kill_merge_screen` 在 `should_stop()` 之後先做 `_choice_merge_clear`(對結果資料夾 `rmtree`),再進 `_kill_run`。`_kill_run` 裡 `Popen` 回來後才設 `_lumos_merge`、才登記進 `_KILL_RUN_LIVE`。
- **漏掉的情況:** SIGTERM 若落在 `should_stop` 與登記之間,`on_signal` 的迴圈裡還沒有這支合併程序。它只把 `interrupted` 設成真,沒有收任何程序。
- **後果:** `_kill_run` 之後照常等 `communicate` 到 `max(m_el*5, floor)` 秒。`interrupted` 要等它回來才被看到,所以第一個訊號後最長拖一整支快篩(約 2.5–5 分鐘),超過 timeout 先 SIGTERM、隔幾秒 SIGKILL 的寬限期。
- **窗口大小:** 窗口是 `rmtree` 加 `Popen` 的時間,約毫秒到數十毫秒。結果資料夾大時會拉長。基準那一側同理(`_kill_merge_base` 裡 `clear` 到 `_kill_run`)。
- **缺口在:** `_kill_run` 登記之後沒有再看一次 `interrupted`。
- 未能重現(窗口太短,要注入延遲才能紅),所以維持 minor。

### 2. 快篩逾時上限不受剩餘總時限約束
severity: minor
blocking: 否
引句:「rc, tail, _el, to = _kill_run(mcmd, c.run_dir, max(m_el * 5, c.floor), merge=True)」
file: `scripts/lumos:29056`、`scripts/lumos:28202`

- **對照:** 合併基準的上限有 `min(..., remaining)`(`_choice_merge_base_cap`),單支基準也有 `max(mg.remaining(), 1.0)`。快篩這一次沒有,上限只看 `m_el` 和 `floor`。
- **輸入:** 總時限 1800 秒,第 29 個壞法在 t=1790 開始,`m_el`=120 秒。快篩上限是 600 秒,一個掛住的壞法(例如被改成死迴圈)會讓這次呼叫跑到約 2400 秒才停。`stop()` 只在配方之間生效,所以不會中途停。
- **逾時之後:** 還要再跑逐支流程,第一支會再吃一次 5 倍基準的逾時。
- **附帶的記憶體與磁碟:** 掛住的壞法如果一直印輸出,暫存檔會增長到逾時為止,然後 `buf.read()` 整份讀進記憶體(`scripts/lumos:28202`)。逾時上限由 5×單支變成 5×合併,約放大測試支數倍。
- **計劃的態度:** 〈實務隱患〉已承認「掛住的壞法多等一次快篩逾時」,但沒有承認會超過總時限。
- 未能重現,維持 minor。

### 3. 「時限夠不夠量齊」用固定 10 秒單價估,基準階段可能把總時限吃光、零壞法判定
severity: minor
blocking: 否
引句:「if mg.remaining() < len(uniq) * _CHOICE_MERGE_UNIT_SECS * _CHOICE_MERGE_BUDGET_K:」
file: `scripts/lumos:28912`、`scripts/lumos:28954`

- **輸入:** 100 支守的測試、每支單支基準 17 秒(慢機器或冷 Gradle),總時限 1800 秒。
- **走法:** 閘檢 100×10×1.5=1500 ≤ 1800,通過。`_kill_merge_base` 先逐支量齊,約 1700 秒,然後 `hk.between()` 發現總時限到了,丟 `_KillHalt`。
- **結果:** 零個壞法被判,rc 2。
- **對照 `--no-merge`:** 基準用到才量,第一支就被殺掉的壞法只需要一支基準,仍能判出若干個。
- **根因:** 估算常數 10 秒是實驗專案的 6 秒取近兩倍,不隨實測調整。第一支單支基準量完就可以用實測值重估,但沒有這一步。
- 量齊之後若合併基準又逾時,同一份預算再被吃一次(上限被 `remaining` 夾住)。
- 未能重現,維持 minor。

### 4. 單支基準與逐支流程沒有合併標記,第一個訊號後 SIGKILL 會留下孤兒 Gradle 客戶端
severity: minor
blocking: 否
引句:「b_rc, b_tail, b_el, b_to = _kill_run(cmd_of[m], c.run_dir, min(max(600.0, c.floor), max(mg.remaining(), 1.0)))」
file: `scripts/lumos:28954`

- **時序:** 量齊階段(`_kill_merge_base`)會連續跑 N 支單支基準,第一支可能含冷編譯,數分鐘。SIGTERM 在這段進來時 `on_signal` 只收帶標記的程序,基準沒有標記。
- **後果:** lumos 照設計等那一支跑完。若呼叫端幾秒後送 SIGKILL,這條程序群組(`start_new_session`)沒人收,繼續跑到自己結束,上限約 600 秒。
- **和前一版的差別:** 前一版逐支流程也有這個行為,屬於〈做法〉4 的 `[不選:第一個訊號就收所有測試程序]`。但這次新增的量齊階段一口氣連跑 N 支單支基準,暴露窗口從一支變成 N 支。計劃對寬限期的論述只針對合併呼叫。
- 若要補,單支基準那一側也加 `merge=True` 標記,或在量齊階段的單支基準都標。

## ⚠ 交編排者(沒驗證到)

⚠ Gradle 背景程序:合併快篩逾時時 `_kill_proc_group` 只收 `gradlew` 客戶端所在的 session。Gradle daemon 與測試 worker 開在自己的 session,不在群組裡。

- **要驗證的事:** 客戶端被 SIGKILL 後,daemon 取消那次建置要多久、掛住的測試 JVM 會不會繼續佔 CPU。之後的逐支配方會不會遇到忙碌中的 daemon,而另起一個冷啟動 daemon。
- **為什麼無法判斷:** 我這邊沒有 Gradle 專案可實驗。
- **為什麼值得看:** 如果冷啟動慢到超過 5 倍單支基準,下一支逐支配方就會被判逾時(timed_out_weak),整組記成跑不出結果。這在前一版單支逾時也會發生,但合併逾時把 daemon 忙碌的時間拉長了。
- **建議:** S16 在實驗專案實測時,順便看逾時後 `ps` 上有沒有殘留的 Gradle Test Executor。

## 圖譜鏡頭
這次沒有附固定席節點(鏡頭計算超時),所以不逐條答。

總結:最高嚴重度 minor
