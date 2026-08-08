---
type: project
status: superseded
created: 2026-08-08
updated: 2026-08-08
signed_off: 2026-08-08
tags:
  - type/project
  - status/superseded
summary: |
  KEY:給 lumos mutate 一個自動消費者(現況零消費=蓋好沒人用病)——advisory 不進閘;核心張力=mutate 對大檔×全套測試爆炸、code-loop 收貨常含大檔,故消費者選型 A(code-loop 即時,踩爆炸)vs B(每日 autonomous-loop 過夜,無延遲無爆炸)傾向 B 先
  KEY:防爆三招=預算上限(sha256 抽樣)+跳過重測試檔(skipped:heavy-test)+總時限 partial;活口→mutation-survivors.jsonl→backlog gap 候選→人裁(不自動寫測試=maker bias 鐵則)
  KEY:刻意不做——自動生成採納測試/mutate 進閘(v2)/改 mutate 本體
  KEY:★r1 panel 致命發現:選型 B(autonomous-loop)是死消費者——非 dry-run 已 exit 2 停用(confused-deputy 凍結),且「git-backup cron 撿走」前提假(那 cron 備份的是 /Users/enzo/script 另一個 repo,碰不到本 repo);retrieval-history 是人做功能時順手 commit 非自動撿。→ mutate 寫進 mutation-survivors.jsonl 會永遠沒人 commit=結果蒸發,比「沒人手動叫」更糟。設計未收斂→待 Enzo 選方向★
  FLAG:DECISION
---
# mutate接消費者_計劃

> ★結案裁定(2026-08-08,Enzo signoff)★:**不接自動消費者、不進閘,mutate 停在手動唯讀觀測工具。** 理由=設計審證兩消費者皆有擋路(B 死/A 需大改)+機制無乾淨的家+避免過度測試(mutate=需要時照洞的手電筒,非全天候探照燈;測試天花板是 oracle 品質非數量)。本計劃擱置,四選一不再懸而未決。**未來若真要接:先解 testmap 逐檔粒度(大檔可用的鑰匙)+防爆,再另立新計劃,勿復用本節點。**

> 緣起(2026-08-08,Enzo):`lumos mutate`(S4 落地)是唯讀觀測工具,現況無自動消費者=撞「蓋好沒人用」命名病(機制價值判準=對自動 loop 有沒有用)。本案給它一個必經之路上的消費者,advisory 不進閘。★核心張力(落地前實測已知)★:mutate 對「大檔×全套測試」= 乘法爆炸;code-loop 收貨處理的 tier=high diff 常含 scripts/lumos 這種大檔——直接接 code-loop 收貨=每次都踩爆炸點。故「接哪個消費者+怎麼防爆」是設計核心。

PRIOR-ART: ① 最小解層級——複用既有 `mutate`(不改工具本體)+接既有消費點(code-loop 收貨段 或 每日 autonomous-loop 的 run_exam 旁),advisory 輸出沿 impact hook 的注入慣例;無新機制。② 世界解:mutation testing 的 CI 整合實務普遍用「diff-scoped + 預算上限 + 只跑受影響測試」控爆炸(incremental mutation testing)——本案的防爆三招同源。③ Growth test 三問:事故=mutate 現況零消費者(蓋好沒人用,機制價值判準明文);非風格;既有機制(mutate/testmap/impact hook)小修即可接,無新輪子。④ 裁定=borrow-design。

## 消費者選型(A/B 攤明,設計審裁)
| 選項 | 消費點 | 爆炸暴露 | 延遲敏感 |
|------|--------|----------|----------|
| A code-loop 收貨 advisory | 終審時對 diff 跑 | ★高★(tier=high 常含大檔) | 高(人在等收斂) |
| B 每日 autonomous-loop | run_exam 旁定期掃近期 diff | 可控(過夜跑,預算大) | 無(無人等) |
| C 兩者都接(B 先) | — | — | — |

**傾向 B 先**:過夜無延遲壓力、預算可放大、活口清單進 backlog 當 gap 候選(接既有 gap 挑選鏈)——爆炸與延遲兩個風險在 B 都不觸發;A 的即時價值高但正踩爆炸點,列 v2 待「只跑快測試檔」的防爆件成熟。

## 防爆:mutate 需小改本體(r1 勘誤:原「不改本體」站不住,pre-flight 抓回——防爆需 mutate 吐選測+內部時限)
三處必要小改(mutate v1.1,非新機制):
- **`--max-seconds` 內部 wall-clock cap**:mutate 自己看時鐘,逾時中止已跑變異、標 `partial:true`——★不靠外部 timeout★(外部 SIGKILL 不觸發 finally,留孤兒 worktree;pre-flight 抓回)。
- **`--json` 加 `selected_tests` 欄**:吐內部實際選到的測試檔集——消費者才能判「這批選到的是不是整套 runner」(現況 tests_for 不外露,判重無據)。
- **`skipped:heavy-test` 桶**:mutate 內部啟發式——選測檔行數 > 閾(如 500,單腳可落地;「全套 runner 標記」無機械錨,誠實天花板,不做另一腳)→ 該 diff 檔整檔跳、標此桶,不硬跑爆炸。
- 預算上限沿既有 `--mutation-budget`(消費者傳保守值如 20)。

