severity: major

**一、分層與依賴方向**

新函式的擺放與呼叫方向整體對齊既有慣例:純函式(`_clause_grammar`/`_clause_body_of`/`_rollback_section_chars`/`_clause_structure_verdict`/`_clauses_grammar_bad`)在前,`_clause_check`(讀-判)其次,再往下是 env-wrapping 的 `_spec_gate_*` 系列與 `cmd_spec_gate`,最後才接 argparse/main() dispatch——這跟鄰居 `clause_bindings`(純函式)→`_clause_bindings_for`(env 包裝)→`_disposal_clause_step`(呼叫端)的三層排法一致,呼叫方向單向、看不到 cmd_* 或 argparse 層被下層直呼。file: `scripts/lumos:4751`(`_clause_check`)對照 `scripts/lumos:4407` 一帶（`clause_bindings`/`_clause_bindings_for`）。`cmd_ci_wait`/`_ci_record`→`_ci_red_escape`→`_auto_escape`、`cmd_canary`→`_auto_escape`、`cmd_loop_escape --auto`→`_auto_escape` 三個呼叫端共用同一支底層函式,也沒有繞層直呼 `_jsonl_append_verified` 以外的寫入原語。

但有一處明確的跨層取代,而不是延伸既有介面:`_spec_gate_load` 找節點沒有走全專案唯一的節點解析路徑。`Env.__init__`(`scripts/lumos:399` 一帶,`self.resolve = make_resolver(...)`)保證每個 `Env` 實例永遠有 `resolve` 屬性,但 `_spec_gate_load` 卻寫成：

引句:「p = env.resolve(node) if hasattr(env, "resolve") else None」

這個 `hasattr` 判斷是死碼(condition 恆真),而且 `env.resolve` 本身語意是「解 `[[連結]]` target」(給 `link_target()` 後的字串用,例 `scripts/lumos:1747`/`10294`),不是「找 CLI 引數指名的節點」。全專案其餘每一個吃 `node`/`--note` 引數的 cmd_*(`cmd_spec_trace` 就在旁邊,`scripts/lumos:5165`;還有 `9496`/`9581`/`9669`/`9875`/`10106`/`10161`/`27966` 等十餘處)一律走 `rel = env.find(node)`,找不到就呼叫 `_node_not_found(env, node)`(`scripts/lumos:8821`,印近名候選 + `lumos search` 提示)。`_spec_gate_load` 另開一條路:先試 `resolve`、再退回手拼 `env.vault / (node+".md")`,找不到只印一句「擋下:找不到計劃節點 {node}」,沒有近名建議、沒有 search 提示,錯誤訊息形狀也跟鄰居不一樣。

severity: major

**二、命名與錯誤處理**

常數命名對齊:`_SPEC_GATE_SINCE` 跟既有 `_CLAUSE_GATE_SINCE`/`_LANDING_GATE_SINCE`/`_SECURITY_SEAT_SINCE` 同一組「`_XXX_SINCE`」命名與註解寫法(講清楚哪個計劃、為什麼不回溯)。file: `scripts/lumos:4744`一帶。印法前綴 `[spec-gate]` 是仿 `[disposal]` 用同一支 `_clause_check` 靠 `tag` 參數產生 `f"[{tag}] 條款綁定:"`,不是另開一套字串拼法;擋下訊息延續「發生什麼→為何在意→指令獨立一行」三段式,例如相依回歸擋下那段先講「幾支沒過」、再講「相依功能的合約測試要全綠才算驗收」、再獨立一行給下一步指令。例外處理上,`except Exception as _e:   # 健檢一段壞了不能拖垮整份;標題寫「不擋」就只准 warn_soft`(doctor S12 段)與 `except Exception as _ex:   # 掛勾不准弄壞記帳`(`cmd_canary` 的逃逸掛勾)都跟既有 fail-open 慣例(例如 `# 觀測絕不擋閘:任何意外只降級為警告`)同一種「寬 except + 中文一句話講清楚為什麼不能讓它炸」寫法,沒有偷改成靜默吞掉或改變擋/不擋的既有語意。

不對齊的地方:

引句:「per_prof = lambda plat: (plats.get(plat) or {}).get("profile_name")   # noqa: E731」

`scripts/lumos:5137`。這是全檔唯一一處 lambda 指定帶 `# noqa: E731` 註解;檔內至少 7 處同型「名字 = lambda …」寫法(`scripts/lumos:3103`/`3106`/`3193`/`5433`/`5447`/`6062`/`12082`/`12086`)都沒有這個註解,是既有 idiom 卻多長了一個獨有的 lint 抑制標記,風格不一致(不影響行為)。

