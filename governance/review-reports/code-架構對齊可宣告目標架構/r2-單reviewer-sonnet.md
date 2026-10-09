severity: major

我獨立核對了修補差異。兩個版本是修前 `fd2bd3ec` 與修後 `9439d9e0`,各自 clone 在 `/tmp/lumos-seat-work/code-架構對齊可宣告目標架構/r2-單reviewer-sonnet/{before,after}`,實驗腳本在同目錄的 `exp/`。結論是 r1 提出的幾個修復大多成立,但「控制字元」那條沒封完,另外有一條同族的守衛洞沒掃到。

## Findings

### COR2-1 控制字元過濾漏掉 U+2028、U+2029、U+0085,含這些字元的檔名會讓掛鉤整段丟掉派工鏡頭
引句:「_ARCH_TARGET_CTRL_RE = re.compile(r"[\x00-\x1f\x7f]")」
- 這條規則只擋 `\x00-\x1f\x7f`。`lumos dispatch-lens --json` 用 `ensure_ascii=False` 輸出,U+2028、U+2029、U+0085 會原樣出現在 JSON 裡。
- 掛鉤用 `json.loads(r.stdout.strip().splitlines()[-1])` 解析(`scripts/hooks/claude/dispatch-lens-hook.py` 的 `_last_json` 與主路徑)。Python 的 `splitlines()` 會在這三個字元斷行,JSON 因此解析失敗,掛鉤走「回傳讀不懂,放行」,圖譜段、角色卡、目標段全部不注入,只寫 debug,沒有任何可見說明。
- 掛鉤自己的 `_clean_field` 已經明文處理這三個字元,註解寫「換行類字元要擋」。新的過濾沒用這個先例。
- 同一洞也讓宣告的 `node` 含這些字元時通過驗證。
- r1 的測試 `t_arch_target_control_chars_never_reach_prompt` 只用 `\n` 做檔名,沒覆蓋這一類。
- 最小重現(`exp/e3.py`):main 上宣告 `app/Domain/**`,分支新增 `app/Domain/Pay\u2028x.py`,掛鉤派工詞帶 `LUMOS-ARCH-TARGET: on`。
  - 修前、修後都是注入為空。
  - 同檔放在宣告目錄外,或不帶 ARCH 旗標,都正常注入。
  - 直接看 CLI:`dispatch-lens main..HEAD --json --arch-target` 的最後一行,用 `splitlines()[-1]` 解析,兩版都 `JSONDecodeError`。
- 歸因:有證據的原有漏查。修前修後結果相同,修補宣稱封住控制字元但沒封全。
- 建議:過濾加上 `\x80-\x9f\u2028\u2029`,或掛鉤改用 `split("\n")` 解析。
severity: major
blocking: 是

### COR2-2 推送前分級仍信任不在主線上的起點,分支自己寫的宣告能把新檔從鄰居基準移走
引句:「_at_rules, _at_warn = _arch_targets_at(repo_root, _at_base) if _at_base else ([], [])」
- r1 的 COR-1 只修了派工鏡頭,`_pitfall_diff_collect` 沒有主線檢查。
- 修補輪用增量範圍時,起點是分支自己的提交。分支在上一輪提交宣告 `app/Domain/** → Systems/Lax`,這輪的新檔就被歸到 `targets`,從 `files`(鄰居對照)消失。
- 同一範圍的派工鏡頭現在回空字串(主線沒宣告就什麼都不附)。結果是這支檔既沒有鄰居基準也沒有目標基準,而且沒有任何說明。
- 重現(`exp/e5.py`):main 無宣告,分支提交 r1 加宣告和 Lax 節點,r2 加 `app/Domain/Order/NewThing.py`。

| 命令 | 修前 | 修後 |
|---|---|---|
| `pitfalls --diff r1..r2 --json` | `targets={'Systems/Lax':[NewThing.py]}`,`files={}` | 同左 |
| `pitfalls --diff main..r2 --json` | `targets=None`,`files` 有 3 個鄰居 | 同左 |
| `dispatch-lens r1..r2 --arch-target` | 附 Lax 的寬鬆規則 | 空字串 |

