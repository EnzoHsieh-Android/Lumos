---
type: project
status: done
created: 2026-07-25
updated: 2026-07-25
tags:
  - type/project
  - status/done
related:
  - "[[Systems/test-profile-multiplatform]]"
  - "[[Systems/check-t-sentinel]]"
  - "[[Systems/lumos-cli-read]]"
summary: |-
  FLAG:DECISION
  KEY:問題(r1 審計改寫根因)=真遺忘合約被 Check T 判「偽證據」的真兇是 discover_test_methods 對★所有語言★做 C 式註解剝離(r1F1 blocker,實測:test_lumos.py 中文註解的 status/* 與 27 萬字元外的 glob 字面 **/ 配對,re.S 一口吃掉過半檔案含 166 個 t_ 測試,260→94)——此地雷★既有★、每次 doctor 都在踩(r1F5),只是至今無合約指到被吃區間才沒發作。原診斷「dirs 找不到資料夾」是錯的(r1F2:Check T 的 discover/haystack 走全 repo os.walk,dirs 只有 guard scaffold 的 _detect_test_dir 在用)
  KEY:修法 v3(std 折入,更簡)=①profile 加 comment_strip 欄位:"c-style"(預設,既有 4 profile 不變)/"none"——★python=none 不剝★(stdF3:hash 剝離會誤傷字串裡的 #;不剝+行首錨即可:被註解的 # def 不在行首,天然排除),discover_test_methods 依 profile 選 ②TEST_PROFILES 加 "python":exts={.py}、PYTHON_TEST_RE=★行首錨 ^def (t|test)_*(欄位0,re.M;stdF1:排除巢狀/類內/縮排 def——本 repo runner 只收 module-global,行首錨對齊收集語意)★、scaffold_ext=".py"(r1F3 KeyError)+★scaffold_name 模板欄="test_{m}.py"★(stdF2:預設 XTests.py 會被檔名錨排除,scaffold 產物必須自己能被掃到)、file_name_match=★新欄位:basename fnmatch glob list ["test_*.py","*_test.py"],副檔名檢查後、讀檔前套用★(stdF4:與 maestro 的 file_must_match(內容 regex 錨)是兩機制,明定型別免混用)、comment_strip="none" ③新欄位全放 TEST_PROFILES dict 靜態值(stdF6:multiplatform 路徑 dict(TEST_PROFILES[p]) 繞過 load_test_profile,欄位放 dict 兩路徑都吃到) ④本 repo config 轉 test_profile=python(inline method_regex 取代非疊加,收斂 t_——Codex 查證確認)。不做 dirs inline 覆蓋(r1F2)
  KEY:python profile 誠實天花板(r1F4+stdF1/F3)=四個既有 profile 都錨框架註冊標記,python 無——緩解:檔名錨(pytest 收集慣例)+行首錨(對齊 module-global 收集)。殘餘誠實記:①行首無斷言 helper(def t_shared_setup)仍判 real——語法先天限制,attr_hint 明示,「寬鬆只漏報」不成立會製造假 real ②三引號字串內恰在欄位0的 def t_x() 仍被誤認(極罕,殘留) ③c-style 剝離對 .cs 字串字面值含 /*或// 的誤剝=★既有病非本刀新增★(stdF3:const string open="/*" 會吃掉真測試;缺 lexical state,修=另立) ④haystack(CODE_EXTS_T 含 .py)與 discover 語言範圍不一致→fake/dangling 訊息措辭可能失準,real 判定不受影響(stdF7,既有,記殘留)
  KEY:落地後回填=lumos-cli-read 真遺忘 KEY 升回正式硬合約(test+audit 章 2026-07-24 已備);[已知缺口]KEY 改記已補+根因更正(是註解剝離非 dirs)
  KEY:Android 側體檢(2026-07-25 順帶)=Citrus_KDS kotlin 正常(1 硬合約 0 偽證據,73 節點綠)/CompassKiosk 正常(19 節點綠);vendored 7/22 版可 lumos update。kotlin/csharp 的 c-style 剝離對其語言正確,不動
  DECISION:根因修正優先(comment_strip 語言感知)+python profile(含 scaffold_ext+檔名錨)+本 repo 轉 python;dirs 覆蓋 YAGNI 砍(r1F2);使用者 2026-07-25
  DEP:scripts/lumos TEST_PROFILES/discover_test_methods/load_test_profile/build_code_haystack/CODE_EXTS_T/cmd_guard_scaffold｜.lumos/config.json
  PRIOR-ART:①最小解=profile 加一欄+剝離器分流+一則 profile dict ②世界解=pytest 檔名收集慣例 test_*.py(borrow 當檔名錨) ③裁定=borrow-design
verified_by:
  - "[[Verification/2026-07-25_CheckT-Python-profile]]"
---
# CheckT-Python-profile_計劃

> **狀態**：done（r1 light＋std Codex 折入 → TDD 落地，見 [[Verification/2026-07-25_CheckT-Python-profile]]）。緣起：真遺忘合約被 Check T 判偽證據；lumos 自己是 Python 卻吃不到自家合約鏈。

## 白話問題（r1 審計後的正確版）

原以為是「Check T 不知道去哪個資料夾找 Python 測試」——**錯**。真兇是：Check T 掃測試時會先把「C 語言式註解」剝掉（`/*...*/`），而且**對所有語言都剝**。Python 沒這種註解，但程式碼裡會巧合出現 `/*` 字樣（例如中文註解寫「`status/*` 標籤」）——剝離器把它當註解開頭、一路配對到幾十萬字元外的下一個 `*/`（一個 glob 字面值），**一口把半個測試檔吃掉**（實測 260 個測試被吃剩 94，真遺忘那條正好在被吃區間）。這顆地雷是**既有的**、每次 doctor 都在踩，只是至今沒有合約指到被吃區間才沒發作。

## 修法（v3，std Codex 折入後——比 v2 更簡）

1. **`comment_strip` 欄位（根因修）**：`"c-style"`（預設；csharp/kotlin/playwright 照舊）／**`"none"`（python）**。**不做 hash 剝離器**（std F3：`#` 行剝離會誤傷字串字面值裡的 `#`，如 regex/URL anchor）——Python 根本不需要剝：被註解掉的 `# def t_x` 不在行首，**行首錨天然排除**。`discover_test_methods` 依 profile 分流。
2. **加 `python` profile**（新欄位全放 `TEST_PROFILES` dict 靜態值——std F6：multiplatform 路徑 `dict(TEST_PROFILES[p])` 繞過 `load_test_profile`，欄位放 dict 兩條路徑都吃到）：
   - `exts={".py"}`；`PYTHON_TEST_RE`＝**行首錨** `^def ((?:t|test)_\w+)\(`（欄位 0、`re.M`）——std F1：排除巢狀/類內/縮排 def，對齊本 repo runner「只收 module-global」的收集語意。
   - **`scaffold_ext=".py"`**（r1 F3：`cmd_guard_scaffold` 直接索引、缺鍵 KeyError）＋ **`scaffold_name` 模板欄＝`test_{m}.py`**（std F2：預設 `XTests.py` 命名會被檔名錨排除、scaffold 產物永遠掃不到——scaffold 產物必須自己能被 Check T 認得）。
   - **`file_name_match`＝新欄位**（std F4 明定，免與 maestro 的 `file_must_match`〔內容 regex 錨〕混用）：**basename fnmatch glob list** `["test_*.py","*_test.py"]`，**副檔名檢查後、讀檔前**套用。
   - `dirs`（`tests`＋`scripts`，僅 guard scaffold 落 stub 用）、`attr_hint`／`fail_hint`、`comment_strip="none"`。
3. **本 repo config**：`test_profile: python`（inline `method_regex` **取代**內建、非疊加——Codex 查證確認；收斂到 `t_` 前綴）。
4. **明確不做**：inline `dirs` 覆蓋（r1 F2：Check T 掃描不吃 dirs，YAGNI）。

## python profile 誠實天花板（r1 F4＋std F1/F3）

四個既有 profile 都錨「框架註冊標記」（`[Fact]`／`@Test`／`test()`／`appId:`）；Python 無。緩解＝**檔名錨**（pytest 收集慣例）＋**行首錨**（對齊 module-global 收集語意）。殘餘誠實記：
1. 行首的無斷言 helper（`def t_shared_setup`）仍判 real——語法先天限制，`attr_hint` 明示；「寬鬆只漏報」不成立、會製造假 real。
2. 三引號字串內恰在欄位 0 的 `def t_x()` 仍被誤認（極罕，殘留）。
3. **c-style 剝離對 `.cs` 字串字面值含 `/*`／`//` 的誤剝＝既有病、非本刀新增**（std F3：`const string open="/*"` 會吃掉後方真測試；根治需 lexical state——另立）。
4. haystack（`CODE_EXTS_T` 含 `.py`）與 discover 語言範圍不一致 → fake/dangling **訊息措辭**可能失準；real 判定只靠 discover、不受影響（std F7，既有，殘留）。

## 落地後回填
- `lumos-cli-read` 真遺忘 KEY 升回正式硬合約（`[test:]`＋`[audit:]` 已備）。
- 同節點「已知缺口」KEY 改記已補＋**根因更正**（是註解剝離、不是 dirs）。

## 明確不做（範圍刀）
- 不動既有 4 profile 的既有欄位值（c-style 剝離對其語言正確；Citrus_KDS 今日體檢正常）。
- 不做 profile 自動偵測。
- 不做 inline `dirs` 覆蓋（r1 F2）。

## 測試策略（TDD，std F5/F6 修正）
1. `t_comment_strip_language_aware`：**r1 實測炸點當 fixture**——`test_x.py` 含「`status/*` 註解＋遠處 `**/` 字面＋中間 `def t_mid`」→ python profile 認得 `t_mid`（不被吃）；**c-style 對照組用 `.cs` fixture**（std F5：拿 .py fixture 掛 csharp 會先被 exts 濾掉、對照假綠——`.cs` 檔含 `/*..*/` 包住的 `[Fact]` 方法 → 確認照舊被剝）。
2. `t_python_profile`：`test_*.py` 的行首 `def test_a`/`def t_b` 認得；**縮排/類內 `def t_nested` 不認**（行首錨）；非測試檔名 `helper.py` 的 `def t_c` 不認（檔名錨）；`scaffold_ext`/`scaffold_name` 存在且 scaffold 產物檔名命中檔名錨（std F2 迴歸）。
3. **multiplatform 路徑**（std F6）：config `platforms: {py: {profile: python}}` → `_platform_test_index` 下 discover 正常（新欄位經 dict 靜態值直達、不靠 load_test_profile）。
4. **本 repo 端到端**：config 轉 python 後 `doctor` Check T：真遺忘合約升格 → 「0 裸合約/0 偽證據/0 未審」。
5. 既有 profile 迴歸：全套不紅（含 multiplatform kotlin/csharp 測試）。

## 實務隱患
- **comment_strip 預設值**：未宣告的自訂 profile 走 `c-style` 向後相容——但這意味「有人用 inline 覆蓋掃 .py 而沒轉 python profile」仍踩地雷；升級提示寫進 doctor 訊息不現實，記文件。
- **檔名錨與本 repo**：`test_lumos.py` 命中 `test_*.py` ✓；未來若加測試檔要守慣例命名。
- **r1F5**：此地雷既有、非本次新增風險——修的是舊病，本計劃是照妖鏡不是病源。
