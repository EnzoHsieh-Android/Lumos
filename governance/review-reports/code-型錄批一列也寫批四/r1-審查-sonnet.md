severity: major

這份 diff 的程式改動本身站得住,有問題的是那 11 列的內容。測試和自檢都綠,但它們擋不住「列說會擋、實際不會擋」的標籤。

我跑了 `python3.14 configs/ast-grep/kotlin-android/check.py --catalog-only`,結果「型錄問題 0 個」。我也跑了 `python3.14 scripts/test_lumos.py -k kt_catalog`,結果 158 passed、0 failed。`--catalog-only`、規則包自檢和 `-k kt_catalog` 都沒有因為這次改動變紅。

## Findings

### F1 現成規則欄寫「間接」「相關」「需標註」的列,被補成「批四(CI 範本:Android Lint)」,但那條 Lint 檢查擋不到這列的壞寫法
severity: major
blocking: 是

位置:`configs/ast-grep/kotlin-android/check.py:128-131`(`batch4_expected_tags` 的 `_B4_SKIP`)和 `skills/kotlin-idioms/checks-catalog.md` 的 TEST-23、UI-1、PERF-2 三列。

`_B4_SKIP` 只排除「待查」「預設關」「相近」「opt-in」。「間接」「相關」「需標註」「只部分涵蓋」不在其中,這幾種註記照樣算「接電」。一般化之後,`_batch4_problems` 對這類列的行為如下:

- 現成規則欄是 `Android Lint:DoNotMock* 系列(只擋被 @DoNotMock 標記的型別,間接)`(TEST-23)。
- 通電批次原本是 `告警帶寫法=批一`。
- 我用 `m._batch4_problems(該欄, "告警帶寫法=批一")` 重現,回傳「第四批通電批次要寫「批四(CI 範本:Android Lint)」」。
- 也就是說,自檢現在**強制**寫上這個標籤。

diff 把 TEST-23 補成 `告警帶寫法=批一(只有提示級規則,預設不接)、批四(CI 範本:Android Lint)`。

但型錄對標籤的定義是「消費專案照範本接 CI 後才擋」。TEST-23 的壞寫法是「只有 `verify` 沒有 `assert`」。`DoNotMock` 只擋被 `@DoNotMock` 標記的型別,擋不到這個寫法,這列自己的註記也這樣寫。所以讀型錄的人會以為 CI 接上 Lint 後這列有人把關,實際沒有。

同類的還有這幾列:

- UI-1:`相關 slack:ComposeItemKeyHashCode`。算出的 tag 是 `['CI 範本:Android Lint']`。UI-1 要抓的是「`items` 呼叫沒有 `key =`」,而 `ConstantContentStateKeyInItemsCall` 這類檢查抓的是別的壞寫法(常數 key、`hashCode` 當 key)。
- PERF-2:`內建:WrongThread(需標註)`。算出的 tag 一樣是 Lint。`WrongThread` 只在方法有 `@WorkerThread`、`@MainThread` 標註時才響,擋不到 OkHttp `execute()` 或 `URL.openStream()`。

kotlin規則包筆記新增的 WHY 寫了 `[不選:那 11 列逐列寫例外(沒有一列是判過不接)]`。TEST-23 那格自己寫著「間接」,這句不成立。第二批計劃筆記原本的 REVISIT 也說「多半註記只部分涵蓋」,diff 結案時沒有逐列回答這點。

引句:「Android Lint:DoNotMock* 系列(只擋被 @DoNotMock 標記的型別,間接) | B | 形狀:@Test 函式裡只有 verify 沒有 assert | 告警帶寫法 | 告警帶寫法=批一(只有提示級規則,預設不接)、批四(CI 範本:Android Lint)」

引句:「[不選:那 11 列逐列寫例外(沒有一列是判過不接)]」

佐證:
- file: `configs/ast-grep/kotlin-android/check.py:128`(`_B4_SKIP` 沒有「間接」「相關」「需標註」)
- file: `skills/kotlin-idioms/checks-catalog.md:11`(標籤定義是「消費專案照 linter 目錄範本接 CI 後才擋」)

建議做法:把「間接」「相關」「需標註」「部分涵蓋」收進 `_B4_SKIP`,TEST-23、UI-1、PERF-2 退回 `告警帶寫法=批一`。或者逐列判斷,並把例外寫進口徑。

### F2 測試的改壞例子只涵蓋 Lint 標籤,compose-rules 標籤的批一列沒有守
severity: minor
blocking: 否

新增的第三個改壞例子,取的是第一個含 `告警帶寫法=批一、批四(CI 範本:Android Lint)` 的列,也就是 API-9。這個例子確實能抓到「把一般化還原」這種改壞:還原成 `"批四" in batch` 才判的舊寫法,API-9 拿掉批四後不會報,測試會紅。

但沒有任何例子針對「批一、批四(推送前:detekt 外掛 compose-rules)」。這類列有 UI-3、UI-10、UI-16(UI-16 兩種標籤都有),而且 diff 自己說它們才是「推送前就在擋卻沒標」的列。

舉一個具體改壞:`_batch4_problems` 對批一的列只比 `B4_TAG_LINT`、不比 `B4_TAG_CR`。真型錄現在已經標好,`probs == []` 照綠。現有三個改壞例子都只動 Lint 那一列,不會翻紅。

引句:「("批一的列拿掉批四", i_b1, f"告警帶寫法=批一、批四({lint})", "告警帶寫法=批一")):」

佐證:file: `scripts/test_lumos.py`(`t_kt_catalog_batch4_wiring` 內 `i_b1` 的 `next(...)` 只用 `{lint}` 找列)

## 其他鏡頭的查證結果

- **〈統計〉「被會擋的規則守到的列數」**:`_guarded_rows` 只看 `"告警帶寫法=批一" in c[9]`。補上去的「、批四(…)」是接在後面,UI-10 那種「批一(只有提示級規則,預設不接)、批四(…)」也仍含這個子字串。所以計數不受影響,`t_kt_catalog_stats_consistent` 綠。
- **`behavior_value`**:PERF-2 與 API-9 的批四括號在「;行為測試或正向約束=」之前,不會影響它切到「;」的邏輯,測試通過。
- **圖譜節點**:
  - kotlin規則包:新增的 WHY 與 check.py 行為一致,但「沒有一列是判過不接」這句被 F1 反駁。
  - 測試假綠形態(INVARIANT):這次的測試有前置斷言(改壞例子必須報出問題),沒破壞合約。
  - 授權與歸屬、lumos-cli-read、design-loop:diff 沒碰它們宣稱的行為,判不影響。
- **角色卡 be-api-compat、be-authz**:這份 diff 沒有端點、欄位或對外 API,題目不適用。

總結:最高等級 major,blocking 1 條(F1),非 blocking 1 條(F2)。
