severity: minor

# 代碼審 r1 通才席(opus):筆記測試綁定要存在

審查範圍:r1-code.patch 全部 1413 行逐 hunk 讀完;對照 r1-snapshot.patch 的筆記與 skill 改動、計劃〈名詞〉〈做法〉〈條款〉S1–S27。
實驗在自己的 `git clone --shared` 臨時目錄(tb-r1-opus)做,沒動被審 repo。

已跑:
- `python3.14 scripts/test_lumos.py -k test_refs`:59 passed;`-k single_table`、`-k test_gone`、`-k fail_open_and_output`:全綠。
- 這次改動自己的推送範圍 `lumos note-shape --diff 64f9c0f0..HEAD`:rc 0、8.4 秒(計劃記 7.7 秒,同一個量級)。
- 7 支探針腳本(probe/p1–p6),每條 finding 下面附輸出。

沒找到 blocker 或 major。下面 7 條都是 minor:有一條是帳上的量測欄位記錯,會直接影響 RETIRE-IF 判斷;有一條是照字面讀計劃會出錯的行為落差;其餘是測試沒釘住,或「判不了」退回成「指不到」。

## F1 帳本的 `new` 用條目第一行判,名稱寫在新加的續行上時記成假

severity: minor
blocking: 否
引句:「new[(v[0], v[1])] = v[1] in rows_new」

1. 輸入:起點的摘要條目是 `WHY:很長的一句`(只有一行)。這次推送只在後面加一行續行 `  接續 [test:test_dead_cont]`。
2. 走到哪:`_ns_test_ref_lines` 對摘要條目回的行號,是 `_note_summary_entries` 給的條目第一行(15),不是名稱實際所在的續行(16)。`_ns_test_refs_collected` 拿這個行號去比 `rows_new`,第 15 行沒新寫,所以 `new=False`。
3. 實測(probe/p2 的 P2 段):`P2 ledger items: [{'name': 'test_dead_cont', 'reason': '指不到真測試(dangling)', 'note': 'docs/kg-knowledge/Systems/A.md', 'new': False}]`。這個名稱是這次新寫的,帳上卻記成舊行。
4. 反過來也錯:只改條目第一行的字、名稱留在沒動過的續行上,會記成 `new=True`。
5. 為什麼要修:計劃〈做法〉8 對 `new` 的定義是「那個名稱所在的行在不在這次新寫的行上」。RETIRE-IF 第②條靠「名稱全在舊行上(new 全為假)的佔一半以上」來決定要不要改回只擋新加的。續行在 PITFALL 和 WHY 很常見,這個偏差會讓這組規則被判成「主要在擋舊行」,誤觸撤除條件。S21 的測試只用單行條目,所以沒抓到。

## F2 單行寫法 summary「只改那一行也算碰到」這條路徑沒有測試釘住

severity: minor
blocking: 否
引句:「hit = any(reg in ("body", "summary") or (reg == "other" and _NS_TR_SUMMARY_KEY_RE.match(ln)) for _i, ln, reg in rows)」

1. 輸入:已提交的筆記用單行 summary `summary: WHY:舊 [test:test_dead_s]`,這次推送只改這一行的字。
2. 現在的程式會擋,這條路徑本身是對的。probe/p1 的 P1 段:rc=1,列出 `Systems/S.md:4 指不到真測試(dangling) test_dead_s`。
3. 突變實驗:把 `or (reg == "other" and _NS_TR_SUMMARY_KEY_RE.match(ln))` 拿掉、清掉 `__pycache__` 後重跑 `-k test_refs`,結果 59 passed,一支都沒翻紅。同一個 P1 探針變成 rc=0,也就是改了之後會放過。
4. 原因:S12 的「單行 summary 帶不帶引號」兩個案例都是整篇新建(`_tr_write` 加 `# S` 標題行)。標題行是新寫的正文,就足以讓這篇算碰到,所以 summary 鍵行這條判法從沒被單獨驗過。計劃審計紀錄 r4-r2 第⑤點特別修的就是這個接點(單行寫法的鍵行落在 other 區),卻沒有測試咬住它。

## F3 正文散文寫 `[test-gone:]` 會被擋,寫 `[test:]` 不會,兩者不一致

severity: minor
blocking: 否
引句:「out += [v for v in (_ns_tr_gone_viol(rel, no, nm, judge) for nm in dict.fromkeys(gones + ([""] if gempty else []))) if v]」

1. 輸入:碰到的筆記正文有一行 `正文提到 [test-gone:] 這個標記,跟 [test:] 一樣`(沒包反引號)。
2. 走到哪:`[test:]` 空方括號只在 `reg == "summary"` 時算違規。正文散文照 S6 與〈做法〉3 第 2 項不算。可是 `[test-gone:]` 的空名稱(`gempty`)不分區塊,一律交給 `_ns_tr_gone_viol` 判成「名稱是空的」。
3. 實測(probe/p1 的 P3 段):rc=1,`A.md:18  [test-gone:] 名稱是空的`。
4. 影響:文件型筆記(系統筆記、計劃正文)要介紹這個新寫法時,`[test:]` 可以直接寫在散文裡,`[test-gone:]` 不行,同一句話裡只有後者被擋。這個區分對使用者來說沒有理由可講,S6 對散文提到標記本身的豁免理由同樣適用於 `[test-gone:]`。

