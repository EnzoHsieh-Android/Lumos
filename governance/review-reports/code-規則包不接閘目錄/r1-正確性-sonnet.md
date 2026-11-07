severity: minor

審查範圍是 r1-snapshot.patch。我另外在 repo 內跑了 `-k kt_rulepack_unwired` 和 `-k kotlin_rulepack_samples`,都全過(8 passed 和 25 passed)。`check.py --sg` 回報「規則 207 條,問題 0 個」。

## F1 rules-unwired 併入 review_ids 的新分支沒有測試守
severity: minor
blocking: 否
引句:「review_ids = {r["id"] for r in rules if r["dir"] in ("rules-review", "rules-unwired")}」
佐證:file: `configs/ast-grep/kotlin-android/check.py:799`。`find samples/good -name 'review-fp-*'` 列出的 10 支檔,全屬 rules-review 規則的好例目錄。8 條 rules-unwired 規則在 `samples/good/<id>/` 底下都沒有 `review-fp-` 開頭的檔。
失敗場景:有人把 `("rules-review", "rules-unwired")` 改回只剩 `("rules-review",)`。目前 8 條 unwired 規則的好例沒有已知誤報檔,所以這個條件不會觸發,`t_kotlin_rulepack_samples` 和 `t_kt_rulepack_unwired_dir` 都照綠。日後有人替 unwired 規則加 `review-fp-*` 樣本,就會被誤報成「好例誤報」。這是這次新增行為的唯一一條沒有紅燈釘的分支。程式碼註解宣稱「不接閘規則已知的形狀誤報」可以免報,但沒有任何案例驗它。