## 消費者接法(v1,取 B——per-file 逐檔跑)
- autonomous-loop.sh run_exam 之後加段:對「近 N 天有改動的 .py 檔」**逐檔**呼叫 mutate(每檔一次 `--diff <range>` 但靠 heavy-test 桶自動跳重檔;`--max-seconds` 各檔設上限、`--mutation-budget 20`)。
- 產出:活口(`mutants[]` 中 `bucket=="survived"`,r1 勘誤:非頂層 survived 鍵)append 進 `governance/mutation-survivors.jsonl`。

## 規格(v1,取 B)
- 活口→gap:呼叫 `backlog.add_gaps(backlog_path, gaps, today)`(r1 勘誤:非 gap_select.select——後者吃單一 report 的 gaps 鍵,格式不符;真正吃 gaps list 的是 backlog.add_gaps),gaps=[{weakness:"<file>:<line> <op> 變異無測試殺得死=測試網洞", suggestion:"補一條會殺死此變異的測試", ...}];人裁放行才進 pending(既有人閘,不自動補測試——maker bias 鐵則)。
- **帳版控裁定(r1,pre-flight)**:`mutation-survivors.jsonl` 比照 `retrieval-eval-history.jsonl` **版控**(它是跨期總帳,非 backlog 那種本機暫存)——不進 .gitignore;dry-run 下 run_exam 已有寫 retrieval-history 先例(雖不 commit,由既有 git-backup cron 拾取),同路徑。
- **不自動寫測試**(合約候選):最多把活口變成「待人補測試」的 gap。
- dry-run 相容:autonomous-loop 非 --dry-run 已 exit 2,mutate 段在 dry-run 下仍真跑觀測(唯讀,同 run_exam)。

## 審計修正紀錄
- **pre-flight(2026-08-08)**:①「不改 mutate 本體」站不住——防爆需 mutate 吐 selected_tests+內部 --max-seconds(外部 timeout SIGKILL 不觸發 finally=孤兒 worktree)+heavy-test 桶,升為 mutate v1.1 ②活口→gap 誤指 gap_select.select(吃單一 report),改 backlog.add_gaps(吃 gaps list) ③mutate --json 無頂層 survived 鍵,改「mutants[] 中 bucket==survived」 ④帳版控裁定=比照 retrieval-history 版控 ⑤「全套 runner 標記」無機械錨,heavy-test 只用行數閾單腳(誠實天花板)。

## r1 panel 結論:設計未收斂(前提失敗,待裁)
**3 席一致 blocker:選型 B 是死消費者**——
- autonomous-loop 非 dry-run 已 `exit 2` 停用(confused-deputy 安全凍結,與本案無關);dry-run 分支不 commit。
- 「git-backup cron 撿走」前提**查證為假**(s2+Codex 實查):那支 cron `cd` 到 `/Users/enzo/script`(另一個 repo),永遠碰不到 `lumos-toolchain/governance/`;retrieval-history 之所以在版控,是人/agent 做功能時順手 commit,非自動機制。
- 故 mutate 接 B = 寫一個永遠沒人 commit 的本機檔=結果蒸發,比「手動沒人叫」更糟。

**其餘 blocker(接 A/B 都要面對)**:mutate 現況無 `--file`/pathspec,「逐檔跑」在現 CLI 做不到(整 range 全跑=爆炸×N);heavy-test 桶的「該檔對應測試」在現況 flat tests_for 架構無逐檔界線;「重用既有 skipped 鍵」是幽靈(mutate 只有 killed/survived/no-test-selected);severity 欄會被 backlog.add_gaps 靜默丟棄。

**待 Enzo 選方向(四選一)**:
1. **轉 A(code-loop 收貨)**——唯一「真的會跑+會 commit」的必經之路;代價=終審延遲+需 mutate 長 `--file` 第四改+heavy-test 防爆真做。
2. **半自動**——mutate 寫進 code-loop 收貨 skill 當「必跑步驟」(人跑 code-loop 時順手跑),介於全自動與沒人叫之間。
3. **先解 autonomous-loop 凍結**(confused-deputy)再接 B——最大、碰安全凍結區,風險最高。
4. **擱置**——記帳「mutate 待基建成熟才有乾淨消費者」,不硬塞。

## 刻意不做
- 自動生成並採納測試(maker bias 閉環,pbt-oracle 鐵則)。
- mutate 進閘(仍觀測;A 案 code-loop 即時接=v2,待防爆件)。
- ~~改 mutate 工具本體~~(r1 撤:防爆需 mutate v1.1 小改——加 --max-seconds/selected_tests/heavy-test 桶;不改的是「算子/殺活判定」核心邏輯)。

## 實務隱患
- **效能/資源**:防爆三招(預算/跳重測試/時限)為核心;過夜跑無延遲面;worktree 沿 mutate 既有清理。
- **[self-governance]**:advisory 不擋人;活口→gap→人裁,誤報成本=人多看一眼即棄。
- **[prod-irreversible]**:不適用(唯讀+臨時 worktree+append 帳)。

## 驗收線
- mutate v1.1 測試:`t_mutate_v11`(--max-seconds 逾時標 partial 且清 worktree/selected_tests 欄吐出/heavy-test 桶行數閾跳檔)。
- 消費者測試:`t_mutate_survivors_to_gap`(活口→backlog.add_gaps 格式/mutation-survivors.jsonl append/不自動寫測試)。
- 實跑:autonomous-loop --dry-run 跑一輪,mutation-survivors.jsonl 產出且活口如實(小檔驗;大檔標 heavy-test)。
- 不設「活口須為 0」門檻(觀測,防預期寫成驗收)。
