severity: minor

審查範圍:整份 diff(1408 行)逐 hunk 讀完。實測:在臨時複本 /tmp/mb2-copy 跑 `python3.14 scripts/test_lumos.py -k plugin`(108 passed, 0 failed);`claude plugin test mods/claude/lumos-context`(6 pass);`claude plugin validate`(gatingHooks 只有 session.compact 且 hasCatch true);在隔離的 CLAUDE_CONFIG_DIR 先以只列一支外掛的市集檔登記市集、再把市集檔改成兩支,`claude plugin install lumos-context@lumos-toolchain --scope user` 直接成功(readFromFolder 指向資料夾),所以「新增外掛不必先更新市集快照」成立。
尾端沒有看到「lumos 自動附加」段,有看到「圖譜沒有釘到節點」備援段(三格皆空)。

逐項走過、判定正確(不列 finding)的路徑:
- 指示邊界:undefined、空字串、純空白、含 \r\n(`trim()` 去掉 \r,整行比對成立)、標記在句中(不算已附)、很長(無長度限制、純字串串接)。
- 例外:`.catch(($, e, next) => next(e))`;掛鉤在 next 之前丟錯,catch 的 next 只往下跑一次;next 之後丟錯則重播上次結果,型別檔 Caught 的說明一致。`agentId` 是 pinned 欄位,`{...e, instructions}` 會保留。
- 安裝端:一支失敗不影響下一支、取最差(max 同分取第一個,無影響);裝完以列表確認;市集檔 plugins 欄位怪或有 BOM 回空集合不丟例外。
- 移除端:只在全部外掛移除成功才移市集;失敗時手動指令只列失敗的外掛加市集;舊版只裝事件帳的機器跑新版 uninstall 時 context 沒列出就略過、市集照移。
- 舊版 lumos 讀新市集檔:舊版只依 id 裝 lumos-ledger,不受影響(僅新舊混用時舊版 uninstall 會移掉市集而留下 lumos-context 孤兒,屬可接受的過渡窗口,不標)。

### F1 plugin.json 與市集檔描述仍宣稱「把會談編號交給 lumos」,但這項已明文不做
severity: minor
blocking: 否 — 只是對使用者顯示的描述文字與實際行為不符,不影響執行
1. `mods/claude/lumos-context/.claude-plugin/plugin.json` 的 description 寫「把當下的會談編號交給 lumos」;`.claude-plugin/marketplace.json` 新列的那支 description 寫「把會談編號交給 lumos」。
2. 同一份 diff 的計劃筆記「不做」節與 `Systems/lumos-context` 都寫明會談編號項實測不成立、整項停下;外掛原始碼 `register.ts` 只掛 `session.compact`、不碰環境變數(S6 掃描也釘住不准)。
3. 使用者在 `claude plugin list`/市集看到的說明因此是不存在的能力。
引句:「Lumos 交棒脈絡:壓縮前叫摘要保住交棒狀態,把會談編號交給 lumos」

### F2 新增 21 處無關測試的檢查標籤被從 S7 改成 S4
severity: minor
blocking: 否 — 只改 check 標籤文字,測試邏輯與結果不變,但標籤與所屬條款不一致
1. diff 在 `t_decision_add_standard_yaml_safe`、`t_doctor_s7_overloaded_note`、`t_escape_stats_next_stage_and_unknown_stage`、`t_cap_hint_vacuous_round_counts_zero`、`t_lint_waive` 等測試裡,把 `check("S7 …")` 的標籤改成 `check("S4 …")`(共 21 行,`git diff 70ffba32 HEAD -- scripts/test_lumos.py | grep -cE '^-.*"S7 '` 得 21)。
2. 這些測試的 docstring 仍寫 `[S7]`(例 `"""[S7] 決策內容也走同一套白名單…"""` 在 file: `scripts/test_lumos.py:2407`),所屬計劃節點的條款也是 `[S7] … [test:t_decision_add_standard_yaml_safe]`、`[S7] … [test:t_escape_stats_next_stage_and_unknown_stage]`;`t_doctor_s7_overloaded_note` 檢查的是 doctor 的 S7 段(同函式內仍 `_section_of(..., "S7")`)。
3. 結果:失敗訊息會標 S4,對不上條款;`t_set_other_keys_single_value_only` 本來就是 [S4] 的測試,標籤出現重名。看起來是想把新條款編號搜尋取代時誤傷。本次改動主題與這些測試無關,屬夾帶改動。
引句:「check("S4 決策內容結尾裸冒號 → 加引號(標準 YAML 否則報錯)」

### F3 外掛與市集訊息缺空格「略過Claude 外掛」
severity: minor
blocking: 否 — 純顯示字樣
1. `_plugin_sync_msg` 的 absent、no-source 分支把 `who = "Claude 外掛 …"` 直接接在「略過」後面,實際輸出 `  (略過Claude 外掛:LUMOS_SKIP_CLAUDE_PLUGIN=1)` 與 `  (略過Claude 外掛 lumos-context@lumos-toolchain:lumos 來源 repo 的 …)`(在複本以 `m._plugin_sync_msg(...)` 實跑得到),舊字樣是「略過 Claude 事件帳外掛」帶空格。
引句:「return f"  (略過{who}:{detail or '找不到 claude 指令'})"」

### F4 uninstall 以外掛 id 移除,不確認市集是不是我們的(範圍隨清單擴大)
severity: minor
blocking: 否 — 沿用既有行為,只是影響面從一支變兩支;需要使用者自己加了同名 lumos-toolchain 市集才會踩到
1. `_teardown_claude_plugin` 迴圈對每個 pid 只看 `_lumos_plugin_user(claude, pid)` 就 `uninstall pid --scope user`,沒有先判市集是不是 `_lumos_market_is_ours`。
2. 輸入:使用者自己加了一個同名 `lumos-toolchain`(github 來源)市集並從中裝了 `lumos-context`。走到迴圈那行會把它移掉(市集保留,因 else 分支只在 `_lumos_market_is_ours` 為真才移)。事件帳那支在改動前就有同樣行為,故只標 minor。
引句:「_claude_do(claude, ["plugin", "uninstall", pid, "--scope", "user"])」

## 圖譜鏡頭
- `Systems/lumos-cli-lifecycle`(外掛安裝與移除):本次改動等於這節宣稱的行為擴成清單;合約「不併進 `_sync_global_hooks` 回傳字串」「掛在 `cmd_uninstall` 開頭探針之後」未被動到(`_sync_claude_plugin` 呼叫點與回傳仍是 ok/absent/no-source/failed 四態),不影響。唯一不一致:該節仍有一句「teardown 的確認清單有列出外掛與市集」,diff 已同步改文字,不影響。
- `Systems/lumos事件帳`:市集檔多列一支,該筆記已補「市集列的外掛要恰好等於外掛清單」,並有 `t_plugin_market_matches_list` 守衛;原 `t_ledger_plugin_files_valid` 的「市集只列一支」已改成對清單,不影響其他行為。
- 其他沒有被釘到的節點,備援段三格皆空,無可逐條答之項。

## 角色鏡頭
LUMOS-ROLE-CARDS 尾端沒有附前端或後端卡,略過。

總結:最嚴重 minor,blocking 0 條
