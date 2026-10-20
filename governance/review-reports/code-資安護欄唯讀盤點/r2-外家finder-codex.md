severity: major

1. 自動找圖譜會跟隨 `docs` 這層的捷徑，讀出 repo 外的 Markdown

severity: major

blocking: 是

歸因:有證據的原有漏查

`_secinv_vault_problem()` 只檢查最終 vault 路徑是不是捷徑；共用 `_vault_in()` 先用 `docs.is_dir()`、`docs.iterdir()` 跟隨了 `docs` 捷徑。之後 `O_NOFOLLOW` 只能保護 vault 內部和路徑最後一段，攔不住已經解析過的上層捷徑。[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:6684>)、[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:28598>)

具體重現：輸入為 `repo3/docs` 指向 repo 外 `outside/docs` 的捷徑，外部圖譜含 `Systems/Secret.md` 與 `SECRET-OTHER-PROJECT-CLAIM`；預期拒讀、退出 2、`read_complete=false` 且輸出不含外部宣稱；實際兩版都退出 0、`read_complete=true`，並把外部宣稱列入 `unclassified_contracts`。

引句:「圖譜目錄 {p} 是捷徑,不跟隨」

同一案例證據：

- claim：圖譜探索不得穿過 repo 內的捷徑讀到 repo 外。
- input/expected/出處：上述 `docs` 捷徑；預期 rc2、不輸出外部內容；出處為設計 S3、讀取邊界，以及 d1「圖譜內任何捷徑都算錯誤退出 2」。
- case_source：本席補的讀取邊界案例。
- before 命令：在 `.../資安-sonnet/v2/repo3` 執行 `python3.14 .../r2-通才-before/scripts/lumos security list --json`。
- before 結果：rc0；`read_complete=true`；`unclassified_contracts=[{"node":"Systems/Secret.md","claim":"SECRET-OTHER-PROJECT-CLAIM",...}]`。
- after 命令：同目錄執行 `python3.14 .../r2-通才-after/scripts/lumos security list --json`。
- after 結果：與修前相同，rc0 且讀出外部宣稱。
- comparison/attribution：同一漏洞修前、修後皆成立，因此是有證據的原有漏查，不是修補回歸。

2. 指向 Systems 的證據引用被標成 `references_valid=true`，仍可把入口顯示成 mapped

severity: major

blocking: 是

歸因:有證據的原有漏查

schema 明定 `evidence_refs.node` 必須是 Verification 節點；但 `_secinv_evidence()` 對 Systems 節點只加入 `not_verification` issue，沒有產生 `reference_error`。修後 `_secinv_check_row()` 因而把它標成 `references_valid=true`，rc0、`registration_complete=true`，並計入入口映射。[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:6989>)、[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:7332>)

具體重現：輸入為合法 inventory 的 `S-refund`，唯一 active security 控制項 `WRONG-NODE` 的 `evidence_refs=[{"kind":"behavior","node":"Systems/SlPay.md"}]`；預期該引用失效、退出 2、`references_valid=false`、入口 unmapped；實際兩版都退出 0、入口 mapped。修後更明示 `references_valid=true`。

引句:「這一條自己記下的引用錯誤決定 references_valid(覆蓋只採計通過的)。」

同一案例證據：

- claim：非 Verification 的 evidence reference 不得算通過引用核對或消除入口缺口。
- input/expected/出處：3 篇記憶體快照，控制項證據指向 `Systems/SlPay.md`；預期 rc2/unmapped；出處為 schema 的 evidence_refs 定義、計劃 d3，以及 Systems 節點「引用失效不消除缺口」。
- case_source：本席補的壞節點類型案例。
- before 命令：`python3.14 -c 'runpy.run_path(".../r2-通才-before/scripts/lumos"); 以該三篇 snap 呼叫 _secinv_build(...)'`。
- before 結果：rc0、`registration_complete=true`、`evidence_check=incomplete`、issue=`not_verification`，但 `state=mapped`、`mapped_control_ids=["WRONG-NODE"]`。
- after 命令：同一 harness 改載入 `.../r2-通才-after/scripts/lumos`。
- after 結果：rc0、`registration_complete=true`、`references_valid=true`、`state=mapped`。
- comparison/attribution：修前已錯誤映射；修後的新 references_valid 判定仍漏掉 `not_verification`，故為有證據的原有漏查。

