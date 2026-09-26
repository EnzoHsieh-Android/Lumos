severity: major

## F1 鎖逾時的 RuntimeError 沒有出口,會裸拋例外而不是「擋下」
severity: major
blocking: 是(照字面實作,拿不到鎖時使用者看到的是 Python traceback 而不是「擋下:…」,不改決策但破壞 S4 明寫的合約與可執行性)

spec 在「上鎖與寫入」段落主張:

引句:「拿不到鎖時照其他寫入指令一樣印「擋下:…」,不讓例外直接冒出來。」

這句話的前提是「其他寫入指令」已經有這個保護,--withdraw 只要沿用就好。但實際查 `scripts/lumos` 的 dispatch 层,`set`/`append`/`remove`/`new`/`rel-cascade`/`decision-refs`/`decision-reindex` 等寫入指令的 dispatch 呼叫**都個別包了** `try: ... except (ValueError, RuntimeError) as e: print(f"擋下:{e}", ...); return 2`(例如 `scripts/lumos:31739-31748` 的 `set/append/remove`,`31866` 附近的 `decision-reindex`)。

但 `loop escape` 的 dispatch 完全沒有這層:

file: `scripts/lumos:31664-31668`(`if args.lcmd == "escape": return cmd_loop_escape(...)`,前後不在任何 try 區塊裡;往上查到 `main()` 開頭 31550 一路到 31870 這一整段 `if args.cmd == "loop":` 分支,以及整個 `main()` 本身、`if __name__ == "__main__": sys.exit(main())`(`scripts/lumos:31873-31874`),都沒有任何一層 try 包住)

`_vault_write_lock` 逾時是明寫的 `raise RuntimeError("等了 60 秒還輪不到寫入…")`(`scripts/lumos:13791`)。今天 `_auto_escape` 已經在用這把鎖(`scripts/lumos:9342`),同樣會踩到這條路徑——這不是 spec 新引入的行為,而是 spec 把「照其他寫入指令一樣」寫成既有事實,實際上這個既有事實本身就不成立。若 --withdraw 照 spec 字面(「整段包在 `_vault_write_lock` 裡」+ 不額外加 try/except)實作,鎖逾時時會直接讓 RuntimeError 冒出 `main()`、`sys.exit()` 印出完整 traceback,rc 也不會是 spec/S4 要求的可控擋下值,直接違反 S4「拿不到寫入鎖時應印擋下訊息而不是拋出例外」與其對應測試 `t_escape_withdraw_validation`。
實作者要另外在 `cmd_loop_escape` 內部包 try/except 或補 dispatch 層的 try,spec 沒有交代這件事,只是斷言「照其他寫入指令一樣」——這句斷言本身是錯的,若照抄不查會漏掉這個合約。

## F2 「確認目標」步驟要看到撤回紀錄,但指定的讀取原語永遠濾掉撤回紀錄
severity: major
blocking: 是(照字面實作,「目標已經被撤過」「目標本身是撤回紀錄」這兩種擋下情況偵測不到,S4 的驗證會漏)

spec 對撤回要擋下的情況之一:

引句:「目標已經被撤過、目標本身是撤回紀錄(撤回不能再撤;要反悔就重記一列)」

而同一節緊接著定義的讀取原語明講:

引句:「`kind=withdraw` 的撤回紀錄**永遠不當成逃逸列回傳**」

也就是 spec 對「讀的一側」的唯一具名讀取入口 `_escape_rows_for`(不管 `include_withdrawn` 是否為真)結構上**永遠不會**把 `kind=withdraw` 的列吐出來。可是撤回指令要判斷「目標已經被撤過」或「目標本身是撤回紀錄」,恰恰需要讀到撤回紀錄本身(要嘛掃出所有 `target==<token>` 的撤回列、要嘛看 `token==<目標>` 那一列的 `kind` 是不是 `withdraw`)——這兩種資訊都在 `_escape_rows_for` 被明文濾掉的那批列裡。

spec 全文唯一提到「有另一支函式能看穿撤回紀錄」的地方是規則缺口統計那一句:

引句:「讀到的列套同一支「是不是撤回紀錄、是不是被撤回」的判斷函式後再數」

但那句話描述的是規則缺口統計**自己找檔案讀原始列**之後再套判斷函式,不是 `--withdraw` 指令的「確認目標」步驟該怎麼讀。spec 在「上鎖與寫入」段只寫「整段『讀帳確認目標→寫入』包在 `_vault_write_lock` 裡」,沒有指明確認目標這一步要用哪一支讀取函式;若實作者依「讀的一側一律認得撤回紀錄」那一整段的字面(唯一具名的是 `_escape_rows_for`)去讀,「目標已被撤過」與「目標本身是撤回紀錄」這兩條擋下規則會永遠判不出來——因為判斷所需的列從讀取端就被拿掉了。這正落在本鏡頭要驗的「鎖內讀帳確認目標」這一步,照字面走會漏掉 S4 要求的兩種擋下情境,對應測試 `t_escape_withdraw_validation` 會紅。

已看,無:
- 「兩個會談同時撤回同一筆,第二個在鎖裡會看到已撤過而擋下」(實務隱患段)——`_vault_write_lock` 是同筆記庫互斥鎖,`_auto_escape` 已用同一把鎖示範「鎖內讀 existing → 判斷 → append」這個模式(`scripts/lumos:9340-9377`),两次撤回會被同一把鎖序列化,第二個進鎖時第一個已經寫完,不會有 TOCTOU;只是「確認目標」這一步能不能真的看到第一個寫下的撤回紀錄,取決於 F2 指出的讀取原語缺口,鎖本身的互斥語意沒問題。
- 「自動記的去重用 `include_withdrawn=True`」與撤回的鎖是否會死鎖——`_auto_escape` 與撤回都只取同一把 `_vault_write_lock(env.vault)`、不巢狀取第二把不同的鎖,`_VAULT_LOCK_HELD` 只在同一個行程重入時才直接放行(`scripts/lumos:13777-13783`),兩個不同指令各自各拿一次、不互相巢狀,沒有死鎖路徑。
- escape-stats 讀 1.7MB 審查帳 + 13MB 治理帳全程唯讀、不取 `_vault_write_lock`,不會跟撤回/自動記/手動記帳的鎖互相阻塞或造成優先權反轉;spec 自己也寫明它不進任何提交或推送的閘,不在寫入鎖的臨界路徑上。
- 手動記帳(非 `--auto`、非 `--withdraw`)今天確實沒有上鎖(`scripts/lumos:9489-9533` 直接 `_jsonl_append_verified` 而不經 `_vault_write_lock`),spec 只針對撤回明確要求「手動記帳今天沒上鎖,這裡要明確加」——這句話讀起來是專指撤回這個新指令要上鎖,不是要回頭幫既有手動記帳補鎖;沒有發現這句話與程式現況矛盾。
- 讀側遇到寫一半的最後一行:`_escape_rows_for` 逐行 `json.loads` 失敗即 `continue`(`scripts/lumos:7404-7414`),撤回/自動記寫入都是單次 `write()` 一行 JSON 加換行(`_jsonl_append_verified`,`scripts/lumos:8024-8025`),與現有機制一致,沒有新增的半行風險。

最嚴重 severity: major;blocking 共 2 條。
