severity: major

整份 spec 已逐節讀完。下面第 1 條是照字面實作會做出錯行為的缺口,其餘三條是精度或自相矛盾的問題。

**Finding 1:統計列的載入器沒有 `site` 欄位,④ 照字面做會永遠數到 0**

severity: major
blocking: 是
判準:照 spec 寫的「數 `site == "pass"` 的 blocked」實作,統計永遠是 0,S9 的「其中 pass 擋下 1 筆」過不了。

- spec 段落:〈範圍〉④、〈做法〉統計、〈做法〉場合參數的「事件」一條、S9。
- 問題:`gov --stats` 不是直接讀治理帳的原始欄位,而是先經載入器把每筆事件轉成固定欄位的統計列。spec 只列了 `_render_gov_choice` 與 `_gov_choice_counts` 要改,沒有列載入器。
- 佐證:choice-kill 的統計列只留白名單欄位。`verdict`、`row`、`attempt`、`reason`、`via`、`run_id` 放在頂層。`file`、`fp`、`killing_test`、`changed`、`mutant_lines`、`secs`、`reasons` 放在 `ck` 底下。`site` 不在任何一組裡。
- 佐證:`_gov_choice_count_one` 的 blocked 分支只讀 `ck`,也沒有 `site`。
- 影響:RETIRE-IF 與 REVISIT:2027-01-21 都要靠這個數字,載入器不改,兩者都量不到。
- 引句:「`gov --stats` 選擇點段的「被擋筆數」分出 pass 與推送」
- file: `scripts/lumos:18552` 是 `ck` 白名單,`scripts/lumos:17915` 是 blocked 計數。

**Finding 2:範圍與推送前不同一套,spec 的防線宣稱不成立**

severity: minor
blocking: 否
判準:是宣稱的精度問題,不是實作會壞;行為上 pass 比推送前擋得更多。

- spec 段落:〈做法〉範圍、〈實務隱患〉守衛面。
- 問題:spec 說判定「同一套範圍(推送前同一頂端本來就會擋同一批)」,但 `_choice_range(rr, None, None)` 呼叫 `_push_range_start` 時,遠端舊值寫死是全零。
- 佐證:推送前真正的起點用遠端舊值。`_push_pick_base` 在舊值找得到、而且每個分岔點都是舊值的祖先時,取舊值(增量)。所以推送前只看上次推送之後的新提交,pass 看的是整條分支。
- 失敗情境:分支早在生效日之前推過,或當時 ast-grep 不在而記成 unverified。生效日之後 pass 會要求這些舊行補 choice-kill 紀錄,推送前不會要求。
- 引句:「判定跟推送前那道同一支函式、同一套範圍(推送前同一頂端本來就會擋同一批)」
- file: `scripts/lumos:77837` 是 `_choice_range` 起點用全零,`scripts/lumos:69640` 的說明寫了遠端舊值的取法,`scripts/lumos:78632` 是 `_choice_push_range`。

**Finding 3:`_choice_range` 的結果要怎麼交給 `_choice_push_round` 沒寫清楚**

severity: minor
blocking: 否
判準:spec 沒交代的接線,做錯的話 pass 會悄悄放行。

- spec 段落:〈做法〉範圍與〈做法〉場合參數。
- 問題:`_choice_push_round` 的簽名是 `(env, rr, git_range, push)`,內部自己呼叫 `_choice_push_range(rr, git_range, push)`,不會呼叫 `_choice_range`。spec 只講 pass 傳 `None` 給 env,沒講 `git_range` 傳什麼。
- 失敗情境:如果實作者傳 `None`,`_lens_range_ok(None)` 回 None,結果是印「範圍 None 不是 A..B」然後放行。這等於整道預判靜默失效,S1 之外的案例也可能看不出來。
- 正確接法:pass 要先呼叫 `_choice_range`,再把 `f"{start}..{tip}"` 當 `git_range`、`push=None` 傳進去。
- 另外,這樣接之後訊息裡的 `how` 會寫成「推送範圍」,這個字樣也要照 `site` 換掉。spec 的換字清單只列了「被推版本」「修好再推」,漏了這個。
- file: `scripts/lumos:78838` 與 `scripts/lumos:78632`。

**Finding 4:事件去重與「同一頂端」的度量互相矛盾**

severity: minor
blocking: 否
判準:是度量精度與自相矛盾,不影響閘本身的判定。

- spec 段落:〈做法〉場合參數的「事件」一條、S9、RETIRE-IF、REVISIT。
- 問題一:pass 通過後,治理帳跟代碼審帳本會一起提交(spec 自己寫在處置說明裡),所以推送前的頂端幾乎一定不是 pass 當下的頂端。
  - RETIRE-IF 說要數「同一個 HEAD 推送前也被擋」的比例,實際上幾乎永遠接近 0,撤除條件等於永遠不會觸發。
  - 這同時讓 S9 的「同一頂端 pass 與推送前各擋一次只記一筆」在實務上很少發生。
- 問題二:`_choice_push_event` 的去重只比 kind、`head_sha` 與原因,不比 `site`。若推送前先在同一頂端記了 blocked,之後 pass 的擋下就被去重掉,「其中 pass 擋下」會少算。
- 問題三:收尾訊息「處置後提交,再重跑 code-loop pass」與缺紀錄那條「跑 `choice-kill` 後再 pass,通過後才提交帳」說法不一。兩種做法行為上都能過,但指示互相矛盾。
- file: `scripts/lumos:78756`。

**逐節與其他核對**

- 〈白話〉、〈舊否決比對〉、〈範圍〉不做項、〈驗收條款〉其餘、〈預期值表〉、〈回退〉:已讀,無其他 finding。
- 已核對屬實的宣稱:
  - `_choice_push_round` 一族確實沒有讀 `env`。
  - `_codeloop_pass_gate` 的現況是 `_codeloop_pass_mech` 排在 `_codeloop_pass_verify` 之前,新增一道的位置合理。
  - `_gov_rows_at` 的 rev=None 模式讀工作目錄,檔不在回 "missing"。
  - 事件去重確實是同一頂端同一組原因只記一次。
  - `_KNOWN_GATES` 已含 choice-kill 與 code-loop-pass,新增 `site` 欄位不會被寫入器拒絕。
  - 兩個 `[[Projects/...]]` 連結目標存在。
- 固定席 bound-tests-gate:不影響。pass 不跑測試、不碰 check 路徑,★INVARIANT★「對 impact 固定席合約綁的測試逐支真跑」的掛點(code-loop check)沒有動。
- 固定席 pitfalls-code-loop:不影響其宣稱。新增一道沿用既有「機械檢查排在留痕驗證之前、不被 light 與沒有審查帳提早返回跳過」的形狀。推送前那一圈本來就在 light 分級之前併入,pass 與它一致。
- 實務隱患鏡頭:
  - 守衛面:有,見 Finding 2 與 4。
  - 耗時:spec 自己承認沒量,但只掃語法樹與讀帳,沿用既有時限,無新 finding。
  - 讀工作目錄的帳:有,未提交的列只在 pass 認,推送前仍會重擋,spec 已寫明。
  - 金流、對外送出、不可逆:無,因為只讀帳、掃語法樹、寫簿記帳。
  - 併發:依指示不考慮。

最嚴重等級 major,blocking 共 1 條
