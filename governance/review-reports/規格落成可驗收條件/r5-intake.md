preflight-4: ran

# r5 收貨紀錄(規格落成可驗收條件_計劃,拆後半套)

- 前掃:lint 0 問題(三篇);refcheck ok;spec-trace 11 條/綁了 0/懸空 11(未寫,預期)。
- 凍結審材 r5-snapshot.md(指紋 8a88175a0897dd65、223 行);六席全新(*5-sonnet);外家席缺席(Codex 額度)。
- 拆分:逃逸自動記_計劃(9 條全綁)、雙向門放行_計劃(todo,18 條草案)在派工材料裡只當背景,不是本輪審材。
- 回滾4 尾行「無 blocker」被記帳器當成藏了更高等級,請該席重傳(只改尾行兩句);以重傳版記帳。
- 席報告先落 repo 外暫存區;正確性/簡化/架構對齊三席由通知抄錄,接手/邊界/回滾三席直接從逐字稿輸出檔抽最後一則(避免手抄漏字);HTML 實體還原同前。架構對齊5 回傳開頭多了一句「正在寫報告」的閒話,存檔從 severity 行起。
- `report-normalize --write`(邊界5/接手5 各 1 處、簡化5 6 處);`refcheck --repo .` 六份 ok。
- 席位尾行:接手5 尾行先寫 4 條後自己更正為 3(以逐條為準);回滾5 尾行把 F4/F5 誤寫成 F9/F10(編號筆誤,內容對得上)。

## quote-check(對回 r5-snapshot.md)
| 席 | 結果 |
|---|---|
| 正確性5、邊界5、回滾5、架構對齊5 | 全數錨定 |
| 接手5 | 7 句 2 句錨不到(#3 少抄半句、#7 引的是 design-loop 節點);該兩條(E11、E20)由編排者重現 |
| 簡化守護者5 | 6 句 1 句錨不到(#4 <10 字);該條(E7)由編排者重現 |

## 編排者重現(機械)
- **E1 支數=斷言數**:`scripts/test_lumos.py` 的 `check()` 逐斷言累加 PASS,摘要行印 `N passed, N failed`;`lumos 測試(N 案例)` 那行才是支數(`:29353`)→ 成立。
- **E2 半套不留痕 → unreviewed 分支永遠 unknown**:`_door_for_loop` 讀 `kind: spec-gate` → 成立(逃逸自動記_計劃已寫「恆零筆」,主計劃沒寫)。
- **E3 無 [SN] 整步跳過**:`_disposal_clause_step` 對 `SPEC_CLAUSE_RE` 零命中 `return "skip"` → 成立。
- **E4 簽名沒有 rows**:現行 `_disposal_clause_step(rows, spec, root, env, loop_id)` 靠 rows 算首筆帳 → 成立。
- **E5 94%/4%/1% 口徑**:全帳設計審 finding_kinds 今天 2083/136/36 = 92/6/2(09-16 是 94/4/1);本迴圈四輪 78/13/5——席位算的是本迴圈,spec 沒寫口徑 → 折成寫口徑,數字本身不是錯。
- **E6 `_run_bound_tests` 既有**:`scripts/lumos:25810` 有 green/red/unproven/no-cmd/逾時整套 → 成立,PRIOR-ART 漏列。
- **E7 英文觸發詞不在文法**:文法產生式只有中文四詞 → 成立。
- **E11 合約草稿缺跳過條件**:design-loop 第 39 行既有 INVARIANT 把「code- 迴圈、無 [SN]、舊迴圈、凍結/回放」寫進正文,草稿沒有 → 成立。
- **E13 `MANUAL_REF_RE` 只認半形冒號**:`scripts/lumos:3402` → 成立。
- **E17 158 vs 409 組**:算法不同(單向包含 vs 互為子字串、是否含 class 前綴),只說明現象,數字改寫成「依算法 158 或 409」。

## 去重對照(E1–E22;全折)
| id | 內容 | 席 | 嚴重度 | 型 | 折法 |
|---|---|---|---|---|---|
| E1 | 自家 runner 的 N passed 是斷言數;`_RAN_EVIDENCE` 沒 unittest 樣式 | 接F1、邊F1、邊F2、正F5 | blocker | spec | N=測試工具的支數;每棧加支數正則(本 repo 讀「N 案例」);補不出的棧只印有沒有跑 |
| E2 | 不留痕 → unreviewed 分支致殘、未揭露 | 簡F3 | blocker | spec | 第三節寫明後果;治理帳 spec-gate-run 一行 |
| E3 | 無 [SN] 整步跳過 vs 全部要有回退節 | 邊F3 | blocker | spec | 回退節只對有 [SN] 的計劃;S3 改寫 |
| E4 | `_clause_check` 簽名沒有首筆帳輸入,S10 不可實作 | 邊F5 | blocker | spec | 不回溯判斷在呼叫端;簽名加 grammar 參數;新 S14 |
| E5 | 94/4/1 對不上本迴圈四輪 | 回F1 | blocker | spec | 寫死口徑=全帳,補今天數字 |
| E6 | 既有 `_run_bound_tests` 沒列 PRIOR-ART,開新指令 | 簡F2 | major | spec | 跑的機器借它,只多一種 items 來源;新指令保留(它會擋) |
| E7 | 英文觸發詞不在文法 | 簡F4 | major | spec | 半套只認中文,散文改掉 |
| E8 | RETIRE-IF ② 量不到;第二階段 30 份也量不到 | 正F6、簡F5、回F6 | blocker | spec | 治理帳 spec-gate-run;三處判準改讀它;新 S12 |
| E9 | 觸發詞開頭無逗號的縫 | 正F1 | blocker | spec | 文法加「缺分隔=格式看不懂」;新 S13 |
| E10 | N==1 但 skipped 印紅或綠未定 | 正F4 | major | spec | 弱證據;S6 改寫 |
| E11 | 合約草稿缺跳過條件、S10 無合約背書;落地第 2 步會波及舊迴圈 | 接F3、接F6 | major | spec | 草稿補全部跳過條件 |
| E12 | 回退節標題/引用塊/fence/多節判準未定 | 正F3、邊F4 | major | spec | 判準寫死 |
| E13 | manual 全形冒號只印通用訊息 | 邊F6 | major | spec | 加提示 |
| E14 | 「已排除:不可逆」把待填講成已有 | 正F7 | major | spec | 措辭改 |
| E15 | 回退 sha 語意(填改動本身 revert 不到);回退①會撤掉在擋的三步 | 回F4、回F5 | major | spec | 基準=父提交、提交前記;回退清單改精確 |
| E16 | RETIRE-IF ① 口徑;跟 design-loop 的 REVISIT:2026-11-08 重疊 | 回F7 | major | spec | 口徑寫死、合併量 |
| E17 | 158 組數字重算 409 | 回F3 | minor | spec | 寫「依算法 158 或 409」 |
| E18 | 前四輪 96 條折入散在三篇無對照 | 回F8 | major | process | 審計修正紀錄加歸屬段 |
| E19 | 「為什麼」表對半套說服力弱 | 簡F6、接F5 | minor | spec | 誠實界線一句 |
| E20 | S9 在只有一種門時是重言式 | 接F4 | minor | spec | 第四節一句 |
| E21 | 停用詞訊息要兩段式;支數三棧收法只是承諾 | 架構對齊 ×2 | minor | spec | 訊息分行;三棧各補一條或印「讀不出」 |
| E22 | doctor 分母為零的印法 | 邊F7 | minor | spec | S11 補 |
接F2/簡F1/回(固定席段)/正F2 為「無缺陷」核對,不列。
