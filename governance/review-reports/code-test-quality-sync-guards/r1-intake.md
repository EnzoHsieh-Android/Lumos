# r1 intake

preflight-4: ran

兩席（單審、架構對齊，皆 Claude sonnet）收齊後才寫入卷證；被審 repo 未被動。架構對齊席報告的三行 severity 為縮排條列，以 report-normalize --write 做純格式搬移（不改等級、不碰引句）。單審席為 clean，實跑五個指令的 --help、兩支掛鉤的 should_exclude（消費專案豁免、來源 repo 不豁免、近似檔名不誤放）、頂層指令實數 85 與四支守衛測試，皆無 finding。

| id | source | severity | reproduce | disposal | evidence |
|---|---|---|---|---|---|
| SGA-1 | 架構對齊 | minor | HIT | folded | reference.md 全覽的 test-quality 條目改成子指令後接括號用途，跟 drift、guard 等鄰居同形 |
| SGA-2 | 架構對齊 | minor | HIT | folded | INDEX 九類子檔表 03 列「裡面有」補上 test-quality，總目錄重新有指路；03 子檔第 45 行連到接入標準；總目錄 4494 字元、t_command_index_complete 綠 |
| SGA-3 | 架構對齊 | minor ⚠ | HIT | accepted | reference.md 全覽按功能分組、INDEX 按情境分子檔，兩份本來就不同軸；test-quality 是寫測試時用、test-layers 是動手前算該補哪層，情境不同 |

regression_set：none（三條都是本輪新改動的寫法與歸位，不涉上一輪修補）。
