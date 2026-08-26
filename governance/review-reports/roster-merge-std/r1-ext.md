### ext-f1 / major / 立案證據把「零使用」誤推成「必須自動使用」

引句:「席位對帳功能是好的但沒人記得敲。」

佐證:file: `governance/review-reports/roster-merge-std/r1-snapshot.md:18`

佐證:file: `skills/lumos-design-loop/reference.md:235`

佐證:file: `skills/lumos-code-loop/reference.md:379`

佐證:file: `scripts/lumos:4707`

說明:快照只提出「治理帳 0 呼叫」，沒有提出任何一次因未跑 roster 而誤判收斂、漏報缺席或事後返工的實例。相反地，兩份流程文件目前都只把它描述成「可跑」的 advisory，程式也明確要求 opt-in。零呼叫同時支持另一個更簡單的解釋：操作者不需要这份資訊，或 dispatch 建立時已經知道派了誰。今天六個迴圈未依賴它仍完成，進一步削弱「只是忘記」這個未驗假設。

因此 S1 把所有問閘都永久增加輸出，卻沒有命中率、採取行動率或至少一個真實漏報案例作驗收。這不是接上既有需求，而是用強制曝光替沒有證據的需求假設買單。應先以一至數輪 dogfood 記錄「對帳是否曾改變處置」；若仍為零，整案不必要。

### ext-f2 / blocker / advisory 與 fail-closed 在同一問閘輸出中自相矛盾

引句:「恆 advisory 不影響 PASS/FAIL。」

佐證:file: `scripts/lumos:5068`

佐證:file: `scripts/lumos:5070`

佐證:file: `scripts/lumos:5072`

佐證:file: `scripts/lumos:10047`

說明:現行 roster 在外家不足時會明印「這席規定缺席就不能放行」及「fail-closed 紀律未滿足」，但 v2 又規定它不得改變 disposal 的 PASS/FAIL。opt-in 時這只是操作者主動要求的旁路診斷；自動併入正式問閘後，合法輸出將變成同一次裁決同時宣告：

- disposal PASS；
- 必要席缺席；
- 規定缺席不能放行；
- 本工具仍不阻斷。

這不是單純噪音，而是正式問閘給出互斥裁決。下游若看 rc 會放行，人若看文字則應拒絕，S1 沒有定義哪個才是治理結論。除非刪除「fail-closed／不能放行」措辭、真的把它納入閘，或只在 PASS 後以不具裁決語意的摘要呈現，否則 spec 不可實作。

### ext-f3 / major / 「當輪」選取沒有可驗證的共同輪序

引句:「輸出尾端自動附最新一輪的 roster 對帳」

佐證:file: `scripts/lumos:5037`

佐證:file: `scripts/lumos:5042`

佐證:file: `scripts/lumos:5044`

佐證:file: `scripts/lumos:5055`

佐證:file: `scripts/lumos:10072`

佐證:file: `scripts/lumos:10093`

說明:disposal 的「最新輪」由 canary log 的 append 序分組後取最後一組；roster 現行則先收 log 輪次，再把 dispatch glob 找到但帳上沒有的輪次附加，之後逐輪輸出。v2 只寫「限定當輪 rid」，沒有指定 roster 必須復用 disposal 已判定的 `rid`，也沒有要求 dispatch-only 的更新中輪應排除。

致命反例是：帳面最後完成輪為 r1，但 r2 dispatch 已建立、尚未 record。disposal 正在裁 r1；若實作者沿用 `_roster_observe` 的輪集合再取末項，附上的卻是 r2。畫面會把 r1 的 PASS/FAIL 與 r2 的席位狀況拼成一份「當輪」裁決。驗收只要求「只有當輪」，沒有交叉斷言 roster rid 必須等於 disposal 實際判定的 rid，因此錯輪仍可全綠。S1 必須明定 `_loop_status_disposal` 解析出的 `rid` 是唯一輸入，不得由 roster 重算。

### ext-f4 / minor / 17 條測試的維護成本攻擊不成立

引句:「--roster 全部 17 條既有測試零改動照綠」

佐證:file: `scripts/lumos:4707`

佐證:file: `scripts/lumos:4710`

佐證:file: `scripts/test_lumos.py:22464`

說明:這 17 條主要保護共用的 `_roster_observe` 解析、分桶與四模式相容性，不等於維護兩套對帳邏輯；旗標入口只是一次共用函式呼叫。只要 S1 同樣復用該函式，保留測試反而能防回放用途倒退。因此攻擊角度③不足以否決 S2。

攻擊角度②「r1 對帳恆綠」也不成立：dispatch 快照若少席、錯家族或同名兼任，r1 就能立即報異常；它不是天然恆綠。真正成立的是 ext-f3：r1/r2 交界可能對錯輪。
