severity: major

## F1 --withdraw 沿用的寫入鎖逾時會讓指令裸拋例外,spec 沒交代這條路
severity: major
blocking: 是(照 spec 字面實作,鎖逾時會讓 `loop escape --withdraw` 印出一段 Python traceback 而不是「擋下:」訊息,使用者與腳本都拿不到乾淨的錯誤,自動化呼叫還會被當成未知崩潰處理——這是會做出錯行為的落差)
引句:「寫入包在既有的圖譜寫入鎖裡。」
file: `scripts/lumos:13757-13803`(`_vault_write_lock` 定義:搶不到鎖每 0.05 秒重試,60 秒還搶不到就 `raise RuntimeError("等了 60 秒還輪不到寫入…")`,這個例外會從 `with` 陳述式直接往外拋)
file: `scripts/lumos:9342`(現有 `_auto_escape` 就是用同一把鎖的既有用法,可對照;它的函式說明自稱「不擋、不炸:任何一步失敗只印一行」,但那個保證只涵蓋鎖已經拿到之後、逐筆迴圈裡的失敗——鎖本身逾時拋出的 `RuntimeError` 不在任何 try/except 範圍內,一路往上穿出 `cmd_loop_escape`)
file: `scripts/lumos:31661-31667`(`args.lcmd == "escape"` 的 dispatch 沒有包 try/except;對照 `scripts/lumos:31861-31864` 另一條路徑對 `(ValueError, RuntimeError, OSError)` 有專門的「擋下:{e}」處理,`loop escape` 這條沒有同款保護)
敘述:兩個以上程序同時寫圖譜(例如撤回同時碰上另一支正在 `lumos set`/`append`/自動記逃逸)、其中一個卡住超過 60 秒未釋放鎖時,第二個呼叫 `--withdraw` 的程序會整段崩潰退出,不是 spec 承諾的乾淨失敗。spec 第三節只寫「包在既有的圖譜寫入鎖裡」,沒有交代逾時要怎麼收尾;若實作者依樣照抄 `_auto_escape` 的 `with _vault_write_lock(...):` 寫法,就會把這個既有落差原封不動複製到一個新的、人工互動的指令上。建議在 spec 補一句:`--withdraw` 要包 `except RuntimeError` 印「擋下:」並回非 0,而不是讓例外裸露。

## F2 rule-gap 沒有 env,spec「改成呼叫 _escape_rows_for」這句字面上做不到
severity: major
blocking: 是(照 spec 字面實作,實作者會在 `cmd_rule_gap` 裡呼叫 `_escape_rows_for(env)`,但那個函式作用域裡根本沒有 `env` 這個名字——不是要多包一行,而是要嘛回頭建一個 vault/Env、要嘛改 `_escape_rows_for` 的介面,兩者 spec 都沒交代,且前者會讓 rule-gap 在 standalone 佈局下的既有支援退化)
引句:「規則缺口統計(`rule-gap`)自己開檔讀,要改成呼叫它」
file: `scripts/lumos:20215`(`def cmd_rule_gap(repo=None, as_json=False):`——簽名裡沒有 `env` 參數)
file: `scripts/lumos:31400-31401`(`if args.cmd == "rule-gap": return cmd_rule_gap(repo=args.rg_repo, as_json=args.rg_json)`,這段在 `main()` 裡排在 `env = Env(vault)` 之前——`env = Env(vault)` 在 `scripts/lumos:31526-31530`——`rule-gap` 分支執行時那個名字還沒被賦值)
file: `scripts/lumos:20224-20227`(rule-gap 自己的註解:「逃逸帳位置:記帳那支寫在「知識庫的上一層」…但知識庫本身就是 repo 根的那種佈局(standalone)會落在別的地方——兩個都找」,兩個候選路徑是 `repo_root/docs/.escape-log.jsonl` 與 `repo_root/.escape-log.jsonl`,不是 `env.vault.parent`)
file: `scripts/lumos:7397-7401`(`_escape_rows_for(env, loop_id=None)` 內部用 `env.vault.parent / ".escape-log.jsonl"`——單一路徑,沒有 standalone 佈局的雙候選邏輯)
敘述:`lumos rule-gap --repo <standalone 佈局的 repo>` 現在能在沒有 `docs/<slug>-knowledge/` 這種常規 vault 佈局時正常運作(靠 `_anchor_repo_root` 找 git 根,不靠 `find_vault`)。若照 spec 字面把 `_escape_rows_for` 塞進 `cmd_rule_gap`,要嘛在函式裡另外呼叫 `find_vault`+`Env(vault)`——在 standalone 佈局極可能找不到 vault(`find_vault` 認的是 `docs/*-knowledge` 或明確的 MOC/Systems 結構,不是任意 repo 根),導致 rule-gap 在它原本設計要撐住的那個佈局上失敗;要嘛悄悄改 `_escape_rows_for` 簽名改吃路徑,那樣會動到 `scripts/lumos:2301`、`6303`、`7082`、`9344`、`18551` 五個既有呼叫點,spec 完全沒提這層改動範圍。

已看,無:三、撤回一節本身(追加寫、不改舊列、理由留帳)在資料模型層面沒有問題——append-only 的設計天然避開「兩個會談同時撤回同一筆」的資料損壞疑慮,即使兩個程序都寫出一筆撤回紀錄,讀側只要用「該 token 是否出現過撤回紀錄」這種集合式判斷去濾,重複紀錄不會讓某一列被算兩次或算錯方向,只是帳面上會多一筆看起來多餘但無害的撤回紀錄(spec 沒禁止,也沒必要禁止)。讀的一側容忍「撤回紀錄寫一半」的疑慮也已經有既有機制接住:`_escape_rows_for`(`scripts/lumos:7397-7415`)逐行 `json.loads`,壞行(含被截斷的最後一行)直接 `except ValueError: continue` 跳過,方向是保守的(讀不到撤回紀錄時,原列還是可見,不會誤判成已撤回而漏算)——這與 spec「讀的一側遇到寫一半的最後一行略過」的敘述一致,machine 驗證後成立。鎖檔位置不可信時的退路完全繼承既有 `_vault_lock_where`(`scripts/lumos:13713-13740`)機制,因為 spec 沒有替 `--withdraw` 另開一套鎖,而是重用 `_vault_write_lock`,所以「不可信就換位置到 vault 自己裡面、只警告一次」的規矩自動適用,不需要 spec 額外交代。escape-stats 讀治理帳(13MB/85270 行)的耗時與記憶體實測:`docs/.governance-log.jsonl` 全檔逐行 `json.loads` 約 0.2 秒、85270 筆 dict 常駐記憶體(規模遠低於會造成問題的量級),且 `cmd_gov`(`scripts/lumos:6871-6904`)現在就是用一模一樣的「整檔讀進記憶體」寫法讀同一份治理帳,escape-stats 只是多一支同形狀的唯讀彙整指令,沒有引入新的效能風險,與 spec「是手動或週報才跑的唯讀指令」的定位相符。金流/對外送出/不可逆三類 spec 已自列「已排除」且與程式碼現況相符(本案全程只讀寫本機 jsonl 帳本、不呼叫外部服務、append-only)。

最嚴重 severity: major;blocking 共 2 條。
