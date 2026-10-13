severity: minor

我沒有找到會讓既有功能壞掉或必須退回的問題。決策指令搬進 `_decision_cmd_locked` 後,所有路徑的輸出都跟修前一致,唯一差別是「拿鎖」,這是這次修補要的行為。下面 5 條都是小問題。

**對照做法:** 修前版是 `git -C <repo> show ea9d1ca2:scripts/lumos`,修後版是 `c0265db0`。兩版各放一份臨時副本(`/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-通才回歸-sonnet/`),對同一份迷你筆記庫逐條比 stdout、stderr 和 rc。

**通才回歸的四個鏡頭**
- **決策指令九條路徑:**
  - 涵蓋 reindex 單篇、add 成功、add 日期錯、supersede 成功(含連鎖單與鄰居)、supersede 找不到、supersede 無決策、節點不存在、reindex 沒給參數、IO 例外(資料夾唯讀)、CRLF 檔。
  - 兩版逐字相同,只有連鎖單編號的時間戳不同。
  - 外部程序持鎖時,修前 add 約 3 秒直接成功;修後等滿 60 秒,印「擋下:等了 60 秒還輪不到寫入…」,rc 2,檔案沒動。
  - 12 個 `decision-add` 並行,修後 12 條都在,rc 都是 0,約 10 秒(單次約 1.5 秒)。
- **`parse_decisions` 與 `decisions_items`:** `parse_decisions` 的函式本體跟 main(b453b94f)逐字相同。`decisions_items` 的 key 參數在修補前後沒動,所有呼叫點都只傳一個參數(`decisions_items` 唯一傳第二參數的是 `pending_questions` 那一處),行為不變。
- **全圖輸出:**
  - `doctor` 的 294 行修前修後完全一致,只有兩處預期差異:連鎖待辦單從 19 張變 20 張、「updated 落後」從 313 篇變 311 篇。
  - 274 篇計劃各跑 `spec-gate --no-run`、`pitfalls --stage 需求`(含 `--json`)和 `lint`,只有〈後端工程提問與證據擴充〉一篇不同,是行號位移加舊否決筆數 195→196。
- **回退:** 用 main 的 `lumos` 對修後筆記庫跑,`lint` 只多一條「沒見過的鍵 pending_questions」警告(rc 0),`spec-gate --no-run` 正常。`decision-add` 也能在帶 `pending_questions` 的計劃上成功。計劃〈回退〉節的描述成立。

另外,`-k decision`、`-k qfm` 的測試全過。`t_cap_retro_decision_preconditions` 在同時跑掃描時逾時,單獨重跑 15 passed。

1. 頂格的 `status:` 等鍵接在 `pending_questions` 後面,現在會被整份擋下。
severity: minor
blocking: 否
- 輸入:合法 YAML 的開頭欄位,頂格的 `status: doing` 排在 `pending_questions` 清單後面。
- 走到:`_pq_scan` 範圍結尾的 `if name in _PQ_KEYS:`,`status`、`class`、`source`、`reason`、`id`、`text`、`decision`、`tests`、`stage` 都命中。
- 修前:`_PQ_TOP_KEY_RE` 把它當下一個欄位,範圍正常結束,`spec-gate` 印「✓ — 1 題」,`question-add` 成功。
- 修後:`lint` 報「第 20 行 status 是題目的鍵,卻寫在頂格」,`spec-gate` 印「✗ … 清單無法判定」,`question-add` 回 2 拒寫。
- 觸發條件窄:`lumos` 的範本把 `status` 放在最前面,`question-add` 也是把欄位加在最後。但手寫或別的編輯器排序時會誤擋,訊息也誤導(說縮排掉了)。
- 重現:`mkvault.sh` 產生迷你庫後,把 P_計劃 的 `status: doing` 移到 `pending_questions` 之後,兩版各跑 `spec-gate Projects/P_計劃 --no-run`。
引句:「            if name in _PQ_KEYS:」
- 佐證:`scripts/lumos:6985`
- 歸因:有證據的修復回歸。
- 查證:`python3.14 lumosbin_before spec-gate Projects/P_計劃 --no-run` 得到「✓ — 1 題,沒有擋進實作的」;同樣指令用修後版得到「✗ — 開頭欄位 pending_questions 清單無法判定…第 20 行:status 是題目的鍵」。

