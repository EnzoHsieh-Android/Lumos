# r2 架構對齊審查——派工鏡頭注入

被審材料(凍結審材):`/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/26a6b57a-9efc-4073-b845-c27e42a2fbb1/scratchpad/派工鏡頭注入-r2.md`
第 1→2 輪差異:`governance/review-reports/派工鏡頭注入/r2-delta.diff`
對照鄰居:`scripts/hooks/claude/impact-hook.py`、`lumos-entry-hook.py`、`ci-status-hook.py`、`check-graph-sync.py`、`scripts/merge-claude-settings.py`、`scripts/lumos`(`_GLOBAL_CLAUDE_HOOKS`/`_RETIRED_CLAUDE_HOOKS`/`_RETIRED_STUB_CLAUDE_HOOKS` :11017-11034、`ANCHOR_FILES` :11404、`enforcement_status` 四元組 :12109-12112、`git show <ref>:<path>` 既有用法 :3131/8954)

判定範圍只問「跟既有做法一不一樣」,不判 bug、不評風格。

---

## 前輪 4 條驗收

r1 架構對齊席(`r1-arch-架構對齊.md`)判了 4 條:f1(updatedInput 第二種做法,major)、f2(失敗一律 stderr 發聲,minor)、f3(Markdown 標頭+方括號代號,minor)、f4(檔名⚠,交編排者裁)。逐條核對 r2 是否真改到:

- **f1**:沒有改回 `additionalContext`(追測二已實測子代理收不到,技術上做不到),但 r2 把它折進 `decisions.d2`「有意識偏離」,寫明理由(additionalContext 到不了子代理,updatedInput 是唯一通道)並綁配套(★永不 deny+進 ANCHOR_FILES★)。file: 審材 `28-33行`(d2 全文)、`70行`(「★折成有意識偏離★:...這是有意識偏離,記 d2,不是沒看到」)。✅ 真改到——不是靜默維持原判,是把「未揭露的第二種做法」變成「揭露且有配套的偏離」,這正是 r1 f1 要求的效果。
- **f2**:設計 §8 改成「失敗一律放行、預設靜默……比照鄰居「技術性失敗純靜默」,只有 `LUMOS_HOOK_DEBUG=1` 才在 stderr 印一行」。file: 審材 `88行`。對照鄰居既有的 `LUMOS_ENTRY_HOOK_OFF`/`LUMOS_PROBE` 環境變數開關慣例(file: `scripts/hooks/claude/lumos-entry-hook.py:89`、`scripts/lumos:10194`),同一種「`LUMOS_*` 環境變數當旗標」命名法。✅ 真改到。
- **f3**:設計 §6 改成「純文字條列(比照四支鄰居的注入格式,不用 Markdown 標題+方括號代號),固定第一行 `lumos 自動附加:……`」。file: 審材 `86行`,對照 `scripts/hooks/claude/impact-hook.py:342-343`(「必看——這 {len(pins)} 篇……」同款純文字條列)。✅ 真改到。
- **f4**:設計 §9 給出檔名 `dispatch-lens-hook.py`,沿 `-hook.py` 慣例。file: 審材 `89行`。✅ 真改到,判不準狀態解除。

四條全部真改到,無一條是文字改了但行為/揭露沒變的假修。

## 問一:分層與依賴方向

新段落沒有改變 hook 站的層:仍住 `scripts/hooks/claude/`、由 `PreToolUse`(matcher `Agent`)觸發、只透過 `subprocess` 呼叫 `lumos impact --diff --json` 與 `git show`/`git ls-tree`,沒有 `import scripts/lumos` 之類跨層直呼。快取檔案 I/O(讀寫 `$TMPDIR/lumos-dispatch-lens/<sha>.json`)與 `git show <base>:<path>` 讀取(file: 審材 `83行`)都在 hook 進程內完成,呼叫鏈跟 `impact-hook.py` 一致(file: `scripts/hooks/claude/impact-hook.py:473-484`)。`git show <ref>:<path>` 這個讀法本身也不是新發明——`scripts/lumos:8954` 的 `_body_hash_of_text`/migrate-stamp 路徑早就用同一招(`subprocess.run(["git", "-C", str(root), "show", spec], ...)`)讀舊版正文,`scripts/lumos:3131` 的 drift-replay 也用 `_git("show", f"{sha}:{f}")`。這條沒有不對齊。

