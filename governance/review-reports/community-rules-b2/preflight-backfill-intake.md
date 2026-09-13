preflight-4: ran

# 補跑的首輪前置掃描（community-rules-b2）

一句話說明：這是 2026-09-13 事後補跑的，原本那一輪沒跑。設計稿描述的機制已經寫成程式了，所以本次掃描直接開 scripts/lumos 與 scripts/test_lumos.py 對照設計稿逐句核對。

## ① 未定義的詞

沒命中。稿子裡用到的內部用語（散文→規則產線、逃逸帳、樣本、閉環、菜單…）都在條款 S1–S8 或誠實邊界段落裡有功能性說明；前置欄位（FLAG/KEY/DEP/TEST/lands_in）是這個知識圖譜的通用格式，非本稿自創術語。

## ② 壞引用

沒命中。逐一查證如下：

- `.lumos/lint-deps.json` → scripts/lumos:17602 `_LINT_DEPS_REL = ".lumos/lint-deps.json"`，存在。
- `.lumos/rules/`、`.lumos/rules/samples/`、`.lumos/rules/index.json` → scripts/lumos:17198（`_rules_index_path`）、17253（`_rules_declared_ids` 掃 `.lumos/rules/` 底下且跳過 `samples`）皆對得上。
- 函式 `_is_dep_manifest`（17624）、`_lint_new_cmd_targets`（17688）、`cmd_rule_check`（17287）、`cmd_rule_gap`（17358）、`cmd_loop_escape` 的 `rule` 欄位（7364 開始的函式簽名含 `rule=None`，7459 `rec["rule"] = rule.strip()`）——五個全部存在，拼寫正確。
- 指令 `lumos rule-check`（scripts/lumos:27586 註冊子指令）、`lumos rule-gap`（27590）、`lumos loop escape --rule`（27226 `--rule` dest=`esc_rule`，28023-28025 派發時傳入 `rule=args.esc_rule`）——三個指令與旗標全部存在且串接完整。
- 測試名 t_lint_deps_layer / t_lint_cmd_targets / t_lint_cmd_targets_applied / t_rule_check / t_rule_id_scanning / t_rule_hit_matching / t_rule_gap / t_rule_gap_robust / t_escape_rule_field——用 `grep -n "def <名字>\b"` 逐一核對，九支全部存在於 scripts/test_lumos.py，數量與命名完全對上。
- 節點連結 `[[Projects/社群規則覆蓋每次提交_計劃]]`、`[[Projects/新增告警閘_計劃]]`、`[[Systems/pitfalls-lint-adapter]]`、`[[Systems/linter精選目錄]]`、`[[Systems/pitfalls-code-loop]]`——用 `ls` 核對檔案全部存在於 docs/lumos-toolchain-knowledge/{Projects,Systems}/。
- 卷證路徑 `governance/review-reports/community-rules-b2/`——存在，內含 r1-通才.md／r1-邊界可執行.md／r1-架構對齊.md／r1-dispatch.json／r1-intake.md／r1-materials.md／r1-snapshot.md／r1-code.patch，跟稿子「三席／16 條」的敘述對得上（外家席缺席，確實只有三份審查稿）。

## ③ 範圍自相矛盾

命中 1 條，而且同一個矛盾重複出現在兩處前置欄位：

- **前置 KEY 行（第 18 行）**：「★依賴宣告檔要自己走一路★……宣告用 `lint.json` 的保留鍵 `deps`（不是副檔名），命中條件=這次改動碰到任何一支依賴宣告檔」
- **前置 DEP 行（第 23 行）**：「`.lumos/lint.json` 的 `deps` 保留鍵」
- 兩者都說依賴層的宣告是塞進 `.lumos/lint.json` 底下一個叫 `deps` 的保留鍵。
- 但正文 **[S1]**（第 41 行）明講的是完全相反的設計：「依賴層的命令寫在 `.lumos/lint-deps.json`（形狀是一個 `cmds` 清單），**不塞進** `.lumos/lint.json`——那個檔的每個頂層鍵都被當成『副檔名→命令清單』嚴格驗證，混一個保留鍵進去等於同一個檔兩種語意」。
- 程式碼與測試都站在 S1 這邊，跟兩處前置欄位矛盾：`_LINT_DEPS_REL = ".lumos/lint-deps.json"`（scripts/lumos:17602）是獨立檔案；`t_lint_deps_layer`（scripts/test_lumos.py）寫的也是 `(root / ".lumos" / "lint-deps.json").write_text(...)`，從沒碰過 `lint.json` 的 `deps` 鍵；`_lint_new_config` 的註解（scripts/lumos:17714）甚至又重申一次「★不放 .lumos/lint.json★」。
- 結論：這是舊版設計殘留在前置欄位裡沒有跟著 S1 定稿改掉的典型漂移——KEY 行與 DEP 行需要改成「宣告放 `.lumos/lint-deps.json` 自己的檔（不進 `.lumos/lint.json` 的保留鍵）」，否則下一個只看前置摘要不看正文的讀者會查錯檔案。

## ④ 機械宣稱驗語意

8 句逐條核對如下（S1–S8 各驗一句代表性宣稱，全部對得上）：

1. 「依賴層的命令寫在 `.lumos/lint-deps.json`（形狀是一個 `cmds` 清單），不塞進 `.lumos/lint.json`」
   → scripts/lumos:17602-17651（`_LINT_DEPS_REL`、`_lint_deps_load`：讀 `.lumos/lint-deps.json`，要求 `cmds` 是清單）。
   → 對得上（程式行為與這句一致；但如上一節所述，前置欄位跟這句自相矛盾）。

