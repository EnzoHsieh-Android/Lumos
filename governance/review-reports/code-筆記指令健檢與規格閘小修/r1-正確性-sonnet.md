severity: major

審的是 `r1-lumos.patch`(主程式)。三條 major 都附能重現的輸入,下面第一、二、四條用 `scripts/test_lumos.py` 的 fixture 在 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/正確性-sonnet/` 跑過。

## Findings

**1. 已完成計劃的留痕過期時,整個跳過不做清單的輕量審檢查,原本會擋的推送被放行**
severity: major
blocking: 是
- 位置:`_spec_gate_push_one` 新增的 `if done:` 分支,放在 `_spec_gate_push_light` 之前。
- 問題:改前,推送範圍改到的 done 計劃會走 `_spec_gate_push_nogo_only`,重判不做清單,略過危險詞就要求輕量審。改後,done、被碰到、又有風險低留痕的計劃會變成 `full`。留痕過期時,函式在 `stale` 那行就回「不擋」,不做清單的檢查完全沒跑。
- 例:計劃已通過輕量審。同一次推送把 status 改成 done,並在 `## 不做` 加一條 `- 不做扣款`。條款指紋含不做清單,所以留痕過期。
  - 預期:擋下(輕量審綁的快照跟現在被略過的行不同)。
  - 實際:rc0,只印「提醒:甲_計劃 已完成,留痕對不上現在的計劃…不擋」。
- 重現:`exp1.py`,用 `_sg_push_setup(body=_NGL_BODY)`、`_ngl_review`、`_ngl_push`。
  - 改前版本(0beb6d7d)回 rc1,印「不做清單略過了 2 個危險詞(扣款、退款)…快照裡被略過的那幾行跟現在的不一樣」。
  - 現版本回 rc0。
- 測試抓不到:`t_prepush_spec_gate_done_in_range` 的 ④ 只用沒有不做清單的計劃,拿掉這個繞過仍然全綠。
- 引句:「            return None, f"{P} 提醒:{Path(prel).stem} 已完成,留痕對不上現在的計劃({_esc_clean(stale, 160)}),條款測試這次沒跑、不擋"」

**2. done 計劃只要有一支留痕測試找不到,其他真的紅的測試也不跑,推送放行**
severity: major
blocking: 是
- 位置:`_spec_gate_push_one` 的 `if done and gone:` 在 `_spec_gate_judge_items` 之前就整個提早返回。
- 問題:docstring 寫「真的紅才擋」,實際是只要有一支 dangling 就整份不跑。
- 例:留痕綁 `t_flip` 與 `t_red2`(實作前都紅)。之後把 `t_flip` 改名,`t_red2` 仍然紅,同一次推送把計劃改成 done。
  - 預期:擋下,理由是 `t_red2` 紅。
  - 實際:rc0,輸出「提醒:甲_計劃 已完成,留痕裡的測試找不到(t_flip——改名或刪了?),條款測試這次沒跑、不擋」。
- 重現:`exp2.py`,用 `_sg_push_setup(clauses=[...t_flip..., ...t_red2...])`,把 `def t_flip():` 改名後 `--push-check HEAD~1..HEAD`。
- 測試抓不到:`t_prepush_spec_gate_done_in_range` 的 ⑤ 只有一支測試且全部改名,沒有「一支找不到、另一支紅」的組合。
- 引句:「        return None, f"{P} 提醒:{Path(prel).stem} 已完成,留痕裡的測試找不到({'、'.join(gone[:5])}——改名或刪了?),條款測試這次沒跑、不擋"」

**3. `summary-line`、`summary-add` 的形狀檢查不理 `note_shape.gate=off`,在非 git 目錄也一律擋(既有的 `summary-line` 退步)**
severity: major
blocking: 是
- 位置:`_summary_write_shape_check` 第一步 `_drift_fix_shape_err`,在讀 `note_shape` 設定之前就先擋。
- 問題:docstring 寫「擋不擋照 note_shape 的總開關與 slots 子開關」,但只有第二步(格子)照開關。擋下訊息只建議改 `slots`,對第一步的擋下沒用。
- 例 A:`.lumos/config.json` 設 `note_shape.gate=off`。
  - `lumos note-shape --staged` 回 rc0,印「這個專案把這道檢查關掉了」。
  - `lumos summary-add Systems/Pay 'FACT:付款服務回 200 [confirmed:2026-10-15]'` 卻回 rc2:「要寫進去的文字過不了筆記形狀擋(現況描述沒寫來源…)」。
- 例 B:沒有 git 的圖譜目錄。
  - 改前版本跑 `summary-line Systems/Pay "KEY:甲" "KEY:甲甲"` 回 rc0,正常寫入。
  - 現版本回 rc2:「git 列不出檔案清單,沒辦法先跑筆記形狀擋」。
  - 同一個 helper 也擋 `summary-add`。
- `summary-line` 的新行有 `if not delete` 才跑檢查,所以只刪片段不受影響。
- 測試抓不到:新增的 `t_summary_*` 都用 git fixture 且 gate 預設,沒有 gate=off 或非 git 的案例。
- 引句:「    err = _drift_fix_shape_err(root, [(line, "summary")])」

