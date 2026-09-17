severity: major

## F1
severity: major
blocking: yes

新的 `_small_change_check`(小改動閘)要同時拿到「改動了哪些檔(含改名)」與「每檔改了幾行」,自己另開一條 `git diff --numstat <range> --` 查詢(非 `-z` 模式),然後手刻一支正則 `_numstat_new_path` 去解 `--numstat` 在非 `-z` 模式下印出的壓縮改名格式 `{old => new}` / `old => new`。

但這個 repo 對「解析 git 改名輸出」早有既定寫法,而且理由正是要避開這個壓縮格式的脆弱性:`_lint_new_changed_files`(19318 行起)一樣是「另開一條只給這道閘用的查詢」,但它選的是 `git diff --name-status --find-renames -z`,用 NUL 分隔的字母代碼(R/C)+ 雙欄路徑去認改名,不去解析 `{a => b}` 這種文字縮寫;`_nodehome_changes`/`_nodehome_name_status` 也是同一套字母代碼 + `-z` 寫法。程式裡唯一一處真的去 regex 解析 `{old => new}` 壓縮字串的,就是這批新加的 `_numstat_new_path`。

而且 `--numstat` 本身在 `-z` 模式下就不會印出 `{old => new}` 這種壓縮格式,而是把新舊路徑各自印成獨立欄位(跟 `--name-status -z` 同一種安全形狀)——我在乾淨的 git 倉庫實測驗證過:同一次改名,`git diff --numstat HEAD~1 HEAD` 印出 `1	0	old.txt => new.txt`,而 `git diff --numstat -z HEAD~1 HEAD` 印出 `old.txt` 與 `new.txt` 兩個各自完整、不經壓縮的 NUL 分隔欄位。也就是說,只要在既有的 `--numstat` 呼叫上加 `-z`,就能沿用這個 repo 每一個同類消費者都在用的安全解析法,不需要另外刻一支正則去啃 git 自己的人類可讀縮寫格式(這格式對有共同前綴目錄的改名還會再摺疊成 `dir/{old => new}/f`,對含 `" => "` 或大括號等罕見檔名字串也沒有機械保證)。

這正好撞上這批自己在同一支函式的程式碔註解裡引用的教訓——16604 行附近解釋「為什麼 lumos 自己呼叫 git 時用 `-c core.quotePath=false`」時提到的就是同一類「非 `-z` 模式下路徑顯示會失真、下游字串比對全失效」的坑,這批卻在同一份 diff 裡對 `--numstat` 反其道而行,新開一種「非 `-z` + 正則拆解縮寫」的解法。

引句:「r = subprocess.run(["git", "-C", str(rr), "-c", "core.quotePath=false", "diff", "--numstat", git_range, "--"], capture_output=True, text=True, errors="replace")」

file: `scripts/lumos:19325`(既有慣例:`r = subprocess.run(["git", "-c", "core.quotePath=false", "diff", "--name-status",`,同函式接 `"--find-renames", "-z", diff_range],`,用字母代碼+`-z` 而非正則解縮寫)

file: `scripts/lumos:20816`(`_nodehome_changes` 同樣用 `"--name-status", "-z", "-M"`)

實測(不在 patch 內,獨立驗證 git 行為):於 /tmp/gittest 建一個改名提交,`git diff --numstat HEAD~1 HEAD` 印出 `1	0	old.txt => new.txt`(觸發這批要解析的縮寫格式);`git diff --numstat -z HEAD~1 HEAD` 印出的是兩個完整、未壓縮的 NUL 分隔路徑欄位,不含 `=>`,證明改用 `-z` 就能免掉這支正則。

## F2
severity: minor
blocking: no

`idx` 元組從既有的 `(split, default, methods_for, plats)` 擴成 `(split, default, methods_for, plats, git_range)`,對照 5479/5528 行既有的 `(split, default, methods_for, plats, names)` 同樣是「用位置成長元組傳一組同源設定」的既有形狀,擴充方式本身沒問題;`docstring` 有跟著更新(`idx=(split, default, methods_for, plats)`)。純粹提醒:這個 docstring 現在跟新簽章不同步(少了第五個欄位),但屬文件落後、不算另立做法。

引句:「idx=(split, default, methods_for, plats)。"""」

## 對照過的既有寫法
- `_BOOKKEEPING_DIR`(單一字串)改成 `_BOOKKEEPING_DIRS`(tuple),三個既有讀者(`_stack_changed_ok`、`_codeloop_record_valid`、`_small_change_check` 自己的排除邏輯)都同步改成 `startswith(_BOOKKEEPING_DIRS)`,沒有漏掉任何讀它的舊呼叫點(全 repo grep `_BOOKKEEPING_DIR\b` 已確認無殘留單數形式)——延續既有「一個常數、單一源」的慣例,不算另立做法。
- `[manual:]` 從擋改成收、`_clause_check_twoway`/`_spec_gate_twoway_static`/`_spec_gate_twoway_run_verdict` 三處都走既有的條款狀態機(`b["state"] == "manual"`)判斷,沒有繞過既有的條款解析或另開一套狀態判斷。
- `_TIER_ROSTER` 新增 `("code", "light")` 沿用既有 `_rseat(slot, family, occ, req, note)` 呼叫慣例與既有其他分級的 note 寫法(例如 `("code", "standard")` 那席「這寫法跟專案既有的一不一樣」的措辭),沒有另開一套編制格式。
- 留痕欄位 `n_manual`/`manual_only`/`small_change_rule` 沿用既有 `door_rule`/`clause_sha` 這類「版本號 + 判定結果」欄位命名慣例,寫入口仍是同一支 `_jsonl_append_verified` + `_vault_write_lock`,沒有繞過既有的寫入口。
- 錨點清單讀取沿用 `_ANCHOR_BASELINE_REL` 既有路徑常數(patch 自己在 5661 行註解也點名「別再手寫路徑、別再猜形狀」)。

引句(clean 段落至少一句完整 patch 內容):「    ★真效果只在 code-loop 留痕豁免這第二消費者★:pitfalls 那端 canary-log 早被」
