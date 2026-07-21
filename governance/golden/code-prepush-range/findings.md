# 收斂凍結：prepush主幹範圍修法（2026-07-21，實質收斂人裁）

spec 凍結版：見 `spec-ref.txt`。收斂形態：design-loop panel cap 3 輪、r3 首個輪有效（opus×2 canary 2/2）、設計本體 Codex 否決席確認解除、殘留全文件歷史衛生（已標作廢）、capture 殘餘卡門（singleton 結構病）→ 使用者裁實質收斂。緣起：[[Issues/code-loop守衛main-direct盲區]] 修法。

## 三個安全設計級教訓（本 loop 核心產出）

1. **留痕座標脫鉤（r1，三席互證）**：hook 逐 ref 檢的是被推送 ref 的 sha，但 pass/skip 留痕原讀當前 checkout HEAD——推非當前 checkout 分支時借錯分支留痕誤放/誤擋。→ `--at-sha`/`--branch` 由 hook 傳。
2. **fail-open 是守衛的錯預設（r2 Codex）**：「算不出比較基準就放行」把盲區升格成不需 `--no-verify` 的穩定繞法。→ 樞紐反轉：無基準改掃 `empty-tree..local_sha` 全部內容（倒向多掃）。
3. **非-heads 判定該用 remote_ref 目的地（r3 Codex）**：用 local_ref 判會誤擋 release tag（新 ref 全掃 high）與 CI `$SHA:refs/heads/x`（raw local_ref）。→ 用 remote_ref：heads 硬擋+skip 逃生、tag advisory。

## 存活 findings 處置（全數已折入或標作廢，無未修）

- r1（7）：留痕脫鉤＋首推 main 空 diff＋shallow＋既有測試崩＋anchor＋聚合成本＋自舉因果——全折 v2；其中 fail-open 決議於 r2/r3 反轉、r1 bullet 已標作廢。
- r2（4 major）：樞紐反轉×2＋--branch 鍵 bug＋git 語意——全折 v3/v4。
- r3（2 major）：非-heads remote_ref 收口＋summary TEST 同步——全折 v5/v6。

### 接受不修（附理由）

- **capture 殘餘卡 1.00**：singleton findings 結構病（三度實證：lumos-show／M1／本 loop）。
- **既有 marker 債（不折）**：`feat/x` vs `feat__x` 鍵碰撞、marker 綁 local_sha 不綁 range——屬既有 marker 設計面，出本 spec 範圍，指 [[Projects/code-loop必用守衛_計劃]] 待另案。
- **tag namespace gate 較弱**：非-heads high 走 advisory（tag 多指已審 commit；硬擋誤擋合法 release tag）——tag 內容 gate 另訂策略，記待辦。

## 審計員校準數據（golden 語料，本 loop 最有價值）

- **canary：r1 s1 missed／r2 s1 missed（同席連 2 漏，護欄觸發）→ r3 升 opus 後 2/2 全抓**。**同一席位 sonnet 漏、opus 接住＝漏抓是模型層非 spec 問題的乾淨實證**（前例混入 placement/lens 變量，本 loop 是純模型層對照）。護欄升級機制實效第 N 筆。
- **spec 每輪自我推翻前輪修法**：r2 反轉 r1 的 fail-open、r3 修 r2 的 self-base 過度反轉與非-heads 硬擋——「改守衛」的設計來回三次才收斂，密度證成 self-governance=high 的審查投入。
- Codex 否決席全程：r1 帶餌 finder＋r2/r3 無餌否決，每輪抓到同門全漏或 v-1 版自身引入的洞（fail-open 方向／self-base 過度／非-heads 誤擋）——跨家族作為「修法自身缺陷」偵測器的實證。
