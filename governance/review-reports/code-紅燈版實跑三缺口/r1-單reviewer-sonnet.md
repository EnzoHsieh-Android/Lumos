severity: minor

整份 diff 我逐 hunk 讀過,並實跑了新增的 10 組測試,全數通過。另外用 `scripts/lumos` 載入成模組,對可疑處走了具體輸入。最高等級是 minor,共 4 條 minor。

## 逐條 finding

### F1 本體簽名改法會讓「搬進巢狀類別」的測試被誤列為測試被刪
severity: minor
blocking: 否
file: `scripts/lumos:48989`(`_tg_functions` 的 `sig`),影響 `scripts/lumos:49665` 的 `_tg_renames`。

測試只是搬進 `inner class`、縮排多一層,本體含多行三引號字串。例如 `val s = """\n    {"a": 1}\n"""` 這種 JSON 或 SQL 固定資料。我對 `_tg_functions` 與 `_tg_renames` 實跑的結果如下:
- 舊簽名(去光全部空白)兩邊相等,`_tg_renames` 認成改名。
- 新簽名 `_tg_ident` 保留字串內空白,縮排不同所以簽名不同,配不成改名。
- `_tg_test_rules` 輸出 `[('tq/test-removed', '改動前有的測試函式不見了(A.t)')]`。
- 同樣的搬法但本體沒有多行字串,輸出為 `[]`。

程式註解、計劃做法 1 與 test-guard 筆記都宣稱「重新縮排照樣不算有變」,對多行原始字串不成立。LF 改 CRLF 也是同一根因。後果是多一條可放行的誤列,不是漏判。新測試沒有覆蓋「縮排不同加多行字串」這一格。

引句:「"sig": _tg_ident(seg_k[close + 1:]) if close >= 0 else ""}」

### F2 多平台改回單平台設定後,新格式留痕會誤判紅並自動記假逃逸
severity: minor
blocking: 否
file: `scripts/lumos:15989` 一帶的 `_spec_gate_push_one`,對應寫入端 `_spec_gate_record`。

新留痕一律寫 `平台:名字`。專案若把 `.lumos/config.json` 的 `platforms` 拿掉、退回舊式單平台設定,這情形沒處理。留痕的條款指紋不含平台設定,所以不算過期。推送前 `split` 為空,`resolve_test_refs` 不切冒號,整串 `jvm:fee_jvm` 被當成測試名,判成「懸空」,再被判成紅。

我用 `_mp_repo` 的 fixture 實跑:
1. 先在多平台設定下跑規格閘,留痕 tests 為 `['jvm:fee_jvm']`。
2. 提交後把設定改成 `{"test_profile":"kotlin-junit","test":{"run_cmd":"python3 run_jvm.py {method}"}}`。
3. 把 `green_fee_jvm` 放好,測試實際是綠的。
4. 跑推送前驗收,結果 rc=1,輸出「留痕裡的測試沒全綠——jvm:fee_jvm:紅」,並印出「逃逸自動入帳」,`.escape-log.jsonl` 多一筆 major。

S5 只處理了「平台改名或刪掉其中一個」。整組平台拿掉的情形仍會誤擋並誤記逃逸,而這正是這次修補想避免的假逃逸。

引句:「tests = sorted({f"{pl}:{m}" for b in clauses for pl, m in refs.get(b["id"], [])})」

### F3 「還沒提交」那句提醒引用了可能不存在的「孤兒那條」
severity: minor
blocking: 否
file: `scripts/lumos:49810`(`_tg_redbase_cands` 的 pending 迴圈)

治理帳被忽略、紅燈版檔只是還沒 `git add` 時,輸出裡只有這一條提醒,沒有孤兒那條。它只說「照孤兒那條的改法改好規則」,卻沒有講改法。改法(去忽略設定檔拿掉或收窄規則、改完看 `git check-ignore -q` 退出碼為 1)只寫在孤兒那句。讀者看不到孤兒那句時,拿到的只有一條規則字串,沒有步驟。S7 只斷言開頭是 `git add`、有講被忽略,抓不到這個缺口。這屬於壞引用。

引句:「照孤兒那條的改法改好規則再把治理帳一起提交」

### F4 計劃宣稱「退回現況切法的兩種寫法,預期值被改時現況本來就列得出」,實測有反例
severity: minor
blocking: 否
file: `scripts/lumos:49087`(`_tg_strip_unreliable`),另見計劃做法 1 與 S2

模板字串含「頂層字面逗號」加「巢狀引號」時,例如 `"${a}, ${f("x")}"`,掃描判不可靠,退回原文切法。原文切法會在字串內的逗號處切開,切成三段,預期值那一半落進「其餘部分」。實測:
- `_tg_expected_changed('assertEquals("${a}, ${f("x")}", s)', 'assertEquals("${a}, ${f("y")}", s)')` 回 False。
- `_tg_pairs` 回 `[]`,不會列出任何候選。

S2 的測試字串 `"${foo("a,b")}"` 剛好有括號包住逗號,舊切法本來就切對,所以沒有暴露這個缺口。這是修補前就有的漏報,沒有變差,但計劃的宣稱失實。S1 想修的「字串預期值被改漏報」在這種寫法仍然漏。REVISIT 條件有涵蓋這一類,所以只列為文件精度問題。

引句:「退回的兩種寫法,預期值被改時現況本來就列得出」

## 已核對、沒問題的部分

