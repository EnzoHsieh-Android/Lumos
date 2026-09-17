# r1 收貨(2026-09-17)

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-sonnet | major | HIT:git mv 後 numstat 印 tests/{test_x.py => test_y.py},落點判外 | 折:numstat 加 --no-renames(案例⑦) |
| F2 | 單reviewer-sonnet | major | HIT:+00:00 與 +08:00 字串比對反序(純 python 重現);與 A3 同一件事 | 折:走 _loop_ts_key(案例⑨) |
| F3 | 單reviewer-sonnet | minor | HIT:numstat 對二進位印 -,記成 0 行相對量恆過 | 折:二進位=算不出量不當小改動(案例⑧) |
| A1 | 架構對齊-sonnet | major | HIT:_BOOKKEEPING_RE 是第二套簿記判準(既有 _BOOKKEEPING_FILES/_DIR 註解明寫單一源) | 折:改用既有白名單+_PITFALL_DIFF_SKIP_EXT+筆記路徑 |
| A2 | 架構對齊-sonnet | major | HIT:手寫 anchor-baseline 路徑與解析,既有 _ANCHOR_BASELINE_REL 與 data.get("anchors") or {} | 折:改用常數與既有解析 |
| A3 | 架構對齊-sonnet | blocker | HIT:同 F2(裸字串比 ISO 時間戳;_loop_ts_key 旁註解就寫過別再犯) | 折:同 F2 |