★但★ 設計 §1 明寫「`--repo` 用 hook payload 的 `cwd`」(file: 審材 `81行`),這條偏離了「hook 怎麼決定自己在哪個 repo」這件事上四支現役鄰居的**一致**做法。四支鄰居沒有一支只用 payload cwd:`impact-hook.py`(file: `scripts/hooks/claude/impact-hook.py:434-436`,註解逐字「repo root: 優先 $CLAUDE_PROJECT_DIR,fallback payload cwd」)、`check-graph-sync.py`(file: `scripts/hooks/claude/check-graph-sync.py:373`)都是 `CLAUDE_PROJECT_DIR` 優先、payload cwd 只當 fallback;`ci-status-hook.py`(file: `scripts/hooks/claude/ci-status-hook.py:52`)、`lumos-entry-hook.py`(file: `scripts/hooks/claude/lumos-entry-hook.py:97`)雖是 payload cwd 優先,但鏈裡仍**保留** `CLAUDE_PROJECT_DIR` 當第二層 fallback。四支鄰居的解析鏈裡 `CLAUDE_PROJECT_DIR` 出現率是 4/4;本設計是 0/4——不是選了鄰居兩種寫法中的一種,是四支都不用的第三種。而且這正是本機制最吃緊的場景:設計自己在同一句話點出理由是「省略 `--repo` 時只從 hook 行程 cwd 往上找,cwd≠目標專案就查錯 repo」,但 `CLAUDE_PROJECT_DIR` 正是 Claude Code 為了解決「行程 cwd 跟目標專案對不上」而設的環境變數——丟掉它,等於把鄰居本來要防的那個洞留著,只是換一顆(payload cwd)去防,沒有防到 CLAUDE_PROJECT_DIR 覆蓋的情形。見 f5,major。

## 問二:命名與錯誤處理

命名慣例(hook 檔名 `dispatch-lens-hook.py`)與錯誤處理(fail-open 預設靜默、`LUMOS_HOOK_DEBUG=1` 才發聲)兩項已在〈前輪 4 條驗收〉核過,對齊。三個登記點的名稱本身也對得上:`_GLOBAL_CLAUDE_HOOKS`(file: `scripts/lumos:11017`)、`merge-claude-settings.py` 的 `HOOK_ENTRIES`(file: `scripts/merge-claude-settings.py:33`)、`enforcement_status` 內寫死的四元組(file: `scripts/lumos:12109-12112`)——設計 §9 三項各自對到正確的變數名與行號量級(file: 審材 `89行`「`scripts/lumos` 約 12109 行」)。

★命名瑕疵★:回滾段寫「沿既有 hook 退役慣例(`_RETIRED_CLAUDE_HOOKS` STUB→DELETE 兩階段)」(file: 審材 `127行`)。但 repo 裡「STUB→DELETE 兩階段」其實是**兩個不同的元組**分別代表兩個階段——階段一 STUB 對應 `_RETIRED_STUB_CLAUDE_HOOKS`,階段二 DELETE 才是 `_RETIRED_CLAUDE_HOOKS`(file: `scripts/lumos:11017-11034`,註解逐字「撤新的 hook:先加進 STUB;下一版把它從 STUB 移到 DELETE」)。設計把兩階段都算在同一個變數名下,照這句話字面操作會直接改錯常數。見 f6,minor。

## 問三:第二種做法

