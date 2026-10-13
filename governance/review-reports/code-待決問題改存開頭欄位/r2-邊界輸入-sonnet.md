severity: major

1. 頂格的 `status:`、`source:`、`class:`、`id:` 等欄位緊接在 pending_questions 之後時,合法筆記被整份擋下,訊息還講錯原因。
severity: major
   blocking: 是
   - 引句:「errs.append((no, f"{name} 是題目的鍵,卻寫在頂格(縮排掉了);縮 4 格放回它那一題底下"))」
   - 佐證:`scripts/lumos:6978`(`name in _PQ_KEYS` 判定),`docs/lumos-toolchain-knowledge/Projects/待決問題改存開頭欄位_計劃.md:69`(規格寫「頂格鍵名是題目的鍵算讀不懂」,沒考慮跟筆記本身的標準欄位撞名)。
   - 最小重現:在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-邊界輸入-sonnet/` 造一篇合法計劃,在最後一題的 `status: 待查` 之後、結尾 `---` 之前加一行頂格 `status: doing`。
     - 修後 `lumos --vault v lint Projects/b_計劃` 報「待決問題清單無法判定:第 20 行 status 是題目的鍵,卻寫在頂格(縮排掉了)」。
     - 修後 `question-add` 被擋:「這篇的待決問題清單本身讀不懂(第 20 行…)」。
     - 修後 `spec-gate` 印「待決問題: ✗ — 開頭欄位 pending_questions 清單無法判定」,硬擋。
     - 修前同一檔 lint 是「0 問題」,`question-add` 成功(Q2),`spec-gate` 印「✓ — 2 題」。
   - 為什麼會發生:Obsidian 屬性面板這類工具會把新屬性接在開頭欄位最後。`lumos set status` 本身會把 status 插在 tags 前面,不會踩到。
   - 另外 `id`、`text`、`reason`、`tests`、`decision` 這幾個頂格鍵,實測也同樣被擋。
   - 歸因:有證據的修復回歸。
   - 兩版查證命令:`python3.14 <scripts/lumos|before_lumos> --vault <v|vb> lint Projects/b_計劃`。修後 1 warning(無法判定),修前 0 問題。before_lumos 是 `git show ea9d1ca2:scripts/lumos` 的輸出。

2. `_pq_bad_char` 只擋 Cc、Zl、Zp,不擋 Cf(零寬字元 U+200B、BOM U+FEFF、雙向覆寫 U+202E)。
severity: minor
   blocking: 否
   - 引句:「return next((c for c in v if unicodedata.category(c) in ("Cc", "Zl", "Zp")), None)」
   - 佐證:`scripts/lumos:6915`。
   - 實跑:`question-add … $'rlo\u202eabc'` 與 `$'zw\u200bsp'` 修前修後都成功寫入,lint 0 error。印出來的訊息是「rlo‮abc」,終端的顯示順序會被 U+202E 影響。
   - 這些字元不會讓 `splitlines` 換行,所以條款行號不會錯位,後果只在顯示偽造與肉眼比對。組合字元、DEL(U+007F,Cc)與 U+0085 實測行為合理。
   - 附帶:lone surrogate(argv 帶非 UTF-8 位元組,例如 `$'bad\xffbyte'`)修前修後都在寫檔時才報 `'utf-8' codec can't encode…`,檔案沒動,但訊息不是白話。
   - 歸因:有證據的原有漏查(修前同樣放行,新規則沒覆蓋 Cf)。
   - 兩版查證命令:`question-add Projects/a_計劃 $'rlo\u202eabc' --class a --stage 需求`。兩版都 ✓。

3. 推送前提醒有兩個盲點:改名後的計劃不比題號,`..f`(`HEAD..f`)被整個跳過。
severity: minor
   blocking: 否
   - 引句:「if new is None:   # 整份被刪或改名走:不是刪題」
   - 佐證:`scripts/lumos:8125` 附近(`_pq_push_remind` 的刪檔與改名分支)。
   - 實跑:計劃 p 在 c2 刪掉 Q2,c3 把檔改名成 q。
     - `--push-check main..f` 在 c2 只改內容時會報「Q2 … 不見了」。
     - 同樣的刪題再加上 c3 改名後,只剩「Q1 標阻塞」,Q2 刪除不再被提醒。修前同樣。
     - `..f` 印「範圍 ..f 不是 a..b 或 a...b,待決問題的提醒跳過」(有出聲但跳過,git 其實把 `..f` 當 `HEAD..f`)。
   - 其他範圍都正常:`main..`、`main...f`、`f~1..f`、`main..HEAD~1`(無輸出)。`nosuch...f` 與 `main..f..x` 在更早的 `git diff` 就被「範圍算不出來,放行」擋掉,所以「合併基準不存在」那條訊息實際上走不到。
   - 提醒本來就不改回傳碼,所以影響有限。
   - 歸因:有證據的原有漏查(改名行為修前相同)。
   - 兩版查證命令:`spec-gate --push-check main..f`,在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r2-邊界輸入-sonnet/g`(三個提交的暫時 repo)上跑。兩版在改名後都只印 Q1。

4. 決策連結的路徑比對沒做 NFC/NFD 正規化。路徑 NFD 寫法的檔名(日文濁音、帶重音字母)會被判不存在。
severity: minor
   blocking: 否
   - 引句:「node = lit + ".md" if (lit + ".md") in env.notes else None」
   - 佐證:`scripts/lumos:7093`。
   - 實跑:筆記檔名 `カフェ_ガ.md`(NFC)。
     - 連結 NFC `Projects/カフェ_ガ#d1` 通過。
     - 連結 NFD 版本「指到不存在的決策」被擋(修前修後相同)。
   - 純 CJK 檔名不受影響:`Projects/中文#d1` 通過。
   - 其餘實測符合新規則:
     - 大小寫不同的路徑、`./Projects/x#d1`、`Projects//x`、`/Projects/x`、`../` 修後都擋(修前多數放行)。
     - 同名不同目錄的短名 `選擇_計劃#d1` 回「格式不合或短名撞名」。
     - 帶目錄的 `Other/選擇_計劃#d1` 通過。
     - `Projects/x.MD#d1` 仍通過,偏寬但無害。
   - 歸因:有證據的原有漏查(兩版對 NFD 都擋)。
   - 兩版查證命令:`question-add … --status 已決 --decision "$(python3.14 -c "import unicodedata;print(unicodedata.normalize('NFD','Projects/カフェ_ガ#d1'))")"`。兩版都「指到不存在的決策」。

