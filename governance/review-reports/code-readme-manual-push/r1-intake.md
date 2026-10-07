# 編排者重現與處置

被審版本：7506c90bc6923c688d2fee798d9c418b3f6ec24b；主線起點：9385ff960b8f52627a539613ecc11616b1bb4c22。原報告與辯方均逐字保存，不將 reported 改成零或改寫原 severity。

| ID | 重現 | 證據與處置 |
|---|---|---|
| F1 | MISS | 原報告的否定 rg 指令實際 rc0，未翻紅；scripts/lumos 相對主線沒有差異；主線 code-loop skill 已明示 rc0 不等於綠。本次手冊改為符合 cmd_ci_wait 的 JSON verdict 契約，沒有引入兩套判定。獨立辯方核對六種回傳，駁回本次阻擋项。 |

新手冊引句及舊 help 簡寫的存在均能重現，但這不等於「本次文件引入錯誤判定」。對 scripts/lumos 的 `git diff --exit-code origin/main...HEAD -- scripts/lumos` 為 rc0。原重現 `! python3 scripts/lumos ci-wait --help | rg -q '綠 rc0/紅 rc1'` 為 rc0，原因是 subcommand help 顯示空格版，斜線版屬頂層摘要。編排者讀過 cmd_ci_wait 的 emit 與各 return 分支；未把 rc0 判綠。

舊 CLI help 縮寫的誤讀風險保留在辯方原報告，尚未修復；本次不改 CLI、不宣稱風險已解決。後續若要改 help，以辯方附的正向 rg 為最小翻紅入口，走獨立程式變更與測試。此輪沒有程式修補，也沒有上一輪修補因果需判定。

審查界線：一席全新架構對齊，單家族視角；凍結材料涵蓋功能文件，歷史 preflight/測試輸出為附件而非先前結論。圖譜鏡頭固定席 0，採手動補送結果；未宣稱本環境 hook 自動注入成功。引句、引用与材料覆蓋檢查通過。