## F2 load_rules 的說明字串還寫「三個規則目錄」
severity: minor
blocking: 否
引句:「CONFIGS = (("rules", "sgconfig.yml"), ("rules-review", "sgconfig-review.yml"), ("rules-hints", "sgconfig-hints.yml"),」
佐證:file: `configs/ast-grep/kotlin-android/check.py:66`。`load_rules` 的 docstring 是「讀三個規則目錄」。這次 CONFIGS 擴成四個,同一個 diff 已同步改了「一條規則都沒讀到」的訊息(第 777 行),唯獨漏了這句。
失敗場景:讀 docstring 的人會以為只讀三個目錄,不知道 rules-unwired 也會讀。只是措辭過期,不影響行為。

## 本案特定鏡頭回答
- **拆檔是否原樣**:不是只看 diff。我寫腳本把 base `4785338d1` 的 `rules-hints/*.yml` 七支檔各切成 `---` 文件,逐份比對(去頭尾空白後)。每一份舊規則都完整出現在新的 hints 或 unwired 其中一邊,缺漏為 0。
  - 新檔兩邊都以換行結尾,沒有空文件。
  - `# T14`、`# T35` 的行首註解都跟著各自的規則走,`# T15` 仍留在 hints 且緊接自己的 id。
  - 8 條 id 分別是 `kt-error-by-message-string`、`kt-click-navigate-unguarded`、`kt-compose-preview-no-theme`、`kt-mutex-reentrant`、`kt-asflow-not-cancellable`、`kt-whilesubscribed-no-timeout`、`kt-prod-reads-system-clock`、`kt-robolectric-legacy-looper`。
  - 四個目錄的實際條數:rules 145、hints 42、review 12、unwired 8。
- **sarif_rule_ids 三條路**:
  - ast-grep 回非 0/1:回 None。
  - 輸出不是 JSON(空輸出、非 JSON 文字都算):`json.loads` 丟 `ValueError`,回 None。
  - 逾時:設 `_TIMED_OUT[0]=True` 並回 None,後續掃描都不跑。
  - 其他形狀也不會丟例外:頂層是 list、`runs` 是 dict、`results` 是 int 或缺欄、`ruleId` 缺,都會被 `except (ValueError, AttributeError, TypeError)` 接住,或得到集合裡含 None 的結果。
  - 真實 ast-grep 0.51.1 對兩個探針樣本都回得出目標 `ruleId`(我實跑確認)。
  - 子程序由 `subprocess.run(timeout=)` 在逾時時終止並回收。
  - 唯一沒接的是 `text=True` 解碼時的 `UnicodeDecodeError`。`scan()` 和 `loaded_count()` 本來就這樣,不是這次新增,所以不標。
  - 非 0/1 和逾時兩條路沒有 SARIF 專屬測試。我想不出會出錯的具體輸入,所以不標。
- **假 ast-grep 是否只攔 SARIF**:是。`case "$*" in *"--format sarif"*)` 只比對 `sarif_rule_ids` 的那次呼叫。`scan()` 用 `--json=stream`,`loaded_count()` 用 `--inspect summary`,都不含該字串,會走到 `exec` 真的 ast-grep。兩個案例都要求恰好 2 條問題(兩個探針)且都含「樣本」,我用 SARIF 檢查實跑確認 25 項全過。
  - 「空結果」案例其實是「有結果但 ruleId 是別條」(`kt-other`),不是空 runs。真正空 `runs` 會走 `set()`、報「沒有 … 的結果」,同一個分支,所以沒有行為缺口。
- **新舊互讀**:`check.py` 與規則目錄同在一個 repo、同一版本,舊 `check.py` 不會單獨去讀新目錄。已宣告 `sgconfig-hints.yml` 的消費專案會少 8 條提示級規則。這是計劃的本意:這些規則引用的型錄列出處不全,而且提示級預設不接閘。repo 內沒有安裝腳本或 `scripts/lumos` 引用 `rules-hints`,所以沒有靜默漏拷貝的路徑。
- **衍生資料**:型錄 8 列的「告警帶寫法」格子都已從「批一(只有提示級規則,預設不接)」改成「未接(規則在 rules-unwired/:…)」。改動前後的列對得上(FLOW-14、STATE-9、CO-37、UI-103、ARCH-3、TEST-16、TEST-33,加上 API-36)。`catalog_problems` 與自檢結果 0 個問題。
- **測試抓錯力**:`t_kt_rulepack_unwired_dir` 的判準來自手造假規則,不拿被測函式的輸出當期望值,也有前置斷言(`weak` 至少一列)。逐條想過它註記的翻紅釘:改回只看等級、把 `.get("dir")` 的預設改成 `"rules-unwired"`、把 unwired 的等級限制縮小、搬回 hints,每種都會讓對應案例變紅。唯一例外是 F1。
- **冪等、寫一半、不可逆**:不涉及。這次是靜態檔案搬移,加上唯讀掃描。檢查程式沒有寫入動作,`git mv` 式搬移已確認內容不變。
- **時間**:不涉及。

## pitfalls manifest 判定
「共享狀態有沒有鎖保護」命中 `configs/ast-grep/kotlin-android/rules-unwired/coroutines.yml` 第 11 行,判為誤報。該檔只是一條 ast-grep 規則的 YAML,`kt-mutex-reentrant` 的訊息文字提到 Mutex,不是會跑的 Kotlin 併發程式。manifest 的併發類檢核題在這個 repo 本來就判範圍外。

## 固定席判定
- **Systems/kotlin規則包**:改動與筆記一致,WHY 的 `[test:]` 改掛 `t_kt_rulepack_unwired_dir`,RULE 的 confirmed 日期已更新,文字與程式相符。
- **Systems/測試假綠形態 ★INVARIANT★**:新測試有前置斷言(`weak` 至少一列),證明現場成立,翻紅釘也列在 docstring。F1 是唯一一條沒有紅燈釘的分支,已標 minor。
- **其餘固定席**:只是因改到超大測試總檔被連帶推出。這次只新增一支測試並在一支既有測試加案例,不影響其餘題目。

## 角色鏡頭(後端卡)
- **be-api-compat**:不涉及對外 API。規則包是工具鏈內部設定。唯一的「舊讀者」風險是消費專案少 8 條提示級規則,上文已判為本意、可接受。
- **be-authz**:不涉及。沒有新增端點。

總結:最高等級為 minor,blocking 共 0 條
