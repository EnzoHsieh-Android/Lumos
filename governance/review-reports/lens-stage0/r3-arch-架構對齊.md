# r3 架構對齊審查——主session鏡頭利用率 code-loop r2 修正

被審:`governance/review-reports/lens-stage0/r3-snapshot.patch`(對應已提交 `310c8f3`「fix(lens-stage0 code-loop r2):
TTL 標記帶擁有權 token 只撤自己的;recount 引號外才認重導向、`<<<` 非 heredoc、shlex 失敗退回不靜默、子殼括號拆開、
腳本路徑就近判(變數追蹤)、python -c 單行;接線測試覆蓋五出口;計劃矛盾句/REVISIT 獨立行/驗證數字修正」)。
唯一工作:判「這份 delta 跟本專案既有做法一不一樣」,不找 bug、不評風格。

## 一、r2 驗收(前輪 minor f1 現狀)

r2 報告(`r2-arch-架構對齊.md`)判過的兩件事,對照這次的 delta:

- **major f1/f2(recount 自寫切詞/自寫 vault 定位)**:r2 已驗收「消除」,這次 delta 沒有再碰
  `_load_hook_helpers()`/`_segment_command`/`_tokens_of`/`find_graph_root` 這條委派線(file:
  `governance/eval/lens-utilization/recount.py:19-30`,原封不動),不是回退。
- **minor f1(5 處 `_ttl_unmark` guard 沒用 try/finally,判「不擋,留給 Enzo 裁」)**:這次 delta 只在既有 5 個
  呼叫點上多帶一個 `ttl_token` 參數(file: `scripts/hooks/claude/impact-hook.py:514,536,542,562,566`),
  guard 本身還是原來那句 `if session_id and not in_cooldown: _ttl_unmark(...)` 散彈形狀,呼叫點數量、位置、
  形式都沒變。r2 判定「本家族目前為止沒有這個 try/finally 慣例可違反,是否收斂留給 Enzo」在這次 delta 裡
  原樣成立——不是新問題,也不是不管前輪意見,是前輪本來就沒要求這輪修。驗收:過,狀態不變,不重複計入本輪。

## 二、三問逐答

### Q1:標記檔內容從「ts」變「ts token」,格式演進有沒有既有慣例?

有,而且是同一種風格。這次改法是:內容從單一數字變成空白分隔兩欄「`<ts> <token>`」,讀取端用位置取值
(`content.split()[0]` 取 ts、`parts[1]` 取 token),舊檔案(只有一個數字)因為 `split()` 天然只回一個元素,
`_ttl_should_inject` docstring 明寫「標記檔內容 = 「<time.time()> <token>」(舊格式只有數字,讀取端相容)。」
(file: `scripts/hooks/claude/impact-hook.py:186`),實際讀取在 `:207`(`last_ts = float(content.split()[0])`);
`_ttl_unmark` 帶 `token=None` 時整段跳過欄位比對、無條件撤(file: `scripts/hooks/claude/impact-hook.py:154-158`)
——這是「新格式讀舊檔不炸,靠欄位數/位置分新舊」的做法。

本專案已有同一形狀的既定慣例:`about_code_stamp` 三段式 `<誰>/<日期>/<正文雜湊12碼>`,第三段不是 12 碼 hex
就視同沒有、按「舊格式」處理(file: `scripts/lumos:8872`「about_code_stamp 三段…第三段非 12 碼 hex 視同沒有
(舊格式)」、`:8884` `about_code_expired`)——同樣是「肉眼文字格式加一段、用位置/格式判斷新舊、明文寫
"舊格式"分支」,不是這次新開的模式。純文字標記檔這個底層選擇(而不是像 `_lens_cache_write` file:
`scripts/lumos:16560` 那樣走 JSON+`tempfile.mkstemp`+`chmod`)本身是 r1 之前就定的(`e5fa932` `marker.write_text
(str(now))`),這次 delta 沒有換底層格式,只是在既有純文字格式上加欄位,跟 about_code_stamp 走的是同一條路。

擁有權 token 本身的生成用 `f"{_os.getpid()}-{_os.urandom(3).hex()}"`(file:
`scripts/hooks/claude/impact-hook.py:170`),跟本專案既有的隨機 token 慣例(`"CANARY-" + secrets.token_hex(4)`,
file: `scripts/lumos:4016,4418`,用於治理帳去重鍵)在**用的模組**上不同(`os.urandom` 直呼 vs `secrets`),但
兩者解決的不是同一個問題——CANARY token 是寫進 append-only 治理帳、要長期唯一的審計鍵;這裡的 token 只活在
單次 hook 呼叫的生命週期內,要分辨「是不是我這個 process 寫的」,帶 `getpid()` 對這個除錯情境有意義,`os.urandom`
在熵源上跟 `secrets`(底層也是 os.urandom)等價。查過本專案 `scripts/hooks/claude/` 這個家族沒有既有的臨時擁有權
token 先例可比,不算違反既定慣例,只是同一件事在不同層各自長出寫法,不列為不對齊。

判定:對齊。file: `scripts/hooks/claude/impact-hook.py:151-176,186,207`(先例:`scripts/lumos:8872,8884`)。

### Q2:`_strip_quoted`/`_safe_tokens`/`_script_marks` 該不該回饋給 `check-graph-sync.py` 共用?兩邊切詞規則會不會分岐?

不用回饋,而且這個分工形狀本身有先例。

