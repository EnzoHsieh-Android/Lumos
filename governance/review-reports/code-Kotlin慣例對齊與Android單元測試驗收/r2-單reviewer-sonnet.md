severity: major

# 第 2 輪代碼審查報告:Kotlin 慣例對齊與 Android 單元測試驗收

審查範圍是 r2-snapshot.patch,修補鏡頭為 e7c5a0d55 到 9ddf8f796。臨時目錄是 `/tmp/lumos-seat-work/code-Kotlin慣例對齊與Android單元測試驗收/單reviewer-sonnet/`。裡面有 `before`、`after`、`probe`、`consumer` 四份 git archive 副本和一份 `*.orig` 備份,我沒在真 repo 寫任何東西。依規定由編排者收貨後刪除。

## G1(重大)修補改了 scripts/test_lumos.py,錨點基準線沒跟著更新,anchor verify 在修補後會失敗

severity: major
blocking: yes

引句:「+    "scripts/test_lumos.py": "56a111ab5e06075fd28ec19a668b089226575456a83f8dfb1e7671afb14e7324",」

這行在 snapshot 的 `governance/anchor-baseline.json` 段。修補 patch 的 `scripts/test_lumos.py` 段改了 S4 測試和 `_need_src`,但修補 patch 沒有 `governance/anchor-baseline.json` 的任何改動。

失敗場景:在 9ddf8f7 的 repo 根跑 `python3.14 scripts/lumos anchor verify`,印出「scripts/test_lumos.py(期望 56a111ab5e06075f… 實際 5501e32109384c82…)」,exit 1。`scripts/hooks/pre-push:380` 和 `.github/workflows/ci.yml:303` 都會跑這道,所以現在推送和 CI 都會被擋。

歸因:有證據的修復回歸。
- 修補前 e7c5a0d:`test_lumos.py` 的 sha256 是 56a111ab…,與基準線一致,`anchor verify` 在 before 副本 rc=0。
- 修補後 9ddf8f7:sha256 是 5501e321…,與基準線不符,rc=1(真 repo 與 after 副本都是)。

補充:重新簽名要使用者在對話裡核可,審查席不能代做。所以這項更像「等待簽名的未完成簿記」,但在這份快照上它是會擋推送的真實狀態。binding 說推送前會壓回各功能提交,壓完仍需重簽,而 binding 的歸因界線沒提這件事。

## G2(minor)修補宣稱的三項文件改動沒有任何測試守著

severity: minor
blocking: no

