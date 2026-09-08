severity: blocker

# 條款綁測試算進度 code-clause-bindings r3(上限,末輪驗收)——單reviewer

被審:`r3-snapshot.patch`(全量,1238 行,凍結)+ `r3-delta.patch`(r2 折入,529 行)。方法:HEAD(732d08e,`scripts/lumos` blob `e71f6c3` 與 r3-snapshot 尾狀態一致)獨立複製到沙盒(`/tmp/r3check`),因工作樹另有別 session 未提交的無關改動(`_extra_fm_keys` 等),一律不對其操作、只用 `git show HEAD:<path>` 取凍結狀態驗證,未動任何真實檔案。凍結狀態下 `python3 test_lumos.py -k clause` 58 案例全綠(基線);另外自寫兩支一次性 repro 案例跑 disposal 閘全流程,驗完即棄。

## 10 條逐一驗

**g1(反引號整段遮掉再掃)修好**。純函式對「同一行成對反引號單組/多組範例」直接測試,`[S9]` 完全不進 `defined`/`fallback`;`test_lumos.py` 的 cg-i/cg-i2 兩案在凍結快照上綠。但這個修法的作用範圍只到「同行成對反引號」,相鄰逃逸路徑見新 finding N1/N2。
引句:「line = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), raw)   # 反引號裡的一律是範例:整段遮掉」

**g2(reference.md 誤帶他人段落)修好,且驗到 HEAD 而不只本輪快照**。用 git history 直接重現:`0e1faab`(r1)scope/ 列被誤換成他人未提交的「值域宣告」版本,`547a960`(r2 修復commit)精確退回到與更早 baseline `76960df` byte-identical 的簡版,`732d08e`(現在 HEAD)仍維持退回;目前工作樹該列仍是未提交的「值域宣告」版(git status 顯示 modified),證實「工作樹保留」的承諾也兌現。
引句:「我改指令參考手冊時又掃進別人同檔未提交的一段,第四次 → 拆回」

**g3(INV_TAG_RE 只放寬 manual)修好**。讀正則確認 test/audit/kill/src/git 仍要求 `[^\]]+`(至少一字元),只有 manual 允許 `[^\]]*`(可空)。
引句:「INV_TAG_RE = re.compile(r"\[(?:(?:test|audit|kill|src|git):\s*[^\]]+|manual:\s*[^\]]*)\]")」

**g4(計劃讀不到 → abort → rc2)修好**。四個呼叫 `_loop_status_disposal` 的入口(freeze 兩趟、golden replay)都在讀 `result_out.get("rid"/"fails")` 之前先判 `rc==2` 分流,`abort` 路徑不設 `result_out` 不會被任何呼叫端誤讀成空 fails 列表。
引句:「計劃讀不成文字 → "abort"(呼叫端同 G3 擋下 rc2,兩步同一種處置)」

**g5(docstring 跳過四種)修好**。docstring「skip 四種」與程式碼四個 skip 分支(凍結/回放、code-、cutoff、無 [SN])一一對上;唯獨本輪新增的「零條定義」fail 分支沒被列進 docstring 的 fail 清單,只是文件完整度問題,另記新 minor finding N3(不影響行為,不觸發折返)。
引句:「skip 四種:①凍結/回放模式(spec_sha_override 有值,對凍結 sha 判、不重讀活檔)②迴圈類型是 code」

**g6(`_roster_kind` None 當設計審)修好**。核對 `_roster_kind` 定義:只有精確 `code-` 前綴才算 code,其餘「code 開頭無連字號」一律落 None、不再提早 skip,直接落入設計審全流程並可被真的 FAIL 擋下(`test_lumos.py` 的 `codecg{id}` 案例綠)。
引句:「_roster_kind 回 None(code 開頭但不是 code-)一律當設計審:fail-closed,免得取個 codeX 的編號就繞過」

**g7(`[manual:]` 要含實字)修好**。純函式對 `[manual:!!!!]`(四個驚嘆號,長度達標但無實字)驗證回到 `untagged` 而非 `manual`,`re.search(r"[^\W_]", x)` 正確擋下純標點。
引句:「if len(x.strip()) >= _MANUAL_MIN_CHARS and re.search(r"[^\W_]", x)]   # ≥4 字且至少一個實字」

