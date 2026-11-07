severity: major

審的是 r1-snapshot.patch 全份。①提示注入有 1 條可利用的洞(F1)。②③各有 1 條縱深類(F2、F3)。實跑過的:F1 在臨時目錄重現了拼接結果,F2 用真的 git 跑出 filter 觸發。

**已看,無的部分**
- `_lint_wt_allow` 白名單用「第一個詞恰為 ast-grep、第二個詞恰為 scan、--config 的 realpath 落在工具鏈 configs/ast-grep 底下、重組後每個詞 shlex.quote」。`;|&` 反引號 `$` 都被擋,`-U` 等旗標也擋。`{LINT_FILES}` 換入的是快照內的絕對路徑,且逐個 shlex.quote。這條 `shell=True` 路徑我沒找到繞法。
- `.lumos/lint.json` 要求已提交、乾淨(無修改、未追蹤或被忽略),打開陌生 repo 時不會執行沒提交的宣告。
- `_trusted_lumos`、家目錄快取目錄逐層檢查、`_name` 消毒都是從既有程式照搬,沒新增洞。
- impact-hook 的決策列來自工具鏈型錄,不是專案可控,出口經 `_plain_label` 與框。
- 密鑰與信箱:新增程式與公開文件裡沒有。
- 安裝與下載來源、環境變數覆蓋下載網址:本 diff 沒碰到。

**F1 放行指令經消毒後被拆出引號,檔名可帶 shell 指令**
- 攻擊路徑:
  - 誰:陌生 repo 的作者。
  - 從哪:收工鉤子 `_reason`,把擋下原因當成下一個提示送給 AI。
  - 送什麼:repo 裡一支 `.kt` 檔,檔名含反引號與分號(例 ``a`;touch /tmp/PWN;`.kt``),內容會觸發規則包告警,且這回合被改到。
  - 拿到什麼:`_lint_waive_cmd` 先用 `shlex.quote` 把檔名包進單引號,反引號在單引號內是安全的。`_safe_path` 再把反引號換成單引號,引號被提前閉合。
- 實跑結果:`lumos lint-waive fp1 --rule r --file 'a';touch /tmp/PWN_X;'.kt' --note "<為什麼放行>"`。擋下原因寫著「確定是誤報就照每條的放行指令補理由」,AI 照抄貼進 Bash 就會執行 `touch /tmp/PWN_X` 這段注入。
- 根因:消毒發生在引號之後,把引號字元換了。檔名來自可被攻擊者控制的 repo。
- 修法方向:放行指令不要過 `_safe_path`,或消毒完再 quote,或檔名含反引號與引號就不印放行指令。
- 引句:「lines.append(f"    放行:{sp(c.get('waive_cmd'))}")」
- file: `scripts/lumos:40526`(`_lint_waive_cmd`)
severity: major
- blocking: 是

**F2 git 防護清單沒涵蓋 clean filter,新增的 git status 照樣觸發**
- 攻擊路徑:
  - 誰:直接交給你整個目錄的人(含 `.git/config` 與 `.gitattributes`)。
  - 從哪:收工鉤子呼叫 `lint-new --worktree`,其中 `_lint_wt_git` 執行 `git status`。
  - 送什麼:`.gitattributes` 寫 `*.kt filter=evil`,`.git/config` 寫 `filter.evil.clean` 為指令,另加已提交且含 ast-grep 的 `lint.json`。
  - 拿到什麼:實測 `git status --porcelain` 對「大小相同但內容被改過」的檔會執行 clean 指令(造出 PWNED 檔)。`_harden_git_env` 只清 `core.fsmonitor` 與 `diff.external`,清不到這個。
- 補充:既有的 `check-graph-sync.py` 本來就跑 `git status --porcelain -uall`,同一個洞早已存在。這份 diff 只是多一個呼叫點,類別不是新的,所以標縱深。
- 引句:「s = _lint_wt_git(repo_root, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching", "--", *_LINT_WT_DECL)」
- file: `scripts/hooks/claude/check-graph-sync.py:359`
severity: minor
- blocking: 否

**F3 殘留的 LUMOS_SKIP_LINT_NEW 會讓收工檢查靜默整道關掉**
- 攻擊路徑:
  - 誰:使用者本人或照常操作的 AI。
  - 從哪:先前為了推送設過 `LUMOS_SKIP_LINT_NEW=1`,環境變數殘留在 shell 或會談裡。
  - 送什麼:之後每個回合結束,鉤子繼承這個環境。
  - 拿到什麼:`_lint_new_wt_verdict` 回 status=off、rc 0。鉤子在 rc 0 時完全不輸出,這道閘整個被走過,沒有任何提示。工作樹模式也不寫治理帳,推送前閘則會留跳過紀錄。
- 修法方向:`LUMOS_SKIP_LINT_NEW` 在工作樹模式生效時,至少往 stderr 印一句,或寫一筆事件。
- 引句:「if os.environ.get("LUMOS_SKIP_LINT_NEW") == "1" or cfg["mode"] == "off":」
- file: `scripts/lumos`(`_lint_new_wt_verdict`)
severity: minor
- blocking: 否

總結:最嚴重是 F1(放行指令在消毒後引號被拆開,檔名可注入 shell 指令),會擋 1 條。
