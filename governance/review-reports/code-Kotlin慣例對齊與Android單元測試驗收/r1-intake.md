# r1 收貨與處置

席報告:r1-單reviewer-sonnet.md(檔級 major,3 條)、r1-架構對齊-sonnet.md(檔級 minor,3 條)。正確性席退件兩次:最後一行總結句用了 severity: 開頭、F2 引句半形逗號錨不到快照,都由該席自己重寫,編排者沒改報告內容;架構對齊席只做 report-normalize --write 的列表項搬成獨立行。

| id | 原報 | 去向 | 理由 |
|---|---|---|---|
| F1 | major | 折入 | 重現成立(見 r1-repro.txt) |
| F2 | minor | 折入 | 機械重現:快照與手冊都有那段漏了 UnconfinedTestDispatcher 的原文 |
| F3 | minor | 放行 | 沿用同檔 dart 真機段的寫法;_SrcOnly 專指缺來源 repo 的產物 |
| A1 | minor | 折入 | 改用 _need_src |
| A2 | minor | 折入 | 新節標題照 java-idioms 寫法標明只有 Android 適用,每條補依據行 |
| A3 | minor | 折入 | 新節開頭補單源 |

## 出處清單(修前先列,修後核對)

- G1(F1,S4 判準):`t_kotlin_idioms_detekt_snippet_runs` 一處程式;同一說法在計劃 S4 條款(已改寫)、驗證紀錄(補 r1 之後一段;舊表那列是歷史實測,不改)。這次改動裡沒有其他跑外部工具、靠退出碼判的測試。
- F2(stateIn 收集者範例):手冊 R22(已改)、測試品質標準新節(本來就對)。
- G2(A1,守門):`_kotlin_idioms_text`、`t_kt_flow_question_events_as_state`、`t_test_quality_standard_android_unit_section` 三處(都已改);改完 grep 新測試範圍內只剩 docstring 提到 _SrcOnly。
- A2:R19–R22 四條都補依據行;節標題一處。
- A3:新節開頭一處。

## 配對案例

- repair:F1 → 故障A、故障B 兩種壞設定都紅;F2、A2、A3 是文字,核對方式是讀修後原文。
- preserve:正常範例 4 passed;六支相關測試(S1–S4、B 的 S1、Room 節守衛)修後全綠;修前 e7c5a0d 版本同六支全綠(r1 派工前已跑)。
- 效能與記憶體:修補只動測試與文字,S4 那支多一次 detekt 呼叫,沒有大型或深層輸入可測,不適用。