- 手冊「宣告只讀改動起點那一版」在單次推送範圍(起點是主線的 merge-base)下成立,增量範圍下不成立。
- 歸因:有證據的原有漏查,同族 COR-1 沒掃完。
- 這條不是 blocker 的理由:規則原文不會經過這條路進派工詞,要有人用分支起點的增量範圍跑 pitfalls 才踩到。
severity: major
blocking: 否

### COR2-3 numstat 解析用 `split("\t")`,含 tab 的檔名被截成不存在的名字
引句:「cols = parts[i].split("\t")」
- `-z` 模式下檔名裡的 tab 不跳脫。`app/Domain/Pay.py<TAB>zz` 被截成 `app/Domain/Pay.py`,這個名字不存在,卻列進目標段;真實檔案沒被列到。
- `app/Domain/Pay.txt<TAB>.py` 被截成 `.txt`,整支掉出目標段。
- 這違反修補自己宣告的「命中檔有控制字元不收」。
- 重現是 `exp/e1.py`,修前修後相同。
- 歸因:有證據的原有漏查(舊解析器同樣 `split("\t")`),只是修補把 pitfalls 也併進同一支函式。
- 修法:改成 `split("\t", 2)`。
severity: minor
blocking: 否

### COR2-4 含控制字元的命中檔被靜默踢出目標段,沒有任何說明
引句:「if not rules or _ARCH_TARGET_CTRL_RE.search(f) or not _arch_code_file(f):」
- 檔名含換行、CR、`\x01` 的檔(例如 `app/Domain/Pay\n...py`)落在宣告目錄內,目標段不列它,也沒有「有 N 支檔因檔名不合法未列入」的提示。
- 修前它被列入但有注入問題。修後注入問題解決,但分支可以用奇怪檔名讓自己的檔脫離目標基準。
- 反而更乾淨的做法是留在目標組裡,靠 `cl()` 把控制字元換成 `?`。`cl()` 本來就存在,這道上游過濾是多餘的收窄。
- 重現是 `exp/e1.py`:修前目標段 6 支檔,修後 4 支(換行與 CR 兩支消失),段內沒有任何說明。
- 歸因:有證據的修復回歸,修補新行為引入的取捨。
- 為什麼只算 minor:該 diff 仍在其他席面前,需要刻意取怪檔名。
severity: minor
blocking: 否

### COR2-5 修補新增的兩個分支沒有測試翻紅
引句:「翻紅釘:失敗回空字串 → 兩條都翻紅。」
- 我在隔離 clone `mut/` 做了變異,實驗用的修改檔不入 repo,跑完還原。
- 設計審目標段的例外分支 `_dispatch_lens_spec_arch_text`,把 `return _arch_target_fail_text(e)` 改成 `return ''`,`-k arch_target` 仍是 62 passed、0 failed。這個分支沒有任何測試。
- `_arch_targets_at` 裡 `cat-file` 回 None 的分支(`if there is None`)改掉也全綠。
- 其他變異都有紅:
  - 拿掉主線檢查:2 條斷言紅。
  - 拿掉 rule_index 的控制字元檢查:2 條紅。
  - 讀不懂一律警告:1 條紅。
  - 分級改回 `added`:1 條紅。
  - 作廢判斷不轉小寫:紅。
  - `raw is None` 靜默:紅。
  - 程式碼目標段例外附空字串:紅。
- 這條可以和 COR2-1 一起修。
severity: minor
blocking: 否

## 三問

### ① 原問題的修復效果,有什麼行為證據
- COR-1 派工鏡頭起點:`exp/e5.py` 的增量範圍,修前附出分支寫的 Lax 規則,修後空字串。
  - `exp/e8.py` 經掛鉤端到端:起點不在主線、主線有宣告時,失敗路徑附上固定說明,角色卡照附。
  - 測試 `lens_trusts_mainline_base_only` 在拿掉主線檢查時紅。
- COR-4 檔名含空白:分級修前列出 `with space.py<TAB>`,修後乾淨,與派工鏡頭同一批。拿掉共用函式時紅。
- COR-8 設定壞掉:`exp/e7.py` 逐例比對。
  - 修前:空檔、頂層是清單、非 UTF-8 但沒提到 `arch_targets`,都警告。
  - 修後:這三種都不警告;提到 `arch_targets` 的壞檔仍警告,BOM 檔正常讀。
- COR-7 git 失敗附說明:`raw is None` 與例外兩條測試都紅過。
- COR-2 控制字元:只覆蓋 `\n`、`\x01`,漏 U+2028 一類(見 COR2-1)。
- 修前缺證據的部分:沒有。