severity: minor

⚠ 這批 diff 順手把 `_node_not_found`(`scripts/lumos:8850` 一帶)與 `cmd_about_code_revert` 兩處 `except Exception:` 後面的 `# noqa: BLE001` 註解拿掉,跟規格閘本身無關,判不準是 lint 設定變動還是誤帶的無關改動,不列入計數。

**三、第二種做法**

找節邏輯的第二套做法已在第一問列出(`_spec_gate_load` vs `env.find`/`_node_not_found`),不重複計 severity。

另一處獨立的第二種做法:

引句:「m = INVARIANT_RE.match(ln) or CHECKPOINT_RE.match(ln) or IRREVERSIBLE_RE.match(ln)」

`scripts/lumos:4955`(`_contract_texts`)。這跟既有 `_lens_contract_lines`(`scripts/lumos:24750`)與 `_lens_contract_rows`(`scripts/lumos:24768`)是同一件事的第三套實作——三支函式做的都是「逐行掃 `INVARIANT_RE`/`CHECKPOINT_RE`/`IRREVERSIBLE_RE`,抓 KEY 合約行」,`_lens_contract_lines`/`_lens_contract_rows` 已經是相鄰兩支各自處理「截斷顯示」與「分類」的版本,`_contract_texts` 沒有重用其中任一支(哪怕只是加個「回 group(1) 而非整行」的參數),而是照抄邏輯再寫一次。

severity: major

其餘查核過、確認沒有第二種做法的地方:支數解析新增 `count_re` 欄位是掛在既有 `_RAN_EVIDENCE` dict 上(`scripts/lumos:25650` 一帶擴充,不是另開新表)；治理帳事件 `_append_governance_log(env.vault, [{"gate":…, "kind":…, "hard":…, "nodes":…, "note":…}])` 沿用既有五鍵形狀,`spec-gate-run`/`escape-auto-failed` 都沒有另開欄位集合；測試新夾具 `_mk_spec_gate_repo` 雖然跟 `_mk_bound_tests_repo` 的假測試執行器輸出格式不同,但那是因為要驗的是全新的「支數解析」(`_ran_count` 讀「lumos 測試(N 案例)」)而不是既有的紅綠判定,兩支假執行器驗的是不同機械行為,不算重複;`per_prof` lambda 賦值本身是既有 idiom,不算第二種做法(已在第二問列風格不一致)。

一處待觀察但不升 severity 的半成品:

引句:「def _clause_check(text, rows_b, grammar=True, door="one-way", tag="disposal"):」

`scripts/lumos:4751`,兩處呼叫(`4995`/`16223`)都硬寫 `door="one-way"`,而函式體內從頭到尾沒有任何一行讀 `door` 這個參數——全檔 `grep door` 只在定義與兩個呼叫點出現字面值。這不是「第二種做法」,是介面先開好、行為還沒接上的半成品參數,容易讓下一個讀者誤以為 `door` 真的分流了行為。

severity: minor

**四、落點與測試**

落點對齊:`Projects/規格落成可驗收條件_計劃.md` 的 `lands_in: [Systems/design-loop, Systems/規格閘]` 指到兩篇既有節點,符合「每支檔有家」——新程式落在既有家,沒有另開無主節點或把 `scripts/lumos` 這支已有多篇家的檔改成單篇獨佔。測試命名延續既有 `t_<主題>_<情境>` 寫法,每支 docstring 都標明對應條款編號(`[規格落成可驗收條件 SN]`)並附「翻紅釘」段落,跟鄰居(如 `t_never_create_dirs_under_an_untrusted_path`、`t_arm_dir_chmod_must_not_follow_a_symlink`)同一種「出身+翻紅釘」寫法一致。新夾具 `_esc_auto_repo`/`_esc_rows`/`_mk_spec_gate_repo` 都沿用既有 `_mk_git_vault`/`_sha256_of`/`run()`/`check()`,沒有另開一條測試執行管線;`_mk_spec_gate_repo` 回傳 `(d, kg)`、`_esc_auto_repo` 回傳 `(root, vault, plan)`,雖然跟 `_mk_bound_tests_repo`(只回 `d`)形狀不同,但這是同一批新增夾具彼此一致(都回多元組給呼叫端拆),屬各自表述自己需要什麼、不構成不一致,不列 finding。

不對齊共 4 條,其中 major 2 條。