2. 決策指令拿鎖不完整,而筆記寫得像全部都鎖了。
severity: minor
blocking: 否
- `decision-reindex --all` 和 `decision-amend` 的 dispatcher(`scripts/lumos:52967`、`52977`)沒有拿 `_vault_write_lock`,但它們寫的也是同一份開頭欄位的 `decisions`。
- 實測:外部程序持鎖時,修後版的 `decision-reindex --all` 約 1 秒就完成並改了 `Systems/A.md`。
- 筆記說「decision-add/supersede/reindex 都拿同一把」,沒分單篇與 `--all`,也沒提 `decision-amend`。`decision-amend` 與 `question-add` 的覆蓋競態仍在。
引句:「decision-add/supersede/reindex(2026-10-12 起,跟待決問題寫同一份開頭欄位)」
- 佐證:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:114`、`scripts/lumos:52967`
- 歸因:有證據的原有漏查。這兩條路徑修前就沒鎖,這次修補沒碰也沒改變它們。
- 查證:`holdlock.py` 持鎖 12 秒時,修前版 `decision-reindex --all` 與修後版都立即完成。

3. 決策連結的短名比對從不分大小寫變成分大小寫,跟 `env.resolve` 不一致。
severity: minor
blocking: 否
- 輸入:`question-add … --status 已決 --decision "a#d1"`,實際檔是 `Systems/A.md`,且決策已有 id。
- 走到:`_pq_decision_state` 新的 `Path(r).stem == lit`。`env.resolve` 是用小寫的 `by_stem` 比對。
- 修前:rc 0,`a#d1` 解得到。
- 修後:rc 2「指到不存在的決策」。`systems/a#d1` 也一樣。但 `A#d1`、`Systems/A.md#d1` 都過。
- 其他走 `_dref_norm` 的決策引用仍不分大小寫,同一個連結在不同檢查有不同結果。
引句:「            hits = [r for r in env.notes if Path(r).stem == lit]」
- 佐證:`scripts/lumos:7091`
- 歸因:有證據的修復回歸。收緊「整條對上」是刻意的,但大小寫差異沒寫進筆記。
- 查證:`vc_before` 與 `vc_after` 各跑 `question-add … --decision "a#d1"`,結果見上。

4. 寫後讀回檢查實際上是同一份記憶體資料再判一次。
severity: minor
blocking: 否
- `_check(_fields)` 完全不用 `atomic_write_verify` 傳進來的 `_fields`(那是從要寫出的行重新解析的結果),而是重新解析閉包裡的 `new_fm`。
- 它跟寫前的 `pq_parse(new_fm)` 判的是同一份輸入,所以抓不到「寫出的行跟記憶體不同」。
- 筆記宣稱「放進 `atomic_write_verify` 的讀回檢查(跟 decision-add 同一個掛法)」,但 `decision-add` 的 `_check` 解析的是 `new_lines`。這次沒抓到實際錯誤。
引句:「        _p, qs2, e2 = pq_parse(new_fm)」
- 佐證:`scripts/lumos:20944`
- 歸因:未判定。修前同樣是寫前驗證,這次只是改了掛法,沒有新的錯誤輸出。
- 查證:我沒做變異實驗,這條純靠讀碼。兩版對 `question-add`、`question-set` 的實際行為相同。

5. 〈lumos-cli-read〉同一節內部新舊矛盾。
severity: minor
blocking: 否
- 同一節前面的一行還寫「沒寫平台前綴就只比名字、不建平台測試索引」,後面新加的一行寫「已驗的測試名照條款綁定那一套平台前綴規則比」。兩句不一致。
- 依 `CLAUDE.md` 規則,這種行是線索,不能推翻程式。程式現在的行為是後者。
引句:「不建平台測試索引;沒寫平台前綴就只比名字」
- 佐證:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:230` 與 `:232`
- 歸因:有證據的修復回歸,筆記只改了新增段落,漏改舊句。
- 查證:`grep -n "沒寫平台前綴就只比名字" docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md` 在修後仍命中一行。

**圖譜鏡頭**
- 〈lumos-cli-write〉:寫入鎖那一句不夠精確(見第 2 條),`_decision_cmd_locked` 沒列進實作落點。
- 〈lumos-cli-read〉:見第 5 條。
- 〈規格閘〉:列的 `_pq_push_remind`、`_pq_git_read_many` 與程式一致,推送前提醒的描述「舊版=a、三點範圍=合併基準、刪檔不比」與程式一致。我另用迷你庫測了 `a..b`、`a...b`、壞範圍、整份計劃被刪四種輸入。
- 〈bound-tests-gate〉:沒有衝突。

**三問**
- **①原問題的修復證據:**
  - 控制字元(`\x0b`、U+2028、ESC)修前 `question-add` rc 0 寫進去,修後 rc 2 並印 `U+000B` 等字元碼。
  - 帶空格或點的頂格鍵(`my key.x: 1`)修前被判「讀不懂」,修後範圍正常結束。
  - 一般中文、冒號、`#`、引號的題目文字照樣寫得進去。
  - 推送前提醒:計劃整份被刪時,修前會誤報 Q1、Q2、Q9 不見了,修後不報。
- **②修補處的正常、錯誤與相鄰路徑:**
  - 決策指令的九條路徑、全圖 `doctor`、274 篇計劃的規格閘、`pitfalls`、`lint` 都成立。
  - 相鄰路徑有三處偏差:`reindex --all` 和 `decision-amend` 沒鎖(第 2 條)、頂格 `status:` 被誤擋(第 1 條)、短名大小寫(第 3 條)。
- **③新發現案例的修前修後:**
  - 第 1 條:修前通過,修後整份擋下。
  - 第 2 條:修前、修後都不鎖。
  - 第 3 條:修前通過,修後被擋。
  - 第 4 條:修前、修後行為相同。
  - 第 5 條:修前沒有這句矛盾,修後因新增段落造成。

總結:這次修補在決策指令與全圖輸出上沒有回歸,整個提交可退;要留意的是第 1 條會誤擋合法排序、第 2 條的鎖範圍比筆記講的小。
