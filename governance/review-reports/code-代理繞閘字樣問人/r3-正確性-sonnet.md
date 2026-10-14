severity: major

我實際載入 `scripts/hooks/claude/bypass-ask-hook.py`(修後)與修前版本跑 `bypass_reasons`,輸入都用真 repo 當 cwd。下面的 `T` 代表一個已存在的暫存 repo 目錄。

1. 條件式 `cd` 的追蹤有兩個洞,會把實際在真 repo 跑的提交判成暫存實驗 repo 而放行(該問沒問)
severity: major
blocking: 是
- 洞 A:`&&` 鏈後面接換行。
  - 輸入:`false && cd T && true⏎git commit -n`
  - 結果:修後回 `[]`;把換行換成 `;` 就正確回 `['commit-n']`。
  - 原因:`_finish` 的 `q = nxt.replace("\n","")`,換行分隔符變成空字串,`if self.cond_pending and q ...` 因此不成立,`cond_pending` 沒被清掉。換行與 `;` 在 shell 裡等價。
  - 後果:`false` 時 `cd` 沒跑,下一行的提交在真 repo 執行。
- 洞 B:`||` 後面的 `cd` 再接 `&&`。
  - 輸入:`true || cd T && git commit -n`
  - 結果:修後回 `[]`。
  - 原因:`p.endswith("||")` 且 `q.startswith("&&")` 時一律設 `cond_pending=True`、保留 `cd` 的目錄。
  - 後果:左邊成功時 `cd` 被跳過,但 `&& git commit` 照跑,而且在原目錄。只有 `&&` 前導的條件式 `cd`,才能說後面的 `&&` 鏈一定在新目錄。
- 計劃 S3 明列「接在 `||` 或 `&&` 後面而沒緊接 `&&` 的條件式 `cd`」要問人,這兩個形狀沒做到。
- 引句:「if self.cond_pending and q and not q.startswith("&&"):」
- 引句:「self.cond_pending = True     # 條件式 cd 之後緊接 &&:這條 && 鏈裡 cd 一定跑過」
- 歸因:有證據的原有漏查。修前 `old.py` 對這兩個輸入也回 `[]`,所以不是修補造成的回歸,但修補宣稱已處理這類。
- 驗證:兩版都跑 `bypass_reasons("false && cd T && true\ngit commit -n", R)`,結果都是 `[]`。

2. 推送位址只看判斷當下查到的設定,同一條指令內的 `-c`、`GIT_CONFIG_*`、`--repo` 改寫位址完全不認,推到真遠端卻被當拋棄式放行
severity: major
blocking: 是
- 以下輸入修後都回 `[]`(暫存 repo T 的 `loc` 遠端指向暫存裸庫 `T/bare.git`):
  - `cd T && git -c remote.loc.pushurl=git@github.com:a/b.git push --no-verify loc`
  - `cd T && git -c url.git@github.com:a/b.git.pushInsteadOf=T/bare.git push --no-verify loc`
  - `cd T && GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.loc.pushurl GIT_CONFIG_VALUE_0=git@github.com:a/b.git git push --no-verify loc`
  - `git push --repo https://github.com/a/b --no-verify T/bare.git`
  - `git push --repo=https://github.com/a/b --no-verify T/bare.git`
- 原因有兩個:
  - `_changes_remotes` 只看 `git remote` 與 `git config` 子指令,沒看全域 `-c remote.*`/`url.*` 與 `GIT_CONFIG_KEY_n`。
  - `_push_remote_arg` 沒處理 `--repo`:`--repo` 一出現,位置參數就是 refspec,真正的目的地是 `--repo` 的值。
- 這就是計劃 d3 要殺的那一類(用改之前的位址判拋棄式),這次換成一行式寫法。
- 引句:「return any(a.lower().startswith(("remote.", "url.")) for a in args)」
- 引句:「elif not a.startswith("-"):」
- 歸因:有證據的原有漏查。修前 `old.py` 對上面每個輸入也都是 `[]`。
- 驗證:兩版都跑上面的輸入,都是 `[]`。

3. `_strip_redirects` 的「刪除運算子前的數字」規則誤刪真參數,漏掉 `-n` 與 `core.hooksPath` 的值(修補造成的回歸)
severity: major
blocking: 是
- 輸入 1:`git commit -m 1 >/dev/null -n`,修後 `[]`,修前 `['commit-n']`。
- 輸入 2:`git config core.hooksPath 0 >/dev/null`,修後 `[]`,修前 `['config-hookspath']`。
- 原因:
  - shlex 分詞後分不出 `1>` 和 `1 >`。
  - 規則 `w.isdigit() and next 是 _Redir` 把空格隔開的真參數 `1` 也刪掉。
  - 刪掉之後 `-m` 吃掉了 `-n`,而 config 的值不見了,被當成唯讀。
- 引句:「if w.isdigit() and k + 1 < len(words) and isinstance(words[k + 1], _Redir):」
- 歸因:有證據的修復回歸(修前回命中、修後不命中)。
- 嚴重度說明:觸發需要數字參數加「空格後的導向」,不常見,所以只算 major 下緣。

4. 其他子殼層漏追蹤(該問沒問)
severity: minor
blocking: 否
- 輸入:`{ cd T; } | cat; git commit -n` 與 `{ cd T; } & git commit -n`,修後都回 `[]`。
- 輸入:`cd T || git commit -n`、`if ! cd T; then git commit -n; fi`,修後也都回 `[]`。
- 原因:
  - 管線或背景的是 `}` 那一段,不是 `cd` 那一段,所以 `_finish` 的目錄還原沒觸發。
  - `||` 右邊或 `then` 分支是 `cd` 失敗才跑,目錄卻被當成已換。
