severity: major

## g1 等鎖時被中斷,「自己建到一半的鎖檔收掉」在最窄的那個空窗不成立
severity: major
blocking: 是
歸因:有證據的修復回歸
引句:「等寫入鎖時照樣立刻中斷(rc 2,自己建到一半的鎖檔收掉)」
file: `scripts/lumos:70695`(`_excl_lock_try`:`os.open(O_EXCL)` 建好空檔,到 `os.write` 寫入程序編號之間才有內容)
file: `scripts/lumos:75567`(`_situation_rule_drop_lock`:只有第一行等於自己的程序編號才 unlink)
1. `_situation_rule_drop_lock` 的說明寫的情境,是 KeyboardInterrupt 落在「建好鎖檔、還沒進 try」之間。那一刻鎖檔是空的,第一行是 `""`,不等於自己的 pid,所以不會被刪。
2. 最小重現:把 HOME 指到臨時目錄,把 `os.write` 換成會丟 KeyboardInterrupt 的函式,再依序呼叫 `_vault_write_lock(vault)` 與 `_situation_rule_drop_lock(lock)`。
   輸出:
   ```
   KI caught; lock exists: True ''
   after drop_lock exists: True ''
   ```
3. 後果:留下一個沒人會自動接手的空鎖檔(`_excl_lock_try` 不接手既有鎖)。之後所有 `set`、`append`、人裁都卡滿 60 秒才拒絕,要人工清鎖。
4. 修前與修後:修前(f04090128)等鎖時第一個訊號只記下,不會丟 KeyboardInterrupt,也沒有 `_situation_rule_drop_lock`,不會有這條路徑。修後就是上面的重現。
5. 範圍:計劃範圍 4、Systems/guard-kill 都說「建到一半的鎖檔收掉」,實際只對寫完 pid 之後的鎖成立。第二個訊號的強制結束走同一個函式,有同樣的空窗。
6. 這個空窗很窄,但它正是 r3 b1 的修補標的。說法與行為不符,後果是整個筆記庫的寫入被卡住。

## g2 依據來源缺中斷兩段式那一列,違反手冊自己新加的規矩
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「折入新增或改動了機制,同一次在計劃〈依據來源〉補或改那一列」
file: `skills/lumos-code-loop/SKILL.md:898`(手冊〈修前先查世界〉那條規則,出處同上)
1. 本次修補把中斷機制改成「業界兩段式」,計劃範圍 4 也這樣寫。
2. 計劃〈依據來源〉表共 13 列,沒有任何一列講 srvx、Lodestar、webpack-cli、oxi-cli 或兩段式。我用 grep 查「srvx|oxi|webpack-cli|Lodestar|兩段式」,計劃裡只在範圍 4 與審計紀錄各命中一次,表內為零。
3. 業界來源只出現在 Systems/guard-kill 的 WHY(一個 srvx PR 網址)和 SKILL.md(只有名字,沒有網址)。三個月後接手的人從計劃找不到依據。
4. `spec-gate --no-run` 顯示「依據來源: ✓ 13 列」,所以這條不會被工具擋住。

## g3 計劃殘留舊說法與中斷訊息的描述不精確
severity: minor
blocking: 否
歸因:有證據的修復回歸
引句:「範圍 4 規定中斷時收掉程序群組與工作樹、開殘骸清理,並在開跑前印預估、提醒在背景跑。」
引句:「**第一個訊號**在標準錯誤印「收尾中…再按一次 Ctrl-C(或再送一次終止訊號)強制結束,暫存現場留給之後的清殘骸」並溫和收尾」
file: `scripts/lumos:75995`(寫回段第一個訊號的提示是「停下中…再按一次…強制結束」)
file: `scripts/lumos:762`(同區:拿到鎖之後 `st.hint` 改成「收到終止訊號:寫回這一步做完就停…」)
1. 〈實務隱患〉那一行沒更新:兩段式之後,第二個訊號強制結束時工作樹是留殘骸的,不是收掉。
2. 範圍 4 把第一個訊號的提示講成單一句「收尾中…」。實際殺傷力段、等鎖時、拿鎖後各印不同的字。意思相近,字面不同。照字面做驗收會對不上。

