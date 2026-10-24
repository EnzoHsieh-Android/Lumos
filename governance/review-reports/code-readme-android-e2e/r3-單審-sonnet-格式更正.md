severity: major

## F1 StrictMode 那一項「沒打開就列成跳過」與計劃筆記的代價條款矛盾(最近一次修補寫錯)
severity: major
blocking: 是
引句:「系統內建的檢查（StrictMode）有沒有抓到資源沒關、註冊沒取消、畫面被留住這類違規（要專案在測試版自己打開，沒打開就列成跳過）。」
出處:
- ``file: `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md:37` ``。「跳過」的條件是 `.lumos/macrobench.json` 的 `stability.strictmode` **沒宣告**。計劃原文寫「[代價:宣告了卻沒真的開,零筆照樣判通過,只有實驗室那條人工驗收會發現…]」。
- ``file: `scripts/templates/android-stability-collect.sh:439-440` ``。沒宣告 strictmode 時回傳 `unsupported`。
- ``file: `scripts/templates/android-stability-collect.sh:443-449` ``。宣告了就只數日誌裡的 "StrictMode policy violation" 行。
- ``file: `scripts/lumos:39967-39976` ``。`violations` 為空就判通過。

失敗場景:專案在設定檔寫了 `strictmode: true`,測試版卻沒開 StrictMode。收集腳本照收,0 筆違規,這一項判「通過」,不會「列成跳過」。讀者看了 README 會以為 Lumos 能分辨「沒打開」。實際上它只看設定檔宣告,分辨不了 App 有沒有真的開。這是計劃自己承認的假綠風險,README 卻寫成相反的保證。上一輪修補把這句改成現在的樣子,新句子仍然寫錯。

建議改法:改成「要兩件事都做:專案在測試版自己打開 StrictMode,並在設定檔宣告;沒宣告就列成跳過。宣告了卻沒真的打開,會被誤判為通過」。英文版對應句同步改。

## F2 「容許誤差正在用實機資料重新校正」把排定的未來工作寫成進行中
severity: minor
blocking: 否
引句:「的容許誤差，正在用實機資料重新校正。」
出處:
- ``file: `docs/lumos-toolchain-knowledge/Projects/Macrobenchmark退步提醒_計劃.md:92` ``。內容是「REVISIT:2026-12-21 …有消費專案的真實數據後,用同一台裝置重跑同一版本至少 5 次量浮動,重訂預設值」。這是排定在 12-21、且要等消費專案數據的回頭檢查。
- ``file: `docs/lumos-toolchain-knowledge/Projects/Macrobenchmark退步提醒_計劃.md:48` ``。「先用 10%,見 2026-12-21 的回頭條件」。

失敗場景:找不到任何「正在進行」的校正工作,讀者會誤以為有人正在做。
建議改法:改成「容許誤差目前是暫定值(預設 10%,另有 1 毫秒下限),預計用更多次實機重跑的數據重訂」。英文版同步。

## F3 「把 skill 和每個工具都固定在同一個版本」與 SKILL 不符
severity: minor
blocking: 否
引句:「我們把 skill 和每個工具都固定在同一個版本，升級時要重新驗過」
出處:``file: `skills/lumos-android-evidence/SKILL.md:12-19` ``。釘的是各自不同的版本:skill 是一個 commit,Perfetto 是 v57.2,NDK 是 28.2.13676358。「升級要重驗」有據,「同一個版本」沒有。
失敗場景:讀者以為只有一個版本號要對。
建議改法:改成「各自釘在固定版本」。英文版 "pinned to fixed versions" 沒有這個毛病,中英已經不對等。

## F4 「Lumos 只補官方沒涵蓋的部分」是找不到出處的否定宣稱
severity: minor
blocking: 否
引句:「Lumos 只補官方沒涵蓋的部分：判斷到底有沒有變慢、分辨問題出在哪一種畫面寫法、抓出第三方套件忘了釋放的記憶體，以及把過程寫成紀錄。」
出處:
- ``file: `docs/lumos-toolchain-knowledge/Projects/Android逐層診斷_計劃.md:25` ``。PRIOR-ART 寫「全借用,skill 只串流程與收據」,沒有任何一處列出「官方沒涵蓋什麼」。
- ``file: `skills/lumos-android-evidence/SKILL.md:16` ``。官方 skill 附的錄製腳本 `cpu_profile`、`heap_profile`、`java_heap_dump` 其實涵蓋了錄製。
- ``file: `skills/lumos-android-evidence/SKILL.md:139` ``。官方的 `[SQL]`/`[INFERRED]`/`[GAP]` 標籤與報告流程也被沿用。
- 這句清單沒提 L2 的 simpleperf 與 L3 的快照分析。這兩層用的不是 android-profiler skill 的分析步驟,讀者會誤解成它們是官方 skill 的一部分。

