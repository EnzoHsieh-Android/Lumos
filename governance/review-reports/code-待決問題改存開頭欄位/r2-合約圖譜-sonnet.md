severity: major

我沒有改過 repo。實驗放在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-合約圖譜-sonnet/`,裡面有修前、修後兩份 clone 和幾個變異副本。

先講沒問題的部分:
- 修後 `python3.14 scripts/test_lumos.py -k t_qfm` 是 147 passed、0 failed。
- 六篇筆記 `lumos lint` 都是 0 問題。
- `lumos doctor` 是 0 issues(851 篇)。
- 筆記裡引用的函式名和測試名(`_pq_scan`、`pq_parse`、`_pq_git_read_many`、`t_qfm_*` 等)grep 全都存在。
- 效能:20000 題解析 0.43 秒,2M 字的值 0.28 秒。
- 沒有殘留 `_strict_list_scan`、`_pq_test_same` 的引用。

1. 決策指令只補了一半的鎖,筆記卻說三個都鎖了
severity: major
blocking: 是
引句:「決策與待決問題寫在同一份開頭欄位,沒鎖會互相蓋掉」
佐證:
- 有鎖的路徑:`scripts/lumos:53011`(`_decision_cmd_locked`)只包單節點的 decision-add/supersede/reindex。
- 沒鎖的路徑:`scripts/lumos:52967`(`decision-reindex --all`)和 `scripts/lumos:52977`(`decision-amend`),它們寫的是同一份開頭欄位。`decision-refs` 的 add-ai、prune、promote 在 `scripts/lumos:52950` 附近也一樣沒鎖。
- 筆記說法:`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:114` 寫「decision-add/supersede/reindex 都拿同一把」,沒講 `--all` 不在內。
- 後果是丟題時指令回傳 0,不報錯。阻塞題被蓋掉,規格閘就放行。

歸因:有證據的原有漏查。修前這些路徑本來就沒鎖,這輪只補了其中一部分。
查證:我造了一篇有一條無編號舊決策的計劃,同時跑 `decision-reindex --all` 加 6 個 `question-add`,重複多回合。
- `--all`:第一批 3 回合中 1 回合只剩 3 題(應為 6),第二批 15 回合中 1 回合剩 5 題。丟題的回合裡,6 個 question-add 的回傳碼仍全是 0。
- 單節點 `decision-reindex Projects/m_計劃`:15 回合 0 次丟題。

2. 有一句筆記跟程式和計劃都對不上
severity: minor
blocking: 否
引句:「已驗的測試名在本篇驗收條款定義行的 `[test:]` 裡(不建平台測試索引;沒寫平台前綴就只比名字)」
佐證:
- 過期的一句在 `docs/lumos-toolchain-knowledge/Systems/lumos-cli-read.md:230`,這是修補差異裡沒動的 context 行。
- 同一段新加的一句(補丁 297 行,即同檔 232 行)寫「照條款綁定那一套平台前綴規則比」。
- 程式 `_pq_clause_tests`、`_nl_rule_pending_questions` 走 `resolve_test_refs`:單平台下 `py:t_x` 和 `t_x` 是不同名字。

歸因:有證據的修復回歸(這輪改了行為,卻漏改這一句)。
查證:`grep -n "沒寫平台前綴就只比名字" Systems/lumos-cli-read.md` 在修後還命中第 230 行,同段第 232 行互相矛盾。

3. 決策 d10 還標有效,卻說 `--stage` 只列需求風險面
severity: major
blocking: 否
引句:「第二次修訂(d11)寫 pitfalls --stage 只列需求風險面;開頭欄位版上線後 --stage 會列題,d11 仍標有效會讓下一個會談以為 --stage 不列題」
佐證:
- `Projects/後端工程提問與證據擴充_計劃.md:107` 的 d10 是 `valid: true`,內容寫「pitfalls --stage 只列需求風險面」和「正文一節暫時只是給人看的清單」。
- 這跟 d12 要消除的毛病一模一樣,但這輪只作廢了 d11、補了 d12。
- 程式現況是 `--stage` 會列題。

歸因:有證據的原有漏查(同一類問題 d11 到 d12 時只掃了一處)。
查證:`grep -n "只列需求風險面" docs/lumos-toolchain-knowledge/Projects/後端工程提問與證據擴充_計劃.md` 命中 107、113、123 行。113 行(d11)已作廢,123 行是 d12 的說明,只有 107 行仍有效。
補充:d12 是照 d11 的方式寫的,只有 context 和 why_chosen 兩欄,沒有 alternatives 和 trade_offs。技能文件 `commands/03-寫回圖譜.md:95` 要重大決策填四欄。d12 只是補記,算不算重大有爭議,所以只當附註。

4. 「決策連結整條比對」是這輪新改的行為,沒有任何 `t_qfm_*` 測試守著
severity: major
blocking: 否
引句:「帶路徑的寫法要整條對得上;只寫短名而同名不只一篇,當格式不合」
佐證:`scripts/lumos:7073` 的 `_pq_decision_state`。測試只有 `t_qfm_lint_attachments`(`scripts/test_lumos.py:56287`)用到有效的 `Projects/g_計劃#d1`。沒有任何一支測「指到別的目錄」「短名撞名」「推送前本篇用被推那一版、別篇用工作樹」。

