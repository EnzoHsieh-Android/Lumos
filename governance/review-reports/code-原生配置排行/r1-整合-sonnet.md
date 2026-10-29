severity: major

整合視角共 6 條 finding,其中 3 條 blocking。主要問題是 S6、S23 兩條款的測試被我改壞後照綠,以及 e2e 傳預算變數那一行完全沒有測試。

我複製一份 repo,改壞正式程式後跑測試。未特別說明的實驗,都是在副本裡改一處再跑對應的 `-k` 子集。未改壞時 `-k android_native` 為 153 passed,`-k android_memstab` 為 389 passed。實驗副本與暫存已用字面絕對路徑刪除。

## 1. S6 的 Android 11(sdk 30)邊界沒有被測到
severity: major
blocking: 是(S6 是驗收條款,把下限改壞測試照綠)
引句:「("Android 10(29)", {}, "29", None, (True, "unsupported", "Android 版本不支援")),」
file: `scripts/templates/android-stability-collect.sh:32` 與 `:561` 是 `NATIVE_MIN_SDK = 30` 和 `res["android_sdk"] < NATIVE_MIN_SDK`。
- **測試只用 29 和預設的 36。** 條款寫「android_sdk 低於 30」,恰好 30 的情況沒人驗。
- **重現:** 把 `NATIVE_MIN_SDK = 30` 改成 `31`,跑 `-k android_native_collect_off`,結果 `13 passed, 0 failed`。
- **後果:** Android 11 裝置會被誤判成「版本不支援」,而計劃明說 Android 11 以上才支援。

## 2. S23 預算公式的係數沒被釘住
severity: major
blocking: 是(S23 是驗收條款,預估公式改壞測試照綠)
引句:「上限 121 秒(預估至少 120 秒加第一段的三倍)」
file: `scripts/templates/android-stability-collect.sh:565` 是 `elapsed + (2 * elapsed + 120) > float(budget)`。
- **測試只用兩個預算值。** 121 秒和 100000 秒,都遠離邊界,量到的第一段秒數又是真實時鐘,所以公式「第一段的兩倍」這個係數沒被釘住。
- **重現:** 把 `2 * elapsed` 改成 `elapsed`,跑 `-k android_native_collect_budget`,結果 `4 passed, 0 failed`。
- **後果:** 預估變短,第二段會被放進本來放不下的預算,拖過 e2e 的步驟上限,連第一段的判定一起丟掉。

## 3. e2e 範本傳預算變數那一行沒有任何測試守,筆記的 [test:] 綁錯測試
severity: major
blocking: 是(S23 在真實流程要生效,全靠 e2e 範本傳這個變數)
引句:「範本叫收集腳本時用 LUMOS_STABILITY_STEP_BUDGET_S 傳這一步的上限(T_LONG);專案把 stability.native_retained 寫進設定等於改了記憶體設定,記憶體設定指紋會變、推送前要重跑整套 [出處:[[Projects/原生記憶體增長提示_計劃]] 設計審 r4] [因:收集腳本不知道 e2e 的單步上限,原生配置排行那段跑不完時會連第一段的判定一起丟] [test:t_android_native_collect_budget]」
file: `scripts/templates/android-e2e-run.sh:516` 是 `senv["LUMOS_STABILITY_STEP_BUDGET_S"] = f"{T_LONG:g}"`。
- **綁定測試測的是別的東西。** `t_android_native_collect_budget` 直接呼叫收集腳本,不經過 e2e 範本。
- **假收集腳本不記環境變數。** e2e 測試用的替身只寫 `echo "$1 ${LUMOS_STABILITY_SCENARIO:-}"`(`scripts/test_lumos.py:19966`),看不到預算變數。
- **重現:** 把 `:516` 那行改成 `pass`,跑 `-k android_e2e_memory_by_case`,結果 `7 passed, 0 failed`。我也 grep 過整份測試檔,`STEP_BUDGET` 只出現在收集腳本的測試。
- **後果:** 刪掉或改名這行,所有測試照綠,而 e2e 流程下預算永遠不生效。S23 在真實流程中形同失效。

