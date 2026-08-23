# 架構對齊審查 r1

審查對象:`/tmp/code-about-code-read-r1.patch`(git diff -U10,1189 行;四支檔:`scripts/lumos`、`scripts/test_lumos.py`、`scripts/hooks/claude/impact-hook.py`、`governance/eval/retrieval_eval.py`)

審查範圍聲明:只判「跟既有做法一不一致」,不找 bug、不評風格好壞。

---

## Q1:分層與依賴方向

**整體對齊。** 新函式的擺放位置與呼叫方向都落在鄰居已經畫好的家族線內:

- `note_body_hash` / `_stamp_parts` / `about_code_expired` / `cmd_about_code_restamp` / `cmd_about_code_migrate_stamp` 全部緊接在既有 `about_code_to_rater`(`scripts/lumos:7677`)之後、`cmd_about_code_revert`(`scripts/lumos:7819`)之前(`scripts/lumos:7700-7817`),跟 about_code 家族本來就聚在一起的排法一致。
- `cmd_about_code_restamp`/`cmd_about_code_migrate_stamp` 直呼 `cmd_set(env, rel, "about_code_stamp", ...)`(`scripts/lumos:7764`、`scripts/lumos:7810`),跟既有 `cmd_self_audit` 直呼 `cmd_set(env, rel, "self_audit", ...)` 的先例(`scripts/lumos:7593`)同一種寫法——cmd_* 之間互相呼叫本來就是常態,不是新東西。
- `_impact_about_counts` / `_impact_mark_about` 插在 `_impact_collect`(`scripts/lumos:13980`)之後、`_impact_knob`(`scripts/lumos:14097`)之前(`scripts/lumos:14056-14096`),跟 `_impact_*` 頂層 helper 家族的排列順序一致;只被 `cmd_impact` 呼叫一次(`scripts/lumos:14441`),沒有被 doctor 或 hook 檔跨層直呼。
- `about_code_expired` 被兩處呼叫:doctor Check S2(`scripts/lumos:888`)與 `_impact_mark_about`(`scripts/lumos:14091`)。這跟 `status_of`、`link_target`、`split_frontmatter` 這類共用工具函式被 cmd_*/Check_*/_impact_* 各家族共同呼叫的既有形狀相同——這支檔案本來就沒有嚴格分層,只有「共用工具函式 vs 各家族專屬函式」的區分,新程式碼落在對的一邊。

**一處值得記一筆但不算不對齊的觀察(⚠):** doctor Check S2(`scripts/lumos:878`)呼叫了 `_impact_knob("LUMOS_IMPACT_ABOUT", 1)`——這是 `run_doctor` 一千兩百行函式體內唯一一處伸手進 `_impact_*` 命名家族的呼叫,這支 diff 之前沒有先例。但程式碼自己的註解交代了理由(「受總開關 LUMOS_IMPACT_ABOUT(0=整段略過,s1f6:只關一半等於沒關)」)——這個環境變數本來就要同時控制 impact 標記與 doctor 過期檢查兩條路徑,是刻意共用同一顆總開關,不是誤伸手。判不準,標 ⚠ 交編排者,但我傾向不算不對齊。

---

## Q2:命名與錯誤處理

**大致對齊,兩處 minor 不對齊。**

對齊的部分:「擋下:」開頭 + rc=2 + stderr 這條主線在新程式碼裡絕大多數地方都守住了(`cmd_about_code_restamp` 前三個防呆分支、`cmd_about_code_migrate_stamp` 找不到 repo 根那支);✓/⚠ 開頭與 stdout/stderr 分流跟 `cmd_set`/`cmd_append`/`cmd_remove`(`scripts/lumos:7549-7674`)一致;doctor Check S2 完整重用 Check S 定義的 `_soft_list` 閉包與 `gov_events` 字典形狀(`{"gate": ..., "kind": "warned", "hard": False, "nodes": [...]}`),跟 Check S(`scripts/lumos:839`)、Check E1(`scripts/lumos:921`)逐欄一致;`report_goldset` 的 gate 判定仍保留 ✅/❌/PASS/FAIL 這套既有詞彙,沒有換新符號。

不對齊:

1. **rc 語意跟鄰居不一致(minor)**——`cmd_about_code_restamp` 裡連續四個防呆分支,前三個都是「擋下:」+ rc=2(跟 `cmd_set` `scripts/lumos:7551-7553`、`cmd_append` `scripts/lumos:7598-7599`、`cmd_remove` `scripts/lumos:7627-7629` 一致的「擋下=使用者輸入有誤/找不到目標→rc2」慣例),但第四個「讀不到正文」也是「擋下:」開頭,卻回 rc=1。
   引句:「print(f"擋下:{rel} 讀不到正文", file=sys.stderr)
        return 1」
   對照:`scripts/lumos:7551-7553`(`cmd_set` 同款「擋下:」訊息一律配 rc=2)

2. **測試 helper 參數命名跟鄰居不一致(minor)**——這支 diff 自己新增的 `lum(*a, env=None, stdin=None)` 用 `env` 當環境變數覆寫參數名,但檔案裡另一個同名函式 `lum(*a, env_extra=None)`(`scripts/test_lumos.py:12878`)與 `run_hook(cwd, env_extra=None)`(`scripts/test_lumos.py:4610`)都用 `env_extra` 這個慣例命名。
   引句:「def lum(*a, env=None, stdin=None):」
   對照:`scripts/test_lumos.py:12878`(既有同名函式 `lum` 用 `env_extra=None`)

