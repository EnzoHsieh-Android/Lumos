severity: major

審查範圍:r2 新寫或改寫的內容,對照 prepush-collect 的 `scripts/hooks/pre-push`、`scripts/lumos`、`scripts/test_lumos.py`。
我在臨時目錄用真的 git 做了 `git push --dry-run` 最小實驗,實驗目錄已刪。

## 實驗結論

- dry-run 會照常呼叫 pre-push,掛鉤拿到的參數是遠端名與網址。推送行照 git 組出,新分支舊值全零,刪除、tag、多 ref 的推送行都正常傳進來。
- 遠端連不上(rc=128)、沒設追蹤分支、detached HEAD 又沒給參數,這三種都是 git 自己先 fatal,掛鉤根本沒被叫。計劃要的「回 2」可以實測成立。
- 兩種情形下掛鉤照樣被叫,但 stdin 是空的,沒有任何推送行:
  - 已是最新(Everything up-to-date)。
  - 非快轉被拒(rejected non-fast-forward):git 先把被拒的 ref 剔掉才叫掛鉤,最後 git 回 rc=1。
- 加 `--no-verify` 時掛鉤不被叫。
- `git rev-parse --git-path hooks/pre-push` 回的是相對於目前目錄的路徑。從子目錄跑會是 `../scripts/hooks/pre-push`,linked worktree 的 `--git-common-dir` 會指到主工作樹的 `.git`。掛鉤的 cwd 固定在 repo 根。
- 掛鉤收到的 `GIT_DIR` 只在 linked worktree 才有。

## Finding

severity: major
blocking: 是 — 計劃自己點名「收集寫錯讓某道擋下被吞掉、變成放行」是最大風險,而這裡有兩條路徑會把 rc1 吞掉,且沒有任何條款或測試涵蓋
引句:「掛鉤讀它,替每個 `reason_kind` 各記一筆」
問題:新模式下,掛鉤是否記下代碼審擋下,取決於解析 `LUMOS-BLOCKS:` 那一行。計劃沒寫「`code-loop check` 回 1,卻沒有這行、這行是空的、或 kind 查不到對照表」時怎麼辦。
另外「記下」只靠追加寫進 `$_PP_TMP/blocks`,「有沒有擋下」也只看那個檔有沒有行。
程式佐證:現行掛鉤擋不擋看 rc,見 `scripts/hooks/pre-push:466`(`cl_rc -eq 1`)。
具體失敗情境:
- 輸入:`code-loop check --keep-going` 回 rc=1,但輸出沒有 `LUMOS-BLOCKS:`(例如 stdout 與 stderr 合併後被截斷,或 kind 是對照表沒有的新值)。結果:記下 0 筆,判斷點看到空檔,往下跑全套,最後 `exit 0` 放行。
- 輸入:`$TMPDIR` 在掛鉤中途寫滿,`printf >>` 失敗。結果:同樣 0 筆,放行。
- 這與計劃「觀測失效不得改變擋下」的原則相反。
- 建議:rc==1 時至少強制記一筆(未知原因也記),並用不依賴檔案的純量旗標(`_PP_BLOCKED=1`)判擋不擋。
- 另加條款:rc1 配壞掉或缺漏的 `LUMOS-BLOCKS`,仍要回 1。

severity: major
blocking: 是 — S11 裡「多個遠端判不出主線」的情境,實作者不猜就建不出來,也沒有可驗的判準
引句:「沒有追蹤時,只有一個遠端就用它,多個遠端時用主線所在的那個(主線候選與 `push-range` 共用同一份);都判不了,回 2 並請人帶參數」
問題:
- 實驗證實,沒有上游時 `git push --dry-run origin`(帶遠端、不帶 refspec)仍然 fatal「no upstream branch」。所以 lumos 必須自己補 refspec,例如 `HEAD:refs/heads/<分支>`,計劃完全沒寫。
- 「用主線所在的那個遠端」做不到。程式佐證:`_push_mainlines(repo_root, remote, pushed_ref)` 在 `scripts/lumos:47247` 附近,它要先給定遠端,才回候選主線 sha;它不能從多個遠端裡挑一個。
- fork 加 upstream 這種兩個遠端都有 main 的常見情形,也沒說算判得出還是判不出。
- 沒有任何遠端時的行為沒寫。
- 還有兩個實作者必須自己決定的地方:
  - `lumos push-preview [git push 的參數…]` 要把任意 git 旗標透傳,和 argparse、lumos 慣用的 `--repo` 衝突(git push 也有 `--repo`)。
  - 使用者自己帶 `--no-verify` 時,掛鉤不被叫、git 回 0、沒有結果檔,應落在 rc 2。
