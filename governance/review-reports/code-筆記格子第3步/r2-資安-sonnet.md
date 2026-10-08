severity: minor

**審查對象**:`/tmp/code3-r2.patch`(對應提交 384f4574)。我在臨時 repo 裡實測了一次 S16 的輸出路徑。

## 發現

### R2S1 doctor S16 把筆記裡的控制字元原樣印到終端,這次改動還把來源換成可能含續行的重組全文
severity: minor
blocking: 否 — 只能騙終端畫面,不能執行程式碼、也拿不到密鑰。
引句:「for t in _ns_summary_logical("---\n" + "\n".join(n.fm_lines) + "\n---\n").values():」
- **誰**:提交惡意筆記的第三方。
- **從哪裡**:被 clone 的陌生 repo,或合併進來的分支,裡面的任一篇筆記 `summary` 的 `RULE:` 行。
- **送什麼**:行內夾 ESC 序列,例如 `\x1b]0;…\x07` 改視窗標題,或 `\x1b[2J` 清屏。
- **拿到什麼**:受害者跑 `lumos doctor` 時,S16 會逐字印出。我在臨時 repo 實測,輸出出現 `hello ^[]0;PWNED^G^[[2J evil`,三個序列都原樣進了終端。攻擊者能改標題、清掉或覆寫前面的警告,讓畫面看起來沒事。
- **缺口**:同一輪的 S17、S18、S19 都補了 `_esc_clean`,S16 漏了。這是同一類問題的漏網路徑。
- **成因**:`_doctor_stale_rules` 組行時用 `f"{rel}:{why}:{(slot_parse(t[5:])['core'] or t[5:])[:40]}"`,沒過 `_esc_clean`。
- **相關程式位置**:`scripts/lumos:3450`、`scripts/lumos:2500-2509`。`rel` 是檔名,git 檔名可含控制字元,同樣沒清。
- **修法**:在組行處包 `_esc_clean(..., 300)`,與 S17 到 S19 一致。

### R2S2 `_metric_gate_off` 的 lint-new 分支沒有走 `_doctor_cfg_bytes` 的捷徑防護
severity: minor
blocking: 否 — 只推論得到縱深防禦缺口,寫不出能拿到的東西。
引句:「return _lint_new_config(root)["mode"] == "off"」
- **推論**:`_lint_new_config` 用 `p.is_file()` 加 `read_text`,會跟著捷徑讀。`.lumos/config.json` 若是指到 repo 外的捷徑,這裡仍會讀它。其他閘走的是 `_doctor_cfg_bytes`,有擋捷徑。
- **為什麼只算縱深防禦**:這支只取 `lint_new.gate` 與整數欄位,值只影響 S18 提醒要不要出現,不外洩內容。攻擊者本來就能直接在 repo 內寫 config.json 達到同樣效果。
- **相關程式位置**:`scripts/lumos:24448`。

## 六類逐類

1. **不可信輸入流到危險操作**:S17、S18、S19 的輸出都過 `_esc_clean`(C0 與 C1 都換成空格)。這包括 `_metric_rows` 的寫法不合提醒,以及 `_slot_replacement_dead` 回傳的訊息(含 `link_target(ref)` 的筆記原文)。S17 的決策引用經 `_dref_parse`、`_dref_norm`,只進 `env.resolve`(查記憶體裡的筆記表)和 `_node_decisions`,不碰檔案系統路徑,也沒有 eval 或 shell 拼接。`_drift_jsonl_parse` 只做 JSON 解析,不做 pickle 之類的反序列化。`datetime.fromisoformat` 的 OverflowError 已補接。唯一缺口是 R2S1(S16)。
2. **登入與權限**:已看,無。
3. **密鑰與個資**:錯誤訊息只印例外類別名(`type(ex).__name__`),不印內容。治理帳寫入沒有新增敏感欄位。已看,無。
4. **加密與傳輸**:已看,無。
5. **執行邊界**:`_doctor_cfg_bytes` 擋了檔案捷徑、`.lumos` 資料夾捷徑,以及 resolve 後路徑不符的情況,三段已合併,行為與原本抄的三份一致。唯一旁路是 R2S2。這次沒有新增 hook 或 CI 去執行不可信位置的檔。
6. **行動端**:已看,無。

新依賴:無(只用標準庫 `datetime`、`json`、`re`)。

最高嚴重度 minor,blocking 0 條
