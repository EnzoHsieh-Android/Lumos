# 選擇點變異加速 r3 收貨

席位:正確性、邊界、整合、資源、回滾、架構對齊,全 sonnet,全新代理,沒讀前兩輪報告。材料 r3-snapshot.md(派工單 r3-dispatch.json 記 spec_commit)。六份收齊後才一次從逐字稿存檔;收齊前沒動被審計劃。report-normalize 六份合格。quote-check 六份全錨定。refcheck 全對得上。審查席臨時目錄收齊後已刪。

發現編號:正確性 c1–c7、邊界 b1–b9、整合 i1–i13、資源 rs1–rs7、回滾 rb1–rb6、架構對齊 a1–a6,共 48 條;原報 major 10 條(c1、b1 b2 b3、i1、rs1 rs2 rs3、rb1、a1),其餘 minor。

核心安全宣稱(合併只確認存活、永遠不判殺掉、判錯方向只會多擋)六席都沒打穿;找到的把該殺判成存活的輸入,只有計劃已承認的測試互相影響。

## 重現表

| 組 | 成員 | 編排者重現 | 處置 |
|---|---|---|---|
| 總時限不夠量齊基準 | rs1 b2 | HIT:_CHOICE_MAX_SECONDS 為 1800 秒(scripts/lumos 常數),守 64 支 × 單支數秒加合併基準可逼近上限;讀計劃無「不夠就不合併」 | 折:開跑前估量齊要多久,剩下時限不夠或只跑一行不合併;S19 |
| 合併基準上限太寬 | rs2 | HIT(讀計劃:上限只寫下限與剩下總時限) | 折:min(max(單支總和×2, 下限), 剩下總時限);S7 |
| 中斷兩個空窗 | rs3 b3 i8 | HIT(讀計劃〈做法〉4 只登記快篩程序;_KILL_RUN_LIVE 為既有登記表) | 折:套壞法後開快篩前先看停止旗標;合併基準也登記、第一個訊號當場收掉;S9 |
| 基準紅的測試進合併 | b1 c3 i5 | HIT(讀計劃:合併道只看名稱檢查,沒看單支基準結果) | 折:只含單支基準綠的;不到 2 支不合併;基準紅照交 abort;S20 |
| 斷路器把編不過算進去 | c1 b6 i7 rs5 rs6 b5 rb6 | HIT:_KILL_COMPILE_RE 存在(scripts/lumos),計劃斷路器定義沒排除它 | 折:〈用詞〉快篩四類,編不過與有失敗不計數不歸零;S8 |
| --only 遇已放行的行靜默無效 | rb1 i13 rb2 | HIT(編排者 grep 到 scripts/lumos 的 ck_waive 與 lint-new waived scope choice-kill 判斷;已放行就跳過的路徑由起草代理讀碼回報,編排者沒逐行追) | 折:印一行指路先撤放行;choice-points 標判法;〈回退〉三步;S21 |
| 介面只有布林 | i1 a3 | HIT:class _KillHooks 為既有選用物件形狀 | 折:同形選用物件帶進剩餘期限、帶出計數與斷路器;S11 |
| 讀結果檔繞過既有讀法 | a1 i6 | HIT:def _secev_junit_facts(raw, tq) 為既有讀法 | 折:改走它,完整名由 classname::name 第一個 :: 切;S15 |
| 安全宣稱、交叉引用、帳欄、預期效益等 | c2 c4 c5 c6 c7 b4 b7 b8 b9 i2 i3 i4 i9 i10 i11 i12 rb3 rb4 rb5 rs4 rs7 a4 a5 a6 | HIT(逐句讀計劃) | 折:見計劃〈審計修正紀錄〉r3 與各節 |
| 環境變數命名語意與既有 LUMOS_SKIP_ 不同 | a2 | 屬實 | 放行:使用者裁定的名字,不改 |

48 條:折 47、放行 1;沒有重現不到的。

## 先查世界

- PRIOR-ART:PIT 在同一個 JVM 子程序裡對一個壞法跑多支測試,第一支殺掉就停、依覆蓋率排序,並以逾時因子判掛住(https://pitest.org/faq 、https://pitest.org/quickstart/basic_concepts/ );採用:合併只拿來確認存活,逐支流程不動;合併基準上限以單支基準總和為依據。
- PRIOR-ART:編譯失敗在變異測試工具裡另歸一類(PIT 的 NON_VIABLE/RUN_ERROR,不算殺掉也不算存活,https://pitest.org/quickstart/basic_concepts/ );採用:斷路器不把編不過計入。
  方向:對 — 時限與中斷、斷路器兩組在 r2、r3 都有 major,但 r3 的是換形狀後的邊界(時限估算、空窗、計數口徑),不是「合併判殺掉」那條路;上面兩個來源都是一個程序跑多支測試、失敗分類另計,跟現在的形狀一致。使用者 2026-11-23 裁跑滿接受風險、進實作。
