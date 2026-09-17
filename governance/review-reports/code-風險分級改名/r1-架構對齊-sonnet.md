severity: major

## F1
severity: major
blocking: yes

`_pitfall_plan_light`(`_pitfall_tier` 的分支)在 pitfalls 這支明文宣告「vault-free」的指令裡,自己 `find_vault` + `Env(vault)` 載整份圖譜,跟這支指令原本的設計不一樣、也跟同一個 hot path 上鄰居(`delguard_check`)的做法不一樣。

引句:「先用便宜的前置(審查帳裡有沒有全靠人驗的風險低留痕)決定要不要載入圖譜——pitfalls 在 pre-push 熱路徑上,圖譜載入要幾秒。」

引句:「vault = find_vault(Path(repo_root))」

file: `scripts/lumos:22249-22265`(`_pitfall_plan_light`);呼叫鏈 `scripts/lumos:22377`/`22441`(`_pitfall_diff_collect` 兩個 return 分支都呼叫 `_pitfall_tier` → 命中時呼叫 `_pitfall_plan_light`)。

為什麼算「寫法跟既有的不一樣」而不是風格偏好:
1. pitfalls 是本檔明文宣告的 vault-free 指令,有兩處獨立來源都這樣講——CLI help `scripts/lumos:29547`「實務隱患提問(vault-free)」,以及圖譜節點 `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:115`「`cmd_pitfalls`:三模式…vault-free、詞表自帶」。這是它的身分,不是隨口一句。
2. pitfalls 在本檔自己的註解裡也承認代價:`scripts/lumos:22493` 附近那句「實測 pitfalls 0.18s / impact 4.7s」——工具鏈原本刻意讓 pitfalls 留在 pre-push 熱路徑上是因為它便宜,`Env(vault)` 走的是 `load_vault` 整份解析(`scripts/lumos:401`),量級跟 impact 同一個等級,不是 delguard 那種輕量掃描。
3. 同一份 pre-push 熱路徑上已經有一個「要不要碰圖譜」的先例——`cmd_delguard_check`(`scripts/lumos:21994`)。它也需要圖譜位置,做法是只呼叫 `find_vault` 拿路徑做字串比對與 grep,★不建 `Env`、不解析全部筆記★,還特地寫死 15 秒 deadline、逾時自動降級 fail-open。這批新加的 `_pitfall_plan_light` 沒有這條防線:`find_vault` 之後一旦前置條件(帳裡有 `"manual_only": true`)成立,就直接 `Env(vault)` 整份載入,沒有 timeout、沒有降級路徑,只用一個籠統的 `except Exception` 接住失敗(讀不動時悄悄回 `standard`,不是「vault-free 但偶爾降級」的語意,而是「這條路徑本來就不該進來卻進來了」)。
4. 觸發面不是理論上的——pre-push 每次都會跑 `pitfals --diff --no-lint --json`(`scripts/hooks/pre-push:210`),`--no-lint` 對應 `_pitfall_diff_collect` 裡 `config is None` 的那個 fallback 分支(`scripts/lumos:22366-22380`),這個分支現在也接進了 `_pitfall_tier`。換句話說:任一支風險低、全靠人驗的計劃留過規格閘之後,接下來★每一次★推送只要沒命中 claims、且改到至少一支程式檔,就會在 pre-push 的常駐路徑上載一次全圖譜——不是一次性的邊界情境。

跟既有寫法對照:本檔對「要不要在熱路徑上碰圖譜」這件事已經有一套講法——便宜先做、貴的要嘛不做要嘛帶降級/timeout(delguard 是後者,pitfalls 原本的設計是前者:乾脆不碰)。這批選了第三種寫法:貴的東西直接做,只用一個字串前置擋一下頻率,不擋量級,也沒有更新「vault-free」那兩處宣告(CLI help 與 `pitfalls-code-loop.md`)去承認例外。

## F2
severity: minor
blocking: no

`_nodehome_code_kind`(`每支檔有家` 節點 `about_code` 列的函式,家在 `scripts/lumos` 那一段)這批被小改動閘(`_sc_diffusion`)與改動風險分級(`_pitfall_tier`)借用,但它的家節點 `docs/lumos-toolchain-knowledge/Systems/每支檔有家.md` 的 DEP 行只列了「三個進入點」(提交前/推送前/健檢),沒提到 `_pitfall_tier`/`_sc_diffusion` 這兩個新消費者。

引句:「code = [f for f in files if _nodehome_code_kind(f[0]) is not None]   # 擴散與落點只算需要有家的程式檔;文件/圖/資料只在相對量那一維度算(2026-09-18:README+圖把目錄數撐破)」

