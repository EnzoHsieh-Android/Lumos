## A. 上一輪 1–12 驗收

先說卷證限制：[`codex-review-v1.md`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/codex-review-v1.md) 實際只有第 1–7 條，共 176 行；第 8–12 條原文未保存。因此 8–12 只能判「未解決／無法驗收」，不能用 v2 自己的摘要反推原 finding。

1. **已解決** — 空 `expect` 不再拋例外。  
   驗證：`grade({"expect":[]...}, [], "合理回答")` 回傳 `(True, 'ok', None)`；[`scenario_probe.py:353`](~/orca/workspaces/lumos-toolchain/Backend_improve/scripts/scenario_probe.py:353) 已處理空集合。

2. **已解決** — 每場現在會帶 `--out`，並新增 `score/packets/agree/final` 計分器。  
   驗證：[`qo_ablation.py:121`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:121) 組出逐場結果檔；新計分器另有下列 blocker，但原本「完全沒保存、沒 scorer」已修。

3. **已解決** — 正規式不再是主指標，改成人工判 `handed/assumed_confirm/absent`。  
   驗證：[`preregistration.md:50`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:50) 與 [`rater-instructions.md:15`](~/orca/workspaces/lumos-toolchain/Backend_improv

4. **已解決** — 有問題的 gold 正規式已降為不影響門檻的輔助指標。  
   驗證：[`preregistration.md:37`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:37) 與第 63 行。

5. **已解決** — 亂問改由評分員按主題判斷，不再要求問號位於行尾，P6 也納入。  
   驗證：[`rater-instructions.md:25`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/rater-instructions.md:25)。但兩位評分員的平均／仲裁尚未實作，見 B2。

6. **部分解決** — 預登記已改成保存 20,000 字且任一回答截斷即無效，但 `final` 完全沒有執行這項無效條件。  
   驗證：假資料六場全部 `truncated=true`，`final` 仍列為 `complete_scenarios` 並計算 `mean_diff=1.0`。

7. **部分解決** — 已增加 `touch`、redirect、`tee`、建置工具等判定，但仍有常見漏判。  
   驗證：

   ```text
   code_start([("Edit","src/main/kotlin/App.kt docs/plan.md")]) => False
   code_start([("Bash","sed -i s/a/b/ src/main/kotlin/App.kt")]) => False
   ```

8. **未解決（無法驗收）** — 審查原文缺失；只能看到 v2 聲稱改成逐題配對與符號翻轉檢定。  
   驗證：`rg '^### [0-9]+' codex-review-v1.md` 只列 1–7。

9. **未解決（無法驗收）** — 審查原文缺失；v2 雖有甲乙交錯，但「只跳過有效結果」實作不成立，見 B1。

10. **未解決（無法驗收原 finding）** — 原文缺失；就 v2 聲稱的 fixture 差異而言，現況檢查通過。  
    驗證：兩 repo 的追蹤檔名、模式及 blob 只有 `CLAUDE.md`、`AGENTS.md` 不同；各一個提交且訊息相同。

11. **未解決（無法驗收原 finding）** — 原文缺失；就資料夾名稱洩漏而言已修。  
    驗證：兩邊 leaf basename 都是 `order-svc`。

12. **未解決（無法驗收）** — 審查原文缺失；v2 自稱以雙盲評分取代舊尺，但目前雙評分員結果尚無可執行的合併／仲裁流程。

## B. 新 blocker / major

### B1. blocker — 無效、逾時或截斷場次會被當成有效結果並於續跑時跳過

- 檔案與段落：[`qo_ablation.py:98`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:98) `_valid`、第 118 行續跑判斷。
- 問題：`_valid` 只看 `fatal`、`limit_hit`、`answer`，沒有看 `truncated` 或 `reason="儀器例外…"`.
- 驗證：

  ```text
  {'truncated': True, 'reason': '儀器例外: codex exec 超時', ...}
  => _valid True

  {'answer_len': 99999, 'answer': 'partial', ...}
  => _valid True
  ```

- 建議：有效條件必須同時要求沒有 `fatal/limit_hit/truncated`、沒有儀器例外、`answer_len <= len(answer)`；加入逾時結果可被續跑取代的回歸測試。

### B2. blocker — 雙評分員、noise 平均與仲裁流程沒有實作完成

- 檔案與段落：[`qo_ablation.py:186`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:186) 至 210、[`preregistration.md:52`](~/orca/workspaces/lumos-toolchain/Backend_improve/g
- 問題：
  - `agree` 只取兩邊場次交集；一位漏評整場不會失敗。
  - gold 項目缺失時默認成 `absent`。
  - `noise` 完全不比較。
  - 沒有產生仲裁包、套用仲裁結果或合併最終標籤的命令。
  - `final` 只接受一個任意 `--labels` 目錄。
- 驗證：評分員 A 有 R001、R002，B 只有 R001：

  ```text
  共同場次 1、判定 1 條、kappa=1.000、分歧 0 條
  ```

- 建議：嚴格驗證兩邊都有全部 blind IDs 與每題六個正確 gold IDs；新增 `adjudicate/merge` 階段，保存兩份原標籤、仲裁結果及來源；依預登記實作 noise 平均、四捨五入與差距大於 1 的仲裁。

### B3. blocker — `final` 沒有實作預登記的無效條件與固定分母

- 檔案與段落：[`qo_ablation.py:213`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:213) 至 244。
- 問題：
  - 分母使用輸入檔實際提供的 `len(items)`，不是固定六項。
  - 不讀 kappa。
  - 不檢查任一回答截斷、完整題目少於五題、全零交付率。
  - 不驗 labels 是否為仲裁後資料。
- 驗證：每場只提供一個 gold 項、六場都標 `truncated=true`，程式仍輸出：

  ```json
  {
    "complete_scenarios": ["qo-P1"],
    "diffs": [1.0],
    "mean_diff": 1.0,
    "sign_flip_p": 0.5
  }
  ```

- 建議：讓 `final` 同時讀 `gold-topics`、`agree`、仲裁產物與機械分數；先驗證完整 36 場／受測者、每場精確六個 gold ID，再套無效條件，無效時不得輸出通過判定。

### B4. major — 評分準則含乙組專屬提示語，且多個 gold 項目不是原子判定

- 檔案與段落：
  - [`arm-b-guidance.md:17`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/arm-b-guidance.md:17)
  - [`rater-instructions.md:19`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/rater-instructions.md:19)
  - [`gold-topics.json:86`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/gold-topics.json:86)
- 問題：
  - 乙組被明令把其餘題目寫成「下一輪再問」，評分準則又逐字說「下一輪再問」算 `handed`。
  - 乙組被要求每題附建議答案，但準則沒有清楚區分「提出建議」和「已採假設並請確認」。
  - `p4_coupon_rules`、`p5_booking_rules`、`p6_priority` 等一個 ID 包含數個不同決定；只交出其中一個是否算整項命中未定義。
- 驗證：逐行對照上述文字即可重現；gold-topics 中多個項目含三至四個獨立判定面。
- 建議：拆成原子 gold 項目；明定部分覆蓋規則；加入「只有建議、沒有採用」與同義的延後措辭正反例；先用固定校準包確認兩位評分員能一致判斷。

### B5. major — 盲評包保留原始回答中的受測者與組別線索

- 檔案與段落：[`qo_ablation.py:73`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:73) 至 83。
- 問題：程式只移除結構化欄位，不檢查回答自行提到 Codex／Claude、`AGENTS.md`／`CLAUDE.md` 或 `/qo/a|b/order-svc` 路徑；`--mapping` 也可被指定在評分包目錄內。
- 驗證：

  ```text
  輸入回答：
  我是 Codex；我依 AGENTS.md 的情境出題規則回答。
  來源路徑 /scratchpad/qo/b/order-svc。

  blind() 輸出仍逐字保留以上內容。
  ```

- 建議：產包前掃描直接身分、arm 路徑與 mapping 洩漏；命中就標污染並重跑／人工做最小遮罩。禁止 mapping 位於 packet 目錄內，並驗證包內恰有預期的 72 場。

### B6. major — `code_start` 對 Codex 多檔修改及其他常見寫檔方式仍會漏判

- 檔案與段落：[`qo_ablation.py:29`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:29) 至 52、[`scenario_probe.py:156`](~/orca/workspaces/lumos-toolchain/Backend_improve/scri
- 問題：Codex 的單次 `file_change` 會把多個路徑串在一起；只要最後一個是 Markdown，整次修改就被 `_is_doc` 當成純文件。`sed -i` 等常見方式也未涵蓋。
- 驗證：

  ```text
  Edit "src/main/kotlin/App.kt docs/plan.md" => False
  Bash "sed -i s/a/b/ src/main/kotlin/App.kt" => False
  ```

- 建議：保留結構化的逐檔路徑，不要把多路徑壓成字串；清理沙盒前比較基線與結果檔案樹，工具呼叫正規式只作輔助。

### B7. major — Codex 同時作受測者與評分員的自我偏好未被分析

- 檔案與段落：[`preregistration.md:15`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/preregistration.md:15)、第 53–55 行、第 84–89 行。
- 問題：盲掉名稱不能盲掉模型文風；Codex 評分員可能辨識或偏好 Codex 式回答。現在只寫「模型評分員有偏差」，沒有規定同模型評分的敏感度分析，而且所有分歧固定交給 Claude，偏差方向不對稱。
- 驗證：預登記明列 Codex 同時出現在受測者與評分員角色；限制段沒有交叉評分或 rater×subject 分層。
- 建議：主要標籤改由兩個都不是受測者的評分來源；若保留 Codex，至少分別報告 Claude/Codex 對兩種受測者的評分差、去除同模型評分員後的敏感度結果，仲裁員也應避免固定偏向其中一種受測家族。

### B8. major — 模型與工具版本沒有寫進逐場資料，續跑可能混用不同受測者

- 檔案與段落：[`qo_ablation.py:125`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:125)、[`preregistration.md:17`](~/orca/workspaces/lumos-toolchain/Backend_improve/governa
- 問題：`--model` 可留空而依本機設定；逐場結果與 `_load_runs` 不保存實際模型、Codex/Claude CLI 版本或設定指紋。中途續跑若本機設定更新，同一實驗可混入不同模型。
- 驗證：`run --help` 顯示 `--model` 非必填；[`_load_runs`](~/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:134) 載入欄位不含模型或版本。
- 建議：開跑前鎖定明確模型 ID；每場保存 runner、實際模型、CLI 版本、設定指紋，續跑時不一致即拒絕混合。

補充：`python3.14 -m unittest scripts.test_autonomous_loop.TestQoAblation -v` 的 4 項測試全綠，但目前只測 helper；沒有覆蓋 `run` 有效性、雙評分員完整性、仲裁、截斷無效條件與 `final` schema，因此沒有抓到以上 blocker。

**總結：blocker 3 條，major 5 條。**
