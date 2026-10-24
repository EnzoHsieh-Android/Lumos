severity: major

## F1 快照「只留 7 天」的說法比實際保留期短，且是隱私承諾
severity: major
blocking: 是
引句:「快照只留在本機 7 天。」
- README.md:344 前後。英文版 README.en.md 同一點寫 `snapshots stay on the local machine for 7 days`。
- 實際行為：7 天清理只在下一次執行收集腳本時才會跑，而且只刪 `heap-*.pftrace`。
  - file: `scripts/templates/android-stability-collect.sh:127-141`
  - file: `skills/lumos-android-evidence/SKILL.md`，L3 第 2 步原文：「下一次跑收集腳本時,超過 7 天的才會被刪,不再跑就不會刪,用完自己刪」
- 失敗場景：專案宣告 `stability.test_data` 後錄了快照，之後不再跑收集腳本。快照會一直留著。L3 第 1 步的 `heap-profile-*` 目錄不符合檔名規則，永遠不會被刪。
- 受影響的是讀者對資料保存期限的判斷，因為快照可能含使用者資料。
- 重現：比對上列 SKILL.md 原文與 README 原文，兩者矛盾。我沒有另外跑指令。
- 建議改法：「快照放在本機，之後每次跑收集腳本時會順手刪掉超過 7 天的；不再跑就不會自動刪，用完請自己刪」。中英兩版一起改。

## F2 「Samsung Galaxy Tab S9」在全部筆記與驗收紀錄裡查無出處
severity: minor
blocking: 否
引句:「用一台 Samsung Galaxy Tab S9，和一個刻意埋了問題的小 App」
- 三份驗收紀錄與計劃筆記只寫 `SM-X710 / Android 16`。對全 repo 搜尋 `Tab S9`，只有這兩份 README 命中。
  - file: `docs/lumos-toolchain-knowledge/Verification/2026-10-23_Android驗證收據第零階段試跑.md:5`
- 失敗場景：型號名稱是作者自行對應型號代碼得來，核對者在 repo 內找不到依據。SM-X710 通常就是 Tab S9，所以事實大概率對，但沒有出處。
- 建議改法：改寫成「一台 Samsung 平板（SM-X710）」，與驗收紀錄的寫法一致。
- 這條沒有可重現的錯，所以降為 minor。

## 逐項核對結果（無問題的項目）
- **產生器**：我在 worktree 跑了 `python3 assets/readme-diagrams/generate.py --check`，輸出 `24 bilingual SVGs: validated, reproducible…`，rc=0。`android-e2e` 場景已在 git 追蹤，不覆寫別張圖，重跑結果相同。
- **L0 到 L3 的流程**：往下條件、記憶體類直達 L3、L3 要先有人宣告、版本釘選，都與 `skills/lumos-android-evidence/SKILL.md` 一致。
- **七件事**：native_unreachable、java_growth、instances、peak_vitals、exits、strictmode、frozen 共七項，與收集腳本和計劃筆記一致。凍結幀的 700ms 門檻也與計劃相符。
- **實驗數字**：4.3→10.4 毫秒、`MainActivity.kt` 第 36 行、Java 多 5 個物件、原生 10 MB（5 輪×2 MB）、三種畫面寫法歸類並指到函式，都與三份驗收紀錄相符。
- **「只提醒不擋推送」**：與 `Projects/Macrobenchmark退步提醒_計劃.md` 的 WHY 相符。「Maestro 流程檔可綁回功能筆記」與 `Projects/Android側UI測試綁圖譜工作流_計劃.md` 記載的 2026-07-02 已交付相符。
- **中英對應與圖**：中英兩版逐段對應，沒有一邊多講。兩份 SVG 的字與替代文字和正文一致。README 與兩份 SVG 都沒有「收據」二字。兩個 docs 連結的檔案都存在。
- **測試**：沒有新增測試。圖的可重現性由 `generate.py --check` 守住，足夠。
- **家節點 `Systems/README圖產生器`**：只新增一行紀錄，不影響它宣稱的行為。
- **表態記錄**：與這次改動無關，我沒有發現矛盾。

總結:全篇最高為 major