- **快取位置與鍵**:位置 `$TMPDIR/lumos-dispatch-lens/<sha>.json`(file: 審材 `87行`)跟鄰居 `impact-hook.py` 的 TTL 標記檔 `tempfile.gettempdir()/lumos-impact-<session_id>/<hash>`(file: `scripts/hooks/claude/impact-hook.py:104-107`)同屬「`<tempdir>/lumos-<機制名>-<key>/<hash 檔>`」這一種形狀,只是把 key 從「session+檔案」換成「repo+base sha+head sha」——這是因為本案要跨 session 共用同輪多席的結果(鄰居的 TTL 冷卻窗設計目的不同,是限流不是快取),兩者解決不同問題,不算引入第二種做法。快取寫入用「寫暫存再 rename」原子換(併發段,file: 審材 `125行`)在 `scripts/hooks/claude/` 目錄下是首次出現,但這個原子寫法本身早就是 `scripts/lumos` 的既有慣例(`os.replace(tmp, path)`,file: `scripts/lumos:8663-8668`、`10165`、`14577`),是借用既有模式落到新位置,不是自創。
- **base ref 讀法**:`git show <base>:<節點路徑>` 與既有 `scripts/lumos:8954`(`subprocess.run(["git", "-C", str(root), "show", spec], ...)`,spec 組法完全同款 `f"{commit}:{path}"`)完全一致,沒有第二種做法。
- **白名單自創 vs 既有消毒函式**:检查過 `scripts/lumos` 內類似「過濾攻擊者可控字串」的既有函式——`_validate_repo_ref`(file: `scripts/lumos:12314-12327`)防的是路徑穿越(絕對路徑/`..`),不是字元集白名單;`_KILL_METHOD_OK_RE`(file: `scripts/lumos:6640`)是方法名白名單,用途不同。沒有找到現成的「檔名字元白名單」消毒函式可重用,設計 §4 的 `A-Za-z0-9_./-`+CJK+長度上限是填補真空,不是重造已有的輪子,不算第二種做法。
- **錨點新類別的處理**:`ANCHOR_FILES` 目前 5 項全是兩支測試 runner + 三支 git hook(file: `scripts/lumos:11404-11409`),沒有 `scripts/hooks/claude/` 底下的檔案。設計把 `dispatch-lens-hook.py` 加進去,用的是同一個清單、同一個 `lumos anchor approve` 核可流程(file: `scripts/lumos:12273` `cmd_anchor_approve`),只是清單裡多一個新類別的條目——機制本身沒有分岔,是既有機制的正常擴充,不算第二種做法。

問三本身找不到新的第二種做法(問一的 `--repo` 解析是依賴方向問題,已在問一記分,此處不重複計)。

---

### f5

`--repo` 只用 hook payload 的 `cwd`,略過四支現役鄰居(4/4)解析鏈裡都有的 `CLAUDE_PROJECT_DIR` 環境變數優先/備援。這不是四支鄰居兩種寫法裡選一種,是四支都沒用過的第三種;且正好卡在設計自己點名要防的那個洞(cwd≠目標專案)上,`CLAUDE_PROJECT_DIR` 正是鄰居用來防這個洞的機制,被整條拿掉。

severity: major
blocking: 是
引句:「`--repo` 用 hook payload 的 `cwd`」
file: 審材 `派工鏡頭注入-r2.md:81`
file: `scripts/hooks/claude/impact-hook.py:434-436`
file: `scripts/hooks/claude/check-graph-sync.py:373`
file: `scripts/hooks/claude/ci-status-hook.py:52`
file: `scripts/hooks/claude/lumos-entry-hook.py:97`

### f6

回滾步驟把「STUB→DELETE 兩階段」全記在 `_RETIRED_CLAUDE_HOOKS` 一個變數名下,但這兩階段實際對應兩個不同元組(STUB 階段是 `_RETIRED_STUB_CLAUDE_HOOKS`,DELETE 階段才是 `_RETIRED_CLAUDE_HOOKS`)。照字面操作會在該退役時把名字加錯常數。

severity: minor
blocking: 否
引句:「沿既有 hook 退役慣例(`_RETIRED_CLAUDE_HOOKS` STUB→DELETE 兩階段)」
file: 審材 `派工鏡頭注入-r2.md:127`
file: `scripts/lumos:11017-11034`

---

## 結論

不對齊共 2 條,其中 major 1 條。