**4(a) `_tg_strip_unreliable`**
- 我試了跳脫引號、`'"'`、`'('`、字串內的 `'`、三引號含 `${f("q,r")}`、`${'$'}`、行尾註解。
- 在字串沒收尾、`${` 在段內不配平這兩種情形,都正確退回原文切法。
- 巢狀引號一定出現在 `${` 之後,所以前半段必不配平,不會漏判。
- 「模板段內配平」(`"總計 ${t}, 稅 ${x}"`)被判可靠,是對的。
- 效能:語句有 2000 字的上限,極端輸入(深度巢狀 `${`、連續引號)耗時都在毫秒內。
- 失敗方向只會退回現況,沒有比現況更差的漏判。
- 一個小缺口:`rest != close` 對「以跳脫引號結尾的未收尾字串」(`"abc\"`)會誤認為已收尾。這只出現在非法程式碼,不構成 finding。

**4(b) `_spec_gate_push_one`**
- 補平台:舊留痕整串先逐字比現在條款,只綁一個平台才補,多個平台照預設。含冒號的舊名字(`fee: rounds up`)被正確認回,不會被當成前綴。
- 平台不在設定裡:未完成的計劃擋下並講明,已完成的降成提醒,不丟例外。
- 逃逸:`real` 旗標只在至少有一支不是「環境沒跑起來」時才記。
- 這三段與既有 done/stale 寬待路徑組合時,bad_plat 的提早 return 不會漏掉不做清單那道。
- 已知的小瑕疵:done 加過期留痕加含冒號的舊名字時,提醒會誤講「平台 fee 不在設定裡」。它只是不擋的提醒,修補前會直接崩,現在較好。

**4(c) `_tg_ledger_ignored`**
- doctor 那段用 `_vault_repo_root` 加 `relative_to` 算出相對路徑。vault 在 `knowledge/` 或 repo 根時算得對。找不到 `.git`、vault 在 repo 外或符號連結時,落到 unknown 或 fail-open,不會誤報。
- git 回 128、逾時、deadline 用完都回 unknown,git 子程序有逾時,不會殘留。
- 已追蹤的檔,`check-ignore` 回 1,不算被忽略,符合設計。
- 其他同族呼叫端沒有被帶壞。spec-gate 那端用固定的 `GOV_LOG_REL`,非 `docs/` 佈局時只會漏提醒,不會誤報。

**4(d) 切參數改法對其他規則的影響**
- 其他吃 `_tg_call_parts` 的規則:常值斷言、`_tg_pair_key`、方向互換、`_tg_split_first_arg`。
- 切對之後的差異都是「該列的多列」。例如 `assertTrue("msg, with comma", true)` 現在被判為常值斷言,`assertEquals("a,b","a,b")` 也是,屬於改進,沒有找到變弱的案例。
- `_rg_split_args` 的 Room 守衛呼叫不帶 `stripped`,行為不變。

**3 測試品質**
- fixture 確實走到要驗的分支:治理帳那幾案真的沒追蹤。否定規則那案用 `git reset` 讓治理帳留在工作目錄,fixture 已修正。多平台 fixture 用 `ran.log` 驗證每支測試實際走哪個平台的指令。
- 卷證 `r1-mutation.md` 的 22 點改壞驗證大致可信。
- 沒有專門守衛的小點有三處,都不足以立為 finding:
  - `_tg_strip_unreliable` 內「跳過註解 token」那行(語句已被先剝註解)。
  - `getattr(e, "prefix", "")` 與退回 `t` 的差別(兩條路徑結果相同)。
  - F1 所說的縮排加原始字串。

**2 pitfalls manifest**
- 落在改動行的 lint 命中為 0,和附件一致。

## 圖譜鏡頭(固定席)

| 節點 | 判定 | 理由 |
|---|---|---|
| `lumos-cli-read`(INVARIANT:search 預設排除 superseded) | 不影響 | diff 沒碰 `search` 與濾網。 |
| `guard-kill`(rc 優先序、`--json` 純度) | 不影響 | `_spec_gate_judge_items` 只有四個呼叫端(規格閘、相依回歸、推送前、修正關卡),`guard kill` 走自己的 `_kill_run` 與歸因,沒呼叫它。 |
| `測試假綠形態`(還原翻紅釘須配前置斷言) | 不破壞 | 新測試多數帶 `★前置★`(S1 切法、S6 接上裝置後三條皆紅、S7 治理帳被忽略、S9 寫出紅燈版)。S3 到 S5 沒有獨立前置,但靠 `ran.log` 與 rc 斷言,fixture 不走到分支就會翻紅。 |
| `lumos-cli-lifecycle`(re-inject 保留 sentinel 外內容) | 不影響 | 沒碰 inject。 |
| `design-loop`(處置閘第五步,計劃含 `[SN]` 時需綁測試) | 不影響 | 計劃的 S1 到 S10 都綁了測試,S11 用 `[manual:]`,符合閘的形狀。 |
| `loop-convergence-recording`、`pitfalls-code-loop`、`reversibility-governance-ledger`(RISK) | 不影響 | 只多了 doctor 一段治理帳被忽略的提醒,以及規格閘留痕的 tests 欄多前綴;Check R/H 與審查帳讀寫不變,`_tg_` 一帶也不影響 `pitfalls --diff` 的計分。 |
| 超過上限只列名的節點(規格閘、bound-tests-gate、room-guard、test-guard 等) | 以上列的 F1 到 F4 為準 | 規格閘與 test-guard 的 WHY 新行和程式一致。 |

## 小結

severity: minor
(最高等級是 minor;F1 到 F4 皆為 minor)

相關檔案:
- `/Users/enzo/harness/lumos-redbase-realrun/scripts/lumos`
- `/Users/enzo/harness/lumos-redbase-realrun/scripts/test_lumos.py`

我的實驗腳本放在 `/tmp/lumos-seat-work/code-紅燈版實跑三缺口/單reviewer-sonnet/`,請編排者收貨後刪除。載入模組時產生了 `scripts/__pycache__`,git 已忽略。