建議改法:改成可由計劃筆記支持的說法,例如「分析卡頓的步驟照官方,Lumos 負責判斷要不要往下、串各層工具、並把過程寫成可重跑的紀錄」。

## F5 查證紀錄內容與可重現程度的敘述偏強
severity: minor
blocking: 否
引句:「手機型號與狀態、安裝的 App 版本、每一條查詢與預期結果、為什麼要往下一層，全都放在同一個資料夾」
出處:
- ``file: `skills/lumos-android-evidence/SKILL.md:32` ``。記的是「從裝置 pm path 拉實際安裝的 APK 算 sha256」,是檔案雜湊,不是 App 版本。
- ``file: `skills/lumos-android-evidence/SKILL.md:23` ``。原始檔(Trace、perf.data、快照)只留在本機 artifacts,進版控的只有紀錄目錄。
- 同章開頭那句「別人照著重跑，會得到一樣的結果」,實際需要本機還留著原始檔。`rerun.sh` 重跑的是對那些檔案的查詢,不是重新量測。
- ``file: `skills/lumos-android-evidence/SKILL.md:71` ``。L2 的數字「不能跟 L0 比快慢」。

建議改法:「安裝的 App(用檔案指紋比對)」;「別人拿到同一批原始檔,照 `rerun.sh` 重跑查詢,會得到一樣的結果」。

## F6 「看七件事」的主詞與細節和機制不完全對得上
severity: minor
blocking: 否
引句:「Lumos 的收集腳本會在手機上反覆打開又關掉同一個畫面，看七件事：」
出處:
- ``file: `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md:21` ``。開關畫面由專案自己寫的驅動(UI Automator 測試,或之後的 Maestro)負責,收集腳本只排順序與收資料,判斷由 `lumos macrobench --stability` 做。
- ``file: `scripts/lumos:39998-40000` ``。七項要門檻檔裡寫了對應 `check` 才會被判。
- ``file: `scripts/lumos:39867` ``。第一項(沒人指著的記憶體)其實只量原生(C/C++)記憶體。README 第一條沒說是原生,Java 的是第二條。

失敗場景:讀者以為裝上就自動看七件事,不知道要先寫門檻檔、寫驅動。
建議改法:補一句「七項各自要在門檻檔寫一條才會判」;第一條加「(C/C++ 那側)」。

## F7 中英圖與替代文字的小差異
severity: minor
blocking: 否
引句:「"Android tool" if en else "官方工具","gold"」
出處:``file: `assets/readme-diagrams/generate.py` ``(android_scene 的標籤與 desc)。
- 中文圖 L2 的標籤是「官方工具」,英文是 "Android tool"。simpleperf 是 Android NDK 附的工具,中文「官方工具」容易被讀成跟 L1 的「Google 官方」同一個東西。
- 中文圖輸入框寫「記憶體與閃退」,英文只寫 "Open and close a screen, repeatedly",沒提閃退。
- 中文 `desc` 還留著「判人裁門檻」「盲測」「捷徑」,而 Systems 筆記 2026-10-25 條目說圖上的字已全改白話。`desc` 是替代文字,沒跟著改。
- 圖本身重新產生可重現(`generate.py --check` 24 張通過)。

建議改法:L2 中文標籤改「Android 工具」;`desc` 改成與 README 正文同一套白話。

## F8 白話:沒背景的人會卡住的詞
severity: minor
blocking: 否
引句:「UI 操作流程目前可以用 Maestro 寫成流程檔、綁回功能筆記當作重驗用的檔」
出處:README.md 該章。
- Maestro 沒有任何說明(UI 自動操作工具)。
- 「較慢的那一成幀，從 4.3 毫秒變成 10.4 毫秒」:「幀」沒解釋。這個數字其實是每幀的 CPU 耗時,見 ``file: `docs/lumos-toolchain-knowledge/Verification/2026-10-23_Android驗證收據第零階段試跑.md:25` ``(frameDurationCpuMs P90 4.3→10.4)。目前寫法會被讀成「整幀時間」。
- simpleperf 在表格裡只有名字;`MainActivity.kt` 沒說是實驗 App 的檔。

