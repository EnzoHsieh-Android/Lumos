severity: major

審查席暫存:本席沒有建立任何暫存檔或實驗目錄,不需要清理。

## 問 1 分層與依賴方向:部分不對齊

新掛鉤放在 `scripts/hooks/claude/`,只依賴 `_hookevent`,方向和鄰居一致。呼叫端也一致,都由 `merge-claude-settings.py` 註冊。差別在判斷放哪裡:

- file: `scripts/hooks/claude/dispatch-lens-hook.py:6-13` 是薄殼。它只做三件事(讀派工詞、叫 `lumos dispatch-lens`、接回傳文字),其餘判斷全在 lumos。
- file: `docs/lumos-toolchain-knowledge/Projects/派工鏡頭注入_計劃.md:104` 記了「hook 是薄殼,邏輯進 lumos」的 r3 裁定。
- file: `scripts/hooks/claude/impact-hook.py:133-160` 是混合型。檔案過濾 `hook_decide` 在 hook 內,重活交給 lumos。
- file: `scripts/hooks/claude/memory-sweep.py` 約 970 行,判斷都在 hook 內。
- file: `docs/lumos-toolchain-knowledge/Projects/Codex行為精修_計劃.md:58` 先例:厚 hook 要寫成「有意識偏離」並附理由。

新掛鉤把整套 heredoc 剝除、shlex 切段、git 全域選項解析、拋棄式路徑判斷全放在 hook 內,屬於厚 hook。鄰居本身不一致,所以厚本身我不硬判(見 F4)。依賴方向上沒有跨層直呼。我 grep 了 `scripts/lumos`,沒有可重用的函式。

## 問 2 命名與錯誤處理:不對齊(F1、F2、F3、F5)

以下幾項一致:

- stdin 用 `json.loads(sys.stdin.read())`,和 `impact-hook.py:771`、`dispatch-lens-hook.py:403` 相同。
- 輸出的 `hookSpecificOutput` 外層形狀相同,見 `impact-hook.py:824-829`。
- 呼叫 `guard` 的外殼也相同,見 `impact-hook.py:919-928`。

不一致的有四項:

- 預算區塊(F1)。
- 事件名(F2)。
- `mark("ok", …)` 的新用法(F3)。
- 預篩放在 `guard` 之外(F5)。

`swallow=True` 的對照:同為 PreToolUse 的鄰居(impact、dispatch-lens)是 `swallow=False`,`swallow=True` 的是 SessionStart 兩支(`ci-status-hook.py:254`、`memory-sweep.py:972`)。這裡的取捨有理由(spec 寫明問人層不是安全邊界),放行方向也比較保守,我不列為 finding。

## 問 3 第二種做法:不對齊(F1、F3、F6)

- shlex 切段:`scripts/lumos` 裡的 `shlex.split` 只有 `:26852`(解析掛鉤註冊命令,不是切 shell 段),其餘都是 `shlex.quote`。沒有現成的 shell 切段或 heredoc 剝除函式,自寫不算第二種做法。
- 註冊方式:HOOK_ENTRIES、HOOK_BUDGET、`_GLOBAL_CLAUDE_HOOKS`、ANCHOR_FILES、`_VENDORED_TREE_FILES`、`enforcement_status` 這幾處,我拿 `memory-sweep.py` 對照,出現的位置就是 spec 列的那幾處,沒有漏列。
- 新的做法有三個:預算區塊缺席(F1)、用存活事件計問人次數(F3)、另一份拋棄式目錄名單加字串前綴判斷(F6)。

## 問 4 落點:對齊

