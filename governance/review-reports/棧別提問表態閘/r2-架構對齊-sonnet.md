severity: major
# r2 架構對齊席(sonnet)——棧別提問表態閘(修訂稿驗收)

### A1 hook「跑 when」主詞不清(minor)
severity: minor
blocking: 否——既有分工是 hook 不持有邏輯只格式化;spec 句子主詞像是 hook 自己跑 regex。
引句:「改檔前 hook：對「目前檔案內容」跑同一組 `when`，只注入命中的題；沒命中任何題就不注入棧段。」
對照 file: `scripts/hooks/claude/impact-hook.py:607-608`("單源在 scripts/lumos 的 _STACK_PERF_QUESTIONS,本 hook 只格式化不持有內容")。⚠ 請改成「lumos impact 對目前檔案內容跑 when 並把結果放進 JSON,hook 只讀結果格式化」。

### A2 ⚠ `stack_questions`「仍是 list of str」與現況形狀不符(major 若按字面)
severity: major
blocking: 是——現況是 `dict[棧, list[str]]`,三個消費者用 `.items()` 讀;字面拍平成陣列會弄壞三處。
引句:「`pitfalls --diff --json` 的 `stack_questions` 改為只列適用題（向後相容：仍是 list of str）」
file: `scripts/lumos:16752`、`scripts/lumos:19021`(`{_sk: [...]}`)、`scripts/test_lumos.py:19074-19080`(`sq["kt"]`)、`scripts/hooks/claude/impact-hook.py:645`(`.items()`)、`scripts/hooks/pre-push:223`(grep 斷言值是物件)。⚠ 請寫清楚外層仍是 `{棧: [題…]}`。

### A3 表態檔傳入形狀兩套說法(minor)
severity: minor
blocking: 否——一處說旗標吃路徑同 `--from-json`,一處寫成裸位置參數 `dispositions <檔.json>`。
引句:「一份 JSON 檔案（旗標吃路徑，同 `--from-json` 慣例；r1 接手席 H9）」
引句:「新寫側原語 `lumos code-loop dispositions <檔.json>`」
file: `scripts/lumos:22337`(`--from-json` 旗標先例)/`scripts/lumos:22161`(裸位置參數先例)。

### A4 ⚠ 新 config 區塊讀法未定(major 若走錯)
severity: major
blocking: 是——`code-loop` 自稱 vault-free;若套 `_lumos_config_near_vault(env)` 就把推送前閘接上要載 vault 的路徑;`ci`/`test`/`platforms` 全走 `Path(repo_root)/.lumos/config.json` 直讀。
引句:「`.lumos/config.json` 的 `stack_questions.gate` 可設 `all`（預設）／`high-only`／`off`」
file: `scripts/lumos:22315`(code-loop help "vault-free")、`scripts/lumos:17524-17536`(`_ci_config` 直讀)、`scripts/lumos:3313-3325`(`load_test_profile` 直讀)、`scripts/lumos:3886`(`_lumos_config_near_vault` 吃 env)。

### A5 `when` 比對要不要剝字串字面沒講(minor)
severity: minor
blocking: 否——`_PITFALL_DIFF_PATTERNS` 非 SQL 軸先 `_strip_string_literals`;`pitfall_when: content:` 不剝也不分大小寫;spec 選了不分大小寫但沒講剝不剝。
引句:「`when` 對「該棧檔案的 added 行」（測試檔排除，同既有規則）做不分大小寫比對」
file: `scripts/lumos:15157`(`_strip_string_literals`)、`scripts/lumos:16725`(`code_nostr`)、`scripts/lumos:18651-18654`(content 分支無 flag)。

### A6 `test:<平台>:<名>` 切分沒點名重用 `resolve_test_refs`(minor)
severity: minor
blocking: 否——既有 `resolve_test_refs` 已實作「含冒號=平台前綴、裸名歸 default」;spec 只點名 `_platform_test_index`,實作可能另刻一份切分。
引句:「`test:<名>`／`test:<平台>:<名>`：用 `_platform_test_index`（多平台感知；r1 F4／C2／H6／B4）取該平台的方法集，裸名走 default_platform」
file: `scripts/lumos:3439-3451`(`resolve_test_refs`)、`scripts/lumos:8162-8186`(`_platform_test_index`)。

## 乾淨借用(無 finding)
path:line 走 `git cat-file -e`/`git show` 同既有 git 原語;原子寫入同 `_write_lf` 與多處 tmp→`os.replace`;`Issues/<名>` 純文字讀 status 無既有等價物,屬填補真空。

不對齊共 6 條,其中 major 2 條(皆 ⚠ 交編排者)。
