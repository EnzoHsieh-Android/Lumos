# code-角色鏡頭 r1 收貨紀錄

三席:正確性-sonnet(standard 單席)、架構對齊-sonnet、外家-codex(gpt-5.6-sol、xhigh,照範本 §3 ④ 帶 -m)。
三份引句全錨、refcheck 無缺檔。正確性席最後一行總結含「severity:」字樣被格式檢查當成孤行,已退回原席改寫(只改那一行)。

## 去重後的發現與去向

| id | 來源 | 嚴重 | 內容 | 去向 |
|---|---|---|---|---|
| a1 | 正確性 F1、外家 F1 | major | 壞宣告警告回填專案寫的 role/path 值,角色段在框外=能往指令區塞字 | 折:警告只寫第幾條與固定原因;測試 t_review_role_warning_never_echoes_config_values |
| a2 | 正確性 F2、外家 F3 | major | 期限短時角色預算 0.6 秒,消費專案前置 git 工作就耗光,手機檔與 .ts 拿不到卡且完全靜默 | 折:預算改 _role_budget(至少 1 秒、平常取期限三分之一、最多 3 秒);超時且全判不出時角色段印一句;測試 t_review_role_timeout_is_not_silent_and_budget_floor。殘餘:單一 git 呼叫本身仍可能超過預算(沿用 _lens_git 的 20 秒上限),預算只在步驟之間檢查 |
| a3 | 外家 F2、正確性 F4 | major | 新掛鉤配舊 lumos:舊版不認 --role-cards 回 rc2,連圖譜段都丟 | 折:掛鉤看到 rc2 且沒輸出、而且帶了旗標,就拿掉旗標重叫一次;測試 t_dispatch_lens_hook_retries_without_role_flag_on_old_lumos |
| a4 | 外家 F4 | major | 300 上限數的是讀取候選(含缺檔的 package.json 候選),提早截斷、誤判後端 | 折:上限改數檔;測試 t_review_role_cap_counts_files_not_candidates |
| a5 | 外家 F5、正確性 F5 | major | 一支檔名含換行的檔讓整批讀取作廢,且誤標超時 | 折:含換行的檔不進讀取清單,只它判不出;測試 t_review_role_newline_path_does_not_poison_batch |
| a6 | 外家 F6 | major | 沒有大小上限,整支大檔讀進記憶體 | 折:先用 ls-tree -l 問大小,超過 _ROLE_MAX_BYTES 不讀;讀到的也只解碼開頭這麼多;測試 t_review_role_skips_huge_blobs |
| a7 | 架構對齊 F1 | major | 讀起點設定另寫 show+json 解析,專案已有 _json_at_ref | 折:改用 _json_at_ref;讀不懂的判法=_json_at_ref 回空但 cat-file -e 說檔在(同 _path_at_pin 的寫法) |
| a8 | 正確性 F3 | minor | 角色計算出錯(例如超深巢狀 package.json 的 RecursionError)拖垮整個派工附段與推送前分級 | 折:解析多接 RecursionError;兩處呼叫點寬接、出錯當沒有角色;測試 t_review_role_errors_never_break_dispatch_or_pitfalls |
| a9 | 架構對齊 F2 | minor | _node_flavor 多一條找 package.json 的路 | 折:工作樹也走同一條往上找的路(_node_flavor_at),只換讀取來源 |
| a10 | 架構對齊 F3 | minor | 設定警告的前綴與通道跟棧別題組設定不同 | 折:推送前分級改印「提醒:…」到錯誤輸出,照棧別題組設定警告的印法 |
| a11 | 架構對齊 F4 ⚠ | minor | 又手寫一份 git diff --name-status -z 解析 | 放行:鄰居本來就各自手寫多份、專案沒有統一的解析可沿用;抽共用超出本案 |

refuted-set:none(三席的現象都自己核對過:a1/a2/a5 看過席位附的重現指令與輸出,a3 在測試裡用假子行程重現,a4/a6 以單元測試重現)。