## 4. 第二段收完錄製後不從 state 拿掉的話,正常路徑會對舊 pid 再送一次 kill
severity: minor
blocking: 否(實際傷害要等 pid 剛好被重用,且 `finally` 仍在;降一級,因為沒有針對「正常完成」路徑的清理次數斷言)
引句:「check("停掉第二段的錄製、刪裝置上 lumos-native 的暫存", log.count("kill -TERM 4321") >= 2」
file: `scripts/templates/android-stability-collect.sh:597`(`del state["rec"]`)與 `:625`(`native_phase` 的 `finally` 裡 `state.pop("rec")`)。
- **缺的斷言。** `t_android_native_collect_ok` 沒有斷言正常收尾後 `kill -TERM 4321` 恰好兩次(第一段一次、第二段一次)。
- **重現:** 把 `del state["rec"]` 改成 `pass`,`-k android_native` 為 `153 passed`。我在副本裡臨時加印 `log.count("kill -TERM 4321")`:原版是 2,改壞後是 3。
- **後果:** 正常完成時會對已經停掉的 perfetto pid 再送一次 `kill -TERM` 並再刪一次檔。pid 若被重用就誤殺裝置上別的行程,這是程序清理的守衛,卻只有 SIGTERM 路徑的測試。

## 5. 範本檔缺失時第二段才炸,訊息不帶檔名,也沒有測試(新舊錯配鏡頭)
severity: minor
blocking: 否(只降級成 failed,第一段不受影響,但訊息無法自救)
引句:「`scripts/templates/android-stability-collect.sh` 照抄進消費專案後,在專案根目錄跑」
file: `scripts/templates/android-stability-collect.sh:310`,`start_record` 開頭的 `open(os.path.join(here, template))`。
- **情境。** 消費專案只照抄收集腳本,沒有補上 `android-stability-heapprofd.pbtxt` 或 `android-stability-native.sql`,而 `lumos update` 只補不刪、不保證兩支新檔已在旁邊。
- **重現:** 副本裡刪掉 `android-stability-heapprofd.pbtxt`,用 `_ms_native_collect` 跑。
  - 結果是 rc 0。
  - `native_retained` 為 `{"enabled": true, "status": "failed", "reason": "第二段出了意外(FileNotFoundError)"}`。
  - 驅動紀錄是 `['2','5','2']`,也就是暖機已經白跑,才在開錄時失敗。
- **缺口。** `preflight` 沒有在打開 `native_retained` 時事前檢查這兩支範本在不在,reason 也沒有檔名。計劃〈回退〉的四種新舊錯配,測試只驗到「舊收集腳本配新 lumos」這一種(`t_android_native_lumos_empty_and_off`)。

## 6. 文件還寫「兩支」、單源計劃沒補新欄位、S7 與 pid 的幾個分支沒被測
severity: minor
blocking: 否(措辭與覆蓋面)
引句:「兩支查詢都只用標準 SQLite 語法,測試用 Python 內建的 sqlite3 照 Perfetto 文件建同名的表跑」
file: `docs/lumos-toolchain-knowledge/Systems/android-stability-collector.md`(正文白話段)與 `docs/lumos-toolchain-knowledge/Projects/Android記憶體與穩定性驗收_計劃.md`。
- **同一篇筆記自相矛盾。** frontmatter 的 responsibility 已寫「三支查詢範本、兩份錄製設定」,正文白話段仍只列兩支查詢、沒提 `android-stability-native.sql`。
- **測試 docstring 沒跟上。** `t_android_memstab_templates_receipt_safe` 的 docstring 寫「兩支新範本的註解沒有以分號結尾的行(收據重跑腳本拿第一個分號結尾的行當查詢結尾)」,但迴圈現在是三支。`t_android_memstab_vendored` 的 docstring 寫「S12:收集腳本、兩支查詢範本與錄製設定要帶 SPDX 檔頭」,實際清單已是三支查詢。
- **單源計劃沒補。** 驗收計劃〈資料怎麼流〉只改了 WHY 和 Native Heap 那一句。
  - 步驟 1 的設定欄位沒有 `native_retained`。
  - 步驟 2 的流程沒有第二段。
  - 步驟 3 的結果檔欄位沒有 `native_retained`。
  - 步驟 5 的診斷仍寫「原生那側用 heapprofd 重跑一次 N 輪」,沒說先看排行。
  - collector 筆記又說「設定欄位、七種檢查與判定規則的單源在」這份計劃,照單源找會找不到。
- **S7 與 pid 的分支沒被測(多出來的保守分支)。** 三個實驗都照綠,影響只是少一道保守擋下。
  - 把 `elif new is None:` 那段刪掉,`-k android_native_collect` 為 `58 passed`。
  - 把 `elif not pids[0] or ...` 的 `not pids[0] or` 拿掉,同樣 `58 passed`。
  - 把 `or res["pids"]["status"] != "ok"` 拿掉,`-k android_native_collect_failures` 為 `20 passed`。
- **規格沒寫。** 計劃 S7 和第 2 步只寫「第一段驅動失敗或 pid 讀不到」與「前後 pid 不同」,沒寫「讀不到第二段結束紀錄」和「pid 讀不到」,也沒有測試。
- **Skill 的落差(L3 步驟 3)。** 步驟標題是「原生那側(`native_unreachable` 沒過)」,L0 的往下條件是「排行不是往下條件」。計劃動機是「SDK 自己留著登記、掃描是 0」,這時 `native_unreachable` 通過、L0 停下,Agent 不會去看 `native_retained`;`peak_vitals` 沒過進 L3 也不看排行。要靠人讀文字輸出才看得到排行。

## 各鏡頭結論
- **鏡頭 1(測試抓不抓得到錯):** 見 1–4、6。
  - `_ms_native` 的假表欄位(`heap_profile_allocation`、`stack_profile_*`、`stats`)與真 Perfetto 一致,假 TP 輸出的引號與整數形狀與既有測試一致。
  - SQL 的 GLOB 前綴、`ERROR` 偽框架、APK `!`、系統目錄旗標、歸併、呼叫者、200 上限與截斷都有行為測試。我拿掉 `_Zna` 前綴和 `calloc` 以外的配置器名單,各有一支測試翻紅。
  - 假 adb 的 `termed` 清除與 `sdk` 檔只在原生分支生效,既有 389 個 memstab 測試全綠,沒有誤入。
  - 拿掉 SQL 的 `heap_name` 過濾、拿掉收集腳本內的二次排序與截 200,測試照綠,但行為等價或假資料不含別的 heap,我不當 finding 提。
- **鏡頭 2(文件對現實):**
  - reference.md 的設定鍵名、`"@default"`、環境變數名、檔名與清理指令,逐句對得上程式。
  - 計劃的 S1–S28 與實作沒有分岔,除了 6 列的多出分支。
  - 我另外確認了最外層(`stability` 以外)誤放 `native_retained` 時 `--check-config` 照過,但這是既有行為,不算本次新增。
- **鏡頭 3(圖譜):**
  - 固定席的 `lumos-cli-read`(search 預設排除 superseded)、`guard-kill`(rc 優先序、`--json` 純淨)、`design-loop`、`lumos-cli-lifecycle`(re-inject)、`bound-tests-gate` 的合約:本次改動只加 macrobench 區塊和測試,不碰這些行為。
  - `測試假綠形態`:新測試多有「前置:範本在」之類的前置斷言,不違反。
  - `pitfalls-code-loop`、`loop-convergence-recording` 是 RISK 節點,不受影響。
  - 這部分是我讀 diff 與 `scripts/lumos` 的判斷,沒有逐一重跑各合約綁定的測試。
- **鏡頭 4(新舊版本錯配):**
  - 舊收集腳本配新 lumos 有測試。
  - 新收集腳本配舊 lumos、新 skill 配舊 lumos 兩種沒有測試,只能靠人工(S19 manual)。
  - 範本檔缺失見 5。

最嚴重 severity: major,blocking 共 3 條(1、2、3)。
