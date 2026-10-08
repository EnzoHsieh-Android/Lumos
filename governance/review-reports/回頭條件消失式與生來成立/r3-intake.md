# 回頭條件消失式與生來成立 r3 收貨

末輪(設計審上限 3 輪)。席位:通才 10(U1–U10)、正確性 10(C1–C10)、邊界輸入 13(B1–B13)、架構對齊 9(Z1–Z9,major 1);共 42 條,blocking 15。通才、邊界輸入兩席引句全錨;正確性 #6(C6)與架構對齊 #6(Z6)同一句引句內又包了「」被截短、錨不到——不改席位引句,編排者對凍結快照機械重現(見重現表),照採。四席交齊才動計劃。

## 人裁(到上限)

第 11 項「寫下時就已成立」三輪每輪都有結構問題、r2 折入的段落自帶錯誤,攤給 Enzo:2026-10-03 裁「縮案:先做 when-gone」——本篇只做第 6 項,第 11 項連同三輪發現拆到 Projects/回頭條件寫下時就成立_計劃,改用既有 `_note_status_seq` 重新設計、重新跑設計審。

## 處置(全部折:第 11 項那一半以「拆出、移到新計劃的坑清單」折掉,`when-gone` 那一半折進本篇)

1. 第 11 項(往回查歷史與 born 呈現):C1、C4、C5、C6、C8、B1、B2、B3、B5、B9、B10、B13、U1、U2、U8、Z1、Z2、Z5、Z6、Z9 → 拆出;坑逐條寫進新計劃〈三輪設計審留下的坑〉。
2. 反斜線與兩條路一致(C2、B4、Z4、U3、C10、Z3)→ 值的正規化與驗證收成 `_probe_check_value`,`_probe_parse` 與 `_slot_retire_err` 共用。
3. 「路徑找不到」的提示(C3、U4、Z7)→ 只給新寫的、加在判定之後。
4. 判不了的原因(B8、U7)→ 記下 gone 判不了的原因、訊息照它寫。
5. 文件同步(C9、B12、U5、U6)→ SKILL.md 移出清單、範本改了跑 `lumos update` 重注入、Check D 守。
6. 反引號原文檢查(Z8)→ 一支 `_probe_gone_backtick_err` 共用。
7. 其餘邊界(B6、U9、B7、B11、U10)→ 字串去頭尾空白、`utf-8-sig`、工作目錄模式寫進天花板、讀檔上限、路徑不能含 `::`。
8. RETIRE-IF 計數被自己的範例污染(C7)→ 改數解析出的 `gone` 條件。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | 讀 `_nodehome_cat_blobs_capped` 回 None 的三種情況 | HIT | 折(第 1 組,拆出) |
| C2 | 讀 `_probe_parse` 依鍵名整串轉反斜線 | HIT | 折(第 2 組) |
| C3 | 讀 r3 稿 1.4 提示句沒限定新寫 | HIT | 折(第 3 組) |
| C4 | 讀 `_nodehome_list` 只回 NFC 路徑 | HIT | 折(第 1 組,拆出) |
| C5 | 讀天花板 2 與 2.5 的標記用語 | HIT | 折(第 1 組,拆出) |
| C6 | 引句錨不到;機械重現:`grep -n 照既有「先前表態」那行的呈現 r3-snapshot.md` 命中〈做法〉2.5;讀 `_drift_prev_ack_line` 只印在 `if not acked:` 底下 | HIT | 折(第 1 組,拆出) |
| C7 | 讀 RETIRE-IF 數 `[when-gone:` 字串 | HIT | 折(第 8 組) |
| C8 | 席位實測每提交建樹加讀語料約 2 秒 | HIT | 折(第 1 組,拆出) |
| C9 | `grep -n when-symbol skills/lumos-project-notes/SKILL.md` 無命中 | HIT | 折(第 5 組) |
| C10 | 讀 `_slot_retire_err` 對 when-* 不轉反斜線 | HIT | 折(第 2 組) |
| B1 | 同 C4 | HIT | 折(第 1 組,拆出) |
| B2 | 同 C1 | HIT | 折(第 1 組,拆出) |
| B3 | 同 C6 | HIT | 折(第 1 組,拆出) |
| B4 | 同 C2(`a\..\x.py`) | HIT | 折(第 2 組) |
| B5 | 讀 r3 稿 2.2 重複條件只在被掃那一版檢查 | HIT | 折(第 1 組,拆出) |
| B6 | 讀 r3 稿字串空白沒釘 | HIT | 折(第 7 組) |
| B7 | 讀工作目錄列檔對 NFD、gitignore 的處理 | HIT | 折(第 7 組) |
| B8 | 讀 scan 判不了的三處固定訊息 | HIT | 折(第 4 組) |
| B9 | 讀 finding 字典沒帶條件解析結果 | HIT | 折(第 1 組,拆出) |
| B10 | 讀 r3 稿 2.4 與資源段 | HIT | 折(第 1 組,拆出) |
| B11 | 讀 `_DriftProbeTree._read` 與單檔上限 | HIT | 折(第 7 組) |
| B12 | 讀 CLAUDE.md、AGENTS.md 的注入區塊 | HIT | 折(第 5 組) |
| B13 | 讀 `log.follow` 對 git log 的影響 | HIT | 折(第 1 組,拆出) |
| U1 | 同 C1 | HIT | 折(第 1 組,拆出) |
| U2 | 同 C4 | HIT | 折(第 1 組,拆出) |
| U3 | 席位實跑 `_slot_retire_err('when-gone:..\x.py')` 放行 | HIT | 折(第 2 組) |
| U4 | 同 C3 | HIT | 折(第 3 組) |
| U5 | 同 C9 | HIT | 折(第 5 組) |
| U6 | 讀 `_START_TEMPLATE` 版本由注入插值、範本無版本戳 | HIT | 折(第 5 組) |
| U7 | 同 B8 | HIT | 折(第 4 組) |
| U8 | 同 B9、C6 | HIT | 折(第 1 組,拆出) |
| U9 | 讀 r3 稿沒說 BOM 與空白 | HIT | 折(第 7 組) |
| U10 | 讀 r3 稿從第一個 `::` 切、路徑含 `::` 的後果 | HIT | 折(第 7 組) |
| Z1 | 讀 `_note_status_seq` | HIT | 折(第 1 組,拆出) |
| Z2 | 同 C4 | HIT | 折(第 1 組,拆出) |
| Z3 | 讀 r3 稿 `_probe_gone_err`、`_probe_norm_value` 沒說呼叫 `_drift_cond_split` | HIT | 折(第 2 組) |
| Z4 | 同 C2 | HIT | 折(第 2 組) |
| Z5 | 讀 `cmd_drift_scan --json` 頂層 `unknown` | HIT | 折(第 1 組,拆出) |
| Z6 | 同 C6 | HIT | 折(第 1 組,拆出) |
| Z7 | 讀 `_drift_probe_judge` 不認得條件鍵 | HIT | 折(第 3 組) |
| Z8 | 讀 r3 稿兩個呼叫端各寫原文檢查 | HIT | 折(第 6 組) |
| Z9 | 讀 `_drift_vault_rel` | HIT | 折(第 1 組,拆出) |
