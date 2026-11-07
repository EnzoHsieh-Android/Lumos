severity: major

我讀了 r2 全文,對照了 `scripts/lumos`、`check.py` 與 r1-intake.md。大多數洞出在「同一格只認第一筆」跟「重判、覆核命中邊界」沒接上。

severity: major
blocking: 是
判準:major,S11 的路徑走不通。判定後同片段處數變多,規則說要「重判」,但記帳規則只認第一筆,材料選取也沒有挑出這種筆的模式。擋下訊息叫人去跑盲判,盲判卻記不進去,只剩人工 `overturn` 或 `lint-waive` 兩條出路。
spec 段:範圍 5 末條、範圍 6 末條、S11、預期值表 S11
引句:「同一格只認第一筆(照既有);`overturn` 讓那一筆作廢後,同一格可以再判(見範圍 6)。」
引句:「判定之後同片段處數變多:那筆判定不再適用,算還沒判(解 r1 回滾 F5、資源 F6:新增的那一處沒被判過)。」
佐證:
- 範圍 4 的選筆模式只有 `--missing`、`--disagreements`、`--unsure`,沒有「處數已變」這一類。
- 既有 `--missing` 的語意是跳過已有 first 判定的格,見 `_kt_bj_pick_rows`:`scripts/lumos:74076`。「算還沒判」的那筆因此不會進材料。
- 「格」在 rule_hits 裡沒有定義,是 seg 還是 (seg, occurrences) 並不清楚。
- S11 的測試只驗「擋」,沒有驗「擋下後有路走得通」。
- 建議:格的鍵納入 occurrences,或讓處數變多自動作廢第一判並進 `--missing`。

severity: major
blocking: 是
判準:major,範圍 2 的共用函式在一個真實路徑上沒有定義,三處算出來的身分可能不一致。
spec 段:範圍 2、範圍 3(`_codeloop_disp_range`)
引句:「範圍一律用 `_codeloop_disp_range`(表態與情境題盲判共用的那一支),三處算出同一組身分。」
佐證:
- `_codeloop_disp_range` 在分支頂端已在主線時回 `(True, None)`,範圍是 None,見 `scripts/lumos:73997-74019`。spec 沒說這時 `_rule_review_hits(…, diff_range=None, …)` 該回空還是報錯。
- 首推新分支(起點全零)與合併提交的範圍,spec 只在 S12 用 feat 合進 main 一例帶過。首推新分支從空樹掃時,全 repo 的覆核命中都算新增。這可能是上千筆,等於每個新分支首推都要整批盲判。
- 建議:寫明 None 範圍回空;首推新分支的處理另列一條。

severity: major
blocking: 是
判準:major,大量命中的 fail-closed 沒有出口。「還沒判就擋」加上分份上限 30 筆,會讓大筆命中變成每次推送派 N 份代理,而且沒有總量上限與批次放行。
spec 段:範圍 4、範圍 6、實務隱患「盲判成本」
引句:「每次推送有覆核命中就要派代理,一份最多 30 筆。」
佐證:
- 改檔名、搬目錄、首推新分支、規則包升級都會讓整批舊命中變新增。1000 筆就是 34 份盲判。
- 單筆放行只有 `lint-waive <指紋>`。`rule-review` 只有 overturn 與 agree,沒有批次放行,範圍 6 還明寫不做 `--all`。
- 「同片段每一處」前後各 8 行,材料大小不隨處數設上限。同片段 200 處就是約 3400 行單筆材料,與「每份最多 30 筆」的 30 是兩種單位。
- 時間預算用完走 fail-open 且留帳,但這是靠運氣放行,不是設計。
- 建議:設單次擋停筆數上限(超過改只提醒並留帳),或給同片段處數的材料上限。

severity: major
blocking: 是
判準:major,補進來的「對應型錄列」宣稱有一部分與程式碼不符,邊界行為沒寫完。
spec 段:範圍 4(讀型錄主表)、用詞「對應型錄列」
引句:「型錄自檢(`check.py` 的 `catalog_problems`)多驗一條:覆核與提示規則訊息開頭的型錄編號要在主表存在、而且主表那個編號只有一列」
佐證:
- `main_rows` 遇重複編號時「後面那列為準」,欄位數不對的列直接略過、不進 rows,見 `configs/ast-grep/kotlin-android/check.py:534-554`。
- `catalog_problems` 已經用 `main_rows(text, problems)` 報重複(`check.py:340`),所以「多驗一條」對重複那半是既有行為。spec 把它當新增,是未查證宣稱。
- lumos 端用 `main_rows(text)` 沒傳 problems。型錄有重複或壞列時,執行期會悄悄取後一列,或把壞列當「對不到」。
- 「對不到、讀不到」都當「不是出處不全」而擋,這會把型錄損壞轉成全量擋停,和「寧多擋不漏」疊加,配合上一條的大量命中更糟。
- 建議:型錄壞時降成只提醒並留帳,或型錄自檢不過就不跑覆核。

