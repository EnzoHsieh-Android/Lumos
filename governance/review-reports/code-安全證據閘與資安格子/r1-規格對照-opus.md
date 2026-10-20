severity: major

## 結論
兩份計劃的條款大部分都已實作，綁定的測試多數也真的驗到行為。有 3 處照規格字面會做出錯誤行為（major），其餘是輸出精度不足或測試沒測到條款裡的部分情境（minor）。

---

### 1. review／deployment 審查紀錄的綁定可以不涵蓋家節點的程式檔：改了程式，人審紀錄不會失效
severity: major
blocking: 是
引句:「綁定集合至少要涵蓋：護欄所在 Systems 節點（護欄的家）about_code 列的全部程式檔」
引句:「綁定的程式與護欄 revision 等於要推的提交，一變判 stale」
diff 佐證：`_secev_judge_item` 寫 `probs += _secev_bindings_problems(it, ctx, ctrl, home_about if kind not in ("review", "deployment") else ())`；另外 `_secev_ip_lists` 允許 `bindings` 是空陣列。所以一筆 `bindings: []` 的人審紀錄在程式改動後永遠不會 stale，跟 驗收閘 d2「綁定的程式或護欄修訂一變就要重審」衝突。綁定測試 t_secev_s09_bindings 只驗了 behavior。

### 2. 工具清單讀不出來時，照樣套用替代欄（規格要求不替代）
severity: major
blocking: 是
引句:「清單讀不出來時不做任何替代，照原最低種類判。」
diff 佐證：`_secev_stage_ctx` 拿到 `perr` 只做 `run.rep["warnings"].append(perr)`，清單變成 `{}`；`_secev_min_kinds` 用 `have = {t["category"] for t in tools.values() ...}` 算有沒有工具，空清單等於「每類都沒工具」，於是全部走替代欄（例如 static_analysis、secret_scan 改成 review 多蓋 manual_check_scope），最低種類反而變鬆。主線清單若讀得出來，`_secev_tool_freeze` 會把主線那幾列補回來，洞因此變窄；但新 repo、或主線清單也壞掉時，洞照樣存在。

### 3. 主線只取第一個候選，分岔點也只對那一個算，沒有用全部候選
severity: major
blocking: 是
引句:「分岔點照 `_push_range_start` 的算法，`git merge-base --all <頂端> <全部候選>`」
引句:「git-flow 與 fork 兩頭顧不到（固定順序取第一個會錯）」
diff 佐證：`_secev_mainline` 回 `return cands[0][1], f"主線 {cands[0][0]}", None`；`_secev_stage_head` 用 `_secev_git(run.repo_root, "merge-base", run.sha, run.ml)` 只對這一個算。這正是規格點名會錯的「固定順序取第一個」。t_secev_s52_mainline 沒有多候選的情境。

### 4. 沒強制把「產生校準樣本的腳本」綁進 bindings ⚠
severity: minor
blocking: 否
引句:「產生校準樣本的腳本要在 `bindings` 裡」
diff 佐證：`_secev_bindings_problems` 只把 `calibration_path`（校準輸出檔）加進必綁集合。圍欄的鍵表沒有任何欄位指名那支腳本，照規格做不到。這是規格缺口，交編排者裁：要嘛補一個欄位，要嘛把 驗收閘[S9] 改成綁校準輸出檔。

### 5. 7 天內到期的提醒少了 gate 設定、人審核可、修訂核可、金鑰四種
severity: minor
blocking: 否
引句:「放行時也印提醒：7 天內到期的核可（例外、gate 設定、人審、修訂、金鑰）」
diff 佐證：`ctx.remind(` 只出現在四處：例外、審查紀錄自己的 `expires_on`、vulndb、considerations。核可鏈上 gate_setting、human_review、revision、approvers_* 那幾筆的到期都沒有提醒。

### 6. 未實作沒被引用的證據項提醒 `orphan_evidence_item`
severity: minor
blocking: 否
引句:「沒有任何護欄引用的項只列提醒 `orphan_evidence_item`、不擋」
diff 佐證：整個 diff 沒有這個代碼。`_secev_node_items` 只挑 `control_id == rec["id"]` 的項，其餘直接忽略。

### 7. `security list` 開頭沒印「狀態詞不通用」那一行
severity: minor
blocking: 否
引句:「兩邊的文字與 JSON 輸出各在開頭印一行」
diff 佐證：`_SECEV_WORDS_NOTICE` 只用在 `_secev_skeleton` 與 `_secev_render`（security evidence）；`_secinv_render` 與 `_secinv_build` 都沒加。

