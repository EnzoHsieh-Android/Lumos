severity: major

已讀整份 spec,並對 `/Users/enzo/harness/lumos-near-miss/scripts/lumos` 逐項核對。繞過的路徑我沒有真的跑,是讀碼推論,每條都附了行號。

這份設計要抓的是「只送一次值的測試,對錯寫法是綠的」。照 spec 字面做,這個洞抓不到。原因有三個:
- 宣告的 `[near:]` 和實際跑的壞法互不相干。
- 殺不掉時有現成的出口,不用補測試。
- 殺掉之後測試還能換綁。

## t1 `[near:]` 與實際跑的 `--old/--new` 之間沒有任何連結,作者可以宣告真壞法、跑一個一定被殺的假壞法
severity: major
blocking: 是——照字面實作,面試題情境(near 寫 flatMapConcat)仍可拿一個無關的變異拿到「殺得掉」紀錄放行。

- 位置:〈範圍〉2 跑、〈用詞〉有效紀錄、〈實務隱患〉第一條。
- 問題:`--file --old --new` 完全由作者自填。工具只把 `[near:]` 原文塞進 recipe 的 `note` 欄,不比對、不驗證 `--new` 是不是那句話描述的寫法。
  - 例:`[near:用 flatMapConcat 代替 flatMapLatest]`,作者跑 `--old "return result" --new "return null"`。測試一定紅,判定 killed,紀錄 `near_text` 寫的是 flatMapConcat,推送放行。
  - 〈實務隱患〉只承認「選得容易殺」要靠設計審。但設計審發生在實作前,看不到 `--new`。
- 帳上也留不下稽核證據:有效紀錄欄位有 `old`,沒有 `new`。殺傷力帳本的欄位有 `note`、`tail`,沒有 old/new,而且推送閘不讀它。事後沒有任何版控的地方能看出當時換了什麼寫法。
- 佐證:`scripts/lumos:28041` 殺傷力帳本寫入欄位沒有 old/new;`scripts/lumos:75883` 人裁的 recipe 同樣只放 `note` 當標籤。
- 引句:「組一條壞法(`invariant` 填 `S<n>`、`test` 填那支、`note` 帶那句 `[near:]` 原文)」
- 引句:「欄位 `plan`、`clause_id`、`clause_sha`(`_clause_sha`)、`near_index`、`near_text`、`test_name`、`file`、`old`、`verdict`」
- 建議:帳上補記 `new`。再多記一個可機械比對的連結,例如 `--new` 必須出現 `[near:]` 裡用反引號標的識別字。或者在天花板誠實寫「`--new` 與 near 的對應全靠人看帳」,並要求代碼審席看 `new`。

## t2 殺不掉時的官方出口是「改寫 near」或「改成無」,所以弱測試永遠不必補強
severity: major
blocking: 是——spec 自己規定的操作路徑,本席要抓的問題(弱測試)會被合法地走掉。

- 位置:〈不做〉第三條、〈範圍〉1、〈範圍〉2 記。
- 問題:survived 時 rc 1 訊息說「補測試讓它紅,或改寫這條近似錯誤寫法」,〈不做〉又寫「改成 `[near:無 …]`,不另開放行通道」。第二個其實就是放行通道。
  - 面試題情境:S2 宣告 flatMapConcat,clause-kill 得 survived。作者改 `[near:]` 為「回傳空清單讓結果消失」,再跑一次,killed,放行。測試依然只送一次值。
  - 更省事的版本:改成 `[near:無 這條沒有有意義的錯寫法可宣告]`。這是 10 個實字,機器只檢字數,見〈範圍〉1。這時推送前那一道「每個非無的 near 要有紀錄」直接零紀錄放行。