建議改法:Maestro 補「(用文字描述點哪裡的畫面操作工具)」;「幀」補「(畫面每重畫一次)」,並寫成「每畫一幀花的處理器時間」。

## 其他逐項判定
- 實驗結果其餘數字都有出處:SM-X710、8 毫秒、第 36 行、多 5 個、10485760 位元組(5 輪乘 2 MB)、`libfakesdk.so` 與 `PlayerActivity.onCreate`、三種畫面寫法都歸對類並指到函式、盲測三種都還原。
- 圖譜鏡頭:固定席節點 `Systems/README圖產生器.md` 沒有 ★INVARIANT★ 合約行。diff 只新增 `android_scene` 與 SCENES 一個鍵,不改既有場景。`generate.py --check` 重跑通過,所以不影響它宣稱的「可重現、驗 XML」行為。
- 「收據」兩字:README 兩版與兩張 SVG 的 grep 都是 0。

## 逐句核對表

| 句 | 出處 | 判定 |
|---|---|---|
| 兩件事:變慢、記憶體 | SKILL:28、39 | 一致 |
| 一層一層查到函式與行號 | SKILL:69-108 | 一致(含 [INFERRED] 例外) |
| 每步寫成紀錄,重跑得一樣結果 | SKILL:137-143 | 偏強,見 F5 |
| 照官方 android-profiler skill | SKILL:14、44 | 一致 |
| Lumos 只補官方沒涵蓋 | 計劃 PRIOR-ART | 找不到出處,見 F4 |
| 先量體溫再抽血(有些工具改變 App、快照含個資) | SKILL:25、71 | 一致 |
| L0:Macrobenchmark、基準、人訂標準 | SKILL:24、39 | 一致 |
| L1:逐毫秒紀錄、Compose/XML | SKILL:33、53-57 | 一致;「逐毫秒」為口語,Perfetto 是奈秒時間戳 |
| L1 往下條件 | SKILL:63-67 | 一致(省略 Compose 分支與 GC 轉 L3,可接受) |
| L2:simpleperf 每毫秒、還原手機設定 | SKILL:86、100-105 | 一致(`-f 1000`);「次數最多就是兇手」偏強,SKILL 有 [INFERRED] |
| L2 往下:大量建立物件 | SKILL:108 | 一致 |
| L3:快照找變數 | SKILL:126-133 | 一致 |
| 固定版本、升級重驗 | SKILL:12-19 | 部分不符,見 F3 |
| 專抓第三方套件忘了呼叫 release | 計劃:21 | 一致 |
| 七件事 | 計劃:61、scripts/lumos:39998 | 項目一致;第 6 項有誤,見 F1、F6 |
| 凍結 0.7 秒 | 計劃:35 | 一致 |
| 記憶體類問題跳 L3 | SKILL:39 | 一致(需有人裁授權,圖與限制段有提) |
| 提交前找不知情的 AI 重判 | SKILL:143 | 一致 |
| 實驗結果各條 | 三篇 Verification | 一致;「幀」見 F8 |
| 限制:一台平板、一個實驗 App | 驗收紀錄 valid_under | 一致 |
| 限制:只提醒不擋推送 | 驗收門檻計劃:21、S7 | 一致 |
| 限制:快照預設不錄、7 天刪 | SKILL:25、sh:127-140 | 一致;只刪 `heap-*.pftrace`,heap_profile 目錄要自己刪,README 末句「用完要自己刪」已涵蓋 |
| 限制:容許誤差正在校正 | 退步提醒計劃:92 | 不一致,見 F2 |
| 限制:Maestro、下一步 | UI 測試工作流計劃(maestro 已交付)、記憶體計劃 REVISIT 2027-01-31 | 一致 |
| 怎麼開始用 | 退步提醒計劃:115 | 一致 |
| 中英對應 | README.en.md | 各段同一件事,沒有一邊多講或少講,版面之外的差別只有 F3 和 F7 |

總結:全篇最高為 major
