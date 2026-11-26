severity: minor

我逐 hunk 讀了 r3-repair.patch,並實跑 `python3.14 scripts/test_lumos.py -k choice_cov`:78 項全過,0 失敗。

**修補三問**
- **修到沒:** 上輪的修補我都對得上程式。
  - Groovy 任務名單加了 `*.toString()`。
  - 存快取走 `_write_bytes_atomic`。
  - 分析輸出缺 `nolines` 或 `noclasses` 算失敗。
  - Robolectric 0 不進快取,而且 `cached()` 讀到舊的 0 份會刪掉重量。
  - 掛覆蓋逾時當場斷路。
  - 不掛重跑被截斷不寫基準。
  - 清快取保留數把這次的 at_sha 算進去,`_choice_cov_prune` 在 `_choice_cov_dir` 建資料夾之前呼叫,清完剛好 2 個。
- **有沒有引入新問題:** 沒找到會做出錯行為的洞。
- **同類位置還有沒有:**
  - `after` 的呼叫端只有 `_kill_measure_singles` 一處(`scripts/lumos:29122`)。沒帶 `after` 的 `_kill_merge_singles` 走 else 分支,`_kill_run` 回傳固定 4 項,解包安全。
  - `cov_judged` 讀寫兩端都齊:`_GOV_FIELD_TYPES`(`scripts/lumos:18496`)、gov 的 ck 欄位(`scripts/lumos:18587`)、寫入端(`scripts/lumos:80145`)。
  - 新增的測試函式沒有同名重複定義。

**合約**
- guard-kill 的 rc 優先序與 `--json` 純淨兩條 ★INVARIANT★ 沒被碰到。
- 新增的斷路訊息走 stderr。

severity: minor
blocking: 否
`scripts/lumos:29290` 的 `red_rerun` 與 `Projects/選擇點存活回指條款_計劃.md:104`、`:105`:程式新加了三個行為,計劃與 `Systems/guard-kill.md` 的 PITFALL 都沒寫。
- 掛覆蓋跑滿單支上限會當場斷路,這次 run 的 `cov` 記 `tripped`。
- Robolectric 專案類別有紀錄數為 0 的覆蓋資料不進續跑快取。
- 分析輸出必須三個鍵都在。

場景:三個月後的人照計劃第 105 行,以為只有「前 5 支 Robolectric 皆 0」才會斷路,看到 `cov: tripped` 卻找不到對應條款。照計劃第 111 行的續跑快取描述,也會預期每份覆蓋資料都在 `choice-cov/` 底下。
- guard-kill 的 PITFALL 只寫「連續 3 支掛覆蓋紅不掛綠就斷路」與 `after` 固定 6 項,沒提逾時即斷路。
- 不影響行為與測試,屬文件精度。

引句:「連續 3 支掛覆蓋紅不掛綠就斷路;after 固定回 6 項」

總結:最高等級是 minor
