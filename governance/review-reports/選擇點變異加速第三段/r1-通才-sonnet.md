severity: minor

整份看完,最高等級是 minor。機制本身(量基準去掉第一支、斷路器半開、拒收代碼、每個壞法記原因)跟程式現況對得上。我實際查證過的有:

- `_secev_junit_facts` 加 `JUnitRejected` 確實是 8 個代碼。
- S1 與 S7 的數字照新口徑重算,結果成立。
- 預期值表第 22 個才再試的算法成立。
- 既有 `t_choice_kill_merge_breaker` 只有 6 到 8 個壞法,碰不到 10 的試探間隔,不會被半開弄紅。

下面是 4 條小洞。

## F1 RETIRE-IF ① 的判準量不出「恢復後又跳開」
severity: minor
blocking: 否。只影響日後撤不撤半開的判斷,實作不會因此做錯。
- 段落:`RETIRE-IF ①`
- 引句:
「其中 `merge_trips`(跳開次數)大於 `merge_reopen` 的超過一半」
- 問題:每個平台只有「啟用」和「停用」兩種狀態,恢復一定接在跳開之後,跳開只會發生在啟用時。所以每個平台的 `merge_trips - merge_reopen` 只可能是 0 或 1,1 代表這次呼叫結束時還停用著。這條判準量到的是「呼叫結束時還停用」,不是「恢復後又跳開的頻率」。真正反映反覆跳開的是 `merge_reopen` 本身的大小。
- 另外,`merge_trips` 與 `merge_reopen` 都是 `{平台: 次數}` 的字典,spec 沒說字典要怎麼比大小。
- 佐證:file: `scripts/lumos:29095`。`_kill_merge_breaker` 目前只有「啟用 → 跳開」一條路,spec 新增的路徑只有「停用 → 恢復」。

## F2 恢復條件含「編不過」,但編不過沒有證明讀結果檔那段是好的
severity: minor
blocking: 否。最壞多付 5 次快篩逾時,spec 〈實務隱患〉已承認這個成本。
- 段落:〈用詞〉「恢復」與〈做法〉2
- 引句:
「試探快篩結果是通過、有失敗或編不過(〈用詞〉沿用 [[Projects/選擇點變異加速_計劃]] 的快篩結果四類」
- 問題:
  - 編不過時沒有任何 `TEST-*.xml`,`_choice_merge_facts` 回的是 `_CHOICE_MERGE_NO_FILES`,讀結果檔的程式沒被跑到。恢復的理由寫的是「這三類代表合併機制跑得乾淨」,對編不過站不住。
  - 試探若剛好抽到編不過或被殺的壞法(這類本來就快),會輕易恢復。之後要再數 5 次沒跑乾淨才會跳開,每次最多等一個快篩逾時上限。
  - 引句裡的「〈用詞〉」是在〈用詞〉這一節裡指向自己,原意是指第一段計劃的〈用詞〉,指向不清。
- 佐證:file: `scripts/lumos:28870`。`why is _CHOICE_MERGE_NO_FILES` 且 `rc != 0` 且符合編譯錯誤字樣時,回 `"compile", "編不過", False`。

## F3 試探間隔的常數沒命名;「最多 9 種」會被誤讀
severity: minor
blocking: 否。實作者自己取名即可;鍵數上限的測試要自己判斷要不要改。
- 段落:〈做法〉2 與 3
- 引句:
「斷路器計數與 `merge_unclean` 的鍵跟著變細(最多 9 種)」
- 問題 a:程式現有 `_CHOICE_MERGE_BREAKER = 5` 等具名常數,spec 說「試探間隔不給旗標」,但從頭到尾沒給「10」一個常數名。S2 測試要改間隔時沒有可引用的名字。
- 問題 b:「最多 9 種」是 8 個代碼加 `OSError`,只算「結果檔讀不出來」這一族。`merge_unclean` 實際最多有 13 種鍵,另外 4 種是 `逾時`、`被系統收掉`、`找不到 JUnit 結果檔`、`結果檔超過大小上限`。
- 補充:`_choice_merge_facts` 裡有兩處 `OSError`,一處是 glob 或 stat,一處是 `read_bytes`。spec 只提「讀檔的 OSError」,兩處都要帶代碼才完整。
- 佐證:file: `scripts/lumos:28845`、file: `scripts/lumos:28857`。glob/stat 那處原本回「結果檔讀不出來」,`read_bytes` 那處原本是 `unreadable`。

## F4 舊計劃的條款與測試沒有標「被取代」,恢復那行也沒寫明走標準錯誤
severity: minor
blocking: 否。只是文件與測試對應會失準。
- 段落:〈不做〉、〈驗收條款〉S1、S2、S7
- 問題 a:第二段計劃的 S7 條款寫著「守 3 支 … 量完第一支就收手 … 約需 9 秒」,綁在 `t_choice_kill_merge_budget_hint`。第一段 S8 條款寫「剩下的壞法不再跑合併」。第三段改了這兩個行為,並把 S7 綁到同一支測試,但沒有要求在舊計劃那兩條標〔已被取代〕。第一段計劃自己有這個慣例(S3 就標過)。同一支測試掛兩份互相矛盾的條款,`spec-trace` 會對不上。
- 問題 b:S2 只說「印一行」,沒寫輸出到標準錯誤。現有跳開那行是 `print(..., file=sys.stderr)`。
- 固定席(guard-kill):不影響。
  - rc 優先序:rc 由各列的 verdict 決定,試探通過走既有 `_kill_merge_emit`,沒有新增 verdict,所以不動。
  - `--json` 輸出純度:這條合約只管成功跑完時 stdout 恰一行 JSON。新增的恢復行若照 spec 在 `_kill_merge_breaker` 內印,實作者必須用 `file=sys.stderr`,否則可能汙染 stdout。這點 spec 應明寫。
- 佐證:file: `scripts/test_lumos.py:146698`(breaker 測試),file: `scripts/lumos:29107`(現有 stderr 印法)。

## 實務隱患逐類
- 效能:持續沒跑乾淨時,最壞一個循環是 5 次逾時加 10 個逐支壞法再加 1 次試探。spec 已寫明,試探上限用 `_choice_merge_screen_cap`,實測約 80 秒。無新增問題。
- 資源:新增 `whys`、`cool`、`reopen`、`trips` 只有幾個小字典,無問題。`merge_why` 的值是固定代碼加原因字串,隨壞法數線性增長,量級很小。
- 回滾:只能整個還原功能提交(spec 已寫),新欄位讀者缺欄讀成空字典,舊帳可讀。無問題。
- 併發:一次呼叫一棵工作樹一條執行緒,查證成立。訊號收掉試探快篩時,走既有的 `_KillHalt`,試探不另開新路徑。
- 試探次數:試探是壞法流程裡的一次快篩,不是額外呼叫,不會在 `--no-merge` 下出現,S5 的守衛成立。

總結:最嚴重 severity 為 minor,blocking 共 0 條(F1 到 F4 皆為否)。
