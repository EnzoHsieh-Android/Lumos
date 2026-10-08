severity: major

## F1 設定先自己解析的折法漏了 load_platforms 自己會丟 ValueError,也沒用它現成的 cfg 參數
severity: major
blocking: 是
引句:「解析得了才呼叫 `load_platforms`,★一次判定裡只呼叫一次★,結果給每條配方共用。」
file: `scripts/lumos:4504`
1. `load_platforms(repo_root, cfg=None)` 已有共用入口:傳入已解析的 dict 當 `cfg` 就不會再讀檔、也不會走「壞 JSON 印警告退回預設」那條路。spec 折法是「自己解析一次、再呼叫 load_platforms(沒提 cfg)」,等於同一支檔讀兩次(兩次之間被改會不一致),且沒用既有參數;既有慣例(`_note_audit_config`、`_note_shape_config`)是「讀一次、壞了就回退預設加一條警告」,不是自己另造「設定檔讀不了」旁路。
2. 更要緊:`load_platforms` 對設定錯誤(`platforms.<名>` 不是物件、profile 名未知、多平台缺 default_platform、default 不在清單)會 `raise ValueError`(同檔 4504 起的函式本體)。既有呼叫端(例如 `cmd_guard_kill` 在 13170 附近)都包 `except ValueError`。spec 的「設定檔讀不了」只定義了「解析不了或不是物件」,沒定義 ValueError。照字面實作:kill-add 現在完全不碰 `load_platforms`,新增判斷後遇到「JSON 合法但 profile 名寫錯」的設定,kill-add 會直接丟例外中斷、不寫入,違反 S1/S2「照舊寫入、回傳碼不變」;P2 則只靠外層「這一段算不出來」兜底,無法對該情況給「設定檔讀不了」的明確說明。
3. 折法:spec 明寫 (a) 解析成功的 dict 以 `load_platforms(root, cfg=<dict>)` 傳入;(b) `ValueError` 一律歸入「設定檔讀不了」(kill-add 印「⚠ 提醒:<原因>,沒驗原文」照舊寫入;P2 印整段跳過);(c) S2/S4 補一個「JSON 合法但 platforms 設定錯誤」的測試題。

## F2 kill-rm 的併發寫法跟專案既有「移除」類指令不同(無 _vault_write_lock)
severity: minor
blocking: 否
引句:「同檔原子寫入(同 kill-add 的寫法)。」
file: `scripts/lumos:15489`
1. `lumos remove`(`cmd_remove`)與 drift ack、逃逸撤回都包 `_vault_write_lock`;kill-add 沒包(`_write_lf` 註解明寫「其他寫入指令仍是 last-write-wins,accepted」)。kill-rm 照 kill-add 做不算引入第二種做法,但它是讀改寫、會刪資料,兩個同時跑會把對方的配方變更吞掉。
2. 理由放行:跟 kill-add 同一寫法、單機 CLI、註解已記為接受的缺口;實作時順手包鎖更好,但 spec 不寫也不會做出錯的行為。

## F3 短身分「前綴對完整雜湊」在專案裡找不到查找先例
severity: minor
blocking: 否
引句:「`lumos guard kill-rm <節點> --id <短身分>`:短身分是 `_kill_recipe_key` 的前 12 個字元」
file: `scripts/lumos:12870`
1. 專案裡雜湊只有「顯示時截斷」的先例(`sha[:12]`、`[:8]`);拿截斷值回頭「前綴比對」的查找只有 git 本身。逃逸撤回、canary 覆核都是整串 token 精確比對。kill-add 自己的身分是 (invariant, file, old) 三元組。
2. 但這裡的「零條或多條就擋下、rc2、不動筆記,多條時列候選」把碰撞風險收乾淨,而且 old 文字可能很長、含多行,貼在可直接複製的修法行裡不實際,所以短身分有正當理由,不判 major。放行理由:不會做出錯的行為;可在 guard-kill 筆記寫一句這是專案第一個「前綴查找」,以後別處要用先照這個。

已讀,無 finding 的節:做法 1、3、5(P2 的 doctor 形狀、`warn_soft`、事件閘名)、條款、回退、實務隱患、誠實界線。

最高等級:major;blocking 共 1 條
