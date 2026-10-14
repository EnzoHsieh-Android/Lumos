severity: minor

我不再跑任何工具,也不清臨時目錄。我的實驗檔留在 `/tmp/lumos-seat-work/code-代理繞閘字樣問人/合約圖譜-sonnet/`,由你刪。

我沒跑 `test_lumos.py`,因為要求不改 repo,怕測試留下檔案。所以測試只靠讀碼核對,另用自寫腳本載入掛鉤實測行為。

## Findings

1. S4 條款文字比掛鉤的實際行為窄,也比〈做法〉窄,廣的那幾種字面判沒有測試
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
severity: minor
   blocking: 否
   引句:「`rebase`、`am`、`cherry-pick`、`pull` 帶 `--no-verify` 只跳過 pre-merge-commit、commit-msg 這類本 repo 沒裝的掛鉤,不影響 Lumos 的提交前閘與推送前閘」
   - `ls scripts/hooks` 只有 `pre-commit`、`pre-push`、`post-commit`,沒有 `pre-merge-commit`,也沒有 `commit-msg`。
   - `git merge --no-verify` 跳過的正是這兩種,同一個理由卻被列進命中:`bypass_reasons("git merge --no-verify main")` 回 `['no-verify']`。
   - 這是誤問方向,符合 d2 的取捨,但〈做法〉與〈範圍〉對 merge 的處理互相矛盾,三個月後的接手人會不知道依哪邊。
   - 應該是:在〈範圍〉明寫 merge 是刻意多問,或把 merge 從 `--no-verify` 命中拿掉。
   - 歸因:未判定。

3. 計劃沒把 `_hookevent.py` 的修剪暫存檔改動列進 `lands_in` 與〈做法〉
severity: minor
   blocking: 否
   引句:「lands_in:\n  - Systems/代理繞閘問人\n  - Systems/lumos-cli-lifecycle」
   - `lumos impact --file scripts/hooks/claude/_hookevent.py` 顯示它的家是新開的 `Systems/掛鉤存活事件`。
   - 專案規則是計劃的 `lands_in` 要列出現況落在哪幾篇,新開的這篇卻沒列。
   - 〈做法〉也沒提 mkstemp 修剪,只在〈審計修正紀錄〉裡一句帶過。
   - 應該是:`lands_in` 加 `Systems/掛鉤存活事件`。
   - 歸因:未判定。

4. 〈回退〉三步驟能讓掛鉤停止問人,但沒說明中間狀態,也沒列要連帶改的名單
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
