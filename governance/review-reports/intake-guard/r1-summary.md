# r1 五席彙總(intake-guard)
severity: blocker

v1(--intake 必附 + 內容驗指令輸出)被五席審出約 36 條、10 blocker,23 條 blocking,全折入 v2 重寫。

| 席 | 結果 |
|---|---|
| 正確性(claude/sonnet) | 2 blocker + 5 major + 2 minor;blocking 7 |
| 邊界(claude/sonnet) | 4 blocker + 4 major + 1 minor;blocking 6 |
| 整合(claude/sonnet) | 2 blocker + 5 major + 3 minor;blocking 7 |
| 架構對齊(claude/sonnet,不佔人數) | 2 major + 2 minor |
| 外家否決(codex/external) | 否決成立,blocker |

## 一致的死因與修法(四席獨立收斂)
- 首日硬擋不可行:自主迴圈每日輪全滅(orchestrator-prompt 不產 intake,兩席+外家獨立抓到)、87 個測試呼叫點全紅且 0 個預期 rc2、7-9 處記帳模板照字面跑不動、11 份既有 intake 全過不了 S2。→ 修法=先 advisory,格式進模板,跑滿 N 輪再轉硬擋。
- S2 判準不可實作:「已驗類條目」無機械判準;「$ 或反引號」子字串啟發式=既有 parse 刻意排掉的逃逸型(架構席:repo 前例是行首錨定宣告行+退化指定字面+單一 parse 函式+讀側對應)。
- ★正確性席 F7(打斷立案理由)★:「有 intake 檔」推不出「跑過前掃第四類」——intake 慣例正本是收貨重現留痕,前掃只是搭便車;要擋目標情境須有前掃專屬區塊標題(零命中也要寫)。
- 範圍溢出:觸發吃到 code-loop(審 diff 無 intake 概念)與處置帳/light/legacy 形態,spec 未裁。
- 架構席 ④:intake 若寫側-only 會成為帳裡第一個「寫側算 sha、讀側沒人驗」的欄位,與「留痕欄一律讀側全席重驗」相反;讀側驗證該落在處置閘(與外家「落點應是輪級」同向,但外家「同輪多筆指同檔=新形狀」的前提被架構席以 --snapshot 實帳反駁)。

## 立案誠信訂正(整合席 F5,編排者認)
v1 引兩來源中較寬那條(「再犯一次→直接做」),同批計劃節點登記的是「連兩案缺席→升級為必帶欄位★再議★」——門檻與結論都不同,挑有利的引=自我授權。實數:慣例落地後 18 迴圈 11 個缺席(機械可數),遠超「連兩案」門檻;v2 改用此為立案基礎並照「再議」定位(本設計審就是那個再議)。

## 其他折入
- 非 UTF-8 讀檔會炸穿(UnicodeDecodeError⊄OSError,slim-uninstall 合約裡有前例);「空檔 rc2」在審查席路徑不可達(severity 掃描先擋);spec 三個行號因自己的順手修漂 2 行;「順手修殘留」已是空操作(前掃當日已修);canary-audit 綁定測試+kill 配方要同步;兩篇權威節點(三修計劃 d4「純 skill 文件」「無機械擋」)落地後變過期敘述要更新;前掃=首輪限定 vs spec 擴到每輪=改慣例未宣告。
