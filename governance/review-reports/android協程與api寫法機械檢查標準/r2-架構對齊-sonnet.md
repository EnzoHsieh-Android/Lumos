severity: major

判讀前提:我只核對 r2 快照和 repo 現況,不重報 r1 已解決的點。r1 的六條裡,快照已修好五條。
- 觸發字比對已放進 lumos 本體,鉤子只印。
- 預算改從 `HOOK_BUDGET` 的內層切一半,不再另設 `stop_budget_sec`。
- 擋停名額標記改放既有目錄、過同一個信任檢查。
- 另開 `Systems/kotlin規則包` 當規則包的家。
- 型錄的家掛進同一篇。
- 新增告警閘本體的落點,快照寫進 `Systems/pitfalls-code-loop`。

## 問 1:分層與依賴方向

**鉤子仍是薄殼,分層對齊。**
- 改檔前推列:快照寫「比對在 lumos 本體做,鉤子只印」。這跟棧別題一致,既有做法是鉤子只讀 lumos 回傳的 `stack_questions_applicable`(`scripts/hooks/claude/impact-hook.py:688-706`)。
- 回合結束那道:鉤子子程序呼叫 `lumos lint-new --worktree --only`。這跟 `_impact_missing` 叫 lumos 的分工同形(`scripts/hooks/claude/check-graph-sync.py:739-750`)。
- 代碼審通過前先查:抽共用函式,`pass` 與推送檢查同呼叫,沒有跨層。

不對齊:新旗標 `--delta-stdin` 見問 2。

## 問 2:命名與錯誤處理

對齊的部分:
- `LUMOS_STOP_LINT_OFF` 對應 `LUMOS_STOP_BLOCK_OFF`(`scripts/hooks/claude/check-graph-sync.py:893`)。
- `--budget 秒` 跟 `drift scan` 同名(`scripts/lumos:70713`)。
- `--only <檔>…` 的形狀跟 `--only` 的 nargs 用法相同(`scripts/lumos:70654`)。
- 回合結束的 `stop_hook_active` 與名額檢查,沿用既有同一套(`scripts/hooks/claude/check-graph-sync.py:895`)。

**(a) `--delta-stdin` 是同一件事的第二個入口。** `lumos impact --file` 已有 `--stdin-payload`(`scripts/lumos:70422`),讀 `{query, prospective}`。改檔前鉤子現在就用它,而且 payload 已經帶 `delta_text` 與 `delta_truncated`(`scripts/hooks/claude/impact-hook.py:1027-1029`)。快照另開一個 `--delta-stdin`,同一個子指令就有兩個不同的 stdin 協定,內容還幾乎重疊(都是寫入內容)。對齊的做法是在既有 payload 加鍵,或讓決策表命中當作 `--ranked` 輸出的一個欄位。

severity: major
blocking: 是
引句:「鉤子把寫入內容交給 `lumos impact --file <檔> --delta-stdin`(新增旗標)」
file: `scripts/lumos:70422`
file: `scripts/hooks/claude/impact-hook.py:1027-1029`

**(b) 新設定鍵 `include_test_paths` 要走既有的驗證路徑。** `_lint_new_config` 的驗證迴圈只處理正整數鍵(`scripts/lumos:38690-38696`),而 `include_test_paths` 是清單。快照沒寫型別錯誤時的行為。既有慣例是「讀不懂就用預設並加一條 warnings」。另外,推送閘讀設定是從快照位元組讀(`from_snapshot=True`,`scripts/lumos:38659-38660`),新鍵要走同一條路。

severity: minor
blocking: 否
引句:「`.lumos/config.json` 的 `lint_new` 區塊加 `include_test_paths`(副檔名清單,預設空 = 照舊排除)」
file: `scripts/lumos:38493-38497`

## 問 3:第二種做法

**暫時索引不是第一次用,也沒有抽檔兩套的問題。**
- 暫時索引已有先例:`_spec_freeze_build` 用 `GIT_INDEX_FILE` 指向暫存索引,做完就刪(`scripts/lumos:65585-65597`)。
- 工作樹終點是改動清單的新來源,不是新的抽檔方式。基準版仍走既有的 `_lint_new_extract`(`scripts/lumos:38816`)。快照也講明「現在版直接讀工作樹」。
- 既有 `_lint_new_changed_files` 對提交範圍用 `git diff --name-status --find-renames`(`scripts/lumos:38699-38710`)。快照的暫時索引加 `diff --cached --find-renames HEAD` 是同一種輸出,可以共用那段狀態碼解析。快照沒明說共用,我標 ⚠:若另寫一份解析,就會有兩份。

**`lint-new` 跟 `lint-check` / `lint-waive` 的分工清楚。**
- `lint-check` 管宣告健康度(`scripts/lumos:70485`)。
- `lint-waive` 管放行(`scripts/lumos:70490`)。
- `lint-new` 管「判新增告警」,而且不寫治理帳。
- 三者分工不重疊,放行仍只有 `lint-waive` 一個入口。

**`--worktree` 旗標。** 既有指令裡沒有這個命名。但它是新的終點種類,不是既有概念的別名,不算不一致。

## 問 4:落點

`Systems/kotlin規則包` 新開合理。理由有兩點:
- 規則包、型錄、semgrep 規則是工具鏈自己的程式與資料,`linter精選目錄` 的定位是菜單,只管一支 `configs/detekt/android.yml`。
- 這符合專案鐵則第 5 點(每支檔要有家)。

其餘落點也對得上:
- 擋停鉤子兩道落在 `Systems/graph-sync-coverage`(管 `check-graph-sync.py`)。
- 改檔前推列落在 `Systems/改檔前推播`(管 `impact-hook.py`)。
- 表態與代碼審落在 `Systems/棧別提問表態閘` 與 `Systems/pitfalls-code-loop`。

沒有新的不一致。

總結:不對齊共 2 條,其中 major 1 條。

臨時目錄:本席沒建任何暫存檔或實驗 repo。