- 既有慣例是「一支掛鉤一個 Systems 節點」,例如 `Systems/改檔前推播.md:9` 管 `impact-hook.py`,`Systems/記憶過期清掃.md:9` 管 `memory-sweep.py`,`Systems/CI回流開場提醒.md:9` 管 `ci-status-hook.py`。新開 `Systems/代理繞閘問人` 管新掛鉤檔,符合這個慣例。
- file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-lifecycle.md:103-110` 的 `about_code` 已列 `scripts/lumos` 與 `scripts/merge-claude-settings.py`。這兩支檔的改動寫進它是對的。
- 沒有專門的 enforcement 節點。這個落點沒有 finding。

## 不對齊條目

**F1. HOOK_BUDGET 登記了 5,但掛鉤忽略 `--budget`,會讓現有守衛測試崩潰**

spec 〈做法〉與〈範圍〉。

引句:「命令列參數(安裝時附的 `--budget 5`)一律忽略、不報錯。」

具體重現:

- file: `scripts/test_lumos.py:17908-17924`(`t_hook_inner_timeout_always_below_outer`)對 HOOK_BUDGET 每個項目,只要檔案存在,就載入該掛鉤並呼叫 `mod._inner_budget(default=...)`。
- 照 spec 實作:HOOK_BUDGET 加 `"bypass-ask-hook.py": 5`,新掛鉤沒有 `_inner_budget`。
- 新檔一出現,這支測試在 `mod._inner_budget` 上丟 AttributeError。
- 應該是:新掛鉤也帶那段逐字複本(`_BUDGET_RATIO` 到 `return max(_BUDGET_FLOOR,…)`)。那段複本有 `len(_sigs)==1` 的漂移守衛。或者 spec 明寫這支不進 HOOK_BUDGET 表,並說明 `t_bypass_ask_registered` 要求的 `timeout 5` 從哪來。

severity: major
blocking: 是 — 照字面實作會讓現有全套測試翻紅,而且 spec 沒有交代怎麼處理。

**F2. 存活事件名和 `enforcement_status` 的列名不一致,新那一列永遠不會是 active**

spec 〈做法〉`guard` 呼叫與 `enforcement_status` 段。

引句:「過了預篩才進 `guard("bypass-ask-hook", __file__, main, swallow=True)`」

引句:「`enforcement_status` 的 Claude 掛鉤列舉加 `("pretooluse-bypass-ask-hook", "bypass-ask-hook.py")`」

具體重現:

- file: `scripts/lumos:27224-27237` 的 `_hook_recent_ok(root, layer, …)` 把列名 `layer` 直接當 hook 名。
- file: `scripts/lumos:23333` 比對 `e.get("hook") != hook_name`,hook 名必須和列名完全相同。
- 鄰居都是事件名和列名同字串:`guard("pretooluse-impact-hook", …)`(`impact-hook.py:928`)、`guard("pretooluse-dispatch-lens-hook", …)`(`dispatch-lens-hook.py:555`)、`guard("sessionstart-memory-sweep", …)`(`memory-sweep.py:972`)。
- 照 spec 實作:事件寫成 `hook: "bypass-ask-hook"`,列名是 `pretooluse-bypass-ask-hook`,兩邊永遠對不上。
- 結果:該列最好只顯示 unknown。spec 〈做法〉把這個狀態說成「近期沒命中過時照既有規則顯示 unknown」,等於把永遠對不上的 bug 說成預期行為。
- `scripts/test_lumos.py:41089` 的驗收測試也斷言 `"bypass-ask-hook"`,會把這個錯綠掉。
- 應該是 `guard("pretooluse-bypass-ask-hook", …)`,測試跟著改。

severity: major
blocking: 是 — 照字面實作會做出一個永遠觀測不到的掛鉤,而且驗收測試會跟著錯。

**F3. 用存活事件記「問了」的次數,違反既有「只記活著沒、不記成效」的界線,也是 `mark` 的新用法**

spec 〈做法〉命中段與〈前言〉PRIOR-ART。

引句:「並用 `mark("ok", "ask:<理由代號>")` 讓存活事件帶上」

引句:「事後量測掃 Claude 事件帳與掛鉤自己的存活事件」

具體重現:

- file: `scripts/hooks/claude/_hookevent.py:26-27`:「★不記「注入 N 次」★:那是成效…本批只做「活著沒」」。
- file: `docs/lumos-toolchain-knowledge/Projects/enforcement可觀測性_計劃.md:18` 與 `:201-206`:明列「不做注入 N 次」,因為那是成效量測。
- file: `scripts/hooks/claude/_hookevent.py:111-125`:`mark` 的語意是「內部吞掉逾時或失敗時自己講一聲」。
- 我 grep 了 `scripts/hooks/claude/` 下所有 `mark`,現有呼叫只有 `error` 與 `timeout`,沒有 `ok`。
- spec 把存活事件拿去計「問了幾次」,供 RETIRE-IF 與 REVISIT 量測。這等於在同一本帳上開了第二種用途(成效計數)。
- spec 也誤引上述計劃:該計劃只決定「記帳不新開端點」,並沒有授權存活事件當成效帳。
- 應該是二選一:
  - 不在存活事件放 `ask:` 備註,量測改走 Claude 事件帳。
  - 或先用 `lumos decision-add` 翻案,再改 `_hookevent` 的界線與 `mark` 的定義。

severity: major
blocking: 是 — 引入第二種記事件的做法,並且推翻既有的明文界線,spec 沒走翻案流程。

**F4. 厚 hook 沒有宣告對「薄殼」裁定的偏離**

spec 〈前言〉PRIOR-ART 與〈做法〉。

引句:「由 `scripts/merge-claude-settings.py` 註冊、讀 stdin 事件、印 JSON;這支照同一種做法」

引句:「用 `shlex`(posix、把 `; & | 換行` 當分隔)切成一段段指令」

具體重現:

- PRIOR-ART 說「照同一種做法」,但最近的同事件鄰居是薄殼(`dispatch-lens-hook.py:6-13`)。
- spec 通篇沒提「薄殼」裁定,也沒寫「有意識偏離」。`Codex行為精修_計劃.md:58` 是先例:有厚 hook,但偏離要明寫。
- ⚠ 交編排者:厚本身不是 finding。`impact-hook.py` 的 `hook_decide` 與 `memory-sweep.py` 證明厚 hook 有先例。「掛鉤不叫主程式」的效能理由在 spec〈實務隱患〉成立。
- 要補的是明寫偏離的理由,並用 `decision-add` 記進決策。

severity: minor
blocking: 否 — 結構可用,缺的是脈絡紀錄,不會讓實作者做錯。

**F5. 預篩放在 `guard` 之外,出現一條不受 fail-open 包覆、也不記事件的執行路徑**

spec 〈做法〉預篩段。

引句:「便宜的預篩(在 `_hookevent.guard` 之外)」

具體重現:

- file: `scripts/hooks/claude/_hookevent.py:127-160`(`guard`)的語意是「每次執行都記一筆」。鄰居的早退(例如 dispatch-lens 的「不帶標記就放行」)全在 `main` 內、`guard` 之下。
- 新掛鉤的預篩在 `main`/`guard` 之前,讀 stdin 和判斷出錯時,spec 的 `swallow=True` 與 `mark("error")` 都沒有包到。
- spec 的 S4 只驗「過預篩之後」丟例外會放行。
- 不確定的點:預篩階段丟例外的實際結果。這取決於 stdin 解碼等實作細節,我沒有實測,所以不下結論。
- 這個取捨(避免灌爆存活事件檔)有理由,所以只列為與鄰居的差異。要補的是預篩階段自己的 try/except 放行。

severity: minor
blocking: 否 — 設計意圖成立,只是缺一道包覆,補一個 try/except 即可。

**F6. 拋棄式目錄判斷用字串前綴,和 lumos-guard 的真實路徑判斷、名單都不一致**

spec 〈做法〉拋棄式目標放行段。

引句:「目標落在 `/tmp/`、`/private/tmp/`、`/var/folders/`、`/private/var/folders/`、`$TMPDIR` 底下」

具體重現:

- file: `mods/claude/lumos-guard/hooks/register.ts:39` 的暫存根是 `/private/tmp`、`/private/var/tmp`、`/tmp`、`/var/tmp`。
- file: `mods/claude/lumos-guard/hooks/register.ts:112-114` 先轉真實路徑,路徑含 `.` 或 `..` 段就當看不懂。
- file: `scripts/lumos:18217` 也用 `os.path.realpath(tempfile.gettempdir())`。
- 輸入:`cd /tmp/../Users/x/repo && git push --no-verify`。
- 照 spec 的字串前綴判斷:落在 `/tmp/` 底下,放行,不問人。
- 應該是:路徑含 `..` 就不當拋棄式,或先 realpath。
- 另一處不一致:`/var/tmp` 在 lumos-guard 算暫存,在 spec 名單裡沒有。因為 `/var/tmp` 和 `/var/folders` 兩邊各漏一半,用到 `/var/tmp` 的指令會被誤問。
- 兩邊語言不同(TS 與 Python)無法共用程式,但名單和 `..` 處理應該對齊。

severity: minor
blocking: 否 — 影響範圍是「寧可漏問」方向的誤放行與少量誤問,不會讓系統壞掉。

不對齊共 6 條,其中 major 3 條(F1、F2、F3)。

最嚴重的是 major,blocking 共 3 條。
