severity: major

## 問 1:分層與依賴方向
結構對。新函式 `_ci_resolve_sha` 放在 `_ci_write` 與 `cmd_ci_wait` 之間(`scripts/lumos:41832`),跟 `_ci_config`(`scripts/lumos:41718`)、`_ci_list_runs`(`scripts/lumos:41752`)同在 CI 回流區段;git 呼叫用 `cmd_ci_wait` 內既有的 `_git_out` 閉包傳進去(`scripts/lumos:41881`),沒有跨層直呼。依賴方向無倒置。
引句:「    sha, sha_err = _ci_resolve_sha(_git_out, sha)」

## 問 2:命名與錯誤處理
對齊。擋下訊息用「擋下:」開頭、寫 stderr、回 rc2,跟同函式上方 `--repo-dir` 那條(`scripts/lumos:41876-41877`)同形;fail-open 的空值(取不到 HEAD)仍走原本的 unavailable(`scripts/lumos:41893` 之後)。命名 `_ci_` 前綴與同區段一致。小差異不列:sha_err 沒像 `--repo-dir` 那條走 emit,但 `--repo-dir` 那條也沒走,兩者一致。
引句:「        return None, f"擋下:--sha {sha!r} 在本機找不到對應的提交——給完整 40 碼 sha,或先 git fetch"」

## 問 3:第二種做法
有重複,見 F1、F2。

## F1 新增 _ci_resolve_sha 與既有 _lens_full_sha 是同一件事的第二種寫法
severity: major
blocking: 是
說明:`_lens_full_sha`(`scripts/lumos:44180-44185`)已經是「rev 換完整 commit sha、找不到回 None」,內容逐字同一條 git 指令(`rev-parse --verify -q --end-of-options <rev>^{commit}`),連「以 - 開頭不當旗標」的註解都有。專案裡約 30 處都走它(例 `scripts/lumos:44112`、`:39404`)。新函式把同一條指令重寫一遍,只是經由 `_git_out` 閉包呼叫。`cmd_ci_wait` 內已有 `root`,直接 `_lens_full_sha(root, sha)` 即可;不用它的理由(`_git_out` 的 30 秒逾時與 fail-open)`_lens_git` 也有(`scripts/lumos:44176` 一帶回 None)。
引句:「    full = git_out("rev-parse", "--verify", "-q", "--end-of-options", f"{sha}^{{commit}}")」

## F2 新增 _CI_FULL_SHA_RE 與既有 _LENS_SHA_RE 重複
severity: major
blocking: 否
說明:`_LENS_SHA_RE`(`scripts/lumos:43927`)就是 40 碼或 64 碼小寫十六進位,新正規式語意相同(一個用 `^…$` 加 match、一個用 fullmatch)。同檔還有 `_ZERO_SHA_RE`(`scripts/lumos:43957`)也是 40|64 兩形狀,既有慣例是一個形狀常數到處用。新增第二個、命名還叫 FULL,日後改形狀(例如接受大寫)會漏改。若採 F1 用 `_lens_full_sha`,這個常數與 `_ci_resolve_sha` 可一併刪掉,只剩「給的已是完整就原樣用、否則換」那幾行,直接用 `_LENS_SHA_RE.fullmatch`。注意 `_LENS_SHA_RE` 定義在檔案後段(`:43927`),但函式內執行期才查,模組載入完成後可用,無順序問題。
引句:「_CI_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")」

## Issue 筆記對照(正文反引號裡的測試名沒人查.md)
一致。摘要用 FLAG:TECHNICAL、KEY(現象)、DECISION(Enzo 裁定先不做,帶日期)、FACT(帶 [來源:] [confirmed:],與同類 FACT 寫法相同)、正文末尾一行 `REVISIT:日期 一句要做什麼`,跟 Issues 目錄既有 REVISIT 行同形。無 priority 標籤,目錄 112 篇只有 21 篇有,不算偏離。FACT 的 [來源:外部] 是 rtb 量測,語意稍勉強,但在可接受範圍,不列。
引句:「REVISIT:2026-12-31 再量一次 rtb 與本工具鏈圖譜:Systems 正文裡指不到的反引號測試名,排除同行有撤除字樣與 WHY/PITFALL 行之後,若真過期的佔多數就做縮小版(只列不擋);否則改評估「測試改名或刪除時列出筆記裡的舊名」這個方向。」

## 家節點(CI回流開場提醒.md)
一支檔多個家的寫法:responsibility 寫了負責範圍與「scripts/lumos 只管 cmd_ci_wait、cmd_ci_status 與它們的輔助函式」,about_code 加 `scripts/lumos`,與專案「節點寫負責範圍」的慣例一致;新增的 `_ci_resolve_sha` 屬於「輔助函式」,範圍涵蓋。不列。

不對齊共 2 條,其中 major 2 條
