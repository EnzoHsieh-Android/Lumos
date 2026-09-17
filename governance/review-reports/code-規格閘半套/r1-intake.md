preflight-4: ran

# code-規格閘半套 r1 收貨紀錄

- 凍結 patch r1-snapshot.patch(-U10,2813 行,指紋 bd9d35b790b778a9;超過 1800 行,單席仍一人審,帳上會標範圍過大)。標準分級:單席循序+架構對齊;外家席缺席(Codex 額度)留痕。
- 兩席報告從逐字稿抽最終回覆存檔;單席第 9 條原寫 `severity: ⚠`,請該席重傳只改成合法值(其餘一字未動)。`report-normalize --write`;quote-check 對回 patch 兩席全數錨定;refcheck ok;seat-check 派工單沒列材料(vacuous)。

## 編排者重現
- **X1 短名找不到**:`lumos spec-gate 規格落成可驗收條件_計劃 --no-run` → 「擋下:找不到計劃節點」rc2(席位重現、我再跑一次)→ HIT。
- **X2 複合觸發誤判**:`_clause_grammar("當收到請求,在三秒內系統應回 200")` → (False, 複合觸發)→ HIT。
- **X3 lands_in 字串被丟**:`_plan_system_links` 對 `lands_in: Systems/Alpha`(字串)回 [] → HIT。
- **X5 合約行掃描第三套**:`_lens_contract_lines`/`_lens_contract_rows`/`_contract_texts` 三支同一組正則 → HIT。
- **X4 Setext**:`_rollback_section_chars("回退\n----\n…")` → None → HIT(設計寫死只認 ##,放行)。

## 去重對照(X1–X7)
| id | 內容 | 席 | 嚴重度 | 型 | 處置 |
|---|---|---|---|---|---|
| X1 | spec-gate 用短名叫節點失靈;沒走 env.find/_node_not_found | 單F1、架構§1 | major | code | 折:走 env.find,找不到印近名提示;釘① |
| X2 | 回應段「在…」當介詞被判複合觸發 | 單F2 | major | code | 折:複合=回應段自己又是「觸發詞…分隔」;釘② |
| X3 | lands_in 是字串時靜默丟掉 | 單F3 | major | code | 折:as_list;釘③ |
| X4 | 回退節不認 Setext 標題 | 單F4 | minor | code | 放行:設計寫死只認 ATX 二級,計劃第二節已明寫 |
| X5 | _contract_texts 是合約行掃描第三套 | 架構§3 | major | code | 折:收斂成 _contract_key_matches,鏡頭與相依回歸共用;lens 213 條測試綠 |
| X6 | lambda 多了獨有的 noqa E731 | 架構§2 | minor | code | 折:拿掉 |
| X7 | _clause_check 的 door 參數沒人讀 | 架構§3 | minor | code | 放行:第二階段保留,計劃第四節已寫「參數先留著」 |
單席 5–8、10 是「已讀無 finding」的核對、9 是 ⚠ 抑噪,不列。架構席順手點到的 noqa BLE001 移除是 lint 規則沒啟用該碼(RUF100),不是誤帶。
