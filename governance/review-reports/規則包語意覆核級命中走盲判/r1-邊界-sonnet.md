severity: major

審查對象:規則包語意覆核級命中走盲判_計劃(r1 快照)。我逐節讀完,並對照 `scripts/lumos`、`check.py` 與兩份 sgconfig 查證。

**固定席逐條判**
- 〈Systems/pitfalls-code-loop〉:影響。該節點管 code-loop 的擋停,本案新增一條會擋的路徑。擋下點與判定函式的接法(finding 3、7)沒寫清楚。
- 〈Systems/kotlin規則包〉:不影響。62 條規則的訊息都帶型錄編號;帶出處不全標記的列剛好 7 條,全在提示級。我用 `main_rows` 和 rules 目錄實際算過,與 spec 宣稱相符。
- 〈Systems/linter精選目錄〉:影響。範本要改成「接在 review 段」。但 `review` 段本身是通用的,範本沒說明 review 命令的命中如何在沒有型錄的情況下處理(finding 9)。

**逐節**
- 〈用詞〉、〈範圍〉1–8:有 finding,見下。
- 〈不做〉:已讀,無 finding。
- 〈回退〉:已讀,無 finding。驗證器要留著認得 `review` 鍵,這點正確。
- 〈依據來源〉、〈審計修正紀錄〉:已讀,無 finding。
- 交叉引用:related 與 lands_in 的目標節點都存在。

---

severity: major
blocking: 是(判準:人複查推翻盲判後,真問題仍被放行,沒有任何機制把它拉回來)
- spec 段落:〈用詞〉人複查、〈範圍〉5 的 `false`、〈範圍〉7
- 問題:`--verdict overturn` 只會被記進統計。`false` 命中的放行檔紀錄不會被撤銷,指紋仍在放行檔裡,`_lint_new_tools` 會繼續把這筆命中濾掉。也就是說,人看完說「盲判錯了,這是真問題」,該命中卻永遠不再被擋。spec 沒定義 overturn 之後的動作,例如撤放行或重新擋下。
- 引句:「確認一筆 AI 放行時,同時註記同不同意盲判」
- 佐證:file: `scripts/lumos:42297`(放行只有新增,沒有撤銷路徑)。
- 佐證:file: `scripts/lumos:42444`(放行的指紋在 `_lint_new_tools` 組 `kept` 時被濾掉)。

severity: major
blocking: 是(判準:記帳到一半失敗後,沒有任何重試路徑,命中會永久卡死)
- spec 段落:〈範圍〉5 的 `false`、〈範圍〉4 治理帳
- 問題:記帳那一步要同時做兩件事,一是追加治理帳的 `rule_hits`,二是寫 origin=ai 的放行。順序與原子性都沒寫。
  - 現況的 `_lint_waivers_add` 在指紋已放行時直接回 `(False, "已經放行過了")`。例如同一指紋先被人放行,或放行檔讀不了,就會走到這裡。
  - 帳只認每格第一筆,而且整份全是已有紀錄的格就拒收。所以「帳已寫成 `false`、放行沒寫成」的狀態無法補寫:這筆命中永遠是「已判誤報」卻沒有放行,會一直被擋,而且重跑記帳指令只會被擋回。
  - 一次記上千筆 `false` 時,每筆各自讀改寫整份放行檔(上鎖),成本是 O(n²)。這是我的推論,spec 沒給批次寫法。
- 引句:「記帳那一步(`lumos code-loop blind-judge <結果檔>`)替它寫一筆放行」
- 佐證:file: `scripts/lumos:42306`。
- 佐證:file: `scripts/lumos:74217`(整份全是已有紀錄的格就不寫帳、回 2)。

severity: major
blocking: 是(判準:判定身分沒綁上下文與分支,過期的誤報判定會把真問題一起放行)
- spec 段落:〈範圍〉3、〈範圍〉5、〈天花板〉1
- 問題:判定身分只有 (規則, 檔名, 命中行片段)。語意覆核規則的判斷依賴型別與上下文(例如 `.setValue` 是 LiveData 還是 Firebase),但前後 8 行的上下文沒進身分。
  - 同一行片段在上下文改變後(例如變數型別改了),會沿用舊的 `false` 判定,而且放行指紋也相同,所以整批被放行。
  - 同檔同片段多處,只取最後一處當代表判,結果套用到全部。若最後一處是誤報、較早一處是真問題,真問題就被放行。「新加的通常在後面」只是經驗猜測,spec 沒有機械保證。
  - 情境段的 `seg` 綁材料內容,上下文變了就要重判;覆核命中沒有這層保護。
  - 判定帳是按分支折的,放行指紋卻是全 repo 通用。同一指紋在分支 A 判 `false`、記了放行,分支 B 就不會再被判,兩套範圍不一致。