具體失敗情境:兩個遠端 origin 與 upstream 都有 main,沒設追蹤,也沒給參數。實作 A 回 2,實作 B 挑 origin 然後跑起來,測試 S11 沒辦法決定哪個才對。
建議:明寫「沒有追蹤時一律回 2 請人帶參數」,最乾淨;或明寫完整決策表。

severity: major
blocking: 是 — 回傳碼契約「0=閘全過」在非快轉與已是最新兩種真實情形下是假的,沒有條款能抓到
引句:「**回傳碼**:0=閘全過、1=有擋下、2=預演沒跑成」
問題:
- 實驗證實,非快轉被拒時掛鉤仍會被叫,但 stdin 是空的,git 最後回 rc=1。
- 計劃沒定義「結果檔存在且 0 筆擋下、但 git rc≠0」要回什麼。
- 計劃也沒定義「stdin 沒有任何推送行」時,印「便宜的閘都過了」是否誠實。
具體失敗情境:
- 輸入:本機落後遠端,`lumos push-preview`。
- 結果:掛鉤只跑了裁判簽名、簽名檔、圖譜健檢三道全域閘,每個 ref 的閘一道都沒跑,結果檔寫 0 筆。
- 實作者若信結果檔,會回 0 並印「便宜的閘都過了」。這句話對使用者是錯的,因為真推送會被 git 拒絕,而且該 ref 的代碼審與漂移閘從未看過。
- S5、S11 都沒有這個情境。
建議:至少兩條規則。
- 推送行數為 0 時,結果檔註明並回 2,或在訊息中講明「沒有 ref 被檢查」。
- git rc≠0 且結果檔存在但 0 筆擋下,回 2。

severity: major
blocking: 是 — S13 是「放行站點不蓋掉擋下」的驗收準繩,漏列的站點正是計劃承認的最大風險型
引句:「走到每一個放行站點(pitfalls 失敗、沒有 JSON、例外、tier 不是 high、留痕有效、留痕被環境變數跳過、合併側放行)都應仍回 1」
問題:
- 實際判定函式在已經可能記下擋下之後,有 8 個放行 return,計劃只列了 7 個(「留痕有效」被當成一個)。
- 程式佐證:
  - 有效留痕直接命中:`scripts/lumos:51173`。
  - 另一個獨立站點:留痕 sha 過時但走祖先加簿記豁免,`scripts/lumos:51185`。
  - 還有一個擋下站點 `scripts/lumos:51091`:advisory 加 tier=high 時重跑合約測試。計劃沒說它在新模式要不要記成 `bound_tests`。
- 「所有 return 改走同一個收尾函式」是結構規則,但驗收條款是逐站點列舉。照這個清單寫測試,簿記豁免那個站點不會被覆蓋。
具體失敗情境:
- 輸入:表態不完整,加上留痕 sha 過時但屬簿記豁免。
- 結果:實作者漏改第二個站點,直接 `return {"blocked": False,…}`。表態擋下被吞掉,rc 變 0。
- S13 全綠,因為沒有一支測試走到那個站點。
建議:S13 改成「掃描 `_codeloop_guard_verdict` 內所有 `return {"blocked": False`」的守衛,加上逐站點行為測試。
建議:S13 的場景搭法也要寫。pitfalls 失敗那三個站點,前面只可能先有 `bound_tests` 擋下,所以必須先造一個紅的受波及合約測試,並用 `subprocess.run` 注入失敗,計劃都沒提這個接縫。

