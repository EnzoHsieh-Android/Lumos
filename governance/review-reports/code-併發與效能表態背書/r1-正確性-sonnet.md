severity: minor

逐 hunk 走過執行路徑,沒找到 blocker 或 major。派工尾端沒有附固定席圖譜筆記,沒有逐條答圖譜鏡頭。

已驗過判為正確:detail=False 各分支 ok 與舊版一致、呼叫端(`scripts/lumos:37427`、`scripts/lumos:37764`)只解兩個值;舊 kill-log 沒有 head_sha/recipe_id 被略過;殘行補換行與位元組切行逐行容錯;cmd_gov 拿掉 import json 後函式內無 json. 用法、模組層有 import(`scripts/lumos:32151`);kill-add 判重等價舊三欄比對;只更新 covers 只改同 key 那條;recipe_id 三處一致、marks 區間切分正確;舊版本上的 survived 會因筆記不是簿記檔而失效;max(key=ts) 只用來顯示。

**K1**
severity: minor
blocking: 否。只改了一句說明文字,ok 沒變。
`_codeloop_record_valid` 預設路徑:merge-base 通過但 git diff 非 0 時,舊版回「之後動了代碼」,現在回「git diff 出錯」;docstring 說預設行為不變,文字其實變了;`_dispositions_verdict` 接成「表態記錄過期…改了碼要重表態」會誤導。讀碼推論,沒造出 git diff 失敗。
引句:「return False, f"git diff 出錯(rc={df.returncode}),判不了 {rec_sha[:8]} 之後動了什麼", True」
file: `scripts/lumos:37310`

**K2**
severity: minor
blocking: 否。需要手改或別版本寫的殘缺行才觸發,後果是所有題退成 none。
`_backing_judge_groups` 直接取 r["weak"],`_backing_kill_rows` 只驗五欄;一行帶 head_sha、recipe_id 但沒有 weak 的紀錄會 KeyError('weak')(已直接呼叫重現),被外層 except 接住,整批被標且 satisfied 的題記 none「讀取失敗:KeyError」。
引句:「if not any(r["verdict"] == "killed" and r["weak"] is not True for r in g):」
file: `scripts/lumos:37951`

**K3**
severity: minor
blocking: 否。需要淺 clone 加特定 kill-log 內容,且只影響只提醒的功能。
merge-base rc 非 0/1(物件找不到)時 detail 回 False 而非判不了;淺 clone 缺祖先 sha、那個 sha 上有 survived,會被當無效丟掉,HEAD 上還有 strong killed 就判 strong,與「判不了的紀錄不能丟」矛盾。讀碼推論,沒在淺 clone 實跑。
引句:「判不了是不是祖先——先確認那個提交還在,不在就照重來的步驟重記"), False」
file: `scripts/lumos:37295`

總結:max severity = minor;blocking 條數 = 0。
