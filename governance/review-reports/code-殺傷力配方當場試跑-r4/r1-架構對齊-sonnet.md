severity: minor

## 三問摘要

1. 分層與依賴方向:結構對。`_guard_kill_pick` 改收 ctx,由 `cmd_guard_kill` 用 `_guard_kill_cfg` 讀完設定再交給 `_kill_check_ctx(repo_root, pdata)`,沒有新增跨層直呼;`_kill_check_ctx` 加選用參數是向下相容(file: `scripts/lumos:13959`)。唯一不同:`_guard_kill_cfg` 只擋 ValueError,鄰居 `_kill_cfg_load` 另擋最外層非物件與各種例外(file: `scripts/lumos:13933`),這是「--id 的設定讀法」與「判法的設定讀法」兩條路,但 guard kill 原本就是只擋 ValueError,屬沿用既有行為,不算新增。
2. 命名與錯誤處理:原地擋的 verdict 用 `error`、detail 帶中文說明,跟 guard kill 既有的「test 名不合法」「file 路徑逃逸」同形;擋的順序(old 在數原文前、new 在原文恰好一次後)照 `_kill_judge_file`(file: `scripts/lumos:14172`)。兩處小不對齊見 F1、F2。
3. 第二種做法:`_krc_match` 仍是對照測試(malformed 多認同一句字串,與 `_kill_recipe_judge` 的 detail 同源),未變成自證。原地擋是對 `_kill_judge_file` 型別規則的手寫子集,見 F1。沒有發現須標 major 的第二種做法。

## F1 原地擋只複製了 `_kill_judge_file` 的一部分規則
severity: minor
blocking: 否
引句:「                if not isinstance(r.get("new"), str):」
file: `scripts/lumos:15183`
1. `_kill_judge_file` 對套壞法那一步判四件事:old 沒寫、new 不是字串、new 含替身字元(寫不成 UTF-8);guard kill 內聯的版本只判 old、new 是否為字串。old 缺欄位(空檔剛好命中一次)、new 含替身字元兩種,內聯不擋,而 `_krc_match` 的 malformed 仍把 UnicodeEncodeError 列為「當掉也算」,所以對照測試不會翻紅。
2. 這是同一條「什麼叫格式壞」的規則存在兩份、涵蓋面不同。對照鄰居:test 名白名單是 guard kill 與判法共用同一個 `_KILL_METHOD_OK_RE`,沒有各寫一份。⚠ 判不準是否算「第二種做法」,故降為 minor;可考慮抽一個小函式(給 r 回 detail 或 None)讓兩邊共用。
3. 沿用已知範圍:不帶 --id 的替身字元當掉屬計劃已列,不重報;這裡只指出結構上的缺口。

## F2 `_guard_kill_pick` 的兜底靜默吞例外,跟鄰居的兜底會留痕不一致
severity: minor
blocking: 否
引句:「判斷自己出錯不擋(照 kill-add 提醒與 P2 的兜底);guard kill 碰到會當掉的兩步已原地擋」
file: `scripts/lumos:15354`
1. 註解說「照 kill-add 提醒與 P2 的兜底」,但 `_kill_add_warn` 的兜底會印一行「判斷時出錯(類別: 訊息),沒驗原文」(file: `scripts/lumos:14204` 起的 except 段),P2 也會記成沒驗;這裡 `res = None` 完全不留痕,使用者看不到「格式壞的檢查被略過」。
2. 結構對(同樣是判法外層包兜底、不擋),僅錯誤處理的可見度不同,故 minor。要對齊就在 except 內往 stderr 印一行,或改註解不再宣稱「照」它們。

不對齊共 2 條,其中 major 0 條
最高等級:minor,blocking 共 0 條
