preflight-4: ran

# r1 收貨紀錄(ci-speedup)

## 首輪前掃(sonnet 一席,唯讀)

四類:①未定義 4、②壞引用 2(另 2 條確認正確)、③範圍矛盾 4、④語意 6 重點;外部事實 5 項前掃標未查證,編排者用 gh api 查了兩項(合併請求 #9 的 merge_commit_sha=主線 ce2a961f;combined status API 可讀),其餘(fork token 唯讀、description 長度)沿用 GitHub 公開行為。

語意類修正(修改前 → 修改後):
1. 〈範圍〉「CI 拆成三個工作」→ 四個工作(多 `mark`),每個工作各自 checkout、補本機 main、裝 Python。
2. 〈做法〉1「照搬」「一字不改」→ 除了 `steps.suite.outputs` 改 `needs.prep.outputs` 外逐字不改;補步驟順序限制(筆記形狀閘在錨點驗證前、漂移檢查緊接回頭重讀提醒)與不寫「note-audit check」字樣。
3. 〈做法〉2「寫不進去就算了」→ `mark` 加 `continue-on-error: true`、只在同 repo 合併請求跑、名稱避開 test 字樣;寫的是 `github.event.pull_request.head.sha`。
4. 〈做法〉3 補 combined status API、repo 名來源;〈做法〉4 補 `GH_TOKEN`;新增〈做法〉5 權限。
5. prep 原本沒要求完整歷史(會讓純文件子集判定悄悄失效)→ 四個工作都要 `fetch-depth: 0`,寫進 [S3]。
6. 「有 37 處測試讀 ci.yml」→ 約 9 支測試讀真 ci.yml。
7. 〈做法〉5「改掉 2026-09-12 那行約 10 分」(壞引用)→ 改 bound-tests-gate「切 4 片」那行與 ci.yml 註解。
8. 〈實作紀錄〉補上該節;`graph` 在〈範圍〉定義。

## 席報告收貨(四席齊了才折)

report-normalize 四份合格;quote-check 四份全錨。Enzo 2026-10-06 看過整合席 F1 後改裁「只做方案 1」——方案 2 整段拿掉,跟它綁在一起的發現以「改設計」折掉。

| id | 席 | 嚴重 | 重現/判讀 | 結論 |
|---|---|---|---|---|
| i1 | 整合 F1 | major | `Systems/測試假綠形態` 那條 PITFALL:2026-10-04 合併請求 #2 綠、主線紅,根因是測試取主線 tip 與 tip~1(看提交歷史) | HIT 採信,折:方案 2 拿掉(Enzo 裁) |
| i2 | 整合 F2 | major | 跳過時全套沒跑,「主線紅、同樹合併請求綠」不會發生 | HIT 採信,折(方案 2 拿掉) |
| g1 | 通才 F1 | minor | 樹相同不等於輸入相同 | HIT 採信,折(方案 2 拿掉) |
| g2 | 通才 F2 | minor | 同 i2 | HIT 採信,折(方案 2 拿掉) |
| g4 | 通才 F4 | minor | mark 只看 shards 綠 | HIT 採信,折(方案 2 拿掉) |
| e2 | 邊界 F2 | minor | ci-reuse 例外與逾時沒寫 | HIT 採信,折(方案 2 拿掉) |
| e5 | 邊界 F5 | minor | 權限層級矛盾 | HIT 採信,折(方案 2 拿掉,不再寫狀態) |
| e7 | 邊界 F7 | minor | 跳過沒有時間上限 | HIT 採信,折(方案 2 拿掉) |
| i4 | 整合 F4 | minor | 同 e5 | HIT 採信,折(方案 2 拿掉) |
| i7 | 整合 F7 | minor | 頭提交來源、combined status 分頁 | HIT 採信,折(方案 2 拿掉) |
| a1 | 架構對齊 問3 | major | 取 repo 名另起一套(鄰居由 gh 依 cwd 判斷) | HIT 採信,折(方案 2 拿掉,沒有新指令) |
| a2 | 架構對齊 問2-1 | minor | 沒寫重用 `_ci_gh` | HIT 採信,折(同 a1) |
| a3 | 架構對齊 問2-2 | minor | 輸出格式與旗標跟 ci-wait 不一致 | HIT 採信,折(同 a1) |
| a4 | 架構對齊 問3-2 | minor | 寫狀態在 YAML、讀在 lumos | HIT 採信,折(同 a1) |
| a5 | 架構對齊 問4 | minor | 指令說明表與註冊沒提 | HIT 採信,折(同 a1) |
| g3 | 通才 F3 | minor | 新工作沒有 timeout-minutes,預設 360 分 | HIT 採信,折:〈範圍〉每個工作設逾時 |
| e1 | 邊界 F1 | major | 同 g3 | HIT 採信,折(同 g3) |
| i5 | 整合 F5 | minor | 同 g3 | HIT 採信,折(同 g3) |
| e3 | 邊界 F3 | minor | 純文件推送也展開多台 | HIT 採信,折:文件子集留在 prep 跑 |
| e4 | 邊界 F4 | minor | 每組只量一次 | HIT 採信,折:每組至少兩次 |
| e6 | 邊界 F6 | minor | 多工作同時紅時記帳只拿日誌尾端 | HIT 採信,折:天花板 3 |
| i3 | 整合 F3 | major | 變假話的句子沒列全、跟逐字不改衝突 | HIT 採信,折:〈做法〉2 列全、只鎖 run/if/continue-on-error,註解可改 |
| i6 | 整合 F6 | minor | 拆分前比對基準沒定義、N 寫在同一處 | HIT 採信,折:[S1] 基準寫死在測試、N 寫在一處 |
| i8 | 整合 F8 | minor | 範本要不要改沒交代 | HIT 採信,折:〈範圍〉不做那條 |
| i9 | 整合 F9 | minor | 掛鉤訊息有幾句會半假 | HIT 採信,折:〈做法〉2 掃掛鉤訊息 |
| i10 | 整合 F10 | minor | 人工確認沒有回頭條件 | HIT 採信,折:REVISIT 行 |