- 引句:「if changed and (_is_pipe(p) or _is_pipe(q) or (q.startswith("&") and not q.startswith("&&"))):」
- 歸因:有證據的原有漏查(修前同結果)。

5. ANSI 引號不認八進位、`\u`、`\U`,`$"…"` 也不處理,旗標被改寫後攔不到
severity: minor
blocking: 否
- 修後回 `[]` 的輸入:`git push $'\055\055no-verify'`、`git push $'\u002d\u002dno-verify'`、`git commit $'-\156'`、`git push $"--no-verify"`。
- 對照:`$'\x2d\x2dno-verify'` 正確命中。
- 原因:`_ANSI_ESC.get(nxt, "\\"+nxt)` 只解 `\x`,其他跳脫原樣保留。預篩看不到 `--no-veri`,也直接放行。
- 計劃寫「`\xHH` 等」,這幾個沒涵蓋也沒列進〈範圍〉。
- 引句:「out.append(_ANSI_ESC.get(nxt, "\\" + nxt))」
- 歸因:未判定。這個處理是 r1 後新加的,修前版本沒有等價結果可比。

6. 逾時預算起點在同一個程序內不會重設,直接呼叫 `bypass_reasons` 重放事件時,3.5 秒後所有拋棄式豁免靜默消失
severity: minor
blocking: 否
- `_remaining_budget` 的 `_BUDGET_START` 只在第一次設一次。`bypass_reasons` 重設了 `_GIT_STATE`,卻沒重設起點。
- 重現:同一程序先呼叫一次 `bypass_reasons("cd T && git commit -n")` 得 `[]`,`sleep(4)` 後再呼叫同一輸入得 `['commit-n']`,此時 `_remaining_budget()` 為 -0.53。
- 掛鉤正式執行一次一個程序,不受影響。計劃寫「事後量測拿事件帳重跑 `bypass_reasons`」,批次重跑會系統性多算問人次數。
- 引句:「return _outer_budget(5.0) * _BUDGET_RATIO - (_tm.monotonic() - _BUDGET_START)」
- 歸因:未判定。

7. `_changes_remotes` 把唯讀的 `git config --get remote.*` 也當成改遠端,造成多餘的問人
severity: minor
blocking: 否
- 輸入:`cd T && git config --get remote.loc.url; git push --no-verify loc`,修後回 `['no-verify']`,修前 `[]`。
- 方向是安全的(多問),只是實驗 repo 裡先查再推的常見寫法會被問。
- 引句:「if _changes_remotes(sub, args):」
- 歸因:有證據的修復回歸(多問方向)。

**驗收三問**
- ① 原問題的修復效果,我驗過、成立的案例(修前與修後都附結果):
  - `LUMOS_SKIP_X=1 lumos doctor`、`env LUMOS_SKIP_X=1 ...`、`export ...; lumos`:修前未逐一對照,修後都命中。
  - `cd T && git commit -n` 在存在的暫存 repo 放行。
  - `git -C T commit -n` 放行。
  - 子殼層 `(cd T && true) && git commit -n`、管線 `cd T | cat; git commit -n`、背景 `cd T & git commit -n` 都正確問人。
  - `true && cd T && true; git commit -n` 修後 `['commit-n']`,修前 `[]`,這條是修好的。
  - 推到不存在的路徑、`host:path`、`ssh://` 都問人;推到存在的暫存裸庫放行。
  - 執行 `python3.14 scripts/test_lumos.py -k t_bypass_ask_throwaway_targets`:70 項全過,0.8 秒。
- ② 相鄰路徑:換行與 `||` 的條件式 `cd`(發現 1)、`-c`/`--repo` 改位址(發現 2)、數字參數加導向(發現 3)不成立。
- ③ 新發現:發現 3 與 7 是回歸;其餘是原有漏查,修前同結果。

**新測試能否抓到實際錯誤**
- `t_bypass_ask_throwaway_targets` 只有 `;` 與單行的條件式 `cd` 案例,沒有換行、`||` 後接 `&&`、`{ ...; } |`。所以發現 1、4 不會翻紅。
- 它也沒有 `-c remote.*.pushurl`、`--repo`,發現 2 不會翻紅。
- 它沒有「數字參數加空格導向」,發現 3 不會翻紅。

**固定席節點**
- `Issues/code-loop守衛main-direct盲區`:不影響,這次沒動 code-loop 守衛。
- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`:不影響。我只審 hook 與 `_hookevent` 兩支檔,這幾篇的 INVARIANT 對應的是 `scripts/lumos` 與測試檔。
- `測試假綠形態`:新測試缺少「前置斷言證明現場成立」,但這不是本席鏡頭,只提示。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(`★RISK★`):不影響。
- 後端卡 `be-api-compat`、`be-authz`:這次沒有對外 API 或端點,不適用。掛鉤的 `permissionDecision` 輸出形狀沒有改。

附記:`_hookevent._trim` 我跑了 4000 筆事件:大小壓在上限一半以內,權限保留 0644,過期的 `.trim` 暫存檔會清掉,無問題。實驗暫存留在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`,請編排者刪。

最嚴重等級 major,blocking 共 3 條(發現 1、2、3)。