## F4 合約行與條款定義行整條提早返回,佔位字、空方括號、`[test-gone:]` 說假話都不查

severity: minor
blocking: 否
引句:「live = [nm for nm in tests if retired and nm and not _ns_tr_placeholder(nm) and judge(nm)[0] == "yes"]」

1. 輸入(probe/p4,每個案例都是推送、`test_refs: block`):
   - `KEY:★INVARIANT★ 不變的事 [test:待補]` → rc=0
   - `KEY:★INVARIANT★ 不變的事 [test:]` → rc=0
   - `KEY:★INVARIANT★ 不變的事 [test:test_other] [test-gone:test_alive]` → rc=0
   - 計劃條款行 `- [S1] 當 x 時應 y [test:test_other] [test-gone:test_alive]` → rc=0
   - 對照組:一般行 `WHY:一句 [test-gone:test_alive]` → rc=1
2. 走到哪:`_ns_tr_line_violations` 在 `kind != "plain"` 時只算「作廢還掛活測試」就 return,後面的佔位字、空方括號、`[test-gone:]` 三項規則都沒跑到。
3. 跟計劃比:〈做法〉3 只有第 1 項寫了「合約行與條款定義行除外」。第 2 項(摘要條目的佔位字或空方括號,合約行也是摘要條目)、第 3 項(`[test-gone:]` 指得到真測試)都沒寫例外。⚠ 計劃是不是本來就想整條豁免,判不準。
4. 實際漏掉的範圍:合約行的佔位字有 doctor Check T 接(`--ci` 會擋)。條款行上的 `[test-gone:活測試]` 則沒有任何一道檢查會看:spec-trace 不認得這個鍵,doctor S20 走的也是同一支函式。

## F5 子模組清單列不出來時,「判不了」退成「指不到」,會擋下

severity: minor
blocking: 否
引句:「rows = r.stdout.split("\0") if r is not None and r.returncode == 0 else []」
file: `scripts/lumos:39195`(`_lens_git` 預設 timeout=20,逾時回 None)

1. 輸入:終點的樹裡有子模組 `vendor/sub`,平台根是 repo 根,筆記綁了一支只在工作目錄、還沒提交的 `test_only_wd`。
2. 正常情況下 `_submodule_hit` 判「平台根跟子模組有關」,結果是判不了、不擋。
3. 如果 `git ls-tree -r -z <終點>` 失敗或逾時(`_lens_git` 回 None,或回傳碼不是 0),`gitlinks` 會被設成空清單,而且快取下來。`_submodule_hit` 因此回假,判定變成 `("no", "推送的版本裡找不到,測試還沒提交?")`,照擋。
4. 實測(probe/p5,替身讓 ls-tree 回 None):
   - 正常:`('undecidable', '平台根跟子模組有關')`
   - 替身:`ls-tree 逾時/失敗: ('no', '推送的版本裡找不到,測試還沒提交?') []`,notes 也是空的,沒有任何一行說明。
5. 跟計劃比:〈名詞〉寫的是第②道 git 出錯「→ 判不了。判不了不擋、印一行」,這裡在同一類 git 失敗上變成會擋、而且不說原因。另外這次 `ls-tree` 用的是 `_lens_git` 預設的 20 秒,不受 `_NS_TR_BUDGET` 的剩餘時間限制,所以整組可能超過計劃宣稱的 20 秒上限。觸發要靠大 repo 或 git 異常,實際機率低。

## F6 碰到的筆記判成「乾淨」時不會進保險,工作目錄的改動讓 `[test-gone:]` 說假話也能無聲通過

severity: minor
blocking: 否
引句:「why = _ns_tr_guard(root, tip, pidx[0]) if (viol and trmode == "block" and not staged) else None」

1. 輸入(probe/p6):推送的版本有 `test_alive`,筆記新寫 `WHY:一句 [test-gone:test_alive]`。
   - 工作目錄乾淨時:rc=1,正確擋下。
   - 只把 `tests/test_x.py` 在工作目錄刪掉(沒提交,`git diff HEAD` 會列成 D):rc=0,這組一個字都沒印。
2. 走到哪:第①道讀工作目錄的索引,找不到 `test_alive`,判 `no`;`[test-gone:]` 的規則看到 `no` 就放行,於是 `viol` 是空的。保險 `_ns_tr_guard` 只在「有違規」時才會跑,所以「設定或測試檔跟推送版本對不上」這件事完全沒被看見。
3. 跟計劃比:〈做法〉5 寫的是這三種對不上的情況要「只提醒不擋並說原因」。這裡判定翻成放行的方向時沒有任何提醒。作廢條目也有同樣的方向:工作目錄刪了測試檔時,活測試會被判成「指不到」,原因欄就報錯了。
4. 有 CI 兜底(CI 的工作目錄就是終點),本機漏掉的推上去會被 CI 擋,所以只標 minor。

