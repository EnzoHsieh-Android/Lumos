severity: minor

# 合約與圖譜一致席(合約圖譜-sonnet)第 1 輪報告

範圍:程式 patch 對照 `Systems/guard-kill.md`、計劃〈實作紀錄〉、skill 的 reference.md / commands/06 / commands/INDEX.md。

查證結論(沒問題的部分):
- `cmd_guard_kill` 與 `_kill_read_recipes` 在 patch 裡沒有任何 hunk,guard-kill.md 的兩條 ★INVARIANT★(rc 優先序、`--json` 純度)沒被碰到。
- `check-p2` 已登記進 `_KNOWN_GATES`;P2 段的 `gov_events.append` 只在 `--ci` 落帳(`gov_events` 的註解與 doctor 收尾寫明),跟筆記「`--ci` 才記 `check-p2`」一致;`warn_soft` 預設最多 3 條、`verbose or ci` 全列,跟 guard-kill.md「預設每段最多 3 條、`--verbose`/`--ci` 全列」逐字對得上。
- `HELP_WHEN` 有 `kill-rm`;guard 子指令清單、`gka --file` help 字串、`gkr` 解析器、`main()` 分派都補了;reference.md 子指令全覽 `kill-rm` 已加,80 個頂層命令總數沒變(kill-rm 是二層子指令,不動總數),符合 `t_docs_enumeration_drift` 的口徑;commands/06 與 INDEX 也補了。
- 筆記描述的行為與程式相符:kill-add 驗「這次實際要寫的那一條」、只補 covers 時用既有那條(`recipe = r`)、判重擋下訊息指向 kill-rm、kill-rm 移光整欄拿掉、只對「被移除的配方對得到、剩下的都對不到」的 KEY 行拿掉標記、短身分大小寫都收、對到不同完整身分擋 rc2。
- guard-kill.md 的 `[test:]` 綁定名(`t_guard_kill_add_warns_drifted_recipe`、`t_doctor_kill_recipe_drift`、`t_guard_kill_rm`、`t_kill_recipe_check_matches_guard_kill`)在 `scripts/test_lumos.py` 都存在。
- P2 段編號:現有慣例有 S2–S15 之類的帶數字段,放在 P 段後沿用同一個 `repo_root` 變數,沒有編號衝突。

## F1 修法提示的「短身分哪裡看得到」在筆記與錯誤訊息裡說得比程式實際印的多
severity: minor
blocking: 否
引句:「lumos doctor --verbose 的 P2 段會印每條的短身分」
佐證:file: `scripts/lumos:13257`、file: `scripts/lumos:13485`、file: `docs/lumos-toolchain-knowledge/Systems/guard-kill.md:70`

1. kill-rm 的「對不到」錯誤訊息與 guard-kill.md CLI 段(「kill-add 提醒與 doctor P2 都會印」)都說 P2 會印每條配方的短身分。實際上 `_kill_p2_one` 只有「判斷結果不是 ok / noroot / noplat」的那一類才附 `修法:lumos guard kill-rm … --id …`;`noplat`(「平台 … 不在設定裡,沒驗」)、`noroot`、整欄解析不了這幾類列出的行都沒有短身分,kill-add 同狀態的「沒驗原文」提醒也沒有。ok 的配方更不會印。
2. 具體場景:配方 `platform` 寫了設定裡沒有的平台,P2 列「平台 foo 不在設定裡,沒驗」;使用者想用 kill-rm 移掉它,但工具沒有任何地方告訴他 `--id`(只有被判重擋下時才印 key 前 12 字)。這種情況修法其實是補設定而不是 kill-rm,所以不構成錯誤行為,只是文字過度承諾。
3. 建議:把錯誤訊息改成「失配的那一條在 doctor P2 或 kill-add 提醒會附修法,可整串貼」,筆記改成「判得出失配的配方才會印」。非阻擋。

## F2 doctor 段落總覽處沒有 P2 的指路(僅提醒)
severity: minor
blocking: 否
引句:「section("P2", "殺傷力配方的原文還對不對得上程式(提醒,不擋)")」
佐證:file: `skills/lumos-project-notes/reference.md:63`、file: `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:120`

1. reference.md 第 63 行的 doctor 說明只列到 Check P;lumos-cli-read.md 第 120 行的字母檢查清單寫「以 run_doctor 現碼為準」且用「等」收尾,所以不算錯,但 P2 這段只寫在 guard-kill.md。收工讀 doctor 輸出的人從 skill 找不到 P2 是什麼。
2. 這是脈絡可及性問題,不是行為矛盾;沒給出會誤導出錯行為的場景,所以只列 minor、不阻擋。若 reference.md 該行本來就刻意只列代表性檢查,可直接忽略。

## 檢查過但不報的點
- 計劃「做法 5」寫設定檔讀不了的字面是「設定檔讀不了,這一段算不出來,先跳過」,程式是「設定檔讀不了:<原因>」+ 標題「這一段先跳過」。〈實作紀錄〉已明寫此差異與理由,依派工規則不當 bug。
- 計劃條款 S7「`cmd_guard_kill` 不應被碰到」:patch 確認沒有碰。

最高等級:minor
