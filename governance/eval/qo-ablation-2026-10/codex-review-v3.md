B1–B8 驗收：

- B1：已解決——`_valid` 已拒絕截斷、逾時、儀器例外及長度不符，續跑只跳過有效且版本一致的結果。
- B2：部分解決——完整性、noise 比較、仲裁包及合併流程已補上，但 `merge` 未驗證仲裁答案必須是包內兩個候選；假資料可注入第三種標籤或任意 noise 值。
- B3：部分解決——固定分母及四項無效條件已實作，但 `final --labels` 仍接受任意完整標註目錄，無法證明輸入確實是 `merge` 的仲裁後產物。
- B4：部分解決——建議／假設及複合項目的評分規則已明定，但複合 gold 未原子化，且乙組指定的「下一輪再問」仍是評分準則直接命中的措辭。
- B5：部分解決——已遮掉 Codex、Claude、指示檔與 `/qo/a|b/`，並禁止 mapping 放進評分包目錄；但 GPT、OpenAI、Sonnet、`/qo-b/` 等等價線索仍原樣保留。
- B6：部分解決——原兩個反例已修，但 shell 同時修改程式與文件時仍漏判；`sed -i … src/App.kt docs/plan.md` 實測回傳 `False`。
- B7：部分解決——已輸出兩位單獨評分的敏感度結果，但未執行預登記的分歧閘；假資料可同時得到主判定 `PASS`、單一評分員 `INCONCLUSIVE`，最終仍保留 `PASS`。
- B8：已解決——`--model` 已強制必填，每場保存 runner、模型、CLI 與 Codex 設定指紋，版本不符即拒絕續跑；目前本機版本及 medium 設定亦符合預登記。

會使結論失真的 blocker：

1. [qo_ablation.py:362](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:362) 未驗證仲裁選項：第三標籤或任意 noise 數值可直接進入主指標。
2. [qo_ablation.py:433](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:433) 不驗證 `--labels` 是仲裁後產物；誤傳單一評分員資料也可能正式產出 PASS。
3. [qo_ablation.py:443](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:443) 只展示敏感度、不在三種判定不一致時改成人裁，違反預登記並可能直接接線。
4. [qo_ablation.py:56](/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/governance/eval/qo-ablation-2026-10/qo_ablation.py:56) 的文件豁免以整段 shell 字串判定，混合修改會漏算「先寫程式」，可能錯判必要門檻。

blocker 4 條
