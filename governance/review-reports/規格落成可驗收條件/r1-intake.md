preflight-4: ran

# r1 intake(首輪前掃 + 編排者重現)

前掃 2026-09-17:派 sonnet 拿固定四類清單掃凍結副本。①未定義 5 條(全是本案要新建,非缺陷)②壞引用 1 條 ③範圍矛盾 2 條 ④機械宣稱驗語意 7 條(5 條驗真、2 條驗假)。

## 直接修真檔的(存在類 / 措辭類,不算 findings)

| 類 | 命中 | 修改前 → 修改後 |
|---|---|---|
| ② | `[[Projects/圖譜效用受控實驗_計劃]]` 在主線工作樹不存在(它在 graph-vs-code 分支) | related 欄拿掉該連結;正文改成「受控實驗(在 graph-vs-code 分支的 lumos-gvc 工作樹)」不用 wikilink |
| ④7 | 引的紀律範本句子「設計 spec 完成→先過審計 loop」不在檔裡 | 改引第 60 行真正那列「設計 spec 寫完、要進實作前的審查迴圈 → lumos-design-loop」 |

## 語意類命中(修真檔 + 留痕;動到核心裁定的升格為正式 finding 交席位)

| id | 命中 | 重現 | 修改前 → 修改後 | 判 |
|---|---|---|---|---|
| PF-1 | 「風險標籤 538 篇只有 34 篇掛、全是守衛面、金流/對外/不可逆零篇」——d6 決策的論據 | `grep -rl 'risk/' docs/lumos-toolchain-knowledge` → 40 篇;守衛面 29、不可逆 5、金流 2、對外送出 0 → **HIT(宣稱為假)** | 第一節帳面事實段與 d6 改成 40/29/5/2/0;結論改成「稀疏且集中在守衛面」;d6 由 d8 取代 | ★升格 finding:動到核心裁定 d6/d8 的前提;席位請重驗「數字對了之後,預設翻成單向門的論證還站不站得住」 |
| PF-2 | 第五節說推送閘來源是「測試紅那型」,但 hook 對 `code-loop check` 任何 rc=1(缺表態/高風險缺留痕/合約測試紅)都記 | `sed -n 227,234p scripts/hooks/pre-push`(改前)→ 無條件呼叫 → **HIT(程式比 spec 寬)** | hook 收窄成只在輸出含「受波及合約的測試沒過」時才記;spec 第五節明寫排除「缺表態/缺留痕」並給理由 | ★升格 finding:動到逃逸帳語意(d5/d7);席位請判「收窄後會不會反而漏掉該記的」 |

## 編排者自驗

- `python3 scripts/lumos lint 規格落成可驗收條件_計劃` → 0 問題;`bash -n scripts/hooks/pre-push` → OK。
- 收窄那一條沒有自動測試釘住(hook 是 shell、現有測試不跑它)——**列為本輪殘餘,席位可報**。
- 外家否決席缺席(Codex 額度 2026-09-19 21:45 前用罄),五席全同門,本輪證據強度打折。

## 席報告收貨中的編排者重現(r1,收齊前只重現不折)

| 席/條 | 席位的觀察 | 重現指令 | 結果 |
|---|---|---|---|
| 正確性 F1 | 雙向門要寫的四行「已排除:<類>:理由」本身就命中同名關鍵字類,會把自己判回單向門 | 把 PITFALL_CLASSES 四類正則套在四行範例上 | **HIT**:金流→payment、對外送出→external-send、不可逆→prod-irreversible 三/四命中;自我治理不命中(表裡沒有「自我治理」字面) |
| 正確性 F3 | 「40 篇/金流 2」仍是錯的:金流那 2 篇是正文範例不是開頭欄位標籤 | 只掃開頭欄位(`---` 區塊)裡的 `- risk/<值>` | **HIT**:34 篇;守衛面 29、不可逆 5、金流 0、對外送出 0。編排者兩版數字都錯(第一版總數對但「三類零篇」錯;第二版把正文範例當標籤) |
| 正確性 F6 | 收窄後會漏記「tier=high 缺審查留痕」這種最該記的 | (引句錨不到,走佐證通道)`sed -n 235,242p scripts/hooks/pre-push`:只在含「受波及合約的測試沒過」時記 | 觀察屬實;判準留席位收齊後裁(這條跟 PF-2 是同一個張力的兩個方向) |
| 簡化 F1 / 邊界(S12 註) | S4、S12 不合五型任一 | 照第二節五型寫近似正則掃凍結稿條款 | **HIT**:S4「在雙向門的計劃裡,若…則…」複合觸發、S12「在…迴圈上」缺「期間」——spec 自己的條款就過不了自己的句式 |
| 正確性 F2 / 邊界 F2 | 第四類叫「自我治理」,但既有值域是「守衛面」,關鍵字表鍵是 self-governance | `grep -n "_RISK_ENUM = " scripts/lumos` → 4422 行 `{"金流","對外送出","不可逆","守衛面"}` | **HIT**:三套詞彙並存 |
| 邊界 F1 | 29+5+2+0=36≠40 | 算術 | **HIT**:「40」是 `grep -rl 'risk/'` 含正文提及的數;開頭欄位實數 34(見正確性 F3 列) |
| 簡化 F2 / 回滾 F1/F2 | 「已收窄」只做在 push-gate;code-loop 來源只看 severity、CI 來源只看 _CI_RED | 讀 scripts/lumos 6181 與 22321 | **HIT**:三來源只有一個收窄,spec 第五節的宣稱過度 |
| 回滾 F3 | 逃逸帳是 git 追蹤檔,hook 只 append 不 commit,會停在 dirty 狀態 | `git ls-files docs/.escape-log.jsonl`;`git status --porcelain docs/.*log.jsonl` | **HIT**:是追蹤檔;此刻 governance/usage 兩本帳就是 M 狀態 |
| 回滾 F6 | `_jsonl_append_verified` 無鎖,兩來源同時寫可繞過去重 | 讀 6193–6222:`open(path, "a")` 直接 append,無 flock、無 vault 寫入鎖 | **HIT**:寫側無鎖;既有寫側鎖是 `_vault_write_lock`(set/append 用),逃逸帳沒套 |
| 邊界 F4 | run_cmd 沒有 {method} 時「至少一支紅」無法歸因;guard-kill 已有 killed_unattributed 弱證據先例 | `.lumos/config.json`(本 repo 有 {method});scripts/lumos:9499/9505 | 觀察屬實(本 repo 有 {method},消費專案不一定);先例存在 |

