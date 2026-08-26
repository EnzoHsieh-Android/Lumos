# dref-v4 r1 架構對齊席
### arch-f1
severity: clean
引句:「雙欄 edit helper(讀一份 fm→remove _ai/add 正欄→一次 atomic_write_verify,★count-based expected_check:此 ref 正欄恰一份、不在 _ai★」
佐證:file: `scripts/lumos:8487`;file: `scripts/lumos:8117`
說明:V6 promote 的「讀一份 fm、改多處、一次 atomic_write_verify」非新招,cmd_decision_supersede 已同款(改 valid/插 superseded_by/bump updated 後一次落盤,註解原話「不串第二個寫命令避免半完成」)。既有寫入原語直接延伸。

### arch-f7
severity: minor
引句:「分欄列 ref(顯式子命令避裸節點名撞子命令)。」
佐證:file: `scripts/lumos:16182`;file: `scripts/lumos:15897`
說明:spec 沒點名六原語底層用哪種掛法。庫有兩種:rel-cascade 單 verb+choices 共用旗標、about-code/guard 巢狀 add_subparsers 各自宣告。六原語參數形狀差異大(backlog 不吃節點/candidates·list 吃節點/add-ai·prune·promote 吃節點+ref),更像後者。實作前照既有兩種裡「參數形狀相近的」(巢狀 add_subparsers)接,免長第三種。

## 對齊良好的面
V6 promote 非自造(supersede 先例);三具名邊對 TYPED_EDGE_FIELDS、exact-dedup 沿 _append_decision_ref、跨欄 expected_check 有 cmd_set 先例;rc 0/2 全庫一致無夾帶 rc=1;decision-refs 獨立子命令群延續 T1 「不進 LIST_KEYS、需專用 writer」界線。唯一沒點名的是 CLI 掛法(arch-f7 minor)。
