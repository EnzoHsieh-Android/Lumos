severity: blocker

### F1 pitfalls --diff 的 lint claims 完全沒套用 vendored 跳過,診斷③沒有真的關掉
severity: blocker
blocking: 是 — 只要消費專案宣告 `.lumos/lint.json`,vendored 檔的 lint 命中照樣把 tier 撐成 high、擋推送,新測試沒蓋到這條路徑
引句:「★整份報告 30 條沒有一條在專案自己的程式碼裡★」
1. 佐證:file: `scripts/lumos:17702` `lint_claims = [c for c in lint_claims if c["line"] in added.get(c["file"], set())]` ——這道過濾只看 `added`(未過濾 vendored)的行號成員,從沒呼叫 `_is_vendored_path`/`_skip_vendored`。
2. 最小重現(已實測):consumer repo 宣告 `.lumos/lint.json` 對 `.js` 掛一支輸出固定 SARIF 的假 linter,commit 新增 `scripts/hooks/claude/h1.js`,跑 `lumos pitfalls --diff HEAD~1..HEAD --repo . --json`(不加 `--no-lint`)。
3. 實測結果:`{"claims":[{"file":"scripts/hooks/claude/h1.js","line":1,"source":"lint:fakelint",...}],"tier":"high",...}` ——跟診斷描述的③一模一樣重現;新測試 `t_pitfalls_diff_ignores_vendored_toolchain` 完全沒設定過 `.lumos/lint.json`,沒蓋到這條路徑。

### F2 _stack_changed_ok 同一支函式三個呼叫點只修了兩個,刪除行分支仍漏 vendored 檔
severity: major
blocking: 是 — 與 F1 同病根,只是餵進 changed_lines→表態閘 S2(要求填「效能檢核題」)而非 tier
引句:「if cur_file and _stack_changed_ok(cur_file):」
1. 佐證:file: `scripts/lumos:17629` 同一函式裡另兩個呼叫點已改成 `_stack_changed_ok(cur_file, _skip_vendored)`,只有處理刪除行那個(context 行,原封未動)還是舊呼叫方式。
2. 最小重現(已實測,今天真實 vendored 檔全是 .py/無副檔名不會命中 stack 題表,所以借 `_VENDORED_DIRS` 認可的路徑放一支 `.vue` 示範同一段程式碼邏輯):`scripts/hooks/claude/h1.vue` 先含 `reactive({a:1})`,下一版只刪掉那一行、不新增任何行並 commit,跑 `lumos pitfalls --diff HEAD~1..HEAD --repo . --dispositions-template`。
3. 實測結果:仍印「要答的題 1 題」並吐出 `vue-reactive` 表態樣板;把第三個呼叫點也補上 `_skip_vendored`(僅在 /tmp 內修改驗證,未動 repo)後,同一指令變成「這次改動沒有要答的效能檢核題」。

### F3 about_code 的 set 會靜默吞掉既有多路徑清單
severity: blocker
blocking: 是 — 對已有多筆 about_code 的節點跑一次 set 就永久刪掉其餘路徑,rc=0、印 ✓ 成功
引句:「fm[a:b + 1] = [f"about_code: {v}"]     # 清單形(含範本的空 [])或壞掉的純量,一律換成一行乾淨路徑」
1. 佐證:file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:35` `about_code:` 底下是 3 個真路徑(`.github/workflows/ci.yml`、`scripts/hooks/pre-push`、`scripts/lumos`),不是範本空 `[]`;同型多項清單在 `codex-harness.md`(6 項)、`slim-install-安裝器.md`(3 項)等數十篇既有節點是常態。
2. 最小重現(已實測):對一個 `about_code:\n  - scripts/hooks/pre-push\n  - scripts/lumos` 的節點跑 `lumos set <node> about_code scripts/lumos`,結果 about_code 變成純量 `scripts/lumos`,`scripts/hooks/pre-push` 永久消失。
3. 補:`about_code` 仍在 `LIST_KEYS` 白名單裡,`lumos append <node> about_code <path>` 仍能把純量長回多項清單(已實測成功),append/set 兩指令並存,下一次 set 又會整包吃掉——不是邊緣案例。

### F4 about_code 的存在性檢查可被絕對路徑/`..` 繞過
severity: blocker
blocking: 是 — 「路徑必須在 repo 裡存在」的檢查對絕對路徑與 `..` 完全失效,擋不住它自己要防的手滑
引句:「if not v or not (root / v).exists():」
1. 最小重現(已實測):`lumos set <node> about_code /etc/hosts`;rc=0,`about_code` 被寫成 `/etc/hosts`,即使該路徑與這個 repo 毫無關係。
2. 原因:Python pathlib 的 `root / v` 在 v 是絕對路徑時會整個丟掉 root(`Path('/a')/'/etc/hosts' == Path('/etc/hosts')`),`root / "../../../etc/hosts"` 也照樣用 filesystem 語意跳出 repo——兩者都繞過設計意圖裡「從 root 算起」的檢查,已用 `../../../etc/hosts` 二次實測同樣 rc=0 寫入成功。

### F5 _VENDORED_DIRS 是第二份硬寫清單,「不另記一份」不成立
severity: minor
blocking: 否 — 今天兩份清單值剛好一致,不會馬上翻紅,只是違反自己聲明的單一源設計
引句:「清單直接吃安裝端的 _VENDORED_TOOLKIT 與同一組目錄,★不另記一份★——」
1. 佐證:file: `scripts/lumos:13303` `for sub in ("scripts/hooks", "scripts/templates"):` ——`_vendor_toolchain` 這裡自己硬寫了一份跟 `_VENDORED_DIRS`(定義於 scripts/lumos:13130)一模一樣的元組,不是同一個常數。
2. 以後在這裡加第三個 vendored 目錄卻忘了同步 `_VENDORED_DIRS`,就會重演 F1/F2 同一種病。

風險掃描清單那 1 條:誤報——scripts/lumos:17562 命中的是 docstring 裡「命中 open(...)」這句中文說明文字本身(討論舊病的註解原文),不是真的未關閉檔案 handle;諷刺的是這正是同一段註解裡自己點名過的「自我餵食」誤觸發案例,只是這次踩在工具鏈本體自己合法的程式碼裡。

總結:最高 severity blocker,blocking 共 4 條
