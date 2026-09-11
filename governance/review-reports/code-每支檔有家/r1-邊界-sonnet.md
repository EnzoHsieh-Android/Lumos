severity: major
# 審查報告

severity: major

### F1 `home check --diff` 三點語法(git 最常見的比較慣用寫法)被靜默吞掉,新違規完全不擋
severity: major
blocking: 是 — 用最常見的三點差異語法呼叫時,gate 從「擋下」變成「找不到,跳過」,真違規完全漏放行(已用兩個分支實測對照)
引句:「a, b = diff_range.split("..", 1)」
1. `--diff` 只驗證字串裡「有沒有 `..`」,沒驗證是不是恰好兩個點;`split("..", 1)` 只切第一個 `..`,遇到三點語法(`main...feature`,git 裡比較兩分支差異的標準寫法)會把第三個點吃進終點字串,變成 `.feature` 這種不存在的 ref。
2. 實測對照:同一個分支(新增一支沒有家的 `scripts/orphan.py`)用 `home check --diff "main..feature"`(兩點)正確印出「擋下:…新違規」、rc=1;換成 `home check --diff "main...feature"`(三點)卻印「每支檔有家:範圍 main...feature 在本機找不到,跳過(fail-open)」、rc=0,同一條違規完全沒被擋到。
3. 目前兩支 hook 自己組出來的範圍固定是兩點,不會踩到;但 `lumos home check --diff` 是公開指令(argparse 有註冊、有 `help=` 說明),任何人或日後的自動化直接照 git 直覺打三點就會讓這道剛上線的擋失效卻看不出是打錯語法。

### F2 doctor 健檢 S8→S9→S10 三段之間漏了空行,跟同一支輸出裡其餘每段的間隔慣例不一致
severity: minor
blocking: 否 — 純輸出格式問題,不影響任何 rc 或判定邏輯
引句:「section("S9", "節點有沒有用反引號寫別人的檔(提醒,不擋;新寫進去的由提交前檢查擋)")」
1. `section("S8", …)`…`section("S9", …)`…`section("S10", …)` 之間都沒有呼叫 `print()`,而同一支 `run_doctor` 裡其餘每一段(S2~S7、H 之前等)結束都固定 `print()` 空一行才進下一段。
2. 本機實跑 `lumos doctor`(用本次 patch 過的 `scripts/lumos`)確認 `[S8]`/`[S9]`/`[S10]` 的輸出確實黏在一起無空行,前後鄰接的 `[S7]`、`[H]` 都有空行分隔,是同一份輸出裡的內部不一致。

### F3 「有 N 個家」的提醒訊息叫人去查「計劃的 lands_in」,但 lands_in 是完全不同語意的欄位
severity: minor
blocking: 否 — 只是提示文字誤導,不影響擋/不擋
引句:「有 {len(hs)} 個家,落點請照計劃寫的(lands_in)。」
1. `lands_in` 是 Projects 計劃節點自己的落點欄位(給 `_disposal_landing_step`/[S21] 審的「這份計劃的現況該寫進哪篇」),跟「這支程式檔同時被好幾篇 Systems 節點的 about_code 認領、現在該挑哪篇當家」是不同問題。
2. 觸發這條訊息時(`nudge-many`)程式完全沒有把「這支檔案」跟「哪一份計劃」關聯起來,使用者收到「照計劃寫的 lands_in」這句提示時很可能根本沒有對應計劃可查,是拿了別的功能的詞彙硬套在這裡。

總結:最高 severity major,blocking 共 1 條
