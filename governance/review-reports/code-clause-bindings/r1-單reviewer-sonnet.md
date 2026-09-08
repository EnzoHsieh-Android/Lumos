severity: blocker

# 條款綁測試算進度 代碼審(單 reviewer,外部審查視角)

被審:`governance/review-reports/code-clause-bindings/r1-snapshot.patch`(1045 行,凍結)。
方法:全份逐段讀 diff,對照 spec(`docs/lumos-toolchain-knowledge/Projects/條款綁測試算進度_計劃.md`),
對可疑處用 `_load_lumos_inproc()` 同款載入方式直接呼叫函式重現,或跑真 CLI 重現。

## 固定席合約節點(前 8 篇,逐條答)

1. **`Systems/lumos-cli-read.md` ★INVARIANT★**(search 排除 superseded 但不排除 stale)——不影響。本批完全沒碰 `cmd_search`/濾網/排序邏輯,只加了 `cmd_spec_trace`/`cmd_handoff`/`cmd_lint`/`_loop_status_disposal` 幾個新增/擴充函式,search 路徑一行未動。

2. **`Systems/bound-tests-gate.md` ★INVARIANT★**(code-loop check 對固定席合約測試逐支真跑)——不影響。本批明講「bound-tests 帳整個不用」(計劃 KEY:「bound-tests 帳★不記測試名★」),沒有任何一行碰 code-loop 的 bound-tests 檢查函式。

3. **`Systems/canary-audit.md` ★INVARIANT★×2**(readback 驗回讀 / second 純 telemetry)——不影響。`_disposal_clause_step` 只讀 `rows` 裡既有的 `ts` 欄位(既有 canary 帳的既有欄位),不寫入新的 canary 紀錄型態,`cmd_canary` 的 record/second 邏輯完全未觸碰。

4. **`Systems/guard-kill.md` ★INVARIANT★×2**(rc 優先序 / json 模式輸出純淨)——不影響。本批未碰 `guard kill` 任何程式碼路徑。

5. **`Systems/slim-get-一行安裝.md` ★INVARIANT★×2**(.ps1 ASCII 無 BOM / `$Args` 保留名)——不影響。本批未碰任何 `.ps1` 檔。

6. **`Systems/slim-install-安裝器.md` ★INVARIANT★×7**——不影響。本批未碰任何 `cmd_slim_install`/CLAUDE.md 注入相關函式。

7. **`Systems/slim-uninstall-一行卸載.md` ★INVARIANT★×6**——不影響。本批未碰任何 `cmd_slim_uninstall`/卸載相關函式。

8. **`Systems/授權與歸屬.md` ★INVARIANT★×2**(LICENSE 白名單 / SPDX 檔頭)——不影響。本批新增的函式全部落在既有已標頭的 `scripts/lumos`/`scripts/test_lumos.py` 內部,未新增檔案、未碰 `_VENDORED_TOOLKIT`/deinit 白名單。

其餘(`測試假綠形態`/`design-loop`/`lumos-cli-lifecycle`/`loop-convergence-recording`/`pitfalls-code-loop`/`reversibility-governance-ledger`/`lumos-deinit`/`check-t-sentinel`/`core-invariant-baseline`/`cochange-guard`/`check-r-guard`/`doctor-irreversible-hint`/`lumos-refcheck`/`judge-severity-gate`)超出上限,只列名,已掃過 diff 未見直接觸碰。`design-loop.md` 例外一提:本批確實給它加了一條新 ★INVARIANT★ KEY(處置閘第五步),但那是本批自己新增的合約、不是對既有合約的破壞,不算「破壞」。

---

## Finding 1

severity: blocker
blocking: 是——判準:反引號範例句(純文字說明「[SN] 要怎麼寫」)被工具誤判成真的第二條驗收條款,導致設計審處置閘對一份「其實只有一條、且已綁定」的計劃仍判 FAIL,是「不改會做出錯的行為」。
引句:「反引號裡的 `[S3] …` 是範例不是定義」

