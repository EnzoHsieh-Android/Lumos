severity: major

我有看到「lumos 自動附加」段,列了 8 篇固定席(pitfalls-code-loop、lumos-cli-read、lumos-cli-lifecycle、design-loop、loop-convergence-recording、guard-kill、測試假綠形態、reversibility-governance-ledger),另有 16 篇只列名。

**問 1 分層與依賴方向:對齊。**
- 新碼分兩側。CLI 側是 `scripts/lumos` 的 `_dispatch_lens_fail`,只被 `_dispatch_lens_graph` 呼叫(`scripts/lumos:45547`、`:45570-45590`)。
- 掛鉤側是 `_fail_note`、`_lens_fail_why`、`_last_json`,只被 `main()` 呼叫(`dispatch-lens-hook.py:174-210`、`:462-470`)。
- 掛鉤只經 subprocess 讀 lumos 印的 JSON,沒有 import lumos,沒有跨層直呼。
- 失敗時寫帳用 `_hookevent.mark`,放在 try/except 裡,跟同檔 `:423`、`:436`、`:459` 相同。

**問 2 命名與錯誤處理:大體對齊,有一條不對齊(A2)。**
- 底線開頭的私有函式、中文 docstring、`_debug`、fail-open 的作法都跟同檔舊碼一致。
- rc 沿用原值:not_git、commit_missing、sha_unresolved 回 2,no_mainline 和 base_not_mainline 回 4。只有新增的 empty_range 回 2,沒有改既有的 rc。
- 不一致的是 JSON 失敗格式(A2)。

**問 3 第二種做法:有一條(A1)。**
- 掛鉤側新增了 `_clean_field`,清理欄位的方式跟專案已有的做法不同(A1)。
- `_SAFE_RANGE_RE` 另寫了一份 ref 字元集,跟 `_lens_range_ok`(`scripts/lumos:44034`)的規則不同。但掛鉤是獨立檔,import 不到 lumos,且用途是白名單而不是驗證,所以不列。

**修補核對。**
- 兩處合成 `_clean_field`:合併前有兩套手寫清理,合併後仍不是專案的標準做法,見 A1。
- 除錯訊息改印「附了 N 段」,結構沒問題,不另列。

## A1 說明行路徑欄位的清理,新寫 `_clean_field`,沒用專案既有的 `_plain_label`
severity: major
blocking: 是
引句:「return str(s).replace("`", "").replace("\n", " ").replace("\r", " ")[:300]」
佐證:file: `scripts/hooks/claude/ci-status-hook.py:110-118`
佐證:file: `scripts/hooks/claude/impact-hook.py:510-518`
佐證:file: `scripts/hooks/claude/lumos-entry-hook.py:90-98`
- 同層三支掛鉤都有逐字相同的 `_plain_label`。`impact-hook.py:519` 的註解說這種複製有守衛盯著不准漂。
- `_plain_label` 做了五件事:單行化、去框線字元「─」、濾掉 ASCII 控制字元、strip、截斷加「…」。
- `_plain_label` 的 docstring 還特別寫明「看起來無害的欄位也要過這一關」。
- `_clean_field` 只做三件:去反引號、換行換空白、截 300 字。
- `_clean_field` 沒濾控制字元(例如 `\x1b`、`\x07`),也沒去框線。
- 它是專案裡的另一套清理,而且比標準那套弱。
- `dispatch-lens-hook.py` 本身沒有 `_plain_label`,所以看起來像「這支檔沒有」。但鄰居的做法是把它複製進來,不是另寫一支。

失敗場景:
- 接手的人要改路徑清理規則時,得在兩套裡猜該改哪套。
- 會談專案路徑含 `\x1b` 或「─」時,三支鄰居掛鉤會濾掉,這支會原樣進派工詞。
- 守衛只盯 `_plain_label` 的複本,不會盯 `_clean_field`。
- 重現:`python3 -c "import ast;print(ast.parse(open('scripts/hooks/claude/dispatch-lens-hook.py').read()) and 1)"`,再把 `\x07` 放進 repo 路徑傳給 `_clean_field`,結果原樣保留。

歸因:有證據的原有漏查。
- 命令 `git show a8b38648:scripts/hooks/claude/dispatch-lens-hook.py | grep -n '_plain_label\|\[:300\]'`:只有 `:203` 的 `where = …replace("`"…)` 和 `:410` 的 `lock_path = …[:300]…`,兩處手寫、都沒有 `_plain_label`。
- 命令 `git show f74169f4:… | grep -n '_clean_field\|_plain_label'`:`_clean_field` 在 `:174`、`:208`、`:414`,仍無 `_plain_label`。
- 所以第二套做法在修補前就存在(`where` 那行是這份 diff 自己新增的)。
- 修補只是把它具名並合併,沒有改去對齊 `_plain_label`。

## A2 失敗回報 JSON 的形狀跟同一組 lens 回報列不同
severity: minor
blocking: 否
引句:「print(_json.dumps({"lens_fail": code}))」
佐證:file: `scripts/lumos:45322`
佐證:file: `scripts/lumos:45373`
佐證:file: `scripts/lumos:45401`
- 同一個 `dispatch-lens` 的失敗列(`:45322` 的 `lock_uncertain`、`:45373` 的 `spawn_error`、`:45401` 的 `lock_error`)用布林旗標當鍵,例如 `{"spawn_error": True, "lock_path":…}`,並且帶 `ensure_ascii=False`。
- 新的 `lens_fail` 是「鍵名固定、值是字串代碼」,而且沒帶 `ensure_ascii=False`。
- 專案別處還有 `{"status": "range-unavailable", "reason":…}`(`:46684`),格式本來就不統一。
- 這條屬於鄰居本身不一致,但離最近的一組(同函式族)最遠。
- 結構是對的:掛鉤端有 `isinstance` 和白名單判斷,不是任意字串都收。

失敗場景:接手的人要再加一種失敗時,會猜該用布林旗標(`xxx_error: True`)還是 `lens_fail` 的新代碼。掛鉤端也要分兩套讀法,`returncode in (2, 5)` 那段讀旗標,`_lens_fail_why` 讀代碼。

歸因:有證據的原有漏查。
- 命令 `git show a8b38648:scripts/lumos | grep -n 'lens_fail'` 與 `git show f74169f4:scripts/lumos | grep -n 'lens_fail'` 結果相同(`:45552` 與 5 處呼叫),修補沒有碰 CLI 端。

不對齊共 2 條,其中重大 1 條
總結:路徑清理另寫了一支,專案裡三支鄰居掛鉤本來就共用同一支更嚴格的做法;失敗回報的 JSON 格式也跟同組舊列不一樣,其餘分層與錯誤處理都跟鄰居一致。
