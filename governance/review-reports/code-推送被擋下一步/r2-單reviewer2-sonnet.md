severity: major

## 審查報告(第 2 輪,單 reviewer2-sonnet)

**我沒做到的部分**
- 全部驗證用臨時 clone 跑,已刪。
- `-k prepush` 的整批子集 22 分鐘還沒跑完,我手動停掉。它的結果不採計。
- `git push` 與 `push` 字樣在本席 Bash 被守衛擋,無法實跑真 git,見 R4。

### R1 測試漏洞:兩種合理改壞,測試照綠
severity: major
blocking: yes
file: `scripts/test_lumos.py` 的 `t_prepush_next_step_is_the_call_the_gate_ran`、`scripts/hooks/pre-push`(約 512、692 行)

**失敗場景**
- 測試的 ② 宣稱「三套範圍互不相同」。但新分支首推時,home 與 note-shape 的 `_hrange`、spec-gate 與 code-loop 的 `_brange` 在測試裡都是同一個 `base..head`。
- 真實情況下兩者會不同。例如 `_hold^`(最早不在任何遠端的提交的上一個)不等於主線分岔點時,home 與 note-shape 的範圍就跟 spec-gate、code-loop 的範圍不同。
- 測試的遠端 ref 只有 `Lumos/main=base`,遠端名只有 `Lumos`,所以遠端名帶 shell 特殊字元(例如網址帶 `&`)的情形從沒被執行到。
- `_push_args` 只在分支名那條(③)驗引號,遠端名的引號沒驗。

**最小重現(兩個改壞都用 `python3.14 scripts/test_lumos.py -k t_prepush_next_step_is_the_call_the_gate_ran`)**
- 改壞一:把 home 那行改成 `... "lumos home check --diff $_brange"`。結果 `40 passed, 0 failed`,沒翻紅。
- 改壞二:把 `_push_args` 裡 `$(printf '%q' "$_PP_REMOTE")` 換成 `$_PP_REMOTE`。結果 `40 passed, 0 failed`,沒翻紅。
- 另造一個情境:遠端已知 `base`,把 `FAKE_PUSH_RANGE` 設成 `head..head`,讓兩套範圍分家。
  - 修後未改壞:home 印 `base..head`,實際呼叫 `base..head`,一致。
  - 改壞一之後:home 印 `head..head`,實際呼叫 `base..head`,不一致。
  - 這個分家情境不在現有測試裡。

引句:「_hrange="$_rsha..$_lsha"」是 pre-push 現有程式。patch 中對應的 + 行是:
引句:「pp_record_block home "$_rref" "有程式檔沒有家,或說明寫進了別人的家" "lumos home check --diff $_hrange"」

**歸因**:未判定。「測試抓不到範圍或引號被換」是修後新測試的盲點。修前測試沒做這種比對,我沒有修前同形改壞的紅綠結果,所以不能說是回歸或原有漏查。

### R2 涵蓋另一類:autoloop 與全套的「下一步」不是閘實際跑的那條
severity: minor
blocking: no
file: `scripts/hooks/pre-push`(約 805 行 `_AUTOLOOP_ARGS`、約 817 行與約 970 行的 `下一步:`)

**失敗場景**
- 純文件或 light 推送時,閘實際跑的是 `test_autonomous_loop.py -k real_claude_md`(`_AUTOLOOP_ARGS`)。
- 印出的「下一步」去掉了 `-k`,整支約 68 秒重跑。
- 全套紅走分片 `--suite docs`,印的是 `--ff -x` 全跑。
- 兩者是實際呼叫的超集。若本機另有別的紅,會誤導人去查不相干的東西。
- `$PY` 沒引號。路徑含空白時,照抄貼上會斷。

引句:「echo "下一步:$PY scripts/test_autonomous_loop.py"」

**歸因**:未判定。這行是 3b76b68 就有,不在修補差異內。測試的 `want in last` 只驗子字串,所以這個落差測不到。

### R3 合約濾除讓「計劃連到作廢 IRREVERSIBLE 的節點」不再算高風險
severity: minor
blocking: no
file: `scripts/lumos`(`_contract_key_matches` 與 `_door_linked_signals`,約 13839 行)

