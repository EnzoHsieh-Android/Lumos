severity: minor

審的是測試文件組(rest.patch)加固定版本 9b8ce146 的完整程式碼。我沒找到 blocker 或 major。下面的發現都是文件和程式對不上、或條款寫了但測試沒驗,都屬小問題。

1. 條款 S3 與計劃〈做法〉明說「同指令前面動過遠端設定」要照問,但 `git -c remote.*.pushurl=…` 和 `GIT_CONFIG_KEY_n=remote.*` 沒被當成動過遠端設定,於是照樣豁免。
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
severity: minor
blocking: 否
引句:「下面查遠端、查工作樹的 git 子程序用 `_inner_budget()` 當逾時」
- 同一段稍後寫「不用 `_inner_budget` 的 1 秒下限」。
- 程式實際用的是 `_remaining_budget()`,`_inner_budget` 只留作逐字複本(為了鄰居掛鉤的一致性測試)。
- 前一句應改成 `_remaining_budget`。

3. 存活事件檔修剪的描述已過時。
severity: minor
blocking: 否
引句:「存活事件檔滿 512KB 會砍到剩最後 2000 行」
- 修補後的 `_hookevent._trim` 還加了「總大小壓在 `MAX_BYTES//2` 以內」。
- 〈做法〉和〈實務隱患〉的「上限 2000 行」沒同步。
- `Systems/掛鉤存活事件` 的 PITFALL 寫對了。

4. 條款 S3 的「GIT_DIR 一族」範圍比實作寬。
severity: minor
blocking: 否
引句:「整條指令任何地方設過 `GIT_DIR` 一族或用了 `--git-dir`/`--work-tree`」
- 〈做法〉和程式都是「之後的命中」才不豁免。
- 重現:`cd exp && git commit -n -m x; GIT_DIR=real/.git git status` 回 `[]`。
- 程式行為合理,應改條款字句成「該設定之後」。

5. 條款寫了但測試沒驗到的項目。每項我都用 `bypass_reasons` 手動確認過,目前程式行為是對的,只是沒有測試釘住。
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
