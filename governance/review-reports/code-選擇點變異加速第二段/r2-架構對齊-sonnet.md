severity: minor

**問 1 分層與依賴方向:對齊。**
- 不合併的原因只剩 `mg.plats` 一處存放。`_kill_merge_off` 寫 `mg.plats[plat] = (False, why)`(`scripts/lumos:28924`)。這跟斷路器既有寫法同形,斷路器寫的是 `mg.plats[plat], mg.tripped = (False, "斷路器"), True`(`scripts/lumos:29094`)。
- `_KillMerge` 少了 `off` 欄位(`__init__`,`scripts/lumos:28892` 一帶),沒有第二份原因存放。
- run 事件的 `merge_off` 在報告端由 `plats` 算出,過濾條件是未啟用、且原因不是「斷路器」(`scripts/lumos:79111`)。這和既有分工一樣:合併物件只存狀態,`_choice_kill_report` 負責組成帳欄位。
- 印字由呼叫端用 `quiet` 決定:`_kill_merge_base` 已經用 `_CHOICE_MERGE_BASE_WHY` 自己印過一行,所以傳 `quiet=True`(`scripts/lumos:29011`);中斷接著就停,也傳 `quiet=True`(`scripts/lumos:29167`)。上一版是在函式裡看 `why` 前綴字串判斷,現在改成參數,比較貼近專案做法。專案裡已有 `quiet=` 參數的先例(`_reinject_all`、`_rel_cascade_pending`,`scripts/lumos:34829` 與 `:33833`)。
- 沒有跨層直呼。`_kill_merge_iter` 的 `got is None` 分支不再自己寫 `mg.plats`,改由 `_kill_merge_ready` 與 `_kill_merge_base` 先記好。

**問 2 命名與錯誤處理:大致對齊,有 1 條 minor。**
- `_ran_solo` 帶底線,沿用 `_mtime_unsure`、`_weak_why`、`_compile_err` 這批 kill 列內部欄位的標記方式。丟出的 JSON 過濾清單也同步改了(`scripts/lumos:28619`)。
- `_KillHooks.note` 交給 `on_row` 的鍵 `ran_solo` 不帶底線,和同一個字典裡的 `weak`、`compile_error` 一致(`scripts/lumos:28708`)。
- 原因字串都是固定中文詞,沿用既有的 `合併基準:<原因>`、`指令過長` 這類寫法。新增的「合併道不足 2 支」在 `_kill_merge_ready`(`:28959`)和 `_kill_merge_base`(`:28998`)兩處用的是同一個字串。
- 印字格式不變,還是 `⚠ <平台>:這次不合併(<原因>),照逐支跑`。
- 
severity: minor
不對齊,minor:帳欄位名是 `single_runs`(`scripts/lumos:18472`、`:78771`、`:79036`),在事件列、`on_row`、`cmd_guard_kill` 裡這個數字叫 `ran_solo`。同一個數量在帳上和執行期用兩套名字。這輪改名的理由是「免得跟判法 single 撞」,結果帳欄位仍叫 `single_*`。
  引句:「if row.get("ran_solo"):   # 壞法階段真的逐支跑了這一支」
  file: `scripts/lumos:79053`(r2-repair.patch 內該行在 patch 第 477 行)
  blocking: 否
  歸因:有證據的修復回歸(這輪改名只改了一半)

**問 3 第二種做法:大致沒有,有 1 條 minor。**
- 沒有第二份原因存放:`off` 字典已移除。
- 沒有第二種印字分流:全走 `_kill_merge_off` 加 `quiet` 一條路。
- 沒有第二種欄位標記:`_ran_solo` 取代 `_single`,仍是同一套底線標記。
- 不對齊,minor:`merge_off` 的過濾直接寫死字面字串 `"斷路器"`(`scripts/lumos:79111`),而這個字串的寫入端在 `_kill_merge_breaker` 一帶(`scripts/lumos:29094`)。兩處靠字面量對上,沒有共用常數。對照既有寫法:`_CHOICE_MERGE_BASE_WHY` 這種原因字串是集中放在一張表,不是散在各處。這不算第二份存放,但把「哪些原因算斷路器」的判斷藏進報告端字面比對,改字時會漏。
  引句:「merge_off={q: why for q, (on, why) in (getattr(mg, "plats", None) or {}).items() if not on and why != "斷路器"})」
  file: `scripts/lumos:79111`
severity: minor
  blocking: 否
  歸因:有證據的修復回歸(`merge_off` 改由 `plats` 算出才引入這個比對)

不對齊共 2 條,其中 major 0 條。⚠ 我沒有重跑測試,只讀 patch 與 repo 真代碼比對。