其餘邊界輸入的實跑結果沒問題,不另開 finding:
- 題號:`Q999999` 可寫入且 `pq_parse` 接受;`Q1000000`、`Q0999`、`q1` 被擋;從 `Q999998` 加題得到 `Q999999`,再加一題回「題號已經到上限」。
- 引號:引號內只有空白、`""`、tab 都被擋;單一引號字元由寫入端加另一種引號保存,能讀回。
- `_yaml_quote`:24 種怪值(`#`、`:`、`yes`、日期、`null`、`~`、`it's "x"`、反斜線)寫入後都能讀回。
- 頂格行:全形冒號、只有冒號、`- a: b`、`<<: *x` 都被擋並指出行號;`"a:b" x` 與帶前導空白的 `#` 註解行不誤擋。`decisions:` 因為 `decision` 不等於 `decisions` 而不誤擋。
- 拼錯欄位名:`pending_question_count` 與 `Pending Questions` 因為前綴比對被報成像是寫錯。這是規格明寫的範圍,但會誤傷名字長得像的別的欄位。
- 效能:3 萬題的 `pq_parse` 0.64 秒,20 萬字單行 0.04 秒,5 萬行頂格重複 0.04 秒,沒有回溯問題。

圖譜鏡頭(四篇 Systems):
- `lumos-cli-read.md`、`lumos-cli-write.md`、`規格閘.md`、`pitfalls-code-loop.md`(只在 patch 範圍外,未改)。
- `lumos-cli-read.md` 說「文法寫死在 `_pq_scan`」,與程式一致。
- `lumos-cli-write.md` 說「決策指令也拿寫入鎖」,方向與程式一致(未逐一驗鎖)。
- `規格閘.md` 說「決策是不是有效:本篇用被推那一版,別篇用工作樹」,對照 `_pq_decision_state` 的 `self_fm` 分支一致。
- 四篇都沒提「頂格撞名會擋」(finding 1)。`規格閘.md` 也沒說改名後的計劃不比題號(finding 3)。這兩處是筆記漏寫,不是筆記說錯。

三問:
① 原問題的修復有行為證據。
- 題號位數上限與全形數字:`Q1000000` 擋、`Q999999` 可寫入、上限處加題有明確訊息,且不再丟 int 例外。
- 控制字元:U+0085、DEL、tab 在讀寫兩端都被擋。
- 決策連結:路徑、大小寫、`./`、雙斜線、短名撞名在修後全擋,修前多數放行。
- 拼錯欄位名:`Pending Questions` 由「頂格寫了…不是鍵也不是題目」改成「像是寫錯」的專用訊息,頂格題目的鍵也被抓到。

② 修補處的正常、錯誤與相鄰呼叫路徑大致成立。
- `question-add/set`、lint、spec-gate、`--push-check` 的正常與錯誤路徑都實跑過。
- 唯一回歸是 finding 1:頂格撞名鍵造成的誤擋,在 lint、question-add、spec-gate 三個路徑一致發生。
- `set status` 把 status 插在前面,所以不踩到;只有手動或外部工具接在後面才會。

③ 新發現的同一案例修前修後結果如下。
| 案例 | 修前 | 修後 |
|---|---|---|
| finding 1 | 放行 | 擋 |
| finding 2 | 放行 | 放行 |
| finding 3 | 改名後無提醒 | 改名後無提醒 |
| finding 4 | 擋 | 擋 |

總結:這輪修補把數字、控制字元與決策連結的邊界收得很好;唯一要補的是 `_pq_scan` 對頂格題目鍵的判定,它會把合法的頂格 `status:`、`source:` 當成縮排錯誤,導致 spec-gate 與 question-add 被擋,是有證據的修復回歸(major)。
