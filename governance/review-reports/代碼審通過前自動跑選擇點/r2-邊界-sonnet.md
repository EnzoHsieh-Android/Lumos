severity: major

整份 spec 逐節讀完,並對照 `scripts/lumos` 查證。共 2 條 major、4 條 minor。

**白話摘要**:spec 把「pass 預判」說成跟推送前那一道完全同形。實際上,「沒有圖譜資料夾」「主線或起點算不出來」兩種情況,推送前那圈的行為跟 spec 說的不一樣。照 spec 字面實作,S6 的測試會紅,pass 也會在推送前會擋的情況下放行。

---

## Finding 1(沒有圖譜資料夾:S6 的預期值是錯的)

severity: major
blocking: 是
判準:照 spec 字面寫 S6,測試永遠不會是「擋下」,條款本身與程式現況矛盾。

spec 段落:〈做法〉「不用圖譜物件」與驗收條款 S6。

引句:「[S6] 當專案沒有圖譜資料夾、其他條件同 S1 時,`code-loop pass` 應 照 S1 擋下,不噴例外」

問題:
- S1 的前提是「碰到進行中計劃、計劃綁了測試」。沒有圖譜資料夾,計劃就不存在,「其他條件同 S1」自相矛盾。
- 程式會走另一條路。`_choice_push_round` 先進 `_choice_push_scan`,再進 `_choice_requirement`。後者呼叫 `_choice_spec_calc`,再呼叫 `_kt_sit_spec_names_calc`。
- 這支在被推版本的樹裡找不到圖譜目錄就回「樹裡沒有圖譜目錄」,`_choice_requirement` 把它丟成 `_KtSitUnverifiable`。`_choice_push_scan` 接住後走 `_choice_push_unverified`,只提醒、回空清單,也就是放行。
- 沒有圖譜目錄時,治理帳寫入也回 None(`_choice_gate_event` 的註解:「None 是這個 repo 沒有治理帳」),所以 S1 要求的「治理帳多一筆」也做不到。
- 結果是「pass 放行並提醒」,不是「擋下」。

佐證:
- file: `scripts/lumos:78581`(`_choice_requirement` 在 `_choice_spec_calc` 回 why 時丟 `_KtSitUnverifiable`)。
- file: `scripts/lumos:78810`(`_choice_push_scan` 抓 `_KtSitUnverifiable`)。
- file: `scripts/lumos:78770`(`_choice_push_unverified` 回 `[]`)。
- file: `scripts/lumos:78183`(`_choice_gate_event` 的 None 語意)。

建議:S6 改成「沒有圖譜資料夾 → 只提醒、照常記通過、不噴例外」。這也是消費專案沒裝知識圖譜時該有的行為。

---

## Finding 2(範圍算不出來:推送前那圈並不「放行」)

severity: major
blocking: 是
判準:spec 引為依據的推送前行為不存在,照字面實作會讓 pass 在推送前會擋的情況放行,目標漏洞沒補上。

spec 段落:〈做法〉「範圍」。

引句:「`_choice_range` 回原因(目前在主線上、頂端已在主線、算不出起點)→ 這一道印一行原因、放行(同推送前那道「範圍算不出來就放行」)」

問題:
- `_choice_push_range` 的真實行為是:`_push_range_start` 回 None(頂端已在主線)或 `_PUSH_START_UNKNOWN`(git 失敗或逾時)時,**退回用推送範圍本身**。
- 也就是照樣掃,而且可能多掃。程式註解也寫「不退成少查」。
- 「放行」只出現在推送範圍字串本身不合法、或 B 取不到時。
- pass 改走 `_choice_range`,這三種情況都回 why,pass 全部放行。具體後果:
  - (a)直接在 main 上提交再推。pass 放行,推送前那圈照樣掃 `old..tip` 並擋缺紀錄。這正是 spec 要消除的「記完通過才被擋」陷阱,卻在單人常見的直推主線流程上原封不動。S10 還把它寫成預期行為。
  - (b)git 查詢逾時或失敗時,pass 靜默放行,而推送前是 fail-closed 式地多查。
  - (c)頂端已在主線:pass 放行,推送時有機會被擋。
