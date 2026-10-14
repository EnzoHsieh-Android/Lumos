severity: major

彙總載體,非新增審查席。32 條由九份原報告逐字彙整,只在每條 severity 行前加 ID 行,severity 與引句不變。


來源:r3-正確性-sonnet.md


我實際載入 `scripts/hooks/claude/bypass-ask-hook.py`(修後)與修前版本跑 `bypass_reasons`,輸入都用真 repo 當 cwd。下面的 `T` 代表一個已存在的暫存 repo 目錄。

1. 條件式 `cd` 的追蹤有兩個洞,會把實際在真 repo 跑的提交判成暫存實驗 repo 而放行(該問沒問)
ID: c1
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
ID: c2
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
ID: c3
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
ID: c4
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
ID: c5
severity: minor
blocking: 否
- 修後回 `[]` 的輸入:`git push $'\055\055no-verify'`、`git push $'\u002d\u002dno-verify'`、`git commit $'-\156'`、`git push $"--no-verify"`。
- 對照:`$'\x2d\x2dno-verify'` 正確命中。
- 原因:`_ANSI_ESC.get(nxt, "\\"+nxt)` 只解 `\x`,其他跳脫原樣保留。預篩看不到 `--no-veri`,也直接放行。
- 計劃寫「`\xHH` 等」,這幾個沒涵蓋也沒列進〈範圍〉。
- 引句:「out.append(_ANSI_ESC.get(nxt, "\\" + nxt))」
- 歸因:未判定。這個處理是 r1 後新加的,修前版本沒有等價結果可比。

6. 逾時預算起點在同一個程序內不會重設,直接呼叫 `bypass_reasons` 重放事件時,3.5 秒後所有拋棄式豁免靜默消失
ID: c6
severity: minor
blocking: 否
- `_remaining_budget` 的 `_BUDGET_START` 只在第一次設一次。`bypass_reasons` 重設了 `_GIT_STATE`,卻沒重設起點。
- 重現:同一程序先呼叫一次 `bypass_reasons("cd T && git commit -n")` 得 `[]`,`sleep(4)` 後再呼叫同一輸入得 `['commit-n']`,此時 `_remaining_budget()` 為 -0.53。
- 掛鉤正式執行一次一個程序,不受影響。計劃寫「事後量測拿事件帳重跑 `bypass_reasons`」,批次重跑會系統性多算問人次數。
- 引句:「return _outer_budget(5.0) * _BUDGET_RATIO - (_tm.monotonic() - _BUDGET_START)」
- 歸因:未判定。

7. `_changes_remotes` 把唯讀的 `git config --get remote.*` 也當成改遠端,造成多餘的問人
ID: c7
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

來源:r3-併發資源-sonnet.md


