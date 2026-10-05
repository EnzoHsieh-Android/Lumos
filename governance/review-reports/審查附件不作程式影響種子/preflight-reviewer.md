實際讀取材料：

- `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `scripts/lumos`：`_review_roles`、`_review_role_changed_files`、`_impact_diff_seed_ok`、`_impact_diff_modes`、`_codeloop_raw_changes`、`_codeloop_raw_modes`、`_codeloop_bookkeeping_code`
- `scripts/test_lumos.py`：`t_impact_diff_review_artifacts`、`t_impact_diff_bookkeeping_code_controls`、兩個凍結內容角色案例、file-cap 正面段、`t_review_role_zero_budget_no_git`
- 未讀 `governance/review-reports/` 下任何舊報告。

① 未定義詞

severity: minor  
blocking: 否  
引句:「只排除已知普通非程式附件。程式副檔名、無副檔名腳本與可執行檔保留；無副檔名普通卷證按凍結首行排除，未知或超過既有上限時保守保留」  
file: `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md:24`  
source 函式證據：實作把「未知」拆成模式缺失、首行整批讀取失敗、單一 blob 超限／缺失、特殊字元路徑等不同狀態，且處置分散於 `_impact_diff_seed_ok` 與 `_impact_diff_modes`；計劃沒有定義「未知」包含哪些狀態，也沒有明說「已知普通非程式附件」以 `_nodehome_code_kind`、模式及首行三者如何合取。file: `scripts/lumos:41018`、`scripts/lumos:41041`

② 壞引用

severity: minor  
blocking: 否  
引句:「卷證 root-red.json」「保留 r1-repair-spec-red.json」「卷證 r2-boundary-red.json」「卷證 r2-role-clock-control.json」「r2-zero-budget-red.json」「r2-role-zero-budget-green.json」  
file: `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md:31`  
source 函式證據：`lumos refcheck … --json` 對整篇回 `claims: []`，上述卷證都只有裸檔名，無路徑或可驗錨點；相對地函式、測試名與提交 `ce2a961f`、`ca6701b2` 均可解析。未讀舊報告內容。

③ 範圍矛盾

severity: major  
blocking: 是  
引句:「本變更只共用原有簿記分類，不增減真正測試的執行、通過或阻擋條件」；「修 _review_roles 零預算直接回超時空結果」  
file: `docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md:33`  
source 函式證據：`_review_roles` 新增 `budget <= 0` 的提前返回，並新增專測禁止 Git／選檔；這是角色鏡頭的執行與逾時行為修復，不只是共用簿記輸入分類。file: `scripts/lumos:24391`、`scripts/test_lumos.py:38531`  
最小重現：`git diff --unified=3 ce2a961f -- scripts/lumos scripts/test_lumos.py | rg -n 'budget <= 0|t_review_role_zero_budget_no_git|零預算不啟動 Git'`，實際命中新分支與新測試。這使原先按「只修輸入分類」取得的低風險授權不再涵蓋實際範圍；本次只能算實作後補審前掃。

④ 機械宣稱是否語意相符

已讀，無 finding。兩個凍結內容案例確實各顯式傳 `budget=30`，file-cap 正面段是第三處；預設仍為 3 秒，零預算在任何 Git／選檔前返回。刪檔取舊模式／物件、staged 取索引、超限或讀不到保守保留、角色消費者共用 `_impact_diff_modes` 與 `_impact_diff_seed_ok`，均與源碼相符。

總結：最嚴重 severity: major；blocking: 1 條。
