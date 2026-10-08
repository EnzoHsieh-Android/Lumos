severity: major

已讀範圍:全份 spec;對照 negguard repo 的 `_kill_read_recipes`、`_kill_recipe_key`、`cmd_guard_kill_add`、`_append_governance_log`、CI 設定、skill 文件。「落點」節與 `--file` 說明字串已讀,見 F4。

## F1 kill-rm 先刪舊配方,接手的人就失去 platform、covers、note、test,重寫時沒東西可照
severity: major
blocking: 是
引句:「`lumos guard kill-rm <節點> --id <短身分>`:短身分是 `_kill_recipe_key` 的前 12 個字元(P2 與 kill-add 提醒都會印);在那篇的配方裡找身分以它開頭的,恰好一條就移除」
file: `scripts/lumos:12934`
1. 修法鏈是「kill-rm 舊的 → 照現在程式改寫 → kill-add → 提交 → guard kill」。kill-rm 一執行,舊配方的 `platform`、`covers`、`note`、`test`、`new` 就從筆記消失。spec 沒有要求 kill-rm 印出被移除那條的完整內容,P2 與 kill-add 的提醒也只印 file、狀態、invariant 前 30 字。
2. 接手的人要重新 kill-add 時,必須自己從 git 歷史或記憶翻出這些值。漏帶 `--platform` 時,多平台專案的配方會悄悄落到預設平台。漏帶 `--covers` 時,`scripts/lumos:38855` 一帶的背書計算只認筆記現有配方的 covers,該題目的背書就無聲失去。
3. rtb 有 73 條配方,10 條掛在 ★INVARIANT★ 上、部分帶 covers。照字面做,K1 清存量時會批量丟掉 covers 與 platform。
4. 折法有兩個方向:(a) kill-rm 成功後把被移除那條的完整 JSON 印到標準輸出,並附一行可貼的 kill-add 骨架(已帶 platform、test、covers、note);(b) 修法文字改成「先 kill-add 新的、再 kill-rm 舊的」。原因是新配方的原文不同,身分不同,不會撞判重;換 `old` 的情況下 kill-add 不需要先移除舊的。(b) 同時避免中間狀態被誤打斷時,KEY 行標記被拿掉再補回。

## F2 格式壞的配方(元素不是物件,或 invariant、file 缺欄位)拿不到可用的短身分,kill-rm 修法走到死路
severity: major
blocking: 是
引句:「每行結尾接可以直接貼的修法「修法:lumos guard kill-rm <節點> --id <短身分>,照現在的程式改寫後再 kill-add」。」
file: `scripts/lumos:38855`
1. spec 要求 `malformed` 狀態的提醒也接同一句 kill-rm 修法,並同時規定「顯示時 `invariant` 缺或不是字串一律當空字串」。
2. 既有身分的計算是 `_kill_recipe_key(node, rec.get("invariant"), ...)`,缺欄位時用 `None`。因此顯示用的 `""` 和 kill-rm 實際比對、`guard kill` 寫 kill-log 用的 `None` 不一致,算出來的雜湊不同。spec 沒說短身分用哪一種值算。實作者各挑一邊,P2 印的 id 就可能 kill-rm 對不到。
3. `kill_recipes` 陣列裡的元素如果根本不是物件,既有程式在 `scripts/lumos:38855` 與 `cmd_guard_kill_add` 的判重迴圈都是 `isinstance(r, dict)` 跳過。這種元素無法算出身分,kill-rm 沒有任何辦法指到它;兩條缺欄位的配方又會算出相同身分,落進「多條就擋下」。
4. 結果:這類配方 P2 每次都唸、提醒叫人 kill-rm、kill-rm 卻動不了它,只能手改開頭欄位(違反「開頭欄位用指令改」的家規)。
5. 折法:明寫身分用「欄位原值(缺則 None)」算,與 `guard kill` 的 recipe_id 完全一致;非物件元素改印「第 N 條(0 起算)」並讓 kill-rm 另收 `--index`,或明確宣告這類只能手改,並讓提醒不要印 kill-rm 那句。

## F3 RETIRE-IF 的第一個條件字面上量不到,而且在工具鏈自己必然成立
severity: major
blocking: 是
引句:「RETIRE-IF: 工具鏈 CI 的 `lumos doctor --ci` 連續 8 週沒有寫出任何 `check-p2` 事件,而且 rtb 同期回報的 P2 段也是 0 條」
file: `scripts/lumos:1251`
1. `_append_governance_log` 寫的是工作目錄裡的 `docs/.governance-log.jsonl`。CI 的 `python scripts/lumos doctor --ci`(`.github/workflows/ci.yml:103-104`)跑在臨時 checkout,事後沒有任何步驟把它提交或上傳。所以「工具鏈 CI 寫出的事件」查不到任何帳。真正會寫進被追蹤檔的,是開發者本機 pre-push 的 `doctor --ci`,而那份檔是否有提交、什麼時候提交都不固定(目前 git status 顯示為未提交修改)。
2. 工具鏈本身只有 1 條配方而且對得上,P2 永遠不會列項目,也就永遠不寫 `check-p2`。第一個條件從上線第一天起恆成立,「連續 8 週」沒有鑑別力。真正有鑑別力的只剩 rtb 那個條件,而它是靠別的會談口頭回報,沒有指令、沒有量法。
3. 接手的人在 8 週後看到這條,無法照字面判斷該不該撤 P2 段。
4. 折法:把 RETIRE-IF 改成可以敲一行指令判的形式,例如「rtb 端 `lumos gov` 或 `grep check-p2 docs/.governance-log.jsonl` 在連續 8 週內無事件」;並明寫哪個 repo、哪個帳、誰回報。另改掉「工具鏈 CI 每次推送都跑 `lumos doctor --ci`」的事件落帳敘述,CI 跑完帳不留存。

## F4 落點「skill 的 guard 指令表補一列」指不到具體檔案,多處散落會漏
severity: minor
blocking: 否
引句:「skill 的 guard 指令表補 kill-rm 一列;kill-add 的 `--file` 說明字串從「相對配方平台 root」改成「相對配方平台所在 repo 的最上層」」
file: `skills/lumos-project-notes/reference.md:594`
1. kill-add 出現在 `skills/lumos-project-notes/reference.md` 的第 117 行(子命令全覽)、第 530 與 594 行(用法)、`commands/06-代碼審與推送.md` 第 23 到 24 行、`commands/INDEX.md` 第 36 行,以及 `Systems/guard-kill.md` 第 65 行。「一列」沒說是哪個表,實作者很可能只補一處。
2. 放行理由:漏補只是說明文件不完整,不影響指令行為,且 spec 另有「散落同步靠漂移守衛」的既有慣例可補。實作時列清單即可。

REVISIT 一節已讀:日期、門檻、「只准延一次」都可照字面做,無 finding。其餘做法節(判斷函式、設定檔、kill-add 提醒、P2 段)在接手視角下無 finding。

最高等級:major;blocking 共 3 條
