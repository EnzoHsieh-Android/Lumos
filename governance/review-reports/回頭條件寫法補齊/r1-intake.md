# 回頭條件寫法補齊 r1 收貨

preflight-4: ran

## 首輪前掃(便宜 agent,固定清單四類)

- ①未定義的詞 0、②壞引用 0、③範圍自相矛盾 0。
- ④機械宣稱驗語意:前掃員報 6 條「錯」,全是把計劃要新做的事(`_revisit_misplaced`、`_revisit_closed`、`_revisit_lines` 加參數、`_probe_lines` 排除已結案、`_ns_revisit_violations` 多看三個位置、E5 多一句)當成「宣稱現況已經這樣」——不採信,計劃那幾句講的是做法。
- 編排者自查補一條語意命中(修真檔,不算 finding):
  - 修改前:「理由…至少 4 個字而且含實字(照 `drift ack` 理由的既有門檻)」
  - 修改後:「至少 4 個實字(字母、數字或漢字…;照「已排除」行理由的既有算法 `_excluded_line`,不照 `drift ack`——那邊只數字元、全是標點也過)」
  - 依據:`drift ack` 的理由檢查只看去頭尾空白後 ≥4 個字元與一行(`cmd_drift_ack` 那段);只數實字的是 `_excluded_line`。沒動「核心裁定」。

## 收貨

席位:通才 8(U1–U8)、正確性 9(C1–C9)、邊界輸入 9(B1–B9)、架構對齊 6(Z1–Z6);共 32 條,blocking 7(C1、B1、B2、U1、U2、U3、Z1)。四席引句全數錨定;架構對齊席報告的 `severity: major ⚠` 用 `report-normalize --write` 拆成兩行(純格式搬移)。外家席依 2026-09-30 使用者裁定預設不派。四席交齊才動計劃。

## 依根因分組(全部折入計劃)

1. 結案日期比今天、CI 時區誤擋(C1、U2、B2,三席獨立)→ 拿掉這條檢查。
2. 結案標記位置與文法(B1、Z2、U7、B9、C5 位置與 `]` 部分)→ 跟 `[by:]` 一樣的開頭標記;值切到第一個 `]`;理由不放連結;行內程式碼先剝。
3. 寫錯的結案標記讀取端怎麼辦(C5、B7、U8 壞損部分)→ 合格才算結案,寫錯當沒寫;壞損行不讀結案標記。
4. 非 REVISIT 行的 `[closed:` 也擋(U1、B6)→ 只在 REVISIT 行上看。
5. 刪除線改法自相矛盾(U3、C7)→ 改法寫成完整的結案寫法,第一層與 Z 段同一句。
6. 存量清單放 E5(U4、U5、B5、Z3、C4、B4)→ 搬到 Z 段(`_probe_lines` 的不評估清單多收一種),不寫帳、不受 E5 軟段上限。
7. 開頭欄位講法(C3、B3、U6)→ 行首形狀不算句中;只有欄名在前的算。
8. 引號範例誤報(C2)→ `REVISIT:` 前面是開引號就不算。
9. 第三套關掉提醒(Z1)→ 寫明三者分工與條件式的判準,drift ack 拒收已結案的行。
10. 介面與共用(Z4、U8 參數部分、Z5)→ 拿掉死參數,實字計數抽成 `_real_chars`。
11. 落點與同步(Z6、C8、U8 另案部分)→ 兩篇各補 WHY;技能主檔也改、範本不改並寫理由;另案開了才放連結。
12. 改名工具改寫舊行(C6)→ 寫進相容與天花板 4。
13. 提示與邊界(B8)→ 改法寫明核取方塊、粗體、星號、刪除線不行,冒號後直接接日期。
14. 先例描述(C9)→ 更正 ESLint 那句。

## 重現表

| id | 怎麼查 | 結果 | 去向 |
|---|---|---|---|
| C1 | 讀 `.github/workflows/ci.yml` 的 note-shape 步驟(沒設時區)與計劃〈做法〉2.3 | HIT | 折(第 1 組) |
| C2 | 讀 `Projects/存量漂移防線_計劃` 第 104 行的引號範例 | HIT | 折(第 8 組) |
| C3 | 讀 `_revisit_lines` 走 `_search_visible_lines`、不分區塊 | HIT | 折(第 7 組) |
| C4 | 讀 `_SOFT_CAP` 與 `warn_soft` | HIT | 折(第 6 組) |
| C5 | 讀 `_probe_parse` 遇到不認得的標記就停 | HIT | 折(第 2、3 組) |
| C6 | 讀 `scripts/graph-rename.sh` 全圖譜改寫連結 | HIT | 折(第 12 組) |
| C7 | 讀計劃 1.2 與 1.4 | HIT | 折(第 5 組) |
| C8 | 讀 `scripts/templates/graph-discipline.md`、`skills/lumos-project-notes/SKILL.md` | HIT | 折(第 11 組) |
| C9 | ESLint no-warning-comments 的 `location` 選項(編排者已知有 start/anywhere) | HIT | 折(第 14 組) |
| B1 | 席位實測 `_probe_parse("[when-file:a.py][closed:…][by:…]")` 回 by None;編排者讀 `_PROBE_TOKEN_RE` 只認 when-/by | HIT | 折(第 2 組) |
| B2 | 同 C1 | HIT | 折(第 1 組) |
| B3 | 同 C3 | HIT | 折(第 7 組) |
| B4 | 讀 E5 迴圈只收 `_revisit_lines` 的 REVISIT 行 | HIT | 折(第 6 組) |
| B5 | 讀 Z 段註解「不寫治理帳」與 E5 的 gov 事件 | HIT | 折(第 6 組) |
| B6 | 讀計劃 2.3「寫在不是 REVISIT 的行」 | HIT | 折(第 4 組) |
| B7 | 讀計劃 2.2 沒定義寫錯的處置 | HIT | 折(第 3 組) |
| B8 | 讀 `_REVISIT_MARK_RE` 只去一層記號 | HIT | 折(第 13 組) |
| B9 | 讀 `_strip_inline_markup` 未閉合反引號截掉後段 | HIT | 折(第 2 組、天花板 5) |
| U1 | 讀計劃摘要行有未包反引號的標記 | HIT | 折(第 4 組) |
| U2 | 同 C1 | HIT | 折(第 1 組) |
| U3 | 讀計劃 1.4 與 2.3 | HIT | 折(第 5 組) |
| U4 | 同 B5 | HIT | 折(第 6 組) |
| U5 | 同 C4 | HIT | 折(第 6 組) |
| U6 | 同 C3 | HIT | 折(第 7 組) |
| U7 | 讀既有標記切法 `[^\]\n]*` | HIT | 折(第 2 組) |
| U8 | 讀 `_revisit_lines` 兩個呼叫端、路線圖第 62 行 | HIT | 折(第 3、10、11 組) |
| Z1 | 讀 `cmd_drift_ack`、`_retire_lines` 跳過 superseded | HIT | 折(第 9 組) |
| Z2 | 同 B1 | HIT | 折(第 2 組) |
| Z3 | 讀 `_drift_doctor_lines` 的 dead 呈現 | HIT | 折(第 6 組) |
| Z4 | 同 U8 參數部分 | HIT | 折(第 10 組) |
| Z5 | 讀 `_excluded_line` 內嵌算法 | HIT | 折(第 10 組) |
| Z6 | 讀 `Systems/筆記內容閘` 既有 REVISIT 規則 WHY 的位置 | HIT | 折(第 11 組) |
