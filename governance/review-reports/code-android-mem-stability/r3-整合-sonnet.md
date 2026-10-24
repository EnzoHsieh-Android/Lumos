severity: major

# 第 3 輪整合席報告(合約與圖譜一致,docs 包,sonnet)

審了 r3-pkg-docs.patch。程式與測試是對照用的工作樹真檔,HEAD f0d41453。共 1 條 major、6 條 minor。

整體結論:接手的人照文件做,大部分描述對得上程式。我逐項對過回傳碼與擋下清單、環境變數名、保留規則、七種判定、官方分級表、frozen 走 L1、範例佔位,都符合。有三處對不上:第一條 major 是 skill 指定的指令漏了一個擋下訊息,可能讓記憶體洩漏被記成「L0 通過」;另外還有一處自相矛盾,和兩處沒有守衛。

## Findings

### 1. skill 指定的 `--json` 路徑,沒有 check 條目時完全無聲,洩漏會被記成「L0 通過」
severity: major
blocking: 是
引句:「L0 改跑 `lumos macrobench --json --stability <那份結果檔>`」
- 失敗場景:
  - 結果檔寫了 native_unreachable 差值 10485760 位元組,但門檻檔 `thresholds` 是空的,或忘了寫 `check` 條目。
  - 照 skill L0 第 8 步跑 `--json`,`threshold_failures`、`threshold_passed`、`threshold_skipped` 三欄全空。
  - skill 接著寫「都沒有 → 收據記 `L0 通過` 後停」,洩漏就被記成通過。
- 條款 S20 寫「給了 --stability 卻沒有 check 條目要印出沒有東西可判」。程式只在文字模式印這句(`/Users/enzo/orca/workspaces/lumos-toolchain/android-mem-stability/scripts/lumos:40111`,條件含 `not as_json`)。JSON 模式沒有任何旗標或欄位。
- 計劃自己寫「這類守衛最常見的失效是讀不到所以全綠」,這裡正是同一種失效。綁定測試 `t_android_memstab_unreadable_never_passes` 只驗文字模式。
- 兩版同一案例(臨時專案只有 `s.json` 與空門檻檔,指令 `lumos macrobench --repo <專案> [--json] --stability s.json`):

| 版本 | 文字模式 | `--json` |
|---|---|---|
| 修前 44d93aba | 無警告,rc 0 | 三欄全空,無警告,rc 0 |
| 修後 f0d41453 | 印「給了 --stability,但門檻檔裡沒有寫了 check 的條目…」,rc 0 | 三欄全空,無警告,rc 0 |

- 沒有門檻檔時 JSON 輸出也一樣。
- 歸因:有證據的原有漏查。修補只補了文字模式,未涵蓋 skill 實際指定的路徑,對應案例 G6 只算修了一半。

### 2. S7 的後半句沒有被它綁的測試守住
severity: minor
blocking: 否
引句:「收集腳本只收量測開始之後的日誌、一筆違規只算一次 [test:t_android_memstab_strictmode]」
- `t_android_memstab_strictmode`(`scripts/test_lumos.py:18246`)只餵假的 `stability.json` 給 lumos 判定,從不跑收集腳本。
- 「只收量測開始之後」「一筆違規只算一次」這半句,實際由 S22 的 `logcat_scope` 與 S16 的 `driver_status` 順帶守住。S7 這行沒有綁它們。
- 失敗場景:有人把 `strictmode_result` 改成堆疊行也算一筆。S7 綁的測試仍綠,要靠別條才會紅。`spec-trace` 顯示「綁了 ✓」,但綁定強度被高估。
- 歸因:有證據的原有漏查(綁定寫法在修前就如此)。

### 3. S24 的 Big5 子句在沒有該語系的機器上自己略過
severity: minor
blocking: 否
引句:「主機語系是 Big5 這類非 UTF-8 時輸出照樣是 UTF-8」
- 測試 `scripts/test_lumos.py:19030` 的 `if big5 == "big5":`,沒有語系就只印「(略過 Big5 語系那條…)」,仍判綠(`:19037`)。程式碼自己的註解也寫「Linux CI 多半沒有,這段不跑」。
- 這台 Mac 有 `zh_TW.Big5`,我跑 `-k android_memstab` 303 案例全綠,該條有驗到。
- 失敗場景:CI 上 `-P` 改回 `-I`,S24 這句沒有任何守衛會紅。
- 歸因:未判定。CI 上實際有沒有語系我沒查。

