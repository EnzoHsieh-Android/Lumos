severity: minor

## 發現

### 1. 本工作目錄沒有同名 hook 時,說明寫成「內容不同」
severity: minor
blocking: 否
引句:「                same = ok and f.is_file() and _same_bytes(f, eff)」
file: `scripts/lumos:26022`
- 輸入:附加工作樹的 `scripts/hooks/` 不存在或沒有 `pre-commit` / `pre-push`。例如 hooks 沒進版控,或工作樹裡被刪掉。同時 `core.hooksPath` 指向主工作目錄那份,且那份可執行。
- 路徑:`ok` 為 True,`f.is_file()` 為 False,所以 `same` 為 False,走到 `add(layer, "degraded", … "本工作目錄的 {fn} 跟它不同,推送時跑的不是這份")`。
- 我實測重現:刪掉工作樹的 `scripts/hooks` 後,兩列都印 `degraded … 本工作目錄的 pre-commit 跟它不同`。
- 壞在哪:「缺」被說成「不同」。更根本的是,推送時跑的本來就是生效的那份,工作樹沒有同名檔並不代表防護有問題。這裡的 degraded 是誤報,實際生效的防護是好的。
- 最小重現:見上面實測。`t_hooks_path_sibling_worktree` 沒有涵蓋這個情境。

### 2. 「同一個 repo 的另一個工作目錄」沒有檢查那是不是工作目錄的根
severity: minor
blocking: 否
引句:「    other = vp.parent.parent」
file: `scripts/lumos:22054`
- 輸入:`core.hooksPath` 指向同 repo 內的子目錄,例如 `<main>/sub/scripts/hooks`。
- 路徑:`other = <main>/sub`,`git -C` 在 repo 內,所以 `--git-common-dir` 與本工作樹相同,函式回傳 `vp`。
- 實測:兩列印 `active … 生效的是同 repo 另一個工作目錄那份 …/main/sub/scripts/hooks/pre-commit`。
- 壞在哪:那個子目錄不是工作目錄,說明文字不準確。git 實際上確實會跑那份 hook,所以狀態本身沒錯。這是描述不準,不是安全洞,所以只列 minor。
- 其他情況我走過一遍,結果都符合預期:
  - 另一個 clone、不同 common dir:回 None,維持 inactive。
  - symlink:兩邊都做了 `resolve()`,比對一致。
  - 舊版 git 不支援 `--path-format`:rc 非 0,回 None,退回原行為。

## 逐項檢查結果(沒有 finding)
- **例外與 None**:`_common` 把例外與逾時都接成 None,`_same_bytes` 接 `OSError`。`hp` 為空時 `_hooks_path_dir` 回 None,在 subprocess 之前就返回。
- **唯讀**:整段沒有任何寫入。
- **新舊互讀**:`_enforcement_prepush_gated` 傳入的 `hp` 是共用設定值,`_enforcement_prepush_ungated` 讀的是 `hp` 指的那份 pre-push,也就是實際生效的那份,判斷正確。
- **狀態消費端**:`enforcement_status` 只被 `cmd_enforcement` 消費,沒有開場提醒或治理帳讀它。`enforcement_summary` 只數 active,degraded 留在分母裡。這兩列原本就是 inactive,分母不變,分子至多多算 active。
- **開場時間**:只有 `hp` 非空且不是自己時才多跑 2 次 git,每次逾時上限 10 秒,正常是毫秒級。在主工作目錄,以及 `hp` 指向自己的情況,都不會多跑。
- **CRLF 與權限位**:比對是純位元組,CRLF 不同會報 degraded,這是正確的,因為 git 實際跑的內容確實不同。權限位不比對,但 `os.access(X_OK)` 檢查的是生效那份。hook 是 symlink 時 `read_bytes` 與 `is_file` 都會跟隨,行為一致。
- **測試品質**:舊實作下 `" active"` 的斷言會翻紅。「指向無關 repo」那條在拿掉 common-dir 比對的變體下也會翻紅,所以不是「永遠回 True 也能過」。弱點是沒測「本工作目錄缺檔」(發現 1)與「相對路徑」。

## 圖譜鏡頭
固定席的 ★INVARIANT★ 節點逐組判定:
- `lumos-cli-read` 的 search 預設排除 superseded:不影響。diff 只動 enforcement 的 git 閘兩列,沒碰 search。
- `lumos-cli-lifecycle` 的 re-inject byte-equal 保留:不影響。沒碰 re-inject。
- `guard-kill` 的 rc 優先序與 JSON 純度:不影響。沒碰 guard kill。
- `測試假綠形態` 的「還原翻紅釘要配前置斷言」:新測試斷言 active,舊實作會翻紅。前置條件(工作樹存在、設定指向主工作目錄)由 `check` 的 active 斷言間接證明。
- `bound-tests-gate`:不影響。
- `授權與歸屬`:`_VENDORED_TOOLKIT` 與 SPDX 檔頭都沒動。
- `_hooks_path_is_ours` 刻意不放寬,所以 deinit / teardown 的安全守衛不變。
- `pitfalls-code-loop` 與 `loop-convergence-recording` 這兩個 ★RISK★ 節點,以及其餘只列名的節點:沒看到相關牽連。

## manifest
diff 內新行沒有新增告警。diff 外我沒看到新碼引入問題。

總結:最高等級 minor