`_CLAUSE_LEAD_RE` 只負責排除「該行不是 lead」時把該次出現丟進 `fallback` 而非 `defined`桶,但 `clause_bindings` 對 `set(defined) | set(fallback)` 一視同仁——只要一個 id 在全文任何地方出現過(哪怕只在反引號範例句裡、且全文沒有其他任何一次出現),就會生出一整條列。當這個「只在範例裡出現一次」的 id 剛好沒帶 `[test:]`/`[manual:]`(範例常見寫法,例如純粹示範「`[S9] 這是範例格式`」),它的 state 會是 `untagged`,直接讓 `_disposal_clause_step` 判 FAIL——即使全文真正的驗收條款早就全部綁好。

最小重現(直接呼叫 `_disposal_clause_step`,spec 只有一條真條款 S1 且已綁 `t_ok`,S9 純屬示範文字):
```
text = "### [S1] 真條款 [test:t_ok]\n- 條款要這樣寫,例如 `[S9] 這是範例格式`,不是真的有第九條\n"
```
輸出:
```
gate: fail
[disposal] 條款綁定: ✗ — 1/2 條驗收條款沒標:S9(第 2 行)
```
S1 明明已綁定,閘卻因為一句純示範文字判 FAIL。設計文件自己在「實作落地」段承認撞過同型問題(「實作當下就被自己的計劃打到:S1 段那個範例行原本被當成 S3 的定義」),但只修了「範例行不會被當成 defined」,沒堵住「範例行仍會被當成一條全新的、待標記的條款」這個更嚴重的後門。

## Finding 2

severity: major
blocking: 是——判準:破壞合約(spec-trace 自稱「★單一裁決來源=綁測試★」,但真的綁了的表格式條款被誤報成懸空)。
引句:「反引號裡的 `[S3] …` 是範例不是定義」

`_CLAUSE_LEAD_RE = re.compile(r"^[\s>*#\-\d.]*(?:\*\*)?\s*\[S(\d+)\]")` 的字元類沒收 `|`,所以「表格列」開頭的 `[SN]`(review 材料明確要求測試的四種格式之一)永遠判不到 lead,永遠落進 `fallback`。若同一個 id 在表格外還有一次「行內引用」(例如「見 [S1] 的做法…」),而那次引用在文字順序上排在表格列之前,`fallback.setdefault` 會鎖住那個引用行當「這條的內容」,表格裡真正的定義(可能已綁好測試)整個被蓋掉。

最小重現(表格式定義 `[test:t_ok]` 真的存在,但排在它前面的行內引用寫了個不存在的 `t_wrong`):
```
text = "見 [S1] 的做法（細節見下表）[test:t_wrong]\n| 條款 | 說明 |\n|---|---|\n| [S1] | 甲 [test:t_ok] |\n"
```
`clause_bindings(...)` 回傳:
```
{'id': 'S1', 'line': 1, 'refs': ['t_wrong'], ..., 'state': 'dangling'}
```
真正綁定 `t_ok` 的表格列完全沒被看到,`spec-trace`/`_disposal_clause_step` 都會把一條已正確綁定的條款報成「懸空(寫錯)」。

## Finding 3

severity: major
blocking: 是——判準:破壞既有合約(`--repo` 覆蓋是同一支處置閘裡「r3 s2 席」明文修過的既有機制,新的條款步驟悄悄繞過它,在支援場景下產出錯誤資料)。
引句:「rr = _vault_repo_root(env) if env is not None else Path(root or ".")」

`_clause_bindings_for` 只要 `env is not None` 就無條件用 `_vault_repo_root(env)` 算 repo 根,完全不理會傳進來的 `root` 參數——即使呼叫端 `_disposal_clause_step(rows, spec, root, env, ...)` 明明把 `root` 傳進去了。而 `_loop_status_disposal` 裡其餘所有步驟(G3、留痕)都走 `_dsp_root = Path(repo).resolve() if repo else _vault_repo_root(env)`(`scripts/lumos:6703`,註解明寫「git-less 部署副本裡 .git 不在,向上找會落錯根——給使用者一條明路」)。也就是說,同一次 `--disposal --repo <根>` 呼叫裡,G3/留痕會正確用 `--repo` 指定的根,條款綁定這一步卻獨自退回會落錯根的 `_vault_repo_root(env)`。

