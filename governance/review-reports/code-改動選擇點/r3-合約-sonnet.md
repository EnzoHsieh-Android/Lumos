severity: minor

## k1 choice-kill 有檔算不出選擇點時回 2,這條合約沒有任何測試釘住
severity: minor
blocking: 否 這條回 2 的規則寫在計劃〈範圍〉2 與 skill 06,卻不屬於任何驗收條款;stderr 仍會警告,只是結束碼不對,所以降為 minor。
- 輸入:改到的檔裡有一支 ast-grep 算不出來(掃描逾時、回錯、輸出過大),其他檔照常。
- 走到 `_choice_kill_report` 最後一行的 rc 運算式。這輪的計劃、skill 06、`cmd_choice_kill` docstring 都寫成「有檔算不出選擇點(那幾支這次不跑)→ 2」。
- 壞法:有人把運算式裡的 `or res.get("unverified")` 拿掉,rc 就變成 0 或 1,被略過的檔看起來像「全部有效處置」。
- 我拿掉那段後跑了三組相關測試,全綠:`t_choice_scan_per_file`(7 passed)、`t_choice_kill_no_result`(9 passed)、`t_choice_no_ast_grep`(6 passed)。
- `grep -n "算不出選擇點\|這次不跑" scripts/test_lumos.py` 無結果。
- 條款 S6 只涵蓋 ast-grep 整個不在;「部分檔算不出來」在驗收條款與預期值表都沒有列。
- 引句:「rc 取最大:全部有效處置 → 0;有存活 → 1;有 no_result、不唯一、沒跑完或中斷、有檔算不出選擇點(那幾支印警告、這次不跑)→ 2。」
- file: `scripts/lumos:78217`
- 歸因:有證據的原有漏查。修前 f1be3141 的程式同一行已有 `res.get("unverified")`,同樣的改壞在修前、修後都全綠。

## k2 整批掃描只用一半時限這條沒有測試釘住
severity: minor
blocking: 否 這是計劃寫的設計參數,不屬於條款,也不是必要行為。
- 輸入:整批 ast-grep 卡到逾時,逐檔其實很快。
- 走到 `_choice_scan` 的 `* _CHOICE_BATCH_SHARE`。計劃〈範圍〉4 寫「整批最多用掃描時限的一半」,PITFALL 也綁到 `t_choice_scan_batch_budget`。
- 我把 `_CHOICE_BATCH_SHARE` 改成 1.0 後,`t_choice_scan_batch_budget`(2 passed)和 `t_choice_scan_per_file`(7 passed)照綠。
- 我寫了個假 ast-grep:整批(最後一個參數是 `src`)睡 30 秒,逐檔立刻回。`_choice_scan(repo, 5 支檔, 8 秒)` 的結果:
  - 現行(0.5):`secs=4.5 scanned=5 bad=0`。
  - 改成 1.0:`secs=8.0 scanned=0 bad=5`,五支全記「超過時限」,推送那一道整圈只提醒。
- 引句:「整批最多用 _CHOICE_BATCH_SHARE 那一份,剩下的留給退回的逐檔」
- file: `scripts/lumos:77142`(`_choice_scan` docstring;`scripts/lumos` 裡 `_CHOICE_BATCH_SHARE = 0.5` 那一行)
- 歸因:未判定。批次優先是這輪才有的機制,修前沒有可比的行為。只能說修補新增的行為缺釘,不是修補造成的回歸。