歸因:有證據的修復回歸(新行為沒有測試)。
查證(修前與修後的行為不同,所以這個改動是真的):

| 連結 | 修前 | 修後 |
|---|---|---|
| `Systems/y/x_計劃#d1`(路徑不存在) | ok | missing |
| `other/Projects/x_計劃#d1`(路徑不存在) | ok | missing |
| `x_計劃#d1`(兩個目錄有同名 `x_計劃`) | ok | bad |

變異驗證:
- 變異 A:把 `_pq_decision_state` 改回舊的 `env.resolve`,`-k t_qfm` 沒有任何斷言變紅。有兩支因 4 個變異副本同時跑、機器忙而逾時,但它們的決策案例都是合法連結,不是專抓這個。
- 變異 G:把推送前提醒的 `self_fm=nfm` 拿掉,同樣沒有斷言變紅。

5. 字元規則漏了 Unicode 格式類字元
severity: minor
blocking: 否
引句:「值裡第一個不准出現的字元:控制字元(含 \x0b \x0c \x85 ESC)與 U+2028/U+2029」
佐證:`scripts/lumos:6915` 的 `_pq_bad_char` 只擋 Unicode 類別 Cc、Zl、Zp。
- U+202E(RLO,雙向文字覆寫)、U+200B(零寬空格)、U+FEFF 都被收下。
- 這些字會被 `spec-gate`、`--stage` 印到終端,能讓顯示跟實際內容對不上。
- 筆記為 ESC 擋下的理由是「印到終端能改畫面」,同一個理由適用於 RLO。

歸因:有證據的原有漏查(修前連 U+2028 都收)。
查證:`probe1.py` 對修前、修後都顯示 RLO 回傳 `errs=[]`、`nq=1`。

6. 新規則會把頂格的 `status:` 誤判成題目的鍵
severity: minor
blocking: 否
引句:「是題目的鍵,卻寫在頂格(縮排掉了);縮 4 格放回它那一題底下」
佐證:`scripts/lumos:6953` 起的 `_pq_scan`。
- `_PQ_KEYS` 含 `status`、`source`、`reason`、`class`、`text`、`id`、`stage` 等常見名稱。
- 計劃若把 `pending_questions` 排在頂格 `status: doing` 之前(例如 `lumos set` 在缺 `status` 時補在檔尾),整份清單就判讀不懂,規格閘整份擋。
- 筆記有寫這條規則,但沒提這個誤傷面。

歸因:有證據的修復回歸。
查證:`probe1.py` 拿同一份開頭欄位,修前 `errs=[]`,修後第 9 行報「status 是題目的鍵,卻寫在頂格」。`source:` 也一樣。

7. 「讀回檢查」其實沒有讀回
severity: minor
blocking: 否
引句:「交給 atomic_write_verify 的讀回檢查,跟鄰居同一個掛法」
佐證:
- `scripts/lumos:20926` 的 `_pq_commit` 裡 `_check` 忽略傳進來的 `_fields`,重新解析的是記憶體裡的 `new_fm`,不是實際寫出的內容。
- 計劃 `Projects/待決問題改存開頭欄位_計劃.md:90` 說「放進讀回檢查」。
- 測試 ⑫ 只能手工塞一個不符的 `want`,正常指令路徑永遠不會觸發這個檢查。

