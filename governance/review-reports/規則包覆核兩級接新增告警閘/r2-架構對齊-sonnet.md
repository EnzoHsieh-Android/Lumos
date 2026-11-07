severity: major

## 1. 分層與依賴方向
做 5 與做 6 的方向大致對齊,但做 6 有一處會逼出跨層直呼。

- 做 5 改的是 `_lint_wt_allow`。它屬於收工白名單層,現況已會讀 `_kt_toolchain_root()` 和 `configs/ast-grep/` 路徑,所以多認兩個規則包檔名,不算新增跨層依賴。對照:`scripts/lumos:41184` 到 `41280`。
- 做 6 把「放行檔」讀進 pitfalls 的 lint 收集。既有的讀法在新增告警閘那一層(`_lint_waivers_load`,`scripts/lumos:42886`)。`_pitfall_diff_collect` 已經在呼叫 `_lint_run_and_parse`、`_lint_gate_covers` 這類 lint 層函式(`:65182-65197`),所以呼叫 `_lint_waivers_load` 方向同向,不算違規。
- 問題在指紋的算法(見 F1):既有的 sha256 截 16 碼寫在 `_lint_new_diff_claims` 裡面,不在 `_lint_new_key`,pitfalls 這邊要自己重算一次。

## 2. 命名與錯誤處理
- 放行檔讀不了時,計劃寫「照舊全算」。既有新增告警閘是歸進「環境不可用」,有候選就擋下,不記自動放行(`:41571-41574`,`:42890-42893` 的 docstring)。pitfalls 這邊是只影響分級,不是放行閘,所以「全算」是保守方向,結構上沒問題。
- 但計劃沒寫放行檔讀不了時要不要印一句話。既有慣例是回傳錯誤訊息讓呼叫端顯示。這是小不一致(F3)。
- 做 5 的拒絕原因,計劃只寫「回『不在工作樹模式自動執行』」。既有每個拒絕分支都是 `return None, "<具體原因>"`,例如 `:41278` 的「--config 的真實路徑不在工具鏈的 configs/ast-grep/ 底下」。拒絕訊息要落在這個二元組格式,並寫出是哪個檔被排除,否則 `wt_rejected` 的 `why` 欄位會變成泛泛一句。

## 3. 第二種做法
- F1(major):做 6 的指紋。計劃寫「用新增告警閘同一支 `_lint_new_key` 算」,但 `_lint_new_key` 回傳的是原始字串,不是放行檔裡存的指紋。放行檔存的是 `sha256(k)[:16]`,這一步只在 `_lint_new_diff_claims` 內聯(`:42850-42880`)。pitfalls 的 claims 沒有 `key` 欄位,也沒有 `text_by_file`。要比對放行檔,pitfalls 這邊就得自己重寫「讀 head 檔文字、`_lint_new_key`、sha256 截 16 碼」,等於另寫一套。正確做法是把那段抽成共用函式,新增告警閘和 pitfalls 都呼叫它。計劃要明寫「抽出共用函式」,而不是「用同一支」。
- F2(minor):做 5 用兩個檔名的黑名單。`_lint_wt_allow` 現況是白名單:只認 `configs/ast-grep/` 底下的真實路徑。做 5 另加兩個檔名黑名單,是同一函式裡的第二種判斷風格。若有人複製一份 `sgconfig-hints.yml` 改名,或另建一個設定檔,黑名單擋不住。與白名單一致的做法,是把准許範圍收到 `sgconfig.yml`,或把「收工可跑」寫成設定檔旁的宣告。計劃要說明為什麼選黑名單,否則下個人會當成不一致來改。
- F3(minor):pitfalls 已有一套「這筆 lint 命中推送閘是否接得住」的標記,`_push_gate_covers`(`:65197`,`:65229`),用 `c.pop` 清掉內部標記後才外流(`:65232`)。做 6 該沿用「加內部標記、分級前過濾、輸出前清掉」這個形狀,而不是另開 `_tier_claims` 的第三條過濾分支。計劃沒寫放行過濾放在哪一步。還有一點必須明寫:`all_claims` 照樣列出放行過的命中,只有分級用的 `_tier_claims` 不算。

## 4. 落點
- `lands_in` 只有 `Systems/kotlin規則包` 與 `Systems/linter精選目錄`。做 5、做 6 改的函式不在這兩篇的家裡。
- 做 5 動的是 `_lint_wt_allow`。我用 grep 找到它的家是 `Systems/回合結束寫法檢查`。
- 做 6 動的是 `_pitfall_diff_collect` 和 `_pitfall_tier` 一帶,另外可能新增共用指紋函式(F1)。我 grep `docs/` 沒找到管這幾個符號的節點,⚠ 判不準它們的家是哪篇,推測是 `Systems/pitfalls-code-loop`。
- 依鐵則 5(改到的每支檔要先有家、說明寫進改到那支檔的家),`lands_in` 應補上這幾篇家節點,否則做 5、做 6 的說明沒地方落。
- 另外,`Systems/linter精選目錄` 現況「沒寫負責範圍」,管 1 支檔。做 4 要改它的範本,而它的負責範圍是空的。這篇節點本身也要補,不然改範本時 lint 會唸。

不對齊共 3 條

## F1 做 6 的指紋要另寫一套 sha256 截斷
severity: major
blocking: 是
引句:「指紋(用新增告警閘同一支 `_lint_new_key` 算)在放行檔裡的不算進分級」
file: `scripts/lumos:42830-42846`、`scripts/lumos:42869-42880`

## F2 做 5 用檔名黑名單,既有函式是路徑白名單
severity: minor
blocking: 否
引句:「`scripts/lumos` 的 `_lint_wt_allow` 對 `--config` 值是規則包 `sgconfig-review.yml` 或 `sgconfig-hints.yml` 的命令回「不在工作樹模式自動執行」」
file: `scripts/lumos:41258-41276`

## F3 做 6 沒說放行過濾要沿用 `_push_gate_covers` 的標記形狀,也沒說放行檔讀不了時要不要印訊息
severity: minor
blocking: 否
引句:「放行檔讀不了就照舊全算。這條對所有 lint 宣告都成立,不只覆核兩級。」
file: `scripts/lumos:65197`、`scripts/lumos:65229-65233`
