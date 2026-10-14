severity: major

彙總載體,非新增審查席。39 條由九份原報告逐字彙整(合約圖譜席用它更正一句引句後重交的版本 r2-合約圖譜-sonnet-引句更正.md;原檔已記帳不動),只在每條 severity 行前加 ID 行。


來源:r2-正確性-sonnet.md


我載入了修前(b5be3aad)和修後(4e87b682)兩版掛鉤,用 `bypass_reasons` 逐案對跑,實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`。下面的指令都是 `bypass_reasons(指令, cwd)`,輸出寫成 `(修前, 修後)`。除另外標明的 cwd,都用 `/Users/enzo/.../Word-wild-search-bypass`;凡涉及暫存根的案例,都把 `_temp_roots` 換成實驗用的假暫存根。

## Findings

**1. 續行合併的引號追蹤沒跟著重構,撇號會讓後面的 `\⏎` 不被合併,續行上的 `--no-verify` 漏問**

ID: c1
severity: major
blocking: 是

引句:「不在單引號裡的「反斜線加換行」換成空白。」

- 走到的位置:`_join_continuations` 用自己一套簡化的單、雙引號狀態。註解(`# don't`)、頂層 heredoc 內文的撇號、`$'it\'s'` 都會讓它誤判成「在單引號裡」。
- 之後的 `\⏎` 就不被合併。`_Normalizer` 照原樣輸出 `\⏎`,shlex 把被跳脫的換行變成一個內容為 `"\n"` 的詞,`_is_sep` 又判它是分隔符,指令在續行處被切斷,續行上的旗標落到沒有 git 的段裡。
- 重現:

| 輸入 | 結果 |
|---|---|
| `# don't skip⏎git commit -m x \⏎  --no-verify` | `([], [])` |
| `# don't skip⏎git push origin main \⏎ --no-verify` | `([], [])` |
| `# don't skip⏎git commit -m x \⏎  -n` | `([], [])` |
| `cat <<EOF⏎it's⏎EOF⏎git push \⏎ --no-verify` | `([], [])` |
| 同一條拿掉 `# don't skip` 那行 | `(['no-verify'], ['no-verify'])` |

- 這是代理「被擋後順手繞」的典型長相:英文註解加多行 git。這輪才修好撇號對 `_Normalizer` 的影響,同族的 `_join_continuations` 沒掃到。
- 應該:續行合併改由 `_Normalizer` 做(它已經精確追蹤引號、註解、heredoc),在非單引號狀態直接吃掉 `\⏎`。
- 歸因:註解與頂層 heredoc 兩個變體是有證據的原有漏查(修前修後都是 `[]`)。
- `$'it\'s'` 變體是有證據的修復回歸:
  - 命令:`echo $'it\'s'; git push \⏎ --no-verify`
  - 結果 `(['literal'], [])`:修前靠切不動走字面判才問,修後重構讓它切得動卻判漏。

**2. 重導向目標被當成推送的遠端,推到暫存位置就整條豁免**

ID: c2
severity: major
blocking: 是

引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」

- `_parse_git` 只丟掉 `>`、`>>`、`&>` 這種運算子,沒丟它後面的目標檔名和 `2>` 的 `2`。`_push_remote_arg` 取第一個非旗標參數,於是 `> /tmp/push.log` 的 `/tmp/push.log` 變成遠端。
- 它是本機路徑又落在暫存根底下,`_push_target_temp` 回 True,`_exempt` 整條放行。
- 重現(cwd 是真 repo):

| 輸入 | 結果 |
|---|---|
| `git push --no-verify > /tmp/push.log 2>&1` | `([], [])` |
| `git push --no-verify >/tmp/push.log` | `([], [])` |
| `git push --no-verify &> /tmp/push.log` | `([], [])` |
| `git push --no-verify >> /tmp/push.log` | `([], [])` |
| `git push > /tmp/p.log --no-verify` | `([], [])` |
| `git push --no-verify 2>/tmp/err.log`(吃到 `2`,不是路徑) | `(['no-verify'], ['no-verify'])` |

- 代理把輸出導到暫存目錄(例如 scratchpad `/private/tmp/claude-501/.../push.log`)是常態,這就等於「不寫遠端的 `--no-verify` 推送」被豁免。計劃〈範圍〉沒承認這個攔不到。
- 應該:在 token 層先剝掉整個重導向(含 fd 數字與目標),再交給各解析函式。
- 歸因:有證據的原有漏查(修前修後相同)。

**3. 同一個根因的另一面:重導向殘留讓讀設定被誤問,`-m ">"` 吞掉 `-n`**

ID: c3
severity: minor
blocking: 否

引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」

- 誤問:`_config_writes_hookspath` 用位置參數個數判寫入,讀值加重導向就多出位置參數。

| 輸入 | 結果 |
|---|---|
| `git config core.hooksPath 2>/dev/null`(讀值) | `(['config-hookspath'], ['config-hookspath'])` |
| `git config core.hooksPath 2>&1` | `(['config-hookspath'], ['config-hookspath'])` |
| `git config core.hooksPath > /tmp/h.txt` | `(['config-hookspath'], ['config-hookspath'])` |
| `git config --get core.hooksPath 2>/dev/null` | `([], [])` |
| `git config core.hooksPath` | `([], [])` |

- 計劃量測說真目錄裡讀值出現 7 次,所以這個誤問是真的會撞到。
- 漏問:`_is_redirect` 比對的是已 `_unmask` 的詞,引號裡的 `">"` 也被當成運算子丟掉,`-m` 的值消失,後面的 `-n` 被當成它的值。

| 輸入 | 結果 |
|---|---|
| `git commit -m ">" -n` | `([], [])` |
| `git commit -m "<" -n` | `([], [])` |
| `git commit -F '>' -n` | `([], [])` |

- 一般訊息不會剛好是 `>`,所以降為 minor。
- 同族:`_note_created` 的 `git clone URL 2>&1` 會把 `2` 當成目標目錄,`cd 倉庫名` 因此被誤問。
- 歸因:有證據的原有漏查(修前修後相同)。

**4. 反引號被反斜線跳脫時仍被當成指令替換,吞掉中間的繞閘指令**

ID: c4
severity: minor
blocking: 否

引句:「close = text.find("`", i + 1)」

- 輸入 `echo \`; git push --no-verify; echo \``,裸的 `\`` 在 shell 裡是字面反引號。`_Normalizer` 保留 `\`` 原樣,`_cmdsub_span` 看到反引號就找下一個,把中間整段換成佔位詞。
- 結果 `(['no-verify'], [])`:修前問,修後漏。
- 實務上要有成對的跳脫反引號夾著指令才會發生,所以給 minor。
- 歸因:有證據的修復回歸(兩版逐案對照)。

**5. export 的 `GIT_DIR` 與 `GIT_WORK_TREE` 沒追蹤**

ID: c5
severity: minor
blocking: 否

引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」

- 只有行內前置賦值 `GIT_DIR=… git commit` 會把生效目錄改成未知。`export GIT_DIR=…`(或 `declare -x`)後面的 git 看不到。
- 修前修後都漏,但行內前置賦值這條路已經補了,export 這條沒補。

| 輸入 | 結果 |
|---|---|
| `cd $(mktemp -d); export GIT_DIR=/Users/someone/work/repo/.git; git commit -n` | `([], [])` |
| `export GIT_DIR=/Users/someone/work/repo/.git; cd /tmp; git commit -n` | `([], [])` |
| `cd $(mktemp -d); GIT_DIR=/Users/someone/work/repo/.git git commit -n` | `([], ['commit-n'])`(對照,行內前置) |

- 這是同一個漏洞的另一條路徑:`_mark_exported` 只認 `LUMOS_SKIP_` 與 `GIT_CONFIG_`。
- 歸因:有證據的原有漏查。

**6. mktemp 只看指令名,`-p` 或範本路徑指到真 repo 底下也算拋棄式**

ID: c6
severity: minor
blocking: 否

引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」

| 輸入 | 結果 |
|---|---|
| `cd $(mktemp -d -p /Users/someone/work/repo); git commit --no-verify -m x` | `([], [])` |
| `cd $(mktemp -d /Users/someone/work/repo/XXXX); git commit --no-verify -m x` | `([], [])` |
| `cd $(mktemp -d --tmpdir=/Users/someone/work/repo); git commit --no-verify -m x` | `([], [])` |
| `cd $(mktemp -d -p .); git commit --no-verify -m x` | `([], [])` |

- 新目錄位在真 repo 的工作樹內,commit 會落到上層真 repo。需要刻意這樣寫,所以只給 minor。
- 歸因:有證據的原有漏查。

**7. git 子程序卡住時,四次呼叫的總耗時超過註冊的 5 秒逾時**

ID: c7
severity: minor
blocking: 否

引句:「timeout=_inner_budget(default=5.0))」

- `_inner_budget` 有 1 秒下限。第一個 git 用掉 3.5 秒後,後三個各拿 1 秒,上限 4 個呼叫(`MAX_GIT_CALLS`)。
- 重現:用一支 `sleep 30` 的假 `git` 放進 PATH,`--budget 5`,五個存在的暫存目錄各一條 `git -C … commit -n`。實測 `bypass_reasons` 耗時 6.52 秒,結果還是 `['commit-n']`。
- 但 Claude Code 在 5 秒就把掛鉤砍掉,這條本該問的指令在 git 卡住時改成靜默放行,存活事件也寫不進去。
- 只有 git 真的卡住才會發生。程式自己的 docstring 就點名過「連續呼叫超過天花板」這種結構性問題。
- 應該:把「剩餘預算」在 `_git_out` 內用絕對截止時間算,到期就直接回 `(None, "")`。
- 歸因:未判定(舊版沒有 4 次上限,我沒對舊版造同樣的卡住場景)。

**8. 存活事件修剪的行數上限與位元組上限不一致,新測試也沒蓋清理分支**

ID: c8
severity: minor
blocking: 否

引句:「keep = f.read_text(encoding="utf-8", errors="replace").splitlines()[-2000:]」

- 修剪保留 2000 行,觸發門檻是 512KB。平均每行超過約 262 位元組時,修剪完仍超過上限,之後每一次 `record` 都整檔重讀重寫。
- 重現:repo 路徑 150 字加 120 字 note 的 error 事件,寫 3000 筆後檔案 1,010,000 位元組、2000 行,必然每次都再修剪。
- 正常路徑(這個 repo 的路徑加 ok 事件)平均 208 位元組,實測 3000 筆後 515,632 位元組,剛好跨過門檻,下一筆之後穩在 2000 行附近,不構成問題。
- `mkstemp` 建的檔權限是 0600,`os.replace` 後事件檔從 0644 變 0600。單人使用不影響。
- `t_hook_event_trim_tmp_unique` 能抓到原本的錯:固定暫存名被資料夾佔住時,舊版留在 4001 行,新版 2000 行。
- 但沒蓋 `os.unlink(tmp)` 的失敗清理分支。把清理拿掉,測試仍綠。
- 歸因:未判定。

