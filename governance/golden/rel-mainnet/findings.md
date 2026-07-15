# rel-mainnet · design-loop findings 語料（3 輪 panel，2026-07-15）

> 狀態：**人裁實質收斂**（2026-07-15）——3 輪 cap 到頂，r3 clean（canary 3/3 + 存活全 minor），唯 capture-recapture 殘餘 2.50≥1.0 未過（推估 ~2-3 條 minor 未發現，交實作真測接）。非 gate-clean，裁定記入計劃節點 ADR。
> spec 快照見同目錄 `spec.md`（＝`Projects/關係層主網_實作計畫` v4）。
> panel 編制：每輪 3×sonnet 異鏡頭（各帶 canary、全過 haiku 難度探針）+ Codex（gpt-5.6-sol）否決席讀 repo + opus 批次辯方（偏離：逐條獨立辯方，經濟考量，三輪同）。

## 輪次帳（canary log：CANARY-084fc018/f35966e1/12720deb｜c2ecfd05/59f043c6/bac63273｜3cff7b86/e5b90b51/0bda2d78）

| 輪 | canary（型別/探針） | 抓到? | 去重候選 | 辯方裁決 | 存活硬傷 → 折入 |
|---|---|---|---|---|---|
| r1 | a 壞交叉引用(recraft×1)/b 未定義旗標/c 未定義欄位(recraft×1) | 3/3 | 24 | 駁 3 降 18 | **D5** cascade-id 淨化不可實作(blocker)→生成式消解、**D10** O_APPEND 宣稱過強→bytes helper+誠實降級、**D16** 「續」無交付→resume、D4 輸出協議 |
| r2 | d 憑空夾具(recraft×1)/a 壞引用/b 未定義旗標 | 3/3 | 12 | 駁 1 降 7 | **R1** cascade-id 無鑄造者+交接通道封死(blocker)→dispatcher mint+stderr 行式 schema、**R3** root 全鏈語意、**R4** header 寫前驗證、**R12** 選擇端 first-match 錯項 |
| r3 | c 未定義欄位(recraft×1)/d 憑空快照檔(recraft×1)/a 壞分款引用(recraft×1) | 3/3 | 8(≥major) | **全降 minor** | 無——15 句級殘留折 v4，clean round |

## 決定性時刻（供 replay 校準）

- **r1 Codex**：dispatcher tuple 撞 sys.exit、impact 已有 --json（spec 引舊輪結論，code 已演進）、repo ledger 全是 `open("a")`——三連行號級。
- **r2 A 席**：cascade-id 無生產者（「公式存在≠有人鑄造並交棒」）——三席合流的主傷口，v2 修 D5 只顧格式沒顧資料流的教科書案例。
- **r2 辯方**：supersede-once 閘反殺「同秒同決策重用」（4302 區 code 反證）——Codex 和審計員都沒想到的可達性論證。
- **r3 辯方**：8 條 major 全數以 spec 原文駁倒/降級（header 全域格式 spec:95、rc=0 範圍 spec:130——兩席審計員漏看已釘的文字）。**教訓：多輪折入後，審計員開始把「已釘但寫在別段」的合約報成缺口——收斂末期的 findings 要先過「spec 全文有沒有」再過「code 有沒有」。**
- **capture-recapture 的誠實極限**：r3 存活全 minor 但 5/8 單席發現→殘餘估 2.5——framing 逼每輪必交 minor 時，數字枯竭壓不到底（skill 自承），人裁是設計好的出口。

## 方法論收穫（meta）

- **嚴重度軌跡 = 收斂的真信號**：blocker(地基)→blocker(資料流)→全 minor(措辭)，架構三輪未翻。比 count 類指標抗 framing 汙染。
- **「修補引入新洞」是 fold 的固有稅**：r2 主傷口（無鑄造者）是 r1 修補（生成式 id）造的；r3 主候選（格式鏈）是 r2 修補（header/全域格式）之間的縫。每輪審 delta 的價值即在此。
- **跨家族 Codex 三輪皆有行號級貢獻**（第三份設計連續驗證否決席常駐的價值）；**opus 批次辯方三輪駁倒/降級 29/44 條**——沒有辯方，spec 會被過度修補污染。
