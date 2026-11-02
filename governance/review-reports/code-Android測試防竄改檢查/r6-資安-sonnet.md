severity: minor

我看了整份凍結 patch 和第六輪修補差異,沒有找到可以直接利用的洞,四條 finding 都是縱深類。我也實跑了 assume/門檻身分、catch 判讀和關閘幾條路徑,修前修後各跑一次(臨時目錄已用字面絕對路徑刪除)。

## ①提示注入
已看,無。候選裡的外來字串(檔名、函式名)都經 `_out_clean` 清控制字元,放行指令用 `shlex.quote` 組出,`lint-waive --list` 的欄位也都清過。

## ②讀寫與執行越界
已看,無。
- `test-guard` 只讀 git:用 `--no-ext-diff --no-textconv`,版本一律先解成完整 sha,`rev-parse` 帶 `--end-of-options`。
- 這輪的 diff 沒有動到 hook、安裝腳本、CI 或下載網址。
- 新增內容裡沒有密鑰或信箱。
- 公開檔的私有考場識別字:新檔和公開卷證只有專案名 mOrangePos;上一版出現過的短提交編號與本機分支名,這版已經拿掉;`history.json` 與 `cases.json` 是代稱。

## ③非刻意、一步就能繞過的守衛

### S1 `reference.md` 仍宣稱 test-guard 會比對建置檔與 CI,跟實際行為不符
severity: minor
blocking: 否 — 只是說明文字與實際範圍不符,工具判讀本身沒有被繞過,縱深類
引句:「建置檔或 CI 讓測試失敗不算數的作弊候選」
file: `skills/lumos-project-notes/reference.md:118`
攻擊路徑:
- 誰:讀這份 skill 的 AI 或使用者。
- 從哪:`reference.md` 的「子命令全覽」把 `test-guard` 寫成會列「建置檔或 CI 讓測試失敗不算數」的作弊候選。
- 送什麼:在 `build.gradle` 加 `ignoreFailures = true`,或在 CI 加 `-x test`。
- 拿到什麼:以為被守住所以不做人工審,實際 `_tg_kind` 對建置檔與 CI 回 None,完全不列。
- 第五輪只改了 `HELP_WHEN`、argparse help 和標準,漏掉這一處。釘文字的測試只掃 `--help` 輸出,抓不到。

重現:
```
grep -c '建置檔或 CI 讓測試失敗不算數' skills/lumos-project-notes/reference.md
```
修前 5516466e 與修後 34bef2d8 都是 1;`lumos test-guard --help` 已不提建置檔,兩邊自相矛盾。

歸因:有證據的原有漏查(兩版都有)。

### S2 catch 裡寫成恆成立但不是字面 `true` 的檢查,吞掉斷言的 catch 照樣不列
severity: minor
blocking: 否 — 已在抓不到清單點名同一類(`assertTrue(true)`),只是舉例太窄;不是這輪修補引入
引句:「(?:check|require)\s*\((?!\s*true\s*\))」
file: `scripts/lumos:48821`
攻擊路徑:
- 誰:照常寫測試的 AI(不一定是刻意)。
- 從哪:新增或修改測試,寫成 `try { f(); fail("x") } catch (e: Throwable) { assertNotNull(e) }`,或 catch 內放 `check(1 == 1)`、`forEach { check(it == it) }`。
- 送什麼:上面這個 try/catch。
- 拿到什麼:`fail()` 丟的 AssertionError 被 `Throwable` 接住,測試永遠綠;`catch_checks` 因為有檢查呼叫為真,第二條「吞掉」判斷不成立,不列 `tq/catch-no-fail`。
- 只有字面 `check(true)`、`require(true)` 被排除。

重現(臨時 repo,`lumos test-guard --diff A..B`):
- 新增 `try{assertEquals(1,f());fail("x")}catch(e:Throwable){assertNotNull(e)}`:退出碼 0,無候選。
- 同上換成 `check(1 == 1)`:退出碼 0,無候選。
- 換成 `check(true)` 或 `require(true){…}`:修後列出,修前不列。這是修補帶來的改善。