- `_choice_range` 的錯誤字串還會教人「帶 `--diff <A..B>` 指定範圍」。`code-loop pass` 沒有這個參數,pass 擋下或放行時印這句會誤導。

佐證:
- file: `scripts/lumos:78632`(`_choice_push_range`:`start is None or start == _PUSH_START_UNKNOWN` 時用 `ends[0]..tip`)。
- file: `scripts/lumos:77862`(`_choice_range` 在主線時回 why 帶 `--diff` 字樣)。
- file: `scripts/lumos:77867`(`_choice_range` 在 start 為 None 或 UNKNOWN 時都回 why)。

建議:
- 明講 pass 這道在主線與算不出起點時「比推送前少查」,並裁示是否接受。
- 或改成跟 `_choice_push_range` 一樣退回某個範圍。
- 至少把「同推送前」那句改掉。
- 為(a)補一條條款:直推主線時 pass 是否仍要預判。
- 錯誤字串在 `site=pass` 時要去掉「帶 `--diff`」。

---

## Finding 3(範圍:全分支對上增量)

severity: minor
blocking: 否
判準:防線描述不精確,實際效果是 pass 比推送前擋得更多,並非無法脫困。

spec 段落:〈實務隱患〉守衛面。

引句:「判定跟推送前那道同一支函式、同一套範圍(推送前同一頂端本來就會擋同一批)」

問題:
- pass 用 `_choice_range(rr, None, None)`,內部傳 `old="0"*n`,起點是跟主線的分岔點,等於整條分支。
- 真正推送帶遠端舊值,`_push_pick_base` 在舊值是所有分岔點的後代時取舊值,只掃增量。
- 所以「推送前同一頂端本來就會擋同一批」只在新分支首推成立。
- 已推過、後來才跨過 `_choice_since()` 生效日的舊分支,pass 會把舊提交裡沒紀錄的選擇點全拉出來擋,推送前不擋。
- 出路只剩對全範圍跑 `choice-kill`(可能很久),或逐行 `lint-waive`。

建議:改寫這句,並在回頭條件的統計口徑裡承認這種「pass 擋、推送不擋」是範圍差異造成的,不是 pass 提早抓到。

---

## Finding 4(S9 去重讓回頭條件數不出來)

severity: minor
blocking: 否
判準:`RETIRE-IF` 與 `REVISIT` 的量法與 S9 互相抵觸,條件事後算不出來。

spec 段落:RETIRE-IF 與 S9。

引句:「過半在同一個 HEAD 推送前也會被擋(代表 pass 這道沒有提早抓到東西)」

問題:
- `_choice_push_event` 對「同 head_sha、同 kind、同 reasons」只記一次。S9 又規定這種情況只留一筆。
- pass 先擋、事件已記為 `site=pass`。之後同頂端推送前再擋,該事件被去重吃掉,帳上看不到「推送前也擋了」。
- 反方向也一樣:推送前先擋後,pass 擋下被去重,`site=pass` 少算。
- 結果是「同 HEAD 推送前也擋」這個分母在帳上永遠為 0。

建議:`site` 不進去重鍵,或另記一筆 `pass-then-push` 之類的事件,或把統計口徑改成靠 `code-loop-pass` 事件加 push 側事件交叉比對。

---

## Finding 5(「要先提交」提示的涵蓋範圍前後不一)

severity: minor
blocking: 否
判準:文字與條款不一致,實作者會漏掉其中一邊,但不影響判定正確性。

spec 段落:〈做法〉「場合參數」與 S7。

引句:「[S7] 當放行檔有那一行的放行但還沒提交時,`code-loop pass` 應 照舊擋存活,訊息含「放行檔與計劃的改動要先提交才算」」

