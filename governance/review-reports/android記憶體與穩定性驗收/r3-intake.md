preflight-4: ran

# android記憶體與穩定性驗收 r3 收貨(上限輪)

審材 r3-snapshot.md(128 行,LUMOS-SPEC f32c6aa1);四席全新 sonnet,派工詞寫明末輪火力集中在 blocker 與 major。四席交回後才一起從逐字稿存檔。整合席檔級寫 major、內文有 blocker,退回該席自己改檔級。四份 quote-check 全錨。

## 編排者重現(實驗室 SM-X710,上一輪實驗留在裝置上的實驗版 App)

- I1(整合席:libmemunreachable 的根集合不含 Java 堆積,SDK 物件活著也會被判沒人指著):開著 NativeLeakActivity(release=true、kb=4096,FakeSdk 用 Java 的 long 欄位握 4 MB),`dumpsys meminfo --unreachable` → `0 bytes in 0 unreachable allocations` → MISS(重現不到;活著時不誤報)。
- G1(通才席:掃描前沒有強制回收會漏報):release=false、kb=4096 開畫面後按返回,1 秒後掃 → `4194304 bytes in 1 unreachable allocation`;`am send-trim-memory … RUNNING_CRITICAL` 後與再等 20 秒都一樣 → MISS(重現不到;關畫面一秒內就抓到,不需要另外觸發回收)。
- B1、I3(driver 失敗把 exits 壓成跳過):讀 r3 快照的 driver WHY 與 S11、S19,三處字面互相矛盾 → HIT。
- B2(logcat 沒起點):席位在 SM-X710 查 `logcat --help` 有 -T;沒帶 -T 時先倒出緩衝歷史 → HIT。
- 其餘條目讀快照本文與既有程式即可判 → 逐條讀過,HIT。
- G8(分級表兩段都是 2.25 GB):對照 r1 讀到的 developer.android.com/google/play/vitals 表,6 GB 與 8 GB 兩列前景上限確實都是 2.25 GB → 已核對一致,照原文。

## 根因分組與修法

- driver 失敗的波及範圍(B1、I3):只跳過需要完整 N 輪的五種,exits 與 strictmode 照判。
- 日誌起點與計數單位(B2、G5):-T 量測開始時的裝置時間;只認 StrictMode policy violation 開頭那一行。
- 快照與掃描順序(B4):先掃再錄快照。
- 輸出、路徑與設定歸屬(G3、G7、I6、A1–A3、G4):文字輸出照 check 分支、條款補綁;--stability 相對路徑與 --update-baseline 的互動;沒有 results_dirs 時 --update-baseline 的行為;stability 段由 lumos 驗、收集腳本呼叫它;exits 的 kind 改名 type、device 改名 adb_serial、佔位改成 {{CYCLES}};驅動指令合成一條。
- 收據(G2、I7):快照查詢寫 expect=-,刪了快照也不會誤報;寫明增減收據驗不到。
- R8 與接入(I2、I5):加 mapping 設定還原類別名、沒給時標明;reference.md 加驅動測試與 Maestro flow 範例。
- 其他(B3、G6、I4、I8、I9):S8 改寫成 frames 欄位;exits 列出只回報的原因編號;ANDROID_SERIAL 給驅動;統計化第 6 條寫成已加;錄製設定副檔名 .pbtxt 用 # 寫 SPDX。

## 逐條去向

| id | 席 | 嚴重度 | 去向 |
|---|---|---|---|
| G1 | 通才 | major | 不成立(重現不到,見上) |
| G2 | 通才 | major | 折 |
| G3 | 通才 | major | 折 |
| G4 | 通才 | minor | 折 |
| G5 | 通才 | minor | 折 |
| G6 | 通才 | minor | 折 |
| G7 | 通才 | minor | 折 |
| G8 | 通才 | minor | 折(核對一致,照原文) |
| B1 | 邊界可執行 | major | 折 |
| B2 | 邊界可執行 | major | 折 |
| B3 | 邊界可執行 | minor | 折 |
| B4 | 邊界可執行 | minor | 折 |
| I1 | 整合 | major | 不成立(重現不到,見上) |
| I2 | 整合 | major | 折 |
| I3 | 整合 | blocker | 折 |
| I4 | 整合 | minor | 折 |
| I5 | 整合 | major | 折 |
| I6 | 整合 | major | 折 |
| I7 | 整合 | minor | 折 |
| I8 | 整合 | minor | 折 |
| I9 | 整合 | minor | 折 |
| A1 | 架構對齊 | minor | 折 |
| A2 | 架構對齊 | minor | 折 |
| A3 | 架構對齊 | minor | 折 |

## 修補因果

r3 的 B1、I3(driver 全部跳過)是 r2 修補加的 driver 來源帶出來的;B2 是 r2 改成串流日誌時沒寫起點;G2 是 r1 改寫的「刪了快照標成不能重跑」沒寫怎麼標;A1–A3 是 r2 新增的欄位與佔位命名。