- 引句:「同檔同片段的多處共用同一個身分與同一個判定。」
- 引句:「材料取檔內最後一處(複製貼上時新加的通常在後面)」
- 佐證:file: `scripts/lumos:42219`(指紋只用片段)。
- 佐證:file: `scripts/lumos:73876`(`_kt_bj_read` 按 `ev.get("branch") == branch` 折帳)。

severity: major
blocking: 是(判準:出處不全的 7 條規則,「還沒判」會擋、判完卻永不擋,與 d1 的理由矛盾)
- spec 段落:〈範圍〉5、d1、S2、S3
- 問題:d1 的理由是「依據不足的規則不准擋人」。但「還沒判:擋,印跑盲判的指令」沒有排除這 7 條。
  - 這 7 條規則的命中,在判定前會擋推送,逼人派代理;判完卻因為最多只提醒而不擋。這個代理成本買不到任何擋停效果,而且推送被擋的原因是一條依據不足的規則。
  - 另有一個沒定義的狀態:第一判是 `unsure`、仲裁還沒回來時,算不算「還沒判」而擋。S5 只寫了仲裁之後的結果。
- 引句:「還沒判:擋,印跑盲判的指令(d2)。」
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:390`(出處不全規則只准 hint 級,共 7 條,已實算)。

severity: major
blocking: 是(判準:結果檔格式與驗證器現況衝突,spec 要的「可單獨一份」做不到)
- spec 段落:〈範圍〉4 結果檔、S5
- 問題:spec 說 `rule_hits` 可以跟 `segments` 同檔或單獨一份。但 `_kt_bj_validate` 對下列情況都直接拒收:
  - 最外層只認 `segments`,多一個鍵就報錯。
  - 要求 `segments` 是非空清單。只有 `rule_hits`、沒有 `segments` 的檔會報「要有 segments 清單」。

  `_cmd_codeloop_blind_judge` 的收尾邏輯也有衝突:若只有 `rule_hits`,`entries` 為空,`n=0`、`skipped=[]`,`len(skipped) == n` 成立,會誤報「0 格全都已有紀錄」並回 2。

  另有三處 spec 沒寫:
  - 結果檔只有 `rule_hits` 時的驗證與落帳路徑。
  - 記帳時為了驗證 seg 必須重跑覆核命令;工具逾時或沒裝時,整份會被拒收。
  - `blind-judge --template` 要怎麼選印覆核份(沒有 `--rule-hits` 之類的旗標),以及 `--part` 屬於情境份還是覆核份。

  此外,入口 `_cmd_codeloop_blind_judge` 在到達新邏輯前,會先要求情境型錄與情境段都算得出來(`_KT_DT_ERR` 與 `_kt_bj_segments` 回 None 都直接回 2),覆核命中的判定被綁在不相干的條件上。
- 引句:「頂層多一個鍵 `rule_hits: [{"seg": <指紋>, "verdict": "real|false|unsure", "reason": "…"}]`,可以跟 `segments` 同檔或單獨一份」
- 佐證:file: `scripts/lumos:74070`、`scripts/lumos:74075`(驗證器的兩個拒收點)。
- 佐證:file: `scripts/lumos:74217`(收尾的全已有判斷)。

severity: minor
blocking: 否(判準:有具體失敗情境,但只影響未宣告一般段的專案與少數環境)
- spec 段落:〈範圍〉2、〈範圍〉6、S7
- 問題:`_lint_new_tools` 在組完一般段的 `cmd_targets` 後,若為空就直接 `no-files` 返回,在 review 段之前。所以只宣告了 `review`、沒有一般 `kt` 命令的專案,覆核根本不會跑,也不會印任何「覆核沒跑」。同樣的早退還有放行檔讀不了(`werr` 自動放行)。
  - S7 只列了三個原因:沒宣告、工具不可用、時間預算用完。實際還有參數太長(`too-long`)、一般段早退、放行檔壞掉,都沒歸類。
- 引句:「推送前印一行「覆核沒跑:<沒宣告|工具不可用|時間預算用完>」」
- 佐證:file: `scripts/lumos:42623`(`cmd_targets` 為空的早退)。
- 佐證:file: `scripts/lumos:42627`(`werr` 的早退)。

severity: minor
blocking: 否(判準:新碼出例外時會連帶讓一般段整道放行,但需要新碼本身有 bug 才觸發)
- spec 段落:〈範圍〉2
- 問題:`_codeloop_lint_new_step` 對整個 `_lint_new_verdict` 包了 `except Exception`,一律 fail-open 放行。覆核段與判定帳解析的新碼若出例外,例如帳裡的 `rule_hits` 格式壞掉,會讓一般段的新增告警整道放行。spec 沒說覆核段要與一般段隔離例外。
  - spec 也沒寫覆核擋停是否遵守 `mode`(off、warn)與 `LUMOS_SKIP_LINT_NEW`。`_lint_new_classify` 在 `mode=warn` 時把擋停降成警告,覆核這條新路徑沒走 classify,可能不受設定控制。
- 引句:「`_lint_new_classify` 的「有新增就擋」只看一般段」
- 佐證:file: `scripts/lumos:74564`。
- 佐證:file: `scripts/lumos:42410`。

severity: minor
blocking: 否(判準:統計建議可能被誤導,但只出建議、不自動改)
- spec 段落:〈範圍〉7、〈實務隱患〉、S8
- 問題:
  - 內部數字矛盾:範圍 7 的說明寫「七成、八成是本案自己的數字」,但正文定義的門檻是一成、九成、八成,沒有七成。
  - 統計偏誤:`real` 判定被擋時,AI 可以自己跑 `lint-waive` 放行。統計算「被人放行」只計 origin human,所以 AI 全部自放行時,「被人放行少於一成」成立,會建議把規則升到 `rules/` 直接擋。AI 繞過反而讓統計顯示「規則很準」。
- 引句:「七成、八成是本案自己的數字,上線後照 REVISIT 回頭校準」
- 佐證:file: `scripts/lumos:41180`(AI 放行的 origin 判定)。

severity: minor
blocking: 否(判準:`--ack` 的既有用法會讓準確率樣本長不出來,RETIRE-IF 靠它)
- spec 段落:〈用詞〉人複查、RETIRE-IF
- 問題:全系統所有提醒印的看過指令都是 `lumos lint-waive --ack --all`,這個指令不帶 verdict。`_lint_waive_ack` 只處理 `_lint_waiver_ai_unacked` 的紀錄,一旦用不帶 verdict 的 ack 標成看過,之後就不能補 verdict。spec 沒定義:
  - `--ack --all --verdict ...` 的批次語意。
  - 已看過的紀錄能不能補 verdict。

  結果多數誤報放行會被不帶 verdict 的 ack 吃掉,準確率的樣本不足 20 筆,RETIRE-IF 的九成判斷與升降建議長期無法運作。
- 引句:「不帶 `--verdict` 的 ack 照舊只記看過、不進準確率。」
- 佐證:file: `scripts/lumos:41192`(`_lint_waive_ack` 只標未看過的 AI 放行)。

severity: minor
blocking: 否(判準:`review` 段是通用設計,但材料與例外判斷綁死規則包型錄,目前 62/62 有編號所以暫無實害)
- spec 段落:〈範圍〉1、〈範圍〉4 材料、〈用詞〉對應型錄列
- 問題:`review` 段接受任何命令,但材料與出處不全例外都靠規則訊息開頭的 `[型錄編號]` 對到 `main_rows`。消費專案若放自己的命令,命中沒有編號或編號對不到列時:
  - 材料四欄怎麼印、出處不全判定怎麼算,spec 沒寫。
  - `main_rows` 的編號正規式只認 9 個前綴,其他前綴會對不到。
  - 材料取「命中行前後各 8 行」也沒說多行命中(用起點還是範圍)、檔頭尾邊界(第 3 行命中)與超長行怎麼處理。S6 只測了同片段兩處。
  - 對應型錄列是「規則 → 列」唯一,但反過來同一列對應多條規則(STATE-16、STATE-7、DATA-30、ARCH-50 各被兩條規則引用),spec 沒影響,僅說明。
- 引句:「本案前提是一條規則只對一列(2026-11-07 用程式核對:62 條各唯一對到一列)」
- 佐證:file: `configs/ast-grep/kotlin-android/check.py:92`(編號正規式)。

最嚴重:major,blocking 5 條(findings 1–5),minor 5 條。
