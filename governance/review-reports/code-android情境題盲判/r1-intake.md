# code-android情境題盲判 r1 收貨(2026-11-06)

範圍:`ad4baf874..8a37edb0e`(盲判段五個提交),tier standard;材料 1890 行超過 1800,拆兩包:甲(scripts/lumos、check.py、手冊,1143 行)、乙(測試與筆記,747 行)。三席:正確性(甲,附角色卡)、測試(乙)、架構對齊(甲)。

## 收貨三道

- 正規化:三份已是正規化格式。
- quote-check:三份對各自那一包全數錨定。
- refcheck:正確性 9、測試 8、架構對齊 12,全對得上。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 正確性-F1 | 讀 `_kt_bj_read`:標記檔能解析且有 cells 就直接回傳,不對治理帳;席位行程內探針:帳有 s1、s2,標記檔只有 s1 → 回 ['s1'] | HIT |
| 正確性-F2 | 讀 `_kt_bj_read` 只驗最外層 dict;`code-loop check` 表態核對整段 `except Exception` 走 `_gate_failopen`;席位探針 AttributeError | HIT |
| 正確性-F3 | `_codeloop_branch_filename` 把 `/` 換 `__`,`a/b` 與 `a__b` 同檔;讀標記檔不核 branch 欄 | HIT |
| 正確性-F4 | 讀 `_kt_bj_check` 仲裁分支:仲裁不等於作者一律進 majority,不看三方是否各異、不看盲判是否判照做 | HIT |
| 正確性-F5 | 讀 `_cmd_codeloop_blind_judge`:全部格已存在時照樣追加事件、rc0 | HIT |
| 架構對齊-F1 | 對照 `_codeloop_guard_verdict` 內嵌的範圍計算與 `_kt_bj_range`:退路不同(推送範圍 vs `_codeloop_default_base`) | HIT |
| 架構對齊-F2 | 讀 `_disp_record_for` 有 merge_side,盲判讀取沒有;沒實跑合併提交 | HIT(讀碼) |
| 架構對齊-F3–F6 | 讀碼對照席位給的 file:line | HIT |
| 測試-F1 | 席位探針 `_render_gov_situation`:作者判不適用、兩盲判判照做 → 「多數決:真陽性 0、誤報 1」;對調標籤判斷統計測試仍綠 | HIT |
| 測試-F2–F5 | 席位在 `--shared` 複本逐處改壞跑測試仍綠(各條附改了哪行) | HIT |

## 先查世界

PRIOR-ART:事件帳與衍生快取誰是真相——事件溯源的通則:只追加的事件帳是唯一真相,現況是從事件折出來的衍生資料,快取(快照、投影)隨時可從帳重建,兩者不一致時以事件為準(https://archman.dev/docs/architectural-styles/event-sourcing 、https://alivedise.github.io/backend-engineering-essentials/messaging/event-sourcing ;皆轉述 Fowler)。採用:盲判紀錄一律從治理帳折出(讀前用位元組比對篩 `blind-judge` 行,同 `_kt_sit_reminder_log` 既有做法),不再讀本機標記檔當判定依據;排除:「標記檔優先、壞了才退帳」(正是 F1–F3 的成因)。
PRIOR-ART:三方標註各不相同——標註研究的通則:三人有多數就照多數,三人各異不硬判,標成無多數交資深者或專家裁,並保留分歧(https://arxiv.org/pdf/2603.17373 SafeTutors、https://arxiv.org/pdf/2602.18446 ReportLogic、https://potatoannotator.readthedocs.io/en/latest/administration/adjudication/ )。採用:三方各異印「沒有多數,要人裁」,不記成 majority-against-author;兩位盲判一致判「照做」時不叫作者「沒照做」。
PRIOR-ART:同一批判者證不了自己的提醒真假——Tricorder 用使用者事後的回饋(not useful)量誤報,不靠產生提醒的同一個分析器自評(https://lup.lub.lu.se/search/files/91080778/ICSE_SEIP_2021_MEAN_final.pdf )。採用:多數決提醒不進「真陽性/誤報」自動計數,統計只印則數並註明升擋前要人抽樣;證據樣式提醒照舊用盲判終局判真假。

## 分組與去向(全數折入)

- 甲 盲判紀錄的真相來源:正確性-F1、F2(major),正確性-F3、F5(minor)→ 只從治理帳折出盲判紀錄(按精確分支過濾、驗票形狀,形狀不對那筆跳過不放行);標記檔不再當判定依據;整份都沒有新格寫入時不追加事件、回非零並講明沒生效;重判的唯一路徑寫進筆記 PITFALL。
- 乙 範圍與分支解析各一份:架構對齊-F1(major)、F2(minor)→ 把 `_codeloop_guard_verdict` 內嵌的範圍計算抽成共用函式,盲判與 check 同呼叫;盲判讀取跟表態用同一套分支解析(含 merge_side)。
- 丙 多數決判定與統計:測試-F1(major)、正確性-F4(minor)→ 只有兩位盲判一致判「適用但沒照做」而作者不同時才算多數判作者沒照做;三方各異印無多數;多數決提醒不進真陽性/誤報計數;升擋 REVISIT 對多數決改成人抽樣。
- 丁 測試缺口:測試-F2、F3、F4、F5(minor)→ 每條補先紅的測試。
- 戊 一致性:架構對齊-F3、F4、F5、F6(minor)→ repo 根與版本解析走 `cmd_code_loop` 既有入口;新欄位補 `_GOV_FIELD_TYPES`;「段|列|種類」編解碼共用一支;`dt_sources` 併進 `dt_row` 讀表那一輪、`_KT_DT_SOURCES` 照 `_KT_DT_ROWS` 的載入慣例。