引句:「+- 依據：[Android 官方架構建議](https://developer.android.com/topic/architecture/recommendations)（2026-10-05 更新）、[官方 Flow 測試](https://developer.android.com/kotlin/flow/test)（2026-09-24 更新）」

這三項是:手冊「五」節標明只適用 Android、R19 到 R22 各有依據行,以及測試品質標準新節開頭的單源指標。

失敗場景:在 after 副本裡一次做三件事:
- 刪掉所有 `- 依據：` 行。
- 把標題改回 `## 五、其他`。
- 拿掉 `(單源=[[Projects/Android本機單元測試驗收標準_計劃]])`。

結果 `t_kotlin_idioms_android_official_rules` 是 6 passed,`t_test_quality_standard_android_unit_section` 是 9 passed,兩支都照綠。計劃的 S5 本來就是 manual 條款,所以這是覆蓋面不足,不是壞行為。

歸因:有證據的原有漏查。這三項是修補新加的,修補前不存在,所以也可算「修補新增內容沒被守」。兩版都沒有守它們的測試。

## 三問

**① 原問題的修復效果,行為證據**

S4 測試只排除退出碼 3、YAML 壞掉照綠。這是修補要解的問題,我在 before 和 after 各打壞一次對照。

| 輸入(把手冊範例壞掉) | before(e7c5a0d) | after(9ddf8f7) |
|---|---|---|
| 少一個右大括號,detekt rc=1 | 3 passed, 0 failed(照綠,漏洞成立) | 2 passed, 2 failed,紅 |
| 加入不存在的 `CoroutineLaunchedInTestWithoutRunTest`,detekt rc=3 | 紅 | 紅(有分析完、退出碼 2,和 GlobalCoroutineUsage 抓到樣本那一行兩條斷言都紅) |
| 把 `GlobalCoroutineUsage` 設成 `active: false`,rc=0 | 未測 | 紅 |
| 範例原樣 | 綠 | 綠(rc=2,輸出含 `A.kt:7:5 … [GlobalCoroutineUsage]`) |

配對案例「少括號 rc=1 應紅、加不存在規則 rc=3 應紅、範例正常應綠」三種都成立。

R22 的 stateIn 收集者範例與官方 Flow 測試頁逐字一致:都是 `backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) { viewModel.score.collect {} }`,頁面更新日期 2026-09-24。

**② 修補處的正常、錯誤與相鄰路徑**

- 檔案存在守門:把 `skills/` 整個拿掉的消費端副本(只留 `scripts`),新改的三支測試都記成 skip(「來源 repo 專用」),不是失敗。
  - 涵蓋 `t_kotlin_idioms_android_official_rules`、`t_kotlin_idioms_detekt_snippet_runs`、`t_test_quality_standard_android_unit_section`、`t_kt_flow_question_events_as_state`。
  - 守門確實用專案既有的 `_need_src`。
- 臨時目錄清理:S4 測試的 `mkdtemp` 在 `finally: shutil.rmtree`,例外或斷言失敗時也會清,資源沒問題。
- 輸出格式假設:這台 macOS 的 detekt 1.23.8 輸出是 `/private/tmp/.../A.kt:7:5: … [GlobalCoroutineUsage]`,斷言 `"A.kt:7" in out` 對得上。其他版本或作業系統我沒驗,未判定。
- 審查鏡頭範圍:把「R1–R22」改回「R1–R18」,`t_kotlin_idioms_android_official_rules` 紅。
- 相鄰既有測試:`stack_question_triggers`(59 條)、`tension_lens_and_gov`、`tension_doc_sync`、`tension_candidates_skip_android_only`、`stack_android_only_inside_applicability` 都綠。
- 筆記 lint:效能檢核目錄、linter 精選目錄、兩篇計劃、一篇驗證紀錄,`lumos lint` 都是 0 問題。
- 路徑不成立的只有 G1 的錨點驗證。

**③ 新發現在修前、修後各是什麼**
- G1:修前 `anchor verify` rc=0,修後 rc=1。
- G2:修前這三項文件尚不存在,修後存在但改壞測試照綠。

## 正向主張的證據

所有 preserve 案例修後都綠。這是只見測試通過;其中 `t_kotlin_idioms_android_official_rules` 的鏡頭範圍斷言我另外用 R1–R18 改壞確認會紅。

| claim | input / expected | case_source | before / after | comparison |
|---|---|---|---|---|
| 這五支測試修後仍綠 | `python3.14 scripts/test_lumos.py -k <名>`,期望全綠 | 作者配對案例 | 修前未逐支重跑,只依 binding 的 preserve 宣稱,修前結果未判定;修後:`t_kt_flow_question_events_as_state` 4 passed、`t_kt_leaks_question_viewmodel_context` 2 passed、`t_kotlin_idioms_android_official_rules` 6 passed、`t_test_quality_standard_android_unit_section` 9 passed、`t_test_quality_standard_android_room_section` 9 passed | 修後通過,不能單憑此證明修前也綠 |
| 手冊引的官方頁敘述與官方一致 | 逐條 WebFetch 官方頁 | 我自己補的案例 | 無修前對照,修補未動這些敘述(R19 到 R21 的官方頁敘述屬 r1 內容) | 與官方頁一致 |

官方頁核對結果:
- 架構建議頁:事件從 ViewModel 送 UI 是強烈建議不要、Context/Resources 強烈建議不要、AndroidViewModel 是建議不要、fakes 優於 mocks 是強烈建議,更新日 2026-10-05。
- 狀態還原頁:ViewModel、保存狀態、本機儲存三者的存活表,以及保存狀態只放基本型別與小字串、序列化在主執行緒,更新日 2026-10-07。
- 協程測試頁:`runTest` 預設逾時 60 秒、`MainDispatcherRule` 先宣告,以及 Unconfined 對併發測試的建議,更新日 2026-09-22。
- 本機測試頁:`returnDefaultValues` 為最後手段,更新日 2026-10-23。
- Robolectric 頁:單元測試只在舊碼或依賴 Android 類別 API 時當最後手段,更新日 2026-03-05。
- 要測什麼頁:測試對象與邊界清單,以及 Activity、Fragment、Service 不優先單元測試,更新日 2026-03-05。

## 未驗範圍

- 沒驗 detekt 其他版本或 Windows、CI 上的輸出格式。
- 沒驗 `ForbiddenMethodCall` 帶 classpath 的實際效果,這在 r1 範圍。
- 沒驗 Gradle 9 的 `failOnNoDiscoveredTests` 說法、命令列測試頁、截圖測試頁、涵蓋率頁、Hilt 測試頁。
- 沒驗 Turbine 的用法、Now in Android 的做法。
- 固定席節點的合約(`search` 預設排除 superseded、還原翻紅釘需前置斷言、bound-tests 綁定測試等)我沒有逐條對 diff 走一遍。這份 diff 只動審查題文字、手冊、測試與註解,沒碰那些合約的程式碼路徑,我判斷不影響,但沒有逐條實跑確認。
- 修補後的全套測試沒跑,按規定留給推送前的閘。

總結:最高等級 major
