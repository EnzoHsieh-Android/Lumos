severity: minor

## 發現

### S1 doctor 新增的 S17/S18/S19 把筆記裡的字原樣印到終端,沒清控制字元
severity: minor
blocking: 否 — 只能讓終端畫面被竄改或偽造輸出,不能執行程式碼、取得資料或繞過任何權限;舊有的 S16 也是這樣印,屬縱深防禦。
引句:「out.append(f"{rel}:{no}:{pf} 上次確認 {conf.isoformat()},超過 {days} 天:{sp['core'][:40]}")」

- 誰:一個陌生 repo 的作者,或在合併分支裡夾帶筆記的人。
- 從哪裡:筆記摘要裡的 `FACT:`、`RULE:` 句子本文,以及 `[被取代:…]`、`[recheck:…]` 欄位的值。
- 送什麼:在句子裡放 ESC(`\x1b`)開頭的終端控制序列,例如 `\x1b[2J`(清畫面)、`\x1b]0;…\x07`(改視窗標題)、`\x1b[31m`(改顏色)。
- 拿到什麼:受害者在這個 repo 跑 `lumos doctor` 時,這些序列會直接進終端。攻擊者可以清掉前面的警告、偽造「全部通過」的畫面,或改視窗標題。
- 實測:我 clone 本審查工作樹的 `2f9cb94f`,在暫存目錄建一篇 `FACT:y\x1b[31mred [confirmed:2020-01-01] [來源:生產]` 的筆記。`lumos doctor` 的 S19 段用 `cat -v` 看到 `y^[[31mred`,ESC 原樣輸出。
- 對照:同一份 diff 裡 drift 那條路都有過 `_esc_clean`(`file: scripts/lumos:10423`),所以這是 doctor 這三段漏掉的同族缺口。`warn_soft` 本身不清字元(`file: scripts/lumos:1354`)。
- 成因:`slot_parse` 的 `core` 只用 `split()` 壓空白,不會去掉 ESC(0x1b)。
- 建議:在 `_doctor_replacement_lines`、`_doctor_metric_lines`、`_doctor_fact_recheck_lines` 組句子時,把 `rel`、`v[:40]`、`rc[:20]`、`sp['core'][:40]` 都過 `_esc_clean`。

## 逐類結論

1. 不可信輸入流到危險操作:除 S1 外已看,無。
   - `[被取代:]` 的值只用來查 `env.resolve` 和 `_node_decisions` 這些已載入的筆記表,沒有組成檔案路徑去讀檔,沒有路徑穿越。
   - 度量式撤除條件的閘名被 `[A-Za-z0-9_-]+` 的正規表示式限制住,只用在字串比對和一組固定的 `_metric_gate_off` 分支,不流進 git 或 shell。
   - `[recheck:]` 被 `fullmatch` 限成數字加單位,`int()` 之前已驗證。
   - 治理帳走 `_drift_jsonl_parse` 的 JSON 解析,`fromisoformat` 失敗會略過,沒有 eval 或反序列化物件。
   - `when-file` 的路徑評估沿用既有的 `_drift_probe_line`,這份 diff 只是多傳 `kind="retire"`。
   - 推送時撤除條件那支的輸出都過 `_esc_clean`(限 300 字),`drift ack` 的新擋下訊息只印 `rel` 和行號。
2. 登入與權限:已看,無。這支 CLI 沒有登入或 session,也沒有放寬授權範圍。
3. 密鑰與個資:已看,無。沒有寫死的密鑰,錯誤訊息只印例外的型別名稱(`type(ex).__name__`),沒印內容。
4. 加密與傳輸:已看,無。沒有加密、網路或隨機數的新用法;`drift ack` 的 token 沿用 `secrets.token_hex`。
5. 執行邊界:已看,無新增。
   - 新增的讀檔只有治理帳檔尾(24MB 上限)和 `.lumos/config.json`,結果只用來判斷閘開或關,不會輸出內容。即使其中一個是指到 repo 外的符號連結,也不會洩漏內容。
   - 沒有新增 hook、安裝腳本或 shell 插值,也沒有寫使用者全域設定。
   - `_lint_new_config` 讀設定檔時會跟著符號連結走(`file: scripts/lumos:24441`),這是既有行為,不是這份 diff 引入的。
6. 行動端:已看,無(不適用)。

新增依賴:無。這份 diff 只用標準函式庫(`datetime`、`re`)。

最高嚴重度 minor,blocking 0 條
