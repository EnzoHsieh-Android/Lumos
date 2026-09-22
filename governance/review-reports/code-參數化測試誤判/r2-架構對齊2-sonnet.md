severity: major

## F1 用「函式掛屬性」塞第二支存取器,繞過這支函式自己一直在用的「多回傳值」慣例

severity: major
blocking: yes

`_platform_test_index` 這支函式本身的既有寫法,是把每一種「該平台的惰性查詢」都當成一個回傳值,回一個 tuple 讓呼叫端解構(`pdata, split, default, methods_for, hay_for = _platform_test_index(...)`)。`methods_for`、`hay_for` 兩支存取器就是這樣並列回傳的。這批新增的第三支存取器 `loose_for` 卻沒有照做,而是掛成 `methods_for` 這個函式物件的屬性:

引句:「methods_for.loose = loose_for」

問題不是「能不能跑」——Python 函式本來就能掛任意屬性,九個呼叫點目前也確實都是直接把 `_platform_test_index` 回傳的同一個 `methods_for` 物件原封不動往下傳,所以 `.loose` 暫時掛得住。問題是這跟本檔案這支函式自己訂的慣例不一致:同一個函式裡,`hay_for` 用明寫的第五個回傳值處理,`loose_for` 卻改用隱性的屬性附掛,兩個結構一樣(都是「plat → 惰性快取結果」的存取器、都用同一個 `lcache={}`/`if plat not in lcache` 寫法),只有「怎麼交給呼叫端」這一步不一致。這代表:
- 之後有人想把 `methods_for` 包一層(例如加 `functools.wraps` 的裝飾器、或改成回傳一個 partial/lambda、或把回傳值改成 namedtuple/dataclass 的欄位)時,`.loose` 這個附掛的屬性會在不噴錯的情況下悄悄消失——`_loose_of` 的 `getattr(methods_for, "loose", None)` 設計上就是「拿不到就回 None」,呼叫端讀到 None 的下游行為是「不豁免」(維持嚴格),所以不會直接放行假綠,但也代表這條路徑失效了不會有任何警訊,純粹要靠人記得。
- 這支函式自己的 docstring 已經跟實際回傳值有落差(`docstring` 只寫「回 (split, default, methods_for, hay_for)」,實際回傳 `pdata, split, default, methods_for, hay_for` 五個值,見 `scripts/lumos:10406`),可見這個回傳介面本來就沒有嚴格維護;再疊上一層「屬性掛在回傳值上」的隱性擴充,只會讓下一個人更難從函式簽章看出 `methods_for` 這個東西實際帶了什麼。

比較一致的做法,是讓 `_loose_declared_methods`/`loose_for` 照 `hay_for` 的樣子,一樣當成 `_platform_test_index` 的第六個回傳值,由三個呼叫鏈(`_spec_gate_run_clauses`/`_spec_gate_regress`/`_spec_gate_push_one`)明寫多帶一個參數——這本來就是這支函式現在在用的模式,不需要發明新機制。

## F2 用字串前綴比對來改寫別人的正則樣式,沒有先例,且對「不是逐字 `(?m)^` 開頭」的等價寫法會靜默退回嚴格版、重演 r1 抓到的那種少算風險

severity: major
blocking: yes

`_loose_declared_methods` 判斷「要不要放寬」的辦法,是對編譯好的 regex 的 `.pattern` 字串做逐字首碼比對:

引句:「if src.startswith("(?m)^") and not src.startswith("(?m)^[") and not src.startswith("(?m)^\\s"):」

這個檔案裡目前所有跟「每個測試棧一支專屬 regex」有關的客製化,一律是走「在 `TEST_PROFILES` 那個 dict 裡手寫一個新欄位」這條路,而且這條路是這份檔案自己講明的慣例——Python profile 那段就直接寫「新欄位全放 dict 靜態值」(`scripts/lumos:3997` 上方註解),`file_name_match`/`comment_strip`/`scaffold_name` 都是這樣加的,沒有任何一處是「讀一條既有 regex 的 `.pattern`、用字串切片/前綴比對去猜、拼出另一條語意不同的 regex」這種做法。這批引入的字串手術是本檔第一例,而且它比對的判準很脆:只認「逐字以 `(?m)^` 開頭」這一種寫法。