**g8(勾選框算定義行、零條定義擋)修好**。純函式驗證 `- [ ]`/`- [x]`/`- [X]` 三種勾選框寫法都能正確定義條款;另外針對審查提示問到的「表格列前導空白/對齊符」額外測了縮排表格列(`  | [S5] | ... |`)與純對齊分隔列(`|:---:|`)兩種邊界輸入,兩者都不誤擋、行為正確,零條定義擋只在真的沒有任何行首定義時才觸發(cg-m 純引用案例仍正確 FAIL)。
引句:「計劃裡有 [SN] 字樣但沒有一條在行首定義({len(undef)} 個只在行內/範例出現)」

**g9(handoff 索引建不起來講原因)修好**。`_handoff_clause_counts` 把 `_clause_bindings_for` 的 `err` 存進 `index_error`,`cmd_handoff` 文字版與 `--json` 都改讀這個欄位、不再在索引壞掉時誤印「0 條」;JSON 輸出把 `index_error` 原樣帶出,程式化消費者可辨識。
引句:「c["index_error"] = err」

**g10(索引建不起來 fail-closed 有測試)修好**。`cg-l` 案例把 `.lumos/config.json` 的 platforms 設定改壞後重新過閘,斷言 `rc==1` 且訊息含「索引建不起來」;凍結快照上重跑此案例與其餘 57 支同綠。
引句:「check("clause-gate: 測試索引建不起來 → FAIL(驗不了≠通過)", r.returncode == 1」

## delta 引入的新洞

### N1
severity: blocker
blocking: 是——直接讓「已標的真條款」在磁碟上等同「未標」,`lumos loop status --disposal` 對合規計劃回 rc1(⛔ DISPOSAL GATE FAIL),違反本輪自己寫的 ★INVARIANT★ 承諾(反引號範例不算條款)。
引句:「反引號裡的內容整段遮掉再掃、只在行內引用裡出現的 id 不算條款」
file: `scripts/lumos:4073`(HEAD 732d08e;`_disposal_clause_step` 的實際擋點在 `scripts/lumos:13449-13453`)
最小重現:計劃寫 `- [S1] 真條款,範例格式是 \`[S9] 範例 [manual:講一下就好]\n`(反引號漏打結尾,常見手誤)。`clause_bindings` 因無法配對反引號完全不遮罩,`[S9]` 被當成同行第二個定義,把行尾的 `[manual:講一下就好]` 分給了 S9,S1 反而變成 untagged;`_loop -- disposal` 全流程重現印出「條款綁定: ✗ — 1/2 條驗收條款沒標:S1(第 3 行)」,rc=1。

### N2
severity: blocker
blocking: 是——同一種「範例被當條款」的合約破壞,只是逃逸路徑換成 fenced code block,不需要任何手誤,是本輪這個遮罩設計的結構性盲區。
引句:「for no, raw in enumerate(text.split("\n"), 1):」
file: `scripts/lumos:4072`(逐行處理、無 fence 狀態追蹤;擋點同 N1,`scripts/lumos:13445-13448`)
最小重現:計劃裡有 ```` ```\n- [S9] 這是文件範例,不是真條款\n``` ```` 這種說明格式用的 fenced block(此 fence 內容行本身不含任何反引號,遮罩機制完全碰不到它),`_CLAUSE_LEAD_RE` 認它是行首定義;`_loop -- disposal` 全流程重現印出「條款綁定: ✗ — 1/2 條驗收條款沒標:S9(第 7 行)」,rc=1,即便計劃自己唯一的真條款 S1 已標好 `[manual:]`。

### N3
severity: minor
blocking: 否——只影響 docstring 的 fail 分支清單完整度,不影響任何實際擋/放行分支,行為本身已被其他測試覆蓋。
引句:「設計審審材不是 .md、首筆帳 ts 讀不動、測試索引建不起來 → fail(驗不了≠通過)」
file: `scripts/lumos:13410`(fail 清單漏列本輪新增的「有 [SN] 但零條在行首定義」分支,實際分支在 `scripts/lumos:13445`)

## 總結

最嚴重 severity:blocker(N1、N2 兩條;10 條 r2 折入全部確認修好,無 blocking 級重現或引入)。blocking 條數:2。
