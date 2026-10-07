severity: minor

## F1 範圍說明行另寫了一套白名單消毒,跟鄰居的消毒做法不同
severity: minor
blocking: 否
引句:「_SAFE_RANGE_RE = re.compile(r"^[A-Za-z0-9._/~^-]{1,200}\.\.[A-Za-z0-9._/~^-]{1,200}$")」
佐證:鄰居是 ``scripts/hooks/claude/dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:410` ``,對鎖路徑只做「截 300 字加換行換空白」,不做字元白名單。lumos 端的範圍驗證是 ``scripts/lumos: `scripts/lumos:44034` `` 的 `_lens_range_ok`,只擋空白、`...`、開頭 `-`,也沒有字元集。
說明:掛鉤是會被複製到使用者家目錄的獨立腳本,不能呼叫 `_lens_range_ok`,所以這不算跨層直呼,也不是重複實作那個函式。但專案裡「說明行消毒」原本只有截斷加換行這一種,現在多出「白名單不合就整段換成 <範圍>」這第二種。同一個 FAIL_NOTE 裡,`what` 走白名單,`repo` 走截斷,兩個欄位的消毒規格不同。結構上有理由,所以只列 minor。

## F2 路徑消毒比鄰居多去反引號,兩處不同步
severity: minor
blocking: 否
引句:「where = str(repo).replace("`", "").replace("\n", " ").replace("\r", " ")[:300]」
佐證:``scripts/hooks/claude/dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:410` `` 的鎖路徑寫法是 `[:300].replace("\n", " ").replace("\r", " ")`,先截再換,也沒去反引號。
說明:計劃稿寫的是「同鎖路徑的處理」。實際上順序不同(先去再截,對上先截再換),還多了去反引號。LOCK_UNCERTAIN_NOTE 的 `{lock}` 沒有同樣的保護。兩處本質上是同一個消毒需求,卻出現了兩個版本。

## F3 失敗分支的除錯日誌在只附說明行時仍寫「放行」
severity: minor
blocking: 否
引句:「_debug(f"lumos dispatch-lens rc={r.returncode}:{r.stderr.strip()[:200]},{'只附角色卡' if _role else '放行'}")」
佐證:此行是 diff 內既有行,現在 `_note` 非空而 `_role` 為空時,日誌會寫「放行」,但實際已改派工詞。同檔 TIMEOUT_NOTE 那條路徑的日誌描述的是真實動作。
說明:這是日誌與行為不一致,結構上沒問題。

## 三問

1. 分層與依賴方向:對齊。掛鉤只讀 lumos 印的 JSON 欄位 `lens_fail`,不 import lumos,也不重算範圍。lumos 端把失敗原因集中在 `_dispatch_lens_fail`,由 `_dispatch_lens_graph` 的各個回傳點呼叫,沒有跨層直呼。
引句:「_note = _fail_note(r, rng, repo)   # 範圍算不出來才有;說明在前、角色卡在後」
佐證:該位置沿用 ``scripts/hooks/claude/dispatch-lens-hook.py: `scripts/hooks/claude/dispatch-lens-hook.py:456` `` 同一個 `if r.returncode != 0` 區塊,延伸既有的 `_role_text` 路徑。

2. 命名與錯誤處理:大致對齊,有 F2、F3 兩處小不一致。`*_NOTE` 常數、`LUMOS-LENS:` 開頭、`_mark("error", …)` 與整段 `except Exception: pass` 都沿用鄰居。`_mark` 的 import 寫法在檔內已是第四次複製,是既有做法,不是新引入。
引句:「_mark("error", "lumos dispatch-lens 範圍算不出來,附了說明行")」

3. 第二種做法:消毒有 F1 說的第二種寫法。範圍驗證沒有重做一套,掛鉤只做字元集檢查,不判斷範圍結構。`_last_json` 把 `_role_text` 的讀 JSON 邏輯抽出來共用,是收斂,不是新增。lumos 端 `--json` 印 `{"lens_fail": …}` 沿用既有失敗 JSON(帶 `role_text`)的形狀。
引句:「code = _last_json(r).get("lens_fail")」

派工詞尾端的「lumos 自動附加」段:有看到,共列 29 篇。其中 8 篇列了詳情:pitfalls-code-loop、lumos-cli-read、lumos-cli-lifecycle、design-loop、loop-convergence-recording、guard-kill、測試假綠形態、reversibility-governance-ledger。另 21 篇標「超出上限,只列名」。

不對齊共 3 條,其中重大 0 條。