最小重現(真跑 CLI,`spec-trace` 在一個沒有 `.git`/`.lumos/config.json` 的「部署副本」vault 裡查一條真的綁了 `t_ok`、而 `t_ok` 真的存在於另一個 repo 的計劃):
```
$ python3 scripts/lumos spec-trace Projects/P_計劃 --json
{"bindings": {"S1": {"state": "dangling", "refs": ["t_ok"], ...}}, "binding_index_error": null, ...}
```
`t_ok` 真實存在(在另一個帶 `.lumos/config.json` 的 repo 裡),但因為索引蓋錯根,回報「dangling」且不報任何錯誤(`binding_index_error: null`)——完全靜默的誤判。`_disposal_clause_step` 用真 `--repo` 跑同款設定也證實同一件事:即使 `--repo` 指向真的有 `t_ok` 的 repo,輸出仍是「綁了 0…懸空 1」。

## Finding 4

severity: major
blocking: 是——判準:同一支檔案裡已經證明過的 bug class(見 `_loop_ts_key` 的說明:「換一台機器寫 UTC 就會靜默把開著判成關了」)被原樣重犯,導致「不回溯 2026-09-08 之前」這條規則會依記帳機器的時區而判不同。
引句:「if first_ts and first_ts[:10] < _CLAUSE_GATE_SINCE:」

`_CLAUSE_GATE_SINCE = "2026-09-08"` 的比較直接對 `first_ts[:10]` 做字串前綴比大小,沒有換算 UTC。這正是同檔案 `_loop_ts_key`/`_loop_ts_newer`(`scripts/lumos:5936-5957`)已經修過的同一類 bug,新程式碼沒有重用它。

