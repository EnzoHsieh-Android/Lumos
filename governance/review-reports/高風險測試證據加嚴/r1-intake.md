preflight-4: ran

# r1 前掃與收貨紀錄

前掃(2026-11-04,sonnet 一席,固定清單四項)命中後直接修進計劃真檔;以下逐條記語意類與核心裁定類的修改前→後。定義、引用、存在類已直接修,不另列。

## 語意類

| # | 修改前 | 修改後 | 證據 |
|---|---|---|---|
| p1 | 紅因判讀「風險高低都適用」,沒有生效日 | 只對首筆規格閘留痕晚於生效日的計劃;在途計劃照舊退出碼 | 在途風險低計劃用 TODO() 紅會變弱證據被 `_spec_gate_twoway_run_verdict` 擋 |
| p2 | 「規格閘本身對風險高仍只印不擋」 | 「對紅綠仍只印不擋;句式、綁定、回退節、相依回歸照舊會擋」 | 風險高現在就會因句式等 rc1 |
| p3 | 找不到報告一律弱證據、只掃 `build/test-results/` | 分四種:斷言→紅;非斷言型別→弱;報告沒有型別(手機上跑的)→紅、紅因未判;哪裡都找不到→弱。多掃 `build/outputs/androidTest-results/` | 手機上跑的測試報告沒有型別,照原寫法 androidTest 條款永遠弱證據 |
| p4 | 直接借 `assertion_failure` | 借 `_secev_junit_facts`(包 `junit()`),那支檔只借不改 | `assertion_failure` 吃單一 failure 元素;test_quality.py 有部署指紋 |
| p5 | `signoff --expected [--note]` | `--note` 必填;`--expected` 不寫 signed_off 與 .signoff-log | 現有參數 required=True;cmd_signoff 會改開頭欄位 |
| p6 | 治理帳事件沒定閘名 | 閘名 expected-signoff 加進 `_KNOWN_GATES`、kind expected-sign、不走 `_gate_event_fit` | 閘名不在清單不寫 |
| p7 | `gov --stats` 直接加統計 | 要改 `_gov_row` 白名單 | 只取白名單欄位 |
| p8 | 規格閘拿退出碼判紅(只舉 TODO) | 補:Kotlin/Java 讀不出支數,編譯失敗與 --tests 篩不到也判紅 | `_RAN_EVIDENCE` 沒有 kotlin/java-junit |
| p9 | 「風險低原本就要求在斷言上紅」 | 「擋下訊息有教,但放行只看退出碼」 | 只在已綠分支印 |
| p10 | 13 份「每份取最新一筆」 | 13 份是任一筆跑出過紅;只看最新一筆是 7 份 | 前掃重數 |

## 核心裁定類(已改,交本輪席位審)

| # | 修改前 | 修改後 | 證據 |
|---|---|---|---|
| c1 | 推送前檢查「pre-push 與 CI 都跑」 | 只有 pre-push;〈不做〉加一條不在 CI 跑,天花板二改寫 | ci.yml 查無 spec-gate;唯一呼叫處在 pre-push |
| c2 | 推送前查「這次範圍碰到的」風險高計劃 | 只查範圍改到計劃檔也改到程式檔、或 status 已 done 的;沒有任何留痕的當新計劃要求先跑規格閘 | `_spec_gate_push_candidates` 會拉進連到同一系統節點的計劃,設計審中的計劃會擋別人推送;沒留痕的原寫法等於不查 |
| c3 | d3 寫翻規格落成 d9「不補人簽門」 | d3 改寫業務簽核留痕「何時該簽由人判,工具不擋」;d9 管風險低四行已排除理由,不同對象不翻 | 規格落成計劃全檔查無「卡住」「無人看顧」 |

## 席位收貨

(本輪席報告收齊後補)
