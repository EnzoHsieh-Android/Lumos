# r3 收貨(2026-09-17;standard 上限輪)

複核:r2 三件關上(通才席重跑;架構席對照)。本輪四條全折;★上限輪的折入沒有第四輪新席複核★(留痕與計劃註明)。

| id | 席 | 嚴重度 | 重現 | 去向 |
|---|---|---|---|---|
| F1 | 單reviewer-r3-sonnet | major | HIT:git mv 程式檔進 governance/replay/ 後被路徑前綴豁免,四維度看不到 | 折:新舊路徑都在簿記/卷證/筆記內才豁免(案例⑫) |
| F2 | 單reviewer-r3-sonnet | minor | HIT:改名+大改用新路徑查 base 樹查不到,原本行數算成 0 | 折:用舊路徑查(案例⑬) |
| A1 | 架構對齊-r3-sonnet | major | HIT:repo 慣例是 -z 欄位解析改名,不自刻正則;實測 numstat -z 改名印 la\tld\t\0舊\0新\0 | 折:改 -z 解析,拿掉 _numstat_new_path |
| A2 | 架構對齊-r3-sonnet | minor | HIT:_spec_gate_push_one docstring 少第五欄 | 折:同步 |
