# r2 收貨與處置(code-筆記格子第0步,修正差異)

兩席收齊才動碼。正確性席報告的 severity 寫在列表項裡,用 `lumos report-normalize --write` 做純格式搬移(不改值、不動引句)。正確性席 R2C2 的引句把多行寫成 \n,quote-check 錨不到,下表機械重現。

## 重現

| id | 做法 | 結果 |
|---|---|---|
| R2C1 | 暫存 `SEE:見` 跑 note-shape --staged;`slot_check("SEE","見")` | HIT:修前提交放行、lint 唸;修後提交也擋,測試翻紅驗過 |
| R2C2 | `grep -n 'if tags.get("seen"):' r2-snapshot.patch` → 第 391 行;對照 `_ns_negation_collected` | HIT:失敗時也印設定提醒;但這正是否定現況句那組(鄰居)的既有行為,本輪 r1 架構席要求對齊它 |
| R2C3 | 搜測試檔 `check-s16` 無命中 | HIT:補測試 ⑤⑥(落帳、登記、_rule_stale_keys),同篇多條只記一筆 |
| R2A1 | 讀 `_KNOWN_GATES` 註解分組 | HIT:check-s16 自成一行帶註解(註解不用半形括號,免得截斷既有測試取 tuple 字面的寫法) |
| R2A2 | 對照 context_marker_warnings 的字樣 | HIT:提交時的格子提醒補「筆記格子『RULE:』」前綴 |

## 處置

- 折入:R2C1、R2C3、R2A1、R2A2。
- 放行:R2C2(minor)——失敗時仍印設定提醒,跟否定現況句提醒(_ns_negation_collected)同一個行為;r1 架構席才要求兩組分解方式對齊,為這點另開一種寫法反而是第二種做法。