## k3 doctor 把選擇點放行混進新增告警條數的改壞測不到
severity: minor
blocking: 否 只影響 doctor 的統計文字,沒有擋推送或寫錯帳。
- `_lint_waivers_doctor_bits` 的 `lint, sit, choice = _lint_waivers_split(waivers)` 後面,若加一行 `lint = dict(lint, **choice)`(重現 r1 g6 的老毛病),`t_lint_waive_choice_ai_summary`(4 passed)和 `t_gov_stats_choice_dedup`(4 passed)都照綠。
- 原因:`t_lint_waive_choice_ai_summary` 只斷言「選擇點放行裡 1 條是 AI 放的」有出現,沒斷言「放行清單」那句不含選擇點。
- 引句:「放行檔拆成三份後,AI 放的選擇點放行在推送前小結消失,lint-waive 的提示卻說小結會列」
- file: `scripts/lumos:42420`
- 歸因:有證據的原有漏查。`_lint_waivers_doctor_bits` 在修前 f1be3141 就是這份程式,這次修補沒動它,只是計劃文字新提到。

## 三問回答

**① 原問題的修復效果(行為證據)**

在修後 8e521300 的乾淨副本跑關鍵字子集,全部通過。

| 測試 | 結果 |
|---|---|
| `t_choice_kill_test_files_in_test_paths` | 19 passed |
| `t_lint_waive_choice_ai_summary` | 4 passed |
| `t_choice_kill_rerun_rules` | 11 passed |
| `t_choice_kill_incremental` | 6 passed |
| `t_choice_kill_platform_key` | 3 passed |
| `t_choice_ledger_write_semantics` | 6 passed |
| `t_spec_gate_push_choice_catalog_change` | 5 passed |
| `t_spec_gate_push_choice_unverifiable` | 8 passed |
| `t_choice_waive` | 10 passed |

- `t_choice_scan_batch_budget` 與 `t_choice_scan_per_file` 後來連跑 3 次、2 次都全綠。
- 第一次跑這兩支時各有 2 個檢查紅(7.7 秒和 7.5 秒收尾),原因未判定,之後無法重現。暫存現場當時沒有可看的內容,我已刪掉。我判斷是當時機器負載的偶發,但沒有證據,請當成「這兩支測試可能對負載敏感」的線索。
- 修前 f1be3141 沒有 `t_choice_kill_test_files_in_test_paths`、`t_lint_waive_choice_ai_summary`、`t_choice_scan_batch_budget` 這三支,所以 repair 案例 H1、H2、H3 缺修前證據,結果是未判定。我沒有補修前版本的紅綠對照。

我還對 H1、H2、H3 做了翻紅驗證:改壞某一道,看那支測試會不會紅。

- 紅(測試有釘住):
  - M1 pick 忽略不明標記:`t_choice_kill_test_files_in_test_paths` 1 failed。
  - M2 stale 不略過不明標記:同一支 1 failed。
  - M5 去掉 `-w`:2 failed。
  - M6 去掉測試路徑過濾:1 failed。
  - M8 挑壞法共用掃描 deadline:`t_choice_scan_batch_budget` 1 failed。
  - M11 簽章只取第一支測試檔:`t_choice_kill_test_files_in_test_paths` 1 failed。
  - M12 雜湊鍵只用測試名:同一支 1 failed。
  - M13 小結不印選擇點行:`t_lint_waive_choice_ai_summary` 1 failed。
- 仍全綠(測試沒釘住):
  - 拿掉 `_CHOICE_GUARD_FLOOR` 那行(M7)仍全綠。這條我判為等價改動,不當 finding:`_choice_guard` 走 `_choice_requirement` 已填的快取,時限實際沒被用到。
  - M3(整批佔比改 1.0)、M15、M16 就是上面的 k2、k1、k3。

**② 修補處的正常、錯誤與相鄰路徑**

- 整批與逐檔的掃描結果一致:對 `configs/ast-grep/kotlin-choice/samples/` 底下 6 支樣本檔(arid、chain、choice、error、multibyte、nested)用真 ast-grep 各跑一次整批和強制逐檔,key 排序後 JSON 比對相同(`SEMANTIC EQUAL True`)。
- 整批卡住時能退回逐檔:假 ast-grep 實驗,現行版 5 支都掃到(見 k2)。
- `git grep -z -o -w -F -I -e …` 對前綴與子字串名字的邊界正確。
  - 輸入:名字 `t_a`、`t_ab`、`t_a_b`、`t_abc`。
  - 同一行 `t_ab(); t_a()` 只命中 `t_ab` 與獨立的 `t_a`。
  - `t_a_z` 與 `t_abc` 內的 `t_a` 不誤命中。