2. 「要看目錄不是只看檔名：第三方或產生出來的目錄（`node_modules/`、`vendor/`、`Pods/`、`build/`…）裡的宣告檔不算這個專案的依賴改動」
   → scripts/lumos:17617-17632（`_DEP_EXCLUDE_DIRS` 含 node_modules/、vendor/、Pods/、build/ 等；`_is_dep_manifest` 先比對排除目錄再認檔名）。
   → 對得上，且 `t_lint_deps_layer` 實測 `node_modules/foo/package.json`、`vendor/bundle/Gemfile.lock`、`Pods/X/Podfile.lock`、`build/package.json` 都回 False。

3. 「而且要收『人／AI 真正會編輯的宣告檔』不是只收自動產生的鎖檔（捏造版本號改的是 `Podfile`／`Package.swift`／`mix.exs`，不是 `.lock`）」
   → scripts/lumos:17612-17614（`_DEP_MANIFESTS` frozenset 明確含 `"Package.swift", "Podfile", "mix.exs"`，並附註解說明這是 r1 通才席抓到的漏）。
   → 對得上。

4. 「每條命令只拿自己那個棧的檔……依賴掃描只拿依賴宣告檔」
   → scripts/lumos:17688-17710（`_lint_new_cmd_targets`：按副檔名分組 `by_ext`，逐副檔名配對命令；`dep_pairs` 另外只餵 `dep_cmds`）。
   → 對得上。

5. 「上一條要守到消費端，不是只守配對函式……假檢查工具把自己收到的檔名寫進記錄檔」
   → scripts/lumos:18168-18172（`_lint_new_verdict` 消費 `cmd_targets` 時 `targets = [files[f] for f in want_files if f in files]`，只把該給的檔傳進命令）＋ scripts/test_lumos.py 的 `t_lint_cmd_targets_applied`（假腳本把收到的檔名寫進 `got.txt`，斷言 Python 命令只收到 `.py`、Kotlin 命令只收到 `.kt`）。
   → 對得上，而且測試手法（記錄檔）跟稿子描述完全一致。

6. 「`lumos rule-check` 跑規則對它自己的樣本，不翻紅就擋」＋「同時掃規則檔宣告的規則 id」
   → scripts/lumos:17287-17356（`cmd_rule_check`：對 `mapping` 每個 rule 執行對應命令跑樣本、解析 SARIF，沒命中就列進 `problems`，有 `problems` 回傳 1）＋ 17253-17277（`_rules_declared_ids` 真的掃規則檔內容找 id，並在 17311 附近比對索引有沒有漏登）。
   → 對得上。另外驗到 S4 提到的「不能用字尾比對」修正：scripts/lumos:17337-17339 明確只認「完全相同」或「以點分隔最後一段相同」，並附註解說明這正是 r1 抓到的問題（`xyz-no-bad` 不會假通過 `no-bad`）。

7. 「記逃逸帳時帶規則 id（真的沒有對應規則就寫 `none`）；`lumos rule-gap` 把『標了該抓、但規則還沒寫』列成待辦，附漏過幾次」
   → scripts/lumos:17358-17414（`cmd_rule_gap`：`rid == "none"` 或空字串算 `unlabeled`；`missing = {k: v for k, v in counts.items() if k not in have}`；輸出裡帶 `漏過 N 次`）。
   → 對得上。`t_rule_gap_robust` 也驗了非字串 `rule` 欄位、壞 JSON 行的容錯降級。

8. 「逃逸帳的欄位要真的寫進去。旗標、記錄欄位、分派三處都要接上」
   → 旗標：scripts/lumos:27226（`--rule` dest=`esc_rule`）；記錄欄位：7459（`rec["rule"] = rule.strip()`，且 7414 `--list` 模式也會顯示「本來該抓的規則」）；分派：28023-28025（`cmd_loop_escape(... rule=args.esc_rule)`）。
   → 對得上，三處都串起來了。

9.（S7/S8 補驗，非逐句但同樣是機械可查的宣稱）「跨語言的社群規則庫與依賴掃描……見 `Systems/pitfalls-lint-adapter`」＋ gapfill skill「能寫成規則的就寫成規則」
   → docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md 第 185-194 行確實新增了社群規則庫（semgrep）與依賴掃描（OSV-Scanner，標「未實跑」）一節；skills/lumos-pitfalls-gapfill/SKILL.md 第 35-38 行第 6 步確實把出口改成「模式比得出來的寫規則+樣本，比不出來的才只寫筆記並附理由」。
   → 對得上。

9 句（含 S7/S8 補驗共 9 條檢查點）全部對得上，稿子的機械宣稱沒有語意落差。

## 這次掃描的天花板

- 沒有真的去裝 semgrep／OSV-Scanner 跑一次端到端，只驗證了程式邏輯與測試斷言；稿子自己也承認「依賴掃描器沒有實跑過」，這點誠實邊界與我查到的事實一致，沒有另外去補這個缺口。
- r1 審查稿（r1-通才.md／r1-邊界可執行.md／r1-架構對齊.md）的具體條數、內容細節沒有逐條讀完比對「16 條全部折入」是否真的每一條都對得上程式改動，只確認了卷證檔案存在、篇數與稿子敘述（三席、外家缺席）一致。
- 沒有跑 `python3 scripts/test_lumos.py -k rule` 等實際測試指令去確認這些測試現在真的是綠的——只讀了測試原始碼確認斷言邏輯與稿子描述一致，沒有執行驗證目前是否翻紅。
- 逃逸帳的「三處都要接上」只查了程式碼路徑（旗標/記錄/分派），沒有另外找一支端到端測試專門斷言這三處串起來（`t_escape_rule_field` 存在但內容沒有細讀是否真的涵蓋三處，只信了函式名稱與程式碼互相印證）。
