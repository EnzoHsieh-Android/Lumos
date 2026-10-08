severity: clean

# 資安-sonnet 第 1 輪:無 finding

已看,無(逐類):
1. 注入:掛鉤呼叫 `"$PY" "$GRAPHCTL" drift check --diff "$_rsha..$_lsha" --repo "$REPO_ROOT"` 全部加引號、無 eval、無字串拼命令;_rsha/_lsha 是 git 從 stdin 給的 40 位十六進位提交編號,ref 名與分支名根本沒進這條指令。CI 那步把 github.event.before 與 github.sha 走 `env:` 再以 "$BEFORE"、"$SHA" 引用,沒有把 `${{ }}` 直接拼進 run:;github.sha、event.before 都不是攻擊者可任意塞字串的欄位(head_ref、分支名、提交訊息皆未用)。
2. 權限/執行不可信位置:CI 觸發是 push(僅 main)與 pull_request,不是 pull_request_target;新步驟本身 `if: github.event_name == 'push'`,只在合併後的主線推送跑。掛鉤跑的 `$REPO_ROOT/scripts/lumos` 沿用既有信任模型(同支掛鉤其他閘已如此),本 diff 未新增執行位置。drift 模式從被推送頂端提交的 .lumos/config.json 讀,送 PR 的人可在自己分支把 gate 寫成 off,但那是本機推送自己的分支,且 CI 只在主線 push 跑、內容已過人審;無新增權限提升(推論,不成 finding)。
3. 密鑰與個資:新增輸出只有提示文字與提交編號範圍,無 token/環境變數進 log;CI 步驟只有 BEFORE、SHA 兩個 env。
4. 加密:無涉。
5. 執行邊界:LUMOS_SKIP_DRIFT_CHECK 只認 "1"、由環境變數控制、留帳,屬設計內的本機逃生口,CI 不吃這個變數(工具內註明 CI 照查)。rc 非 0/1 放行為設計(同其他閘),非新增繞過面。
6. 行動端:無涉。

本席無 finding,所以沒有引句。

最高等級:clean
