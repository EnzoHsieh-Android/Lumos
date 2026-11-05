severity: minor

**1. 分層與依賴方向:對齊**
- 掛鉤沒有自己判主線。`scripts/hooks/pre-push:547` 只把 `$_rref` 交給 lumos,再讀 pitfalls JSON 的 `pushed_mainline`(`pre-push:589`)。這跟既有的 `light_ok`、`affected_keys`、`autoloop_full` 同一條路:lumos 判、掛鉤讀 JSON 欄位。
- 新函式 `_pitfalls_pushed_mainline` 放在 `scripts/lumos:61991`,緊鄰 `_pitfall_diff_mode`,由它呼叫。判主線直接重用 `_note_reread_mainline_names`(`scripts/lumos:53734`),沒有另寫第四套候選推導。
- 欄位加法沿用既有寫法:`_test_suite_for_range` 多一個 `computed` 鍵,`_pitfall_diff_collect` 兩處輸出都照抄成 `suite_computed`,跟 `graph`、`suite_graph` 同形。
- 探舊版也是讀檔找字樣,跟 `--keep-going`(`pre-push:479`)、`--suite`、`--graph` 同一種。不同的是這次找 `dest="pf_pushed_ref"` 而不是 `"--pushed-ref"`;註解已說明原因(別的命令也有 `--pushed-ref`),合理。
- 唯一跨層疑點是把「推主線」的判定放進 pitfalls 子指令。主線判斷在 lumos 裡本來就有多套(`_push_mainlines`、`_mainline_ref`、`_note_reread_mainline_names`),但沒有哪一套是專給 pitfalls 的。⚠ 交編排者:`_push_mainlines` 的 docstring(`scripts/lumos:65276` 起)列了主線判法並存的理由與收斂路,新增這個呼叫端沒有補進去。

**2. 命名與錯誤處理:大致對齊,有兩處不一致**
- 對齊的部分:
  - dest 用 `pf_` 前綴,跟同子指令的 `pf_diff`、`pf_branch`、`pf_stage` 一致。
  - bash 變數 `_PF_PR`、`_SUITE_BRANCH_DOWN`、`_pf_extra` 跟 `_CL_KG`、`_SUITE_*` 同風格。
  - 空陣列展開用 `${_pf_extra+"${_pf_extra[@]}"}`,跟既有 `${_PP_LINES+"${_PP_LINES[@]}"}` 一致。
  - 失敗方向都往全套退:`pf_json` 空、舊版沒欄位、`suite_computed` 不是 true,都不降級。
- 不對齊的兩處見下面 finding 1、2。
- 另有一個觀察,不當 finding:鄰居的 `--pushed-ref` dest 命名本身不一致(`prg_ref`、`rg_ref`、`na_pushed_ref`、`dr_pushed_ref`),所以 `pf_pushed_ref` 沒有單一慣例可對。

**3. 第二種做法:沒有引入會讓接手者在兩套之間猜的新做法**
- 判主線沒有另寫一套(用 `_note_reread_mainline_names`),探旗標沒換方式(讀檔找字樣),JSON 讀取沒換方式(`grep -q` 加既有的 `python -c json.load`)。
- 有一處重複,但結構對:掛鉤裡「抽 `affected_keys`、併進 `_SUITE_KEYS`、記 `autoloop_full`」這三行(`pre-push:592-594`)是 light 區塊(`pre-push:582-584`)的逐字複製,見 finding 3。
- 測試端的 `_ppfb_harness` 是把 `t_prepush_docs_and_light_run_subset` 的假執行器與假自主迴圈設定抽成共用函式。舊測試仍保留內嵌版本,所以現在有兩份。差異是新版假執行器不處理 `FAKE_KEYS_RC`。這屬於測試輔助碼的重複,不影響行為。

---

severity: minor
blocking: 否
Finding 1:`suite_computed` 用 `.get(..., True)` 讀,跟鄰居直接索引不一致,預設值還往降級方向偏
引句:「"light_ok": _sr["light_ok"], "suite_graph": _sr["graph"], "suite_computed": _sr.get("computed", True),」
- `scripts/lumos:61913` 與 `scripts/lumos:61984` 同一行裡,`light_ok` 和 `graph` 都是 `_sr[...]` 直接索引。
- `_test_suite_for_range` 的每個回傳路徑都已帶 `computed`,所以 `.get` 的預設值是死碼。哪天有人新增回傳路徑漏了 `computed`,`.get(..., True)` 會被讀成「算得出來」,與同一份 docstring 寫的「算不出範圍 → full(fail-safe 是多跑,不是少跑)」方向相反。
- 場景:新分支回傳少了 `computed` → 功能分支被降級成子集。

severity: minor
blocking: 否
Finding 2:`--pushed-ref` 單獨給,沒有跟 `--push-remote` 成對,和其他吃這個旗標的命令不一致
引句:「p.add_argument("--pushed-ref", dest="pf_pushed_ref", default=None, metavar="遠端ref",」
- `scripts/lumos:49220`(room-guard 的 `_rg_precheck`)與 `scripts/lumos:53490`(reread-prepare)都要求 `--push-remote` 與 `--pushed-ref` 成對,否則擋下。
- 掛鉤對這幾個命令也一律成對傳(`pre-push:718`、`pre-push:736`、`pre-push:762`)。
- 這裡只傳 `--pushed-ref`,因為判主線不看遠端名(`_note_reread_mainline_names` docstring 明說)。結構上沒錯,但同旗標在不同命令的契約不同,接手者要自己記哪個要成對。
- ⚠ 鄰居本身的 dest 命名也不統一,這條只算「契約不一致」,不算命名。

severity: minor
blocking: 否
Finding 3:掛鉤裡同一段「抽關鍵字與自主迴圈旗標」複製了兩份
引句:「_k="$(printf '%s' "$pf_json" | "$PY" -c 'import json,sys; print(",".join(json.load(sys.stdin).get("affected_keys", [])))' 2>/dev/null || true)"」
- 同樣三行出現在 `pre-push:582-584`(light 判定)與 `pre-push:592-594`(功能分支降級)。
- 場景:以後改 `affected_keys` 的讀法或 `autoloop_full` 的處理,只改到其中一處,兩條降級路徑產出的關鍵字集合就會不一致。
- 專案在同檔其他地方有「抽成函式免得兩處各寫一份」的先例(`pre-push:401-402` 的 `pp_range_for` 註解),這處沒照做。

---

不對齊共 3 條,其中會擋的 0 條。