問題:
- 〈做法〉只把那句掛在「缺紀錄」的處置說明下,S7 卻要求「存活」的訊息也含它。
- 另外幾條推送前訊息在 pass 場合也沒被覆蓋:
  - 「無規格」(計劃未提交時會誤報)。
  - 「帳不在」「帳讀不了」「放行檔讀不了」,尤其 `_choice_push_read` 的「被推版本…修好再推(帳要提交)」。
- spec 只列了「缺紀錄」與「被推版本/修好再推」的替換。pass 場合的「帳不在」本來該指向 `choice-kill`,卻會說「帳要提交」。

佐證:
- file: `scripts/lumos:78885`(`_choice_push_read` 的訊息字串)。
- file: `scripts/lumos:78867`(「無規格」的訊息)。

建議:把訊息替換表擴成每個原因各一列,並為「無規格」「帳不在」各補一條條款。

---

## Finding 6(邊界條款缺口與空轉成本)

severity: minor
blocking: 否
判準:驗收條款沒蓋到使用者點名的邊界,不改變設計正確性,但現況為風險。

spec 段落:驗收條款 S1 到 S11。

問題:
- 缺條款的情境:
  - detached HEAD。
  - 分支沒有上游或遠端分支已被刪(走 `_PUSH_START_UNKNOWN`,見 Finding 2)。
  - 生效日當天。程式用 `since > today` 判斷,當天要判;spec 〈範圍〉有講,卻沒有條款。
  - 工作目錄有未提交的計劃改動。
  - 範圍只改測試檔:`_choice_requirement` 的「改到的行有 .kt 正式碼」在 `.kt` 測試檔上是否為 false,沒條款鎖。
  - 幾百行有選擇點:`_choice_push_show` 每種原因只列 20 行,輸出長度與耗時沒量(spec 自己承認「這次沒另外量 pass 時的耗時」)。
- 非 Kotlin 的消費專案:`_choice_range` 先於平台判斷執行,每次 pass 都做 git 範圍運算,在主線時每次還印一行原因,雜訊。
- 無上游、找不到主線的新本地 repo:`_push_no_mainline` 會「從空樹算」,pass 會掃整個 repo。預判的「幾秒」預期沒依據,可能吃到 `_KT_SIT_BUDGET` 才放行。

建議:至少為上列幾種各補一條「照常記通過/擋下」的條款。把「範圍算出來前先判有沒有 kotlin-junit 平台」放到 `_codeloop_pass_choice` 最前面,省下非 Kotlin 專案的空轉與雜訊。

---

## 逐節結論

- 白話、WHY、PRIOR-ART、RETIRE-IF:已讀,只有 Finding 4 與 Finding 3 涉及。
- 舊否決比對:已讀,無 finding。
- 範圍:見 Finding 2。
- 做法:見 Finding 1、2、5。
- 驗收條款與預期值表:見 Finding 1、5、6。
- 回退:已讀,無 finding。
- 實務隱患:見 Finding 3、6,其餘已讀無 finding。
- 依據來源、審計修正紀錄:已讀,無 finding。

## 實務隱患鏡頭

- 金流、對外送出、不可逆:無,spec 已排除,pass 不跑測試、不連網、不改程式,屬實。
- 守衛面:有,即 Finding 2 與 3(多擋或少擋,不會讓 pass 永遠過不了)。
- 脫困:`code-loop skip` 仍可繞過整個 gate(`scripts/lumos:80365`),而擋下訊息的路徑有出口,所以不會永遠過不了。
- 耗時:Finding 6。
- 併發與交易:依題設不考慮。

## 固定席

- `Systems/bound-tests-gate` 的 ★INVARIANT★ 是 check 才真跑受波及測試、pass 不掛真跑。spec 這版只預判、不跑測試,不破壞該合約。
- 它在 pass 前多一道 `_choice_push_round`。該函式不執行測試,只讀帳與掃語法樹。判「不影響」。
- `Systems/pitfalls-code-loop`:pass 的新增告警與表態兩道排在前面,不被新一道改動。spec 把新道排在其後、留痕驗證之前,不影響既有順序。

最嚴重等級 major,blocking 共 2 條
