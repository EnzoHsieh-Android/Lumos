severity: clean

# 邊界-sonnet 第 3 輪報告

方法:臨時目錄 hook-r3/bnd-sonnet(clone --shared 自 clone-hook,直譯器 /opt/homebrew/bin/python3),用 importlib 直接呼叫 `_push_range_start`,並用 `lumos drift check --diff ... --push-remote ... --pushed-ref ...` 跑 CLI 確認回傳碼。沒有動 repo 根。

## 實測表(起點 = 實際算出的起點;M=主線頂端、F1=推過的分支頂端、Z=全 0)
| 輸入 | 起點 | 回傳碼/行為 |
|---|---|---|
| 遠端名 `/tmp/my repo.git`(含空白)、`https://x/y.git`(網址)、空字串 | 舊值 F1 | CLI rc0,argparse 收得下(掛鉤有加引號) |
| 遠端名以 `-` 開頭 | 不適用 | argparse rc2;掛鉤對「其他非零」放行講一句沒檢查;真實遠端名/網址不會以 - 開頭 |
| pushed_ref = refs/tags/v1、refs/heads/a/b、無前綴別名、空字串、refs/pull/1/merge | 都不跳過主線候選,舊值在就用舊值 F1 | rc0 |
| 新分支(舊值全 0)開在主線上 | M(分岔點)| rc0 |
| 舊值本機找不到(force push)/ 舊值空字串 | M(分岔點) | 空字串在 CLI 端被 `_lens_range_ok` 拒(rc2,而掛鉤永遠給 40 個 0 或 sha,CI 已換成 0) |
| 推主線本身(遠端 HEAD、main@{upstream}、origin/main 全被「就是被推那條」跳過)| 舊值 M | 增量,rc0 |
| 遠端 HEAD 指到不存在分支(懸空)| 略過該候選,改用 main@{upstream} | 正確 |
| 遠端 HEAD 是直接 sha(非捷徑)| 不跳過,但推主線時合併基底=舊值,結果一樣用舊值 | 正確 |
| 孤兒分支首推 / 孤兒增量 | 空樹(截到上線點)/ 舊值 | 說明「沒有共同祖先」,正確 |
| 舊值、新值都是 annotated tag 物件 | `^{commit}` 剝殼成提交,與提交同結果;tag 在主線上→None(沒有新東西) | rc0 |
| upstream 設在另一個遠端(fork/origin)| 名稱相同視為同一條而跳過,退回舊值 | 保守,不誤算 |
| 淺層 clone | 工具端在算範圍前就跳過 | rc0 並記 skipped-env |
| GITHUB_REF 是 refs/pull/…/merge | CI 只在 push 事件跑且 ci.yml 的 push 只有 branches [main],實際不會出現;餵進去也不跳過候選、正常算 | rc0 |
| before 空字串 | CI shell 換成 40 個 0;工具端直接給 `..sha` 則 rc2 | 符合預期 |

## Finding
無。

備註(不構成 finding,沒有具體失敗場景):
1. pushed_ref 若是空字串又推主線,origin/main 不會被跳過而判成「頂端已在主線、沒有新東西」;但掛鉤的 `_rref` 與 CI 的 `GITHUB_REF` 在 push 事件恆有值,只有手動呼叫才會走到。
2. 跳過主線候選只比分支短名、不比遠端(fork 流程推 `origin main`)——結果是退回舊值,不會多算也不會漏算。

## 圖譜鏡頭逐條判定
- Issues/code-loop守衛main-direct盲區、Systems/存量漂移守衛、每支檔有家、筆記內容閘、anchor-integrity:掛鉤只新增漂移檢查一段與 `pp_stop_if_signaled`,其他閘的呼叫與 rc1 擋的語意不變;新增的起點邏輯在工具端一處,實測不影響這幾道閘的範圍。不影響。
- Systems/測試假綠形態 ★INVARIANT★(還原翻紅釘要有前置斷言):這次未見新增「修 bug 的還原釘」被我審到的失敗;本席只做輸入實測,對該合約不判破壞。不影響。
- lumos-cli-lifecycle / lumos-cli-read 的 INVARIANT(re-inject byte-equal、search 排除 superseded):diff 不碰這兩條行為。不影響。

最高等級:clean