severity: major
blocking: 是
判準:major,mixed 檔的整份拒收會讓正常的情境判定一起被丟。
spec 段:範圍 5 第一條、S10
引句:「`rule_hits` 的每個 `seg` 要在範圍 2 那支當下算出的新增命中裡,不在就整份拒收(擋偽造與抄錯)。」
佐證:
- 結果檔可以 `segments` 與 `rule_hits` 同檔,當下命中又是「現在算」的。從材料印出到記帳之間只要多一個提交或改一行,seg 就對不上,整份連合法的情境 `segments` 一起被拒。
- 現行 `_kt_bj_validate` 對段已經是「對不上整份拒收」,見 `scripts/lumos:74064`。spec 沒說兩種材料的驗證是否各自獨立、錯誤是否分開報。
- 範圍 4 也沒說兩份材料能否各派一席、各自記帳。「不讓同一個代理同時判兩種」,同檔卻允許兩個鍵,兩者自相矛盾。

severity: minor
blocking: 否
判準:minor,有邊界缺口,但有已有機制可補。
spec 段:範圍 5(結果檔空物件、格式壞)、用詞「覆核宣告」
引句:「`_kt_bj_validate` 改成兩個鍵至少一個非空」
佐證:
- 現行函式對 `{}` 與缺 `segments` 的報錯文字是「要有 segments 清單」,見 `scripts/lumos:74064`。改成「至少一個非空」後,這句錯誤要改寫,spec 沒列。
- 覆核宣告檔(`lint-review.json`)是空物件、格式壞、重複副檔名、`{LINT_FILES}` 在多個命令中只有部分帶,這些行為只說「報錯」。報錯時是擋推送還是只印,沒寫。S1 只驗兩列。

severity: minor
blocking: 否
判準:minor,統計與回頭條件的口徑漏洞,不影響擋停行為。
spec 段:範圍 8、RETIRE-IF
引句:「`false` 經人複查至少 20 筆、`agree` 至少九成、而且 `false` 佔該規則判定八成以上 → 建議刪掉或改形狀。」
佐證:
- RETIRE-IF 寫「判定準確率低於九成」,但只有 `false` 判定會被人複查。`real` 判定的「放行」不等於推翻,所以 `real` 的準確率永遠沒有數字,那句撤除條件只對 `false` 成立。
- 範圍 8 的 `overturn` 判定作廢後,是否從「判定幾筆」扣除沒寫,可能重複計數。
- 邊界值:恰好 20、19、「被放行少於一成」的 2/20 剛好等於一成,S8 預期值表只列了 1 筆與 19 筆,沒有 20 筆恰好、一成恰好的列。

severity: minor
blocking: 否
判準:minor,弱比對路徑 spec 未提。
spec 段:用詞「覆核命中」、範圍 5
引句:「身分(`seg`)是新增告警閘的指紋:`_lint_new_key` 的(規則, 檔名, 命中行片段)取 sha256 前 16 碼。」
佐證:
- `_lint_new_key` 在取不到片段(行號缺失或超出檔案長度)時退到「規則+檔名+訊息」的弱比對,所有處共用一個身分,見 `scripts/lumos:42219-42236`。
- spec 只談處數,沒說弱比對的筆要不要擋、判定能不能綁。

僅就 `.lumos/lint.json` 的驗證器與 `--smoke` 不動這一條,我判「不影響」。範圍 1 另開檔、不碰舊驗證器,與既有的 `_lint_deps_load` 做法一致,見 `scripts/lumos:41928`。

總結:最高 major,5 條 blocking(S11 重判走不通、`_codeloop_disp_range` 回 None 與首推新分支未處理、大量命中沒有出口、型錄壞列的處理與宣稱不符、mixed 結果檔整份拒收),另有 3 條 minor。
