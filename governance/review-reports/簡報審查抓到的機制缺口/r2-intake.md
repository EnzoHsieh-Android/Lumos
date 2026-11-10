# r2 收貨紀錄:簡報審查抓到的機制缺口

四份報告從逐字稿存檔;架構對齊席做了 report-normalize 的格式搬移。四份 quote-check 全數錨定;refcheck 三份各有 1 條檔案不存在(都是席位實驗暫存目錄或別的工作樹的路徑,不是被審宣稱)。收貨時 `git status` 只有卷證與治理帳在動。

編號:正確性 c1–c11、邊界 b1–b9、整合 i1–i12、架構對齊 a1–a7,共 39 條。

## 判讀:同類 major 連兩輪,換形狀

r1 與 r2 的 major 集中在範圍 2(高風險路徑)與範圍 3(行內忽略註解):r1 是提交訊息標記被打穿,改成路徑清單後 r2 又在「讀哪一版設定、改到的檔從哪來、提醒看不看得到、跟既有讀設定與命令切段的做法不一致」被打穿;範圍 3 r2 另被指出跟 [[Systems/pitfalls-lint-adapter]] 的既有決策「lumos 不內建棧規則、規則庫讓給社群 linter」相反。照手冊「同類兩輪換形狀」與跑滿前的熔斷提示(累計折入超過 20 條,建議拆小),這一輪不在原計劃裡再補,改成:

- 本計劃縮成範圍 1(規則例外)與範圍 4(README),兩件在 r2 只剩可直接折的小問題。
- 範圍 2 移到 [[Projects/人工指定高風險路徑_計劃]],範圍 3 移到 [[Projects/行內忽略註解要留紀錄_計劃]],r1、r2 所有相關發現原文帶過去當設計輸入(兩篇計劃的〈審查帶過來的問題〉節逐條列編號)。

## 先查世界(換形狀前)

PRIOR-ART: 行內忽略要留痕,社群 linter 自己就有對應規則,不必由 lumos 建對照表 → ESLint 社群規則 require-description、no-use(忽略註解本身當告警);detekt 規則 ForbiddenSuppress;ruff 的 PGH004(blanket noqa)與 RUF100(沒用到的 noqa);SonarQube 的 S1291。這條方向跟 pitfalls-lint-adapter 的「規則庫讓給社群 linter」一致,列為新計劃的首選方向,另一條「lumos 自建對照表」列為對照,由新計劃的設計審裁。
PRIOR-ART: 人工指定敏感路徑 → GitHub CODEOWNERS;本 repo 讀宣告用 `_trusted_decl_ref`(起點與主線分叉點那一版)與 `_lumos_config_at_ref` 四態讀法;改到的檔照殘留索引用 `git diff --name-only -z --no-renames`。新計劃照這三條既有做法重寫,不另寫。

## 處置表

| 編號 | 席 | 嚴重 | 去向 | 說明 |
|---|---|---|---|---|
| c1 | 正確性 | major | 折 | 範圍 2 移出本計劃,帶進 Projects/人工指定高風險路徑_計劃 |
| c2 | 正確性 | major | 折 | 同上 |
| c3 | 正確性 | major | 折 | 範圍 3 移出本計劃,帶進 Projects/行內忽略註解要留紀錄_計劃 |
| c4 | 正確性 | major | 折 | 壞例加「Activity 裡有內部 Service、Activity 自己的收集照報」,規則的 has 只看直接繼承清單 |
| c5 | 正確性 | minor | 折 | 範圍 3 移出 |
| c6 | 正確性 | minor | 折 | 範圍 3 移出 |
| c7 | 正確性 | minor | 折 | 範圍 2 移出 |
| c8 | 正確性 | minor | 折 | 範圍 2 移出 |
| c9 | 正確性 | minor | 放行 | Service 裡的內部 Fragment 也豁免是刻意選的語意,照同包 kt-register-without-unregister 的既有寫法;實務上罕見,天花板已寫 |
| c10 | 正確性 | minor | 折 | 範圍 2 移出 |
| c11 | 正確性 | minor | 折 | 範圍 3 移出 |
| b1 | 邊界 | major | 折 | 範圍 2 移出 |
| b2 | 邊界 | major | 折 | 範圍 2 移出 |
| b3 | 邊界 | major | 折 | 範圍 2 移出 |
| b4 | 邊界 | major | 折 | 範圍 2 移出 |
| b5 | 邊界 | minor | 折 | 範圍 2 移出 |
| b6 | 邊界 | major | 折 | 範圍 3 移出 |
| b7 | 邊界 | minor | 折 | 範圍 3 移出 |
| b8 | 邊界 | minor | 折 | 範圍 3 移出 |
| b9 | 邊界 | minor | 折 | 範圍 3 移出 |
| i1 | 整合 | major | 折 | 範圍 2 移出 |
| i2 | 整合 | major | 折 | 範圍 2 移出 |
| i3 | 整合 | major | 折 | 範圍 2 移出 |
| i4 | 整合 | major | 折 | 範圍 2、3 的文件清單隨兩件移出;本計劃的範圍 5 只留 README 與型錄 |
| i5 | 整合 | major | 折 | 範圍 3 移出,新計劃首選改用社群 linter 自己的規則 |
| i6 | 整合 | major | 折 | README 改寫:筆記正確時另做過 80 場,只有一題看得出幫助;S4 對照兩份原始紀錄 |
| i7 | 整合 | minor | 折 | 範圍 2 移出 |
| i8 | 整合 | minor | 折 | 樣本補巢狀兩種;型錄 STATE-5 寫在「情境」欄後面的說明,不動實測欄 |
| i9 | 整合 | minor | 折 | 範圍 3 移出 |
| i10 | 整合 | minor | 折 | 範圍 3 移出 |
| i11 | 整合 | minor | 折 | 範圍 2 移出(掛鉤改動跟著走) |
| i12 | 整合 | minor | 折 | 範圍 2 移出 |
| a1 | 架構對齊 | major | 折 | 範圍 2 移出,新計劃照 _trusted_decl_ref |
| a2 | 架構對齊 | major | 折 | 範圍 3 移出 |
| a3 | 架構對齊 | minor | 折 | 範圍 2 移出 |
| a4 | 架構對齊 | minor | 折 | 範圍 2 移出 |
| a5 | 架構對齊 | minor | 折 | 範圍 3 移出 |
| a6 | 架構對齊 | minor | 折 | 範圍 3 移出 |
| a7 | 架構對齊 | minor | 折 | lands_in 拿掉 pitfalls-code-loop 與 pitfalls-lint-adapter,只留 kotlin規則包 |

重現表:本輪沒有編排者重現不到、要列進 refuted 的發現。c4 由編排者照席位寫法在樣本上加內部 Service 案例確認(見實作時的樣本)。