以本批自己新增的 `.lumos/config.json` 逃生口(`test.method_regex`,見 `scripts/lumos:4082`,經 `_safe_user_regex` 編譯、只套 `re.S`、不會自動幫使用者補 `(?m)`)為例:如果有人照這個逃生口的既有範例(fixture 裡就是這樣寫的,`method_regex: "(?m)^def (t_[A-Za-z0-9_]+)\\s*\\("`)去客製一條同時要多行錨定又要別的 inline flag 的正則,例如把 flag 合併寫成 `(?im)^def ...`(忽略大小寫+多行,兩個修飾字母順序調換也完全合法、語意跟 `(?mi)` 一樣),`src.startswith("(?m)^")` 就會判 False——因為字串比的是「這四個字元剛好是 `(?m)^`」,不是「這條 regex 有沒有用多行模式錨在行首」。判 False 會直接落到 else 分支:

引句:「loose = mre          # 本來就不是錨在欄位 0 的樣式,直接用」

這一行的註解假設「判不到 `(?m)^` 開頭 = 這條 regex 本來就沒有錨在欄位 0」,但 `(?im)^...` 明明就是錨在欄位 0 的多行樣式,只是文字順序不同。結果是:`loose_for` 對這種自訂 regex 悄悄退回跟 `methods_for` 一樣嚴格的版本(沒有放寬),而 `_loose_of`/`_spec_gate_declared` 這條路徑本身設計上「算不出來就不豁免」是安全的——但這裡不是「算不出來」,是**判斷邏輯本身誤判成算不出來、又剛好走到「維持嚴格」這個安全分支**,純屬僥倖,不是這支函式的設計保證。如果哪天有人把這個字串前綴判準改個方向(例如誤解成「判不到就當作已經夠寬」),或是這個函式被拿去用在其他「少算=危險」的地方,這個脆弱點就會變成真正的少算。

這正是這批修改本身在寫的那句話所擔心的情境(「改寫在哪些樣式上會失敗」):

引句:「回 None 的意思是「這個棧我沒把握掃得全」,呼叫端要當成「不知道」而不是「沒有別的」——」

——但 `(?im)^` 這種案例並不會走到「回 None」那條有把關的路徑,而是被誤判成「不用放寬」直接放行 `mre`,繞過了這句話原本想保護的那道防線。

現有測試 `t_spec_gate_collision_inside_class_still_weak`(新增於 `scripts/test_lumos.py`)只驗了預設 Python profile 的 `(?m)^def (...)` 這一種寫法,沒有任何測試餵一條 flag 順序不同或用其他方式達成「多行行首錨定」的自訂 `method_regex`,所以這個退化路徑目前完全沒有紅綠可驗。

---

已驗過、沒問題的部分(供對照,非發現):
- 九個內建 profile 的 `method_re` 常數逐一核對過(`scripts/lumos:3761-3826`):只有 `PYTHON_TEST_RE`、`MAESTRO_NAME_RE` 逐字以 `(?m)^` 開頭,其餘六個(C#/Kotlin/Java/Playwright/Dart/Swift/Jest)本來就不靠行首錨,`loose_for` 對它們會落 else 分支原樣使用,不會誤放寬也不會誤收窄。
- `loose_for`/`lcache` 的快取寫法(`if plat not in lcache: ...` + `pdata["platforms"].get(plat)` + `pl["root"]`/`pl["profile"]`)跟同函式裡 `methods_for`/`hay_for` 的 `mcache`/`hcache` 寫法逐行對得上,快取粒度、key、guard 條件都一致,這部分沒有風格落差。
- `_loose_declared_methods(repo_root, profile=None)` 的簽章跟它要仿的 `discover_test_methods(repo_root, profile=None)` 一致,呼叫慣例(`profile = profile or load_test_profile(repo_root)`)也照抄。
