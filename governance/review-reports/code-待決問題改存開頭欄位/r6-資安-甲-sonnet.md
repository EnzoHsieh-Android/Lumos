severity: minor

我跑了 patch 與工作樹實測(實驗放在 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-資安-甲-sonnet/t.py)。工作樹目前在 2ea5dbff,與 patch 的 5498fec8 可能略有差異,但相關函式文字相同。

severity: minor
blocking: 否
標題:CRLF 計劃檔或行尾帶註解的題號行躲過 `_PQ_CUT_RE`,被切斷的阻塞題對規格閘消失。
攻擊路徑:
- 誰:陌生 repo 的計劃作者,或在 Windows 上編輯而不自知的人。
- 送什麼:CRLF 換行的計劃檔,在 `pending_questions` 清單後面放一個頂格鍵(例如 `reason: x`),再接一行 `  - id: Q2`。
- 拿到什麼:`_pq_scan` 對題目行先做 `rstrip`,但對切斷偵測是用未去尾端的 `fm_lines[k2]` 去比 `_PQ_CUT_RE`。該正規式以 `[ \t]*$` 結尾,不吃尾端的 `\r`,所以整份讀回 `errs=[]`、只有 Q1,Q2 的 `blocking: true` 被丟掉。
- 實測:同樣內容在 LF 檔報「清單範圍外」錯誤,CRLF 檔報 `[]`,`_spec_gate_pending` 因此放行。
- 另兩種也躲過:`  - id: Q2 # c`(行尾註解)和 `  - {id: Q2, blocking: true}`(流式寫法)。
- 這不是作者蓄意躲避才有的洞:CRLF 檔是日常情況。把攻擊者定位為「蓄意藏題」時價值較低,因為他直接不寫那題就好,所以只算縱深防禦缺口。
引句:「if _PQ_CUT_RE.match(fm_lines[k2]):」
佐證 file: `scripts/lumos`(patch 第 205 行:`_pq_scan` 內的切斷偵測;第 74 行:`_PQ_CUT_RE` 定義)

severity: minor
blocking: 否
標題:放行的字元仍構成可藏字的通道,人看不見、AI 讀得到。
攻擊路徑:
- 誰:陌生 repo 的計劃作者。
- 從哪裡:題目的 `text` 欄,內容會被 `lumos pitfalls --stage` 與規格閘印到 AI 的上下文。
- 送什麼:
  - U+200C 與 U+200D 任意長度連續,視為 0/1 位元,U+00AD 當分隔。實測 `a\u200c\u200d\u200d\u200c\u00ad…` 通過 `_pq_bad_char` 與 `_strict_scalar`,patch 只擋異體選擇符連續,沒擋這三個。
  - 異體選擇符每個可見字元後各接一個,16 種選擇符等於每字藏 4 位元,也不被擋。
  - 旗幟形狀可以重複串接:每面旗放 3 到 5 個小寫字母或數字的標籤字,`_PQ_FLAG_TAG_RE` 只限單面,沒限次數。
- 拿到什麼:能讓提示工程類的隱藏指令進入 AI 讀取的終端輸出。
- 這是推論:沒有證據某模型會解碼這些通道,所以不升級。
引句:「_PQ_CF_OK = "\u200c\u200d\u00ad"   # 放行的格式字元:零寬連接字與不連接字(emoji 組合、印度文字)、軟連字號」
佐證 file: `scripts/lumos`(patch 第 78 行:`_PQ_CF_OK`;第 99 行:`_pq_bad_char` 的異體選擇符判斷;第 115 行:`_PQ_FLAG_TAG_RE`)

逐類結論(其餘已看,無):
- 命令、路徑、模板注入:已看,無。
  - `--output=` 類範圍由入口擋掉。
  - 其餘 git 呼叫都帶 `--end-of-options` 或經 `_lens_full_sha` 驗過。
  - 決策連結只拿來查 `env.notes` 的字典與索引,沒有檔案系統遍歷。
- 符號連結檢查:已看,無可利用的繞過。
  - 資料夾連結指到庫外時,`_vault_lock_held_for` 用 `realpath` 比對庫根,會拒寫。
  - 剩下的檢查後換連結的時序競爭需要本機寫入權,不報。
- 權限與守衛繞過:除第一條外已看,無。
- 密鑰與個資、加密與傳輸:已看,無。
- 執行邊界:已看,無。
  - 題目文字經 `_pq_bad_char`,涵蓋 C0、C1、Cf、U+2028 與 U+2029。
  - 檔名經 `_esc_clean`。
  - 題號、鍵名、錯誤中的值都走正規式、`!r` 或 `ascii()`。
- 行動端:不適用。
- 新依賴:無。

總結:共 2 條發現,都是縱深防禦類,沒有可直接利用的洞。最值得先修的是第一條,切斷偵測應改用已去尾端的行,並容許行尾註解。
