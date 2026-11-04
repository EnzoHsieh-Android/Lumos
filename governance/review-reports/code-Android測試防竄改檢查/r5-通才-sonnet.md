severity: major

這份差異把建置檔與 CI 兩類規則整段移走,測試檔的規則基本守住,但有一條 major、五條 minor。我在 `5516466eb` 的 clone 裡跑了 `-k tq_guard` 173、`-k lint_new` 82、`-k lint_waive` 31,全綠。

### F1 assume 條件的字串常值只在字首或字尾加空白時,條件改動不會被列出
severity: major
blocking: 是 — 計畫 S1 條款寫「把既有 assume 的條件改掉」要列 `tq/skip-added`,而這個改法列不出來,綁定測試 `t_tq_guard_skip_added` 沒抓到。
引句:「(換行重排不算改動,字串常值 "c i" 跟 "ci" 仍不同)」
file: `scripts/lumos:48892-48895`(`_tg_stmt_at` 末尾的 `re.sub(r"\s*([^\w\s])\s*", r"\1", text)`)
失敗場景:標點兩側的空白一律被吃掉,而引號本身也算標點。`assumeTrue(env == "ci")` 改成 `" ci"` 或 `"ci "`,條件變成永遠不成立,身分字串仍是 `assumeTrue(env=="ci")`,所以不列。`"a, b"` 改成 `"a,b"` 同理。新測試 `ws` 只測了單字之間的空白(`"c i"`),所以沒抓到。
重現:
```
base: assumeTrue(env == "ci")
head: 把 "ci" 換成 " ci"  →  rules = []          (換成 "ci " 也是 [])
head: 把 "ci" 換成 "c i"  →  [('tq/skip-added', …)]
```
把整行正規化改回「去掉全部空白」,`ws` 測試會翻紅;但上面這個缺口我沒找到任何現有斷言會翻紅。
另外,計畫 `Android測試防竄改檢查_計劃.md` 第 132 行與 `Systems/test-guard.md` 第 24 行仍寫「整個敘述去掉空白」,和現在「壓成一格、標點兩側去掉」不一致。
歸因:有證據的原有漏查。修前(fcd27439)和修後兩版對 `" ci"` 的結果都是 `[]`。修補只補了單字之間的空白那一半。

### F2 `buildSrc`、`build-logic` 底下的測試仍算測試檔,但沒有任何測試守這一點
severity: minor
blocking: 否 — 行為目前正確,是改壞測試照綠的缺口,守的是計畫第 92 行的設計宣告,不是 S 條款。
引句:「    in_build_dir = (p.startswith(("buildSrc/", "build-logic/")) or "/buildSrc/" in p or "/build-logic/" in p) and not _rg_is_test_path(p)」
file: `scripts/lumos:48393`
失敗場景:這一輪把判斷改成 `or in_build_dir → None`,於是 `not _rg_is_test_path(p)` 成了唯一讓 `build-logic/convention/src/test/.../FooTest.kt` 繼續被當測試檔的條件。拿掉它,這類測試加 `@Ignore` 就列不出來。
重現:在 clone 裡把 `and not _rg_is_test_path(p)` 刪掉,跑 `-k tq_guard` 為 173 passed、`-k lint_new` 為 82 passed。沒有紅燈。
歸因:未判定。repo 裡 `buildSrc` 只出現在計畫和 `S11 r4` 的 `_tg_kind` 斷言,修前沒有這條測試,但這一輪改寫了這一行。