### 4. reference.md「表格以外的欄位會被當成寫錯」與程式不符
severity: minor
blocking: 否
引句:「寫了表格以外的欄位會被當成寫錯、回 2」
- 程式 `scripts/lumos:39805` 允許 `device_model` 與 `version`。計劃本身也寫「`device_model` 照舊選填並照舊篩裝置」,但 reference 的表格與句子沒列它。
- 實跑 `check` 條目加 `"device_model": "SM-X710"`,`--check-config` 回 0、「macrobench 設定與門檻檔都合格」。
- 接手的人照 reference 會以為不能寫 `device_model`,或誤刪它。
- 歸因:有證據的原有漏查。修前 44d93aba 的 reference 與 `scripts/lumos` 都已是同樣寫法。

### 5. 範例佔位:只擋日期,`decided_by` 佔位照樣過
severity: minor
blocking: 否
引句:「日期佔位不改會被 --check-config 擋下」
- 這句話本身是對的。但 skill 與 reference 靠它擋「照抄範例」,實際只擋日期。
- 實跑:把 `stability.test_data` 的日期改成真日期、`decided_by` 留 `"<裁定的人>"`,`--check-config` 回 0。
- 失敗場景:AI 只改日期就打開 `test_data`,等於寫下「人裁」宣告,收集腳本照錄 Java 快照。
- 計劃已把「AI 改設定檔就能打開宣告」記為信賴範圍。但文件暗示佔位會被擋,與實際不一致。
- 歸因:有證據的原有漏查。修前 `scripts/lumos:39446` 起的檢查邏輯相同。

### 6. 逐層診斷計劃對「沒有保存裁定」的停點與「宣告」語意前後不一
severity: minor
blocking: 否
引句:「skill 應指示停在 L2 並記 `[GAP] L3 未授權`,不得錄記憶體快照」
- 同一份補丁的 L0 列寫「沒有 `stability.test_data` 宣告時停在 L0,收據記 `[GAP] L3 未授權`」。記憶體類 check 根本不經 L2,S6 條款字面(停在 L2)對這條路徑不成立。
- 補丁只在 manual 備註說兩句「照舊成立」,沒有改條款句。
- skill 用「有宣告才做」,但程式(S15)要求 `value: true`。`value: false` 也是一份宣告,skill 字面會讓人去 L3 錄快照。
- 歸因:有證據的原有漏查。

### 7. 統計化計劃指向不存在的 REVISIT
severity: minor
blocking: 否
引句:「併做 [[Systems/macrobenchmark-adapter]] 那條容差實測的 REVISIT」
- `Systems/macrobenchmark-adapter.md` 只有兩條 REVISIT:基準裡的舊情境(2026-12-21),以及 NaN(已 closed)。沒有容差實測那條。
- 容差實測的 REVISIT 實際在 `Projects/Macrobenchmark退步提醒_計劃.md:92` 與 `Verification/2026-10-23_macrobench實機端到端.md:29`。
- 三個月後的人點過去找不到,會以為這件事沒人記著。
- 歸因:有證據的原有漏查。`git show 44d93aba` 已有同句。

## 已驗、無 finding 的項目

- **spec-trace(S1–S26 是否綁到真測試)**:`lumos spec-trace` 結果是 26 條、綁了 23、靠人 3(S17–S19)、懸空 0、壞名 0。`python3.14 scripts/test_lumos.py -k android_memstab` 303 案例全綠。
  - 讀過各測試的斷言,除 #2、#3 外,每條都對得上條款全文,例如 S4 每級上下界、S20 的 15 種壞形狀。
  - 改壞實驗:在 f0d41453 的暫存工作樹把 `stop_logcat` 的 `time.sleep(SETTLE)` 拿掉,`collect_never_fakes_ok` 與 `collect_logcat_scope` 轉紅,所以 PITFALL「日誌最後幾行被丟」有守衛(但靠「一開就斷」那案紅,不是「晚到的行」那案)。
- **行為描述對得上程式**:
  - 回傳碼與擋下清單:`collect.sh:14,339-354,496-499`。
  - 環境變數 `ADB`、`TP`、`JAVA_HEAP_DUMP`、`LUMOS_STABILITY_SETTLE`(預設 2)、`LUMOS_STABILITY_STOP_TIMEOUT`(30)、`LUMOS_STABILITY_LONG_TIMEOUT`(1800),以及 `CYCLES`、`ANDROID_SERIAL`。
  - 保留規則:只刪 `heap-*.pftrace` 超過 7 天、`logcat.raw` 必刪。
  - 官方分級表與 `scripts/lumos:39772-39773` 一致。
  - exits 崩潰類不靠 pid;driver failed 或 pid 變了時五種跳過、exits 與 strictmode 照判。
