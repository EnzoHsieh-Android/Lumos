# code-否決提案收齊查重 r2 收貨紀錄

- 凍結材料:r2-snapshot.patch(sha256 3f40ca85cc49526093284d69e788d4dacdf9d20535a35fe09ced6a6be1c5d51c),範圍 6467401a7012bb39acb3d5be064bb88758f45818..09ffec28781a3df9c71c36d214a4f3e134beb934,排除帳本 jsonl 與 governance/ 卷證;修補差異 r2-repair.patch(c728cf14 → 09ffec28),來源 r2-repair-binding.json。
- 席位:正確性r2-sonnet(找問題席)、架構對齊r2-sonnet(不算人數),都是全新代理,派工詞明寫不讀 r1 卷證。
- 兩席收齊後才一次寫進卷證(從逐字稿取最後一則回答,避免完成通知把 < 轉成 &lt;);`git status` 只多卷證檔與兩本帳(殺傷力配方重跑留的),`git reflog -2` 最新仍是 09ffec28。
- 收貨三道:quote-check 兩席全錨(正確性 4/4、架構對齊 4/4);refcheck 全 ok(7、6 條);seat-check vacuous。
- finding ID:正確性席 F1–F3 記為 r2c1–r2c3;架構對齊席 F1–F4 記為 r2a1–r2a4。
- 本輪有 major(r2c1、r2a1),整輪 accepted 必空,全部折。

## 重現表

| id | 編排者重現 | 結果 | 採信 |
|---|---|---|---|
| r2c1 | 臨時庫一篇決策 `valid: false` 加空的 `superseded_by:`:09ffec28 的 `lumos rejections` 印 `TypeError: cannot use 'tuple' as a set element (unhashable type: 'list')`;同庫 `decisions --superseded` 印 `A_計劃: 舊做法 → []` | HIT | 採信,折;歸因修復回歸(r1 把 context 改成原值、又拿它當去重鍵) |
| r2c2 | 讀碼:先切 120 字再扣引號,引號跨界線時切完變未閉合;「推翻在前就排除」以整條決策為單位,`推翻了 d3 的舊方案;卯方案停案` 這種一句推翻、另一句停案的會漏 | HIT | 採信,折(界線:原有漏查;混合句:修復回歸) |
| r2c3 | 讀計劃 [S4]「收集出錯時 應 略過這行」,而 r1 修後實作與綁定測試要印一行略過原因 | HIT | 採信,折;歸因修復回歸(r1 改行為沒改條款) |
| r2a1 | 讀碼:`_drift_mask_quotes`(全形引號遮成等長佔位字,docstring 寫明「只是在提某個詞」的慣例)與 `_NS_NEG_QUOTES` 已有同功能;新碼另立 `_REJ_QUOTED_RE` | HIT | 採信,折 |
| r2a2 | 讀碼:認前綴行的慣例是 `SYMBOL_RE.match(line.strip())`,新碼另立 `_REJ_WHY_RE` | HIT | 採信,折 |
| r2a3 | 讀碼:`_STATUS_ENUM["project"]` 沒有 rejected;新表 project 那格有 rejected,佈景也用了不合法的值 | HIT | 採信,折 |
| r2a4 | 讀碼:`cmd_query`、`cmd_search` 的 JSON 頂層是 `results`,新指令用 `items` | HIT | 採信,折 |

## 根因分組與修前選例

| 組 | 涵蓋 | 根因 | repair 案例 | preserve 案例 |
|---|---|---|---|---|
| h1 去重鍵型別 | r2c1 | context 放進未正規化的欄位值,當 set 鍵會遇到 list | `superseded_by:` 空鍵與區塊清單兩種寫法,`lumos rejections` 與 `--json` rc 0,context 分別是 null 與 `d2,d3`;同類欄位(content、id)全部先轉字串 | `decisions --superseded` 對同兩種寫法輸出不變(`→ []`、`→ ['d2', 'd3']`);一般純量 `→ d2` |
| h2 不做的判法 | r2c2、r2a1 | 引號遮蔽另寫一份、且在切窗之後才遮;推翻判定不分子句 | 遮蔽改用 `_drift_mask_quotes`,先遮全文再切 120 字;用 `_NS_NEG_SEG_CUT_RE` 切子句,同一子句裡推翻在前才排除;引號跨 120 字界線的不收、一句推翻另一句停案的照收 | 評測尺那種「推翻…的刻意不做」照排除;開頭停案、後文提推翻的照收;引號裡的否決照不收;120 字外的照不收 |
| h3 前綴辨識 | r2a2 | 正文 WHY 行另寫正則 | 正文改走 `SYMBOL_RE`,列表項先剝掉 `- `/`* ` | 列表行、一般行照收;圍欄內照不收 |
| h4 狀態值域 | r2a3 | 作廢狀態表跟 `_STATUS_ENUM` 不一致 | project 只收 superseded;新測試斷言每個值都在 `_STATUS_ENUM` 該類型裡 | system superseded/rejected、issue wontfix 照收 |
| h5 JSON 頂層名 | r2a4 | 頂層陣列名跟鄰居不同 | `--json` 頂層改 `{"total", "results"}` | 每條欄位 node/kind/content/context 不變 |
| h6 條款與行為 | r2c3 | r1 改了略過行為沒改條款 | [S4] 改寫成「收集出錯時不印筆數、改印一行略過原因」,條款指紋變了,規格閘照制度重跑留痕 | 綁定測試照舊是 t_spec_gate_rejections_hint |

- r2c2 另提的巢狀引號(`「不做「X」不做」`):改用共用的 `_drift_mask_quotes` 後跟全專案同一個行為(不處理巢狀),不在這裡另寫一套;真圖譜 0 筆。