**失敗場景**
- 計劃只連到節點 A,A 只有一行 `KEY:★IRREVERSIBLE★ 刪除帳號後不可還原 [status:superseded] [被取代:Systems/B]`,而 B 沒被計劃連到。
- 我實跑 `_door_linked_signals`:基底 14cf40143 回傳 `[('Systems/A', '★IRREVERSIBLE★')]`,修後回傳 `[]`。
- 風險門訊號變少,偏向放寬。
- 這是筆記宣稱的有意決定(「計劃風險理由一起生效」)。
- 但 `t_superseded_contract_not_sent` 只測 `_contract_texts`,沒測 `_door_linked_signals`。將來有人讓門另掃一份,測試不會紅。

引句:「if not _ns_superseded(s.partition(":")[2]):」

**歸因**:有證據的新增行為,來自 3b76b68 的 `_contract_key_matches` 濾除,不在這次修補差異內。

### R4 「整段輸出最後一行」的前提對真的推送不成立(⚠ 未能實跑)
severity: minor
blocking: no
file: `scripts/hooks/pre-push`(約 770 行 `echo "下一步:$_PP_FIRST_NEXT" >&2`)

**失敗場景**
- 我依 git 原始碼印象判斷:掛鉤回非零後,真的推送在掛鉤輸出之後還會印 `error: failed to push some refs to '…'`。若屬實,代理讀到的最後一行是 git 自己的,「下一步」只是掛鉤輸出的最後一行。
- 測試只看掛鉤自己的 stderr,測不到。
- 這點我沒實跑,不能當事實,請作者實測確認。

引句:「[[ -z "$_PP_FIRST_NEXT" ]] || echo "下一步:$_PP_FIRST_NEXT" >&2」

**歸因**:未判定,設計層。

### R5 錨點基準線跟最終內容對不上
severity: minor
blocking: no
file: `governance/anchor-baseline.json`

**失敗場景**
- 修補提交 e4190cab7 又改了 `scripts/hooks/pre-push` 與 `scripts/test_lumos.py`,但基準線還停在 3b76b68 時簽的版本(`a1de62…`、`dd9d016…`)。
- 我在 e4190cab7 跑 `python3.14 scripts/lumos anchor verify`,回 rc=1,實際雜湊與基準線不同。
- 推送前會被擋,要重簽。治理帳也已記下 3b76b68 的 anchor blocked 事件,作者知情。
- 基準線 note 寫的「原話:簽」是對舊版內容簽的,新版要重新取得。

引句:「"scripts/hooks/pre-push": "a1de6213ac73330e802939f6ee8e2e68a130825b3111f92715402fb67075544b",」

**歸因**:有證據的修補後狀態(修補沒更新基準線)。

### R6 筆記更正措辭過度延伸
severity: minor
blocking: no
file: `docs/lumos-toolchain-knowledge/Projects/世界解重新註解2026-10_Agent編排_調研.md` 與 `…_總覽_調研.md`

**失敗場景**
- 更正寫「Lumos 派的 Sonnet 席不在安全區」。
- 來源 `04_Agent編排.md` 表 II 測的是 Claude Sonnet 4.5(−21.9,顯著),且同檔自己寫「前沿版本的數字要自己量」。
- 本專案記憶記的子代理 Sonnet 是 5.5。更正把 4.5 的結果直接套到 5.5,只是推論,卻寫成斷言。
- 照做不會出錯,只是措辭。

引句:「Lumos 派的 Sonnet 席不在安全區,唯一通用防線是不把表態放進去」

**歸因**:有證據的修補新增字句,屬修補引入的措辭問題。

---

### 固定席判定(LUMOS-IMPACT)
- `Issues/code-loop守衛main-direct盲區`、`Systems/bound-tests-gate`(INVARIANT:受波及合約測試逐支真跑)、`Systems/pitfalls-code-loop`、`Systems/loop-convergence-recording`、`Systems/reversibility-governance-ledger`:diff 沒動閘判定邏輯,只加「印下一步」。判不影響。
- `Systems/lumos-cli-read` 的 INVARIANT 說 search 排除 `status=superseded` 節點。那是節點層級的作廢,不是這次的行層級作廢,判不影響。
- `Systems/design-loop` 與 `Systems/測試假綠形態`:本席不在其範圍,但 `測試假綠形態` 要求修法要有前置斷言證明現場成立。新測試用假 lumos 記下的真實呼叫比對(獨立判準),符合,但有 R1 的盲點。
- 殘留段:鏡頭算不出殘留。我讀了 diff:沒動 `governance/residual-index.json`,治理帳只多 4 筆 anchor 的 blocked 與 approved 事件,沒有殘留或問答列,不用逐條回答。

