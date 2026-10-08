severity: clean

# 推送閘接漂移檢查 第 2 輪 資安-sonnet 席

沒有 finding。逐類結果如下。

## 六類逐項

1. 注入:已看,無。
   - 掛鉤裡的遠端名 `$1` 只在 `pp_mainline` 拼成 `refs/remotes/$_PP_REMOTE/HEAD` 這類字串,放進陣列後每次都加雙引號傳給 `git rev-parse -q --verify "$_c^{commit}"`。前面固定有 `refs/remotes/`,不會被 git 當成選項(開頭不是 `-`)。沒有 eval,也沒有未加引號的展開。
   - 遠端名就算含空白或 `..`,最壞是 rev-parse 找不到,走「找不到主線」那條,講一聲後交給 lumos 自己判。
   - 遠端名來自使用者本機 `.git/config`,clone 不會帶過來。所以「別人控制遠端名」這條攻擊路徑成立不了。
   - `_DR_RANGE` 由 git 給的 sha 與 `git merge-base` 輸出組成,以單一引號化參數傳給 `--diff`。裡面不會出現以 `-` 開頭的值。
   - CI 與健檢範本裡的 `BEFORE`、`SHA` 走 `env:`,沒有把 `${{ }}` 直接內插進 shell 本文。步驟裡全部加了引號。範本會在消費專案 CI 跑,同一段也是這樣寫的。
   - `github.event.before` 是 GitHub 產生的 sha,不是使用者可控的字串。
   - `OLD="${BEFORE:-(空的)}"` 只用在 echo,沒有進指令。
2. 權限與執行不可信位置的檔:已看,無新增。
   - 這次新加的部分沒有新增「執行工作樹裡的檔」的路徑。`$PY $GRAPHCTL` 沿用原有寫法。
   - 工具讀被推送頂端提交的 `.lumos/config.json` 決定 block/warn/off。這代表推送者能在自己的提交裡把它設成 off 來繞過。但推送者本來就能用 `--no-verify`,在自己的分支上這不算邊界。
   - CI 只在 push 事件跑,不跑 fork PR,所以 fork 貢獻者碰不到這一步。⚠ 推論:這一點是看 `if: github.event_name == 'push'` 得出的,我沒有另外實測 fork 情境。
3. 密鑰與個資:已看,無。步驟裡沒有印任何 token 或環境變數,只印 sha。
4. 加密:已看,無,這次不涉及。
5. 執行邊界:已看,無。
   - rc 大於等於 128 就停下掛鉤,其他非零只放行並提醒。這是可用性與正確性取捨,不是資安洞。
   - CI 對非零一律紅,是更嚴格的一邊。
6. 行動端:已看,無,這次不涉及。

圖譜鏡頭固定席判定:牽連節點裡的 INVARIANT 只有 `Systems/測試假綠形態`、`Systems/lumos-cli-lifecycle`、`Systems/lumos-cli-read` 三則。它們分別涉及「還原翻紅釘要有前置斷言」、「re-inject 只覆蓋 sentinel 之間內容」、「search 預設排除 superseded」。這份 diff 只改 pre-push 的漂移檢查範圍計算、ci.yml 一步,以及健檢範本字串。沒有動 sentinel 注入、search 排除邏輯或還原翻紅釘的測試結構,所以不影響這三則。`Issues/code-loop守衛main-direct盲區` 與其餘 [家] 節點,從資安角度沒有牽連到可被利用的行為。

最高等級:clean
