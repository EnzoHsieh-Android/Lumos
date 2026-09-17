severity: blocker
# 外部審稿意見(第 3 輪修訂稿)

severity: blocker

## 逐節讀後記錄

**開頭欄位/decisions/lands_in**:已讀,無 finding——d1–d12 的疊代軌跡(valid/superseded_by)內部一致,d12 是現行版。

**為什麼(數字表)**:已讀,無 finding——本輪未重新稽核帳面統計本身(94%/97%/93%、34/29/5/0/0),留給量法本身的稽核;本輪聚焦第③問指定的程式對照。

**兩層要分開**:已讀,無 finding。

**設計一(門怎麼判)**:已讀,無 finding——`_excluded_line` 尚未落地(規格閘本體待做),純設計層面自洽。

**設計二(句式)**:已讀,無 finding。

**設計三(綁定規則)**:已讀,無 finding——S25 的兩條堵法(至少一條未標 keeps + keeps 測試早於計劃建立)邏輯自洽,尚未落地無法機械驗證。

**設計五(逃逸自動記)**:見 F1、F2、F3。

**設計六(退場條件)**:見 F2。

**進度 / 要動什麼 / 實務隱患 / 回退 / 誠實界線 / 審計修正紀錄**:已讀,無新 finding(「殘餘」段已誠實承認樁測試漏洞並指定由代碼審/guard-kill 兜底,不重複標記)。

---

## Finding 1

severity: blocker
blocking: 是——判準:程式現況直接讓 spec 第五節表格宣稱的「CI 逃逸來源排除 build/lint」機制在本 repo 完全失效,不是理論邊界情況,是已經在產生的真實資料。

spec 第五節「逃逸自動記」CI 來源這一行寫:
引句:「`failed_step` 切詞後有一個詞等於 test/tests/pytest/unittest/testing」

問題:`_ci_step_is_test` 只看 `failed_step` 切詞後有沒有 `test` 類詞,但 `failed_step` 的實際組成是 `f"{job_name}/{step_name}"`(`_ci_failed_step`,`scripts/lumos:22168-22183`)。本 repo `.github/workflows/ci.yml` 只有一個 job,job id 是 `test`(沒有另外設 `name:`),所以**每一個失敗步驟的 `failed_step` 字首都帶 `test/`**——`docs/.ci-log.jsonl` 裡已經實際出現 `'test/Anchor verify (baseline 缺失必紅)'`、`'test/SyntaxWarning 歸零閘'`、`'test/code-loop gate (push 後盾;體檢'` 這幾筆(非測試步驟),切詞後都含 `test` 這個詞,`_ci_step_is_test` 對它們全部回 True。這代表 spec 表格宣稱的「不記:build/lint/timeout/startup_failure」在這個 repo 從一開始就是空話——job 名稱本身把每一步都偽裝成測試步。

file: `scripts/lumos:22168-22183`(`_ci_failed_step` 組字串)、`scripts/lumos:22360-22364`(`_ci_step_is_test`)、`.github/workflows/ci.yml:10`(job id `test`)、`docs/.ci-log.jsonl`(已觀察到的真實 `failed_step` 值)。

r2 修的是「子字串比對誤中 latest/attestation」這個假陽性,但沒有意識到真正的假陽性來源是 job 名稱前綴——`t_escape_auto_ci_only_test_step`(`scripts/test_lumos.py:31359`)的測資用 `"build"`、`"Publish latest image"`、`"attestation"`、`"test (unit)"` 這種裸字串,從未餵過本 repo 真實的 `"job名/步驟名"` 形狀,所以這個回歸沒被任何測試攔住。

---

## Finding 2

severity: major
blocking: 是——判準:第六節的退場門檻(RETIRE-IF ①/①b/②)是 spec 自己說的「承重牆」,若門檻計數對精確度不同的資料一視同仁,承重牆本身的可信度就有洞,應在上線前釐清。

d12 承認逐條嚴重度拿不到時會退回粗判並標記:
引句:「沒給就退回輪級判準並在逃逸帳標 precision=round」

問題:第六節的三個撤除條件(blocker 級逃逸即退、前 30 份 major 以上逃逸 ≥3 份、`push-gate-unreviewed` ≥2 份)只講「幾份」「幾筆」,完全沒有區分 `precision: finding` 與 `precision: round` 兩種記法。`precision: round` 本身就是「這輪最高嚴重度配任一條 code 型發現」的粗判,d12 自己舉例「一條 spec 型 major 配一條 code 型 minor 也會誤記」——也就是說這種粗判本身就可能把不該算 code-major 的逃逸算進去。第六節的絕對門檻(尤其 ②「前 30 份 major 以上逃逸 ≥3 份」)一旦被幾筆 `precision: round` 的誤記湊到 3 份,就會觸發「整套退回」,而這個退回決策的依據裡可能有假陽性——S13 健檢也只說「按門與階段分開印」,沒說要分開印 precision。這是設計文本自己點名的量測精確度問題,卻沒有接到它會影響的下游機制。

file: `scripts/lumos:6196-6216`(precision 寫入邏輯)、spec 第六節(退場門檻,未寫 precision 過濾)。

---

## Finding 3