### ② 修補處的相鄰路徑
- 正常:
  - `-k arch_target` 62 passed;`-k review_role` 81 passed;`-k dispatch_lens` 117 passed;`anchor-baseline` 的兩個 sha256 與檔案相符。
  - `review_roles` 改用 `_config_glob_error`,邏輯與舊檢查逐字等價。
  - `_json_at_ref` 的 `strict=False` 路徑與修前相同。
  - 圖譜段改用 `_lens_base_on_mainline`,錯誤分支(`no_mainline`、`base_not_mainline`、`empty_range`)與舊寫法等價。
  - 設計審鏡頭包一層後,`--spec` 搭配有無 `--arch-target`、有無 `--json`、檔案不存在、`/etc/hosts`、子目錄 cwd、不給 `--repo`,共 9 種輸出與修前 stdout 逐字相同、rc 相同。
  - 效能:15000 檔、41 條宣告的範圍,目標段 2.3 秒(修前 2.4 秒),`_arch_target_changed_files` 約 1.7 秒。
- 不成立或有疑慮:見 COR2-1 到 COR2-5。
- 順帶看到:`..` 段的檢查被拿掉,`Systems/../Systems/DDD目標` 現在算合法節點。`git show` 不解析 `..`,結果只是「讀不到規則」並由 doctor 提醒,不構成失敗場景。

### ③ 新發現的同一案例在修前、修後
- COR2-1:修前、修後都是掛鉤注入為空。
- COR2-2:修前、修後 pitfalls 輸出相同,只有派工鏡頭那一半不同。
- COR2-3:修前、修後都列出不存在的 `app/Domain/Pay.py`。
- COR2-4:修前列入(帶注入),修後不列入。
- COR2-5:是測試覆蓋問題,不分兩版。

## 圖譜鏡頭(固定席)
- `pitfalls-code-loop`:`arch_alignment` 的算法改了,但我查過沒有流入 tier 或 claims,不影響分級。
- `lumos-cli-read` INVARIANT(search 預設排除 superseded):沒動 search 路徑。
- `guard-kill` INVARIANT:沒動。
- `lumos-cli-lifecycle` INVARIANT(re-inject):掛鉤只改函式名,與 re-inject 無關。
- `design-loop` INVARIANT(處置閘):設計審鏡頭輸出與修前逐字相同,處置閘未動。
- `測試假綠形態` INVARIANT(前置斷言):新測試多數有前置斷言。`config_reader_cases` 的 ① 只比 `broken == plain`,沒確認 `plain` 非空,屬弱斷言,但我的變異讓它紅了,所以不算空殼。
- `loop-convergence-recording`、`reversibility-governance-ledger`:程式碼未動帳本邏輯。
- 備援段:沒逐條答。

## 角色鏡頭(後端卡)
- `be-api-compat`:
  - `arch_targets` 宣告格式放寬了 `..`,收緊了控制字元。這個功能在同一分支才新增,沒有舊消費者。
  - `dispatch-lens` 的 JSON 欄位 `text`、`role_text`、`arch_text` 沒變。
  - 新舊掛鉤互讀沒受影響。
  - `--spec --arch-target` 輸出相容(見②)。
- `be-authz`:沒有端點。對應的「誰有權決定審查基準」就是 COR2-2 與 COR-1:派工鏡頭已限制為主線起點,pitfalls 沒有。角色卡讀分支的 `review_roles`,已有 Issue 記錄(`Issues/角色鏡頭在起點不在主線時讀分支宣告.md`),不算本輪新發現。

## 未驗範圍
- 沒跑全套 3700+ 測試,只跑了上面三個子集。
- 我用的 `/Users/enzo/.claude/skills/lumos-project-notes/commands/03-寫回圖譜.md` 沒找到〈實作測試品質〉那一節,測試品質是依 `測試假綠形態` 的前置斷言原則自行判斷。
- UTF-16 編碼的 `config.json` 若宣告了 `arch_targets`,修後因為位元組搜尋不到字串而不警告(修前會警告)。這個場景冷僻,沒列 finding。
- 設計審讀 HEAD 版宣告與規則,是設計決定,有記載,未重審。
- 本機 `mut` 內的變異都已還原。

總結最嚴重 severity: major