- 也就是說,一個高風險計劃把所有綁測試條款都寫成 `[near:無 …]`,既不跑 clause-kill 也不被擋。
- 與 Google 的比較:PRIOR-ART 引的是「活下來的變異都有處置」。那邊處置是補測試或證明等價;這裡的處置包含「刪掉這個變異」。
- 缺口:`[near:無]` 沒有任何收斂手段,連計數都沒有。〈範圍〉4 也沒要求設計審席去看「無」的理由與近似句品質。
- 引句:「等價就代表這句近似錯誤寫法寫錯了,改寫那句 `[near:]` 或改成 `[near:無 …]`,不另開放行通道。」
- 建議,至少做一項:
  - (a) survived 的 near 被改寫後,舊句的 survived 紀錄仍在帳上,推送前印出「此條曾有 near 判 survived 後被改寫」,留給人看。
  - (b) 「無」的使用在推送輸出裡列出,並計入 RETIRE-IF。
  - (c) 規定設計審席對「無」與近似句逐條判。

## t3 有效紀錄沒有要求 `test_name` 等於條款現在綁的測試,殺完可以換綁
severity: major
blocking: 是——紀錄驗證用 `clause_sha`,而它刻意不含 `[test:]`,換綁後紀錄仍「對得上」。

- 位置:〈用詞〉有效紀錄、〈範圍〉3。
- 問題:有效紀錄的比對項目是計劃、條款編號、`clause_sha`、近似句原文。`_clause_sha` 的 docstring 明寫「不含綁的測試」,因為 `_clause_body_of` 剝掉 `[test:]`。
  - 操作:S3 綁 `t_strong`,clause-kill 殺得掉。之後把 `[test:t_strong]` 改成 `[test:t_weak]`,`clause_sha` 不變、`old` 仍出現一次,推送放行。
  - 並且 S6 說「綁多支要 `--test` 指定」,推送時沒要求「其餘綁的測試」被殺證。
- 對照:現行 `_spec_gate_ruled_events` 正是為此多比一個 `got[1] == {e["test_name"]}`,還在註解裡說「多綁、換綁都不算」。〈用詞〉沒有抄這一半。
- 佐證:`scripts/lumos:13913`(`_clause_sha` 說明);`scripts/lumos:14577`(人裁比對多比測試名)。
- 引句:「計劃、條款編號、條款雜湊、第幾個、那句原文都對得上現在那一行,判定殺得掉」
- 建議:有效紀錄加一條「`test_name` 屬於該條款現在綁定的測試集合」。

## t4 RETIRE-IF 兩條都量不到
severity: major
blocking: 是——spec 把「RETIRE-IF 第一條量這件事」當 t1 隱患的緩解手段,但量測面沒有被設計。

- 位置:RETIRE-IF、〈實務隱患〉第一條。
- (a) 「推送前被擋的次數」沒有帳。對照 `_expected_push_one` 在擋下時會寫一筆 `expected-unsigned`(`scripts/lumos:17382`)。〈範圍〉3 沒有說擋下要記事件,更沒有「是否工具誤判」的欄位。分母和分子都不存在。
- (b) 「第一次跑就殺掉的比例」:
  - 〈用詞〉規定同一條款同一個第幾個「取最新一筆」,但沒定義「第一次」。
  - 作者改寫 near 後,算同一個 `near_index` 的第二次還是新的第一次?照 t2 的操作,每次改寫都生成新的「第一次」,比例可以被洗。
  - 如果把 `clause-kill` 加進 `gov --stats`,統計折疊鍵是 (commit, nodes, gate, kind),同一提交多次執行會折成一筆(`scripts/lumos:18282` 附近的 token 鑑別子只特判了 situation-rule 等)。spec 沒說要加 token,量到的次數會偏少。
- (c) `[near:無]` 的比例沒有量。這是 t2 最大的洞,卻不在 RETIRE-IF 的任何條件裡。
- 引句:「上線兩個月,宣告的近似錯誤寫法第一次跑就殺掉的比例超過九成五」
- 建議:
  - 在 clause-kill 事件加 `attempt_no` 和 `token`。
  - 推送擋下時記 `near-blocked` 事件並帶 `reason`。
  - RETIRE-IF 加一條「無」占比。