severity: minor
blocking: 否 — 條款可以寫,但判準太鬆,實作者會各猜各的
引句:「預演擋下時,版控治理帳與逃逸帳的內容都不應改變,本機帳應多出帶 `preview: true` 的事件」
問題:
- 閘名單是「實作第一步先盤點」,尚未做。S9 又只斷言治理帳與逃逸帳兩本,沒涵蓋盤點可能找到的其他版控檔。
- 不如把判準寫成「預演前後 `git status --porcelain` 對受追蹤檔無差異」,這個比兩本帳的斷言強。
- 「兩支寫入器」的說法對 `_gate_event`(`scripts/lumos:1544`)與 `_append_governance_log`(`scripts/lumos:1657`)是對的。我查了 `_codeloop_gov_log` 與 `_codeloop_dispositions_gov_log`,它們直接寫版控帳(`scripts/lumos:49337`、`scripts/lumos:50329`),但只被 `pass/skip/dispositions` 呼叫,掛鉤路徑不會碰到,所以目前沒洞。
- `_gov_routes_local` 要求 `hard is False` 且在白名單,新規則「帶 preview 一律分本機」要明寫是覆蓋這兩個條件,否則 hard 事件會漏進版控帳。
- 另外,`prepush-summary` 要先加進 `_KNOWN_GATES`(`scripts/lumos:9331`),否則 `_gate_event` 會因為不在名單而不寫、只印警告(`scripts/lumos:1537`)。這個地方計劃沒提,S12 的紅測試會暴露,但實作者要自己找。

severity: minor
blocking: 否 — 守衛規則字面不可滿足,需要豁免清單
引句:判斷點之前每一行 `"$PY" "$GRAPHCTL"` 呼叫,緊接著都要有 `pp_stop_if_signaled`
問題:
- 掛鉤裡有刻意 fail-open 的呼叫:`loop escape --auto … || true`、`test-layers … || true`、`bound_tests_advisory`。
- 還有管線式的 `spec-gate | tee`,靠 PIPESTATUS 取 rc。
- 此外 `pitfalls … || true` 在 `$(…)` 裡,`impact_once` 在 `if` 裡。
- 字面規則逐行驗會一直紅。S10 的「pitfalls、impact 等輔助呼叫」這個「等」字也沒列清單。
- S10 後半的測試也沒有搭法:要給假 lumos 一個「睡到收到標記才回」的能力,讓測試只向掛鉤送 SIGTERM。bash 會等前景子行程結束才跑陷阱,測試要處理這個延遲。
- 現有 `_dr_hook_fakes`(`scripts/test_lumos.py:63736`)沒有睡眠和同步機制。
- 第 2 點說 EXIT 陷阱只刪 `$_PP_TMP`,第 7 點說「掛鉤結束時刪票」,票存在 common-dir,不在 `$_PP_TMP`。被 INT 或 TERM 中斷時票不會被刪,只能靠 10 分鐘清理。
具體失敗情境:實作者照字面規則把 `loop escape` 包上 `pp_stop_if_signaled`,守衛測試綠;實作者另一種做法豁免三處,守衛測試紅。

severity: minor
blocking: 否 — 低機率,但是計劃自己不夠明確的地方
引句:`push-preview` 每次開始時先刪掉那個資料夾裡超過 10 分鐘的票與結果檔
問題:
- 多 ref 時最壞時間,一個 ref 可到 300 加 60 加 30 秒,兩個 ref 就接近或超過 10 分鐘。
- 這時另一次 `push-preview`(例如另一個 worktree,同一份 common-dir)啟動,會把這次仍在跑的預演票刪掉。
- 結果是後面的 lumos 事件失去預演標記、寫進版控帳,違反 S9。結果檔被刪還會讓回傳碼變 2。
- 掛鉤用 bash 判「建立不到 10 分鐘」,可攜寫法沒定義(macOS 與 GNU 的 stat 參數不同)。建議用 `find -mmin`,並寫進計劃。
- 清殘檔的門檻最好大於最壞預演時間,或改用票內寫入 pid 與存活檢查。