## 附:三問、圖譜鏡頭
引句:「**第二個訊號**強制結束:收掉還在跑的測試程序群組、刪自己建的寫入鎖檔、印目前進度後立刻離開,不等收尾」

三問(只列有行為證據的項目):
- ①原問題(r3 資源 z1,收尾卡住時停不下來)的修復。
  - 程式有 `_situation_rule_force_exit`,第二個訊號會收 `_KILL_RUN_LIVE` 裡的程序群組並 `os._exit`。
  - 在 `/Users/enzo/harness/lumos-spec-cite` 跑 `python3.14 scripts/test_lumos.py -k situation_rule`,結果 `143 passed, 0 failed`,含 `t_situation_rule_double_signal`、`t_situation_rule_force_kills_live_group`、`t_situation_rule_write_phase_signals`。
- ②修補處的正常、錯誤、相鄰路徑。
  - 第二個訊號的 rc 與計劃的對照成立:還沒寫計劃 2;正在寫或帳沒記或記帳當中 1;帳已記 0。程式依進度設 `st.force_rc`。
  - 「已寫過」三種出口成立:同段同列 rc 0;別段別列或帳沒有 rc 2;讀帳失敗 rc 2 且不叫人刪條款。這些出口都走 `_situation_rule_already`,最後由 `_situation_rule_say` 回 rc 2。
  - 計劃與三篇筆記裡,r2 的「第二個以後只記下」沒有殘留,只剩 `scripts/lumos` 的說明字串在講撤回。
  - 讀計劃的拒絕條件(讀不到、非 UTF-8、無欄位區塊、未收尾、BOM、CRLF、單獨 CR)與 `load_raw_for_edit` 一致。`_disk_spelling` 的口徑(只差 Unicode 寫法算同一個、某層讀不到就拒絕)也一致。
  - 唯一不成立的是等鎖空窗,見 g1。
- ③新發現同一案例的修前修後。g1:修前沒有這條路徑,修後重現為空鎖檔殘留。g2、g3 是文件問題,修前沒有「兩段式」的描述,所以無法比較。

筆記與手冊檢查:
- `lint` 四篇(Systems/guard-kill、Systems/棧別提問表態閘、Systems/規格閘、計劃)全是 `0 問題`。
- WHY 行都有 `[出處:]` 與 `[因:]`。新增的 `[test:]` 在 `scripts/test_lumos.py` 都找得到:`t_situation_rule_double_signal`、`t_situation_rule_force_kills_live_group`、`t_situation_rule_write_phase_signals`、`t_situation_rule_signal_during_write`、`t_isolated_worktree_keep_failed_build`、`t_situation_rule_already_seg_row`、`t_situation_rule_plan_disk_spelling`、`t_spec_gate_ruled_ai_reminder`。
- `spec-gate --no-run` 的條款綁定是「19 條全標」。
- `skills/lumos-project-notes/commands/06-代碼審與推送.md` 的人裁那一列只講用法,沒有 rc 與中斷細節,跟上列文件沒有矛盾。
- 規格閘那篇 WHY 的 consent 標示、SKILL.md 的〈中斷處理照兩段式〉、templates.md §5 的〈寫小工具前先找既有〉彼此一致。
- 這兩處手冊引的 `cap-retro.json` 在工作目錄存在,但不在提交 7e2c292e3 裡(整個 `governance/review-reports/code-情境題引規格出處/` 目前是未追蹤)。提交時要記得一起帶進去,否則引用會懸空。這不是 finding,只是提醒。

圖譜鏡頭:這次沒附固定席節點(鏡頭計算超時)。我只憑 diff 判斷:Systems/guard-kill、Systems/棧別提問表態閘、Systems/規格閘與計劃四篇是這次實際牽連的,都已逐句對過程式。

最嚴重:major;blocking 共 1 條