先看這三支各自在解什麼問題:`_strip_quoted`(file: `governance/eval/lens-utilization/recount.py:37-39`)是為了讓
`REDIRECT_RE` 這個**對著原始字串跑的正則**不要把引號裡的 `>` 誤判成真重導向(注解「commit message 提到路徑旁有 >
被誤判」);`_safe_tokens`(file: `:42-49`)是把 `$(`/反引號先拆開再丟給 `_tokens_of`(避免子殼括號黏進 token);
`_script_marks`(file: `:52-74`)是判斷 heredoc/`python -c` 腳本內某個筆記路徑「被讀還是被寫」。這三件事全部只跟
`classify_bash()`(file: `:132-177`)這個 recount 專屬的「Bash 命令有沒有碰到某篇筆記,讀還是寫」的判斷有關。

`check-graph-sync.py` 自己的 Bash 掃描(`touched_graph_via_cli`、`extract_bash_file_paths`,file:
`scripts/hooks/claude/check-graph-sync.py:190,218`)只認「某個 segment 的**第一個 token**是不是
`obsidian <mutate 子命令>` 或 `rm/mv/cp/git rm/git mv`」,靠 shlex 逐段切詞後比對位置——這個做法天然不會被
「commit message 裡引號內剛好有 `>` 或提到 `rm`」誤導(shlex 會把整段引號文字收成一個 token,不會被拆成看起來
像獨立 verb 的字),也完全不涉及 heredoc 內容的讀寫語意。也就是說 recount.py 要修的這三個坑,是它自己新增的
**正則直讀原始字串**(REDIRECT_RE/HEREDOC_RE)這條路徑才會踩到的,check-graph-sync.py 沒有走這條路徑,沒有同類
的坑可回饋修。

分工形狀對照 `governance/eval/k1_stop_replay.py`:同樣是 `governance/eval/` 下的唯讀重算腳本,用
`SourceFileLoader` 從 `scripts/lumos` 借一個單一實作(`_est = _lm._estimate_remaining_defects`,file:
`governance/eval/k1_stop_replay.py:10-16`),再疊自己專屬的 `rounds_of`/`clean_round` 邏輯,疊上去的邏輯沒有
被要求回推進 `scripts/lumos`。recount.py 這次的結構完全一樣:借來的 `_segment_command`/`_tokens_of`/
`find_graph_root` 三支還是唯一實作、沒被複寫(這是 r1 f1/f2 major 判準要守的線),疊上去的三支新 helper 是
recount 專屬的業務邏輯,不是同一件事的第二份實作。

會不會「分岐」:兩邊共用的切詞原語(`_segment_command`/`_tokens_of`)沒有變、也沒有被複寫第二份,所以不會出現
「同一段命令兩邊切出不同結果」這種真分岐;`_safe_tokens` 對 `_tokens_of` 回傳結果做的後處理(去掉黏住的
`()$`)只影響 recount 自己往下用的 token 列表,不回寫、不影響 check-graph-sync 那邊的呼叫。

⚠ 判不到 100% 乾淨的一點:`_safe_tokens` 的 docstring 寫「shlex 對不成對引號會拋 ValueError→退回正規式切詞」,
但它包的 `_tokens_of` 其實是 check-graph-sync.py 那支——那支自己已經把 `shlex.split` 包了 `try/except ValueError:
return []`(file: `scripts/hooks/claude/check-graph-sync.py:183-187`),不會真的往外拋。這屬於「對借來的函式
之錯誤處理契約假設錯了」,不是架構層級的分工問題(不影響本題判準:要不要回饋、會不會分岐),按派工詞範圍
不在本輪找 bug,不列 f 項,留意即可。

判定:對齊。file: `governance/eval/lens-utilization/recount.py:37-74`(先例:`governance/eval/k1_stop_replay.py:10-16`;
對照無同類坑:`scripts/hooks/claude/check-graph-sync.py:190-247`)。

### Q3:REDIRECT_RE/HEREDOC_RE 正則命名慣例對不對齊?

對齊,而且這兩個名字不是這次新造的。`REDIRECT_RE`/`HEREDOC_RE` 在上一輪就已經存在(這次只改了正則本身,
沒有改名),這次唯一新增的常數名 `QUOTED_RE`(file: `governance/eval/lens-utilization/recount.py:33`)延續
同一批既有名字(`HDR_OLD`/`HDR_NEW`/`PIN_LINE`/`TOKEN_RE`,file: `:75-80`)的命名法:`<語意>_RE` 全大寫加底線。

這個 `<NAME>_RE = re.compile(...)` 是本專案跨檔案都在用的慣例,不只 recount.py 自己這批——`scripts/lumos` 裡
幾十個模組級常數都是這個格式(`INVARIANT_RE`/`CHECKPOINT_RE`/`TEST_REF_RE`/`ROLLBACK_REF_RE`/`_LENS_SHA_RE`
等,file: `scripts/lumos:2405,2776,2426,2778,16495`),hooks 那邊也一樣:`dispatch-lens-hook.py:19` 的
`MARKER_RE`、`verification-rot-check.py:36` 的 `GIT_COMMIT_RE`。`SCRIPT_HINTS`(file: `:34`,一個 tuple 常數)
也對得上同層的 `READ_VERBS`/`LUMOS_CMDS`(file: `:78-79`)這種全大寫 tuple/set 命名,沒有另立一套。

判定:對齊,無不對齊項。

---

不對齊共 0 條,其中 major 0 條。

severity: clean
blocking: 否
