severity: minor

# 測試假綠審查:Java 補棧(631d7e3b..HEAD)

## 審查方式

在 `/tmp/java-audit/repo`(`git clone -q /Users/enzo/harness/lumos-toolchain repo`,clean clone,HEAD=cb94003c,working tree clean)上動手,**沒有**碰 `/Users/enzo/harness/lumos-toolchain` 本身。每個翻紅釘都是:改一行 production 碼(用 python heredoc 精準字串替換,改完先 `python3 -c "import ast; ast.parse(...)"` 驗語法)→ 跑 `python3 scripts/test_lumos.py -k <關鍵字>` → 看輸出 → `git checkout -- scripts/lumos`(或 `scripts/test_lumos.py`)還原再測下一條。全程用的都是被測程式本身的正式路徑(`discover_test_methods`、`_init_config_skeleton`、`_stack_applicability`、`pitfalls --diff --json` 子行程、`code-loop check --json` 子行程),不是測試自己另開的假管線。

## 逐條核對

### `t_java_profile_discovery` —— 兩條翻紅釘,一條不成立

- **JAVA_TEST_RE 的 `.*?` 換回 Kotlin 版 `[^{]*?` → 宣稱②翻紅**:實測只有 ② 紅,其餘全綠。**成立**。
- **exts 從 `.java` 改掉 → 宣稱⑤翻紅**:實測不成立。我用兩種「改掉」的解讀都試過(改成 `.jav`;改成空集合 `set()`),兩次結果一致:紅的是 ①②③⑥⑦(5 條),⑤(「註解裡的假測試剝掉」)**全程維持綠燈**——因為 exts 一改,`discover_test_methods` 根本掃不到任何 `.java` 檔,`got` 變空集合,而 ⑤ 斷言的是「`commentedOut`/`inBlockComment` 不在 got 裡」,空集合當然滿足這句話,所以不會紅。真正因為 exts 被改掉而翻紅的是 ⑥(直接斷言 `prof["exts"] == {".java"}`)以及連帶失去掃描結果的 ①②③⑦。

  這屬於鏡頭第 4 型(翻紅釘寫在註解裡但其實不成立)。不影響防線本身——測試整體確實會抓到這個回歸(有 5 條斷言紅),只是 docstring 指錯了行號,會讓下一個做同樣「實際拿掉驗一次」的人(包括我一開始)去對錯的斷言、白繞一圈。

  引句(docstring 原文,file: `governance/review-reports/code-java補棧/r1-slice-code.patch:34378`,對應到 `scripts/test_lumos.py` 內 `t_java_profile_discovery` 的翻紅釘那行):
  「把 exts 從 .java 改掉 → ⑤翻紅」

### `t_java_stack_wiring` —— 兩條翻紅釘都成立,且額外驗出真殺傷力

- **`_ARCH_IDIOM_SKILL` 拿掉 `"java"` → 宣稱②翻紅**:實測兩條標②的斷言(`.java → java-idioms`、`架構對齊附 java-idioms`)都紅,其餘綠。**成立**。
- **`_STACK_QUESTION_SPECS` 拿掉整個 `"java"` 鍵 → 宣稱①③翻紅**:實測 ①③ 皆紅(外加一條連帶的②鍵值斷言與一個 KeyError 提前中止,屬預期的附帶效應,不影響①③的成立性)。**成立**。
- 我另外自己造了一個「壞版本」測抓不抓得到:把 `java-collections` 這一題整條從清單刪掉(7 題變 6 題),但**不動**任何測試碼(讓 `t_stack_question_triggers` 裡寫死的 id 集合維持包含 `java-collections`)。結果 `t_java_stack_wiring` 的「①java 題組七題」與「③java 棧附七題」翻紅,`t_stack_question_triggers` 的「①id 集合釘住」也翻紅——三條斷言都抓到了。
- 我又造了第二個「壞版本」:在 `java-android` 的 `when` 清單裡混進一條屬於 `java-data` 的觸發詞(`findAll\(`),模擬複製貼上時誤把後端資料層字眼也塞進 Android 題。結果「④後端改動(findAll)只讓 java-data 適用,不問 Android」精準翻紅(2 個 id 命中而非預期 1 個)——證明「平台特有題互不干擾」這條斷言不是空話,是真的在比對集合。