## t5 新閘名沒登記:`_KNOWN_GATES` 與 gov 統計的幾張清單
severity: minor
blocking: 否——實作時 S4 的測試就會紅,不會悄悄做錯,但 spec 漏了這一步。

- 位置:〈範圍〉2 記、〈範圍〉4。
- 問題:`_gate_event` 對不在 `_KNOWN_GATES` 的閘名直接「不寫並印警告」。`situation-rule` 已在名單(`scripts/lumos:17760`)和另一張 pair 清單(`scripts/lumos:20659`)。clause-kill 要加進這兩處。此外 `t_gov_stats_gate_drift` 會紅,spec 的〈範圍〉4 也沒列。
- 佐證:`scripts/lumos:1840-1845`。
- 引句:「不論判定,治理帳寫一筆 `clause-kill` 事件(欄位見〈用詞〉有效紀錄)」

## t6 人裁寫回的條款(situation-rule)會在新規則下立刻缺 `[near:]`
severity: minor
blocking: 否——是流程摩擦,不會放過壞事。

- 位置:〈範圍〉1。
- 問題:`_expected_requirement` 明確把人裁寫回、沒改過字的條款扣掉,理由是殺傷力已證過。新規則「每條綁了 `[test:]` 的條款都要 near」沒做同樣的豁免。`cmd_situation_rule` 插入的行是 `- [Sn] 條款 [test:x]`,沒有 near。
  - 輸入→預期:人裁寫回一條 → 規格閘馬上要求補 `[near:]`,而它的壞法其實剛剛才被殺證過。
- 兩個選擇都要寫明:豁免人裁條款,或要求 `situation-rule` 插入時就帶 near。
- 佐證:`scripts/lumos:14631`(`new = new - ruled`);`scripts/lumos:75927` 的 `wline = f"- [{cid}] {clause} [test:{test}]"`。

## t7 〈範圍〉3 的「推送版本」沒有定義,而且計劃文字讀的是工作目錄
severity: minor
blocking: 否——是定義補強。

- 問題:`_spec_gate_push_check` 只收 `git_range`,可以是 `A..B`、`A...B`。「`git show <推送提交>:<file>`」的推送提交未定義。同函式裡計劃正文讀的是工作目錄(`_expected_push_one` 註解自承),而紀錄比對 `old` 讀的是推送提交,兩邊可能不同版本。
  - 輸入→預期:工作目錄的計劃已把 near 改過、推送提交裡的計劃是舊的,會用錯版本判。
- 建議:明定取 range 的右端點,且計劃也從該提交讀。
- 佐證:`scripts/lumos:17337-17345`。

## t8 near 句子會被門判定的關鍵字掃描讀進去,可能把風險低計劃翻成風險高
severity: minor
blocking: 否——只會多判高,方向保守。

- 問題:`_door_judge` 掃全文每一行(含程式碼圍欄、行內程式碼)。near 描述的是「錯的寫法」,很自然會用「刪除」「覆寫」「付款」這類字。
  - 輸入→預期:風險低計劃的某條寫了 `[near:直接覆寫舊資料而不保留]` → 命中關鍵字 → 門判高 → 突然要求每條 near。
- 〈範圍〉1 說風險低不要求,但沒說 near 句子不參與門判定。
- 建議:要嘛在門判定前剝掉 near,要嘛在〈實務隱患〉記一行。
- 引句:「風險低的計劃不要求(那邊已經各自要紅)。」
- 佐證:`scripts/lumos:14191-14205`。

## t9 INV_TAG_RE 是合約行共用的,加 `near` 會連合約指紋一起改
severity: minor
blocking: 否——只有合約行裡出現字面 `[near:…]` 才受影響,機率低。