審的是併發、資源與效能這一鏡頭。環境:Python 3.14、repo 固定版本 9b8ce146 的工作目錄。實驗放在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`。

## 一句人話
掛鉤平常很快,git 卡住時也守得住總預算。但有一個短指令能讓它吃掉十幾 GB 記憶體:同一條指令裡連續寫 `A=$A$A`,變數值每次翻倍。存活事件檔的修剪另有三個小缺口,影響都很輕。

## Finding

1. 變數展開指數膨脹:250 字元的指令能吃掉 14GB 記憶體、跑 10 秒
ID: r1
severity: major
blocking: 是
- 輸入:`A=xx;` 接 33 次 `A=$A$A;`,再接 ` git commit -n`。長度約 250 字元,遠低於 `MAX_LEN=20000`,所以不走字面判。`--no-verify` 這類預篩字樣也能帶到。
- 走到:`_Walker._assign` 對每次賦值呼叫 `_expand`,它把已賦值的變數值整段代入,值的長度翻倍。`variables` 裡沒有長度上限。
- 重現(`bypass_reasons(指令, "/tmp")`,實測值):

| 翻倍次數 | 指令長度 | 時間 | maxrss |
|---|---|---|---|
| 24 | 187 字元 | 0.02 秒 | 87MB |
| 27 | 208 字元 | 0.09 秒 | 557MB |
| 29 | 222 字元 | 0.24 秒 | 2.2GB |
| 33 | 250 字元 | 10.2 秒 | 14.4GB |

- 估算(沒有實跑):每多一次翻倍就多一倍,35 次約 60GB。
- 把翻倍後的變數用在 `cd $A`,記憶體更高:`cd $A` 版本 27 次是 4.3GB、1.4 秒,因為 `_join` 與 `normpath` 又多複製一份。
- 後果:這不是「失敗就放行」。`decide` 的 `except Exception` 接不到記憶體吃光,只會讓機器 swap 或被系統砍掉。計劃宣稱的「任何失敗都放行」在這條路徑上不成立。
- 應該:`_expand` 或 `_assign` 展開後長度超過例如 4096 就回 `_UNKNOWN`(跟「判不出」同路);或限制單次判斷的賦值次數。
- 引句:「+        self.variables[name] = _expand(val, self.variables)」
- 歸因:有證據的原有漏查。修前版本(`git show 4e87b682:…` 存成 `old.py`)翻倍 27 次:208 字元、557MB(修後同輸入 556.9MB,兩版一致),`_expand` 同樣沒有長度上限。修後(`_Normalizer` 等重寫)沒有加重,也沒有修掉它。修前 `cd $A` 版本翻倍 27 次跑到 120 秒仍沒結束,我把它砍掉;修後同輸入是 1.4 秒,沒有拿到可比數字。

2. 修剪與別的程序同時追加時,中間追加的行會遺失,但沒人察覺
ID: r2
severity: minor
blocking: 否
- 輸入:A 程序進了 `_trim`,在 `read_text` 之後、`os.replace` 之前,B 程序 append 了一行。
- 走到:`lines = f.read_text(...)` 讀的是舊內容,`os.replace(tmp, f)` 換進去的是不含 B 那行的新 inode。B 那行寫到舊 inode,隨之消失。
- 重現:我把 `os.replace` 換成「先 append 一行 `CONCURRENT-LINE` 再真換」,`record` 回 True,行消失(`concurrent line survived: False`)。
- 影響:只掉 telemetry 一行。若剛好是唯一的 `ok`,儀表板會短暫多出 stale 假象。修法留給作者,可以接受並寫進註解。
- 引句:「+    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()[-2000:]」
- 歸因:有證據的原有漏查。舊程式 `tmp.write_text` 加 `os.replace` 是同一個窗口,新碼沒改變它。

3. 修剪被砍時殘檔可能長期留著,最壞幾百 KB
ID: r3
severity: minor
blocking: 否
- 輸入:修剪中程序被砍。我用 `os._exit(9)` 替換 `os.replace` 模擬。
- 現象:留下 `hook-events.08qg6m65.trim`(262KB),不是 `.jsonl.tmp`。清殘檔只在下一次 `_trim` 裡跑,而下一次修剪要等事件檔再長約 256KB。修剪完只剩約 256KB,所以安靜的 repo 裡殘檔可以留很久。
- 清理條件是 mtime 大於 60 秒。被砍後 60 秒內發生的那次修剪不會清它,它就一直留到再下一次修剪。
- `.gitignore:36` 蓋掉 `governance/runtime/`,所以不會污染 `git status`。但 `scripts/lumos:24499` 的註解提到有消費專案曾把 `hook-events.jsonl` 提交進版控,那種專案的 `.trim` 會變成未追蹤檔。
- 引句:「+            if time.time() - old.stat().st_mtime > 60:」
- 歸因:有證據的修復缺口。「清殘檔」是這輪新加的,上面描述的現象是它的行為邊界。

4. 目錄唯讀時,事件檔會無限長大,`record` 仍回 True
ID: r4
severity: minor
blocking: 否
- 輸入:`governance/runtime/` 目錄權限 555,事件檔本身可寫。
- 走到:append 成功,`_trim` 裡 `mkstemp` 丟 `PermissionError`。它是 `OSError`,被 `record` 外層的 `except OSError: pass` 吞掉。
- 重現:`rec True size grew True files ['hook-events.jsonl']`。`guard` 看到 True,不會印 telemetry-write-failed 警告。
- 對照:事件檔本身唯讀(444)時 `open(f,"a")` 就丟例外,`record` 回 False,`guard` 會印警告,這條路徑是對的。
- 影響:只在目錄唯讀而檔案可寫的少見組合,事件檔會越過上限一路長大,沒有任何訊號。
- 引句:「+    fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
- 歸因:未判定。修前固定名 `.jsonl.tmp` 在唯讀目錄下同樣會失敗,所以失敗本身是舊的。沒有證據顯示修補讓它變糟。

## 已驗的主張(無 finding,附證據)

1. 2 萬字內其他形狀都夠快。形狀有:巢狀 `$(`、未閉合括號、反引號對、`cd` 連鎖、導向連串、`git` 或 `lumos` 或 `env` 連串、未結束 heredoc、ANSI 引號、遮罩字元、`\` 續行。
   - 都落在約 0.001 到 0.06 秒,記憶體約 20MB,沒有二次方增長。
   - `_Normalizer`、`_paren_pairs`、`_replace_cmdsubs`、`shlex`、`_strip_redirects` 這幾個函式都是線性。
   - 上面超過 20000 字元的例子走字面判,0.001 秒。
2. 整支掛鉤用 `--budget 5` 從 stdin 跑(指令 `git commit --no-verify -m x`):

| 情境 | 結果 |
|---|---|
| 正常(cwd 是 /tmp 下真 repo) | 0.12 秒,放行 |
| 假 git 卡 30 秒(連子程序也卡) | 3.59 秒,回 ask,rc=0 |
| 假 git 卡 30 秒(cwd 在暫存目錄) | 3.59 秒,回 ask,rc=0 |
| PATH 找不到 git | 0.12 秒,回 ask,rc=0 |
| cwd 無權限進入或不存在 | 0.13 到 0.15 秒,回 ask,rc=0 |

   - 卡住的上限是預算 × 0.7(3.5 秒)加一點:`_root_from_cwd` 吃掉 3 秒,`_remaining_budget` 讓後面的 git 只剩 0.5 秒。
   - `subprocess.run` 逾時只 kill 並 wait,不會被孫程序卡住管線。
   - 預算概念成立,修前 `_inner_budget` 有 1 秒下限,修後 `_remaining_budget` 沒有下限、用完就是 0。
3. 多程序同時修剪:16 個程序各寫 60 筆(共 960 筆),`record` 全部回 True。
   - 最終只剩 `hook-events.jsonl` 一個檔,沒有殘檔。
   - 0 行壞 JSON,權限維持 0o640(修剪沒有改掉權限)。
4. 磁碟滿:`os.fdopen` 寫入丟 `ENOSPC` 時,暫存檔被清掉,原檔保留,`record` 回 True。例外沒有冒出來。

## 三問
1. 原問題的修復效果:
   - 暫存檔獨立名字。16 個程序同時修剪,沒有互相覆蓋或 `FileExistsError`。
   - 權限照原檔。0o640 修剪後還是 0o640。
   - 殘檔清理有效,但有 finding 3 的延遲。
   - 預算:卡住的 git 總時間 3.59 秒(預算 5 的 0.7 倍)。
2. 修補處的相鄰路徑:正常、唯讀檔案、磁碟滿、卡住的 git 都不冒例外;唯讀目錄是 finding 4。
3. 新發現的修前與修後:finding 1 兩版行為一致(原有)。finding 2、3、4 的修前形狀不同,但沒有證據指出修補造成的回歸。

未驗範圍:macOS 以外的平台;真正的 kill -9 在 `mkstemp` 與 `os.replace` 之間的所有時序(我用 `os._exit` 模擬);超過 14GB 的情況(我沒有往下跑到系統被砍)。

## 固定席節點逐條判

| 節點 | 判斷與理由 |
|---|---|
| Issues/code-loop守衛main-direct盲區 | 不影響。談的是 main 直推守衛的盲區,本改動沒碰分支守衛;牽連檔只有 `test_lumos.py`。 |
| Systems/lumos-cli-read(search 預設排除 superseded) | 不影響。本鏡頭實測的是掛鉤與事件檔,沒有碰 `search` 路徑。 |
| Systems/lumos-cli-lifecycle(re-inject 保留 sentinel 之外內容) | 不影響。掛鉤與 `_hookevent.py` 沒有改動 CLAUDE.md 注入。 |
| Systems/design-loop(處置閘第五步) | 不影響。處理的是設計審迴圈的審材型別,不是掛鉤。 |
| Systems/測試假綠形態(還原翻紅要配前置斷言) | 屬測試文件組,我沒讀。補充:finding 1 到 4 若補測試,要先斷言現場成立,例如斷言 `_expand` 真的走到代入、`_trim` 真的進了 mkstemp。 |
| Systems/guard-kill(rc 優先序與 JSON 純度) | 不影響。與掛鉤的 rc 或輸出無關。 |
| Systems/pitfalls-code-loop、reversibility-governance-ledger(兩篇 RISK) | 不影響。談風險分級與可逆帳,與我測的資源行為無關。 |
| 其餘「超出上限只列名」的節點 | 我沒讀內容,無法逐條判。只看到名字:`bound-tests-gate` 的子集規則可能影響測試要不要重跑。 |

最嚴重等級 major;blocking 共 1 條(finding 1),minor 3 條。

來源:r3-邊界輸入-sonnet.md


我載入修後(9b8ce146)與修前(4e87b682)的 `bypass-ask-hook.py`,跑了約 300 條邊界輸入。能對照的都兩版並排,結果有兩層:
- `bypass_reasons`:直接比兩版的輸出。
- 掛鉤入口 `entry()`:餵 JSON 事件,看有沒有印出 `ask`。
- 實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/邊界輸入-sonnet/`(`t1.py` 到 `t11.py`)。

**發現**

1. 預篩擋在分類器前面,r3 補的解碼能力有一整批到不了。
引句:「low = re.sub(r"['\"\\]", "", _command_text(raw)).lower()」
ID: e1
severity: major
blocking: 是
- 預篩只拿掉引號和反斜線,不解 `$'…'`,也不接續行。分類器已經認得的寫法,在入口就被擋掉,整條放行。
- 重現(`entry()` 對照 `bypass_reasons`):

| 輸入 | `bypass_reasons` | `entry()` |
|---|---|---|
| `git commit -$'n'` | `['commit-n']` | 無輸出 |
| `git push --no-ve$'\x72'ify` | `['no-verify']` | 無輸出 |
| `git push $'\x2d\x2dno-verify'` | `['no-verify']` | 無輸出 |
| `git push --no-ver\<換行>ify` | `['no-verify']` | 無輸出 |
| `git commit -\<換行>n` | `['commit-n']` | 無輸出 |
| `git commit -a\<換行>n` | `['commit-n']` | 無輸出 |
| `git config core.hooks\<換行>Path x` | `['config-hookspath']` | 無輸出 |
| `LUMOS_SKIP\<換行>_X=1 git commit` | `['lumos-skip']` | 無輸出 |
| `git commit --no-$'verify'` | (未單獨查) | 無輸出 |

- 原因:反斜線被拿掉後換行還在,`--no-veri` 的字樣被換行切斷。
- 計劃 S1 明寫「續行切開長選項」「`$'…'` 之後或包住旗標」要問,而〈做法〉第 87 行舉的例子 `git commit -$'n'` 本身就是無聲放行。
- 同一批裡,`$'\055\055no-verify'`(八進位)、`\u002d`、`\c` 解碼器不認,`bypass_reasons` 本身就回 `[]`。
- 應該怎樣:預篩要用跟 `_Normalizer` 同一套前處理(至少接續行、解 `$'…'`)再比字樣。或者只要原文有 `$'`、反斜線加換行,就一律放進分類器。
- 歸因:有證據的原有漏查,修補不完整。
  - 修前 `bypass_reasons("git commit -$'n'")` 是 `[]`,修後分類器補上了,但入口擋住,效果為零。
  - 修前預篩連引號都沒剝。修後只補了引號和反斜線,沒補上面這兩類。
  - 兩版查證:`python3.14 t7.py`、`t8.py`、`t9.py`。

2. 大括號群組的 `cd` 不被當子殼層,誤給豁免。
引句:「elif changed and (p.endswith("&&") or p.endswith("||")):」
ID: e2
severity: minor
blocking: 否
- `{ cd /tmp/exist; } | cat; git commit -n`,cwd 在真 repo:兩版都回 `[]`。`{ cd X; } &` 同樣。
- 原因:`{` 只是關鍵字,沒有像 `(` 那樣推進 stack,管線判斷只看分隔符。
- 實際上管線或背景裡的群組跑在子殼層,`cd` 不會傳到後面,提交其實在真 repo,卻被豁免。
- 應該怎樣:`{ … }` 緊接管線或 `&` 時,把這段的 `cd` 還原。或者看到 `}` 後面接 `|` 或 `&` 就把目前目錄設為判不出。
- 歸因:有證據的原有漏查(兩版相同,非回歸)。

3. 條件式 `cd` 的第一個分支成功時,第二個 `cd` 根本不會執行,仍被當成已生效。
引句:「self.cond_pending = True     # 條件式 cd 之後緊接 &&:這條 && 鏈裡 cd 一定跑過」
ID: e3
severity: minor
blocking: 否
- `cd <真repo> || cd /tmp/x && git commit -n`:兩版都回 `[]`。`test -d R && cd R || cd /tmp/x && …` 同樣。
- 原因:`cd R` 成功時 `|| cd /tmp/x` 被跳過,提交跑在真 repo。程式把 `||` 後面、緊接 `&&` 的 `cd` 當作「一定跑過」。
- 反過來,`cd /tmp/x || cd <真repo> && …` 正確地問了。
- 應該怎樣:`||` 之後的 `cd` 一律設為判不出,或把前一個 `cd` 的目錄也納入,兩者都要是暫存才豁免。
- 歸因:有證據的原有漏查(`cond_pending` 是 r3 前就有的邏輯,兩版同結果)。

4. 括號後緊貼導向,括號被吃進詞裡,子殼層沒有還原。
引句:「if _is_sep(t):」
ID: e4
severity: minor
blocking: 否
- `(cd /tmp/x)>/dev/null; git commit -n`:兩版都回 `[]`。有空格 `) >/dev/null` 則正確回 `['commit-n']`。
- `(cd /tmp/x;git commit -n)>/dev/null; git commit -n` 也是 `[]`。
- 原因:shlex 把 `)>` 切成一個詞。`_is_sep` 不成立(含 `>`),`_is_redirect` 也不成立(含 `)`),於是成了普通詞,括號層沒被彈出。`)&>`、`;>` 同理。
- 應該怎樣:`_tokens` 切詞前先把括號、分號跟導向字元拆開,或在標點串裡逐字分類。
- 歸因:有證據的原有漏查(兩版都 `[]`)。

5. `{fd}>log` 形式的導向沒有被剝掉。
引句:「if w.isdigit() and k + 1 < len(words) and isinstance(words[k + 1], _Redir):」
ID: e5
severity: minor
blocking: 否
- `git {fd}>log commit -n` 回 `[]`。
- 原因:`{fd}` 被當成子指令名。
- 應該怎樣:在 `_strip_redirects` 一併剝掉 `^\{[A-Za-z_]\w*\}$` 且後面緊接導向的詞。
- 歸因:未判定,兩版都漏。

6. `GIT_DIR` 一族的判斷太寬,多問。
引句:「_GITDIR_NAME = re.compile(r"^(GIT_DIR|GIT_WORK_TREE|GIT_COMMON_DIR)(\+?=|$)")」
ID: e6
severity: minor
blocking: 否
- `cd <暫存repo> && echo "GIT_DIR=foo" && git commit -n`、`grep GIT_DIR f`、`git commit -n -m GIT_DIR` 都會多問。
- 修前這些是 `[]`,修後是 `['commit-n']`。
- 修前就有的 `GIT_DIR=/r git commit` 等本來就問。
- 這種誤問對照計劃「寧可多問」可以接受。heredoc 內的 `GIT_DIR` 被剝掉所以不影響,屬於範圍外。
- 應該怎樣:只在賦值形式 `NAME=`,或是前一個詞是 `export`/`declare`/`env`/`unset` 時才算,不用 `$` 比對單獨的詞。
- 歸因:有證據的修復造成的新多問,不是漏問,可接受。

**已驗、無問題**

重現檔都在 `t1.py` 到 `t11.py`。

- 導向寫法:`>|`、`<>`、`<<<`、`2>`、`&>>`、`>&-`、`>log git push --no-verify` 都問,兩版一致。
  - 夾在 git 全域選項之間:修前漏、修後問,如 `git >log push --no-verify`、`git -c a=b >log push …`。
  - 管線 `cd X 2>&1 | tee`、`cd X |& tee` 修後會問,是對的。
- 跳脫字元:`\\` 結尾、`\"` 在雙引號裡、單引號內的反斜線、`\$`、`\#` 結果都對。
  - 結尾孤立反斜線,修前走 `literal`,修後走結構判斷,也問。
- ANSI 在分類器層:
  - `\x` 後無十六進位數字、未閉合的 `$'`,都沒丟例外。
  - `$'a\nb'` 內含換行,結果對。
- 續行:單引號內不接、雙引號內接、註解內不誤接,都對。
  - heredoc 內,bash 實際會把 EOF 吃成續行,程式則多問,可接受。
- 條件式與管線 `cd`:
  - `if cd X; then …`、`while cd X`、`cd X && { …; }`、`cd X && ( … )`、`(cd X; true)|cat` 都對。
  - `cd X | cat && …` 修後問,對。
  - `cd >/dev/null X &&` 修後比修前更準確(導向被剝掉,`cd X` 才被認得)。
- `_local_url` 與推送目標:
  - `file:/x`(單斜線)、`~/x`、`$HOME/x`、`origin`、`host:/x` 全部走網路位址,都問,偏安全。
  - `file:///tmp/../Users`、`file://…/../../..`、指到真 repo 的符號連結都問。
  - `file://tmp/x` 回傳相對路徑,只有 cwd 剛好是 `/` 才可能誤豁免,不構成實際問題。
  - `git push /tmp`(目錄本身)豁免,但那不是 repo,推送本身會失敗,無害。
  - `file://localhost/tmp/x` 多問,可接受。
- 效能:各種 1 萬到 2 萬字的最壞輸入都在 0.04 秒內。

**三問**

- 原問題的修復效果:導向剝除、管線 `cd` 還原、`$'…'` 解碼、結尾反斜線、續行這幾項,在 `bypass_reasons` 層都有同一案例「修前 `[]`、修後命中」的證據(`t1.py`、`t2.py`、`t7.py`)。但發現 1 顯示其中解碼與續行兩項在入口層沒有生效。
- 修補處的相鄰路徑:正常與錯誤路徑成立。例外是發現 2、3、4,仍會誤給豁免。這三條在修前就如此,修補沒有惡化。
- 新發現的同案例修前修後:發現 2、3、4、5 兩版都是 `[]`。發現 1 的分類器層是修前 `[]`、修後命中,入口層兩版都靜默。發現 6 是修前不問、修後多問。

**固定席節點逐條判**

- `Issues/code-loop守衛main-direct盲區.md`:只牽連 `scripts/test_lumos.py`,與本席的掛鉤邊界輸入無關,不影響。
- `Systems/lumos-cli-read.md`:search 排除 superseded 的 INVARIANT 與本改動無關,不影響。
- `Systems/lumos-cli-lifecycle.md`:re-inject 保留 sentinel 之外內容的 INVARIANT 與本改動無關,不影響。我沒看到新掛鉤動 CLAUDE.md 注入。
- `Systems/design-loop.md`:處置閘第五步的 INVARIANT 與本改動無關,不影響。
- `Systems/測試假綠形態.md`:要求還原翻紅釘配前置斷言。發現 1 正好是同型風險,分類器層測試綠、入口層靜默;測試應從 `entry()` 層驗,但這屬於測試組的範圍。
- `Systems/guard-kill.md`:guard kill 的 rc 與 JSON 純度與本改動無關,不影響。
- `Systems/pitfalls-code-loop.md`、`Systems/reversibility-governance-ledger.md`:牽連 `scripts/lumos`,不在我的程式組範圍,未判,不影響本席結論。
- 其餘只列名的節點:不在我的程式組範圍,未判。

最嚴重等級為 major,blocking 共 1 條(發現 1),其餘 5 條為 minor。

來源:r3-通才-sonnet.md


我沒找到不刻意混淆、也不在〈範圍〉裡的寫法能讓這支掛鉤放行真繞閘。「只認判斷當下的事實」確實有縫:同一條指令把已存在的暫存目錄換成指向真 repo 的連結。我判斷它屬於有心改寫,但〈範圍〉沒列,且與 d3 的「封閉」說法矛盾,所以列為 minor。

## Findings

1. 判斷當下存在的暫存目錄,在同一條指令裡被換成指向真 repo 的連結,仍然放行。

   - 輸入(cwd 為真 repo,`E` 是判斷當下已存在的暫存實驗 repo):
     - `rm -rf E && ln -s <真repo> E && git -C E commit --no-verify -m x` → `[]`
     - `mv E E.old && ln -s <真repo> E && git -C E commit --no-verify -m x` → `[]`
     - `cd 已存在的空暫存目錄 && ln -s <真repo>/.git .git && git commit --no-verify -m x` → `[]`
     - 對 `echo 'gitdir: <真repo>/.git' > P/.git && git -C P commit -n -m x` 也是 `[]`(P 為已存在的暫存空目錄)。
     - `git -C 暫存空目錄 config core.hooksPath /dev/null` 也放行。
   - 對照:`mkdir W/newdir && ln -s … && git -C W/newdir commit -n`,目錄是同指令新建的,所以回 `['commit-n']`。
   - 走到的程式:`_not_real_repo` 先看 `_existing_temp_dir(eff)`,再用 git 查共用目錄。查的是執行前的狀態,指令真正執行時已被換掉。
   - 我的判斷:要連做兩步才成立,屬於〈範圍〉承認的「有心改寫」,不是一般代理「順手繞」。但有兩點與文件不符:
     - d3 選項②當年被否決的理由是「仍擋不住刪掉重建成連結」,出貨版同樣擋不住,所以 d3 的「攻擊面收成封閉」不成立。
     - 程式註解與計劃說「git 明說不在 repo 裡,之後建的只會是新的」。這個推論本身就被上面的 gitfile 與連結寫法推翻,而 d3 說要拿掉的正是這類推論。
   - 應該是:要嘛在〈範圍〉明列這一類(同指令改寫判斷當下已存在的暫存目錄)並改寫 d3 的「封閉」說法,要嘛判斷時對同一條指令裡出現 `ln`、`mv`、`rm` 或寫 `.git` 的情形不給豁免。
   - 歸因:有證據的原有漏查。修前版本(4e87b682)與修後版本同一組輸入都回 `[]`。
   - 查證命令:用 `SourceFileLoader` 載入兩版的 `bypass_reasons(cmd, 真repo)`,輸出見上。
   - 引句:「而且共用 git 目錄也在暫存根底下;或 git 明說它不在任何 repo 裡。不靠同一條指令裡的推論」
ID: t1
severity: minor
   - blocking: 否

2. commit 與 `git config` 的拋棄式豁免只看共用 git 目錄在不在暫存根底下,沒看是不是真遠端的工作副本。

   - 輸入:`/tmp/.../realclone` 是 `git init` 後 `remote add origin git@github.com:EnzoHsieh-Android/Lumos.git` 的工作副本,cwd 設在這個目錄。
     - `git commit --no-verify -m x` → `[]`
     - `git config core.hooksPath /dev/null` → `[]`
     - `LUMOS_SKIP_X=1 git commit -m x` → `[]`
     - 同一目錄的 `git push --no-verify origin main` → `['no-verify']`,推送端有擋。
   - 與文件的關係:計劃〈量測〉自己說暫存目錄裡有真工作副本,例如 `/tmp/lumos-readme-oct-audit` 一週 5 次一般推送。推送端因此改查推送位址,commit 與 config 端沒有對應檢查。
   - 影響:提交端的閘在這類目錄裡被繞過時不會問。後續的一般 `git push` 也不帶旗標,所以不會補問。如果那個副本裝了 Lumos 的提交前閘,這就是真繞閘。我沒驗證 `/tmp` 工作副本實際有沒有裝閘,⚠ 交編排者判斷。
   - 應該是:要嘛承認並寫進〈範圍〉,要嘛 commit 與 config 的豁免多查 `remote get-url`(網路位址就不豁免),或至少為這個取捨補一條說明。
   - 歸因:有證據的原有漏查。修前修後同為 `[]`。
   - 引句:「+        return _not_real_repo(eff)」
ID: t2
severity: minor
   - blocking: 否

## 已驗正向主張

甲(閘被擋、使用者在催的代理,正常寫法)

- 真 repo 裡下面這些都回對應代號,都會問:
  - 順序或位置變化:`git push --no-verify`(旗標在前或在後)、`git push origin HEAD --no-verify`、`git commit -nm`、`git commit --amend -n`
  - 縮寫、全域選項與前綴:`--no-verif`、`git --no-pager push --no-verify`、`git -C . push --no-verify`、`command`、`sudo`、`env`、`timeout` 等前綴
  - 括號與迴圈:`( … )`、`{ …; }`、`if … then`、`for … do`
  - 管線與導向:管線、`>/dev/null`、`2>&1`
  - 引號與反斜線:`g"i"t`、`$'--no-verify'`、`--no-ve''rify`、反斜線續行
  - 設定改寫:`-c core.hooksPath=`、`--config-env=`、`GIT_CONFIG_*`、`export` 後再提交、各種 `git config` 寫法(`--add`、`--unset`、`--worktree`、`-f`、`--file=` 等)
  - 環境變數:`LUMOS_SKIP_*` 前綴、`env` 前綴
- 以下被放行,與〈範圍〉承認的一致:`sh -c '…'`、`$(…)` 內的指令、`!git`(感嘆號黏著)、`echo $((git push --no-verify))`。
- 目錄追蹤:真 repo cwd 下,`cd 暫存目錄 && cd 真repo` 之類的組合(`&&`、`||`、`;`、子殼層、`$HOME`、`~`、`git -C 真repo`)都回 `commit-n`,不誤放行。
- `--git-dir`、`--work-tree` 與 `remote set-url`、`add`、`rename`、`config remote.*`、`config url.*` 都使豁免失效,回報 `['no-verify']` 或 `['commit-n']`。唯讀的 `git remote -v` 不影響豁免。
- 暫存目錄 `E` 的 `.git/config` 被 `sed -i` 或 `echo >>` 改成指向真遠端後再推送,仍回 `[]`。這是〈範圍〉已承認的「直接改 `.git/config`」,不重報。

乙(日常不該問的指令)

- 以下全部回 `[]`,沒有誤問:
  - 審查席在已存在的暫存 repo 裡的實驗:`git -C E commit --allow-empty --no-verify`、`cd E && git commit -n`、`git config core.hooksPath` 寫入、帶遠端名稱的 `push --no-verify`(遠端指向暫存裸 repo)、`gctl-run-*` 的子目錄提交。
  - 搜尋與讀值:`grep`、`rg` 搜尋這些旗標名、`git config core.hooksPath` 讀值、`--get`、`--local`。
  - 一般提交推送與 `git log -n`:Claude 慣用的 `git commit -m "$(cat <<'EOF' … EOF)"` 含撇號、`--no-verify`、`-n`、`LUMOS_SKIP_` 字樣的訊息,`git commit -F - <<'EOF'`,以及 `git log -n`、`git diff -n`、`git push -n/--dry-run`、`git push -u`、`--no-edit`、`--no-gpg-sign`。
- 沒加引號的 `echo git push --no-verify` 會問,這是文件承認的誤問。
- 小的誤問(不另列 finding):
  - 旗標值剛好是 `--no-verify`:`git commit -m --no-verify`、`git push --push-option --no-verify` 會問。
  - `cd W/exp && git push --no-verify` 沒寫遠端,保守地問。
  - `cd $TMPDIR && …` 目錄判不出,會問。
- 效能與巢狀:
  - 輸入:1.9 萬字、各 3000 層巢狀 `$(` 或 `(`、2000 個 `cd`、800 個 heredoc,不論有無結束字。
  - 結果:最慢 0.016 秒,沒有退化。超過 2 萬字走 `literal`,長度夠但沒有可疑字樣的指令回 `[]`。
- `_hookevent._trim` 修補驗證:
  - 20 萬行的檔修剪後剩 2000 行,權限保持 `0640`。
  - 超過一分鐘的殘留 `*.trim` 暫存檔被清掉,新的暫存檔保留。
  - 經 `record()` 觸發的修剪正常。
  - 單行超過 `MAX_BYTES/2` 時整檔會變成只剩換行。`record` 把 note 截在 200 字,實務上不會發生,不報。

## 三問

1. 原問題修復效果:新規則下,同指令新建目錄、`mktemp`、同指令動遠端設定這幾類都回對應代號,舊版(4e87b682)放行,例如 `mkdir nd && git -C nd init && git -C nd commit --no-verify` 舊 `[]`、新 `['no-verify']`。對判斷當下已存在目錄的同指令改寫,新舊都放行(finding 1)。
2. 相鄰路徑:已存在的暫存 repo 實驗、`gctl-run` 子目錄、讀值、搜尋、heredoc 提交訊息都沒被誤問(見乙)。
3. 新發現的修前修後:兩條都是新舊同結果,屬原有漏查,不是修補引入的回歸。

## 固定席節點逐條判

- `Issues/code-loop守衛main-direct盲區`:不影響。該事故講守衛盲區,這次兩個掛鉤檔不碰那條路徑。
- `Systems/lumos-cli-read`(含 ★INVARIANT★ search 排除 superseded):不影響。改動沒碰 `search` 或讀取邏輯。
- `Systems/lumos-cli-lifecycle`(含 ★INVARIANT★ re-inject 保留 sentinel 外內容):不影響。程式組只動掛鉤與 `_hookevent`,沒碰 re-inject。`scripts/lumos` 與 `merge-claude-settings.py` 的改動屬測試文件組,我沒逐 hunk 讀。
- `Systems/design-loop`(處置閘第五步)、`Systems/測試假綠形態`(還原翻紅釘要前置斷言)、`Systems/guard-kill`:不影響程式組。測試是否帶前置斷言屬 `test_lumos.py`,不在我的分組。
- `Systems/pitfalls-code-loop`、`Systems/reversibility-governance-ledger`(★RISK★):不影響。程式組沒碰 pitfalls 分級或帳本。
- 超出上限只列名的節點:`Systems/bound-tests-gate`、`Systems/slim-install-安裝器`、`Systems/lumos-deinit` 等,與程式組無關,沒逐條判。

總結:最嚴重等級 minor,blocking 共 0 條。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`
- `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/_hookevent.py`
- 我的實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/通才-sonnet/`,請編排者刪除。

來源:r3-架構對齊-sonnet.md


我只讀了 patch 和 `scripts/lumos`、鄰居掛鉤的對應段落,沒有載入掛鉤去重現行為。以下三問逐問答,findings 放在第 2、3 問。

## 1. 分層與依賴方向:對齊

- 新掛鉤 `bypass-ask-hook.py` 只往下依賴 `_hookevent`(`guard`、`mark`)。
  - 沒有去呼叫 `scripts/lumos`,`_hookevent` 也沒有反向依賴掛鉤,沒有跨層直呼。
  - 對照 file: `scripts/hooks/claude/impact-hook.py:928` 和 file: `scripts/hooks/claude/dispatch-lens-hook.py:555`,鄰居也是只經 `_guard(...)` 進 `_hookevent`。
  - `_trim` 留在 `_hookevent` 內,沒有搬到掛鉤裡。
- 已知偏離(guard 外預篩、模組頂層載入共用模組、分類邏輯放在掛鉤內)不重報。
- 本輪新增的 `_Redir` 是已記錄的 `_Sep` 無先例做法的同形延伸,不另報。

## 2. 命名與錯誤處理

1. 預算函式出現第二種做法,且還帶不同的預設值。
引句:「return _outer_budget(5.0) * _BUDGET_RATIO - (_tm.monotonic() - _BUDGET_START)」
ID: a1
severity: major
blocking: 是
   - 這支掛鉤逐字複製了 `_inner_budget`,帶 1 秒下限,預設 `default=10.0`。但檔內沒有任何地方呼叫它,只剩定義和 `_remaining_budget` 的 docstring 提到它。
   - 另外新寫 `_remaining_budget`:沒有下限,預設 `_outer_budget(5.0)`,並且讀寫同一個模組全域 `_BUDGET_START`。
   - 鄰居用到預算的地方全走 `_inner_budget(...)`。對照 file: `scripts/hooks/claude/impact-hook.py:810` 的呼叫,以及 file: `scripts/hooks/claude/memory-sweep.py:180`。
   - 結果是同一檔裡有兩套「還剩幾秒」的算法,預設值 5.0 對 10.0 也不一致。複本是為了過「各份一模一樣」的測試才保留,實際上是死碼。
   - 這裡有正當理由:`_git_out` 需要「用完歸零」的語意,1 秒下限會讓預算用完後還跑 git。這個理由我沒有重現,所以標 ⚠。
   - 對齊的做法有兩種:
     - 給 `_inner_budget` 加一個無下限的參數。
     - 或在計劃的偏離清單補一條,承認 `_remaining_budget` 是第二種做法。
   - 此外,`_remaining_budget` 靠 `entry()` 第一行呼叫來起算 `_BUDGET_START`,這個副作用鄰居沒有。
   - 歸因:未判定,我沒有讀修補差異裡這段是否為本輪新增。

2. `_trim` 的權限照抄寫法,跟 `scripts/lumos` 既有的暫存寫入不同。
引句:「mode = _stat.S_IMODE(f.stat().st_mode)」
ID: a2
severity: minor
blocking: 否
   - `_trim` 的做法是 `tempfile.mkstemp`,再 `os.chmod(tmp, S_IMODE(原檔))`,最後 `os.replace`。
   - `_write_lf` 的做法不同:
     - 用 `os.open(..., O_EXCL, 0o666)`,權限受 umask 管。
     - 原檔在就 `shutil.copymode(path, tmp)`。
     - docstring 明寫「不用 mkstemp 再改權限」。
     - 見 file: `scripts/lumos:19474`。
   - `_home_cache_write` 是 mkstemp 加固定 `chmod 0600`,見 file: `scripts/lumos:46067`。所以 mkstemp 加 chmod 在 repo 內有先例,結構是對的。
   - 不一致處是「照原檔權限」本來有 `copymode` 這個既有寫法,`_trim` 另外手刻了一份。
   - 歸因:未判定。

3. `_trim` 的失敗清理只抓 `OSError`,跟既有暫存寫入的清理慣例不同。
引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
ID: a3
severity: minor
blocking: 否
   - 這個函式的清理寫法是 `except OSError: unlink; raise`。
   - `_write_lf` 用 `except BaseException`,`_codeloop_write_dispositions` 用 `finally: unlink`。
   - 見 file: `scripts/lumos:19474` 和 file: `scripts/lumos:48743`。
   - 另外,`_trim` 開頭 `glob("hook-events.*.trim")` 掃一分鐘以上的殘檔,這在 `scripts/lumos` 沒有先例。這個做法有寫在 docstring,結構上沒問題,只是屬於新增的做法。
   - 歸因:未判定。

## 3. 第二種做法

- 上面第 1 條是唯一的第二種做法。
- 其餘的都是已記錄的偏離,或結構對、細節不同的 minor。
- 這個版本我沒有找到自寫的 git 子程序呼叫之外的重複工具。`_git_out` 是帶快取和次數上限的小包裝,鄰居是直接 `subprocess.run(["git","-C",...])`(file: `scripts/hooks/claude/ci-status-hook.py:30`),它的差異屬於預算語意,已併入第 1 條。

## 固定席節點

- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill` 這幾篇的 ★INVARIANT★:本 patch 的程式組沒有碰 search 濾網、re-inject、處置閘、guard kill,不影響。
- `Issues/code-loop守衛main-direct盲區`、`pitfalls-code-loop`、`reversibility-governance-ledger`:牽連的是 `scripts/lumos` 和 `test_lumos.py`,程式組只有 `_hookevent.py` 和新掛鉤,不影響。
- 其餘「只列名」的節點未讀,未判。

不對齊共 3 條,其中 major 1 條。

來源:r3-資安-sonnet.md


我只讀了程式組,逐 hunk 讀完。修補前後的行為都用 `bypass_reasons` 實跑過。在 `/tmp` 底下造了一個暫存 repo `exp`,另有一個指向真 repo 子目錄的符號連結 `lnk`。

1. 路徑含 `..` 時,掛鉤把它當純文字化簡,和 git 與作業系統實際走的路不同。暫存目錄裡的符號連結因此可以讓 `git -C` 的目標或 push 的目標落在暫存根之外,卻仍被當成拋棄式放行。
ID: s1
severity: major
blocking: 是
- 攻擊者是被提示注入的代理,從 Bash 指令送進來。
- 先做一件在暫存根底下普通的事:`ln -s <真repo>/scripts /tmp/x/lnk`。
- 再送 `git -C /tmp/x/lnk/.. commit -n -m x`。
- 掛鉤的 `_join` 用 `os.path.normpath` 把路徑化簡成 `/tmp/x`,它存在、在暫存根下、不是 repo,於是豁免。git 的 `-C` 是真的 chdir,`lnk/..` 實際走到真 repo,提交前閘被跳過而且不問人。
- push 也一樣:`git push --no-verify /tmp/x/lnk/../remote.git` 在 `_temp_target` 裡被化簡成 `/tmp/x/remote.git`。只要那個路徑存在(先 `mkdir` 一個就行),就當作暫存目標,實際推到 `<真repo>/remote.git`。
- 計劃〈範圍〉說「比對前兩邊都 realpath」,但判斷「存在」與取目錄的是化簡後的路徑,realpath 只對化簡後的結果做。
- 注意,shell 的 `cd` 是邏輯路徑,`cd /tmp/x/lnk/..` 確實會到 `/tmp/x`,所以 `cd` 追蹤沒有這個問題。只有 `git -C` 和 push 的路徑參數有。
- 引句:「return isinstance(p, str) and os.path.exists(p) and _under_temp(p)」
- 引句:「eff = _join(eff, _expand(d, self.variables))」
- 重現(修後版):
  - `git -C /tmp/secx.J6Bh/lnk/.. commit -n -m x` 回 `[]`,放行。
  - `git push --no-verify /tmp/secx.J6Bh/lnk/../remote.git main` 回 `[]`,放行。
  - 對照:`git -C /tmp/secx.J6Bh/lnk/.. rev-parse --show-toplevel` 實際印出真 repo 路徑。
  - 對照:同樣的 push 直接寫真路徑回 `['no-verify']`,會問。
- 修法方向:先用 realpath 解開整條路徑,再判存在與是否在暫存根;或路徑含 `..` 就不豁免。
- 歸因:有證據的原有漏查。修前版(4e87b68)的同一組指令也回 `[]`,不是這輪修補引入的。

2. d3 只認「判斷當下存在」的事實,但同一條指令裡把那個已存在的暫存目錄「刪掉或搬走再換成連結」,掛鉤沒有追蹤,仍然判成拋棄式。
ID: s2
severity: major
blocking: 是
- 攻擊者是被提示注入的代理,從 Bash 指令送進來,而且 `exp` 是之前的指令留下的暫存 repo。
- 送 `rm -rf /tmp/x/exp && ln -s <真repo> /tmp/x/exp && git -C /tmp/x/exp commit -n -m x`。
- 判斷當下 `/tmp/x/exp` 是暫存根下的真暫存 repo,共用 git 目錄也在暫存根下,於是豁免。實際執行時它已被換成指向真 repo 的連結,提交前閘被跳過。
- 把 `rm -rf` 換成 `mv exp old` 一樣放行,也沒有被問。
- 計劃 d3 把「保留同指令建目錄但限完全相同路徑」否決的理由是「仍擋不住刪掉重建成連結」。但現行的 d3 也沒有擋住對已存在目錄做同樣的事,所以上一輪同一類繞法換了形狀又回來。
- 引句:「(同指令建的目錄、mktemp、remote add 都不算——兩輪審查都在這類推論上找到繞法,計劃 d3)」
- 重現(修後版):
  - `rm -rf /tmp/secx.J6Bh/exp && ln -s <真repo> /tmp/secx.J6Bh/exp && git -C /tmp/secx.J6Bh/exp commit -n -m x` 回 `[]`。
  - `rm -rf /tmp/secx.J6Bh/remote.git && ln -s <真repo>/docs /tmp/secx.J6Bh/remote.git && git push --no-verify /tmp/secx.J6Bh/remote.git main` 也回 `[]`。
  - 對照:`mv exp old && ln -s <真repo> exp && git -C exp push --no-verify` 回 `['no-verify']`,是因為這條沒寫遠端,不是因為抓到換連結。
- 修法方向,三選一:
  - 同一條指令裡出現 `rm`、`mv`、`ln`、`cp` 等會動檔案系統的指令,就不給豁免。
  - 或在 `_Walker` 追蹤這些指令碰到的路徑。
  - 或把這個洞明文收進〈範圍〉承認攔不到。
- 歸因:有證據的原有漏查。修前版同一條指令也回 `[]`,但 d3 宣稱「換形狀」已處理這類,這個宣稱不成立。

已看,無的類別:
- **git 錯誤訊息判斷**:語系或 `LANG` 變動只會讓訊息不含 "not a git repository",結果是不豁免、照問,方向安全。真 repo 被誤判成「不在 repo 裡」,我只想到 `GIT_DIR` 一族,而它已被 `gitdir_seen` 擋掉。
- **清殘檔 glob**:`_trim` 的 `d.glob("hook-events.*.trim")` 只在事件目錄內,`unlink` 刪連結本身而不是它的目標,檔名不含使用者輸入。暫存檔用 `mkstemp` 建立,`chmod` 只動自己的暫存檔。無洞。
- **輸出**:確認框理由只用固定代號文字,不嵌入指令內容。存活事件的 note 是例外類型名稱加截斷到 120 字的訊息,沒有指令內容。無洞。
- **範圍內不重報**:`include.path` 和 `GIT_CONFIG_GLOBAL` 這類改設定檔而不是用 `-c` 的寫法(E 案回 `[]`),屬〈範圍〉承認的「直接改設定」,我沒有當 finding 報。

回答三問:
1. 原問題的修復效果:`LUMOS_SKIP_*` 前綴、`mv` 到新連結後的 push 這類被問到,但 d3 沒涵蓋上面兩條路徑。
2. 修補處的相鄰路徑:push 的目標路徑與 `git -C` 這兩處都經過化簡後的路徑,所以 finding 1 同時影響它們。
3. 新發現同一案例的修前與修後:兩條在修前(4e87b68)與修後都回 `[]`。證據是 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/資安-sonnet/t.py`(修後)與 `t_old.py`(修前)。

固定席節點:這次改動只動 `scripts/hooks/claude/_hookevent.py` 與新掛鉤。`lumos-cli-read` 與 `lumos-cli-lifecycle` 的 INVARIANT(search 排除 superseded、re-inject 只覆蓋 sentinel 之間)不受影響,`design-loop`、`測試假綠形態`、`guard-kill` 也不涉及;本組程式不動 `scripts/lumos`、`merge-claude-settings.py` 與測試。其餘節點未讀正文,判不影響的依據只有牽連檔清單。

臨時目錄 `/tmp/secx.J6Bh` 是我建的,請編排者刪。

最嚴重等級 major,blocking 共 2 條。

來源:r3-合約圖譜-sonnet.md


審的是測試文件組(rest.patch)加固定版本 9b8ce146 的完整程式碼。我沒找到 blocker 或 major。下面的發現都是文件和程式對不上、或條款寫了但測試沒驗,都屬小問題。

1. 條款 S3 與計劃〈做法〉明說「同指令前面動過遠端設定」要照問,但 `git -c remote.*.pushurl=…` 和 `GIT_CONFIG_KEY_n=remote.*` 沒被當成動過遠端設定,於是照樣豁免。
ID: g1
severity: minor
blocking: 否
引句:「同一條指令前面動過遠端設定(`git remote` 的寫入子指令,或 `git config` 碰 `remote.*`、`url.*` 的鍵)時不給豁免」
- 程式的 `_changes_remotes` 只看 `git remote …` 和 `git config remote.*`,沒看全域 `-c remote.*` 或 `GIT_CONFIG_*`。
- 重現:在暫存實驗 repo 裡,`git -c remote.local.pushurl=git@github.com:o/r.git push --no-verify local`,`bypass_reasons` 回 `[]`。
- 對照:同一條 `git -C … -c remote.local.pushurl=… remote get-url --push local` 實際解析出 `git@github.com:o/r.git`,所以這條會真的推到網路位址。
- `GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=remote.local.pushurl GIT_CONFIG_VALUE_0=… git push --no-verify local` 也回 `[]`。
- 對照組:`git config remote.local.pushurl … && git push --no-verify local` 會問(`['no-verify']`),可見只漏了 `-c` 和環境變數這兩種寫法。
- 歸因:有證據的原有漏查。修前版 4e87b682 同三條也回 `[]`。
- 處理:要嘛把 `cfgs` 和 `GIT_CONFIG_KEY` 的 `remote.`/`url.` 鍵併入 `remotes_dirty`,要嘛在〈範圍〉承認。這是 d3 同一類(同指令推論)的第三種形狀。

2. 計劃〈做法〉的逾時預算段前後打架。
ID: g2
severity: minor
blocking: 否
引句:「下面查遠端、查工作樹的 git 子程序用 `_inner_budget()` 當逾時」
- 同一段稍後寫「不用 `_inner_budget` 的 1 秒下限」。
- 程式實際用的是 `_remaining_budget()`,`_inner_budget` 只留作逐字複本(為了鄰居掛鉤的一致性測試)。
- 前一句應改成 `_remaining_budget`。

3. 存活事件檔修剪的描述已過時。
ID: g3
severity: minor
blocking: 否
引句:「存活事件檔滿 512KB 會砍到剩最後 2000 行」
- 修補後的 `_hookevent._trim` 還加了「總大小壓在 `MAX_BYTES//2` 以內」。
- 〈做法〉和〈實務隱患〉的「上限 2000 行」沒同步。
- `Systems/掛鉤存活事件` 的 PITFALL 寫對了。

4. 條款 S3 的「GIT_DIR 一族」範圍比實作寬。
ID: g4
severity: minor
blocking: 否
引句:「整條指令任何地方設過 `GIT_DIR` 一族或用了 `--git-dir`/`--work-tree`」
- 〈做法〉和程式都是「之後的命中」才不豁免。
- 重現:`cd exp && git commit -n -m x; GIT_DIR=real/.git git status` 回 `[]`。
- 程式行為合理,應改條款字句成「該設定之後」。

5. 條款寫了但測試沒驗到的項目。每項我都用 `bypass_reasons` 手動確認過,目前程式行為是對的,只是沒有測試釘住。
ID: g5
severity: minor
blocking: 否
引句:「`git config` 寫入或拆掉 `core.hooksPath`(含 `--unset`、`--unset-all`、`--replace-all`、`--add`、空值、`set`/`unset` 新語法」
- S1:`git config unset core.hooksPath`(新語法 `unset`)沒有案例,只有 `set`。
- S1:前綴 `sudo git …`、`! git …` 沒有案例,`sudo` 只測了接 `lumos`,`!` 只在 `if ! git push; then` 的前一個 push 裡出現。
- S3:「暫存目錄裡用符號連結指回真 repo」。測試的 `mkdir && ln -s … && cd` 是同指令才建,判斷當下目錄不存在,所以不會走到 `realpath` 或 `get-common-dir` 的防線。我手動建好連結的版本,commit 會問(`commit-n`)。
- S3:`GIT_COMMON_DIR`(〈做法〉明列)沒有案例,只有 `GIT_DIR`、`GIT_WORK_TREE`、`--git-dir`、`--work-tree`。
- S3:`git config remote.*`/`url.*` 當「動過遠端設定」沒有案例,只測了 `remote set-url`。
- S3:事件 `cwd` 不是字串沒有案例,只測了 `None`。
- S3:push 目標用 `./` 開頭路徑沒有案例,只測了 `../`、絕對路徑和 `file://`。
- S4 字面判:條款寫「含 `git` 或 `lumos`,且有 `--no-veri`/`hookspath`/`lumos_skip_`/`commit` 加 `-n`」。測試只驗了 `git push --no-verify` 這一種。其他三個字樣和 `lumos` 分支(例如 `lumos "x core.hooksPath`)都沒測。
- S4:「預篩階段丟例外」有測,但 `main` 內 `decide` 吞例外只用 mock 的 `mark` 驗,沒走真的 `guard` 到 `record` 那條。

6. `anchor-baseline.json` 在固定版本是舊的。計劃〈做法〉寫「`lumos anchor approve` 簽進 `governance/anchor-baseline.json`」。
ID: g6
severity: minor
blocking: 否
⚠ 交編排者
- 我用 `git show 9b8ce146:` 逐檔算 sha256 比對,13 個錨點裡有 3 個對不上:`scripts/test_lumos.py`、`scripts/hooks/claude/bypass-ask-hook.py`、`scripts/hooks/claude/_hookevent.py`。目前工作目錄的 HEAD(0b3933d9)也一樣對不上。
- `bypass-ask-hook.py` 在 baseline 有條目但雜湊是舊的,不是漏登記。
- 這是帳本檔,不在審材裡,而且是 wip 提交,可能留到最後一次簽。
- 推送前要先 `anchor approve`,否則 `anchor verify` 會擋推送,而且那道不可跳。

核對後對得上的部分:
- 命中規則的主體對得上:`--no-veri` 前綴判定、commit 吃值旗標集合(`m F C c t`,`S u` 只能黏著)、`--` 之後不看旗標、config 讀寫判定與導向剔除、`export -n` 不算、lumos 指令在段裡任何位置都認、拋棄式只認判斷當下的事實、MAX_GIT_CALLS=4、預算 `外層×0.7` 扣已耗、長度上限 2 萬字、字面判。
- 註冊與安裝:`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`_VENDORED_TREE_FILES`、`enforcement_status` 列(測試列數 24 改 25)、`HOOK_BUDGET` 5、Codex 跳過 Bash matcher。〈回退〉提到的 `_RETIRED_STUB_CLAUDE_HOOKS`、`_RETIRED_CLAUDE_HOOKS`、`graph-sync` 的「Quote-aware 不嚴格」自註、`mods/claude/lumos-guard` 都存在。
- 計劃 frontmatter 與正文引用的所有 `[[連結]]` 節點都存在。
- 三篇 Systems 節點的摘要行格式(前綴與必有鍵)合格。
- `t_*` 測試名都存在。

條款 S1–S5 都有綁定測試,S6 是 `[manual:]`。我另外確認了兩件事:
- 計劃 S6 之外沒有「S1–S5 以外」的條款說法衝突。
- S4 的「10 萬字單詞等各 0.5 秒」那組有逐項計時測試。

固定席節點逐條判:
- `Issues/code-loop守衛main-direct盲區`:不影響。diff 只在 `test_lumos.py` 新增測試,沒碰 code-loop 守衛的 main-direct 路徑。
- `Systems/lumos-cli-read`(search 預設排除 superseded 的 INVARIANT):不影響。`scripts/lumos` 只動三份名單和 enforcement 一列,沒碰 search。
- `Systems/lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間的 INVARIANT):不影響。diff 只在摘要加一行 WHY。這條 WHY 的 `[test:t_bypass_ask_registered]` 只驗安裝名單和 enforcement 列,沒驗它宣稱的「工具自裝檔與錨點名單」兩項,這是上面第 5 點同類的缺口。
- `Systems/design-loop`(處置閘第五步的 INVARIANT):這份是 code- 開頭、帶連字號的迴圈,不屬設計審。計劃本身有 [SN] 且 S1–S5 都有綁定測試,符合「任一條款定義 [綁定測試:有]」。
- `Systems/測試假綠形態`(還原翻紅釘要配前置斷言的 INVARIANT):大致符合。S3 放行清單一律斷言 `out is None`,但沒逐條證明「同一條指令在真 repo 會問」。靠 S1 的相似案例和 S3 的問人清單當對照,不是逐案對照,屬於部分適用。`t_hook_event_trim_tmp_unique` 有「暫存檔名被資料夾佔住」的前置條件,但沒斷言初始檔大小確實超過 `MAX_BYTES`(4000 行×301 位元組約 1.2MB,實際成立)。
- `Systems/guard-kill`(guard kill rc 優先序和 JSON 純度的 INVARIANT):不影響,沒碰 `guard kill`。
- `Systems/pitfalls-code-loop`、`Systems/reversibility-governance-ledger`(★RISK★):不影響,`scripts/lumos` 的改動只有名單與列舉。
- 只列名的其餘節點(bound-tests-gate 等):`bound-tests-gate` 要求 `[test:]` 名稱存在於索引,新條款與兩個 PITFALL 的測試名都在。其餘節點我沒逐篇讀,判為不影響。

最嚴重等級 minor,blocking 共 0 條。

我的臨時檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/w/`,請編排者依規則清掉。

來源:r3-資安-文件-sonnet.md


我已逐 hunk 讀完測試文件組,從攻擊者角度看,沒有發現能被利用的洞。以下是各類的結論,最後三問附在後面。這次只讀了 patch 和 repo 在 9b8ce146 的相關行,沒有另外跑重現,所以結論是讀碼判斷。

## 逐類檢視

1. **執行邊界:已看,無。**
   - `scripts/test_lumos.py` 新增的測試,暫存目錄都用 `mkdtemp`,前綴是 `gctl-bypass-*` 或 `gctl-hookevent-trim-`。清理只對自己建的目錄做 `rmtree(..., ignore_errors=True)`,沒有萬用字元,也沒有寫到暫存目錄外。
   - 假 git 放在獨立的 `gctl-bypass-fakegit-*` 目錄,內容是 `sleep 30`,`chmod 0o755`。PATH 只加在傳給子程序的 `env` 裡,不污染測試行程。
   - 子程序都是固定的 `[sys.executable, 腳本路徑]`,沒有 `shell=True`,也沒有拼接指令字串。
   - `t_bypass_ask_registered` 把 `HOME`、`USERPROFILE`、`CODEX_HOME` 指向假 home 再跑 `merge-claude-settings.py`,不會碰真的 `~/.claude`。
   - `t_hook_event_trim_tmp_unique` 的 `chmod 0o644` 只對自己建的檔做。它對 `.trim` 殘檔的 `utime` 和 `unlink` 也都在自己的暫存目錄內。
   - `scripts/merge-claude-settings.py` 新增 `matcher: "Bash"` 的註冊,指令走既有的 `_hook_cmd`,逾時 5 秒。`_codex_entries` 對 Bash 這條用 `continue` 跳過,所以 Codex 不會收到看不懂的 `ask`。
   - `scripts/lumos` 把 `bypass-ask-hook.py` 加進 `_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES` 和 `enforcement_status`。
   - 反安裝名單(第 25408 行)用 `_GLOBAL_HOOKS + _RETIRED_*`,所以新檔會跟著清。
   - 安裝名單只增不減,沒有新增可任意指定路徑的入口。
2. **文件裡給人照抄的回退步驟:已看,無。**
   - 計劃〈回退〉的步驟只動 repo 內的註冊、名單和測試。
   - 它明講「只拿掉 matcher 不夠,已寫進 settings 的條目不會被剪」,要走空殼期再真刪。
   - 我驗證了 `_RETIRED_STUB_CLAUDE_HOOKS` 和 `_RETIRED_CLAUDE_HOOKS` 都存在於 `scripts/lumos`,步驟可照做。
   - 空殼是直接放行,不是靜默擋住,照做不會讓使用者被卡死或誤放。
   - 〈回退〉也沒有 `rm -rf`、`--force` 或繞閘的指令。
3. **授權範圍有沒有被放寬:已看,無。**
   - 掛鉤只回 `ask`,不回 `allow`。
   - 錯誤、逾時和壞輸入一律放行,這是計劃明寫的設計決定,不是新洞。
   - 掛鉤檔進了錨點名單(`anchor`),被改動會被擋推送,所以對它的防護是增加。
   - 複製到 `~/.codex/hooks` 但不註冊,是死檔,不會被執行。

## 固定席節點判讀

- **lumos-cli-read、lumos-cli-lifecycle、design-loop、測試假綠形態:不影響。**
  - 這次沒有動 `search` 排除邏輯、re-inject 的 sentinel 行為、處置閘判定,也沒有動還原翻紅釘的前置斷言。
  - 新測試都只做正向斷言,而且都是對真實呼叫做斷言,不是重寫實作。
- **guard-kill、pitfalls-code-loop、reversibility-governance-ledger:不影響。**
  - 沒有碰 guard kill 的 rc 優先序或 JSON 輸出。
  - `scripts/lumos` 的改動只是名單增列,沒有新增不可逆操作。
- **code-loop守衛main-direct盲區 Issue:不影響。**
  - 新掛鉤只問人,沒有處理 code-loop 守衛的 main 直推路徑。

## 修補鏡頭三問(測試文件組範圍)

1. **原問題的修復效果:**
   - 我只驗證了測試是否會抓到問題,沒有跑修前與修後的重現。
   - 讀碼可見 `t_hook_event_trim_tmp_unique` 的前置條件(把固定名 `.tmp` 佔成資料夾)會讓舊的固定暫存檔寫法失敗,所以能抓到回歸。
   - 但這是讀碼判斷,不是同一案例修前修後的實跑結果。
2. **修補處的正常、錯誤與相鄰路徑:**
   - 修剪的正常路徑、`os.replace` 失敗的清理分支、長行、權限保留、舊殘檔的清掃,測試都有覆蓋。
   - 我沒有發現相鄰路徑被破壞。
3. **新發現:無。** 修前與修後比對因此不適用。

未驗範圍:程式組(`bypass-ask-hook.py`、`_hookevent.py` 的實際分類邏輯)由另一席資安看,我沒有重現。

最嚴重等級:clean,blocking 共 0 條。

來源:r3-規格符合-sonnet.md


我把規格組的〈做法〉與 [S1]–[S6] 逐條對照,版本取 9b8ce146(工作目錄 HEAD 是 0b3933d9,只多了派工材料提交)。我用 `SourceFileLoader` 載入掛鉤,另外呼叫 `entry()` 實際走了預篩。

## 做法逐點裁定

| 規格點 | 裁定 | 佐證 |
|---|---|---|
| 讀輸入與預篩 | 縮水,見 finding 1 | `-$'n'` 的預篩輸出 False |
| 預篩不記事件、不跑子程序 | 已實作 | `entry()` 預篩為 False 時直接 `return 0` |
| `guard`、事件名、`swallow` | 已實作 | `_guard("pretooluse-bypass-ask-hook", …, swallow=True)` |
| 逾時預算與 git 子程序上限 | 已實作 | `_remaining_budget`、`MAX_GIT_CALLS=4`、cache;沒有 1 秒下限 |
| 長度上限與字面判 | 已實作 | 引號不成對回 `['literal']`;超長走 `_literal` |
| 前處理(註解、遮罩、ANSI、續行、heredoc) | 已實作 | 詞中的 `#` 不當註解、`$(cat <<'EOF'` 內的撇號、續行切開長選項、`$'n'` 解碼,抽測皆符合 |
| 切詞切段、導向剝除 | 已實作 | `2>&1 -n` 仍命中 `commit-n`;`config core.hooksPath 2>/dev/null` 放行 |
| 找 git 指令與全域選項 | 已實作 | `timeout`、`env`、`sudo`、`!`、`if…then`、括號前綴都命中 |
| `no-verify` 與縮寫 | 已實作 | `--no-veri` 命中;merge、rebase、pull 放行 |
| `commit-n` | 已實作 | `-m -n`、`-F -n`、`-mnote`、`-uno` 不命中;`-m x -S -n` 命中 |
| `c-hookspath` | 已實作 | `-c`、`--config-env`、`GIT_CONFIG_KEY_0=…`、`export GIT_CONFIG_KEY_0` 都命中 |
| `config-hookspath` | 已實作 | 帶值、空字串、`--unset`、`set`、`--remove-section core` 命中;只給鍵或加導向放行 |
| `lumos-skip` | 已實作 | 前綴、`env`、`export`、`declare -x`、先賦值再 `export 名稱`、`+=` 命中;`export -n`、`grep` 參數放行 |
| 拋棄式判定(生效目錄、`cd` 追蹤、暫存根、git 確認) | 已實作 | 見下方 S3 |
| 拋棄式判定中 GIT_DIR 一族一律不豁免 | 縮水,見 finding 2 | push 加本機路徑時仍豁免 |
| 命中輸出與三段式 | 已實作 | 理由只用固定文字,不嵌入指令內容 |
| `decide` 與 `bypass_reasons` 拆分 | 已實作 | `main` 只解析、叫 `decide`、印出 |
| `merge-claude-settings.py` 註冊 | 已實作 | Bash matcher、`HOOK_BUDGET` 5 秒、`_codex_entries` 跳過 Bash |
| `scripts/lumos` 註冊 | 已實作 | `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`ANCHOR_FILES` 都有 |

「多做」沒發現。

## S1–S6 裁定

- **S1 縮水:** 只有 `$'…'` 這一項不成立,見 finding 1。其餘抽測都命中:前綴、跨行與續行、詞中 `#`、跳脫字元、`$(cat <<'EOF'` 帶撇號、私用區字元。
- **S2 已實作:** 引號裡的字樣、heredoc 內容、`echo` 與 `grep` 參數、吃值旗標、`HUSKY=0`、merge/rebase/pull、`git config` 讀值都放行。
- **S3 縮水:** 只有 GIT_DIR 加 push 一項不成立,見 finding 2。抽測項目的結果如下:
  - **已存在的暫存 repo:** 放行,包括 `-C`、`cd`、`config`、push 到本機 bare repo 或 `file://`、以及 `cd A && cd B &&` 這種緊接 `&&` 的條件式 `cd`。
  - **仍然問人:**
    - `mkdir`/`git init`、`$(mktemp)`;
    - `cd exp && git -C 真目錄`、`cd` 在子殼層、管線或背景裡、`cd -`、`cd ~`;
    - 符號連結指回真 repo;
    - `config --global`;
    - 網路遠端、`host:path`、沒寫遠端;
    - 同指令 `remote set-url`;
    - 暫存目錄裡的 `lumos-skip`;
    - 缺 `cwd` 或 `cwd` 不是字串。
  - **放行:** 暫存根底下、git 明說不是 repo 的目錄。
- **S4 已實作(⚠ 部分只抽測):** 引號不成對走字面判,`-$'n'` 之外的拆字寫法(`-"n"`、`--no-\⏎verify`、續行後的 `-n`)都過預篩。1000 段和 8000 個 `$(` 在 0.002 秒內判完。1500 個未閉合 heredoc 在 0.019 秒內判完。⚠ 未實測:git 卡住的 5 秒上限、非 UTF-8 輸入。
- **S5 已實作:** 註冊、timeout 5、Codex 跳過、`_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列,對照 `merge-claude-settings.py` 與 `scripts/lumos` 原文都有。
- **S6:** 人工條款,不判。

## Findings

1. 預篩把 ANSI 引號包住的旗標漏掉,[S1] 不成立。
   - 〈做法〉預篩規定「先拿掉引號與反斜線」,但沒有解 `$'…'`。
   - 輸入 `git commit -$'n' -m x`:`bypass_reasons` 會判 `['commit-n']`,但 `prefilter` 回 False,`entry()` 直接放行不問。
   - `-$'\x6e'` 結果相同。
   - [S1] 明列「`$'…'` 之後或包住旗標」必須 ask,實際整支掛鉤端到端放行。
   - 引句:「`$'…'` 之後或包住旗標、跳脫的反引號夾著指令」
   - 預篩該用與 `_Normalizer` 相同的 ANSI 解碼,或在看到 `$'` 時直接放行進分類。
   - 歸因:未判定。
   - 重現:`python3.14 t.py` 與 `t2.py` 在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`。`entry()` 的輸出是「pass」。修前版本沒有跑。

ID: p1
severity: major
blocking: 是

2. GIT_DIR 一族加 push 到本機暫存路徑時仍被豁免,與規格不符。
   - 〈做法〉與 [S3] 規定,整條指令任何地方設過 `GIT_DIR`、`GIT_WORK_TREE`、`GIT_COMMON_DIR` 或用了 `--git-dir`/`--work-tree`,之後的命中一律不給豁免。
   - 輸入 `GIT_DIR=/x/.git git push --no-verify /tmp` 與 `git --git-dir=/x/.git push --no-verify /tmp`:`bypass_reasons` 回 `[]`。
   - 原因:`_git` 把 `eff` 設成 `_UNKNOWN`,但 `_push_target_temp` 對絕對路徑參數不看 `eff`,仍然豁免。
   - 同樣的 commit 與 config 形狀會正確問人。
   - 影響面小:目標已存在且在暫存根底下的本機 bare repo,影響也受限。
   - 引句:「`self.gitdir_seen = True          # 賦值、export、declare、env 前綴都算`」
   - 歸因:未判定。

ID: p2
severity: minor
blocking: 否

縮水+未實作共 2 條

## 回答三問

1. **原問題的修復效果:** 此席只對規格,不做修前修後比較。拋棄式推論類(同指令 `mkdir`、`mktemp`、`set-url`、符號連結、`..`)修後抽測全部照問。
2. **相鄰路徑:** 同類的 push、commit、config 在 GIT_DIR 下並不一致,見 finding 2。
3. **新發現的修前修後:** finding 1、2 都沒跑修前版本,歸因標未判定。

實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`,含 `w/` 與 `h/` 副本,由編排者刪。