## 三問與正向主張

**① 原問題的修復效果**

我獨立跑了 `r2-intake.md` 配對案例表的 19 個案例,每個都對兩版跑 `bypass_reasons`(cwd=`/Users/someone/work/repo`),全部與表一致:

- repair 類修前 pass、修後 ask:
  - 詞中間 `#`(`git checkout -b fix#1 && git push --no-verify`)
  - 訊息 heredoc 有撇號後 `-n`
  - `git commit -m "(" -n`
  - `--git-dir` 指回真 repo
  - `config --global` 在暫存目錄
  - mktemp 子路徑用 `..` 繞出
  - cd 到不存在又沒建的目錄
  - timeout 前綴的 lumos
  - `--config-env`
  - 先賦值再 export 名稱
  - 續行後頂在行首的 `-n`
- preserve 類兩版皆 pass 或皆 ask:
  - heredoc 內文提繞閘
  - 引號裡的說明文字
  - 詞首註解
  - mktemp 新目錄提交
  - 同指令建的暫存目錄
  - 真目錄推送
  - LUMOS_SKIP 接跑測試
  - git 前的 LUMOS_SKIP

另加 31 個真實形狀的對照全部成立,涵蓋 `-qn`、`-an`、`-sm … -n`、`--amend -n`、`-C` 目錄、背景 `&`、`( … )`、`{ …; }`、`for/if` 內、`| tail`。

另外拿 `/Users/enzo/harness/lumos-toolchain/governance/runtime/events` 的 29317 條不重複 Bash 指令,兩版重放比對。扣掉事件帳截成 500 字的,過預篩 270 條,兩版判定不同的 6 條全是修後「問」。這 6 條的目錄在重放時已不存在,不是新漏問。

**② 修補處的正常、錯誤與相鄰呼叫路徑**

- 引號與 `$(` 重開一層:指令替換裡的引號與括號、`"$(echo ")")"`、heredoc 在 `$(…)` 裡,實測正常。
- 子殼層與背景:`(cd X && …)`、`cd X &`、`cd X & git commit -n` 都正確。
- 變數、export、declare 的 LUMOS_SKIP 路徑:`LUMOS_SKIP_X=1; export LUMOS_SKIP_X; git push`、`declare -x LUMOS_SKIP_X=1; git push` 實測成立。
- 隨機片段共 3 萬條都沒丟例外。
- 效能:最壞約 1.8 秒(`$(a ` 重複 5000 次、`$((` 重複 6000 次)。其餘各種近兩萬字的形狀都在 0.1 秒內。
- 不成立的路徑:findings 1、2、4、5、6 就是相鄰路徑上沒蓋到的。

**③ 新發現在修前、修後的結果**

- 同一案例兩版結果都已寫在各 finding。
- 1 的 `$'…\'…'` 變體與 4 是修復後新出現的漏。
- 其餘(1 的註解與 heredoc 變體、2、3、5、6)修前修後相同,屬原有漏查。

未驗範圍:

- 沒跑 `test_lumos.py` 子集。
- 沒驗 `scripts/lumos`、`merge-claude-settings.py`(文件組)。
- Codex 路徑沒驗。

固定席節點:

- 全部判不影響:lumos-cli-read 的 search 排除 superseded、lumos-cli-lifecycle 的 re-inject 只覆蓋 sentinel 之間、design-loop 的處置閘第五步、guard-kill 的 rc 優先序與 `--json` 純度。
- 測試假綠形態的 INVARIANT(還原翻紅釘要有前置斷言):
  - 新測試 `t_hook_event_trim_tmp_unique` 的 4000 行起始檔(約 1.2MB,超過 512KB)隱含證明修剪路徑被走到。
  - 還原修法會翻紅(舊版 4001 行 vs 新版 2000 行)。
  - 但清理失敗分支沒有翻紅釘(finding 8)。
- 角色卡 be-api-compat、be-authz:判不影響。這支是本機 PreToolUse 掛鉤,沒有對外 API 欄位,也沒有端點與資料授權。

最嚴重等級是 major,blocking 共 2 條(1、2)。

主要檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`、`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/_hookevent.py`。

來源:r2-併發資源-sonnet.md


臨時檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/併發資源-sonnet/`。我用 4e87b682 的 `bypass_reasons` 量時間,用 `_hookevent.record` 做併發與砍程序實驗,修前版本拿來對照。

## Finding

1. `_replace_cmdsubs` 搭配 `_match_paren` 是平方時間,20000 字內最慢的輸入是大量沒配對的 `$(`。
   - 引句:「close = _match_paren(text, i + 1)」
   - 輸入:`"git commit -n; " + "$(" * 9990`(約 2 萬字)。
   - 路徑:每個沒配對的 `$(` 都從該處掃到字串尾,找不到才回 -1,然後外層迴圈只前進一格。
   - 命令:`bypass_reasons(cmd, "/Users/enzo")`,結果 `['commit-n']`,耗時 3.17 秒。
   - 同形的 `"$(("*6000` 要 1.65 秒,`'"$("' * 3000` 要 0.66 秒。
   - 整個程序實測:hook 以 `--budget 5` 執行(註冊表給這支的逾時是 5 秒),從 stdin 進、cwd 是暫存 repo,牆鐘 3.18 秒。正常指令是 0.09 秒。
   - 後果:Claude Code 以 5 秒殺掉 hook 就等於放行,而這個平方形狀已吃掉預算的 64%。
   - 應該是:用一次線性的堆疊配對,或預先算好每個 `(` 的配對位置。
   - 其他形狀(8 種引號、heredoc、註解、`&`、mkdir、remote add、`cd` 重複)在 2 萬字內都在 0.1 秒以下;例外是 heredoc 不終止 0.37 秒(修前量到,修後 0.03 秒)、全是反引號 0.89 秒(修前 0.84 秒,不是這次修補造成)。
   - 歸因:有證據的修復回歸。
     - 修前 `b5be3aad` 同一輸入 0.01 秒。
     - 修後 `4e87b682` 為 3.17 秒。
     - 修前沒有逐個 `$(` 的配對掃描。
   - 我沒有實測更慢的機器。「再慢 1.6 倍就超過 5 秒」是用 3.18 秒推算的。
ID: r1
severity: minor
   - blocking: 否
   - 降級理由:這是問人層,失敗放行是設計決定。輸入也是人為灌的畸形指令,正常指令不會有上千個沒配對的 `$(`。

2. `_hookevent.record` 修剪時,程序在 `mkstemp` 之後、`os.replace` 之前被殺,`.trim` 殘檔沒人清,會越積越多。
   - 引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
   - 路徑:清理只在 `except OSError` 裡;SIGKILL、SIGTERM 或 hook 逾時被殺不會進去。
   - 重現:在子程序裡把 `os.replace` 換成 `os.kill(os.getpid(), 9)`,連跑 3 次。結果留下 3 個各 218057 位元組的 `hook-events.*.trim`,沒有任何程式會去掃。
   - 整個目錄在 `.gitignore`(`governance/runtime/`),所以不會冒出 `git status` 的雜檔。
   - 殘檔產生的條件很窄,要被殺在修剪那幾毫秒內。
   - 現在固定名字改隨機名,修了 r1 說的「暫存名被佔住就永遠修剪失敗」。代價就是殘檔不再被下一次覆蓋。
   - 建議:修剪前順手清掉 `hook-events.*.trim` 中超過一分鐘的舊檔,或是接受並寫成回頭條件。
   - 歸因:有證據的修復回歸。
     - 修前固定的 `.jsonl.tmp` 會被下次覆蓋。
     - 修後是隨機名,殘檔不會被覆蓋。
ID: r2
severity: minor
   - blocking: 否

## 其他已驗

- **`_git_out` 的上限與快取**:每次 `bypass_reasons` 開頭都重設 `calls` 和 `cache`,沒有跨呼叫殘留,超過 4 次回 `(None, "")`。這部分沒有發現問題。
- **`_inner_budget()` 預算起點**:`entry` 開頭先叫一次,起點在進場、早於 `guard` 裡的 `git rev-parse`。同一程序重複呼叫 `entry` 時,`_BUDGET_START` 是模組全域變數,只設定一次,測試裡的第二次起會一律拿到 1 秒下限。正式環境每個事件各自起一個程序,不受影響。
- **多會談同時修剪**:8 個程序各寫 400 筆,0.21 秒完成,0 行壞 JSON,沒有留下 `.trim`。是否掉行我量不出來,因為修剪本來就會丟舊行。讀取後到 `replace` 之前別人追加的行理論上會被覆蓋,但這是問人層的存活紀錄,我沒有當 finding。
- **檔案權限**:`mkstemp` 建出 0600,修剪後 `hook-events.jsonl` 從 0644 變 0600(實測)。只有單一使用者,不影響。
- **磁碟滿**:修剪寫入拋 `OSError` 時會 `unlink` 暫存檔再走 `except OSError`,不會殘留。我沒有真的造出磁碟滿,只讀程式判斷。
- **⚠ 交編排者**:git 卡住時的最壞總耗時,我沒有實測。從程式推算:`guard` 的 `_root_from_cwd` 最多 3 秒,再加 4 次 `_git_out`,每次下限 1 秒,總計約 7 秒,超過 5 秒的 hook 逾時。同樣只是放行,而且需要 git 真的卡住,所以沒列為 finding。

## 三問

1. **原問題的修復效果**:暫存名衝突已修好,多程序併發修剪實測無壞行、無殘檔。
2. **相鄰呼叫路徑**:正常指令 0.09 秒;`_git_out` 與預算起點正常;唯一退化是 finding 1 的修後新平方成本。
3. **同一案例修前與修後**:
   - 沒配對的 `$(`:修前 0.01 秒,修後 3.17 秒。
   - 修剪中被殺:修前殘檔會被下次覆蓋,修後會累積。

## 固定席節點