- **事故筆記**:`dispatch-lens` 的根因屬實(`scripts/lumos:60698` 用 `_codeloop_git_branch(root)` 讀 marker)。repro 我重跑了:在 Backend_improve 跑 `dispatch-lens 7d17bd73..44d93aba`,表態行印「分支 EnzoHsieh-Android/Backend_improve,版本 abee7dee」。小瑕疵:筆記寫「在 `cmd` 裡」,實際函式是 `cmd_dispatch_lens`。
- **lint 與 doctor**:八篇改動節點 `lumos lint` 全 0 問題。`lumos doctor` S6 提醒 `Systems/android-stability-collector.md` 沒被總索引連到,是不擋的提醒,同樣的有 29 篇,有先例。
- **新增 WHY/PITFALL 之間無矛盾**:沒有與 `Android逐層診斷`、`Macrobenchmark退步提醒`、`macrobenchmark-adapter`、`派工鏡頭` 既有決定衝突(「不接裝置」「不加 Lumos 指令」都靠「收集腳本不是 lumos」成立)。

## 固定席節點逐條

這包只改 md 與 skill 文件,沒動 `scripts/lumos` 與 `scripts/test_lumos.py`,下列都不受影響。

| 節點 | 判斷 |
|---|---|
| `Issues/vendored測試套件在消費端假紅` | 文件只描述「登記 `_VENDORED_TREE_FILES`」,與該事故一致,沒有改任何登記 |
| `Systems/lumos-cli-read` ★INVARIANT★ | 新筆記是一般節點,沒有 superseded 或 stale 行,search 預設排除規則不受影響 |
| `Systems/測試假綠形態` ★INVARIANT★ | 本包沒新增「還原翻紅釘」;PITFALL 綁定的測試我用改壞實驗各驗過一次 |
| `Systems/bound-tests-gate` | 文件變動不改閘行為,綁定強度的缺口見 #2 |
| `Systems/guard-kill` | 不受影響 |
| `Systems/lumos-cli-lifecycle` | 不受影響 |
| `Systems/design-loop` | 不受影響 |
| `Systems/pitfalls-code-loop` ★RISK★ | 不受影響 |

## 殘留必答

本包沒有 `governance/residual-index.json` 與 `docs/.governance-log.jsonl` 的改動,鏡頭也標「算不出來」,所以「有沒有換編號或改字重問、第二個代理是不是另一個代理」這題我答不了,判未判定。

## 三問與限制

1. **原問題的修復效果有何行為證據?**
   - 本席範圍內(docs)只有 G6 與 Issue 兩項可獨立驗。
   - G6 只修了一半:文字模式修好,JSON 模式沒有(見 #1,兩版指令與輸出已列)。
   - Issue 的 repro 在這台機器上成立。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?**
   - 有門檻、有 check 條目的正常路徑,文字與 JSON 輸出都照常(`t_macrobench_*`、`check_compat` 綠)。
   - 錯誤路徑成立:壞結果檔回 2。
   - 相鄰路徑 `--json` 沒有走到修補,見 #1。
3. **新發現的同一案例在修前、修後各是什麼結果?** 都已寫在各條。#1 兩版同缺,#4、#5、#6、#7 兩版程式與文字相同;#2 是兩版相同的綁定寫法,#3 的 CI 環境未驗。

**未驗與限制**
- 計劃寫「其餘情況都寫出結果檔並回 0」(`android-stability-collect.sh:500` 的 `except BaseException: ... raise` 會讓意外例外變 traceback,rc 1)。我沒造出具體輸入,不標 finding。
- 計劃寫「每個子程序都自成程序群組」,但日誌串流 Popen 沒有(`collect.sh:374`)。我沒找到會失敗的場景,不標 finding。
- 實機相關的敘述(Verification 筆記、`dumpsys` 格式、`java-profile-*` 暫存檔位置)沒有裝置可驗,未判定。
- 我沒碰 adb 連著的裝置。暫存清理:兩個臨時工作樹與臨時專案目錄已用字面路徑刪除,`/tmp/lumos-seat-work/code-android-mem-stability/整合-sonnet/` 已移除。我自己跑紅燈留下的四個 `gctl-run-*` 現場也已逐一刪除。

最嚴重 severity:major,blocking 共 1 條。