歸因:有證據的原有漏查(修前修後對 `assertNotNull(e)`、`check(1==1)` 結果相同)。

### S3 try 裡只有 Kotest 的點號呼叫寫法斷言時,被 catch 吞掉不列
severity: minor
blocking: 否 — 縱深;Kotest 點號寫法搭配吞例外不常見,修前也是同樣結果
引句:「_TG_INFIX_STRICT = re.compile(r"(?<=\s)should[A-Z]\w*(?=\s+[^\s=:])")」
file: `scripts/lumos:48824`
攻擊路徑:
- 誰:用 Kotest 匹配器的 AI。
- 從哪:新增 `@Test`,寫成 `try { f().shouldBe(5) } catch (e: Throwable) { println(e) }`。
- 送什麼:上面這個 try/catch。
- 拿到什麼:窄規則要求前後都是空白,認不出 `.shouldBe(`,所以 `tried` 為假,第二條「吞掉」判斷不成立;不列 `tq/catch-no-fail`,測試永遠綠。
- 計劃 S6 只寫「try 裡只有 Kotest 中綴斷言……要列」,但抓不到清單沒提點號寫法。

重現:
- 點號寫法 `f().shouldBe(5)`:退出碼 0,無候選。
- 中綴寫法 `f() shouldBe 5`:修後列出,修前不列(修補的改善)。

歸因:有證據的原有漏查(點號寫法修前修後都不列)。

### S4 shell 殘留 `LUMOS_SKIP_LINT_NEW=1` 時,推送輸出什麼都不印
severity: minor
blocking: 否 — 只有治理帳(沒有候選時連帳都不寫),健檢只做軟提醒,且關閘留帳是已知取捨
引句:「skip_env = os.environ.get("LUMOS_SKIP_LINT_NEW") == "1"」
file: `scripts/lumos:38951`
攻擊路徑:
- 誰:使用者本人。
- 從哪:先前為了單次出口把 `LUMOS_SKIP_LINT_NEW=1` 寫進 `export` 或 shell rc,之後忘了。
- 送什麼:之後每次一般的 `git push`。
- 拿到什麼:新增告警閘整道(含作弊比對的擋)被走過,推送輸出一個字都沒有。
- 鄰居閘如 `LUMOS_SKIP_FIX_CHECK` 跳過時會印「跳過」一行,這道不印。
- 只有「有候選或比對出錯」才寫 `skipped-env` 帳;乾淨範圍什麼都不留。

重現(`_lint_new_verdict` 加 `_codeloop_lint_new_step`,設 `LUMOS_SKIP_LINT_NEW=1`):
- 有作弊候選的範圍:status=off、blocked=False,stdout 與 stderr 皆空。
- 乾淨範圍:同樣是空,也沒有 events。
- 設成 `0`:照常判並擋下(第五輪「只認 1」有效)。

歸因:有證據的原有漏查(修前修後輸出相同)。

### 逐項查證(不另列 finding)
- **身分只在字串外整理空白**:實跑沒有「字串外小改動被誤當新增」,也沒有「新作弊被舊放行放掉」。
  - 字串外空白重排、逗號前空白、`x - 1` 與 `x -1`、註解插入都不列。
  - 字串內多一個空白、raw string 縮排不同、門檻 0.01→0.5 都列。
  - 身分字串變細,舊放行指紋只會失配後重新擋(往安全方向),不會放過新作弊。
- **說明文字**:除 S1 外,help、`HELP_WHEN`、標準的抓不到清單、`_TG_LIMITS` 與計劃都已改成「這一版不比建置檔與 CI」。

總結:這一輪的修補沒有引入可直接利用的新洞;四條 minor 全是修前就存在的縱深或文字問題,其中 S1 最值得順手改一行。
