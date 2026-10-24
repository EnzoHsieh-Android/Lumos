severity: major

## F1 第六件事「主執行緒做不該做的事」跟程式實際檢查的東西不符
severity: major
blocking: 是
引句:「- Whether it did forbidden work on the main thread.」
file: `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md:37`
file: `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md:60`

失敗場景:七件事裡的第六件對應判定項 `strictmode`。出處(計劃第 37 行)寫明檢查的是 StrictMode 的 VM 規則,也就是「可關閉物件沒 close、註冊沒取消、Activity 被留住」。這是資源和物件洩漏,跟主執行緒無關。第 60 行的表只說「N 輪期間這個 pid 的日誌 / 有一筆 StrictMode 違規」。README 寫成「在主執行緒做不該做的事」,讀者會以為它在抓主執行緒上的磁碟或網路操作。這是 StrictMode 的另一組規則,Lumos 沒有檢查,屬於誇大能力的事實錯誤。中文版對應句「有沒有在主執行緒做不該做的事。」也一樣。

建議改法:中文改成「有沒有出現系統內建檢查(StrictMode)抓到的資源沒關、註冊沒取消、畫面被留住這類違規。」。英文對應改成「Whether Android's built-in StrictMode check caught leaks such as an unclosed resource, an unregistered listener, or a screen kept alive.」。

主執行緒相關的是第七件事(凍結幀,出處是追蹤檔的幀時間線),它沒有問題。

## 其餘逐項查證
以下都已對過出處,沒有問題,不另列 finding。

- **快照保存的新寫法**:`scripts/templates/android-stability-collect.sh` 的 `prune_old_snapshots`(第 126 到 141 行)只在每次開跑時刪超過 7 天的 `heap-*.pftrace`。`skills/lumos-android-evidence/SKILL.md` 第 126 行寫「不再跑就不會刪,用完自己刪」。修補後的中英兩版都對得上。
- **平板型號**:SM-X710 在三份 Android 驗收紀錄裡都有。其中一份(`Verification/2026-10-23_Android驗證收據第零階段試跑.md:52`)寫「只有一台 Samsung」,所以 Samsung 加 SM-X710 成立。
- **實驗數字**:4.3 到 10.4(frameDurationCpuMs P90)、`MainActivity.kt` 第 36 行、Java 側多 5 個、原生 10 MB(5 輪各 2 MB)、700 ms 凍結幀,都與驗收紀錄和計劃一致。
- **其他宣告**:「只提醒不擋」「記憶體類跳過中間層直達 L3」「提交前找沒脈絡的 AI 重判」「skill 釘版本」都有出處。
- **盲測那句**:紀錄寫的是三種都還原,其中 B 只推到「綁定列多約 11 ms 純 CPU 工作」。README 的「三種都找到了問題所在」是可接受的簡化。
- **Maestro 那句**:計劃寫的是驅動「現在是 UI Automator,子案二換成 Maestro」。README 說的是 Maestro 能寫流程檔並綁回功能筆記,把它跟效能、記憶體一起變成端到端驗收是下一步。我沒找到說 Maestro 流程可綁回功能筆記的出處,但這一句不構成誇大。
- **產生器**:在修補後的 repo 跑 `generate.py --check`,輸出「24 bilingual SVGs: validated, reproducible…」,通過。
- **說明檔**:`assets/readme-diagrams/README.md` 的場景數 12、圖檔數 24 和 Android 條目都對。`data-kind` 已改成單詞 `android-record`。
- **中英兩版**:章節結構、七件事、限制清單逐段對應,沒有漂移。
- **「收據」兩字**:全文沒有出現。
- **圖譜鏡頭(LUMOS-IMPACT)**:這份 diff 不影響 README圖產生器 節點宣稱的行為。`generate.py` 只新增一個場景,沒動既有場景,`--check` 仍通過。節點新增的日誌行只是紀錄。

總結:全篇最高為 major
