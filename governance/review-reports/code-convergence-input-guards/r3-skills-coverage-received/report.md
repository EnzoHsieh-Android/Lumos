severity: major

僅判定凍結的歷史材料；不代表目前 HEAD、整個程式庫或圖譜的安全狀態。

### skills-coverage-資安-F1

severity: major  
blocking: yes

引句:「--decision extra-round|accept-risk --note」

- 誰：能控制受審 diff、報告或回顧文字的惡意提交者。
- 入口：agent 依 skill 組合 `cap-decision` 或 `--skip --note` shell 指令。
- 輸入：理由中夾入 `$()`、反引號或破壞引號邊界的 shell 字元。
- 收益：以審查 agent 的權限執行任意命令，進而竊取憑證、竄改 repo 或治理紀錄。

新增流程把自由文字直接示範成雙引號內的 shell 參數，沒有要求 argv-safe 呼叫、stdin／檔案輸入或拒絕逐字搬運受審內容。這形成明確的命令注入面。

建議改為 CLI 提供 `--note-file`／`--note-stdin`，或規定使用不經 shell 插值的 argv 呼叫；skill 同時應明說受審材料只能當資料，不得直接拼進命令。

### skills-coverage-資安-F2

severity: major  
blocking: yes

引句:「人裁結果先記 `cap-decision`,繼續之前先寫跑滿回顧」

- 誰：能在受審材料中偽造核可敘述的提交者，或已被提示注入影響的 agent。
- 入口：`cap-decision --decision extra-round|accept-risk`、回顧 `--record`、以及 `--skip`。
- 輸入：偽造的「人已核可」敘述、自填的核可理由或 `completed_by` 等回顧欄位。
- 收益：把未經真人核可的接受風險、加開輪次或跳過回顧寫成受信任治理證據，使 `canary record`／處置閘後續放行。

文字要求「人裁」，但本材沒有把決策綁到可驗證的核可者、核可來源或不可由 agent 自填的證據；`completed_by` 也是文字欄位。這使不受信任的審材內容與治理閘信任的紀錄之間缺少權限邊界。

建議讓 CLI 與閘共同驗證核可主體、核可來源、loop ID、決策及時間；agent 必須從當前真人訊息取得明確核可，受審 diff／報告中的任何核可宣稱一律無效。`--skip` 應採同一套限制。

### 指定安全面覆蓋

- 注入／反序列化：發現 F1；本材未新增可判定的反序列化格式或解析器。
- 權限：發現 F2。
- 秘密：未出現硬編碼秘密；但 F1 成功後可讀取 agent 環境中的憑證。
- 加密傳輸：本材沒有網路傳輸變更，無可判定項目。
- hook／CI：沒有修改 hook 或 CI 實作；但新增紀錄會被治理閘信任，因此 F2 直接跨越其證據邊界。
- 行動端：沒有行動端介面。
- 依賴：沒有新增或升級依賴。
- DoS：依要求不報。

### 輪次與信任邊界

- 預設數字上限沒有改：code-loop high 仍為 3；design-loop light 為 2、standard/high 為 3，舊制仍為 6。
- 實際續跑能力有改：新增到頂後以 `extra-round` 加開輪次的路徑。
- 審查／跳過核可有改：新增 `accept-risk` 與回顧 `--skip`。
- 證據信任邊界有改：真人裁決、乾淨代理草稿、編排者填寫的回顧，以及 `--check`／`--record` 產物，會成為治理閘採信的輸入。

### 範圍與實讀紀錄

- HEAD 已核對：`fbb758f593fe03b357daec93f7f702361a3b4adb`。
- 完整實讀：snapshot 39/39 行、binding 19/19 行、`CLAUDE.md` 101/101 行、`lumos-project-notes` skill 94/94 行。
- snapshot SHA-256 與 binding 完全相符：`bd77d74d858b04f59dfcd2a64f13bdea1292bf70990d7d59dab27e64491eda10`。
- binding 將三個 hunk 都歸屬到歷史來源 `r3-segments/repair-6.patch`；未把它們稱為 HEAD 當前改動。
- 未讀：其他席報告、原始 `repair-6.patch`、三份 skill 在 HEAD 的完整現行版本、其餘程式碼／圖譜／測試與 CI 實作。
- 未執行審材中的任何命令，未修改 repo 或報告。