3. 修補新增的 `invalid_reference_control_ids` 只出現在 JSON，文字盤點漏列

severity: major

blocking: 是

歸因:有證據的修復回歸

修補在每個 surface 新增 `invalid_reference_control_ids`，但 `_secinv_render_coverage()` 的固定欄位清單沒有加入它。相同盤點的文字與 JSON 因此不再是同一份資料；文字使用者看得到 unmapped，卻看不到哪些已登記控制項因引用失效而被排除。[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:7280>)、[scripts/lumos](</tmp/lumos-seat-work/code-資安護欄唯讀盤點/r2-通才-after/scripts/lumos:7416>)

具體重現：輸入為 `S-refund` 的 active security 控制項 `BADREF`，其 `source.decision_ref=Systems/SlPay#d9` 不存在；預期修後 JSON 與文字都列 `invalid_reference_control_ids=["BADREF"]`；實際修後 JSON 有該欄，文字 coverage 完全沒有。

引句:「invalid_reference_control_ids,但不消除入口缺口」

同一案例證據：

- claim：文字與 JSON 必須保留同一份入口缺口資料。
- input/expected/出處：無效來源決策的 `BADREF`；預期兩種輸出都列失效控制項 ID；出處為 CLI「文字與 JSON 同一份資料」契約及 d3。
- case_source：intake G3 repair 案例加本席的文字／JSON parity 檢查。
- before 命令：以 `runpy` 載入 `.../r2-通才-before/scripts/lumos`，對同一 snap 執行 `_secinv_build()`、`_secinv_render()`。
- before 結果：rc2，但錯誤地 `state=mapped`、`mapped_control_ids=["BADREF"]`；JSON 與文字都沒有 `invalid_reference_control_ids`。
- after 命令：同一 harness 載入 `.../r2-通才-after/scripts/lumos`。
- after 結果：JSON 正確變成 `state=unmapped`、`invalid_reference_control_ids=["BADREF"]`；文字只印 `state=unmapped mapped_control_ids=[] ... unclassified_control_ids=[]`，遺漏失效 ID。
- comparison/attribution：G3 的核心映射錯誤確實修好，但修補新增 JSON 欄位時未同步文字 renderer；這個 parity 缺陷只在修後成立，屬有證據的修復回歸。

三問回答：

1. 原問題的修復效果：已獨立證實 G3 的無效來源案例由修前 `mapped` 變成修後 `unmapped`，JSON 也新增失效控制項 ID；但文字輸出沒有同步。其餘 G1–G9 未因作者測試通過就視為已驗。
2. 正常、錯誤與相鄰路徑：正常合法控制項 `GOOD` 兩版均 rc0、`registration_complete=true`、`state=mapped`、`evidence_check=declared_only`、`security_verdict=not_assessed`；repo 自身零登記案例兩版均 rc0、`registration_complete=false`，文字明示「未登記/無法判定」；錯誤與相鄰路徑則有上述三項缺口。
3. 新發現的兩版結果：Finding 1、2 在兩版都失敗，屬原有漏查；Finding 3 的底層 G3 行為修後改善，但文字／JSON 分裂只見於修後，屬修復回歸。

證據限制：指定的 `code-seat-common.md` 絕對路徑不存在，且搜尋暫存區與 repo 均無同名檔；正式 `test_lumos.py -k seclist_g` 也因本席唯讀 sandbox 沒有可寫暫存目錄而在測試隔離初始化前失敗。因此以上正向主張只限已實跑的固定案例，不構成整體無回歸保證。

最嚴重 severity: major；blocking 共 3 條。
249,753