### F3 `lumos test-guard` 的說明文字還在宣稱會比對建置檔與 CI
severity: minor
blocking: 否 — 只是說明文字,但這是防竄改工具,錯的覆蓋宣稱會讓使用者以為建置與 CI 有人看。
引句:「放寬 Gradle 或 CI 的測試設定(推送前新增告警閘也會跑)。」
file: `scripts/lumos:70965`、`scripts/lumos:72187`(subparser help 寫「建置或 CI 的測試設定被放寬」)
失敗場景:`lumos test-guard --help` 和 `lumos --help` 的列表都還印著這句。實際上改 `ignoreFailures = true` 或 `-x test || true` 不會出任何候選(F1 之外我另外跑過,結果 `[]`)。計畫、標準、`Systems/test-guard` 都已改成「這一批不比」,只有這兩處漏掉。
歸因:有證據的修復回歸。修前這句是真的,縮範圍之後變成假的,這一輪的 diff 沒碰到。

### F4 `tq/too-large` 的新措辭「超過的部分沒有比對」對整檔超限不準,測試只是把常數再比一次
severity: minor
blocking: 否 — 人看到訊息會誤判比對範圍,但訊息仍指示人工看改動。
引句:「"tq/too-large": ("檔案超過比對工具的上限,超過的部分沒有比對", "人工看這支檔的改動,或拆小"),」
file: `scripts/lumos:48968`(整檔超限的出口在 `scripts/lumos:49074`)
失敗場景:單檔超過行數或位元組上限時整檔不比,只出這一條候選。訊息卻讓人以為只有超過的那段沒比。
重現:測試檔開頭加 `@Ignore`,後面補 10 萬行註解 → 只有 `('tq/too-large', '檔案超過比對工具的上限,超過的部分沒有比對')`,沒有 `skip-added`,也就是前面那行 `@Ignore` 根本沒比。
`S11 r4 太大的訊息說的是…` 只斷言常數字串包含這句話,沒驗它描述的行為。長行只抹掉該行、其餘照比,這個情境才符合「超過的部分」。
歸因:未判定。

### F5 類別父型別換行的修補只有逗號一個樣本,冒號結尾沒測,逗號後接空行或註解行仍會丟掉類別路徑
severity: minor
blocking: 否 — 改壞冒號分支,測試照綠。
引句:「        if stripped[max(j, p - 50):p].rstrip().endswith((",", ":")):    # 行尾逗號或冒號:父型別接在下一行(只看換行前一小段,不複製整行)」
file: `scripts/lumos:48479`
失敗場景:`S16 r4` 只用 `Base(),` 一個樣本。
重現:
- 把 `(",", ":")` 改成 `(",",)`,`-k tq_guard` 仍為 173 passed。
- `class FooTest :\n    Base() {` 在這個改壞下會退回 `['t']`,沒有類別名。
- 逗號後插空行、`// note`、KDoc 的 `class FooTest : Base(),\n    // note\n    Other {`,現在的結果也是 `['t']`,類別路徑掉了。修前也是這樣。
歸因:修補本身有效,修前 `class FooTest : Base(),\n    Other {` 是 `['t']`,修後是 `['FooTest.t']`。其餘是新分支沒測和原有限制。

