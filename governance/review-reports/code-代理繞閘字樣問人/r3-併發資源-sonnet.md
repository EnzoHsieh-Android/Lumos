severity: major

審的是併發、資源與效能這一鏡頭。環境:Python 3.14、repo 固定版本 9b8ce146 的工作目錄。實驗放在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`。

## 一句人話
掛鉤平常很快,git 卡住時也守得住總預算。但有一個短指令能讓它吃掉十幾 GB 記憶體:同一條指令裡連續寫 `A=$A$A`,變數值每次翻倍。存活事件檔的修剪另有三個小缺口,影響都很輕。

## Finding

1. 變數展開指數膨脹:250 字元的指令能吃掉 14GB 記憶體、跑 10 秒
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
severity: minor
blocking: 否
- 輸入:A 程序進了 `_trim`,在 `read_text` 之後、`os.replace` 之前,B 程序 append 了一行。
- 走到:`lines = f.read_text(...)` 讀的是舊內容,`os.replace(tmp, f)` 換進去的是不含 B 那行的新 inode。B 那行寫到舊 inode,隨之消失。
- 重現:我把 `os.replace` 換成「先 append 一行 `CONCURRENT-LINE` 再真換」,`record` 回 True,行消失(`concurrent line survived: False`)。
- 影響:只掉 telemetry 一行。若剛好是唯一的 `ok`,儀表板會短暫多出 stale 假象。修法留給作者,可以接受並寫進註解。
- 引句:「+    lines = f.read_text(encoding="utf-8", errors="replace").splitlines()[-2000:]」
- 歸因:有證據的原有漏查。舊程式 `tmp.write_text` 加 `os.replace` 是同一個窗口,新碼沒改變它。

3. 修剪被砍時殘檔可能長期留著,最壞幾百 KB
severity: minor
blocking: 否
- 輸入:修剪中程序被砍。我用 `os._exit(9)` 替換 `os.replace` 模擬。
- 現象:留下 `hook-events.08qg6m65.trim`(262KB),不是 `.jsonl.tmp`。清殘檔只在下一次 `_trim` 裡跑,而下一次修剪要等事件檔再長約 256KB。修剪完只剩約 256KB,所以安靜的 repo 裡殘檔可以留很久。
- 清理條件是 mtime 大於 60 秒。被砍後 60 秒內發生的那次修剪不會清它,它就一直留到再下一次修剪。
- `.gitignore:36` 蓋掉 `governance/runtime/`,所以不會污染 `git status`。但 `scripts/lumos:24499` 的註解提到有消費專案曾把 `hook-events.jsonl` 提交進版控,那種專案的 `.trim` 會變成未追蹤檔。
- 引句:「+            if time.time() - old.stat().st_mtime > 60:」
- 歸因:有證據的修復缺口。「清殘檔」是這輪新加的,上面描述的現象是它的行為邊界。

4. 目錄唯讀時,事件檔會無限長大,`record` 仍回 True
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