### 8. `_SECINV_NOTICE` 沒改
severity: minor
blocking: 否
引句:「唯讀：盤點與證據判定；寫入在 code-loop 族」
diff 佐證：parser help 與 `HELP_WHEN["security"]` 改了，但 `_SECINV_NOTICE = "唯讀盤點,不是安全驗收"` 原樣保留，只多一行註解。

### 9. 不算數的 considerations 列沒附原因（提問）
severity: minor
blocking: 否
引句:「輸出另列這些不算數的列與原因，留著不刪也不出錯」
diff 佐證：`_seccell_cell` 只放 `cell["not_counted"] = [x["where"] ...]`；`_secev_consideration_counted` 只回 True/False，沒說為什麼不算數。

### 10. JUnit 遇到 DTD 或 XML 語法錯時沒丟帶型別的拒收，呼叫端改用比對訊息字串
severity: minor
blocking: 否
引句:「XML 語法錯或含 DTD→`report_unparseable`」
引句:「各呼叫端比對例外訊息字串」
diff 佐證：`_JUnitStream.doctype` 丟的是一般 `ValueError("DTD/entity declarations not accepted")`，`ET.ParseError` 也沒轉成 `JUnitRejected`；`_secev_junit_facts` 用 `"report_unparseable" if "DTD" in str(e) else "report_malformed"` 判。這正是 test-quality-cli 的 WHY 否決過的做法。

### 11. 逐種類那一列的「綁定的版本」只印數量
severity: minor
blocking: 否
引句:「證據檔路徑、工具名與版本、綁定的版本、觀察時間、例外到期日」
diff 佐證：`_secev_judge_item` 輸出 `"bindings": len(it["bindings"])`；例外到期日只放在護欄層，種類那一列沒有。

### 12. 版本變更說明沒寫這一道新判定 ⚠
severity: minor
blocking: 否
引句:「`lumos update` 的版本變更說明都要寫出這一道新判定」
diff 佐證：repo 有 CHANGELOG.md，但這條分支沒改它。可能算發布步驟的事，交編排者判。

### 13. 驗收閘[S18] 的綁定測試沒測「需求修訂」那種情境
severity: minor
blocking: 否
引句:「當需求修訂、實作或 `environment_ref` 指的環境描述檔改了之後套用舊證據時,真實推送應被擋下並判 stale」
diff 佐證：t_secev_s18_real_push_stale 只真推了「改實作」與「改 Dockerfile」兩種；revision 改了的情境只在不真推的 S9 測試裡。

### 14. 驗收閘[S26] 沒測 rebase
severity: minor
blocking: 否
引句:「合格核可的例外在壓提交、rebase 與合併提交之後應仍有效」
diff 佐證：t_secev_s26_signatures 只做了 `reset --soft` 壓提交與 merge。

### 15. 驗收閘[S27] 沒有三道同時擋的樣本
severity: minor
blocking: 否
引句:「當安全證據判定與表態閘、新增告警閘同時擋下而帶 `--keep-going` 時,三道應各自出訊息」
diff 佐證：t_secev_s27 的合成 repo 只有安全證據那一道擋，docstring 自己也承認多道同時擋交給別支測試。

### 16. 驗收閘[S41] 沒驗「同一份檔只算一次額度」
severity: minor
blocking: 否
引句:「同一份檔被多條護欄引用時應只算一次額度」
diff 佐證：t_secev_s41_s43 的總量情境只斷言兩次跑超限的是同一批，沒有共用檔加總的對照。

### 17. 驗收閘[S45] 沒測「自然過期」的 gate_setting
severity: minor
blocking: 否
引句:「沒有核可、核可過期、值看不懂或是 off」
diff 佐證：t_secev_s45 測了 31 天和貼回舊筆（斷鏈），沒有一筆原本有效、今天已過期的核可。

### 18. 驗收閘[S30] 的早退情境只測一條
severity: minor
blocking: 否
引句:「當安全判定遇到取不到 HEAD、merge-base 等於 HEAD、算不出 merge-base 或 pitfalls 失敗這些既有放行早退時」
diff 佐證：只測了「merge-base 等於 HEAD」（在 main 上跑 check）。pitfalls 失敗、算不出 merge-base 都沒有樣本；結構上安全那一步排在最前，風險不大。

