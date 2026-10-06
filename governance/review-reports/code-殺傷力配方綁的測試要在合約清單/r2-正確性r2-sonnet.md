severity: minor

## F1 合約片段以減號開頭時,貼出的 guard bind 指令會被當成選項
severity: minor
blocking: 否 — 只是照貼會失敗(argparse 報錯),不會執行任何東西;合約片段以 - 開頭很少見
引句:「fix = (f"要讓推送閘也守它:lumos guard bind {na} {inv} {meth}{f' --platform {plat}' if plat else ''}"」
file: `scripts/lumos:15071`
重現:in-process 載入 scripts/lumos,對 recipe {"invariant":"-x","test":"Foo"}、合約行 "KEY:★INVARIANT★ -x [test:Bar]" 跑 _kill_binding_msg,輸出 `lumos guard bind Systems/L -x Foo`。shlex.quote 對 -x 不加引號,貼進去 -x 會被當選項。平台名同理(`--platform -x`)。_kill_cmd_arg 只擋 shell 斷字與控制字元,擋不住選項注入。要不要處理看需求(可在 bind 指令加 -- 或對開頭是 - 的字改印佔位),不擋。
未能重現成安全問題:這只會讓指令報錯,不會多執行東西。

## 已讀無 finding 的逐項(含修正)
- _kill_cmd_arg 回 None 的每個分支:platform 分支(want 不安全)文字通順,講「kill-rm 後改用合約綁的平台重新 kill-add(…不印可貼的指令)」;unbound 分支 inv 或 plat 為 None 時改講手動 guard bind,方法名非識別字優先走「綁不了」。皆已用 in-process 實跑與測試 ⑭⑮ 確認,沒有任何分支把未過濾的字貼進指令。
- 其他進指令的字:節點名走 _kill_node_arg(控制字元印佔位)、方法名只在 IDENT_RE 過才貼(_kill_norm_method 已去前後空白,IDENT_RE 的 $ 容許尾端換行在此到不了)、id 是 hex。清單上的測試名、合約前 30 字、平台名顯示處都過 _kill_show 或 _kill_esc,含替身字元(Cs 在 _PATH_SPECIAL_CATS 內,不會讓 print 丟 UnicodeEncodeError)。
- guard audit 改用 _kill_find_contract:多筆回 many→同一句擋下 rc2、零筆→同一句 rc2,邏輯與原迴圈逐行等價;kill-add 同理。
- warn_box 形狀改為 (配方, 合約行):只有 _kill_add_after_lock 一個讀者(grep 確認),_kill_add_try 取 warn_box[0][0] 正確;只更新 covers 路徑 recipe 是既有 dict、test 非字串時 skip 不崩。
- _kill_check_ctx 提到鎖外並包 try:丟例外時 ctx=None,_kill_add_warn 內自己再建一次、仍在它的 try 內只印一行;binding 在 pdata=None 時 skip,不會多印。無寫入後丟例外的路徑。
- doctor:_p2 為 None(掃描崩潰)或無配方(ctx None)或設定壞(pdata None)皆回 []; 一篇內逐條 try;load_raw_for_edit 與 _kill_read_recipes 重複讀,僅效能小成本、無一致性問題。check-p2t 已加進 _GOV_LOCAL_PAIRS 與 _KNOWN_GATES 各一次。
- 單平台含冒號、反引號、前綴後空白、平台不同、未定義前綴,以 in-process 與 t_kill_add_warns_test_not_bound 走過,行為符合筆記。
- 測試:python3.14 scripts/test_lumos.py -k kill 431 passed 0 failed。新測試格不是空殼:① 與 ② 互為對照(在清單/不在清單),⑨ 檢查兩行順序,⑭⑮ 直接檢驗指令內容;t_doctor_kill_test_not_bound 的 ②(Systems/Bound 不在輸出)單看可能空過,但 ① 證明該提醒會印、⑩ 證明會消失,不影響。既有 ⑨a 測試改合約為 [test:b:TestLimitFive] 是為了不讓新提醒混入,合理。
- 圖譜鏡頭:固定席節點 guard-kill 的兩條 INVARIANT(rc 優先序、--json 純淨)——本次不動 cmd_guard_kill 的判定與 stdout,kill-add 只多 stderr,不影響;lumos-cli-read(search 濾網)、lumos-cli-lifecycle(re-inject)、測試假綠形態、design-loop 皆不碰其程式路徑,不影響。kill 測試 431 綠。
- 角色鏡頭卡:未附,略過。

總結:max severity minor;blocking 0 條。