- **`Systems/lumos-cli-read`、`lumos-cli-lifecycle`**:其 ★INVARIANT★ 是 `search` 預設排除 superseded、re-inject 只覆蓋 sentinel 之間。`_hookevent.py` 只是列在牽連檔,本席沒讀到 `search` 或 re-inject 相關的 diff。不影響。
- **`design-loop`、`測試假綠形態`、`guard-kill`**:這三條合約分別管設計審的材料格式、還原翻紅釘要有前置斷言、`guard kill` 的 rc 與 JSON。本席沒讀到相關改動。測試假綠那條也適用於 finding 1,即「修了平方成本」的測試要證明測到的輸入真的走到 `_match_paren`。不影響。
- **`pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★)**:牽連檔是 `scripts/lumos`,屬文件註冊組,不在本席範圍。不影響。
- **`Issues/code-loop守衛main-direct盲區`**:牽連的是 `test_lumos.py`,我沒有讀它。不影響本席鏡頭。

最嚴重等級 minor,blocking 共 0 條。

來源:r2-邊界輸入-sonnet.md


我載入修後(4e87b682)與修前(b5be3aad)兩版,跑了約 450 條邊界輸入。修前修後的輸出逐條對照,「歸因」就是這樣得出的。實驗目錄是我自己建的,收尾已刪。

## Findings

**1. `git push` 沒寫遠端、只用 `>` / `&>` / `<` 導向暫存檔時,導向的檔名被當成推送目標,整條被判成拋棄式而放行**
ID: e1
severity: major
blocking: 是
- 引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」
- 走到的地方:`_parse_git` 只丟掉 `>` 這個運算子,後面的檔名留在 args。`_push_target_temp` 取第一個位置參數當遠端,`/tmp/x.log` 是本機路徑且在暫存根底下,於是被當成拋棄式。
- 重現(cwd 是真 repo,輸出都是 `bypass_reasons` 的回傳):
  - `git push --no-verify > /tmp/x.log` 回 `[]`,應為 `['no-verify']`
  - `git push --no-verify >/tmp/x.log 2>&1` 回 `[]`
  - `git push --no-verify &> /tmp/x.log` 回 `[]`
  - `git push > /tmp/x.log --no-verify` 回 `[]`
  - `git push --no-verify < /tmp/in` 回 `[]`
- 對照組:有寫遠端的 `git push origin --no-verify > /tmp/x.log` 會問,`git push --no-verify 2>/tmp/err` 也會問(第一個位置參數是 `2`)。
- 應該怎樣:解析 git 參數時,把重導運算子連同它後面的目標一起丟掉。
- 歸因:有證據的原有漏查。修前與修後這 5 條輸出都一樣。
- 補充:新測試 `t_bypass_ask_throwaway_targets` 沒有任何一條帶重導的推送。代理把輸出導到 `/tmp/*.log` 是很常見的寫法,所以我給 major。

**2. 引號裡剛好是 `>` 或 `<` 的詞也被當重導丟掉,把 `-m` 的值位移,`-n` 被吃掉**
ID: e2
severity: minor
blocking: 否
- 引句:「return words[j], [a for a in words[j + 1:] if not _is_redirect(a)], gdirs, cfgs, moved」
- 原因:`_unmask` 先還原遮罩,`_is_redirect` 才判斷。引號裡的 `'>'` 還原後跟真的 `>` 沒有分別,被丟掉。`-m` 的值消失後,`-n` 反而被當成 `-m` 的值。
- 重現:
  - `git commit -m '>' -n` 回 `[]`(修前也是 `[]`)
  - `git commit -m ">>" -n` 回 `[]`
  - 這輪新加的遮罩帶來一條修前沒有的路:指令本身含私用區字元時,`git commit -m '<U+E006>' -n` 修前回 `['commit-n']`、修後回 `[]`。`<U+E005>` 與 `<U+E004><U+E006>` 同樣。
  - 私用區 U+E000 到 U+E00A 是 Nerd Font 的 Pomicons 區段,不算絕對不會出現。
  - 其他私用區字元(`<U+E003>`、`<U+E004>` 單獨出現)沒影響。
- 應該怎樣:`_is_redirect` 在切詞階段、用 `_Sep` 那種「切詞時認定」的標記判斷,不要看還原後的字串。
- 歸因:`'>'` 這條是有證據的原有漏查。私用區字元這條是有證據的修復回歸(遮罩機制的副作用),只此一條。

**3. 有撇號的註解會讓後面的反斜線續行不再接起來,`--no-verify` 被切成另一段而漏掉**
ID: e3
severity: minor
blocking: 否
- 引句:「out.append(" " if cmd.startswith("\\\n", i) else cmd[i:i + 2])」
- 走到的地方:`_join_continuations` 只追蹤引號,不認註解,也不認 `$'…'` 內的 `\'`。註解裡的 `don't` 讓它誤以為單引號打開了,之後的 `\<換行>` 不會被接起來。shlex 把換行當分隔符,`--no-verify` 變成獨立一段。
- 重現:
  - `"# don't do this\ngit push \\\n  --no-verify"` 回 `[]`,修前也是 `[]`
  - `"# don't do this\ngit commit -m x \\\n  -n"` 回 `[]`
  - `"echo \"don't\" # it's\ngit commit \\\n  --no-verify"` 回 `[]`
  - 修前不同的一條:`"echo $'a\\'b' ; git push \\\n --no-verify"` 修前回 `['literal']`,修後回 `[]`,因為修後把 `$'…'` 換成佔位詞,但 `_join_continuations` 仍不認 `$'`。
- 同一函式還有一個小問題:續行換成一個空白,而不是 bash 的「直接去掉」。所以 `git push --no-\<換行>verify` 回 `[]`(bash 會接成 `--no-verify`),`--no-veri\<換行>fy` 卻湊巧命中。
- 應該怎樣:`_join_continuations` 要認註解與 `$'`,或改成在 `_Normalizer` 裡處理續行。
- 歸因:前三條是有證據的原有漏查,`$'a\'b'` 那條是有證據的修復回歸。

**4. `git remote set-url --add` / `--delete` 被當成「把位址換成暫存路徑」,推送被誤判為拋棄式**
ID: e4
severity: minor
blocking: 否
- 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
- 重現:
  - `git remote set-url --add o /tmp/lsw/rem && git push --no-verify o` 修後回 `[]`、修前回 `['no-verify']`
  - `git remote set-url --add --push origin /tmp/lsw/rem && git push --no-verify origin` 修後 `[]`、修前 `['no-verify']`
  - `--delete` 同樣被放行。
- 原因:`--add` 是在原位址之外再多一個,原本的真遠端還在,推送會兩邊都推。`--delete` 是刪掉符合的位址,不是設定新位址。
- 應該怎樣:`--add`、`--delete` 不要記進 `added`。
- 歸因:有證據的修復回歸(修前問、修後放行)。

**5. `git -C 別處 remote add 名稱 暫存路徑` 設的遠端,被拿去判斷目前目錄那個 repo 的同名遠端**
ID: e5
severity: minor
blocking: 否
- 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
- 重現:cwd 是真 repo,`git -C /tmp/lsw/x remote add origin /tmp/lsw/rem && git push --no-verify origin` 回 `[]`。實際推的是真 repo 的 origin。
- 原因:`added` 是整條指令共用的一個字典,沒有按生效目錄分開。
- 應該怎樣:`added` 以生效目錄加遠端名稱為鍵。
- 歸因:有證據的原有漏查(修前也是 `[]`)。

**6. `export GIT_DIR=…`(或 `GIT_WORK_TREE`)不會讓生效目錄變成未知,拋棄式豁免繼續成立**
ID: e6
severity: minor
blocking: 否
- 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
- 重現:`cd $(mktemp -d); export GIT_DIR=/Users/enzo/x/.git; git commit --no-verify` 回 `[]`。
- 對照:同一條改成行內 `GIT_DIR=… git commit` 或 `env GIT_DIR=…` 會問。修前這兩種行內寫法都漏,修後補上了,但 `export` 形式沒補。
- 歸因:有證據的原有漏查。

**7. `export` 只認「export 名稱」,`declare -x 名稱` 與 `typeset -gx 名稱`(只給名稱、不帶 `=`)沒跟上**
ID: e7
severity: minor
blocking: 否
- 引句:「handler = {"cd": self._cd, "pushd": self._lose_dir, "popd": self._lose_dir, "export": self._export,」
- 重現:
  - `LUMOS_SKIP_X=1; export LUMOS_SKIP_X; git commit -m x` 修後回 `['lumos-skip']`、修前回 `[]`
  - `LUMOS_SKIP_X=1; declare -x LUMOS_SKIP_X; git commit -m x` 回 `[]`
  - `LUMOS_SKIP_X=1; typeset -gx LUMOS_SKIP_X; git commit -m x` 回 `[]`
  - 另有 `set -a; LUMOS_SKIP_X=1; git commit -m x` 回 `[]`,屬於承認範圍內的寫法。
- 應該怎樣:`_declare` 比照 `_export`,名稱已在 `variables` 裡就標記為匯出。
- 歸因:有證據的原有漏查。`export` 是這輪補的,`declare` 同族沒一起補。

**8. `cd` 放在管線裡、或放在 `||` 與條件後面,仍被當成真的換了目錄**
ID: e8
severity: minor
blocking: 否
- 引句:「handler = {"cd": self._cd, "pushd": self._lose_dir, "popd": self._lose_dir, "export": self._export,」
- 重現:
  - `cd /tmp | cat; git commit --no-verify` 回 `[]`,`cd /tmp 2>&1 | tail; …` 也是
  - `cd /tmp |& cat; …` 回 `[]`
  - `cd /real/nope || cd /tmp; …` 回 `[]`
  - `[ -d /nope ] && cd /tmp; …` 回 `[]`
- 原因:bash 裡管線的每一段在子殼層跑,`cd` 影響不到後面。這輪補了 `&` 背景的還原,管線沒補。後兩條是條件式 `cd`,分析把它當成無條件執行。
- 應該怎樣:`|`、`|&` 後的段還原目錄(跟 `&` 一樣);條件式 `cd` 保守起見讓生效目錄變 `_UNKNOWN`。
- 歸因:有證據的原有漏查。
- 補充:`&` 本身我驗過沒問題:`cd /tmp & git commit --no-verify`、`(cd /tmp & …)`、`cd /tmp &> /dev/null; …` 三種結果都符合 bash。

**9. 以下寫法會漏問或誤問,但屬於有心改寫或罕見,我只列出不要求處理**
ID: e9
severity: minor
blocking: 否
- `$(mktemp -d -p /真repo底下)`:只看指令的第一個詞是不是 `mktemp`,就判成暫存目錄,沒看 `-p` 或模板路徑。
  - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
  - 重現:`cd $(mktemp -d -p /Users/enzo/orca) && git commit --no-verify` 回 `[]`。
  - `mktemp -d /Users/enzo/orca/xXXXXXX` 與 `$(mktemp -d >/dev/null; echo /Users/enzo/orca)` 同樣回 `[]`。
  - 歸因:原有漏查。
- `git init -b main DIR`、`git init --template X DIR`、`git clone --depth 1 URL`、`git clone -b main URL` 這幾種寫法,值旗標沒被跳過,目標抓錯,於是多問(修前放行)。
  - 引句:「target = pos[0] if pos else "."」
  - 歸因:有證據的修復回歸,方向是多問,不危險。
- `git commit -$'n'` 修後回 `[]`、修前回 `['commit-n']`。
  - 引句:「self.out.append("__LUMOS_ANSI__")」
  - 原因:`$'…'` 被換成佔位詞,內容丟了。
  - 歸因:有證據的修復回歸,屬有心改寫。
  - `git push $'--no-verify'` 與 `git $'push' --no-verify` 修前修後都回 `[]`。
- `git config --remove-section core` 與 `--rename-section core x` 會拆掉 `core.hooksPath`,回 `[]`。`〈範圍〉`只承認 `--edit` 與直接改檔。
- 以下是設計上已承認或不危險,我確認過,不當 finding:
  - `echo git push --no-verify` 這類沒加引號的字面提到會問。
  - `$(…)`、反引號、`bash -c` 裡的指令不看。
  - `git -ccore.hooksPath=/x` 黏在一起的寫法 git 本身不收。

## 已驗為正常的路徑(輸入、預期、修前修後結果相同或更好)
- **引號與註解**
  - `$(` 在單引號、雙引號、反斜線之後,都正確:`echo '$('`、`echo \$(foo`、`"\$(…)"` 都正常。
  - `$'…'` 不閉合或內含 `\'` 時,未閉合與閉合兩種都沒有崩潰。
  - `#` 接在 `$`、`{`、`=` 之後不當註解:`echo $#`、`${#x}`、`x=#a`、`a#b` 修後都問、修前漏。
- **heredoc**
  - 在 `$(` 裡、在雙引號 `$(` 裡、結束字是 `)` 或 `A B` 都正確。
  - 找不到結束字時停止剝除,寧可多問。
  - 結束字帶尾端空白或 Tab 時不算結束字,跟 bash 一致。
  - `git commit -m "$(cat <<'EOF'…EOF)" --no-verify`(內文含 `don't`、括號、引號)修後回 `['no-verify']`、修前回 `['literal']`。
- **GIT_CONFIG_KEY_n 與 --config-env**
  - `GIT_CONFIG_KEY_0=core.hooksPath` 的值大小寫都命中(`CORE.HOOKSPATH` 也是),`export` 形式命中,沒 `export` 的單獨賦值不命中,符合 bash。
  - `--config-env=core.hooksPath=X` 與分開寫都命中(修前漏)。
- **export / declare**
  - `export -f`、`-p`、`-fn` 都命中。
  - `declare -gx`、`declare -x`、`typeset -x`、`declare -xn` 帶值時命中。
  - 沒 `-x` 的 `declare` 與 `declare -p` 不命中。
- **cwd 與目錄**
  - `cwd` 是 `/` 問、`/tmp` 與 `//tmp` 放行、`rel`、空字串、`None`、`/tmp/../Users` 問、不存在的 `/tmp/zzzz` 問。
  - `mkdir -p a b c`、`--parents`、`-m 755` 都正確;`git init --bare DIR` 正確。
  - `d=$(mktemp -d); cd $d/../..` 問(修前漏)。
  - `cd /tmp &> /dev/null` 與 `cd /tmp & git …` 的行為符合 bash。
- **commit -n 解析**
  - 組合旗標與帶值旗標的跳過都對:`-mn`(訊息 `n`)、`-Sn`、`-un`、`-m -n`、`-F -n`、`-- -n` 都不誤判。
  - `-vn`、`-anm`、`-nq`、`-S"key" -n` 命中。
- **pitfall:`LUMOS_SKIP_*`**
  - 一般無害指令 41 條都不誤問,包含 `grep LUMOS_SKIP_`、commit 訊息裡提到 `--no-verify`、heredoc 內文提到、`LUMOS_SKIP_X=1 pytest`。
- **事件入口**
  - `decide` 對 `None`、`[]`、`{}`、`tool_input` 為 `None`、`command` 為數字或空字串、`cwd` 為數字都放行,不丟例外。

**效能**:長度上限 20000 之下,最壞是未閉合的 `$(` 重複約 9990 次,耗時 3.06 秒;`$((` 重複 6600 次耗時 1.96 秒;反引號重複 19900 次耗時 0.89 秒(原因是 `_replace_cmdsubs` 對每個沒配對的 `$(` 都掃到結尾)。其餘輸入(巢狀已閉合的 `$(`、引號、heredoc、分號、export 等)都在 0.1 秒以內。註冊的逾時是 5 秒,逾時失敗也是放行,所以只是延遲,不算 finding;要處理的話,在 `$(` 沒配對時一次判斷就不要再重掃。

**三問的回答**
- 原問題的修復效果:路徑 A(引號、註解、heredoc、`export`、`--config-env`、`&` 背景 `cd`、`GIT_DIR` 行內)的案例,修前漏或誤、修後正確,上面列了逐條輸入與兩版結果。
- 修補處相鄰路徑是否仍成立:多數成立。回歸只有 finding 2 的私用區字元、finding 3 的 `$'a\'b'` 加續行、finding 4 的 `set-url --add/--delete`、finding 9 的 `git init`、`git clone` 值旗標與 `$'n'`。
- 同一案例修前修後:每條 finding 都標了兩版結果。

**未驗範圍**:merge-claude-settings.py 的註冊、`_hookevent.guard` 的存活事件寫入、test_lumos.py 各測試案例是否真能翻紅,我都沒讀。固定席節點的判斷如下。
- `Issues/code-loop守衛main-direct盲區`:只牽連 `scripts/test_lumos.py`,我沒有改測試相關行為的輸入,不影響。
- `lumos-cli-read` 的 search 排除 superseded INVARIANT、`lumos-cli-lifecycle` 的 re-inject 保留 sentinel 之外內容、`design-loop` 的處置閘第五步、`guard-kill` 的 rc 優先序與 json 純度:這些路徑都跟 Bash 掛鉤的指令分類無關,不影響。
- `測試假綠形態`的「還原翻紅釘需前置斷言」:我沒審這輪新增的測試。但這輪測試缺重導、`-m '>'`、`set-url --add` 這幾條,所以那幾種修補還原後測試不會翻紅。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★):只牽連 `scripts/lumos`,我沒審。

最嚴重等級 major,blocking 共 1 條(finding 1)。

涉及的檔案:`/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass/scripts/hooks/claude/bypass-ask-hook.py`。

來源:r2-通才-sonnet.md


審的是程式組全份加掛鉤全文(載入 `bypass-ask-hook.py` 實測,修前版本用 b5be3aad 存到臨時目錄對照)。沒找到 blocker 或 major。主要的繞過路徑(`--no-verify` 與縮寫、`-n` 短旗標組、`-c`/`--config-env`/`GIT_CONFIG_*`、`git config` 寫入與拆除、`LUMOS_SKIP_*` 的各種前綴)正常寫法都會問。四個新加規則各有一條縫,另有一條新增的誤問。

## Findings

1. 新規則「lumos 在段裡任何位置都認」造成誤問(修補引入的回歸)
ID: t1
severity: minor
   blocking: 否
   - 引句:「lk = next((k for k in range(i, len(seg)) if _lumos_at(seg, k)), None)」
   - `_skip_before` 用 `_SKIP_ASSIGN.match(w) for w in seg[:end]` 掃 lumos 詞之前的每個詞,不限賦值位置。所以 `grep -n "LUMOS_SKIP_NOTE_SHAPE=1" scripts/lumos` 或 `rg "LUMOS_SKIP_X=1" scripts/lumos` 會被判成設了跳過。這個 repo 常用這類 grep 查跳過旗標。
   - 預期放行,實際回 `['lumos-skip']`。
   - 歸因:有證據的修復回歸。
     - 修前版本同一條指令回 `[]`。
     - 修後版本回 `['lumos-skip']`。
     - `grep -rn LUMOS_SKIP_X=1 docs scripts/lumos`、`grep -c "LUMOS_SKIP_X=" scripts/lumos` 同樣如此。
     - `cat scripts/lumos | grep LUMOS_SKIP_X=1` 兩版都放行(lumos 在另一段)。
   - 應該只認「賦值出現在命令前綴」的詞,或把 lumos 詞限定為被執行的那個詞(直譯器之後的第一個非旗標參數)。

2. 「推送看推送位址」:省略使用者名的 scp 式位址在暫存目錄會被當成本機路徑
ID: t2
severity: minor
   blocking: 否
   - 引句:「if "://" in url or re.match(r"^[^/]+@[^/]+:", url):」
   - 只有 `user@host:path` 被排除。`aliashost:Org/Repo.git` 或 `github.com:Org/Repo.git` 這種靠 ssh config 補使用者的寫法,會被 `os.path.join(eff, url)` 接在暫存目錄後面,判成暫存根底下。
   - 重現:`git -C r1 remote add aliasr aliashost:EnzoHsieh-Android/Lumos.git`,`r1` 在 `/tmp/lumos-seat-work/...`。
     - `bypass_reasons("git push --no-verify aliasr main", r1)` 回 `[]`,等於放行。
     - 同樣的位址換成 `user@example.com:a/b.git` 回 `['no-verify']`。
   - 這正是計劃〈量測〉裡說暫存目錄有真工作副本對真遠端推送的情形。
   - 歸因:有證據的原有漏查。修前版本同輸入也回 `[]`,不是這輪造成的。
   - 另一個窄縫:`git remote set-url --add origin /tmp/x` 只加一個位址,推送仍會送到原本的真位址,但掛鉤用 `added[origin]=/tmp/x` 豁免。
   - 同理 `git remote add origin /tmp/b; git push ...`:`origin` 已存在時 add 會失敗,掛鉤仍當 origin 是暫存。

3. 「同指令建過」與「`$(mktemp -d)` 直接當目標」各有縫:都放行,真實目錄上的提交會漏問
ID: t3
severity: minor
   blocking: 否
   - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
   - 3a. 只看指令替換內文的第一個詞:
     - `cd $(mktemp -d && echo <真repo>) && git commit -n` 回 `[]`。
     - `cd $(mktemp -d; cd <真repo>; pwd) && git commit -n` 回 `[]`。
     - 這兩條寫法不自然。
   - 3b. `mktemp -d -p <真repo>`、`mktemp -d ./scratch.XXXX`、`mktemp -d --tmpdir=<真repo>` 建在 repo 工作樹裡的新目錄,仍被當暫存而豁免。`D=$(mktemp -d ./scratch.XXXX) && cd $D && git commit -n` 回 `[]`,但 `$D` 其實在真工作樹裡。
   - 3c. `mkdir /tmp/a && ln -s <真repo> /tmp/a/x && cd /tmp/a/x && git commit -n` 回 `[]`:「同指令建過」的目錄底下被放了符號連結。
   - 歸因:有證據的原有漏查。3a、3b 修前同輸入結果一樣。

4. 匯出的 `GIT_DIR`、`GIT_WORK_TREE` 不被追蹤
ID: t4
severity: minor
   blocking: 否
   - 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
   - 只認同段內聯的賦值。
   - `export GIT_DIR=<真repo>/.git; cd /tmp; git commit -n` 回 `[]`。`GIT_WORK_TREE` 同樣。
   - 先 `cd` 到 mktemp 目錄再 `export GIT_DIR=...` 也回 `[]`。
   - 歸因:有證據的原有漏查。修前版本結果相同。
   - 計劃〈做法〉只寫了同段賦值,所以這是文件與實作一致但有縫,不是不一致。

5. 未閉合 `$(` 的效能退步,〈做法〉宣稱的「2 萬字最壞 0.11 秒」不成立
ID: t5
severity: minor
   blocking: 否
   - 引句:「def _match_paren(text: str, i: int) -> int:」
   - `_replace_cmdsubs` 對每個沒配對的 `$(` 呼叫 `_match_paren`,每次掃到尾,所以是平方時間。
   - 重現:`"$("*9000 + " git commit -n"`(約 18000 字)耗時約 2.5 秒。2 萬字上限內純 `"$("*9990` 約 3.1 秒。
   - 修前版本同輸入約 0.01 秒。
   - 結果仍正確(`commit-n`)。掛鉤預算是 5 秒,慢機或有負載時可能超時,超時就放行。
   - 歸因:有證據的修復回歸(兩版耗時如上)。
   - 修法:`_replace_cmdsubs` 一次預算配對表,或第一次找不到配對就停止再找。

## 已驗的正向主張

以下都在修後版本實測,輸入與預期都符合:

- 縮寫:`--no-verif` 與 `--no-verify` 命中。`--no-ver`、`--no-ve`、`--no-v` 在 git 2.39 都不被接受(實測印出用法說明),所以預篩從 `--no-veri` 起算沒有漏。
- `-n` 判斷:
  - `-qn`、`-anm`、`-m x -S -n`、`-F msg -n`、`--amend -C HEAD -n`、`-C . commit -n` 命中。
  - `-m "x" -- -n`、訊息裡的 `-n`、`git log -n 5 && git commit -m x` 不誤問。
- 設定與環境變數:
  - `-c core.hooksPath=` 的大小寫、引號、空值、`--config-env=` 命中。
  - `GIT_CONFIG_KEY_0=core.hooksPath` 與 `GIT_CONFIG_PARAMETERS` 命中。
  - `git config` 的 `--get`、只給鍵、`-l`、`grep` 不誤問。
  - `--unset`、`--unset-all`、`--add`、`--replace-all`、`--worktree`、`--global` 寫入命中。
- 包裝與前綴:`env`、`sudo`、`timeout`、`command`、`\git`、`/usr/bin/git`、子殼層、`&&`、管線、續行都能找到 git。
- `LUMOS_SKIP_*`:前綴、`export`(含分行)、`env -i` 命中;`bash -c`、`lumos-foo`、`lumos.sh` 不誤問。
- 暫存放行:
  - `/tmp` 實驗 repo 裡的 `git commit -n`、`git config core.hooksPath`、`git -C <暫存repo> commit -n`、`mktemp -d && git init && commit -n` 都放行。
  - 這個 repo 的審查席暫存目錄也放行。
  - `cd` 回真 repo、`cd ..`、`cd -`、`pushd`、`$OLDPWD`、不存在的目錄、`--git-dir`、`--work-tree`、`-C <真repo>`(含 `~`、`$HOME`)都仍問。
- 暫存目錄裡的 clone:
  - 對真遠端 `git push --no-verify` 仍問。
  - 只在 clone 內提交放行。
- 一般的 `git push origin HEAD`、`git commit -m` 在預篩就停,不誤問。
- heredoc 內文與引號內的字樣不誤問;`echo git push --no-verify` 會問,屬計劃明載的刻意誤問。

## 配對案例(修前、修後)

| 案例 | 修前 | 修後 |
|---|---|---|
| `grep -n "LUMOS_SKIP_X=1" scripts/lumos` | `[]` | `['lumos-skip']`(finding 1,新增誤問) |
| 未閉合 `$(` 約 18000 字 | 約 0.01 秒 | 約 2.5 秒(finding 5) |
| `aliasr` 推送到 scp 式遠端 | `[]` | `[]`(finding 2,未變) |
| `export GIT_DIR=...; cd /tmp; git commit -n` | `[]` | `[]`(finding 4,未變) |
| `LUMOS_SKIP_X=1 timeout 5 lumos doctor`、`... sudo lumos doctor` | `[]` | `['lumos-skip']`(正向改善,屬 lumos 任何位置都認的預期效果) |

## 對三問的回答

1. 原問題的修復效果:
   - 「lumos 任何位置都認」修了 `timeout`、`sudo` 前綴漏問,見上表第 5 列。
   - 「推送看推送位址」,pushurl 與 fetch 位址不同的情形我沒有另建案例驗,未判定。
2. 修補處的相鄰呼叫路徑:正常、錯誤與相鄰路徑仍成立,例外是上面 finding 1 與 5。
3. 新發現的同一案例修前修後的結果:見上表。

## 固定席節點

- `lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill` 的 ★INVARIANT★:判不影響。這些 INVARIANT 都是關於 `scripts/lumos` 的 search、re-inject、處置閘、測試假綠與 guard kill,本輪程式組只新增獨立掛鉤與 `_hookevent.py` 的修剪暫存檔改為獨立名字(`tempfile.mkstemp`),沒碰這些行為。我沒有逐條驗證 INVARIANT 的綁定測試。
- `Issues/code-loop守衛main-direct盲區`:這輪改動沒有碰 main 直推守衛,判不影響。
- `pitfalls-code-loop`、`reversibility-governance-ledger`(★RISK★,牽連 `scripts/lumos`):程式組沒改 `scripts/lumos`,判不影響。
- 其餘「超出上限只列名」的節點:我沒有逐篇讀。

## 未驗範圍

- `test_lumos.py` 新增的測試沒有逐條跑,也沒有確認它們是否涵蓋 finding 1 與 5。
- 文件註冊組沒讀。
- Windows 路徑、`safe.directory` 造成 rev-parse 失敗被誤當「不在 repo」的情形沒測。

最嚴重等級 minor,blocking 共 0 條(5 條 finding 都是 blocking:否)。

來源:r2-架構對齊-sonnet.md


**0. 範圍說明**
- 已讀:新掛鉤 `bypass-ask-hook.py` 全檔結構、`_hookevent.py` 修剪段、鄰居 `impact-hook.py`、`dispatch-lens-hook.py`、`ci-status-hook.py`、`memory-sweep.py`、`check-graph-sync.py`,以及 `scripts/lumos` 的暫存寫入函式。
- 沒有逐 hunk 讀 `/tmp/code-代理繞閘字樣問人-r2-code.patch` 全文,也沒有載入掛鉤跑任何指令,所以沒有行為重現。
- 以下行號都是 4e87b682 這版。
- 已知偏離(d1:分類邏輯放在掛鉤內;進入點預篩在 guard 之外)沒有重報。我只確認 `entry()` 的註解(約第 906 行)有交代理由,是真的。

**問 1:分層與依賴方向**
- 依賴方向跟鄰居一致:掛鉤只往下依賴共用的 `_hookevent`,沒有反向依賴,也沒有呼叫 `scripts/lumos`。
  - 對照:`scripts/hooks/claude/impact-hook.py:924-928`、`scripts/hooks/claude/dispatch-lens-hook.py:551-555`。
- 兩處接法跟鄰居不同,結構對、寫法不同,對應下面 1 與 2 兩條。

**問 2:命名與錯誤處理**
- `_GIT_STATE = {"calls": 0, "cache": {}}`(`bypass-ask-hook.py:467`)是模組層可變狀態,在 `bypass_reasons` 開頭(約第 845 行)重置。
  - 鄰居有同形寫法:`memory-sweep.py:202-203` 的 `_PUSH_CACHE = {}`、`_FETCHED = {}`,`_hookevent.py:119` 的 `_MARKED = {...}`。判一致。
- `_Normalizer`(第 258 行)、`_Walker`(第 700 行)是私有類別,命名一致。
  - 鄰居的類別是 `memory-sweep.py:536` 的 `_Clock` 和 `:595` 的 `Tally`。判一致。
- `_Sep(str)`(第 418 行)是 `str` 子類別,拿來標記切詞時就認定的分隔符。
  - 範圍:我只 grep 了 `scripts/lumos`、`scripts/hooks/*/*.py`、`scripts/*.py`,repo 內沒有先例,是新引入的寫法。但它只在這個檔案裡用,不外露,不影響結構,判 minor。
- 暫存寫入(`_hookevent.py:87-98`)共有三種做法,對照如下:
  - `scripts/lumos:20604` 的 `_write_lf`:自己用 `os.open(O_EXCL, 0o666)` 建檔、原檔在就 `copymode`。docstring 明寫「不用 mkstemp 再改權限」。
  - `scripts/lumos:50542` 的 `_codeloop_write_dispositions`:裸 `tempfile.mkstemp(dir=…)` 加 `os.replace`,沒有 `copymode`。
  - `scripts/lumos:47710` 的 `_home_cache_write`:函式內 `import tempfile as _tf`,`mkstemp` 加 `chmod 0600`。
  - `_hookevent.py` 用的是第二種(裸 `mkstemp`,函式內 `import tempfile`)。
  - 差異:`hook-events.jsonl` 原本由 `open(f, "a")` 建成一般權限(通常 0644),修剪後被 `mkstemp` 換成 0600,沒做 `copymode`。`_write_lf` 的 docstring 正是針對這個權限漂移而選了另一條路。

**問 3:第二種做法**
- 專案原本沒有「真的 shell 詞法分析器」。既有的是:
  - `check-graph-sync.py:439-445` 的 `_segment_command`:用 `re.split` 切 `&&`、`||`、`;`、`|`,自述「Quote-aware 不嚴格」。
  - 同檔的 `_tokens_of`:`shlex.split`。
  - `scripts/lumos:27048` 的 `shlex.split`。
- 新掛鉤自寫了一整套:`_Normalizer` 做引號遮罩和 heredoc 內文剝除,`shlex.shlex(punctuation_chars=…)` 做切詞,`_Walker` 追蹤 `cd`、`export`、變數、`mktemp` 目錄。這是第二套指令切段做法,而且規模大一個量級。
- 計劃 PRIOR-ART(第 35 行)為 d1「厚掛鉤」和「逐段解析、寧可漏問」(對照審查席粗擋 d3/d4)做了交代,但**沒有交代為何不沿用 `_segment_command` 加 `shlex.split`**。
- 這套切段只在這支掛鉤內部使用,沒有跨層直呼,所以不是 major。判成「引入第二種做法」是否該升 major,標 ⚠ 交編排者裁。

**不對齊清單**

1. 
   - 引句:「sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))」
   - 事項:共用模組的載入位置不同。鄰居的 `sys.path.insert` 和 `from _hookevent import guard` 放在 `if __name__ == "__main__":` 區塊內(`impact-hook.py:922-928`),新掛鉤放在模組頂層。
   - 差別:頂層寫法用 `try/except` 加自訂 `mark` 空殼,多了一種備援形狀。
   - 這一條跟已知偏離(預篩在 guard 之外)有重疊,但「載入位置」本身沒被那段註解涵蓋。
   - 歸因:未判定。

ID: a1
severity: minor
blocking: 否

2. 
   - 引句:「fd, tmp = tempfile.mkstemp(dir=str(d), prefix="hook-events.", suffix=".trim")」
   - 事項:裸 `mkstemp` 加 `replace`,修剪後 `hook-events.jsonl` 權限從建檔預設變成 0600。`scripts/lumos:20604` 的 `_write_lf` 為此特別用 `copymode`,同檔的 `_codeloop_write_dispositions`(`scripts/lumos:50542`)則跟新寫法一樣沒做。
   - 差別:repo 內有兩種慣例,新碼選了較弱的那種。
   - 這個權限變化只影響同機其他使用者能不能讀事件檔,單人情境下是否有害我判不準,標 ⚠。

ID: a2
severity: minor
blocking: 否

3. 
   - 引句:「class _Sep(str):」
   - 事項:新增 `str` 子類別當分隔符標記,repo 內沒有同形先例。結構上只在本檔使用。

ID: a3
severity: minor
blocking: 否

4. 
   - 引句:「lex = shlex.shlex(text, posix=True, punctuation_chars="();<>|&\n")」
   - 事項:見問 3,自寫完整指令切段器,與 `_segment_command` 加 `shlex.split` 並存。
   - 計劃有 d1 解釋「厚掛鉤」,但沒解釋不沿用既有切段器。
   - ⚠ 判不準:若認定這是「第二種做法」就該升 major,若認定這是規模自然成長就維持 minor。我暫標 minor,交編排者裁。

ID: a4
severity: minor
blocking: 否

**固定席節點判讀**
- `Issues/code-loop守衛main-direct盲區`、`lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger`,以及其餘只列名的節點,都不影響架構一致性判斷。
  - 理由:這份改動只加掛鉤、改 `_hookevent.py` 的修剪寫法、註冊進 `scripts/merge-claude-settings.py`。
  - 沒碰 search 排除邏輯、re-inject sentinel、設計審處置閘、guard kill 的 rc 優先序。

不對齊共 4 條,其中 major 0 條(第 4 條判不準,已標 ⚠ 交編排者裁)。

來源:r2-資安-sonnet.md


審查結果(資安席,第 2 輪):找到 5 條可被利用的洞,其中 4 條是 major,1 條 minor。第 4 條是這輪修補自己引入的回歸。第 1、3 條跟修前行為相同,是原有漏查,但都不在〈範圍〉的「攔不到」清單裡。

**重現方式**:`SourceFileLoader` 載入修後 `4e87b682` 與修前 `b5be3aad` 的 `bypass-ask-hook.py`(臨時目錄 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/資安-sonnet/`,腳本 `p.py`,新舊版分別在 `n/`、`o/`),對同一批輸入呼叫 `bypass_reasons(指令, repo根)`。回傳 `[]` 代表放行。下面的 `R` 是真 repo 路徑 `/Users/enzo/orca/workspaces/lumos-toolchain/Word-wild-search-bypass`。

1. `mktemp` 只看詞首,後面接什麼參數、跟什麼指令都當成新暫存目錄
   - 引句:「subs[key] = _unmask(body).strip().split(" ")[0] == "mktemp"」
   - 位置:`_replace_cmdsubs`,`_expand` 對 `subs[word]` 回 `_MKTEMP`,`_not_real_repo(_MKTEMP)` 直接回 True。
   - 攻擊路徑:
     - 誰:被提示注入、想順手繞閘的代理。
     - 從哪:一條普通 Bash 指令。
     - 送什麼:`cd $(mktemp -d -p R); git commit --no-verify -m x`,或 `d=$(mktemp -d -p R); cd $d; git commit -n -m x`,或 `cd $(mktemp -d >/dev/null; echo R); git commit --no-verify -m x`。
     - 拿到什麼:`mktemp -p` 把目錄建在真 repo 底下,後面的提交跑在真 repo,掛鉤卻放行不問。第三種用 `echo` 直接換掉 `cd` 的目標,同樣放行。
   - 重現:三條都回 `[]`。對照組:`git commit --no-verify -m x` 回 `['no-verify']`。
   - 歸因:有證據的原有漏查。修前版本同樣回 `[]`,不是修補造成。
   - 應該是:只在 mktemp 後面沒有 `-p`、`--tmpdir=`,也沒有其他指令,而且參數都是已知安全旗標時才算新暫存目錄。其他一律判不出,照問。

ID: s1
severity: major

blocking: 是

2. `export GIT_DIR` / `GIT_WORK_TREE` 沒被追蹤
   - 引句:「if moved or any(_GITDIR_ASSIGN.match(w) for w in seg[:gi]):」
   - 位置:`_GITDIR_ASSIGN` 只檢查同一段 `git` 詞之前的賦值,`_mark_exported` 完全不認這三個名字。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`export GIT_DIR=R/.git GIT_WORK_TREE=R; cd $(mktemp -d); git commit --no-verify -m x`。
     - 拿到什麼:生效目錄被判成暫存目錄,實際上 git 動的是真 repo,掛鉤放行。
   - 重現:回 `[]`。內嵌寫法 `GIT_DIR=… git commit --no-verify` 已被 r1 修補擋住,所以只有 export 這條路漏。
   - 歸因:有證據的原有漏查(修前同樣回 `[]`)。
   - 應該是:`export`、`declare -x`,或先賦值再 `export` 這三個名字後,生效目錄一律判不出。

ID: s2
severity: major

blocking: 是

3. 「同指令建過的目錄」的豁免,擋不住 `ln -s` 指回真 repo
   - 引句:「return _within(eff, created)     # 不存在又不是這條指令建的:cd 會失敗,git 跑在原目錄」
   - 位置:`_not_real_repo`,目錄在掛鉤判斷時還不存在,`created` 靠字串前綴比對,不管路徑之後被什麼換掉。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`mkdir /tmp/zz9 && ln -s R /tmp/zz9/r && cd /tmp/zz9/r && git commit --no-verify -m x`。
     - 拿到什麼:`/tmp/zz9/r` 落在 `created` 底下,被當成拋棄式。實際上它是指回真 repo 的符號連結,掛鉤放行。換成 `rm -rf` 後再建連結、或 `git init /tmp/x; rm -rf /tmp/x; ln -s …` 也一樣。
   - 重現:回 `[]`。
   - 歸因:有證據的原有漏查(修前同樣回 `[]`)。
   - 應該是:同一條指令裡出現 `ln`、`mv`、`rm`、`cp` 等會動到路徑的指令(其他指令的寫法也一併想過),就取消「同指令建過」的豁免。

ID: s3
severity: major

blocking: 是

4. 修補回歸:同指令的 `git remote set-url` 被當成「推送位址就是這個」
   - 引句:「added[pos[0]] = _join(eff, url) if isinstance(url, str) and _is_local_path(url) else None」
   - 位置:`_remote_set`(在 `_git` 裡呼叫),以及 `_push_target_temp` 的 `if added and remote in added:`。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:
       - `git remote set-url --add --push origin /tmp/zz && git push --no-verify origin`
       - `git remote set-url origin /tmp/zz && git push --no-verify origin`
     - 拿到什麼:
       - `--add --push` 是追加一個推送位址,原本的真遠端仍然在;推送會同時送到真遠端。
       - 沒帶 `--push` 的 `set-url` 只改抓取位址;若原本另有 `pushurl`,推送仍然去真遠端。
       - 掛鉤兩種都判成「推送到暫存目錄」而放行。
   - 重現:修後兩條都回 `[]`;修前同兩條都回 `['no-verify']`(照問)。
   - 歸因:有證據的修復回歸。「同指令 `set-url` 一律記下」是 r1 之後為了放寬誤問才加的。
   - 應該是:只有 `git remote add` 的位址才採信(新增的遠端不會有舊的真位址)。`set-url` 帶 `--add`、`--delete`、不帶 `--push`,或這個名稱已存在,就不採信。

ID: s4
severity: major

blocking: 是

5. 預篩被引號拆字繞過(實際進入點上的洞)
   - 引句:「return "git" in low and re.search(r"\bcommit\b", low) is not None and _PRE_SHORT_N.search(low) is not None」
   - 位置:`prefilter` 只做子字串比對,不解引號;`entry` 在 `_guard` 之外先呼叫它。
   - 攻擊路徑:
     - 誰:同第 1 條。
     - 送什麼:`git push --no-ver''ify origin`,或 `git commit -"n" -m x`。
     - 拿到什麼:`bypass_reasons` 對這兩條會回 `no-verify` / `commit-n`(實測),但實際從 stdin 走 `entry`,`prefilter` 回 `False`,整支掛鉤不會被叫到。
   - 重現:`prefilter(json)` 對 `--no-ver''ify` 回 `False`,修前修後都是。
   - 歸因:有證據的原有漏查。
   - 說明:計劃〈範圍〉只說「有心改寫攔不到」,沒明列引號拆字。我判這條屬於未明列。
   - 理由:這是單人、問人層的設計,且需要有心改寫,標 minor;但這輪新加的拋棄式規則都可以用正常寫法繞過(第 1 到 3 條),相比之下這條是原有的設計缺口。

ID: s5
severity: minor

blocking: 否

**逐類確認:**
- 類 1,不可信輸入流到危險操作:
  - 已看,無可利用的路徑。
  - `git -C <目錄> rev-parse --git-common-dir` 與 `remote get-url --push <名稱>` 不會觸發 `core.fsmonitor`(只有 `status` / `diff` 這類動到 index 的指令才會),也不會執行設定檔裡的程式。
  - 名稱以 `-` 開頭時,`_push_remote_arg` 把它當選項跳過;含換行時被 shlex 切開。
  - 副作用:目錄不是 repo,或 git 因 `safe.directory` 拒絕時回 rc 非 0,`_not_real_repo` 會判成「不在任何 repo 裡」而放行。這要求目錄先在暫存根下,屬「暫存目錄就當拋棄式」的設計取捨,不單獨報。
- 類 2,輸出:已看,無。理由只用固定代碼對應的文字;存活事件的 note 是 `type(e).__name__ + ":" + str(e)[:120]`,不含指令原文。
- 類 3,`_hookevent` 的 mkstemp 新增寫入面:已看,無新的利用。暫存檔隨機命名、在同一目錄、`os.replace` 原子換入。`hook-events.jsonl` 若是符號連結,`open(f, "a")` 會追加到連結目標,那是原有行為,不是 mkstemp 新增的。
- 類 4,繞過面:見第 1 到 3 條(新加的拋棄式規則)與第 4 條。
  - 另外 `git push` 的 `file:` 位址、`_remote_url_temp` 對沒有 `@` 的 `host:path` 位址(例如 `github.com:org/repo`)會被當成本機相對路徑。若生效目錄在暫存根下就判拋棄式。要求先在暫存目錄裡操作,我沒有寫出完整攻擊路徑,標推論 minor,不列為 finding。

**三問(用於核對 r1 修補):**
- ①原問題的修復效果:本席只驗證了第 4 條的反面。同指令 `remote set-url` 在修前是照問,修後變成放行,不是修好,是放寬。其他 r1 修補(內嵌 `GIT_DIR=`、`--git-dir`、`mktemp ..`)我沒有逐條重驗。
- ②修補處的相鄰路徑:第 1、2、3 條在修前修後都不成立(都放行),所以這幾條不是修補造成,但都落在拋棄式判定的相鄰路徑上。
- ③新發現的同一案例在修前修後:見上面各條的「歸因」。只有第 4 條是修補造成的回歸(修前 `['no-verify']`,修後 `[]`)。

**固定席節點:**
- `Issues/code-loop守衛main-direct盲區`、`lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`測試假綠形態`、`guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger` 等:不影響本席的資安判斷。它們的 INVARIANT 都是 search 排除、re-inject、處置閘、guard kill 等,與這支掛鉤的拋棄式判定無關;本席沒有從這幾篇找到可利用的點。
- `_hookevent.py` 屬 lumos-cli-read / lifecycle 的牽連檔;本席只檢查了 mkstemp 與 record 的寫入面,見類 3。

最嚴重等級 major,blocking 共 4 條(第 1、2、3、4 條),另 1 條 minor。

來源:r2-合約圖譜-sonnet-引句更正.md


我沒再跑任何工具,也沒清臨時目錄。我的實驗檔留在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/`,由你刪。

我沒跑 `test_lumos.py`,因為要求不改 repo,怕測試留下檔案。所以測試只靠讀碼核對,另用自寫腳本載入掛鉤實測行為。

## Findings

1. S4 條款文字比掛鉤的實際行為窄,也比〈做法〉窄,廣的那幾種字面判沒有測試
ID: g1
severity: minor
   blocking: 否
   引句:「當指令引號不成對或超過 2 萬字時,含 git、push 或 commit、`--no-veri` 三者 應 問人,其他 應 放行」
   - 〈做法〉的「字面判」寫的是:含 `git` 或 `lumos`,加上 `--no-veri`、`hookspath`、`lumos_skip_` 任一個,或 `commit` 加含 `n` 的短旗標。
   - 實測(`bypass_reasons`):
     - `git config core.hooksPath x "unclosed` 回 `['literal']`。
     - `lumos x LUMOS_SKIP_A=1 "unclosed` 回 `['literal']`。
     - `git commit -m "unclosed -n` 回 `['literal']`。
   - 這三種都不符合 S4 的「三者」,條款漏寫。
   - `t_bypass_ask_fallbacks_and_budget` 只測了 `git push --no-verify "未閉合` 這一種,另外三種(hookspath、LUMOS_SKIP、commit -n)沒被綁到。
   - 應該是:條款改成〈做法〉的寫法,測試補這三例。
   - 歸因:未判定。修前版本我沒載入,只見修後的條款與測試落差。

2. 〈範圍〉說 `merge --no-verify` 不影響 Lumos 的閘,但命中規則仍把 merge 列入
ID: g2
severity: minor
   blocking: 否
   引句:「`rebase`、`am`、`cherry-pick`、`pull` 帶 `--no-verify` 只跳過 pre-merge-commit、commit-msg 這類本 repo 沒裝的掛鉤,不影響 Lumos 的提交前閘與推送前閘」
   - `ls scripts/hooks` 只有 `pre-commit`、`pre-push`、`post-commit`,沒有 `pre-merge-commit`,也沒有 `commit-msg`。
   - `git merge --no-verify` 跳過的正是這兩種,同一個理由卻被列進命中:`bypass_reasons("git merge --no-verify main")` 回 `['no-verify']`。
   - 這是誤問方向,符合 d2 的取捨,但〈做法〉與〈範圍〉對 merge 的處理互相矛盾,三個月後的接手人會不知道依哪邊。
   - 應該是:在〈範圍〉明寫 merge 是刻意多問,或把 merge 從 `--no-verify` 命中拿掉。
   - 歸因:未判定。

3. 計劃沒把 `_hookevent.py` 的修剪暫存檔改動列進落點與〈做法〉
ID: g3
severity: minor
   blocking: 否
   引句:「新 Systems 節點 `Systems/代理繞閘問人` 管這支掛鉤檔(每支檔有家,與 `Systems/改檔前推播`、`Systems/記憶過期清掃` 一支掛鉤一篇的慣例同);`scripts/lumos` 與 `merge-claude-settings.py` 的改動寫進 [[Systems/lumos-cli-lifecycle]]。」
   - 這句是計劃〈做法〉談 Systems 節點寫進哪裡的地方,只列了 `Systems/代理繞閘問人` 與 `Systems/lumos-cli-lifecycle`。
   - `lumos impact --file scripts/hooks/claude/_hookevent.py` 顯示 `_hookevent.py` 的家是新開的 `Systems/掛鉤存活事件`。
   - 計劃 frontmatter 的 `lands_in` 同樣只列前兩篇,沒有 `Systems/掛鉤存活事件`。專案規則是 `lands_in` 要列出現況落在哪幾篇,新開的這篇卻沒列。
   - 〈做法〉也沒提 mkstemp 修剪,只在〈審計修正紀錄〉裡一句帶過。
   - 應該是:`lands_in` 與這句都加上 `Systems/掛鉤存活事件`。
   - 歸因:未判定。

4. 〈回退〉三步驟能讓掛鉤停止問人,但沒說明中間狀態,也沒列要連帶改的名單
ID: g4
severity: minor
   blocking: 否
   引句:「把檔名從 `scripts/lumos` 的 `_GLOBAL_CLAUDE_HOOKS` 移到 `_RETIRED_STUB_CLAUDE_HOOKS`(相容期換成空殼,下一版再移到 `_RETIRED_CLAUDE_HOOKS` 真刪)」
   - 我在 `4e87b682` 的臨時副本裡,用隔離的 HOME 依序模擬,結果如下:

   | 步驟 | settings.json 的 Bash 註冊 | 掛鉤檔 |
   |---|---|---|
   | 初次安裝 | 有 | 真檔 |
   | A 只拿掉 matcher | 仍在 | 仍是真檔,仍會問 |
   | B 搬到空殼名單 | 仍在 | 換成 exit 0 空殼,不再問 |
   | C 下一版移到真刪名單 | 被 `_prune_dangling` 剪掉 | 刪除 |

   - 計劃對 A 的說明正確,B 也退得掉。
   - 不足有兩點:
     - 計劃沒說 B 之後註冊還留在 settings.json,要到 C 才清掉。
     - 計劃沒提 `t_bypass_ask_*` 測試,以及 `_VENDORED_TREE_FILES` 與 `ANCHOR_FILES` 該怎麼處理。
   - 歸因:未判定。

5. `git config unset core.hooksPath` 在計劃裡說同樣命中,但沒有測試
ID: g5
severity: minor
   blocking: 否
   引句:「新語法 `git config set core.hooksPath …`、`git config unset core.hooksPath` 同樣命中」
   - 實測 `git config unset core.hooksPath` 回 `['config-hookspath']`,行為與文字相符。
   - S1 測試只有 `set` 一例。
   - 另外 `-c core.hooksPath=` 接 `am`、`revert`、`merge` 在條款裡列了,測試只有 commit、push、rebase、cherry-pick。
   - 歸因:未判定。

## 固定席節點逐條判

- `Issues/code-loop守衛main-direct盲區`:不影響。牽連只在 `test_lumos.py`,這批新增的測試沒碰 code-loop 守衛。
- `Systems/lumos-cli-read`(家,★INVARIANT★ search 排除 superseded):不影響。改動沒碰 `search`。
- `Systems/lumos-cli-lifecycle`(家,★INVARIANT★ re-inject 保留 sentinel 外內容):不影響該合約。
  - 新句是 WHY 一行,`lumos lint` 回 0 問題,格式有出處、因、不選、test。
  - 內容與程式相符:Codex 轉換跳過 Bash matcher、安裝名單、防護列、vendored 與 anchor 名單都有加。
  - `[test:t_bypass_ask_registered]` 只驗註冊、Codex 跳過、安裝名單與防護列。vendored 與 anchor 名單靠既有的全表比對測試,我沒獨立驗過。
- `Systems/design-loop`(家,處置閘):不影響。
- `Systems/測試假綠形態`(★INVARIANT★ 還原翻紅釘要配前置斷言):不影響合約本身。
  - `t_bypass_ask_throwaway_targets` 有現場成立的前置(`allow` 與 `ask` 兩組對照)。
  - 幾百段的 git 上限測試只靠「照問」間接證明上限,沒量到逾時。上限被拿掉時 `asked` 會變 False,測試仍會紅,所以不構成假綠。
- `Systems/guard-kill`、`pitfalls-code-loop`、`reversibility-governance-ledger`:不影響。
- 其餘「超出上限、只列名」的節點:我未逐篇判。

## 另外核對的項目

- `Systems/代理繞閘問人`:`lumos lint` 0 問題。
  - responsibility 與 `about_code` 對得上,家是 `bypass-ask-hook.py`。
  - 5 條 PITFALL 都有 `[出處:]`、`[根因:]` 和 `[test:]`,測試名都存在。
- `Systems/掛鉤存活事件`:`lumos lint` 0 問題。
  - `about_code` 為 `_hookevent.py`,`impact` 確認它是唯一的家。
  - responsibility 與程式相符:寫入器、修剪、不讀事件。
  - `t_hook_event_trim_tmp_unique` 存在,驗到「固定暫存檔名被佔住仍能修剪」與「沒有殘餘檔」。
- 計劃 `Projects/代理繞閘字樣問人_計劃`:`lumos lint` 0 問題。
  - 以下項目與程式相符:`MAX_GIT_CALLS = 4`、同查詢快取、預篩三字樣加短旗標、`entry` 先算預算、事件名等於列名、`_codex_entries` 跳過 Bash。
  - 防護列在 stale 或 unknown 時不進分母,我讀 `enforcement_status` 確認過。
  - 計劃寫「原為 24 列」,測試已改成 25 列。
- 量測數字(371、375、387 條,一週與近 30 天)我沒重算。事件帳會持續增長,數字無法逐字重現。〈實務隱患〉用 371,〈量測〉後面又寫 375 和 387,屬於不同時間點的量測,不算矛盾。

## 三問

1. 原問題的修復效果:
   - 續行加 `-n`、詞中 `#`、`$(cat <<'EOF'…)` 撇號、`--git-dir`、`config --global`、`GIT_CONFIG_*`、`--config-env` 這幾類,我用現行程式實測或讀測試案例,行為都符合文字。
   - 我沒載入修前版 `b5be3aad`,所以沒有「修前紅、修後綠」的同案例對照,這部分未判定。
2. 修補處的正常、錯誤與相鄰路徑:
   - 我實測了這些輸入,結果都符合計劃文字:
     - `commit --message -n` 與 `commit -m x -- -n` 放行。
     - `git commit -m x --no-verif` 命中。
     - `git commit --amend --no-edit -n` 命中。
     - `export LUMOS_SKIP_X=1 && lumos doctor` 命中。
     - `LUMOS_SKIP_X=1 git status && git commit -m y` 放行。
     - 引號不成對時三種字面判命中。
   - 未驗:修剪暫存檔的權限。`mkstemp` 會讓 `hook-events.jsonl` 的權限變 0600,沒有 `copymode`。依單人模型我判定無實害,沒列為 finding。
3. 新發現的修前與修後對照:五條都是文件與測試落差,修前版本我沒載入,全部歸因未判定。

最嚴重等級 minor,blocking 共 0 條。

來源:r2-資安-文件-sonnet.md


文件註冊組(計劃、三篇 Systems 節點、`scripts/lumos`、`merge-claude-settings.py`)的 456 行 patch 我逐 hunk 讀完,沒有可利用的洞。除下面第 1 類的路徑引號驗證外,以下都是對 patch 內文的推論,我沒另外跑重現。

**1. 執行邊界:已看,無。**
- **指令字串組法**:新的 `bypass-ask-hook.py` 註冊是用 `HOOK_ENTRIES` 裡既有的 `_hook_cmd("bypass-ask-hook.py")` 組出來。
  - 組法沒有改動。我讀了修後版的 `_hook_cmd`,POSIX 分支把 Python 路徑用 `shlex.quote` 包好,`${HOME}/.claude/hooks/<rel>` 放在雙引號裡,所以路徑含空白不會被 shell 切開。
  - `rel_path` 是寫死的常數,不來自外部輸入。
  - `--budget 5` 來自 `HOOK_BUDGET` 常數。
  - 這條註冊沒有引入新的注入面。
- **`_codex_entries` 的跳過判法**:判法是 `event == "PreToolUse" and e.get("matcher") == "Bash"`,比對的是程式內建的 `HOOK_ENTRIES` 字典,不是讀使用者設定檔。設定檔內容繞不過它。
  - 這個跳過只影響 Codex 的註冊表產出,不涉及授權。
- **安裝、拆除名單**:`_VENDORED_TREE_FILES`、`_GLOBAL_CLAUDE_HOOKS`、`ANCHOR_FILES`、`enforcement_status` 的新增項都是字面常數檔名,沒有路徑分隔符,也沒有變數拼接。
  - 一個固定檔名被複製或刪除,無法指向別的位置。
  - 我沒有把這些名單背後的複製與刪除函式整支讀一遍,只確認新增項本身是安全的常數。
- **錨點**:`ANCHOR_FILES` 加一項,是把這支每條 Bash 都會跑的掛鉤納入完整性監控。這是收緊,不是放寬。

**2. 文件裡寫給人照抄的指令:已看,無。**
- 〈回退〉只講「拿掉 matcher、移到 `_RETIRED_STUB_CLAUDE_HOOKS`、拿掉 enforcement 列舉、重跑安裝」,沒有 `rm -rf`、`curl | sh`、`sudo`、`--force` 之類的危險指令。
- 計劃文件裡出現的 `F=--no-verify; git push $F` 等寫法,是〈範圍〉列的「攔不到寫法」範例,不是要人執行的步驟。
- 筆記裡的 `[test:…]` 只是引用測試名。

**3. 授權範圍有沒有被放寬:已看,無。**
- 新 matcher 為 `Bash`,每條 Bash 指令都會叫這支掛鉤。
- 掛鉤只會回 `ask`,也就是把原本不問的指令升級成要問人。patch 裡沒有任何路徑讓它回 `allow`,也沒有改寫 `permissionDecision` 為放行。
- 失敗時放行,等於維持沒有這支掛鉤時的原狀,不是新放寬。計劃明寫這是問人層、不是安全邊界,範圍外的繞法我不當 finding 重報。
- 逾時 5 秒。只有命中且落在暫存目錄時才會跑 git 子程序,這部分屬程式組,不在本組。

**固定席節點逐條判:**
- `Issues/code-loop守衛main-direct盲區`:不影響。本 patch 沒動 code-loop 守衛的判斷。
- `lumos-cli-read`、`lumos-cli-lifecycle` 的 ★INVARIANT★:不影響。
  - 這次對 `scripts/lumos` 的改動只有名單加一項,沒碰 search 濾網或 re-inject。
  - lifecycle 筆記只多一行 WHY,沒有動 re-inject 的 sentinel 行。
- `design-loop`、`測試假綠形態`、`guard-kill`:不影響。patch 沒有改這些合約管的邏輯。
- `pitfalls-code-loop`、`reversibility-governance-ledger` 的 ★RISK★:不影響。
  - `scripts/lumos` 的改動只是名單加字面常數檔名。
  - 這些筆記管的風險路徑沒有被碰到。
- 其餘「只列名」節點:本組 patch 內容與它們無關,不影響。

**修補鏡頭三問:**
- **原問題的修復效果**:本組只含文件和註冊,沒有行為性修復,未判定。行為修復在程式組。
- **修補處的正常、錯誤與相鄰路徑**:註冊路徑沿用既有 `_hook_cmd`,與同批其他 hook 同形,我判定仍成立。
- **新發現的修前、修後差異**:沒有新發現,不適用。

**未驗範圍:** 我沒載入 `bypass-ask-hook.py` 跑 `bypass_reasons`,因為那屬程式組。也沒實測 `merge-claude-settings.py` 在路徑含特殊字元時的實際輸出。

最嚴重等級 clean,blocking 共 0 條。

來源:r2-規格符合-sonnet.md


**總判**:〈做法〉每一點與 [S1]–[S6] 我逐條對過,沒有縮水,也沒有未實作。只有一條「規格內部不一致」的發現,下面第 1 條。

我用 4e87b682 的掛鉤檔載入 `bypass_reasons` 跑了約 55 條輸入,對照 spec 逐條判。實驗檔在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/規格符合-sonnet/`(`t.py`、`t2.py`)。注意不是每條都有跑過。

## 〈做法〉逐點裁定

| 項目 | 裁定 | 佐證 |
|---|---|---|
| 讀輸入與預篩(guard 外) | 已實作 | `entry`/`prefilter`:先解 JSON 取 `command`,`_PRE_WORDS` 三字樣加 `git`+`commit`+含 n 短旗標;預篩例外直接 return 0;`_guard(..., swallow=True)`;事件名 `pretooluse-bypass-ask-hook`;`decide` 內例外 `mark("error")` |
| 逾時預算 | 已實作 | `_outer_budget`、`_inner_budget` 逐字複本;`entry` 一進場就先叫一次 `_inner_budget()`;`MAX_GIT_CALLS=4`;`_GIT_STATE` 快取在 `bypass_reasons` 開頭重置 |
| 長度上限 | 已實作 | `len(command) > MAX_LEN` 走 `_literal`。實測 `git commit -m` 加 10 萬字單詞,耗時 0.001 秒,結果 `[]`(沒有三字樣,放行) |
| 一趟前處理 | 已實作 | `_Normalizer` 涵蓋:詞首 `#` 才算註解、`$(` 重開引號層、引號遮罩、ANSI 引號佔位、heredoc(`<<<` 與 `$((` 不算、多個 heredoc 依序配對、`<<-`、找不到結束字就停止剝) |
| 切詞與切段 | 已實作 | `_join_continuations`、`_replace_cmdsubs`、`_tokens`(shlex 加 `punctuation_chars`,換行當標點)、`_Sep` |
| 找 git 指令 | 已實作 | `_command` 取段裡第一個檔名是 `git` 的詞,`_parse_git` 跳全域選項;黏著的 `--git-dir=X` 不多吃;`--no-veri` 縮寫判法與 spec 一致 |
| 命中規則 | 已實作 | 實測:`--no-verif`、`-qn`、`-m x -n`、`--config-env`、`GIT_CONFIG_KEY_0=`、`config --unset`、`config set`、`export LUMOS_SKIP`、`env`/`timeout`/`sudo` 前綴下的 lumos,全部命中。`-mnote`、`-m -n`、`-F -n`、`--no-verified`、`--get`、只給鍵、`HUSKY=0`、`LUMOS_SKIP` 接 pytest、`lumos search LUMOS_SKIP_X=1` 全部放行 |
| 拋棄式判定 | 已實作 | 實測:`mktemp` 加 `$S/w` 放行;`mkdir`+`git init` 放行;`git -C /tmp` 放行;不存在的目錄、`--git-dir`、子殼層 `cd`、`&` 背景 `cd`、`pushd`、`cd /tmp/../Users`、`git -C ..` 全部照問;`remote add` 本機路徑放行,網址照問;`-c core.hooksPath` 接 rebase 照問;暫存目錄裡的 `LUMOS_SKIP` 接 lumos 照問;`_exempt` 分 sub 處理 |
| 字面判 | 已實作(見第 1 條) | 引號不成對時回 `["literal"]` |
| 命中輸出 | 已實作 | `_reason_text` 為三段式固定文字,不嵌入指令內容 |
| `decide`/`bypass_reasons`/`main` 分工 | 已實作 | 與 spec 一致 |
| `merge-claude-settings.py` | 已實作 | Bash matcher 加 `HOOK_BUDGET` 5,`_codex_entries` 對 `Bash` 的 PreToolUse 直接跳過 |
| `scripts/lumos` | 已實作 | `_GLOBAL_CLAUDE_HOOKS`、`enforcement_status` 一列、`_VENDORED_TREE_FILES`、`ANCHOR_FILES` 都加了。repo 的 `governance/anchor-baseline.json` 有簽(grep 命中 1 筆) |
| Systems 節點與 lifecycle 註記 | 已實作 | 在文件註冊組 patch 裡,我沒逐行核,只確認檔存在 |

## 條款 S1–S6

- **S1**:已實作。上表命中形狀都有實測。
- **S2**:已實作,只有一處需要說明。`git commit -m '--no-verify'`(引號裡的值剛好整串是 `--no-verify`)會命中。spec 對 `--no-verify` 沒有像 `-n` 那樣的吃值旗標排除,而且 shlex 切完詞後引號就不見了,所以符合 spec 字面。
- **S3**:已實作。放行與照問兩邊的形狀,抽測的都符合。
- **S4**:已實作,但字面判條件有內部不一致(第 1 條)。10 萬字單詞的耗時有量。其餘幾項我沒測:大量分段、大量未閉合 `<<EOF`、大量 `$(`、幾百段都要查 git、`--budget 5`。
- **S5**:已實作。patch 內容符合,但「列數 25」的測試與 `t_bypass_ask_registered` 不在 patch 裡,我沒驗。
- **S6**:屬人工條款,實作層無對應,不判。

## 發現

1. S4 的字面判條件與〈做法〉「字面判」不一致,實作照〈做法〉。
ID: p1
severity: minor
   blocking: 否
   引句:「當指令引號不成對或超過 2 萬字時,含 git、push 或 commit、`--no-veri` 三者 應問人,其他 應放行」
   - S4 要求同時有 git、push 或 commit、`--no-veri` 三者才問。
   - 〈做法〉寫的是「含 `git` 或 `lumos`,而且有 `--no-veri`、`hookspath`、`lumos_skip_` 任一個、或有 `commit` 加含 `n` 的短旗標」。實作 `_literal` 跟這句。
   - 實測:`git push --no-verify 'unclosed` 回 `['literal']`,兩種寫法都問。`git config core.hooksPath 'x` 這類寫法,只有〈做法〉會問。
   - 歸類:多做(相對 S4 字面),但有〈做法〉的 spec 對應,算 spec 內部矛盾。S4 應改成與〈做法〉同句。⚠ 請編排者裁定以哪句為準。

縮水+未實作共 0 條
