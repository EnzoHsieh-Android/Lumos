## 審查結果

### 症狀

已讀，無 finding。

### 診斷

已讀，無 finding。`RISK·守衛面` 確實由 frontmatter 的 `risk/守衛面` 經 `_impact_contract()` 組成；risk 值域也確為四值。現行 indirect 保送字面條件確為任何非空 `contract` 且 hop 在上限內。

### 反事實

已讀，無 finding。

### 主案 v2

#### f1 — blocker — 主案 v2 §2–§3／落地驗收／尺

引句:「被降節點仍在輸出 → must_in_out 結構性不退,棘輪只當覆核」

問題：這個「結構保證」偷換了兩種輸出口徑。`must_in_out` 計的是 `impact --json` 的完整 `results`，而 hook 才是人實際看到的輸出。主案同時規定 reference lane 的 JSON 全量保留、hook 卻只顯示 3 條；第 4 條以後即使是 goldset 的 must，也會被 `must_in_out` 算成「在輸出內」，但人根本看不到。現行 rescued 沒有 cap，hook 會逐條全部顯示；所以「hook cap 3」不是沿用 rescued 的結構保證，而是新造一個未被棘輪覆蓋的召回洞。測試清單只有「被降者仍在 results」，沒有「所有 must reference lane 均在人讀 hook 可見」或明文承認 cap 後不再保證人眼召回。這直接打穿 v2 用 reference lane 解召回風險的核心賣點。

查證：`governance/eval/retrieval_eval.py:355`、`governance/eval/retrieval_eval.py:359`、`scripts/hooks/claude/impact-hook.py:356`、`scripts/hooks/claude/impact-hook.py:359`；spec `/tmp/pin-denoise-a-r2.md:64`、`:66`、`:73`、`:75`、`:87`、`:97`、`:101`、`:113`、`:126`。

#### f2 — major — 主案 v2 §2–§3／工具清單 #4

引句:「★不過門檻、不佔名額、不進 free 排序★,附加在 free(與 rescued)之後輸出」

問題：新增 `lane` 後，現行 evaluator 不會依 `lane` 分桶；它把所有 `pinned` 非真值項都當 free。這不只污染 `eval_edit` 的 P@8/nDCG：評測前置的 `_touched_edit()` 也用相同的 `not x.get("pinned")` 判準，會把 soft-guard 納入「free 前 k」的未標觸及集。工具清單只點名修改 `eval_edit`，漏了 `_touched_edit`／`collect_unjudged`。結果可能在真正計分前就被 ablation 的 unjudged 閘擋下；而本案又凍結 goldset，不能靠補標解除。故「P@8 母體不含 lane」目前不是只改工具清單 #4 所述落點即可成立，落地規格不完整。

查證：`governance/eval/retrieval_eval.py:159`、`:161`、`:207`、`:232`、`:335`、`:336`、`:340`；spec `/tmp/pin-denoise-a-r2.md:64`、`:65`、`:73`、`:79`、`:99`、`:101`。

### 落地驗收

#### f3 — major — 落地驗收／總開關／尺

引句:「固定席噪音:held 82→預期 ~39(考卷口徑;live 96→53)、train 15→~8;★落地時 pin_noise 進閘「不准變多」★。」

問題：按 spec 的預設值，落地後 `LUMOS_IMPACT_HARD_PIN=0`，整段是死碼，固定席仍是舊制，因此預設驗收不可能得到 82→39；必須明定這些數字是在 `LUMOS_IMPACT_HARD_PIN=1` 的候選臂驗收。更嚴重的是，現行 `pin_noise` 明文「只印不閘」，verdict 與 gates 都沒有該欄。工具清單 #4 只要求修正口徑，沒有把 row → verdict → gate → history 的接線列入工具清單或測試。照草案落地會出現文件宣稱「進閘」，實作仍只是報表數字。

查證：`governance/eval/retrieval_eval.py:361`、`:417`、`:420`、`:421`、`:438`、`:596`、`:601`；spec `/tmp/pin-denoise-a-r2.md:76`、`:78`、`:86`、`:99`、`:111`。

### 工具清單（草）

除 f2、f3 外，已讀，無 finding。

### 已試已殺

已讀，無 finding。

### 尺（v2）

除 f1、f3 外，已讀，無 finding。

### PRIOR-ART

已讀，無 finding。「合約值域既有、硬軟分級為本案新規則」與 code 現況相符。

### 實務隱患

#### f4 — major — 實務隱患／召回風險、回滾

引句:「召回風險:v2 結構性歸零(被降者不離開輸出;free 不動)」

問題：召回風險不能稱「歸零」。四層逐條看：

- R1：hard-pin 分級本身不刪被降節點，但是否真正保留取決於新 reference lane 實作。
- about 豁免：已退出，故無此層可補漏。
- 治標籤：已退出，故無此層可補漏。
- 棘輪：現行只看 JSON `results`，看不到 hook cap 3 造成的人眼漏檢；完整執行時目前也只 ratchet `all`，不是 held 個別棘輪。

因此第 4 條以後的 soft-guard must 會形成「JSON 算召回成功、hook 實際沒顯示、棘輪仍綠」的假陰性。回滾方面，knob=0 若確實包住 reference lane 可回舊制，這部分可行；但 spec 的「逐 byte」測試應覆蓋完整 JSON、human-readable CLI 與 hook additionalContext，不能只測 `results`。

查證：`governance/eval/retrieval_eval.py:355`、`:359`、`:473`、`:495`、`:611`、`:617`；`scripts/hooks/claude/impact-hook.py:332`、`:339`、`:356`；spec `/tmp/pin-denoise-a-r2.md:66`、`:74`、`:78`、`:101`、`:113`、`:126`、`:129`。

- 守衛面：有 f1、f4；會產生「機械綠、人看不到」。
- 回滾：除 f4 所述測試範圍不足外，單 knob 包整段的方向可行。
- 效能：無否決級問題；新增 lane 是既有候選的記憶體分桶與格式化，沒有新增讀盤。
- 併發：無；流程是單次呼叫內的局部 list 操作，未新增共享可變狀態或寫入。

### 審計修正紀錄 r1

已讀，無 finding。r1 對 about 豁免、治標籤及「降自由席等於保留」的撤回與現碼、前案一致；但沒有預見 f1 的 JSON/hook 新口徑裂縫。

### 下一步

已讀，無 finding。

最嚴重 severity：blocker