### F6 深巢狀路徑換成摘要時,摘要裡的 sha256 沒有測試守
severity: minor
blocking: 否 — 改壞照綠,但實作現況正確。
引句:「    return "#" + hashlib.sha256(full.encode("utf-8", "replace")).hexdigest()[:16] + "…" + full[-(_TG_MAX_PATH_CHARS // 2):]」
file: `scripts/lumos:48456`
失敗場景:把 sha 拿掉只留 `"…" + 最後 100 字`,`-k tq_guard` 173 passed。新測試每一層的類別名都不同,最內層 100 字恰好唯一,所以不用 sha 也不會撞鍵。實際會用到 sha 的情況是兩個頂層類別的深鏈最後 100 字相同,例如各有一條很長的相同內層鏈:拿掉 sha 後兩邊的函式鍵一樣,靠 `#2` 順序區分,改動前後的配對會錯位。
重現:在 clone 把上面那行改成只回 `"…" + full[-100:]`,跑 `-k tq_guard` 為 173 passed。
歸因:未判定。

### 圖譜鏡頭
- `Systems/test-guard` 已把建置檔與 CI 寫成「不負責,移到第二批」,有 `WHY`、`REVISIT:2026-12-15`。計畫的〈三類檔〉也標了第二批,`RETIRE-IF` 保留。
- 計畫第 92、96 行寫的 `buildSrc` 測試是測試檔、正式程式檔不含 `buildSrc` 和 `build-logic`,和程式一致,但沒有測試守(F2)。
- 計畫第 132 行的身分規則沒跟著改(F1)。
- 標準檔裡「抓不到」和 `_TG_LIMITS` 逐字相同,由 `t_tq_guard_cli_contract` 釘住,這一輪也過。
- 新增的限制句(多個 catch 只看第一個、try-with-resources)和程式行為一致:`_TG_CATCH.match` 只配第一個 catch,`try\s*\{` 不認 `try (`。
- 測試假綠形態:F1、F2、F5、F6 屬「守衛的能力宣稱比它擋得住的寬」。F4 的訊息斷言屬重寫常數。
- 其他呼叫端沒壞:`_tg_sort_changes`、`_tg_kinds` 對 `None` 會略過;`_rg_*` 沒被改;新增告警閘不依賴已刪的規則;全 repo 找不到殘留的 `tq/build-config` 與 `tq/ci-config` 引用,只剩計畫第二批的描述和考場 `cases.json`。

### 做過的改壞實驗(都在 clone 內)
- 有翻紅,測試是真的守住:
  - `--list` 的檔名與規則欄不清控制字元 → 紅。
  - 自動放行三個出口(依賴宣告壞掉、放行檔壞掉、git 算不出改動清單)各拿掉原因 → 各紅。
  - `_TG_CHECK_CALL` 失效 → `S6 r4` 紅(`s8`、`s9`)。
  - 中綴斷言判斷失效 → `S6 r4` 紅(`s7`)。
  - 敘述擷取改用保留字串的文字 → 紅。
  - 身分改回去掉全部空白 → `ws` 紅。
  - 拿掉 `.` 續行 → Truth 鏈測試紅。
- 照綠,對應 F2、F5、F6:`buildSrc` 測試路徑條件刪掉、冒號結尾分支刪掉、sha 拿掉。
- 自動放行與 `--list` 這兩組只加了測試,程式碼在本輪沒動,屬補測試,不是新修補。

### 三問
1. 原問題的修復效果有行為證據。
   - G2:兩萬層、每層一支測試,修前 9.73 秒、峰值 2375 MB、最長鍵 128896 字,修後 1.84 秒、41 MB、205 字,結尾都是自己那層的類別名。
   - G5:`class FooTest : Base(),\n    Other {` 修前是 `['t']`,修後是 `['FooTest.t']`。
   - G3:assume 字串裡有 `(`、只改下一行的斷言,修前誤列,修後不列;`"ci"` 改成 `"c i"` 修前漏,修後列;多行 assume 改成 `false` 兩版都列。
   - G4:catch 內的 `shouldBe` 與 `check(`,修前誤列,修後不列;catch 空的吞斷言兩版都列。
   - G1:建置檔與 CI 放寬,修前列三條,修後 `[]`;測試檔加 `@Ignore` 兩版都列。
   - 唯一沒修乾淨的是 F1 的字首、字尾空白。
2. 修補處的正常、錯誤與相鄰呼叫路徑大致仍成立:`S11` 大輸入、巢狀 try、250 行泛型都過,字串、字元、原始字串裡的括號也正確。已知缺口是 F1 的空白,F5 的逗號後空行與註解行是原有限制。
3. 新發現的案例修前、修後:F1 兩版都是 `[]`(原有);F3 修前說明為真、修後為假(縮範圍帶出的回歸);F2、F4、F5、F6 在兩版的程式行為相同,差別只在測試缺口或措辭。

這一輪沒有 blocker 級問題,只有 F1 一條需要在程式裡修(正規化要保留引號內緊貼引號的空白),其餘是測試補強與說明文字。
