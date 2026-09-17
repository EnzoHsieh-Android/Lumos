severity: blocker
# 審查報告:規格落成可驗收條件_計劃(r3)

severity: blocker

## 逐節閱讀結果

**開頭欄位/decisions/summary**:已讀,無 finding(decisions 鏈 d1→d12 的 superseded_by 串接可追,valid 欄位與內容一致)。

**兩層要分開**:已讀,無 finding。

**設計 一、門怎麼判**:見 F1、F7。
**設計 二、條款句式**:見 F8。
**設計 三、綁定規則**:見 F8(keeps 語法位置)、F6。
**設計 四、新閘**:見 F4、F5。
**設計 五、逃逸自動記**:見 F2、F3;`push-gate-unreviewed` 舊帳冒號版本問題見下方「已答無 finding」。
**設計 六、退場條件**:已讀,無 finding(三個數字承認是拍的、口徑寫死、人裁不機械擋,誠實揭露到位)。
**進度/要動什麼/實務隱患/驗收條款/回退/誠實界線/審計修正紀錄**:已讀,無 finding(RETIRE-IF 與 REVISIT 格式合規)。

## Findings

**F1**
severity: blocker
blocking: 是(基礎機制邊界未定義,直接決定已排除豁免與雙向門判定對/錯)
spec 一、門怎麼判;S16/S23
問題:規格反覆講「實務隱患節」但全篇從未定義怎麼機械認出這個節的邊界(標題字面、層級、起訖),而本 vault 已有真實計畫用「## 五、實務隱患」「## 實務隱患（r1 折入版）」等變體標題。
引句:「只跳過「實務隱患」節內、且形如 `已排除:<四類中文名>:<理由>` 的合格行」
file: `docs/lumos-toolchain-knowledge/Projects/關係層傳播守衛_計劃.md:141`(標題是「## 五、實務隱患」);`docs/lumos-toolchain-knowledge/Projects/收斂閘殘餘估計降級_計劃.md:74`(標題是「## 實務隱患（r1 折入版）」)——這兩篇若走規格閘,節邊界判定規則不明。

**F2**
severity: blocker
blocking: 是(本 repo 現有 CI 步驟就會撞到,逃逸帳會靜默漏記)
spec 五、逃逸自動記(CI 列)
問題:`_ci_step_is_test` 用 `re.split(r"[^a-z0-9]+", name.lower())` 切詞,中文字元不落在 a-z0-9,純中文步驟名切出來是空字串,永遠不含 test 類詞;本 repo `.github/workflows` 已有步驟名「自主迴圈測試」,這一步若紅,不會被記為逃逸,跟表格自己的宣稱矛盾。
引句:「結論在 `_CI_RED` **且 `failed_step` 切詞後有一個詞等於 test/tests/pytest/unittest/testing**」
file: `scripts/lumos:22360-22365`(`_ci_step_is_test` 定義);`.github/workflows/*.yml:61`(步驟名「自主迴圈測試」)。

**F3**
severity: major
blocking: 是(逃逸帳 precision 欄位失真,直接餵給第六節退場門檻)
spec 五、逃逸自動記(代碼審列)
問題:程式碼 `_hit = any(v in ("major","blocker") and (_kinds is None or _kinds.get(k)=="code") ...)`——沒給 `--finding-kind` 時把「不知道是不是 code 型」當成「就是 code 型」處理,precision 卻仍標成 `"finding"`(逐條高信心),跟五節「代碼審只收 code 型」的敘述及「沒給就退回輪級並標 round」的對稱處置矛盾;規格只講了「沒給 severity 退回輪級」,沒講「給了 severity 卻沒給 kind」這個組合。
引句:「逐條嚴重度走新的 `--finding-severity`;沒給就退回「輪級 major 且任一條 code」並在逃逸帳標 `precision: round`」
file: `scripts/lumos:6198-6207`。

**F4**
severity: major
blocking: 是(「紅」的判準是雙向門放行/擋下的關鍵閘,規則模糊會讓實作者自己猜)
spec 四、新閘(「紅」的判準)
問題:規格稱「借 [[Systems/bound-tests-gate]] 的做法」,但被借的 `_run_bound_tests`/`_ran_evidence_check`(scripts/lumos:25801-25852)只做「有沒有證據跑過」的布林判斷,不數「幾支」,也不分辨 pytest 的「1 failed, 1 passed」與 unittest 的「Ran 2 tests」;規格閘要求「恰好跑到 1 支」比被借對象更嚴,卻沒有給任何跨框架計數規則。
引句:「看測試工具說「跑了幾支」,恰好跑到 1 支且失敗才算紅」
file: `scripts/lumos:25818-25852`(`_run_bound_tests` 無計數邏輯,只有 `_ran_evidence_check` 布林判斷)。

**F5**
severity: major
blocking: 否(方向是失敗安全——誤判只會多擋、不會少擋;但會造成規格閘幾乎每次動計劃就要整批重驗)
spec 四、新閘(留痕過期)
問題:過期比對用整份計劃檔 sha256;CLAUDE.md 鐵則要求開頭欄位改動一律走 `lumos set`/`append`(含常態性的 `updated:` 挪動),任何一次無關條款內容的欄位維護都會讓既有 spec-gate 留痕變「過期」,逼著重跑全部綁定測試——規格沒有排除只 hash 條款區塊的做法,也沒評估這個常態摩擦成本。
引句:「留痕記的計劃 sha256 跟現況不同 → 擋下印「規格閘留痕過期,重跑 `lumos spec-gate`」」

**F6**
severity: minor
blocking: 否(失敗方向是拒收/擋下,不會讓不合格的 keeps 矇混過關;只是會誤拒真正夠格的測試)
spec 三、綁定規則(keeps 既存性)
問題:`git log -S"def <測試名>" --diff-filter=A --format=%ad` 抓「首次出現日期」在 squash/rebase 過的歷史裡會被重寫成 squash 當下,或測試改過名字時「這個確切名字」首次出現的日期晚於邏輯真正存在的日期,兩種情況都可能把老測試誤判成「晚於計劃建立」;規格沒交代,也沒交代 `git log` 對還沒提交(worktree 未提交)的 keeps 測試回傳空結果時該怎麼判(擋下?當作不合格?)。
引句:「`git log -S"def <測試名>" --diff-filter=A --format=%ad` 的首次出現日期 < 計劃 `created`」

**F7**
severity: minor
blocking: 否(失敗方向安全:未被承認的清單前綴會讓該行照掃或照樣算缺類,兩種結果都不會讓風險被洗白,只會多擋)
spec 一、門怎麼判(`_excluded_line`)
問題:清單前綴只列 `-`/`*`/`數字.` 三種,markdown 常見的「1)」寫法、tab 縮排、雙層引用「> >」沒被列舉為明確等價形式;若真按字面實作,這些變體寫的合格「已排除」行會被判成不合格,連帶讓門白白判成單向(不是洩露而是誤擋,但規格自己在 r2 才因為「縮排/引用塊/全形冒號變體」的理由改過一次,這裡漏列的變體同一類坑還在)。
引句:「去掉行首空白、清單前綴(`-`/`*`/`數字.`)與引用符 `>` 再比」

