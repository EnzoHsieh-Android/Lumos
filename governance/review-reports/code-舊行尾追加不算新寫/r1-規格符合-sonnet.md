severity: minor

審查依據:spec 為 `docs/lumos-toolchain-knowledge/Projects/舊行尾追加不算新寫_計劃.md`,diff 為 `/tmp/code-tail-r1-code.patch` 與 `/tmp/code-tail-r1-notes-tests.patch`。我只對條款,沒有跑測試。

## 縮水

**P1 筆記內容審_計劃 沒有補〈做法〉判定檔 `tail` 欄與〈判定者能不能用〉第 2 版一列**
severity: minor
blocking: 否 — 只是文字與紀錄層的同步,不會讓實作者交出錯行為
引句:「ctx = lines[max(0, i - 3):i - 1] + lines[i:i + 2]」
1. 引自 spec〈做法〉8:「[[Projects/筆記內容審_計劃]]:〈判定者能不能用〉補第 2 版結果那一列;〈做法〉判定檔格式補 `tail` 欄。」
2. notes-tests patch 的 `diff --git` 清單裡沒有 `Projects/筆記內容審_計劃.md`。spec 〈做法〉4 的接線守門也要讀這份(派工詞第 2 版驗收結果的那一列)。
3. 同一點讓 [S39] 無法在 diff 內核對:派工詞升到第 2 版,但 diff 裡沒有回歸組 68 句與補括號組 9 句的結果。見下方 ⚠1。
4. 這一條只看 diff 清單,我沒有去 repo 內另查該檔。

**P2 spec 點名要同步的 docstring 有 4 支沒更新**
severity: minor
blocking: 否 — 文字層面
引句:「"""清單檔 → (內容, 清單指紋)。本文=頂端提交+逐行;指紋=本文的雜湊(開頭不算,所以開頭能寫出指紋給判定者照抄)。"""」
1. 引自 spec〈做法〉8:「`_note_audit_render_list`(多印兩行)、……`cmd_note_audit_record` 與 `cmd_note_audit_skip`(涵蓋改走共用的那支)、`_note_audit_parse_verdict` 與 `_note_audit_fold`(`tail` 欄)」。
2. `_note_audit_render_list` 的 docstring 在 diff 裡是原樣的上下文行,只加了行內註解。
3. `_note_audit_parse_verdict` 的 docstring 同樣原樣,只加了行內註解 `# 只判句尾的範圍欄`。
4. `cmd_note_audit_record` 與 `cmd_note_audit_skip` 的 docstring 在 diff 裡沒出現。
5. skip 在 repo 內的 `scripts/lumos:29978` 起仍是舊 docstring。
6. 其餘點名的 docstring 都已改:`cmd_note_shape`、`_note_shape_eval`、`_note_shape_doctor_lines`、`_ns_diff`、`_notelines_parse_added`、`_note_audit_items`、`_ns_negation_collect`、`_ns_negation_hints`、`_note_audit_fold`、`_note_audit_doctor_lines`、`_drift_m1_fit`、測試 `t_note_shape_block_message_and_fail_open`。

**P3 送審清單的「舊句」那行沒有照原位元組印,CRLF 筆記的 CR 被丟掉**
severity: minor
blocking: 否 — 只影響清單顯示,判定與涵蓋不看這行
引句:「body.append(f"舊句(起點版本已有,不在這次判的範圍): {it['old']}")」
1. 引自 spec〈做法〉4:「兩行都照原位元組印(CRLF 筆記不換掉 CR,同既有 PITFALL)」。
2. `it["old"]` 在 `_note_audit_mark_appended` 裡設成 `o.rstrip()`(`it["old"], it["appended"] = o, it["text"][len(o):]`),舊行尾端的 `\r` 已被去掉。
3. 「只判這次補在句尾的」那行用 `it["appended"]`,是從原行切下的,保留 CR。兩行因此不一致。
4. 重現:CRLF 筆記補括號後 `note-audit prepare`,清單的舊句行沒有 `\r`。我沒有實際跑,是從 diff 推得。

