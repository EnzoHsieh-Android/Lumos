severity: major

## F1 被擋規則的新增命中會把 `pitfalls --diff` 的分級推成 high,而且 `lint-waive` 管不到它
severity: major
blocking: 是(判準:照字面實作後,放行過的命中仍讓分級變 high、逼出代碼審,spec 宣稱的「放行」只對一道閘成立)
- spec 段落:範圍做 4(宣告範本三條)、〈不做〉「不改新增告警閘本身」。
- 問題:`.lumos/lint.json` 的宣告不只被新增告警閘讀。`pitfalls --diff` 也逐條跑宣告,而且完全不看放行檔。對齊時,落在新增行上的命中直接進分級。`_pitfall_tier` 只要有任何 claim 就回 high,不分 level。覆核級、提示級的新命中本來就會常出現。每一筆命中,即使作者已經 `lint-waive`,都會讓整批改動變成 tier high,逼出代碼審迴圈。spec 的〈實務隱患〉只談誤擋量與放行,沒寫這條路。放行後 push 仍被「要過審」卡住,等於放行沒放。
- 佐證:file: `Lumos/main:scripts/lumos:65191` 的 `_lint_run_and_parse` 收集 `lint_claims`,對齊時只用 `added` 行過濾,沒有套放行。file: `Lumos/main:scripts/lumos:64545` 的 `_pitfall_tier` 寫著 `if claims: return "high"`。
- 引句:「作者用 lint-waive 附理由放行(誤報或接受風險都寫進理由)」
- ⚠ 這是從程式推出來的,我沒有實際跑過 pitfalls。

## F2 `check.py` 現有的「規則目錄全空」改壞測試在搬目錄後會判錯
severity: minor
blocking: 否(判準:只是測試期望過期,CI 會當場紅,容易修)
- spec 段落:範圍做 1、2(新增第四個規則目錄)。
- 問題:`t_kotlin_rulepack_samples` 的 `me` 複本只刪 `("rules","rules-review","rules-hints")` 三個目錄的 yml,然後斷言要報「一條規則都沒讀到」。`load_rules` 加了第四組之後,`rules-hints-unsourced/` 的 8 條還在,`rules` 不空,這個斷言翻紅(CI 有 ast-grep 才會跑到)。spec 的測試只列了 `t_kt_rulepack_unsourced_dir`,沒列要改這條。
- 佐證:file: `Lumos/main:scripts/test_lumos.py:126457` 的 `for d in ("rules", "rules-review", "rules-hints")`。
- 引句:「新增 `sgconfig-hints-unsourced.yml` 只載這個目錄」

## F3 `catalog_problems` 的既有測試傳的規則 dict 沒有 `dir` 鍵
severity: minor
blocking: 否(判準:實作時用 `r.get("dir")` 就沒事,用 `r["dir"]` 才會例外)
- spec 段落:範圍做 2(出處不全「只准放在 `rules-hints-unsourced/`」)。
- 問題:現在的檢查只看 `r["severity"]`。新檢查要看目錄,若寫成 `r["dir"]`,`t_kotlin_rulepack_messages_cite_catalog` 的改壞案例 `{"id":"kt-w","severity":"error","message":...}` 會 KeyError。spec 沒說這個案例要補 `dir`,也沒說缺 `dir` 時怎麼算(照字面該報)。
- 佐證:file: `Lumos/main:scripts/test_lumos.py:126500` 附近 `m.catalog_problems([{"id": "kt-w", "severity": "error", ...}])`;file: `Lumos/main:configs/ast-grep/kotlin-android/check.py` 的 `catalog_problems` 末段。
- 引句:放在 `rules/`、`rules-review/`、`rules-hints/` 任一個都報

## F4 新增的 SARIF 自檢步驟沒說要走逾時旗標與讀不懂輸出的處置
severity: minor
blocking: 否(判準:實作時順手接上就好,但不接會讓兩條既有改壞測試翻紅)
- spec 段落:範圍做 3、S2(標為 manual)。
- 問題:現有的 `scan()` 讀 `--json=stream`,有 `_TIMED_OUT` 旗標,輸出讀不懂回 None 報「跑不起來」。SARIF 要另一支函式。若它自己用 `subprocess.run` 而不共用旗標,改壞測試「逾時一次之後整次在 2.5 秒內」(`SCAN_TIMEOUT=1`)會多等,測試翻紅。junk sg(印 `not json` 然後 exit 1)也不能讓它噴例外。S2 又標成 manual,新步驟本身沒有機械的改壞測試。
- 佐證:file: `Lumos/main:scripts/test_lumos.py:126430-126460` 的 slow、slow2、junk 三組替身。
- 引句:型錄自檢的完整模式(要 ast-grep,CI 跑)多一項

## F5 沒有反向檢查:不是出處不全的規則放進 `unsourced/` 沒人報
severity: minor
blocking: 否(判準:只讓規則靜默不接閘,不會誤擋)
- spec 段落:範圍做 2、預期值表 S1。
- 問題:檢查只管「出處不全的規則不准在三個接閘目錄」和「unsourced 只收 hint」。有出處的規則放進 `rules-hints-unsourced/` 不會報,等於有一條逃出新增告警閘的路。之後某列補了出處,它的規則也不會被要求搬回。
- 佐證:`_DIR_SEVERITY` 只依 severity 判;`catalog_problems` 目前只算 `weak_ids`。
- 引句:`_DIR_SEVERITY` 讓 `rules-hints-unsourced` 只收 hint