### 19. 驗收閘[S55] 只驗了「列出變弱」，沒驗「真的照主線那一列判」
severity: minor
blocking: 否
引句:「閘應照主線 tip 版那一列判」
diff 佐證：t_secev_s55 只看 `rep["freeze"]["tool_list"]` 的說明，沒有任何證據項真的被主線那一列（例如較高的 min_requests）擋下。

### 20. 驗收閘[S31] 沒測「改用最低種類較少的表版號」
severity: minor
blocking: 否
引句:「或改用最低種類較少的表版號」
diff 佐證：t_secev_s31 沒有表版號的樣本。t_seccell_s10 已示範可以用測試接縫多塞一版表，這裡沒用。

### 21. 提問[S13] 規格閘那一半只驗了開頭字樣
severity: minor
blocking: 否
引句:「spec-gate 對連到有資安登記 Systems 的計劃應印出護欄、連到的入口上的 open 格子數與全庫 open 總數而不擋」
diff 佐證：綁定的 t_secq_s09_s13 只驗 hint；t_seccell_s20 的對照只檢查 `"[spec-gate] 資安登記: 連到的節點登記了"` 這個開頭，沒驗格子數與全庫總數的數值。

### 22. 驗收閘[S51]、[S52] 各有一種情境沒測
severity: minor
blocking: 否
引句:「因主線認不出、鏈分岔或取不到提交擋下時,warn 應無效並印出原因」
引句:「有 remote 但沒有追蹤 ref、或 git 查詢逾時」
diff 佐證：t_secev_s51 沒有 commit_unavailable 加 warn 的樣本；t_secev_s52 沒有 git 逾時的樣本。

---

### 多做 1. revision 核可的 target 自訂成「護欄 id|decision_ref」
severity: minor
blocking: 否
規格表寫的是「`revision` | 護欄 id」。diff：`_secapr_c_revision` 寫 `raise ValueError("revision 的 target 寫 <護欄 id>|<decision_ref>")`；`_secev_revision_ok` 用 `startswith(cid + "|")` 比對。

### 多做 2. 核可鏈每一筆多了選填鍵 `outcome`
severity: minor
blocking: 否
規格寫明每筆的鍵「不准有未列的鍵」。diff：`_secapr_entry_shape` 寫 `if set(e) - {"outcome"} != need`；payload 那邊寫 `body["outcome"] = outcome`；`_secapr_entry_dates` 靠這個鍵決定 consideration 的到期上限是 30 天還 180 天。

### 多做 3. 從 `environment` 字串解析壓測與動態掃描的目標 ⚠
severity: minor
blocking: 否
規格說 `environment`「只記不比對」，但 diff 用 `_secev_target_host(it["environment"])` 抽 `target=` 來判 target_not_authorized。規格本身沒有「目標位址」欄位，交編排者決定要不要補欄位。

### 多做 4. `--questions --plan` 掃整份計劃全文去重，不只看 pending_questions
severity: minor
blocking: 否
diff：`have = set(re.findall(r"\[cell:([^\]\s]+)\]", plan_text or ""))`。正文裡提到某個 cell id 也會讓那一題不再輸出。

### 多做 5. 例外缺欄位時改成整道擋，而不是只讓例外不算數 ⚠
severity: minor
blocking: 否
diff：`_sc_exception` 在 v2 把 `compensating`、`covers_kinds` 列成必填，缺了就是 invalid_record，到閘門變成整道 `registration_error`（而且可以用 gate_setting 降成只提醒）。規格〈擋下條件〉寫的是缺欄位時「例外不算數，底下的種類照原判定」。另外 v1 例外沒有 `covers_kinds`，會判成 `exception_fields_missing`，規格寫的是 `exception:exception_unapproved`。

---

