severity: major

我載入了修前(b5be3aad)和修後(4e87b682)兩版掛鉤,用 `bypass_reasons` 逐案對跑,實驗檔都在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/正確性-sonnet/`。下面的指令都是 `bypass_reasons(指令, cwd)`,輸出寫成 `(修前, 修後)`。除另外標明的 cwd,都用 `/Users/enzo/.../Word-wild-search-bypass`;凡涉及暫存根的案例,都把 `_temp_roots` 換成實驗用的假暫存根。

## Findings

**1. 續行合併的引號追蹤沒跟著重構,撇號會讓後面的 `\⏎` 不被合併,續行上的 `--no-verify` 漏問**

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

severity: minor
blocking: 否

引句:「close = text.find("`", i + 1)」

- 輸入 `echo \`; git push --no-verify; echo \``,裸的 `\`` 在 shell 裡是字面反引號。`_Normalizer` 保留 `\`` 原樣,`_cmdsub_span` 看到反引號就找下一個,把中間整段換成佔位詞。
- 結果 `(['no-verify'], [])`:修前問,修後漏。
- 實務上要有成對的跳脫反引號夾著指令才會發生,所以給 minor。
- 歸因:有證據的修復回歸(兩版逐案對照)。

**5. export 的 `GIT_DIR` 與 `GIT_WORK_TREE` 沒追蹤**

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
