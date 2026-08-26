# 審查報告:嚴重度綁定機械掃 r3(delta 席,折入回歸鏡頭)

sha256 已核對 = fbf0a098073c2b53288625d2b1a516a0277e42c5f576b179cd81bb291e7d6b4e。已讀 r3 快照全文、r1 五席+r2 delta/外家報告、與 r2→r3 逐行 diff;並對照 scripts/lumos 寫側(cmd_canary/argparse)、disposal 尾端與 T6 定錨程式碼、docs/.canary-log.jsonl 真實帳本(754 行全量掃描)。

### d-f1
severity: major
引句:「凡帶 --loop+--round+--auditor 的★審查席帳列★一律必附 --report」
佐證:file: `governance/review-reports/severity-scan/r3-snapshot.md:28`
佐證:file: `scripts/lumos:15463`(--severity 為獨立選填引數)
佐證:file: `scripts/lumos:15493`(--report 為獨立選填引數,無 required/互斥綁定)
佐證:file: `docs/.canary-log.jsonl:492-494`(2026-08-22T19:05:25~26,bound-tests-gate-b/r1,auditor=s2/s3/arch,severity=major,loop/round/auditor 齊備但無 report_path)
佐證:file: `docs/.canary-log.jsonl`(全量 754 行,681 行同帶 loop+round+auditor,其中 286 行缺 report_path)
說明:照這段文字實作,`canary record` 只要偵測到 --loop --round --auditor 三者齊備、卻沒帶 --report 就直接 rc2 擋掉入帳,而且沒有任何時間或情境豁免——條款自己在下一段把「生效日」明文限定只給 [S2] 讀側用,並明禁在 [S1] 寫側刻 ts 分支,所以這條硬擋是無條件、立刻生效的。用今天(2026-08-26)這份真實帳本實測:同時帶 loop+round+auditor 的 681 行裡,286 行(42%)沒有 report_path;把 2026-08-14 canary 協議停用後的「none」世代單獨抓出來看,08-22(離這次 r3 審查只有 4 天)的 `bound-tests-gate-b/r1` 迴圈裡,s2、s3、arch 三個席位就是照現有程式碼合法呼叫方式——帶 loop/round/auditor/severity/findings_set 等 T1 處置帳欄位,但沒帶 --report——留下的,而且同一分鐘內緊接著的 `bound-tests-gate-c` 又把同一輪重新完整記了一次(顯示這不是死掉的舊制度,是這條工具鏈這幾天實際被使用、且會重複發生的操作形狀)。這三筆帳完全不落在條款寫明的唯一豁免類別「非審查類帳列如自主迴圈結局帳」裡(它們帶 findings_set,是不折不扣的審查席帳)。字面上線那一刻,任何人只要重演這個帳本四天前才發生過的操作順序,就會被硬性擋下,而條款全文沒有承認這是一次行為改變,也沒有交代要不要豁免、怎麼過渡。

### d-f2
severity: major
引句:「對 2026-08-25 起全部 d5 迴圈帳列跑 [S2] 歷史掃」
佐證:file: `governance/review-reports/severity-scan/r3-snapshot.md:31`
佐證:file: `scripts/lumos:3914`(2026-08-14 canary 協議停用註解,d5 世代起點)
佐證:file: `docs/.canary-log.jsonl`(ts≥2026-08-14 且同帶 loop+round+auditor 共 343 行,其中 218 行 ts 落在 08-14~08-24、早於 08-25 掃描起點)
佐證:file: `docs/.canary-log.jsonl:492-499`(bound-tests-gate/-b/-c 三迴圈全部落在 08-22,即該 218 行之內)
說明:[S4] 自稱要把「0/18 的人工核升級成 n/全量的機械帳」,但把首次歷史掃描起點釘死在「2026-08-25 起」。實測帳本:進入條款自己定義的 d5 世代(2026-08-14 協議停用)之後、同時帶 loop+round+auditor 的帳列共 343 筆,其中 218 筆(約 64%)ts 落在 08-14 到 08-24 之間,早於 08-25 這條掃描起點——包含 d-f1 引用的 `bound-tests-gate`/`-b`/`-c` 三個迴圈(08-22)全部在內。這代表就算 [S1] 寫側強制真的照計畫落地,[S4] 承諾的「首驗」本身也不會去檢查這 218 筆:它們既晚於協議停用、屬於條款自己劃定的守備範圍(d5),又落在條款宣稱要「全量」機械化的名單裡,卻因為一個條款裡沒交代來源的日期常數被排除在外。照字面實作上線,驗證紀錄裡要寫的「n/全量」其實是「n/(全量−218)」,而條款文字沒承認這個落差,也沒交代 08-25 這個起點怎麼選、要不要往前補。

## 掃過但乾淨的面
- r2 六條折入逐條核對 r3 條款本文,全部真的落進條款/fixture(非只改現況事實段落散文);與 r2→r3 全文 diff 核對,六處改動與審計修正紀錄逐條對應,無掛羊頭。
- 「非審查類帳列如自主迴圈結局帳不受影響」這條豁免在真實帳本上機械成立:全帳僅 2 筆帶 --outcome 的自主迴圈結局帳,兩筆都只帶 loop+auditor、不帶 round,天生落在「loop+round+auditor 三者齊備」條件之外,不會被 [S1] 誤傷。
- `_SEV_ORDER` 折入(arch-f2)屬實:`scripts/lumos:3911`、`scripts/lumos:4100` 兩處既有字面序完全一致,與 `scripts/lumos:15463` 的 --severity 四值白名單對齊,抽常數不會遇到既有三處互相打架的隱藏地雷。
- S1 條款本文沒再提 --snapshot 是否仍強制,不構成新缺口:disposal ③ 留痕重驗(`scripts/lumos:10226-10262`)已經獨立對「判定輪全席」逐一要求 report_path 與 snapshot_path 齊全、sha256 與帳面一致,任一缺席都 FAIL——這一層既有且不受本案改動。
- d-f4 折入的「高報安全」方向有真代碼撐著:`scripts/lumos:10217`、`scripts/lumos:10219-10220`——帳面記得越高,下游判定越嚴,不存在「回報高反而放水」的路徑。
- ext-f5 的 regex 修法邏輯自洽:逐行 fullmatch 天生不會有 \s* 吞換行跨行黏合的問題。
