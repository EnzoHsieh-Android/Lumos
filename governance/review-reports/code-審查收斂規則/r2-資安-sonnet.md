severity: major

最高等級是 major。下面四條 finding,其中 3 條 blocking。

## F1 分兩次推送,第一次縮小索引的守備範圍(about_code 與 tests)
severity: major
blocking: 是 — 攻擊者的目標是「改到帶殘留合約的程式卻不被要求高風險審」,這條兩次推送就做得到,而且第一次推送不會被攔。
引句:「elif bp - hp:」
攻擊步驟與判定:
- **根因**:`_residual_tier_hits` 的「拿掉殘留」只比 `(節點, 殘留指標)` 這組 pairs。`about_code`、`test_files`、`tests` 縮小或清空,完全不算改動。
- **步驟**:
  1. 推送 1 只動合約的家(把 guard.py 從 about_code 移到別的節點)並重建索引,或改掉合約綁的測試名。pairs 沒變。
  2. 推送 2 改 guard.py,拿推送 1 的結果當 base,`whole` 已經是空的。
- **為何擋不到**:
  - `whole = bw | hw` 只對同一次範圍的 base 與 head 取聯集,擋不到跨次推送。
  - 推送 1 只有圖譜與 json,pitfalls 判 light。
  - 家的規則要求每支程式檔有家,把檔案轉掛到別的節點就合規。
  - doctor 的「索引對圖譜」只比對重算結果,圖譜與索引一起改就一致。
- **函式層實驗**:
  - 基準:索引條目 `about_code=[scripts/guard.py]`、`tests=[t_guard_one]`,pairs 為 `Projects/p#d1`。
  - 推送 1(只把 `about_code` 與 `tests` 清空,pairs 不變):`_residual_tier_hits(repo, B..P1)` 輸出 `{}`。
  - 推送 2(改 guard.py):`P1..HEAD` 輸出 `{}`。
  - 同一批改動合成一次推送:`B..HEAD` 輸出 `{'files': ['scripts/guard.py']}`。只有「分兩次」躲得掉。
- **未驗證**:我沒有在真實 vault 上端到端跑「改節點加重建索引再過 doctor --ci」,「doctor 不會報」是從程式推論的。
- 佐證:`scripts/lumos:44461-44462`(removed 只比 pairs)、`scripts/lumos:44466`(whole 只合併同範圍的兩端)。
- **建議**:把「同一個 `(節點, 殘留指標)` 在 base 有的 `about_code`、`test_files`、`tests` 項目,head 沒有」也算 removed。

## F2 只改綁定測試檔裡別的地方(輔助函式、斷言、夾具)
severity: major
blocking: 是 — 把綁定測試掏空而不碰測試名,就不會升 high,而合約的守備就是靠那支測試。
引句:「if ln.startswith(("+", "-", "@@")) and rx.search(ln):」
攻擊步驟與判定:
- **根因**:`tests_of` 只在 `-U0` diff 的增刪行或 hunk 標頭出現綁定測試名時才算命中。
- **步驟**:
  1. 測試檔 tests/test_g.py 有輔助函式 `helper_assert`(含 `assert x == 1`)與綁定測試 `t_guard_one`(內容只呼叫 `helper_assert(1)`)。
  2. 把 `assert x == 1` 改成 `assert True`,測試名沒出現在 diff。
- **函式層實驗**:`_residual_tier_hits(repo, B..HEAD)` 輸出 `{}`(預期應升 high)。
- **同族**:
  - 夾具檔、資料檔、conftest 這類不在 `test_files` 的檔,同樣不會命中。
  - hunk 標頭取的是前一個 def,輔助函式在綁定測試之前時標頭是輔助函式本身。
- 佐證:`scripts/lumos:44425-44442`(`_residual_diff_touches`)、`scripts/lumos:44481`。
- **建議**:改動只要落在 `test_files` 的任一行就升 high,或綁定測試檔整檔算命中。

## F3 同一反例用「合約改一個字」重問,或刪帳列重問
severity: major
blocking: 是 — 「同一個反例只准問一次」可以被攻擊者機械繞開,取得第二個代理的 untestable 並記成殘留。
引句:「——同一個反例只准問一次(編號不分大小寫與標點),不能換代理重問到聽見想要的答案」
攻擊步驟與判定:
- **根因**:問答的鍵是 `(節點, 合約指紋)`。指紋是合約內文去掉空白與標點後的雜湊,改字詞就換指紋;帳檔也沒有任何防刪或防改機制。
- **步驟 a(改字詞)**:
  1. 對 guard-kill 的 KEY 行問 `--case c9 --verdict testable`,rc 0。
  2. 把行內「guard kill rc 優先序」改成「guard kill 目前 rc 優先序」。
  3. 再問 `--case c9 --checker opus/... --verdict untestable`,rc 0。
  4. 兩次問答都留在帳上。舊的 testable 屬於舊指紋,doctor 與 `--add` 都不會看到。
- **步驟 b(刪帳列)**:
  1. 在 `docs/.governance-log.jsonl` 問 testable,再要求重問:rc 2,被擋。
  2. 用腳本刪掉 `"residual-ask"` 那行,再問 untestable:rc 0,✓。
  3. 帳檔沒有雜湊鏈,`git diff` 只看到淨 +1 行。
  4. 刪的若是已提交的列,也沒有任何檢查報「帳少東西」。
- **補充**:`--checker` 只驗 `<模型>/<日期>` 的字串形狀,可以自己填,沒有第二個代理存在的證明。這也是攻擊者宣稱的能力範圍,放在一起記。
- 佐證:`scripts/lumos:18849-18855`(`_residual_claim_fp`)、`scripts/lumos:18925`(prev 比對)、`scripts/lumos:14566-14592`(`_gov_vc_gate_events` 無完整性檢查)。
- **建議**:
  - 問過 testable 就在節點層記黑名單:反例編號或殘留一輩子不准改成 untestable,不綁指紋。
  - 或讓推送前閘檢查帳的 residual-ask 列只增不減。

## F4 只靠索引判分級,索引與圖譜的對應在 pre-push 之外沒有強制
severity: minor
blocking: 否 — 現有 doctor --ci 在 pre-push 會報「索引對不上」,F1 之外的手改索引都被擋住;這條只記錄 F1 補完後仍留著的缺口。
引句:「拿掉殘留本身要過代碼審,分兩次推送也躲不掉」
攻擊步驟與判定:
- **現況**:`--no-verify` 與 CI 外沒有其他旁路。改名檔案(`--no-renames`)、刪索引(missing 加 pairs 差集)、讓索引讀不出(`head_bad`)這三條我都對照過程式,看起來都升 high。
- **殘留風險**:一個 AI 編排者以為「不要 doctor 報」就夠,實際上 F1 證明只要圖譜與索引一起改就一致。
- 佐證:`scripts/lumos:2175-2181`(doctor 的警告)。

## 實驗環境
- 函式層實驗用 `/private/tmp/claude-501/.../scratchpad/cr-rc2-資安/` 的一次性 repo,以 `SourceFileLoader` 載入 `scripts/lumos`。
- F3 在該目錄下 `git clone` 的副本上跑,沒動原 repo。實驗目錄已刪,沒有程序開著。

總結:最高等級 major,共 4 條 finding,其中 blocking 3 條(F1、F2、F3)。
