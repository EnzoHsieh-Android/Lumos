severity: minor

## Z1 關簽章顯示逐呼叫加旗標,沒放進既有的 git 旗標釘住點
severity: minor
blocking: 否
引句:「lg = _ns_git(repo_root, "log", "--no-show-signature", "--follow",」
file: `scripts/lumos:40418`
說明:專案把「使用者 git 設定汙染輸出」的對策放在兩處:共用 helper 內(`_lens_git` 以 quote=True 統一加 `-c core.quotePath=false`,`_ns_git` 靠它,40418-40424、27486)與 diff 共用封裝(`_ns_diff` 把 `--inter-hunk-context=0` 等一次釘好,27495-27499)。這次改成在兩個呼叫點(29996、33141)各自塞 `--no-show-signature`,結構上對(旗標是 log/show 專屬,放 helper 全域不合適),但同一輪新增了兩處手寫、其他 log/show 呼叫(44335 `log -1 --date=short --format=%ad %s`、38864 `log --name-only --format=@%cs`、41933 `show -s --format=%cI`)都沒加,日後第三處容易漏。屬命名/釘法與鄰居不完全統一,非第二種結構。

## Z2 _git_commit_date 是專案第三個取提交日期的寫法
severity: minor
blocking: 否
引句:「def _git_commit_date(root, sha):」
file: `scripts/lumos:41930`
說明:既有 `_codeloop_git_ts`(41930-41936)用 `subprocess.run` 取 `%cI`、失敗回空字串;44335 用 `_lens_git` 取 `--date=short %ad`、失敗回 None;38864 內嵌 `%cs`。新函式用 `_lens_git` + `%cs` + 形狀驗證、失敗回 None。走 `_lens_git` 與 None 約定和 44335 一致,但沒有複用或擴充既有 `_codeloop_git_ts`(回傳格式不同:ISO 時間 vs 日期),且放在 `_drift_born_eval` 旁而非 git helper 群(`_lens_*`)旁。形狀驗證是新增的防禦,鄰居沒有。結構尚可,列 minor。

## 三問
1 分層與依賴方向:新函式留在 drift 區、呼叫 `_lens_git`(下層 helper),`_note_versions` 照舊經 `_ns_git`;沒有跨層直呼,方向一致。
2 命名與錯誤處理:`_git_commit_date` 與同批 `_git_log_sha_status_paths` 同為 `_git_` 前綴,但 drift 區其他函式多用 `_drift_born_*`,helper 群用 `_lens_*`/`_ns_*`,前綴略雜(見 Z2)。錯誤處理:失敗回 None、解析不認得整份回 None,與 `_ns_git`/`_lens_git` 的 None 慣例一致;`_note_versions` 對 `rows is None` 接著回 None,與其對 `lg is None` 的處理一致。簽章旗標見 Z1。
3 第二種做法:提交日期取法見 Z2(第三種);其餘無。測試的暫換模組函式再還原手法已有大量先例:scripts/test_lumos.py:45957-45963(`m._lens_git = spy` / finally 還原)、51082-51087(`m._ns_git = spy`)、54315-54347、58761-58771、66166-66171,新測試同型,一致。僅 `import re as _re` 在函式內另取別名,若檔頭已匯入 re 屬純風格,不列。

總結:不對齊共 2 條,其中 major 0 條;最高等級 minor
