severity: major

**鎖檢查**:`/Users/enzo/.cache/lumos/dispatch-lens/e66c46f232ba45926460402ae71cc97b4218b4c132a2860b2ad8075c5539647b.json.warming` 目前不存在。目錄裡只有 4 個別的 `.warming`,我沒動它們。我也沒刪任何鎖。

severity: major
blocking: 是
`scripts/lumos`(`_CHOICE_COV_ANALYZE`,r2 修補 ④):分析任務「依賴編譯」的修法在 Groovy 裡不會生效,等於沒修。
引句:「if (v) dependsOn(proj.tasks.matching { it.name in ["compile${v}Kotlin", "compile${v}JavaWithJavac"] })」
- 這個清單裡是 GString(帶 `${v}` 的字串)。`it.name` 是 String。`in` 走 `list.contains(it.name)`,也就是 `String.equals(GString)`,結果恆為 false,所以 `matching` 永遠是空集合。
- 失敗場景是續跑快取全命中:`todo` 為空,沒跑任何單支基準,而隔離樹是新建的,樹上沒有編好的類別。
  - 這時分析任務沒有編譯依賴,`files.isEmpty()` 成立,輸出 `noclasses: true`。
  - 這一路再走到 `_choice_cov_parse` 回「分析失敗」,所有行不明、壞法跑全部測試。
  - 同一份快取重跑,每次都停在這裡。這正是 r1 F4 要修的情境。
- 最小重現(已用本機 Gradle 8.13 附的 Groovy 3.0.22 實跑):
  ```
  java -cp "$(ls <gradle-8.13>/lib/groovy-*.jar | tr '\n' ':')" groovy.ui.GroovyMain t.groovy
  ```
  內容 `def v='Debug'; println('compileDebugKotlin' in ["compile${v}Kotlin"])` 印 false。加 `.toString()` 後印 true。
- 測試為什麼沒抓到:`t_choice_cov_init_scripts` 只檢查 `"dependsOn" in ana` 這種子字串。假 Gradle 不執行腳本,所以把依賴弄壞,測試照綠。這個測試保護的是必要行為,卻抓不到它壞掉,依你們的判準算 major。
- 修法方向:清單改成字串字面值或 `.toString()`,或改成 `it.name.startsWith("compile${v}")` 之類的比對。測試至少要用 Groovy 解析或執行這段判斷,不能只看有沒有 `dependsOn` 這個字。

severity: minor
blocking: 否
`scripts/lumos`:`_choice_cov_analyze_cmd` / `_analyze`。「未能重現」,沒有真的 Android 專案可跑。
引句:「cap = max(60.0, len(cand) * 0.5)」
- 就算上一條修好,續跑全命中時分析任務要先冷編譯整個模組,上限只有 60 秒加每支 0.5 秒。
- 大型 App 冷編譯很容易超過,逾時回「分析失敗」。
- 這個失敗會被記成暫時性、每次續跑都再發生。
- 預算判斷的 `remaining() < cap + avg` 也沒把冷編譯算進去。

severity: minor
blocking: 否
`scripts/lumos`:`_choice_cov_prune`。
引句:「for x in subs[_CHOICE_COV_KEEP:]:」
- 這次的 at_sha 還沒有資料夾時(新提交第一次跑),清檔先保留舊的 2 個,之後 `_choice_cov_dir` 才建新的。這一輪結束時 `choice-cov/` 底下有 3 份,多於計劃寫的「只留最近 2 個」。
- 下一次 choice-kill 開頭才會收斂。只佔磁碟、不影響判定。

**其餘我走過、沒找到洞的 r2 修補**
- cov_sha 讀寫共用,`None` 判成不同、寫入記空字串,`_choice_kill_pick`、`_choice_reach_valid`、`--reach-only` 三處都對得上。
- `_choice_reach_fill` 的 `guard` 在 `rng` 為假時不會被取用,沒有 NameError。
- 連續 3 支掛覆蓋紅就斷路:連續數在綠時歸零,`_kill_measure_singles` 的第 5 項秒數也有接上預估。
- 覆蓋資料檔在快取與 scratch 的存放路徑沒有碰撞。
- `cov_judged` 只有寫入端,沒有任何讀者(`gov --stats` 的 `ck` 欄位清單也沒帶它),所以不報。

**圖譜固定席**
- `guard-kill` 的兩條 `★INVARIANT★`(rc 優先序、`--json` 只印一行 JSON)沒被碰到:新增輸出都走 stderr。
- `rc` 的映射沒改。
- 其他固定席節點都是牽連檔重疊,這次沒有內容衝突。

總結:最高等級是 major(1 條:分析任務的編譯依賴在 Groovy 裡是空的,測試也抓不到)。