**4. `_spec_gate_pick` 遇到無法解析的 ts 會 TypeError**
severity: minor
blocking: 否
- 位置:`k = _loop_ts_key(...) or (0,)`。`_loop_ts_key` 成功時回 float,失敗時被換成 tuple,下一行 `k > bk` 就拿 float 比 tuple。
- 例:`_spec_gate_pick({"token":"A","ts":"2026-10-15T10:00:00+08:00"}, {"token":"B","ts":"2026-10-15T11:00:00"})` 拋 `TypeError: '>' not supported between instances of 'tuple' and 'float'`,順序反過來也拋。
- 影響:註解與 docstring 寫「ts 讀不懂的排最前」,實際是整個推送閘崩潰。
- 降為 minor 的理由:`docs/.canary-log.jsonl` 與 `docs/.governance-log.jsonl` 共 127492 列,我用腳本掃過全部帶時區,所以現有資料碰不到,要手改或舊格式的帳才會觸發。
- 測試抓不到:`t_spec_gate_record_in_governance_log` 的 ③ 只測兩筆 ts 都合法的情況。
- 引句:「        k = _loop_ts_key(str(r.get("ts", ""))) or (0,)」

**5. `_git_ignored` 把結尾斜線剝掉,被忽略的整個目錄仍被報成 missing**
severity: minor
blocking: 否
- 位置:`dict.fromkeys(str(x).rstrip("/") ...)`。
- 原因:`git check-ignore -- runtime` 對不存在的路徑回 rc1,因為不知道它是目錄,帶斜線的 `runtime/` 才會被 `runtime/` 規則吃到。
- 重現:repo 內 `.gitignore` 寫 `scripts/runtime/`,筆記寫 `` `scripts/runtime/` `` 與 `` `scripts/runtime/state.json` ``。
  - `lumos refcheck n.md --repo .` 的結果是 `✗ missing scripts/runtime/`,而 `state.json` 那條正確標成 `○ ignored`。
  - doctor P 段同一支 helper,同樣會漏報。
- 引句:「    cand = [p for p in dict.fromkeys(str(x).rstrip("/") for x in paths) if p and not p.startswith("/") and ".." not in p.split("/")]」

## 其他逐項走過、沒問題的
- **`summary-add` 位置與寫入**:縮排取第一條實行、中間夾空行、`--after` 落在續行、`--after` 打到 `summary:` 標題行(回「找不到」),用 `|-` 縮排 4 格加 tags 欄的檔案試過,新行都插在正確位置,`updated` 有改。
- **`_has_line_break` 抽取**:行為跟原寫法一致。
- **`lands_in` 正規化**:`link_target` 去掉 `[[ ]]`、`.md`、別名後再過 `_lands_in_bad`,寫入前會印提醒。
- **`_lint_born_true`**:有條件已成立的行會唸;只有 `when-status` 時不建樹,`tree=None` 沒有問題;混用別種條件的整行不唸;舊行不唸。
- **`_lint_excluded_lines`**:半形全形冒號、引用塊、散文行都跟規格閘判法一致。
- **`_spec_gate_low_not_red`**:(a) 路徑要求條款指紋與門規則版本都相同才 rc0;`--no-run`(verdicts 為空)落到 `other`,不會誤放。
- **`_nodehome_worktree_homes`**:輸出是 bytes,拆 `\0` 型別對;工作目錄已刪的節點會 pop。
- **`book` 集合**:`edited` 裡的節點必在 `N.notes`,兩邊 `about` 都是 list,比較沒有型別問題。
- **否定句 v4**:`_ns_neg_clause_break` 與收尾括號跳過沒找到可舉的具體誤放輸入,所以不報。

## 角色鏡頭
- **be-api-compat**:治理帳新增 `kind=spec-gate-record`,舊讀者看不懂的事件種類會略過。`t_gov_readers_ignore_spec_gate_record` 驗過 doctor S12 與 `lumos gov`。`_SPEC_GATE_PUSH_FIELDS` 加 `token`,對外沒有欄位改名或刪除。
- **be-authz**:沒有新增或改動的端點(純命令列與帳檔),不適用。

## 固定席節點
這份 diff 對下列節點宣稱的行為與合約都沒有破壞。
- `lumos-cli-read`:`search` 的 superseded 過濾沒改。
- `guard-kill`:rc 優先序與 `--json` 純度的程式沒碰。
- `design-loop`:處置閘第五步沒碰。這份 diff 動的是推送前規格閘,不是處置閘。但 finding 1 與 2 動到的是推送閘對輕量審的把關,見上。
- `測試假綠形態`:沒有新增還原翻紅釘。finding 1 到 3 的測試缺口屬同一類。
- `筆記內容閘`、`pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`:有牽連檔,但這份 diff 沒有改變它們記載的行為。

臨時目錄 `/tmp/lumos-seat-work/code-筆記指令健檢與規格閘小修/正確性-sonnet/` 留給編排者收貨後刪,裡面的 `tmp/` 是測試 fixture 暫存。

最嚴重 major;blocking 共 3 條(finding 1、2、3)。