---

## Q3:第二種做法

**兩處 major。**

1. **測試裡引入了全檔唯一一次的「探測 fixture 簽章再決定怎麼呼叫」寫法(major)**——`t_doctor_about_code_expiry` 要跑一次帶自訂環境變數的 `doctor`,正確做法(這支 diff 自己在 `t_impact_about_hit` 就示範過)是寫個小的本地 wrapper 直接組 `subprocess.run(..., env={**os.environ, ...})`。但這裡改用讀 `run.__code__.co_varnames` 去反查共用 fixture `run(vault, *args, expect_rc=None)`(`scripts/test_lumos.py:58`,本來就沒有 `env_extra` 這個參數)有沒有支援 `env_extra`——條件恆假,三元運算式的真分支永遠不會被執行,直接落到 `if r0 is None` 手動組 subprocess 那條路。全檔 22k 行測試碼裡,`__code__.co_varnames` 這個技巧只出現這一次,沒有第二個先例。
   引句:「if "env_extra" in run.__code__.co_varnames else None」
   對照:`scripts/test_lumos.py:696`(同一支 diff 自己寫的 `lum(*a, env=None, stdin=None)` 本地 wrapper,才是這個檔案處理「CLI 要帶自訂 env」的既有正確做法)

2. **`cmd_about_code_migrate_stamp` 內自行重算正文雜湊,沒有呼叫既有的雜湊工具(major,⚠ 判不準)**——`note_body_hash`(`scripts/lumos:7700-7709`)已經是「讀正文→sha256 前 12 碼」這件事的唯一實作,但 `cmd_about_code_migrate_stamp` 因為文字來源是 `git show` 而不是磁碟檔案,沒有重用它,而是在逐篇迴圈裡自己重打一次一模一樣的雜湊公式(而且 `import hashlib` 放在迴圈裡,每篇都重 import 一次)。嚴格說這是同一段邏輯的第二份實作,不是新的子系統,判不準是否夠格算「自創工具函式」,標 ⚠ 交編排者。
   引句:「h = hashlib.sha256(body.rstrip().encode("utf-8")).hexdigest()[:12]」
   對照:`scripts/lumos:7700-7709`(`note_body_hash` 同一條 sha256 公式的既有實作)

其餘檢查過、判定對齊、不算不對齊的地方(附證據供編排者複核):

- `_ABOUT_COUNTS_CACHE`(`scripts/lumos:14053`)刻意沿用 `_BASENAME_COUNTS_CACHE`/`_GIT_DATES_CACHE`(`scripts/lumos:13715`、`scripts/lumos:13757`)的「路徑字串當 key」慣例,連程式碼自己的註解都寫明「id(env) 是全庫沒先例的第二種做法」——刻意避開了第二種做法,不是新增的。
- `about-code restamp`/`migrate-stamp` 兩個子命令用 `acsub.add_parser(...)` 註冊,跟既有 `revert` 完全同款;`main()` 裡的 dispatch 也維持既有的「一串 `if`(不用 `elif`)各自 `return`」寫法,跟 `canary`/`about-code` 既有 dispatch 一致。
- `int(_impact_knob("LUMOS_IMPACT_ABOUT", 1))`、`int(_impact_knob("LUMOS_IMPACT_ABOUT_MAX", 8))` 這兩個 knob 讀法,跟既有 `LUMOS_IMPACT_BASENAME_MATCH`(`scripts/lumos:13794`)、`LUMOS_IMPACT_PIN_HOP`(`scripts/lumos:14420`)、`LUMOS_IMPACT_FREE_QUOTA`(`scripts/lumos:14458`)同一種「`int(_impact_knob(...))` 包一層」寫法,沒有引入新的旋鈕讀法。
- `impact-hook.py` 的 `ab = "★關於★" if x.get("about_hit") else ""`(`scripts/hooks/claude/impact-hook.py:349`)跟緊鄰的 `ct = f" ★{x['contract']}★" if x.get("contract") else ""`(`scripts/hooks/claude/impact-hook.py:238`,同函式內)是同一種「條件式 ★...★ 包字串再塞進 f-string」寫法。

**一處 minor、判不準,列出但不主張是不對齊(⚠):** `governance/eval/retrieval_eval.py` 的 `report_goldset` 把原本 `[search n=...] nDCG@{k}: legacy=... ranked=...` 這種短括號式報表(這支 diff 動之前,`retrieval_eval.py` 自己就是這樣寫,同目錄底下沒動到的 `retrieval_eval_multiword.py` 現在也還是這樣寫)整段換成白話敘事風格。這算不算「第二種做法」見仁見智——它沒有引入新機制,只是換了訊息的字面內容,而且 doctor 既有的 Check 訊息本來就是白話敘事風格,所以也可以解讀成「補齊跟 doctor 一致」而不是「另立一套」。歸在 Q2(訊息風格)、標 minor、標 ⚠。
   引句:「print(f"=== 考卷:{_tag_plain}——{_n_s} 題搜尋、{_n_e} 題改程式 ===")」
   對照:`governance/eval/retrieval_eval_multiword.py:67`(同目錄未動檔案仍用 `=== 多詞回退量測(k={k};語料釘 {a.vault}) ===` 短括號格式)

---

## 總計

不對齊共 5 條,其中 major 2 條。