file: `scripts/lumos:5660`(`_sc_diffusion`)、`scripts/lumos:22240`(`_pitfall_tier`)、`docs/lumos-toolchain-knowledge/Systems/每支檔有家.md:60`(DEP 行只列三個進入點)。

這不算「另刻一份工具函式」——這批正確地重用了既有判定(`_nodehome_code_kind`),避免第二套副檔名清單漂移,符合本檔一貫的「單一源」慣例(參照 `scripts/lumos:18409` 附近的「兩個消費者…都走這一支,別各自抄」講法)。只是家節點的 DEP 行沒跟著補,不是這批寫法本身有問題,列為 minor、不擋。

## 對照過、沒發現問題的地方(逐項)

- **legacy 相容表寫法**:`_PLAN_RISK_LEGACY = {"one-way": "high", "two-way": "low", "high-risk": "high", "low-risk": "low", "high": "high", "low": "low"}` + `_plan_risk_norm`/`_rec_plan_risk`/`_note_plan_risk_flag` 三層讀取,跟本檔既有「舊欄位相容 + lint 只給軟提醒不升 error」的慣例一致(對照 `door` 欄位原本的 lint 處理與 `_KNOWN_FRONTMATTER_KEYS` 的軟提醒設計,`scripts/lumos:4484` 附近)。lint 訊息「door 是舊寫法(2026-09-17 改名),改成 plan_risk: high(舊值仍讀得懂)」跟同一段裡未知欄位提醒的語氣、句式一致。
- **`find_vault` 在 main/hook 端的既有用法**:main() 建 `Env` 一律先 `find_vault(Path.cwd())`(`scripts/lumos:15474`/`24722`/`29913` 等)再整份載入,這是「使用者主動下指令、預期要碰圖譜」的路徑;`_pitfall_plan_light` 的問題不是「find_vault 這個 helper 用錯」,是用在了一支宣告不碰圖譜的指令內部(見 F1)。
- **函式加布林旗標(quiet/record_escape)vs 本檔「同一支函式兩種模式」慣例**:`quiet=False` 這個形狀在本檔已有先例——`_panel_round_conjuncts(recs, quiet=False)`(`scripts/lumos:7582`)、`_rel_cascade_pending(header, trans, quiet=True)`(`scripts/lumos:13950`)、`_reinject_all(root, slug, quiet=False)`(`scripts/lumos:14875`)。`_spec_gate_push_scan(..., quiet=False)` 與 `_spec_gate_push_one(..., record_escape=True)` 跟這個形狀一致,不是新做法。`_spec_gate_push_scan` 回傳形狀從 `bad` 改成 `(bad, oks)`,兩個呼叫端(`_spec_gate_push_check`/`_spec_gate_push_report`)都同步改了拆包方式,沒有漏改的呼叫端。
- **`tier_reason` 欄位命名**:本檔已有 `<欄位>_reason` 的先例(`not_run_reason`、`intent_unavailable_reason`,`scripts/lumos:27228`/`28758`),不是孤例新造詞;跟另一批更常見的裸 `"reason"` 欄位(單一輸出物件裡只有一種 reason 時用)是兩種各自成立的既有寫法,`tier_reason` 用在「一個物件裡有多個可能需要理由的欄位」的情境下選了跟 `not_run_reason` 同一種,合理。
- **pre-push 註解改名跟 lumos 端用語一致性**:pre-push 這批全部改成「風險低/風險高」+「(不)派設計審」,跟 `scripts/lumos` 側 `_spec_gate_print_door`("計劃風險: 低/高")、S14 健檢區("風險低計劃放行"/"風險高計劃")、`_pitfall_tier` 相關訊息用的詞面一致,沒有兩邊各自叫不同名字的情形。
- **`INV_TAG_RE` 註解、`_clause_check`/`_spec_gate_*` 系列函式改名**:純文案改名(`雙向門`→`風險低`、`單向門`→`風險高`),邏輯分支條件同步從 `== "two-way"` 改成 `== "low"`,沒有漏改的分支(逐一核對 `_clause_check`、`_spec_gate_front`、`cmd_spec_gate`、`_spec_gate_push_stale`、`_spec_gate_push_one` 內的 door 比較,新舊值都對得上)。

引句(對照用,取自本批凍結 patch):「warns.append(f"plan_risk 只認 high / low,你寫的是 {str(_pr)!r}(規格閘會當沒寫;low 寫了也不會比機械判定更鬆)")」
