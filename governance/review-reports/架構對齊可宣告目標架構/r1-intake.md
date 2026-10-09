# r1 intake

preflight-4: ran

## 前掃（便宜代理，四類）

- ① 未定義的詞 2 條，直接修真檔：「DDD」補定義；目標規則編號 `[A<序號>]` 補寫法說明。
- ② 壞引用：無（五個 [[連結]] 皆存在）。
- ③ 範圍矛盾：無。
- ④ 機械宣稱驗語意：無命中。計劃描述的現況全部成立——`_arch_alignment_hints` 只取同資料夾、同副檔名、檔名最像三個檔且不讀設定；§7.6 三問皆比對照檔；.lumos/config.json 無架構宣告欄位；慣例 skill 寫當地慣例贏；code-loop check 存在。

## 收貨三道（四席）

- report-normalize：四份皆已是正規化格式。
- quote-check（對 r1-snapshot.md）：邊界、接手、架構對齊全數錨定；通才 12 句錨到 11 句，GEN-4 引句內含「」被截斷。
- refcheck：四份引的 file:line 全部存在（通才 28、接手 28、架構對齊 28 ok；邊界用絕對路徑，refcheck 抽到 0 條，改由下方重現）。
- seat-check：四席都標「沒提到工作副本路徑」——派工材料就是那份副本，席位改引凍結內容，只觀測不擋。

## 編排者機械重現

| finding | 重現方式 | 結果 |
|---|---|---|
| GEN-4 | `grep -n '那句在宣告範圍內，以目標架構節點為當地慣例' r1-snapshot.md` | HIT（快照第 40 行） |
| ARC-1 BND-10 GEN-9 HND-5 | 讀 `_pitfall_tier` docstring 與「只印字不真的跑 impact」註解 | HIT（pitfalls 刻意不載圖譜，0.18s 對 4.7s） |
| BND-2 HND-6 GEN-8 | 讀 `_arch_alignment_hints`：`if not sibs: continue`、`if not out_files: return {}` | HIT |
| ARC-2 BND-1 GEN-6 HND-1 | 讀 `_review_roles_config` docstring 與 `_review_roles` 用 `_json_at_ref(root, base, ...)` | HIT（既有慣例只信起點版） |
| GEN-5 BND-6 | 讀 dispatch-lens-hook 的標記正則：只有 LUMOS-IMPACT、LUMOS-SPEC、LUMOS-ROLE-CARDS | HIT |
| BND-9 GEN-7 | 讀 pre-push 呼叫 pitfalls 的那行帶 `2>/dev/null` | HIT |
| BND-3 BND-4 HND-11 | 讀 `_cochange_excluded`：fnmatch、`**/` 前綴去掉再試 | HIT |
| GEN-2 BND-11 HND-7 | 讀 templates.md §7.6 標題「code-loop 與 design-loop 皆派」 | HIT |

其餘條目為規格缺口（spec 沒寫某件事），不涉程式行為，以讀凍結快照確認缺口成立。

## 處置

47 條全數折入（含折入後鏡像核對補齊的 12 條半處理與 4 處矛盾），無放行、無駁回。