### `t_stack_question_triggers`(java/py 相關改動部分)

- 新增的 id 集合(py-*/java-*)、`_samples`(命中/不命中)、`_legacy`(舊寫法同題）、`when_raw` 反面詞(`log.error("time.sleep failed...")` 不誤觸 `py-eventloop`、`raise ValueError('call fetchall()...')` 不誤觸 `py-memory`)全部驗證過:baseline 全綠;上面兩個「壞版本」(少一題、跨題污染)都能讓這支測試的斷言連動翻紅,不是獨立於 `t_java_stack_wiring` 之外的裝飾性斷言。

### `t_init_writes_config_skeleton`(五語言那段新增)

- 把 `_init_config_skeleton` 裡的迴圈從 `for ext, n in ranked:` 改回舊版 `for ext, n in ranked[:3]:`(對應的舊行為),新增的「③五種語言全部列進平台表」斷言立刻翻紅(平台表只剩 `kotlin/node/python` 三個),抓到了修復前的真實回歸(commit cb94003c 修的正是這個)。**測試會咬人,不是心安符**。

### `t_python_stack_wiring`

- 「把 python-idioms 目錄改名 → ④翻紅」實測成立:`mv skills/python-idioms skills/python-idioms-renamed` 後,④(「慣例對映表指到的每個 skill 都真的存在」)精準翻紅,其餘全綠。

### 額外驗到的真殺傷力(不在被要求逐條翻紅清單裡,但直接相關)

- `t_codeloop_guard_verdict` 新增的 `reason_kind` 斷言:我把 `_make_high_tier_repo` 裡新加的 `_answer_stack_questions(d)` 呼叫拿掉(還原成表態閘上線前的行為),結果「codeloop_guard: tier=high∧pass(HEAD 符)→ 不 blocked」「…skip(HEAD 符)→ 不 blocked」等 5 條斷言全部翻紅,且訊息直接印出 `reason_kind: dispositions`——精準重現了 commit 13e1d2a6 修的那個「代碼審守衛的測試被表態閘擋住,驗不到它真正要驗的那一關」的真實事故。這條護欄不是裝飾。

## 結論性判斷(對照鏡頭四型)

1. 現場走不到被測分支——**沒發現**,五支測試都經由真正的生產路徑(`discover_test_methods`/`_init_config_skeleton`/`pitfalls --diff --json` 子行程/`code-loop check --json` 子行程)驅動。
2. 斷言太寬——**沒發現**,平台隔離、跨題污染、id 集合釘住等斷言在我造的兩個「壞版本」下都精準翻紅,不是「有結果就過」的寬鬆寫法。
3. 測到測試自己造的假資料——**沒發現**,合成的 `.java`/`.py` 樣本是驅動真實 regex/真實 CLI 的輸入,不是自我循環驗證。
4. 翻紅釘寫在註解裡但其實不成立——**發現一條**:`t_java_profile_discovery` 的「把 exts 從 .java 改掉 → ⑤翻紅」不成立,實際翻紅的是 ①②③⑥⑦。防線本身沒有破洞(整體測試仍能抓到回歸),純粹是文件指錯了斷言編號。

severity: minor
blocking: 否
引句:「把 exts 從 .java 改掉 → ⑤翻紅」

位置:file: `scripts/test_lumos.py`(`t_java_profile_discovery` 函式 docstring 最後一句;對應到本次審查材料 `governance/review-reports/code-java補棧/r1-slice-code.patch:34378` 附近的新增區塊)

## 跑過的指令與代表性輸出

```
mkdir -p /tmp/java-audit && cd /tmp/java-audit && rm -rf repo && git clone -q /Users/enzo/harness/lumos-toolchain repo

# baseline(全部先確認乾淨 clone 上全綠)
cd /tmp/java-audit/repo && python3 scripts/test_lumos.py -k t_java_profile_discovery
# 8 passed, 0 failed
python3 scripts/test_lumos.py -k t_java_stack_wiring
# 9 passed, 0 failed
python3 scripts/test_lumos.py -k t_stack_question_triggers
# 51 passed, 0 failed
python3 scripts/test_lumos.py -k t_init_writes_config_skeleton
# 8 passed, 0 failed
python3 scripts/test_lumos.py -k t_python_stack_wiring
# 8 passed, 0 failed

# 翻紅釘①:JAVA_TEST_RE .*? 換回 [^{]*?
python3 scripts/test_lumos.py -k t_java_profile_discovery
# ✗ java ②參數化註解帶大括號也認得(Kotlin 版正則在這裡會漏)  {'totalIncludesTax', 'legacyJUnit4Style'}
# 7 passed, 1 failed   → 只有②紅,成立

# 翻紅釘②:exts 從 .java 改成 .jav(以及另試 set())
python3 scripts/test_lumos.py -k t_java_profile_discovery
# ✗ java ①... ✗ java ②... ✗ java ③... ✓ java ④... ✓ java ⑤...
# ✗ java ⑥... ✗ java ⑦...
# 3 passed, 5 failed   → 紅的是①②③⑥⑦,不是宣稱的⑤;⑤全程綠燈——docstring 這條不成立

# 翻紅釘:_ARCH_IDIOM_SKILL 拿掉 "java"
python3 scripts/test_lumos.py -k t_java_stack_wiring
# ✗ ②.java → java-idioms  None
# ✗ ②架構對齊附 java-idioms  {...idiom_skills: []...}
# 7 passed, 2 failed   → 兩條②都紅,成立

# 翻紅釘:_STACK_QUESTION_SPECS 拿掉整個 "java" 鍵
python3 scripts/test_lumos.py -k t_java_stack_wiring
# ✗ ①java 題組七題 ... ✗ ③java 棧附七題 {} ... EXCEPTION: 'java'
# 1 passed, 4 failed   → ①③紅,成立

# 自造壞版本一:少一題(java-collections)、id 集合不改
python3 scripts/test_lumos.py -k t_java_stack_wiring
# ✗ ①java 題組七題 ['kt', ..., 'java']  ✗ ③java 棧附七題 {...6題...}
# 7 passed, 2 failed
python3 scripts/test_lumos.py -k t_stack_question_triggers
# ✗ FAILED t_stack_question_triggers(1 條斷言)  → id 集合釘住抓到

# 自造壞版本二:java-android 混入 findAll\( 觸發詞(跨題污染)
python3 scripts/test_lumos.py -k t_java_stack_wiring
# ✗ ④後端改動(findAll)只讓 java-data 適用,不問 Android  2
# 8 passed, 1 failed   → 精準抓到污染

# 翻紅釘:ranked[:3] 回退(五語言平台表)
python3 scripts/test_lumos.py -k t_init_writes_config_skeleton
# ✗ ③五種語言全部列進平台表(不是只留前三名)  ['kotlin', 'node', 'python']
# 7 passed, 1 failed

# 翻紅釘:python-idioms 目錄改名
mv skills/python-idioms skills/python-idioms-renamed
python3 scripts/test_lumos.py -k t_python_stack_wiring
# ✗ ④慣例對映表指到的每個 skill 都真的存在(打錯字=審查員拿到一份不存在的慣例)  ['python-idioms']
# 7 passed, 1 failed
mv skills/python-idioms-renamed skills/python-idioms

# 額外:拿掉 _answer_stack_questions(d) 呼叫(還原成修復前行為)
python3 scripts/test_lumos.py -k t_codeloop_guard_verdict
# reason_kind: dispositions(預期 review)→ 5 條斷言翻紅,重現真事故
```

## 結尾

最嚴重 severity:minor;blocking 條數:0。