**F8**
severity: blocker
blocking: 是(規格聲稱只有「一條文法」機械判定條款合不合格,但該文法定義本身不含 `[keeps]`,而 S6/S7/S25 又都依賴 `[keeps]` 判定——文法定義與實際使用互相矛盾)
spec 二、條款句式(形式文法)+ 三、綁定規則(keeps 標記解析)
問題:section 二給出的正式文法「定義行 = "- [S<n>] " 觸發子句? 主體 "應" 回應 " [test:…]"」完全沒有 `[keeps]` 的位置;section 三卻說 `[keeps]` 收進 `[test:]`/`[manual:]` 同一個標記家族 `INV_TAG_RE` 解析、且可以「在同一定義行任意位置」出現——但目前 `INV_TAG_RE` 的正則只有 `test|audit|kill|src|git` 與 `manual` 分支,沒有 `keeps` 這個裸標籤的分支,「同一個標記家族」這句話對照現有程式碼是假的,而「要動什麼」表也沒列出要改 `INV_TAG_RE`。
引句:「收進 `[test:]`/`[manual:]` 同一個標記家族(`INV_TAG_RE`)解析」
file: `scripts/lumos:3408`(`INV_TAG_RE = re.compile(r"\[(?:(?:test|audit|kill|src|git):\s*[^\]]+|manual:\s*[^\]]*)\]")`,無 `keeps` 分支)。

