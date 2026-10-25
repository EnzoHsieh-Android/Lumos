# code-android-e2e-batch1 r1 收貨

- 分級 standard:單審一席(正確性,附角色鏡頭)+ 架構對齊一席。報告從完整逐字稿存檔,兩份都已是正規化格式、引句對凍結 patch 全錨。
- 編號:s 單審、a 架構對齊,後接各席報告裡的條號。
- 修正提交:73f36793(修正前 533a083e)。

## 編排者重現表

| id | 宣稱 | 重現 | 結果 | 處置 |
|---|---|---|---|---|
| s1 | 中斷時直接 SIGKILL 整組,子程序與收集腳本、toolkit 的收尾不會跑 | 先補測試:假 maestro 接 TERM 寫收尾標記,對範本腳本送 TERM;修前標記沒出現(紅) | HIT | 折(先 TERM、等 LUMOS_E2E_STOP_GRACE 秒再 KILL;改壞驗證改回直接 KILL 會紅) |
| s2 | 關掉終端時錯誤輸出寫不出去,中斷路徑丟例外、沒存 steps.json 也沒呼叫 judge | 先補測試:關掉腳本的錯誤輸出管線再送 HUP;修前 steps.json 的 interrupted 是 false、沒有這次的紀錄(紅) | HIT | 折(收尾與擋下訊息一律走印不出也不丟例外的 say) |
| s3 | 同一個 check 另有別的情境或裝置的門檻條目時,記憶體塊永遠沒判完 | 先補判定情境:本情境全過、另兩條是別的情境與別的裝置;修前判 unjudged(紅) | HIT | 折(lumos macrobench --stability 對不適用的跳過條目標 applies=false,判定不算它們;另補直接呼叫判定函式的測試守這一欄) |
| s4 | 範本只在回傳碼非 0 時重跑,跟計劃「沒過再跑一次」不一致 | 讀計劃〈一次驗收跑什麼〉UI 那一列與範本的重跑條件 | HIT | 折(計劃改寫成回傳碼不是 0 才重跑,並寫明回傳碼 0 但報告零案例或有失敗重跑也一樣,直接算沒過) |
| a1 | 新寫一支 git 呼叫包裝,既有有 _nodehome_git | 讀 `_nodehome_git`:位元組輸出、失敗回 None,語意相同 | HIT | 折(拿掉 _e2e_git,三處改用 _nodehome_git) |
| a2 | JSON 讀檔沒有既有的限深與孤立代理字元清洗 | 先補判定情境:判定輸出帶孤立代理字元;修前寫紀錄時 UnicodeEncodeError 整支崩(紅) | HIT | 折(照 _macrobench_stab_load 限深並清洗) |
| a3 | 時間格式函式跟第 40664 行的既有函式重複 | 讀第 40664 行:那就是這份 diff 新寫的 _e2e_now 本身,專案裡沒有另一支同功能的函式(其他地方是行內寫) | MISS | 駁回(席位把這份 diff 自己的函式當成既有函式) |
| a4 | JUnit 用 ElementTree 自己讀,沒走既有包法 | 讀 `_secev_junit_facts`:安全證據閘用 test_quality.junit()(拒收 DTD、案例數要對得上);先補帶 DTD、案例數對不上兩個情境,修前都判通過(紅);另拿平板實跑的兩份 Maestro 報告驗既有讀法讀得懂 | HIT | 折(改用 test_quality.junit()) |
| a5 | 裝置鎖依程序編號接手,跟本體鎖不自動接手的做法相反 | 讀 `_excl_lock_try` 說明:ABA 雙持所以不接手 | HIT | 折(家節點寫 WHY:範本是獨立 Python、無人看顧時不接手會卡死;雙持風險照威脅模型不另外防) |
| a6 | 測試沒隔開使用者的全域 git 設定 | 讀 _ms_collect_env 的註解:全域 gitignore 讓產物檢查誤紅 | HIT | 折(e2e 測試的 git 與子程序都帶 GIT_CONFIG_GLOBAL=/dev/null、GIT_CONFIG_NOSYSTEM) |
| a7 | 從提交樹讀設定用 utf-8-sig,跟 _macrobench_config 的 utf-8 不同 | 讀兩處讀法 | HIT | 折(改成 utf-8,同一個檔兩條讀法容忍度一樣) |
| a8 | 建了 e2ecmd 子命令卻不看它分派 | 讀分派那一行 | HIT | 折(照 e2ecmd == "judge" 分派) |

修補對照:修正提交 73f36793 的差異就是修改前→後;每組的先紅測試與改壞驗證結果寫在 r1-fix.json。