severity: minor
blocking: 否 — 彙總印法的輸入不夠,實作者得自己加參數
引句:ref 欄只在這次推送有兩個以上非刪除的推送行時印
問題:`push-summary --blocks-file …` 只收擋下檔,不知道這次推送共有幾行非刪除推送行。擋下檔裡只有被擋的 ref,不等於推送行總數。
具體失敗情境:兩個 ref 只有一個被擋時,blocks 檔裡只有一筆,`push-summary` 無從判斷要不要印 ref 欄。S14 只驗「兩個都被擋」,沒涵蓋這個情形。
建議:掛鉤傳 `--refs N`,或把 ref 欄改成「有任何一筆 ref 非空就印」。

severity: minor
blocking: 否 — 描述分類有誤,影響 lint_new 是否在 pitfalls 失敗後執行
引句:pitfalls 失敗時,需要 tier 的後幾道照現在的 fail-open 不判,前面記下的擋下照算
問題:
- 表態(`dispositions`)需要的是 pitfalls 的 JSON 資料,不是 tier;新增告警閘(`lint_new`)兩者都不需要,只吃 `diff_range`(`scripts/lumos:51145` 附近)。
- 這句話沒說清楚 pitfalls 失敗後,`lint_new` 是否照跑。
- 照現況(`scripts/lumos:51074` 是 early return)兩者都被跳過;照字面「需要 tier 的」,`lint_new` 應該要跑。實作者無法判斷。
- S4 與 S13 也沒涵蓋這個交叉。

severity: minor
blocking: 否 — 純實作者要自己查的點
引句:先確認會被呼叫的掛鉤支援預演——用 `git rev-parse --git-path hooks/pre-push` 找到那支檔
問題:
- 實驗證實,這個指令回的是相對於目前目錄的路徑,從子目錄跑會是 `../scripts/hooks/pre-push`。實作要用同一個 cwd 解析。
- 既有 helper `_hooks_path_dir`(`scripts/lumos:27478` 附近的 `_enforcement_prepush_ungated` 用的)已經做同一件事「core.hooksPath 優先,沒設看 .git/hooks」,而且該函式同樣檢查掛鉤文字,建議重用。
- 新子命令還要登錄 `scripts/lumos:52219` 的指令說明表、`scripts/lumos:53127` 附近的 argparse 區塊,以及 `_KNOWN_GATES`。這些計劃都沒列進實作清單。

## 逐節核對

- S1、S2:已讀,無 finding。現有 `t_prepush_cheap_gates_run_before_expensive_suite` 搭法可延用。
- S3:已讀,無 finding。先紅不適用,計劃已註明是保留既有行為。
- S6、S7、S14:已讀,無額外 finding。
  - S6:現有 `_dr_hook_fakes` 的 `FAKE_RC_CMD` 已能讓每個子命令單獨擋。
  - S7:假 lumos 的 `--help` 搭法夠用。
  - S14:多 ref、刪除、tag 的推送行,實驗證實 git 的輸入格式沒有意外。
- S4:除了上面第 5 段提到的接縫,場景搭法缺一個說明。表態不完整加新增告警要造真場景,或用 `_sp.run` 注入;計劃沒給搭法。
- S8、S12:已讀,無額外 finding(S12 的 `_KNOWN_GATES` 見上)。
- 實作清單、回退節:已讀,無 finding。

總結:最高等級是 major,blocking 共 4 條。
- 代碼審 rc1 被吞掉。
- 預演沒有追蹤分支時如何選遠端。
- 預演回傳碼與 git rc 對不上。
- S13 站點清單漏項。

另有 6 條 minor 不阻擋。

相關檔案:
- `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/hooks/pre-push`
- `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/lumos`
- `/Users/enzo/orca/workspaces/lumos-toolchain/prepush-collect/scripts/test_lumos.py`