最小重現(呼叫 `_disposal_clause_step`,帳的 `ts` 是本地晚上 8 點 -05:00,換算 UTC 其實已經是 `2026-09-08T01:00:00+00:00`,理論上該套用新閘):
```
ts_a = "2026-09-07T20:00:00-05:00"   # 真 UTC = 2026-09-08T01:00:00+00:00,晚於 cutover
_disposal_clause_step([{"ts": ts_a}], "...", None, None)
```
輸出:
```
skip | [disposal] 條款綁定: —(迴圈首筆帳 2026-09-07 早於 2026-09-08,不回溯)
```
同一個真實時刻,只因為記帳機器的時區偏移不同,「該不該套用新閘」的判定會不一樣——這正是這個 repo 自己在 `loop list` 那次事故裡寫進圖譜、明講要避免的錯法。
附帶一個更輕的邊界:`first_ts` 若是壞資料(例如手改帳留下 `"0000-00-00T00:00:00+08:00"`),因為 `"0000-00-00" < "2026-09-08"` 成立,一樣判「不回溯」直接放行——跟同一支函式裡「findings 欄壞值 fail-closed」的既定風格相反(壞資料本該擋、不該放）。這條只到 minor,不單獨計分。

## Finding 5

severity: minor
blocking: 否——判準:純文件性錯誤,不影響任何實際行為,只是誤導讀者。
引句:「rc:全認領=0;有未認領=1;計劃無 [SN] 標記=0(opt-in 未啟用)。唯讀。」

`cmd_spec_trace` 本體的 docstring(patch 裡是未改動的 context 行,`scripts/lumos:4173`)仍寫著舊制 rc 語意(「未認領」= 舊制驗證筆記回指未回),但本批已經把 rc 改成看「未標」(`untagged`)。同一批也沒更新 argparse 的 `--help`。
file: `scripts/lumos:21439` ——`help="條款級追溯(RTM 輕量):計劃 [SN] 條款 × 回指 Verification 認領;未認領 rc1"`,同樣還停在舊語意,`lumos spec-trace --help` 會告訴使用者錯的 rc 判準。

## Finding 6

severity: minor
blocking: 否——判準:文件與程式碼行為對不上,但不影響輸出。
引句:「skip 三種:審材不是 .md 計劃(code 迴圈的 patch)/ 迴圈首筆帳早於 _CLAUSE_GATE_SINCE(不回溯,週跑回放會重跑閘)/ 計劃無 [SN](opt-in 未啟用)。」

`_disposal_clause_step` 實際有 4 條 skip 分支,docstring 漏列「`spec_sha_override is not None`(凍結/回放模式)」那一條(程式碼裡它是第一個 `if`,且自己印一行不同的理由句)。維護者照 docstring 數 skip 條件會少算一種。

## Finding 7

severity: minor
blocking: 否——判準:測試覆蓋缺口,不是功能缺陷(讀 code 確認邏輯本身是對的:`unt` 只算 `untagged`)。
引句:「v = mkvault()」

`t_disposal_clause_gate` 的兩個真正判定案例(cg-a 判 FAIL、cg-b 判 PASS)全部只用 `[manual:]`,從沒用過 `[test:]`。原因是 fixture 用 `mkvault()`(`scripts/test_lumos.py` 裡不跑 `git init`、也沒有 `.lumos/config.json`),`_vault_repo_root` 找不到 `.git` 只能退到 vault 上層,平台索引永遠是空的——任何 `[test:xxx]` 在這個 fixture 底下都會被判 `dangling`,測試作者顯然是刻意避開了它。結果是:「綁了真測試 → PASS」與「綁了但懸空 → 只提醒不擋,閘照過」這兩句 spec 裡的行為承諾,在 `_disposal_clause_step` 這一層完全沒有整合測試直接驗證過(`t_spec_trace_clause_table` 有驗到 spec-trace 層級的「懸空只提醒」,但走的是另一支函式路徑)。

## Finding 8

severity: minor
blocking: 否——判準:測試覆蓋缺口。
引句:「(d / "tests" / "test_t.py").write_text("def t_ok():\n    assert True\n", encoding="utf-8")」

`_clause_repo` fixture(`t_spec_trace_clause_table`/`t_handoff_clause_pointer_only` 共用)只放了一支測試 `t_ok`,計劃裡只用了 `t_ok`(綁了)跟 `t_gone`(全無,dangling)兩種 ref,從未安排一個「檔裡有這個字串但不是 `def`」的情境。所以「只被提到(mentioned)」這一態在走真索引(`build_code_haystack`/`_platform_test_index`)的整合測試裡完全沒被打過,只在 `t_clause_bindings_states` 的 stub 索引單元測試裡驗過。

## Finding 9

severity: minor
blocking: 否——判準:審查材料範圍與作者自述不符,是流程/可審性問題,不是功能 bug。
引句:「[工具分類 2026-09-08,plan:Projects/工具分類_計劃]」

這份「凍結 patch」除了條款綁測試算進度(clause-bindings)的改動外,還夾帶了一整組跟它無關的功能:`_lumos_config_near_vault`/`_scope_policy`/`cmd_lint` 的 scope 標籤值域檢查、以及 `t_lint_scope_policy` 測試——出自另一個計劃「工具分類」。派工訊息的「作者自述」完全沒提到這塊。已就這塊粗讀一遍(fail-open 讀設定、只 warning 不擋、MOC 豁免、有自己的測試),沒發現額外功能性 bug,但混進「只審這份」的凍結材料裡會讓審查範圍失焦,值得在收貨時分開。

---

## 已讀無 finding 的部分

- `docs/…/條款認領追溯_計劃.md` 的 frontmatter/summary 補 KEY 與 `scope/guards-gates` 標籤——純追溯性文件更新,內容與程式碼行為一致。已讀,無 finding。引句:「單源 [[Projects/條款綁測試算進度_計劃]] [test:t_spec_trace_clause_table]」
- `docs/…/design-loop.md` 補的 ★INVARIANT★ KEY 對到 `_disposal_clause_step` 的實際行為(skip 條件、fail 條件)敘述正確(除 Finding 6 那個「三種」的小落差外)。已讀,無 finding。引句:「.patch 審材、無 [SN]、舊迴圈、凍結/回放模式一律跳過不擋」
- `governance/anchor-baseline.json` 的 sha256 更新——用 `hashlib.sha256` 現算 `scripts/test_lumos.py` 核對過,雜湊值吻合檔案實際內容,不是編造的。已讀,無 finding。引句:「條款綁測試算進度 S1+S3 落地:clause_bindings/spec-trace 條款表/handoff 一行/處置閘第五步 + 5 支測試」
- `skills/lumos-design-loop/SKILL.md` 第 10 步新增一句、`skills/lumos-project-notes/commands/05-設計審查迴圈.md` 新增一列——都只是把已落地的行為寫成操作指引,跟程式碼行為一致。已讀,無 finding。引句:「lumos spec-trace <計劃> 看哪條是哪一態」

---

## 總結

最高 severity:**blocker**(Finding 1)。
blocking 條數:**4**(Finding 1 blocker、Finding 2/3/4 major)。