歸因:有證據的原有漏查(修前寫入前的比對也是同一份記憶體資料)。
查證:`atomic_write_verify`(`scripts/lumos:19907`)把 `parse_frontmatter(new_lines)` 的結果傳給 `expected_check`;`_check` 沒用它。

8. 新加四支測試沒綁進任何筆記,驗收條款文字也沒跟上
severity: minor
blocking: 否
引句:「讀寫兩端用同一條規則:值不能含換行類字元」
佐證:
- 這四支測試是 `t_qfm_value_hygiene`、`t_qfm_range_end`、`t_qfm_linear_cost`、`t_qfm_decision_add_shares_lock`。在六篇筆記和兩份計劃裡 grep 不到它們的名字。
- 條款 S2、S3 還是舊文字:S3 寫「任何值含換行或 tab」,實際擋所有控制字元和 U+2028/2029;S2 沒提「題目的鍵掉到頂格」「連字號欄位名」「題號最多 6 位、到 Q999999 就不能再加」。
- 推送前綁定測試閘只看有綁定的測試,這幾支靠不上它。

歸因:有證據的修復回歸。
查證:`grep -o "t_qfm_[a-z_]*" -rh docs/lumos-toolchain-knowledge | sort | uniq -c` 只有舊的幾支。

**新測試抓不抓得到真錯。** 對照 `commands/03-寫回圖譜.md`〈實作測試品質〉,我做了下列驗證:

| 測試 | 驗證方式 | 結果 |
|---|---|---|
| `t_qfm_value_hygiene` | 把 `_pq_bad_char` 停用,8 種字元全部變成讀得懂;另確認測試裡的 U+2028/U+2029 是真字元,不是空白 | 抓得到 |
| `t_qfm_linear_cost` ② | 拿掉 `_pq_blocking_open` 的共用 cache,決策解析變 60 次 | 變紅 |
| `t_qfm_decision_add_shares_lock` | 拿掉決策指令的鎖,重跑 5 次 | 4 次變紅,1 次仍綠(機率性,約五分之一漏接) |
| `t_qfm_strict_parse_fail_closed` | 每例只放一處毛病,並斷言行號與原因 | 設計合格,不會被別條規則代打 |

兩個缺口:
- 第 4 點的「整條比對」和推送前的版本選擇完全沒被測到。
- 測試 ⑫ 是手工餵不符資料,測的是正常路徑到不了的檢查。

**三問**

① 原問題的修復效果。
- 字元衛生、題號上限、範圍結尾、決策只解析一次、整條比對、三點範圍,在修後都有程式行為證據(`-k t_qfm` 147 全過,加上上面的對照探針)。
- 單節點的決策指令與 `question-add` 互斥有效,15 回合 0 次丟題。
- 但互斥只涵蓋單節點三條指令,`--all` 與 `decision-amend` 等路徑仍會丟題(第 1 點)。

② 修補處的正常、錯誤與相鄰路徑。
- 正常路徑(合法題目寫入、讀回、規格閘、lint、`--stage`)都成立。
- 錯誤路徑(讀不懂整份擋、寫入拒絕)成立,且行號基準有測試鎖住。
- 相鄰路徑有三處不成立:
  - 其他寫同一份開頭欄位的決策指令沒鎖(第 1 點);
  - 頂格的 `status:` 被誤判(第 6 點);
  - 筆記裡有三句過期文字(第 2、3 點,以及 `Systems/lumos-cli-write.md:149` 還寫著「不照抄 decision-add 的沒鎖」,跟同檔 114 行互相矛盾)。

③ 新發現的同一案例修前與修後各是什麼結果(以下是我實測的行為,不是 `r1-repair-before.txt` 的內容)。
- `decision-reindex --all` 與 `question-add` 同時跑:修前與修後都會偶發丟題,回傳碼 0。
- 頂格 `status:` 接在題目後面:修前讀得懂,修後讀不懂,屬修補造成的退步。
- RLO(U+202E):修前與修後都收。
- 路徑不存在的決策連結:修前判 ok,修後判 missing。同名短名:修前判 ok,修後判 bad。

總結:這輪修補對原本點名的問題有行為證據,但鎖只補了一半(`--all`、`decision-amend` 仍會靜默丟題)、決策 d10 還標有效卻跟程式相反、新改的整條比對沒有測試;整體 severity 為 major。