severity: major
blocking: 是——判準:這是一個 2026-10-17 就要人來讀的回頭條件,若它的判準本身答不出它宣稱要答的問題,到期時會給錯誤的心安,而不是真正的重驗。

引句:「看治理帳有無 escape-auto-failed、逃逸帳有無斷點;有就補第三層,沒有就維持」

問題:`_escape_auto_failed` 寫治理帳失敗時,例外被整個吞掉(`except Exception: pass`,`scripts/lumos:7602-7603`),只剩 `print(..., file=sys.stderr)`。也就是說,「治理帳也寫不進去」(雙重失敗)這個情境,依定義下**治理帳裡永遠不會出現任何紀錄**——這正是 REVISIT 打算靠「看治理帳有無 escape-auto-failed」去偵測的那個事件。REVISIT 能看到的只會是「單一失敗」(逃逸帳寫失敗但治理帳寫成功)的情形,對它自己在意的「雙重失敗」是結構性瞎的:雙重失敗發生了,治理帳一樣是空的,跟「沒發生」在這個判準下無法區分。spec 第五節自己也寫「沒有第三層兜底——接受,REVISIT 見文末」,但把驗證方法留給了一個量不到目標事件的判準。

file: `scripts/lumos:7597-7604`。

---

## 已核實、無新 finding 的三個指定問題(①/③/⑤)

**①(`_hit` 三種情境)**:`--finding-kind` 若給,CLI 要求 `set(kinds) == F`(`scripts/lumos:5982-5983`),`--finding-severity` 只要求 `set(sevs) <= F`(`scripts/lumos:5999`)——兩者共用同一個發現編號空間 F,「kinds 有、sevs 有但鍵不重疊」這個情境在目前 CLI 驗證下不可能發生(kinds 若給必覆蓋全集,sevs 的鍵必是全集子集)。「kinds None、sevs 有」→ 不看型別、只看嚴重度,`_hit` 保守納入,符合文件講的邏輯。「sevs 給了 clean」→ 該條不進 `_hit`,符合預期。程式行為與文件一致,已讀無 finding。

**③(pre-push 兩個 grep)**:`scripts/lumos:26851/26853/26859` 三句缺留痕訊息全部以 `"tier=high 且"` 開頭,沒有第四句;`受波及合約的測試沒過`(`scripts/lumos:26008`,由 `scripts/lumos:26729` 早退)與 `tier=high 且...`(`scripts/lumos:26856/26862`,由 tier 檢查之後才觸發)是同一次 `check` 呼叫裡互斥的兩條回傳路徑,不會同時出現在同一份 `$_cl_out`——r2 修正屬實,已讀無 finding。

**⑤(回退基準 sha)**:S8(處置閘第五步接同一支檢查器)尚未落地(spec 進度段自陳「規格閘本體...等設計審過閘」),`回退基準 sha:(待填)` 留白是預期狀態,不是遺漏;已落地的逃逸自動記三來源已在 `scripts/lumos` 確認存在且與回退範圍無關(spec 第 277 行④已聲明保留)。已讀無 finding。

---

## 固定席節點逐條影響判斷

- **Systems/design-loop**(★INVARIANT★ 處置閘第五步材料/日期規則):本次改動只是把第五步的「條款檢查」邏輯換成共用的 `_clause_check(plan, door)`,不動「審材必須是 .md」「首筆帳日期」這些既有合約行的判定邏輯——不影響。
- **Systems/bound-tests-gate**(★INVARIANT★ 合約測試逐支真跑/懸空/偽證據判準):spec-gate 的「跑」段(S17/S27)是另開一條獨立的測試執行路徑(規格閘綁定測試 vs. bound-tests-gate 的波及合約測試),兩者互不覆寫對方的判準——不影響,但兩套「測試證據可信度」標準不同(bound-tests-gate 有 fake/dangling/unattributed 分類,spec-gate 只分「紅/0 支跑到/其他」),spec 第 177 行已自承是殘餘風險並指定由代碼審/guard-kill 兜底,不重複計為新 finding。
- **Issues/code-loop守衛main-direct盲區**:本次改動不涉及 main 分支直推路徑——不影響。
- **Systems/anchor-integrity**(★RISK★):`scripts/hooks/pre-push` 是錨點檔,spec 進度段已示範遵守「改錨點檔要 `lumos anchor approve`」的紀律——不影響既有合約,只是每次落地都要重做這一步。
- **Systems/每支檔有家**:新開 `Systems/規格閘` 承接 `cmd_spec_gate`/`_clause_check`/`_excluded_line` 與 pre-push 新增段落,落點聲明清楚——不影響。
- **Systems/canary-audit**(★INVARIANT★ record/second 落盤自驗):`kind: spec-gate` 走既有 `cmd_canary`→`_jsonl_append_verified` 寫入口,沒有另開寫路徑——不影響落盤自驗合約;second 的 telemetry-only 合約與本案無關。
- **Systems/guard-kill**(★INVARIANT★ rc 優先序/JSON 純淨):本案不呼叫 guard kill——不影響。
- **Systems/lumos-cli-read**(★INVARIANT★ search 排除 superseded 不排除 stale):本案不改 search 濾網——不影響。

---

最嚴重 severity:blocker;blocking 共 3 條(與逐條標記一致:F1 blocker/是、F2 major/是、F3 major/是)。
