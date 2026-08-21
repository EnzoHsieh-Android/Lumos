本席為外部否決席（第一席），針對 v3 規範進行前提層審查。本輪發現 1 項 Blocker 與 4 項 Major 缺陷。

### Finding 1: [Blocker] 棘輪機制在「局部掃描」情況下會靜默重置，導致硬擋失效
**說明**：S2 定義「最新 run 不出現 → 不升」。然而 `doctor` 常見用法包含指定節點掃描（如 `doctor --node <file>`）。若某次 commit 僅觸發了 `check-a`（符合 run 定義）但掃描範圍未涵蓋帶有 `check-s` 存量警告的節點，則該次 run 的事件簿將不含該鍵，導致連續 20 次的計數器被靜默重置。這使得開發者可透過「交替提交局部修改」來永久規避棘輪升級，違背「硬擋」初衷。
引句：「最新 run 不出現 → 不升(剛清的不升)。」
**Severity**：Blocker

### Finding 2: [Major] 承認句標記與 YAML Frontmatter 語法衝突
**說明**：S1 要求在 frontmatter（含 summary 等欄位）中出現詞表時必須補標記。然而 frontmatter 本質為 YAML 格式，若直接插入 `<!--lumos:risk=...-->` 標記，將破壞 YAML 解析器的正確性（除非該欄位被視為純文字塊且標記被包含在引號內，但規範未強制要求欄位值的引用格式）。這會導致「為了通過 lint 檢核而毀損節點元數據結構」的矛盾。
引句：「掃描範圍:整檔文字(frontmatter 全部——含 summary/decisions[].content/why_chosen——加 body)」
**Severity**：Major

### Finding 3: [Major] 留痕綁定 HEAD 導致常規 Git 操作（如 Amend）觸發錯誤硬擋
**說明**：S3 要求留痕必須綁定 `head_sha`。在 `code/high` 流程中，開發者執行 `pass` 後若發現小錯並使用 `git commit --amend` 修正，此時 `head_sha` 已變更，導致 `code-loop check` 判定留痕無效。這迫使開發者在每次微調後必須重新跑完完整的外家檢核流程，對高頻迭代的開發行為造成不合理的硬阻斷。
引句：「range 不同源=視同無留痕,印「留痕範圍 X ≠ 推送範圍 Y,重跑 pass」」
**Severity**：Major

### Finding 4: [Major] 外家席位判定不具累加性，增加無謂的流程摩擦
**說明**：S3 要求「至少一輪 ≥ 2 席」。若兩位外家審查員分別在 R1 與 R2 留下紀錄（例如 A 在 R1 簽收，B 在 R2 簽收），系統判定每一輪的 external 席數均為 1，從而觸發 fail-closed 阻斷。這種「單輪必須達標」而非「窗口內累計達標」的假設，忽視了非同步協作中審查員反應時間不一的常態，會強制產生不必要的 `waive` 或 `skip`。
引句：「至少一輪 ≥ _TIER_ROSTER[("code","high")] 的 required-fail-closed 席數(2)→ 通過」
**Severity**：Major

### Finding 5: [Major] 詞表掃描缺乏上下文識別，導致元數據引用產生誤報
**說明**：S1 規定「不做區段標題豁免」。這意味著若節點的 `tags` 或 `related` 連結中包含詞表關鍵字（例如連結到一個標題為 `Issues/關於零檢查的討論` 的節點），掃描器將視為「承認句」並要求標記。由於 frontmatter 結構限制，此類自動化產生的引用難以嵌入 HTML 註釋標記，將導致大量無法消除的 lint 錯誤。
引句：「★不做區段標題豁免★(frontmatter 無標題,r2 s4-F4)——歷史敘述改用 H 型標記。」
**Severity**：Major