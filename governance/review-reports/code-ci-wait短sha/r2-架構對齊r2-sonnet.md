severity: minor

## F1 同一函式內兩條 git 路徑(git_out 與 _lens_git)
severity: minor
blocking: 否
引句:「        return (git_out("rev-parse", "HEAD") or None), None」
說明:取 HEAD 走 cmd_ci_wait 自己的 `_git_out`(`scripts/lumos:41884` 一帶的閉包,fail-open 回空字串),換短碼走 `_lens_full_sha`(`scripts/lumos:44179`,底層 `_lens_git`)。同一支輔助函式裡 git 呼叫分兩條路。專案其他地方取 HEAD 都是 `_lens_full_sha(root, "HEAD")`(如 `scripts/lumos:28934`、`scripts/lumos:29904`)。結構仍在同層、沒有跨層直呼,所以只算 minor;若是為了保留「取不到 HEAD 照舊判 unavailable」的行為,屬刻意,⚠ 交編排者定奪。

## 三問

1. 分層與依賴方向:`_ci_resolve_sha` 只呼叫既有 `_LENS_SHA_RE`(`scripts/lumos:43926`)與 `_lens_full_sha`(`scripts/lumos:44179`),不再自寫 rev-parse 與正規式,上輪的重複已除;依賴方向 ci 區塊往 lens 共用工具走,與 `scripts/lumos:28934` 等既有呼叫同向(模組層級後定義、執行期才解析,`scripts/lumos:32793` 等也是同樣排法)。引句:「    full = _lens_full_sha(root, sha)」
2. 命名與錯誤處理:`_ci_` 前綴、錯誤以「擋下:…」寫 stderr 並 rc2,與同函式的 `擋下:--repo-dir 指的目錄不存在`(`scripts/lumos:41875`)一致;回 None 時錯誤訊息涵蓋「本機沒有、短碼不唯一、git 跑不起來」三種,其他 `_lens_full_sha` 呼叫端多半只是靜默 None 或各自報錯,這裡報得更細但不衝突。`(值, 錯誤)` 二元組回傳有先例(`scripts/lumos:44003` 的 `(sha, False)`)。見 F1 的 git 路徑分歧。引句:「        return None, (f"擋下:--sha {sha!r} 換不成完整的提交編號——本機沒有這個提交(先 git fetch)、短碼對到不只一個提交"」
3. 第二種做法:沒有。短碼換完整碼、完整 sha 形狀判斷都只剩既有那兩支;完整 40/64 碼直接放行不驗存在,與原行為一致。唯一的分歧是 F1。引句:「    if _LENS_SHA_RE.match(sha):」

不對齊共 1 條,其中 major 0 條