### 本案特定鏡頭(濾除作廢行後,誰需要看到作廢行)
- 規格閘相依回歸 `_contract_texts`:作廢合約的 `[test:]` 不再算回歸綁定。合理,測試有蓋。
- 派工鏡頭 `_lens_contract_lines`、`_lens_contract_rows`:統計列是用同一份 rows 算的,顯示行與統計行一致。
- 計劃風險理由 `_door_linked_signals`:唯一一個會因濾除而放寬的呼叫者,見 R3。
- doctor 與 extract_contracts 的 20 幾個呼叫者沒動,作廢行仍算,維持原狀。
- 我沒找到其他需要看到作廢行的呼叫者。

## 三問

**① 原問題的修復效果**
- 修前版本 3b76b68 的 hook 搭修後的新測試(同一組 `-k t_prepush_next_step_is_the_call_the_gate_ran`):`18 passed, 22 failed`。
  - 原因是新分支首推與推標籤時,印的範圍不等於閘實際呼叫。
  - 例如 home 印 `4b825dc…..head`(空樹),實際是 `base..head`。
- 修後 e4190cab7:同一支測試 `40 passed, 0 failed`。
- 分支名帶分號時,整行貼進 `/bin/bash` 能還原成原始參數(③)。
- `t_prepush_blocked_last_line_is_next_step`:`2 passed`。
- `t_prepush_summary_records_event`:`3 passed`。
- `t_superseded_contract_not_sent`:`9 passed`。

**② 修補處的正常、錯誤與相鄰路徑**
- `_cl_next` 在 `/bin/bash` 3.2.57 與 `set -u` 下,`_ba`、`_kg` 空陣列與非空陣列都展開正常。
- 分支名含非 ASCII 時,3.2 輸出 `$'…'` 形式,貼進 bash 或 zsh 仍能還原。
- `_cl_next` 在每條 `pp_record_block code-loop` 路徑之前都已定義。
- 整個 repo 查不到 `--first-range`、`_PUSH_SUMMARY_NEXT`、`_PP_CUR_RANGE` 等舊名殘留。
- `note-audit reread-check` 的接線檢查要求同行有 `--gate`,新增的那一行有帶。
- 舊 lumos 配新 hook 走簡版彙總,測試 ⑥ 綠。
- 我手工驗過 `_PP_NBLK=1` 時 `_PP_FIRST_NEXT` 會設成第一筆的 `$4`。但「多 ref 推送時第一筆是哪一個」沒有自己的測試案例。
- 衍生資料與時間:在未提交檔或暫存檔跟掛鉤當下不同時,doctor 重跑不帶 `--touched-from`,是閘的超集。只在 home 與 drift 這類以舊 `lsha` 為範圍的指令上,修好後再提交,重跑該指令仍看舊範圍。這是「看修法」而非「驗證已修好」的語意。未驗:我沒在真實 git 流程實跑。

**③ 新發現在修前與修後各是什麼**
- R1:修前沒有同形的測試比對可比。修後兩個改壞都測不到。
- R2:修前與修後相同,不在修補差異。
- R3:基底回傳風險訊號,修後回傳空,來自 3b76b68。
- R4:兩版本相同,設計層。
- R5:修前基準線對的是 3b76b68 的內容,修後對不上最終檔。
- R6:修補才寫出的字句。

**零 finding 的主要 hunk 驗證**
- `_PP_FIRST_NEXT="${4:-}"`:`40 passed`,「①兩道都擋 → 指第一筆」綠。
- 全套紅與 autoloop 紅補上的「下一步」:`t_prepush_blocked_last_line_is_next_step` 兩項綠。

**未驗範圍**
- 全部 `-k prepush`。
- 真實 `git push` 的最後一行(R4)。
- 完整測試套件。
- 研究筆記更正只抽查了 ETH v3、Mitropoulos 表 II、auto mode 的 89% 與 17%、ImpossibleBench 的 79%、d1 到 d2、TDAD,都與來源一致。其他更正沒逐條對。

本報告最高等級:major