**P4 [S17] 綁的測試名 `t_ns_append_rule_hints` 不存在**
severity: minor
blocking: 否 — 斷言內容存在,只是綁定名稱對不上
引句:「+- [S17] 當補更正的是 RULE 行,前綴提醒 應 照現行出 [test:t_ns_append_rule_hints]」
1. notes-tests patch 新增的測試只有:`t_notelines_parse_hunks`、`t_notelines_parse_git_config`、`t_ns_append_old_line`、`t_ns_append_negation`、`t_ns_append_refs`、`t_ns_append_bypass`、`t_ns_append_edits`、`t_ns_append_limits`、`t_ns_append_context`、`t_ns_append_rename_binary`、`t_ns_append_base_read`、`t_ns_append_eol`、`t_ns_append_ledger`、`t_ns_append_wake`、`t_ns_append_push_range`、`t_ns_append_cumulative`、`t_ns_append_doctor`、`t_ns_append_failure`、`t_note_audit_append_marks`、`t_note_audit_append_failure`、`t_note_audit_append_scope`、`t_note_audit_judge_template_pinned`。
2. 沒有 `t_ns_append_rule_hints`。
3. S17 的斷言實際寫在 `t_ns_append_old_line` 的檢查 ④(該測試 docstring 標了 `[S1][S16][S17]`)。
4. 若 spec 綁定機制按 `[test:名稱]` 找函式,這條會找不到。

## 未實作

無程式碼層的未實作。[S39] 見 ⚠1。

## 多做

無。diff 裡沒有 spec 沒對應的行為變更。下面兩點是實作細節,見 ⚠2,不列 finding。

## ⚠ 交編排者

1. **[S39] 派工詞驗收(manual)。** 範本已改、版本已升到 2、雜湊已釘(`t_note_audit_judge_template_pinned`)。但 diff 裡沒有回歸組 55/13 的門檻結果,也沒有補括號組 9 句的結果。spec 要求記進 筆記內容審_計劃。這是不是上線前必須完成的人工關卡,請編排者裁定。
2. **送審清單標頭多了 ` | 尾 <16碼>` 標記。**
   - `_note_audit_parse_list` 因此多回 `tails` 欄,`_note_audit_scoped_row` 靠它讓 record 寫出 `tail`。
   - spec 只說「record 寫的那一列多一個可省略的 `tail`」,沒講怎麼從清單傳過去。
   - 這是清單檔格式的可見變更,但不影響判定語意。我判為實作手段,不算多做。
3. `_ns_append_candidates` 多限制 `b.endswith(".md")` 與路徑不含換行。spec 沒寫,但配對只發生在圖譜 `.md`,我判為無害。

## 已實作

