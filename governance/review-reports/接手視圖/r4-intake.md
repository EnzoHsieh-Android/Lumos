# r4 intake — 接手視圖(代碼審驗收輪,外家 Codex,2026-09-07)

preflight-4: n/a(代碼審,非設計審)

材料:`r4-snapshot.diff`(r3 #6/#7 折入後、相對 HEAD 的 diff)、派工詞 `r4-codex-prompt.txt`(只驗 #6/#7)、報告本體 `r4-外家codex.md`(從逐字稿最後一個 `severity:` 切出;完整逐字稿 `r4-外家codex-transcript.md`)。
席位宣告 severity: blocker,1 條新 finding(#8)。#6、#7 驗收通過(席位各附 檔:行,四個指定案例與三種鄰居路徑都不放行)。

## 逐條

- **#8 `os.stat` 讀外部檔中繼資料零稽核事件 — HIT,折**。CPython 的 stat 家族沒有 audit event(席位實測 `os.stat("/etc/passwd")` 零事件),探針判綠。折法:匯入期間把 os 模組的 `stat / lstat / access / readlink / statvfs` 包起來,套同一套路徑政策(只准 hook 自己與標準庫本體);只包 os 模組名字——importlib 走 posix 模組原函式不受影響,hook 裡 `os.stat` / `os.path.exists` / `pathlib.Path.stat()` 都會經過。翻紅釘:stat / path.exists / pathlib stat / access 四種都要紅。
- **席位把這條標 blocker**:嚴重度照收(blocker 只能折,已折)。但要講清楚一件事:「不產生任何外部動作」這種宣稱是無底的——每一輪都能再找一個沒有稽核事件的讀取原語(下一個可能是 `os.getcwd`、`os.environ`、經 `posix` 模組直呼)。所以這輪同時把測試宣稱改成★精確範圍★(寫/建/刪/改權限任何檔、開子程序、開 socket、讀 hook 與標準庫以外的檔案內容 / 目錄清單 / 中繼資料)並★明寫殘餘面★(讀程序自身狀態、經 posix 直呼、其他無事件原語)。殘餘面要再縮就得動 hook 或不執行 hook,兩者都在範圍刀外。

## 帳與上限
- r4 已記(severity blocker、findings 1、folded 8;reviewed 指紋=席位看到的計劃版本)。
- ★這是第四輪,超過 standard 分級的三輪上限★:r4 的折法只有自己的翻紅釘、沒有獨立席驗收。照 skill:到頂沒過→停,攤給人裁。攤給 Enzo 的問題:①殘餘面(讀程序自身狀態、posix 直呼、無事件原語)可不可以接受;②要不要再派一輪只驗 #8;③還是改成「不執行 hook」(把人話判定與工具名單複製進 lumos、加漂移守衛)——那是範圍刀外的設計變更。
