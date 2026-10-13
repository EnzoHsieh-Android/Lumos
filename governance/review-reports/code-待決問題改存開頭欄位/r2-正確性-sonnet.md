severity: major

## Findings

1. 決策指令只鎖了三支,同一份開頭欄位的 `decision-amend` 與 `decision-reindex --all` 仍沒鎖,題目會被靜默蓋掉
severity: major
blocking: 是
引句:「+        return _decision_cmd_locked(env, rel, args)」
- 位置與寫法:`_decision_cmd_locked` 只包 decision-add、decision-supersede、單節點 decision-reindex。`scripts/lumos:52972` 附近的 `decision-amend`(`cmd_decision_amend`,用 `atomic_write_verify` 讀改寫同一份 `decisions:` 區塊)和 `decision-reindex --all` 都沒進鎖。
- 後果:`_write_lf` 的說明還寫「其他寫入指令仍是 last-write-wins」。上輪修補的理由是「決策與待決問題寫在同一份開頭欄位,沒鎖會互相蓋掉」,這個理由對 amend 與 reindex-all 一樣成立。
- 失敗場景:對同一篇計劃同時跑 8 個 `decision-amend` 和 8 個 `question-add`,16 個指令全部回 0,檔案裡卻少題或少改。
- 最小重現:`python3.14 /tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-正確性-sonnet/stress.py after 4`
  - 修後版:4 回合裡 3 回合掉資料,`(0, 8題, 6改)`、`(1, 8題, 7改)`、`(3, 7題, 7改)`,rc 全是 0。
  - 修前版:`stress.py before 4` 也掉資料,`(0, 7題, 7改)`。
- 歸因:有證據的原有漏查。修前與修後都沒鎖,兩版都重現。修補只補了其中三支,這是上輪併發席同族沒掃完。
- 標 ⚠:機率性競態,一般單人用 CLI 很少碰到。但遺失是靜默的,而且修補聲稱已處理這一族。

2. 已驗的測試名改用 `resolve_test_refs(f"[test:{t}]", …)` 重新組字串解析,名字帶 `]` 就被當成另一個名字
severity: minor
blocking: 否
引句:「+                    keys = resolve_test_refs(f"[test:{t}]", plats, default)」
- 失敗場景:`tests: t_green]`,條款只有 `[test:t_green]`。`resolve_test_refs("[test:t_green]]")` 回 `[('py','t_green')]`,`]` 被正則吃掉,`miss` 為空,lint 不報。
- 同理,`t_green]  [test:t_red` 會被拆成兩個名字,兩個都綁了就通過。
- 重現:fixture 在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-正確性-sonnet/fx2_{before,after}`,用 `lumos lint Projects/p_計劃` 跑。
  - 修前:「已驗的測試 t_green] 不在本篇驗收條款的 [test:] 裡」。
  - 修後:無任何輸出。
- 歸因:有證據的修復回歸。修前用精確字串比對,修後改走條款綁定那套;`t_red` 兩版都正確報錯,只有帶 `]` 的名字行為改變。
- 影響不大:`tests` 欄位本來就不驗測試是否存在,但原本的精確比對漏洞變成了放行。

3. 圖譜 `lumos-cli-read.md` 的 lint 段落留著修補前的舊句「沒寫平台前綴就只比名字」
severity: minor
blocking: 否
引句:「不建平台測試索引;沒寫平台前綴就只比名字」
- 位置:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:230`。
- 矛盾:同一節新加的一句寫「已驗的測試名照條款綁定那一套平台前綴規則比」。計劃筆記與測試 `t_qfm_lint_attachments` ③ 也都說單平台下 `py:t_green` 不等於 `t_green`。
- 後果:下一個 session 會依舊句以為 `py:t_x` 與 `t_x` 同一支。
- 歸因:有證據的修復回歸。這句修前是對的,修補改了行為卻沒改這句。

4. 設定檔壞掉時,lint 對每個「已驗」的題各重讀一次設定並重印警告
severity: minor
blocking: 否
引句:「+            plats, default = _pq_platforms(env)」
- 位置:`_pq_platforms(env)` 放在迴圈裡,每個已驗題呼叫一次 `load_platforms`,而 `ctests` 只用第一次的結果。
- 重現:`.lumos/config.json` 壞掉、6 個已驗題,跑 `lumos lint`。
  - 修前:「提醒:.lumos/config.json 讀不了」印 1 次。
  - 修後:印 7 次。
- 歸因:有證據的修復回歸。
- 修法:把 `_pq_platforms` 提到迴圈外只算一次。