| 條款 / 項目 | 裁定 | diff 佐證 |
|---|---|---|
| S1、S2、S3、S4、S5(第一層扣減與否定提醒) | 已實作 | `_ns_append_subtract` 加 `_ns_viol_key`:行號引用與釘版本用(規則, 片段),回頭條件三種用(規則, 改法),其餘用規則名,做 Counter 扣減。`_note_shape_eval` 的 `line_viol` 對新舊行各算。`_ns_negation_hints` 只留 `h[1] >= len(ovis)` 的命中。 |
| S6、S7、S8、S9 | 已實作 | `_ns_append_candidates` 只留刪加行數相等的改動段(`len(dels) == len(adds)`),按位置 `zip`。`_ns_is_tail_append` 用 `startswith` 並要求新行比舊行長,縮排要一樣由 `startswith` 保證。 |
| S10 | 已實作 | 常數 `_NS_APPEND_MIN_OLD`=8、`_NS_APPEND_MAX_TAIL`=300、`_NS_APPEND_MAX_LINE`=2000。`_ns_paren_groups_only` 認半形全形混用與巢狀,群外有字就不算。 |
| S11 | 已實作 | 兩邊都 `rstrip()` 比;`_ns_append_same_context` 用 `split("\n")` 且不換 CR。 |
| S12 | 已實作 | `_ns_append_same_context` 比 `_ns_is_regen`、`_notelines_regions`、`_visible_lines`。 |
| S13 | 已實作 | `a != b`、`None`、非 `.md` 都略過;`-M` 沿用。 |
| S14、S15 | 已實作 | `_nodehome_cat_blobs_capped(..., _NS_APPEND_BASE_MAX_BYTES)`;起點行對不上、`UnicodeDecodeError` 都只讓那一篇回 `{}`。表鍵用 `nfc(b)`,取內容用原樣路徑。 |
| S16 | 已實作 | `_NS_REVISIT_RULES` 含「條件寫在不評估的地方」。 |
| S17 | 已實作(綁定測試名見 P4) | `_ns_rule_hints` 未動,沒有被扣減。 |
| S18 | 已實作 | `_ns_relaxed_record`:kind `relaxed`、`state` `done`、`check` `append-only`、`base_sha`、`head_sha`、`violations`、`rules`、`pairs`、`pairs_total`;經 `_gate_event_fit(list_key="pairs")` 裁到 4096 位元組。 |
| S19 | 已實作 | `relaxed = None if staged else {}`;doctor 與跳過逃生口不傳 `relaxed`。`_ns_relaxed_settle` 把被喚醒報過的行整行從 `fin` 拿掉。 |
| S20 | 已實作 | 扣減發生在 `viol.extend(pv)` 之前,喚醒那一路沿用原邏輯。 |
| S21、S22、S23、S24、S38、S41(範圍與起點) | 已實作 | 配對起點用呼叫端自己的 `base_where`:提交前是釘住的 HEAD sha,`_ns_diff("--cached", base_where, ...)`;其餘是 `_ns_diff(base_where, tip_where, ...)`。`not base_where or == _EMPTY_TREE_SHA` 回 `({}, None)`。 |
| S25(doctor) | 已實作 | doctor 沿用 `_note_shape_eval`,訊息改列出幾種可能並帶 `_NS_APPEND_MAX_TAIL`。 |
| S26 | 已實作 | `_notelines_append_pairs` 吞例外,回 `"git"` 或例外類別名;`_ns_relaxed_record` 對應 `git-failed` 或 `error`,並帶 `error` 欄(`error` 欄只在非 git 失敗時帶)。 |
| S27 | 已實作 | `_note_audit_mark_appended` 經 `_NotelinesPairs.table()`,失敗回空表,整行送審。 |
| S28、S29 | 已實作 | `_notelines_parse_hunks`、`_notelines_hunk_line`、`_notelines_header_line`:照 `@@` 計數吃行,`diff --git` 重置;`_notelines_parse_added` 改包它。 |
| S30 | 已實作 | `_ns_diff` 加 `--inter-hunk-context=0` 與 `--diff-algorithm=myers`;上下文行會切改動段並計入行號。 |
| S31、S32 | 已實作 | `_note_audit_mark_appended` 的「同編號全配到同一句」規則;`render_list` 多印兩行(位元組問題見 P3);完成審的行不標。 |
| S33 | 已實作 | `_note_audit_fold_scoped` 加 `_note_audit_class_for`,prepare、record 尾端、check、check 工作目錄份都改用它。skip 與 doctor 沿用 `_note_audit_fold`,現在對同編號所有 `tail` 取最重,正是 spec 要的「看任何 `tail`」。 |
| S34 | 已實作 | `_note_audit_doctor_lines` 沿用 `_note_audit_fold`,不比範圍。 |
| S35 | 已實作 | notes-tests patch 把測試改成 `_NOTE_AUDIT_PROMPT_VERSION` 減一。 |
| S36 | 已實作 | `_drift_m1_fit` 改呼叫 `_gate_event_fit(list_key="rows", then=cap_nodes)`。`cap_nodes` 只在 `len>20` 才截並設 `rows_truncated`,與舊行為等價。 |
| S37 | 已實作 | `t_note_audit_judge_template_pinned` 釘 `(2, 雜湊)`。 |
| S40 | 已實作 | `_note_audit_parse_verdict`:`"tail" in r and not isinstance(r["tail"], str)` 回 `None`。 |
| 〈做法〉1 其餘 | 已實作 | `_NotelinesPairs` 用到才算、帶 `failed`/`error`。`_notelines_append_pairs` 回 `(表, 原因)`。`_NotelinesNet` 未動。 |
| 〈做法〉3 前綴提醒不套用 | 已實作 | `_ns_rule_hints` 未動。 |
| 〈做法〉4 範本、版本、`tail` 傳遞 | 已實作 | 範本新段在規則段與輸出段之間,優先於規則 2 與 5,不含 `{{` 與 Output。`_NOTE_AUDIT_PROMPT_VERSION` 為 2。record 經 `_note_audit_scoped_row` 寫 `tail`。 |
| 〈做法〉5 `_gate_event_fit` 簽名 | 已實作 | `(repo_root, gate, kind, note, extra, list_key, *, hard, head_sha, nodes, then)` 回 `nodes`,量的與寫的是同一行(用 `_gate_event_build`)。 |
| 〈做法〉5 不加 `_SLOT_METRIC_KINDS` | 已實作 | diff 未動。 |
| 〈做法〉7 doctor 訊息 | 已實作 | 見 S25。 |
| 〈做法〉8 skill 子檔 | 已實作 | `03-寫回圖譜.md` 與 `06-代碼審與推送.md` 都已改,含 `reset --soft` 重提、`amend` 不行、已推上去只能再補一段括號。 |
| 〈做法〉8 其餘節點同步 | 已實作 | 從 patch 檔案清單看,Issues/治理帳多個寫入者都沒上鎖、否定現況句配回頭條件_計劃、存量漂移防線_計劃、筆記形狀擋_計劃、筆記格子寫法與過期檢查_計劃、reversibility-governance-ledger、存量漂移守衛、筆記內容審、筆記內容閘都有改動。筆記內容審_計劃缺,見 P1。 |

縮水+未實作共 4 條,最高嚴重度 minor,blocking 0 條