### 已實作（簡表）
| 條款 | 佐證（函式／hunk） |
|---|---|
| 驗收閘 S1、S2 | `_codeloop_security_step` 沒登記回 None；cmd_code_loop 的 `--json` 加 no_registration 鍵；`_secev_active_sec` 只收含 security 的條目 |
| 驗收閘 S3、S47、S51 | `_secev_stage_reports`（read_incomplete、registration_error）；`_secev_freeze_removed`；`_SECEV_WARN_OK` |
| 驗收閘 S4、S28 | `cmd_security_evidence` 與 code-loop check 共用 `_secev_evaluate`；inventory_report 由 `_secinv_build` 產生 |
| 驗收閘 S5–S7、S16、S17、S59 | `_secev_judge_junit`、`_secev_junit_declared`、`fault_check`、`ReceiptRejected`、`_secev_kind_verdict` 取最差；`JUnitRejected` 加 `_JUnitStream` 深度上限 |
| 驗收閘 S8、S20、S39、S40、S62 | `_secev_judge_review`、`_SECEV_JUDGMENTS`；human 要核可鏈上的 human_review、雜湊蓋整份紀錄 |
| 驗收閘 S9（S4 那條除外）、S10、S44 | `_secev_bindings_problems`、`report_sha256` 比對、`_secev_item_dates` 用 committer date |
| 驗收閘 S11、S12、S58 | `_secev_judge_sarif`、`_secev_sarif_run`、`_secev_coverage_ok`、`_secev_sarif_calibration`、suppression 要核可 |
| 驗收閘 S13、S22 | `_secev_judge_k6`、`_secev_k6_thresholds`、`_secev_loopback` |
| 驗收閘 S14、S57 | `_secev_control_table`、`_secev_min_kinds`、`_SECTT_APPROVED` |
| 驗收閘 S15 | `_secev_question_open` 照 `_pq_settled` 判；`_pq_node_target` 從 `_pq_decision_target` 抽出 |
| 驗收閘 S18、S19 | 合成 repo 真推送 |
| 驗收閘 S21、S33、S34、S35、S36 | `_secev_tools_load`、`_secev_item_tool`、`_secev_fence`、`_secev_node_items`、vulndb 14 天 |
| 驗收閘 S23–S26 | `_secev_exception`、`_secev_log_exception_use`（冪等鍵帶核可鏈 seq） |
| 驗收閘 S27、S32、S60 | pre-push 的 `pp_cl_reason` 與非分支路徑 `--security-only`；`_cl_say_sec_block`；ci.yml 的 security_tag 工作 |
| 驗收閘 S29、S31、S53、S54、S55 | `_secev_stage_freeze`、`_secev_weaker`、`_secev_strict_merge`、`_secev_frozen`、`_secev_tool_freeze` |
| 驗收閘 S30、S52 | 安全那一步排在所有早退之前；`_secev_mainline`（新 repo 當空樹、mainline 設定、force push 退版）；主線認法見發現 3 |
| 驗收閘 S37、S38 | `_secev_gk_backing`、`_secev_gk_group`、`cmd_codeloop_security_backing` |
| 驗收閘 S41–S43 | `_secev_budget_prepass`、`ctx.cached`、`_secev_loads` 深度上限、`evaluation_error` |
| 驗收閘 S45、S46 | `_secev_config`、`_secev_stage_chain`；`_sc_v2` 加 `ver` 參數 |
| 驗收閘 S48–S50 | `_secapr_verify`、`_secapr_entry_status`、`cmd_codeloop_security_approval_add` |
| 驗收閘 S56 | `_secinv_snapshot_tree`、`_secev_snap_clash`、evidence_node_too_large |
| 驗收閘 S61、S63 | `_secev_doctor_lines`；security list 不起程序、標 considered_unverified |
| 提問 S1–S3、S5、S10、S14–S22 | `_seccell_plan`、`_seccell_cover_row`、`_seccell_state`、`_seccell_cons_index`、`_seccell_questions`、`_SECCELL_LIMIT`、`_spec_gate_security_line` |
| 提問 S4 | `_secev_consideration_counted`（30 天、180 天、到期日比對） |
| 提問 S6–S9、S11、S13 | `_REQ_SEC_*` 詞表、`_facet_triggered`、`hint` |
| 提問 S12 | `_SECTT_TABLES` 加 t_sectt_drift |

### 計劃正文跟決策欄（或彼此）矛盾的地方
- 驗收閘〈接手先讀〉寫「本篇自己的決策寫 d1–d10」，但決策欄已經到 d16。
- 驗收閘〈二〉「表還沒核可時」那段還寫著表未核可、沒有鏡像常數；但下一行 REVISIT 已經結案，d11 與程式的 `_SECTT_APPROVED={1}` 都是已核可。「設計內容暫在姊妹計劃」也跟姊妹計劃寫「正本在 Systems/資安威脅類別表」衝突。
- 驗收閘〈擋或只提醒的設定〉寫「使用者要給過渡期（Q4）」，跟 d13「不給過渡期」衝突。
- 提問〈四〉寫「not_applicable 最長 180 天（見 d4）」，但 d4 已作廢，現行的是 d9。
- 程式註解 `_SECTT_TABLES` 上方寫「經使用者核可升版號」，跟 提問 d5 的雙家協定衝突（`_SECTT_APPROVED` 那段註解寫的是對的）。

縮水+未實作共 22 條
