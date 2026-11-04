severity: major

## ①提示注入

已看,無。外來文字(檔名、測試函式名、行內容)進擋下訊息前,仍由 `_tg_cand` 呼叫 `_out_clean` 清控制字元。放行指令由 `_lint_waive_cmd` 用 `shlex.quote` 包過。這一輪新增的 `extra` 說明文字是固定字串加常數,不含外來文字。

## ②讀寫與執行越界

已看,無。
- `test-guard` 只用 `git diff --raw -z --no-ext-diff --no-textconv` 之類的唯讀 git 指令,沒有新的讀寫路徑、hook、安裝腳本或下載來源。
- 凍結 patch 的新增行裡沒有密鑰、信箱或 `/Users/` 路徑。
- 公開檔只出現 `mOrangePos`,其他套件名是 `com.example.pos.*` 這種假名。
- 說明文字與宣稱範圍一致:
  - `lumos test-guard --help` 和 `lumos --help` 的 test-guard 條目都沒提建置檔或 CI。
  - 全 repo 掃過,`skills/lumos-project-notes/reference.md` 與 `commands/` 底下的 test-guard 描述也沒有。
  - 「整支沒比對」的訊息確實只加在整支檔過大那一條。

## ③非刻意、一步就能繞過的守衛

### S1 Kotest 匹配器改成照名字前綴認之後,「try 結尾 fail() 而 catch 接住 AssertionError 只吞掉」的寫法,換個 should 開頭的方法名就不再被列
severity: major
blocking: 是 — 守衛被一步編輯繞過,而且上一輪剛修的就是這一類
引句:「_TG_KOTEST_CHECK = re.compile(r"(?<!\w)should(?:Be|Not|Have|Contain|Start|End|Match|Throw|Exist)\w*(?!\w)(?!\s*[=:])")」
file: `scripts/lumos:48822`(用到它的判斷在 `_tg_catch_no_fail` 的 `catch_checks`,約 48846 行以下)
- 誰:照常操作的 AI,或使用者本人。
- 從哪:改一支測試的 catch 區塊。
- 送什麼:`try { foo(); fail("x") } catch (e: AssertionError) { shouldNotify(e) }`,意思是 catch 裡只做不丟出的事。名字只要是 `shouldNot…`、`shouldBe…`、`shouldHave…`、`shouldContain…`、`shouldStart…`、`shouldEnd…`、`shouldMatch…`、`shouldThrow…`、`shouldExist…` 開頭,後面接任何字都算。例如 `shouldNotify`、`shouldBeLogged`、`log.shouldNotLog(e)`。
- 拿到什麼:`catch_checks` 被這個普通方法名滿足,第二個分支(try 裡有斷言、catch 接得住 AssertionError、卻不檢查也不丟出)被跳過。`fail()` 丟出的 AssertionError 被吞掉,測試永遠綠,`tq/catch-no-fail` 不出。
- 為什麼不是第 5 輪就已知的取捨:第 5 輪的窄認法要求「前面空白、後面空白再接值」,`shouldNotify(e)` 後面是 `(`,不會算檢查。新正規式的 `\w*(?!\w)` 加 `(?!\s*[=:])` 只排除了宣告和具名參數。`WHY:` 的「寬判法讓名字以 should 開頭的變數或方法算成檢查」那一類洞,在前綴白名單內重新打開。
- 重現:在臨時 repo 加兩支測試,用兩版的 `lumos test-guard --repo <repo> --diff HEAD~1..HEAD --json` 跑。
  - `swallow`:`try { foo(); fail("x") } catch (e: AssertionError) { println(e) }`
  - `swallow2`:`try { foo(); fail("x") } catch (e: AssertionError) { shouldNotify(e) }`
  - 修前版本(34bef2d8)輸出 `[('tq/catch-no-fail','FooTest.swallow'), ('tq/catch-no-fail','FooTest.swallow2')]`,rc=1。
  - 修後版本(c2335430)輸出 `[('tq/catch-no-fail','FooTest.swallow')]`,`swallow2` 消失。
  - 直接呼叫 `_tg_catch_no_fail`,以下三種寫法修前都回 True、修後都回 False:
    - `catch (e: AssertionError) { shouldNotify(e) }`
    - `catch (e: Throwable) { shouldBeLogged(e) }`
    - `catch (e: AssertionError) { log.shouldNotLog(e) }`
  - 對照:`shouldRetry(e)` 和 `println(e)` 修前修後都列。
- 補一個副作用:try 側的 `tried` 也用同一條正規式,`try { shouldNotify(1) } catch (e: AssertionError) { println(e) }` 修後被列。這只是誤報,不算洞。
- 歸因:有證據的修復回歸。上面的兩版比對就是證據。

### S2 測試函式宣告的泛型兩層以上巢狀,整支測試不進比對
severity: minor
blocking: 否 — 只能新增沒斷言或弱斷言的測試,既有測試改成這樣會被列為測試被刪;而且新寫進抓不到清單的「兩層以上巢狀」已明講
引句:「測試函式宣告的泛型兩層以上巢狀或超過 400 字時那支不比」
file: `scripts/lumos:48413`(`_TG_NAME_RE`;`_tg_functions` 找不到名字就 `continue`)
- 誰:照常操作的 AI。
- 從哪:新增一支 `@Test`,宣告寫成 `fun <T : Map<String, List<Int>>> weak() { foo() }`。
- 送什麼:本體沒有斷言的新測試。
- 拿到什麼:`_tg_functions` 取不到名字就略過這支,`tq/no-assertion` 不出。我實跑兩支這樣的新測試,rc=0、候選為空。
- 限制:既有的 `fun a()` 改寫成這種宣告,head 這邊找不到它,會列 `tq/test-removed`。所以只漏新增的測試。
- 歸因:有證據的原有漏查。修前版本連一層巢狀(`<T : List<Int>>`)都找不到名字,修補擴大到一層,兩層仍不認。現在寫進抓不到清單,說明與行為一致,所以只報縱深。

S1 是這一輪修補把上一輪的洞重新打開,而且是一步編輯就能走過去;S2 已寫進抓不到清單,只算縱深。提示注入、讀寫與執行越界、公開檔的私有識別字都已看,沒有發現。