## F6 回合結束檢查(工作樹模式)也會跑這三條宣告,spec 沒評估
severity: minor
blocking: 否(判準:對自動流程是新增摩擦,不是錯誤輸出)
- spec 段落:範圍做 4。
- 問題:工作樹模式的白名單只認 `configs/ast-grep/` 底下的任何 `--config`,新設定檔會被接受。三條宣告 × 兩份快照,命中會逐回合擋,預算也變成原來的三倍。spec 的誤擋量實驗只量推送前。⚠ 我沒有實跑預算,只從 `_lint_wt_allow` 與 `_LINT_NEW_WORKTREE_FLOOR_SEC` 推。
- 佐證:file: `Lumos/main:scripts/lumos:41184`(`_lint_wt_allow`)、`:40933`。
- 引句:(三條同一個寫法、各自 `{LINT_FILES}`、`{LINT_SARIF_OUT}`)

## F7 型錄文字改寫的數字與分隔字元風險
severity: minor
blocking: 否(判準:只影響文字同步的精確度)
- spec 段落:範圍做 5。
- 問題:
  - 主表第 9 欄「批一(只有提示級規則,預設不接)」實際是 40 格,spec 說 41 格(多算了定義那一行)。8 條出處不全列都在這 40 格裡,要保留的是其中 8 格,實際改寫 32 格。
  - 這欄用 `;` 分隔子欄,`behavior_value` 的正規式是 `行為測試或正向約束=([^;]*)`。新文字不要在括號內放 `;`。
  - 測試用「告警帶寫法=批一」當前綴挑列(`test_lumos.py:126658`),新文字要保留這個前綴。
- 佐證:`checks-catalog.md` 主線版,我用 `main_rows` 讀表算出 40 與 7;`catalog_problems` 與 `behavior_value`。
- 引句:第 11 行通電批次欄的定義、那 41 格

---

## 逐類回答(其餘風險類,皆未發現問題)

- 8 條搬目錄後同檔其他規則:主線算出恰為 API-36、ARCH-3、UI-103、CO-37、FLOW-14、STATE-9、TEST-16、TEST-33 各一條,全是 `rules-hints/` 的 hint。`api`、`architecture`、`compose`、`coroutines`、`flow`、`state` 各剩 4 到 6 條。`testing.yml` 7 條拿走 2 條(TEST-16、TEST-33),剩 5 條,新目錄的 `testing.yml` 含 2 條。搬的時候要照 `---` 切文件。沒有檔會變空。壞例、好例按規則 id 分目錄,`_sample_owner` 不受影響。
- 好例檢查的已知誤報排除:現有 `review-fp-` 樣本 12 份全在 12 條覆核級規則底下,提示級沒有。所以「只對 `rules-review/`」照舊成立。提示級若日後放 `review-fp-` 檔,會當好例誤報、沒有逃生口,這是嚴格而不是錯。
- SARIF 的 note 等級:`_lint_run_and_parse` 不看 `level`,note 的結果照樣變成 claim(file: `Lumos/main:scripts/lumos:42244`)。ast-grep 主線 `cloud_print.rs` 的 `severity_to_sarif_level` 把 Info、Hint 都對應成 note,SARIF 模式有輸出;GitHub 模式才略過 hint。0.51.1 沒實跑,本機沒有 ast-grep。
- 指紋穩定性:`_lint_new_key` 用規則加檔名加命中片段,不含 level 與工具名,note 結果的指紋跟其他告警同形。
- 三條宣告重複規則 id:每份設定只載自己的目錄,`check()` 本來就在全部規則上查 id 重複,所以不重複。`_lint_stacks_for_diff` 對不同字串的命令不去重。
- 型錄自檢的批次欄(`batch4_expected_tags`):只看「批四」與接電標籤,不讀「批一」文字,所以改寫那 40 與 7 格不會碰到它(受 F7 的 `;` 限制)。型錄 41 格與 7 格的改寫不會撞到 `catalog_problems` 的其他檢查。
- 規則包測試的複本:`_ktpack(copy=True)` 用 `copytree` 整包複製,會自動帶上新目錄(受 F2 的限制)。

## 固定席:對 `規則包覆核兩級接新增告警閘_計劃` 與連結節點的影響
- 對 [[Systems/kotlin規則包]]:節點管 5 支檔,0 條合約,0 行 KEY,所以不破壞任何合約。唯一牽連是它的 WHY「查不到的列標(出處不全),引用它的規則只准提示級」。這份設計把它收緊成「只准放 `rules-hints-unsourced/`」,方向一致,但 F5 指出反向沒守。
- 對 [[Systems/linter精選目錄]]:節點 0 條合約。其中 KEY「提示級規則預設不接」被這份設計改寫,是計劃明說的。KEY 是線索,不是合約,計劃有列入文字同步,不算破壞。

總結:最高等級為 major,blocking 共 1 條