5. 測試缺口:決策連結「短名撞名當格式不合」沒有任何測試守
severity: minor
blocking: 否
引句:「+            if len(hits) > 1:」
- 變異實驗:把這條改成 `len(hits) > 99`(`$W/m3`),`-k qfm` 全數通過,無一翻紅。
- 其他變異:
  - 帶路徑要整條對得上:改掉後 `t_qfm_gate_holds_blocking` ⑥ 與 `t_qfm_lint_attachments` ② 翻紅。
  - 決策只解析一次、`cat-file` 大小欄位位移、`_pq_commit` 的 `_check` 改成 return True:都有翻紅。
  - 拿掉決策指令的鎖:`t_qfm_decision_add_shares_lock` 單獨跑只在 3 回合中的第 1 回合翻紅,偵測是機率性的。
- 順帶:`_check` 解析的是記憶體裡的 `new_fm`,不是 `atomic_write_verify` 傳入的 `_fields`,所以所謂「讀回檢查」其實是寫入前的同源重驗,抓不到寫檔實際發生的差異。修前行為相同,不另列為缺陷。
- 歸因:有證據的修復回歸(新規則無測試)。

## 沒找到問題的部分

- `_pq_git_read_many`:`$W/g1` 實測二進位檔、空檔、無結尾換行檔、含換行或 `\r\n` 的內容、路徑含空白或以 " missing" 結尾、目錄(tree)、不存在的版本、重複 spec、git 不存在,解析全部對。
- `_decision_cmd_locked`:
  - 鎖可重入。
  - 回傳值與例外路徑和修前一致;拿鎖逾時走「擋下:」並回 2。
  - supersede 呼叫鏈經 AST 掃過,沒有子程序。
- 修補前後 `pq_parse` 的行為差異,我用 14 種頂格輸入比對,只有刻意的三處不同:
  - 帶空格的鍵不再誤判。
  - 題目的鍵掉到頂格會報讀不懂。
  - 頂格 `id:` 會報讀不懂。
- 頂格 `status:` 接在 `pending_questions` 後面現在會被判讀不懂。`lumos set` 只改既有純量欄位、不會把 `status` 之外的題目鍵加到後面,所以只有手改才會碰到,不列 finding。

## 圖譜鏡頭

- `lumos-cli-read.md`:有影響,見 finding 3。`_pq_scan` 與「決策只解析一次」的描述和程式一致。
- `lumos-cli-write.md`:「decision-add/supersede/reindex 拿同一把鎖、沒拿的仍後寫蓋先寫」與程式一致。`reindex --all` 與 `decision-amend` 屬於「沒拿的」,見 finding 1;CRLF/BOM 拒寫那段與 `load_raw_for_edit` 一致。
- `規格閘.md`:舊版定義(`a..b` 取 a、`a...b` 取合併基準)、單次 `cat-file --batch`、被推那版與工作樹的決策分工,都與程式一致,不受影響。
- `pitfalls-code-loop.md`:本輪沒改。`--stage` 那段仍成立,只是讀法變嚴,不影響句子。

## 三問

① 原問題修復的行為證據:我把修後測試檔放到修前程式(`$W/bef`)上跑,對照如下。

| 修復項 | 修前 | 修後 |
|---|---|---|
| 值衛生 `t_qfm_value_hygiene` | 2 過 23 敗 | 全過 |
| 範圍結尾 `t_qfm_range_end` | 1 過 7 敗 | 全過 |
| 線性成本 `t_qfm_linear_cost` | 兩條都敗,6 萬空白那行 11.06 秒,決策解析 60 次 | 全過 |
| 推送前提醒範圍 `t_qfm_push_remind_ranges` | 兩條都敗 | 全過 |

- 併發修復有證據:拿掉決策鎖後 `t_qfm_decision_add_shares_lock` 翻紅,但只涵蓋三支指令。
- preserve 案例在修前版全部照過:
  - `t_qfm_strict_parse_fail_closed`:40 過。
  - `t_qfm_gate_holds_blocking`:17 過。
  - `t_qfm_lint_attachments` 只有新行為的 ③ 失敗。
- 修後 `-k qfm` 共 147 過 0 敗。

② 修補處的正常、錯誤與相鄰呼叫路徑:
- 正常與錯誤路徑成立,見上面「沒找到問題的部分」。
- 相鄰路徑有三處不成立:
  - 決策相鄰寫入指令未鎖(finding 1)。
  - 帶 `]` 的測試名被放行(finding 2)。
  - lint 迴圈內重讀設定(finding 4)。

③ 新發現案例在修前與修後的結果:

| Finding | 修前 | 修後 |
|---|---|---|
| 1 | 同樣丟資料 | 同樣丟資料 |
| 2 | 報不在條款 | 不報 |
| 3 | 舊句正確 | 舊句與新行為矛盾 |
| 4 | 1 次警告 | 7 次警告 |
| 5 | 規則不存在 | 規則存在但無測試 |

總結:修補把上輪讀寫兩端的洞大多補實了,有行為證據;但決策寫入的鎖只補三支、漏了 `decision-amend` 與 `reindex --all`(major),另有三個修補自己帶進來的小回歸(finding 2、3、4)和一個測試缺口(finding 5)。

臨時檔都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-正確性-sonnet/`,repo 內沒有改任何檔案。
