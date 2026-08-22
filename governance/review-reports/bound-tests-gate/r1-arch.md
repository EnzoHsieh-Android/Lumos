# r1 架構對齊席
F1 [major] 引句:「不動 pre-push 本身(它認留痕即可)。」+「先把波及節點上綁的合約測試真跑一遍,一條紅就拒絕留痕」——跑測試掛在 pass(記錄路徑)不在 check(擋的路徑);tier 非 high 不要求 pass → 新閘形同虛設。依賴方向反了。(scripts/lumos:14394-14485 _codeloop_guard_verdict;pre-push:126)
F2 [minor] 引句:「帳:治理帳 gate=code-loop kind=bound-tests-red / bound-tests-green(節點=被擋的合約),gov --stats 可見。」——鄰居慣例是子機制各自成 gate、kind 裸結果詞(kill/delguard/design-loop);應 gate=bound-tests kind=red/green/skipped。
F3 [major] 引句:「超時:每支 max(60s, 5×baseline?) —— 沒 baseline,固定 300s,`LUMOS_BOUND_TEST_TIMEOUT` 可調;超時算紅(沒跑完=沒驗)。」——第二種 timeout 政策(kill 是 baseline×5 floor 可覆寫);兩套以後要改兩處。
不對齊共 3 條,其中 major 2 條。
