severity: minor

**發現 1:題號欄位沒過 `_pq_bad_char`,控制字元(ESC 等)會經錯誤訊息印到終端(縮排欄位標了「讀寫兩端共用」,這個欄位漏了)**
severity: minor
blocking: 否
引句:「errs.append((ln, f"{qid} 缺必有的鍵 {k}"))」
佐證 file: `scripts/lumos`(patch 的 `pq_parse` 內,約 patch 第 211–213 行;`_pq_scan` 組項目的第 167 行,以及第 172 行 `cur['id'][0]` 重複鍵訊息)
- 攻擊路徑:攻擊者是陌生 repo 的作者,他在計劃筆記開頭欄位寫 `  - id: Q1<ESC>[2J...` 這類題號,例如整題只有 id 沒別的鍵。受害者在該 repo 跑 `lumos lint <計劃>`。
- 成因:`_pq_scan` 把 id 值 `.strip()` 後就收下,沒檢查控制字元。`_strict_scalar` 只管其他鍵的值,不管 id。`pq_parse` 發現題號格式不對時,「題號 …」那條用 `!r`,是安全的。但同一函式後面的「缺必有的鍵」和「寫了兩次」等訊息,把未驗證的 `qid` 原樣放進 f-string。
- 結果:lint 會逐條印出 `errs`,ESC 或 C1 控制序列就到了終端。攻擊者能改畫面、改視窗標題、偽造「通過」的輸出行,或蓋掉前面的錯誤行。
- 規模:效果只在顯示層,沒有程式執行,所以標縱深防禦。
- 修法:id 也過 `_pq_bad_char`,有壞字元就把 id 換成 `!r` 或固定字樣再放進訊息;或讓所有進訊息的 `qid` 都走 `repr`。

**已看,無的類別**

1. 不可信輸入流到危險操作
   - `cat-file --batch` 的 stdin:
     - 路徑來自 `touched`,由 `splitlines()` 切開,所以每個路徑裡不會再有 `\n`。git 預設會把含換行或控制字元的檔名加引號,加引號的名字不以 `vrel/` 開頭,會被 `startswith` 濾掉。含 U+2028 或 `\x85` 的檔名會被 `splitlines` 切碎,碎片最多對應到不存在的物件,結果是 `missing`,不會錯位。
     - 版本字串來自 `re.fullmatch(r"(.+?)(\.\.\.?)(.*)")`,`.` 不吃 `\n`,所以含換行的範圍字串整個不匹配。三點範圍的 base 換成 `merge-base` 輸出的 sha。因此 batch 沒有注入換行的入口。
   - batch 回應的解析:位置完全由 git 回報的 size 推進,`missing` 和 `ambiguous` 都各佔一行。
   - 決策連結:`_pq_decision_state` 的 `../` 和絕對路徑只做 `(lit + ".md") in env.notes` 的字典成員比對。`self_fm` 分支重讀磁碟,但 `node` 只可能是 `env.notes` 的成員或 `rel` 本身。只回 ok/missing/superseded,沒有內容外洩,也沒有跳出圖譜。
   - 符號連結:vault 內若有指向外面的 `.md` 符號連結,是 `env.notes` 建立時就有的舊行為,不是這次 diff 新增的。重讀只回布林,外洩不了。
   - `merge-base` 參數:`base` 是 `(.+?)` 起頭,理論上能以 `-` 開頭,變成給 `git merge-base` 的選項。`merge-base` 沒有寫檔或執行類選項,範圍字串又來自 pre-push 的 sha 或 CLI 參數,不是 repo 內容。推論,無實際攻擊面,不另列發現。縱深防禦可以在 `base`、`head` 前加 `--`,或用 `git merge-base -- <a> <b>`。
   - 寫入端:`question-add` 和 `question-set` 的值都先過 `_pq_bad_char`(擋 Cc/Zl/Zp)再進 `_yaml_plain_ok` 或 `_yaml_quote`,換行無法夾帶額外的 YAML 鍵。`_PQ_SUB_RE` 擋了底線開頭的鍵。
2. 權限與守衛繞過:惡意計劃讀不懂時,規格閘回 1 擋下,推送前只提醒、不放行。我沒找到讓閘「放行」的路徑。被刪的計劃用 `continue` 略過,屬刻意設計。
3. 密鑰與個資:`pending_questions` 的欄位文字會印到終端,但不進帳檔或 log,patch 裡沒有新增寫檔路徑。
4. 加密與傳輸:不適用。
5. 執行邊界:新的 subprocess 都是 list 形式(沒有 `shell=True`),`git -C <repo root>` 加逾時,沒有新的全域設定或 hook 變動。`_decision_cmd_locked` 只是把鎖包起來,沒有新權限。
6. 行動端:不適用。
7. 新依賴:無。

總結:`cat-file --batch` 的 stdin、決策連結重讀、`merge-base` 都沒有可利用的洞,只有題號欄位漏了控制字元檢查這一條縱深防禦類發現(minor、不阻擋)。