- 問題:`INV_TAG_RE` 被 `_inv_fingerprint`(`scripts/lumos:28232`)、`kill` 配方比對(`scripts/lumos:27270` 等)共用。加進 `near` 之後,若某條 ★INVARIANT★ 行文裡有 `[near:…]` 字面,指紋會變、配方會判 drifted。〈範圍〉1 只講 `_clause_body_of` 要剝掉。
- 對固定席的影響:不影響 guard-kill 的兩條 ★INVARIANT★,因為它們沒有 `[near:` 字樣。
- 佐證:`scripts/lumos:6051`。
- 建議:另開 `NEAR_TAG_RE` 只給 `_clause_body_of` 用,或在〈範圍〉1 記這個副作用。

## 其他逐項

- 範圍 N、S<n>、預期值表、〈用詞〉交叉引用:S1–S10、範圍 1–4 都存在,預期值表每列的「來源」對得上〈範圍〉。
  - 小疏漏 1:S6 的條款文字沒列「平台沒有 `run_cmd`」,〈範圍〉2 有。
  - 小疏漏 2:預期值表 S3 的來源欄引用〈範圍〉1 的「風險高綁測試的條款要宣告」,與該列內容(雜湊不變)不太對得上。
- 〈舊否決比對〉三筆:
  - d1「不自動產生變異」:不衝突,同為宣告式。但 d1 的理由含「等價變異不可判定」,這裡的處置(改寫 near)恰好是繞開了不可判定。
  - 高風險測試證據加嚴的第二批:不衝突。
  - guard-kill 否決「另抽共用函式」:不衝突;但 `source` 參數加了第二個呼叫端,`_situation_rule_kill` 的信號處理、`result_out` 取值這層包裝是否複用 spec 沒說。若各寫一份,會與那條否決的精神衝突。
- 天花板:三條都成立,但漏了 t1(near 與壞法脫鉤)和 t3(可換綁測試),還有帳可手寫偽造。偽造可以算第三條「信帳」的延伸,可以不單列,但要提。
- 前置:`/Users/enzo/harness/lumos-near-miss` 目前沒有 `fail_excerpt` 與 `also`,確實在 `/Users/enzo/harness/lumos-srl-android`(`scripts/lumos:26727` 等),spec 的〈用詞〉前置說法屬實。

## 固定席:對 guard-kill 節點合約的影響
- `guard kill rc 優先序`:不影響。新增的 `source` 只影響殺傷力帳本那一筆的欄位,不碰 rc 判定。前提是實作不改 verdict 到 rc 的映射(`scripts/lumos:28060` 附近)。
- `guard kill --json` stdout 恰一行:不影響。clause-kill 不傳 `as_json`,自己的輸出走另一條路。
- 讀殺傷力帳本的讀者(`_backing_kill_rows` 等):spec 已點名要一併跳過 `clause-kill`,這點正確。

## 實務隱患鏡頭
- 作者可操作性(挑易殺、敷衍):見 t1、t2。
- 帳可信度與偽造:紀錄在純文字 jsonl,可手寫一行 `verdict: killed`。spec 天花板 3 承認信帳,但沒有任何手段(例如 `head_sha` 必須是推送範圍的祖先、必須有對應 kill-log 的重算)。同代碼審留痕的天花板,本席不另算 finding。
- 資源與效能:`old` 可能是多行,事件整行超過 4KB 時 `_gate_event` 照寫(`_gate_event_fit` 只對有 list_key 的呼叫端丟尾端),治理帳會長胖。無影響閘判斷,不阻擋。
- 併發與交易:「無」。單人單機,spec 已排除。
- 安全:near、`old` 是作者輸入,進治理帳後被推送閘讀並可能印到訊息。未見需要新增跳脫的路徑(`_kill_esc` 已用於人裁路徑),實作須沿用。

最嚴重:major;blocking 共 4 條