## F7 doctor S20 印出的筆記路徑沒清控制字元、也沒限長度,跟 S19 的做法不同

severity: minor
blocking: 否
引句:「cats[c].append(f"{rel}:{no}  {why} {_esc_clean(nm, 80)}".rstrip())」
file: `scripts/lumos:3717`(`_doctor_fact_recheck_lines` 整行過 `_esc_clean(..., _DOCTOR_LINE_MAX)`)

1. 輸入:知識庫裡有一篇檔名帶 `\x1b[2J` 的筆記,裡面有指不到的 `[test:x]`。
2. 走到哪:S20 只清了名稱(`_esc_clean(nm, 80)`),`rel` 原樣印出。散文撤除候選那一行 `f"{rel}:{no}  條款仍掛 [test:],下一層寫了撤除"` 也是原樣。doctor 印出這行時,終端會執行裡面的跳脫序列。
3. 相鄰的 S19(`_doctor_fact_recheck_lines`)整行都過 `_esc_clean` 並截到 `_DOCTOR_LINE_MAX`。note-shape 這邊的印法(`_ns_tr_format`)也有清路徑,只有 S20 漏了。

## 條款對照(S1–S27)

- 23 支測試逐支讀過,沒有看到夾具空轉:每支都有對照組或反向斷言,S3 用已推過的起點,S16 的 `src/a.py` 是已追蹤的程式檔。docstring 宣稱的翻紅釘,抽驗了「`_ns_skip_slot_extra` 照舊在格子 off 時提早回 None」這條,讀碼確認推論成立。
- 斷言偏鬆或沒涵蓋到的地方:
  - S12 沒驗到「單行 summary 鍵行算碰到」(F2)。
  - S21 沒涵蓋續行(F1)。
  - S14 ① ③ 只斷言 `undecidable`,沒斷言條款要求的「印一行」(⑤ 有斷言)。
  - S10 沒涵蓋合約行與條款行的佔位字與 `[test-gone:]`(F4)。
- 程式照條款做:S1–S27 都對得上,只有 F4 與計劃〈做法〉3 第 2、3 項的字面有落差。計劃〈實作紀錄〉自承的兩處偏差(正文佔位字也擋、`clause_bindings` 傳空索引),讀碼確認行為跟紀錄描述一致。

## 本案特定鏡頭

1. `cmd_note_shape` 一律傳 `slots` 容器。`_note_shape_eval` 原本就固定 `keep_other=True`,而且 `mark2=(slots or {}).get("mark2")`;容器是空的時 mark2 是 None,所以 `_notelines_range_added` 不走 texts2 與 pre2 那條分支(要 `mark2 and sink is not None` 才會走)。容器只會被放進 `notes` 與 `old_by`。格子違規只由 `_ns_slots_collected(…, slots)` 判,`slots` 是 None 時直接回 `[]`,帳上不會有 `slots_lines` 等鍵(S26 有驗)。結論:不影響。
2. `_ns_skip_slot_extra(root, slots_flag=True)`:正式呼叫端只有一處,傳 `(root, slots_flag)`,條件從「staged 而且有 slots_flag」改成「staged」。既有測試三處用預設 True 呼叫,行為跟改之前一樣(格子模式照讀、合併中照樣回 None);`-k fail_open_and_output` 全綠。提早返回改成「格子跟測試綁定兩個都 off」,沒帶 `--slots` 時格子視為 off,符合〈做法〉8。
3. `_gate_event_build` 會用 `ev.update(extra)` 把 extra 攤到最上層。原本的頂層鍵有 ts、commit、gate、kind、hard、nodes、note、detail、attempt_id、ref、head_sha;note-shape 既有的 extra 鍵有 check、slots_lines、slots_missing、lines、notes(否定現況句的整數)。`test_refs` 跟這些都不撞,全檔也沒有讀頂層 `test_refs` 的讀端。不影響。

## 圖譜固定席逐條判定

派工詞的 LUMOS-LENS 註明這次沒附固定席節點(鏡頭計算超時),也沒有附備援段,所以這裡沒有要逐條回答的節點。順帶看過四篇 lands_in 筆記這次的改動(筆記內容閘、lumos-cli-read、bound-tests-gate、棧別提問表態閘):沒有跟程式對不上的描述。表態閘那篇說 `_test_in_tree` 抽出後行為不變,讀碼加上 S25 都確認了(四種情況的判定與訊息逐字相同,逾時一樣把例外丟給外層)。

## 角色鏡頭

- be-api-compat:對外看得到的改動都是只加不改:設定加 `note_shape.test_refs`(沒寫就是 warn)、帳上加 `test_refs` 鍵、格子加 `test-gone` 鍵、`_ns_skip_slot_extra` 加了有預設值的參數。舊程式讀新帳會忽略新鍵;舊程式讀新筆記時,`[test-gone:]` 會被當成核心句的文字(計劃〈回退〉有寫);舊掛鉤不帶 `--slots` 跑新程式,這組照跑、格子不跑(S26)。沒發現相容性問題。
- be-authz:這次是 CLI 與掛鉤,沒有新增或改動任何端點,不適用。

最高等級:minor,blocking 共 0 條
