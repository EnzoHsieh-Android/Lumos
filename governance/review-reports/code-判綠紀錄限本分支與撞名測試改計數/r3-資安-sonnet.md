severity: minor

我讀完整份 r3 patch,並在 repo 與臨時目錄查證了下面的點。沒有 major 或 blocker。有兩條 minor,都不阻擋。

1. 設定裡只寫裸鍵 `promisor`(沒有 `= true`)時,`_git_partial_clone` 判成非部分複製,過濾照樣去問 git
severity: minor
blocking: 否
引句:「        if key.endswith(".promisor") and val not in ("true", "yes", "on", "1"):」
- 這條屬類別③,但是推論。誰是使用者本人,或手改過設定檔的 AI。從哪是 `lumos spec-gate` 進到 `_redbase_on_branch`,或推送閘走到 `_drift_born_env_err`。送什麼是 `.git/config` 的 `[remote "origin"]` 下只寫一行 `promisor`。拿到什麼是部分複製的守衛被意外走過,git 會自動去連遠端抓。
- 我在 git 2.39.2 實測了兩件事。`git config --get-regexp` 對裸鍵只印 `remote.origin.promisor`,沒有值,所以 `val` 是空字串,被 `continue` 略過,函式回 False。同一個設定加上 `remote.origin.uploadpack` 指向留記號的腳本後,`cat-file -e` 查一個不存在的提交,記號出現了,也就是 git 確實去連了遠端。
- 影響只有「為了判祖先去連使用者自己設的遠端」,不是任意碼執行,而且要手寫裸鍵才會發生。`git clone --filter` 寫的是 `promisor = true`,走正常流程不會中。
- 反方向也有一處:遠端名含空白時,`partition(" ")` 切錯,`if val: return True` 會誤判成部分複製。這是偏安全的一邊。
- 另有一個類似處:`_git_partial_clone` 回 None(git config 逾時或回傳碼不是 0 或 1)時,`_drift_born_env_err` 裡的 `if _git_partial_clone(root):` 把 None 當成「不是部分複製」。舊寫法也是如此,所以不是這輪新增的退步。`repo_kind()` 則把 None 當 "unknown" 而照留,兩處方向不一致。

2. 治理帳被忽略時,判綠紀錄的過濾遇到 amend、rebase 或 `git branch -m` 會把自己的判綠丟掉,「判綠過不存紅燈版」的保護變鬆
severity: minor
blocking: 否
引句:「 判綠過的、逾時紅的不存(治理帳被 git 忽略的專案,壓過或 rebase 過的分支上舊的判綠紀錄不算)」
- 這條屬類別③。誰是照常操作的使用者或 AI。從哪是判綠後跑一次 `git commit --amend`、rebase 壓提交,或 `git branch -m`。送什麼是普通的 git 指令。拿到什麼是原判綠紀錄的 head_sha 不再是祖先,或分支名對不上,`_redbase_on_branch` 把它丟掉。之後同一支測試再判紅時,會把實作後那一版存成紅燈版,比對作弊的起點因此變弱。
- 計劃的「天花板一」和「天花板一的代價補一句」已寫明這點,`_TG_LIMITS` 與測試品質標準也同步列了,所以只當縱深提醒。治理帳進版控的專案走 `ignored != "ignored"` 那條,不受影響,測試 S7 也釘住了這點。

三類查核:

① 提示注入:已看,無。
- 分支名先過 `_note_reread_branch` 到 `_note_reread_show` 清洗:控制字元、U+2028 和 U+2029、雙向覆寫換成空格,並截到 1000 字。再以 `ref` 欄位寫進治理帳,寫入用 `json.dumps`。
- 讀取端對 `ref` 只做字串相等比對,沒有拼進派工詞、hook 附加段或指令。
- 新增的 stderr 訊息只印筆數和常數,沒有外來文字。
- 我查了 `_codeloop_read_from_ledger`:它要 `gate == "code-loop"` 且 `kind` 在白名單才算數,新加了 `ref` 的 spec-gate 事件不會被誤當成代碼審通過的留痕。

② 讀寫與執行越界:已看,無。
- 傳給 git 的 `head_sha` 來自帳本內容,先過 `_LENS_SHA_RE.fullmatch`(40 或 64 位十六進位),所以不會被當成旗標,`cat-file -e <sha>^{commit}` 也不會被注入。
- `_git_partial_clone` 的正規式是常數,用 `_lens_git_dl` 傳 argv 列表,沒有 shell 插值。
- 沒有新的寫檔路徑,只多了治理帳一個既有欄位。
- 測試把 `remote.origin.uploadpack` 設成臨時目錄裡的 `#!/bin/sh` 腳本,只設在測試自己複製出來的 repo,內容是 `touch '{mark}'; exit 1`,不連網。`mark` 路徑來自測試臨時目錄,不是外部輸入,沒有越界。
- 新增內容沒有密鑰或真實信箱,只有 `t@t` 這類假值。
- 沒有安裝腳本、下載網址或環境變數覆蓋的改動。

③ 非刻意一步繞過:見上面兩條。
- 此外我沒有找到新的 `LUMOS_SKIP_*`,或讀 `PYTHONPATH` 的路徑。
- 過濾只在 `_gov_ledger_ignored` 回 "ignored" 時才啟動,判不了時整批照舊算,方向與過濾前一致。

另外順帶一提:測試新增的 `git checkout -f`、`branch -D` 等都用 `git -C <fixture>`,與既有測試同一寫法;若外層帶入 `GIT_DIR`,既有測試也有同樣的風險。這不是這份 diff 新增的,我沒有實測。

臨時目錄 `/tmp/lumos-seat-work/code-判綠紀錄限本分支與撞名測試改計數/資安-sonnet` 已用字面路徑刪除。

最嚴重等級是 minor,blocking 共 0 條。