## r1 去重對照(載體 findings-set 用的 id → 來源席)

| id | 一句 | 來源席 | 型 | 去向 |
|---|---|---|---|---|
| A1 | 已排除四行自我否決(關鍵字命中同名類) | 正確性 F1 | spec | 折:掃描跳過已排除行 |
| A2 | 句式表過不了自己的 S4/S12;無條件型無排除規則 | 簡化 F1、接手 F3、邊界 註 | spec | 折:一條文法+禁複合觸發+無條件型排除規則 |
| A3 | 風險標籤數字第二版仍錯(40/金流 2) | 正確性 F3、邊界 F1、接手 F1 | spec | 折:34/29/5/0/0,量法寫死;d8→d9 |
| A4 | 四類詞彙三套並存(自我治理/守衛面/self-governance) | 正確性 F2、邊界 F2、接手 F4 | spec | 折:對照表 |
| A5 | 引錯函式(_classify_one→_clause_bindings_for) | 正確性 F4 | spec | 折 |
| A6 | 至少一支紅可被樁測試/同一支測試/空集合繞過 | 正確性 F5、邊界 F5/F6、簡化 F7 | spec | 折:每條新行為各自紅、[keeps]、名互異、零條款擋;樁測試殘餘明寫 |
| A7 | 逃逸來源:推送閘收窄過頭/另兩來源沒篩 | 正確性 F6、簡化 F2、回滾 F1/F2、邊界 F8、接手 F2 | code | 折:三來源篩法定死+push-gate:unreviewed;程式已改(t_escape_auto_scope_rules) |
| A8 | RETIRE-IF 拿雙向門跟單向門比,不對等 | 簡化 F3 | spec | 折:絕對門檻 |
| A9 | 逃逸帳 hook 只 append 不 commit;fail-open 失敗看不見 | 回滾 F3 | code | 折:健檢提醒未提交列;失敗寫治理帳(程式已改) |
| A10 | 寫側無鎖,並行繞過去重 | 回滾 F6 | code | 折:_vault_write_lock(程式已改,t_escape_auto_lock) |
| A11 | RETIRE-IF 的量測工具不存在 | 回滾 F4 | spec | 折:上線順序寫死,S13 前一律單向門 |
| A12 | 回退步驟②沒有錨 | 回滾 F5 | process | 折:tag pre-spec-gate |
| A13 | 訊號 2 走的是合約行掃描不是關鍵字表,要動什麼漏列 | 接手 F5 | spec | 折 |
| A14 | 推送閘「條款全綠」靠 diff 對不回後續推送 | 接手 F6 | spec | 折:改讀 spec-gate 留痕的測試清單 |
| A15 | skill 同步範圍漏 templates/reference/INDEX | 接手 F9 | process | 折 |
| A16 | 兩條 SINCE 疊加順序;door 欄位要登記 | 接手 F7/F8 | process | 折 |
| A17 | spec-gate 留痕要走 cmd_canary 擴 kind | 架構對齊 1 | spec | 折 |
| A18 | 沒回答「light 分級為什麼沒人走」 | 簡化 F8 | spec | 折:第一節與為什麼段補(判準看規模風險面不看 spec 品質、仍要一席) |
| A19 | S14 是 S2 子集 | 簡化 F5 | spec | 折:併入 S2 |
| A20 | 五型對可驗性無增量 | 簡化 F6 | spec | 折:五型改成只是名字,機械只驗一條文法 |
| A21 | 回退節「非空」太鬆 | 邊界 F3 | spec | 折:≥20 字含實字 |
| A22 | run_cmd 無 {method} 歸因不到;guard-kill 弱證據先例 | 邊界 F4 | spec | 折:擋下並印怎麼改 |
| A23 | 計劃路徑存在性沒做 NFC | 邊界 F7 | code | 折(程式已改) |

放行 0;重現不到 0;外家否決席缺席(額度)。