- 修補沒有碰 `cmd_guard_kill`。我用 `git diff -U0` 列出 `scripts/lumos` 所有 hunk 的函式名,沒有任何一個落在它裡面。
- 沒測到的路徑:
  - 真 Android 專案的端到端耗時(S26 手動驗收)。
  - 整批輸出超過上限時,約 450 支以上的大檔改動會超出推送前時限。這條只寫在卷證 `r3-behavior-cases.md` 的「未覆蓋」,圖譜筆記沒有記。我沒有重跑這個量測。

**③ 新發現的同一案例在修前、修後的結果**

- k1:修前 f1be3141 與修後 8e521300 都是「拿掉 `or res.get("unverified")` 仍全綠」。
- k3:修前 f1be3141 的 `t_lint_waive_choice_ai_summary` 不存在,所以 doctor 改壞只在修後可測;`t_gov_stats_choice_dedup` 在修前沒被改壞抓到的記錄,我沒另跑。
- k2:修前沒有批次優先機制,無法比。

## 合約鏡頭

**Systems/guard-kill 的兩條 ★INVARIANT★**

不受影響。

| 合約 | 綁定測試 | 修前 f1be3141 | 修後 8e521300 |
|---|---|---|---|
| guard kill rc 優先序 | `t_guard_kill_rc_precedence` | 4 passed | 4 passed |
| guard kill --json 純度 | `t_guard_kill_json_purity` | 6 passed | 6 passed |

兩版都在乾淨副本實跑過,修補差異沒動到 `cmd_guard_kill`。

**這次改到的筆記**

計劃筆記與 `Systems/規格閘.md` 都沒有 ★INVARIANT★、★IRREVERSIBLE★、★CHECKPOINT★ 的合約行。`規格閘.md` 裡出現「★IRREVERSIBLE★/★CHECKPOINT★」字樣的是描述風險門檻的正文,不是合約行。`lumos lint Systems/規格閘.md` 回 0 問題。

**文件對程式的語意核對**

逐句對照 `scripts/lumos`,以下都一致:

- `choice-points` 有檔算不出來回 3,其他檔照列,stderr 說哪幾支。
- `choice-kill` 有檔算不出選擇點回 2,印警告,這次不跑那幾支。
- run 事件 `tests` 欄三元組 `[平台, 測試名, 簽章]`,多支用 `+` 接、不明記 `?`。
- `tests_sha` 帶 `?` 時存活的行一律重跑、推送端不比。
- AI 放行小結那一行與 doctor 的措辭,跟 `_cl_say_lint_waive_notes` 與 `_lint_waivers_doctor_bits` 的輸出字樣一致。
- lint-waive 提示句講的是小結的哪一行,跟程式一致。

條款 S11 與預期值表 S11 的三列(跳過、tests_sha 變了才重跑、max-seconds)跟程式一致。這輪新增的兩條行為(部分檔算不出來的 rc、`?` 不明標記)在驗收條款與預期值表都沒有對應列,這點在 k1 已提。

## 圖譜鏡頭

這次沒附固定席節點。

## 清理

我的臨時副本與實驗檔(`/tmp/lumos-seat-work/code-改動選擇點/合約-sonnet/` 底下的 clone、假 ast-grep、實驗腳本)和兩個 `gctl-run-*` 現場都已刪除,只刪我這個會談建的。留在該目錄的只有 `diff1.py`、`mut.py`、`mut2.py`、`mut2_0.py`、`share.py` 這幾個實驗腳本,沒刪,裡頭寫死的 repo 路徑已不存在。

最嚴重:minor;blocking 共 0 條