## 已核對、判「無 finding」的邊角問題(逐項交代)

- **`push-gate-unreviewed` 舊帳冒號版本讀側**:無。該路徑要求「該計劃有雙向門留痕」,而 spec-gate 從未落地,所以在 d10(冒號版)存續期間這個分支必然是恆為零筆(spec 自己 line 197 也這樣講),已用 `grep push-gate docs/.escape-log.jsonl` 核對現況只有一筆 `code-loop` 逃逸、零筆 `push-gate` 系列,不存在需要相容的舊冒號列。
- **停用詞「當然」後面接真觸發子句(如「當然,當方案啟用時,應退回」)**:無。文法把「觸發子句」設為 optional,停用詞覆寫只影響五型「名字」歸類(僅供人讀),不影響格式合不合格、也不影響測試綁定判準,所以誤分類不會造成靜默放行或擋死。
- **`created` 欄位是 NFD 日期字串**:無。`created` 值域是 ISO 日期字串(如 `2026-09-17`),純 ASCII 數字與連字號,不含可被 NFC/NFD 正規化影響的字元。
- **`_ci_step_is_test` 大小寫、`"tests/"`**:無。`.lower()` 處理大小寫;`re.split(r"[^a-z0-9]+", ...)` 對 `"tests/"` 這種帶路徑分隔符的字串會正確切出 `tests` 這個詞,不受影響——中文步驟名那條路才是真的破口,已列 F2。

## 固定席節點:是否破壞其宣稱行為

- **Systems/design-loop(★INVARIANT★)**:不影響。r3 只是把處置閘第五步改成呼叫同一支條款檢查器並多帶 `door` 參數,S8 的新文字草稿(spec 四節)仍保留「[SN] 定義行要合文法、綁 `[test:]`(單向門可 `[manual:≥4 字]`)」,原合約要求的「有 [SN] 時任一條款要綁定測試」被沿用且加嚴(雙向門禁 manual),沒有削弱。
- **Systems/bound-tests-gate(★INVARIANT★)**:不影響。規格閘的「紅」判準是借用同精神但走自己的跑測流程(spec 四節),不改動 `_run_bound_tests`/`_bound_tests_check` 本身的 rc 判定邏輯。
- **Issues/code-loop守衛main-direct盲區**:不影響。本案沒有觸及 main 直推繞過守衛的既有機制。
- **Systems/anchor-integrity(★RISK★)**:不影響(已自行處理)。spec 進度節已明講改了 `scripts/hooks/pre-push` 會讓 `lumos anchor verify` 翻紅,推送前要先 `anchor approve`,自己承認並排進流程。
- **Systems/每支檔有家**:不影響。`lands_in` 已列 `Systems/design-loop`、新開 `Systems/規格閘`,涵蓋提到的 `scripts/lumos`、`scripts/hooks/pre-push`、`scripts/test_lumos.py`。
- **Systems/canary-audit(★INVARIANT★ ×2)**:不影響。spec 明講擴充 `cmd_canary` 的 kind 列舉、不准繞過既有寫入口(`_jsonl_append_verified` 沿用),readback 驗證機制不變;second/telemetry 那條跟 `spec-gate` 無關聯。
- **Systems/guard-kill(★INVARIANT★ ×2)**:不影響。規格閘的「不收弱證據」是借鑑同精神,不是改動 guard kill 本身的 rc 優先序或 `--json` 輸出邏輯。
- **Systems/lumos-cli-lifecycle(★INVARIANT★)**:不影響。spec 只提到模板改了要在本 repo 跑 `lumos update`,這是使用既有 re-inject 機制,不是修改它。

## 結論

最嚴重 severity:**blocker**
blocking 計數:**4 條**(F1、F2、F3、F8)
