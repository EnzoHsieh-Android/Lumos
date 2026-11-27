severity: major

## F1 既有的「釘值」測試用真型錄掃樣本檔,上線後會紅,spec 沒列也沒處置
severity: major
blocking: 是(判準:照 spec 實作後,既有測試在本機閘與 CI 必紅,而 spec 的測試清單與落點都沒涵蓋;要改釘值就得動 `scripts/test_lumos.py`,又要先簽章,但〈實務隱患〉只寫了要簽章)
引句:「只有同一級類別的行,打亂的清單跟改之前逐項相同(同一份清單、同一個種子),挑到同一個壞法。多級混合的行」
- 做法:我在 repo 的複本裡照 spec 〈做法〉改了 `_choice_pick_iter` 的排類別段(三級各自打亂、依序串接),只跑 `t_choice_points_batch2_stable` 與 `t_choice_points_batch3_*`。
- 還原成原版 `scripts/lumos` 時 `t_choice_points_batch2_stable` 全綠。改成三級挑法後,`t_choice_points_batch2_stable`(`_CB2_S7_PIN`,`scripts/test_lumos.py:148731` 起)與 `t_choice_points_batch3_stable` 各紅一條,批 3 其餘案例仍綠。
- 82 條釘值裡有 8 行改挑,原挑法與新挑法如下:
  - `arid.kt:18`:`C-1`(ROR)改成 `C-18`(SBR)。
  - `choice.kt:58`:`C-1` 改成 `C-20`(API)。
  - `choice.kt:60`:`C-1` 改成 `C-22`。
  - `choice.kt:61`、`66`、`67`、`68`、`69`:`C-18` 改成各自的 API 列(`C-23`、`C-28`、`C-29`、`C-30`、`C-31`)。
- 這兩條測試的宗旨是「挑法跟加入前釘下的相同」。spec 沒說要重釘、豁免或拆成同級行,也沒提這兩條會紅。
- 上線前重算紀錄(S7)只量實驗專案的 4a 範圍,量不到這 8 行。
- 我沒跑完 `-k choice` 全部案例,別的選擇點測試有沒有同樣被帶紅,spec 作者得自己掃一遍。

## F2 S6 的測試形狀測不到挑法改了:`_choice_disposition` 根本不看壞法
severity: major
blocking: 是(判準:驗收條款綁的測試不論實作怎麼挑都綠,等於沒有守衛,S6 也就無法證明「已處置的行不重跑」)
引句:「已殺掉或已放行的行 應 在挑法改了之後照舊算有效處置、不重跑」
- 輸入:S6 的 killed 行,帳上有 killed 事件且 `killing_test` 在 bound 裡。
- `_choice_disposition(evs, waived, bound)`(`scripts/lumos:79774`)的參數裡沒有壞法與挑法。函式只看帳上最新一筆的 verdict 與 bound,新舊挑法在它眼裡一模一樣,直接呼叫它的測試永遠綠。
- 「不重跑」的判斷其實在 `_choice_kill_pick`(`scripts/lumos:80047`):`disp in ("waived","killed")` 就 `done += 1; continue`。S6 要綁的是這一支,而且要用新舊兩種 `res["lines"]`(各自挑出不同壞法)分別餵。
- 題目要求驗的四種狀態,spec 只管了 killed 與 waived:
  - killed:有效處置,不重跑。
  - waived:有效處置,不重跑。
  - survived:守的測試雜湊沒變就帶過去、不重跑,見 F3。
  - no_result:一律重跑,而且用新順序挑。
- 另外還有 stale(殺掉它的測試已沒有條款綁著),也是重跑。spec 沒有任何一條條款釘 survived、no_result、stale。

## F3 「存活的行用新順序重跑」不成立:守的測試沒變的存活行被帶過去,顯示的卻是新壞法
severity: major
blocking: 是(判準:spec 宣稱的行為與程式在這條路徑上不同,S7 的「改挑行殺/存活數」口徑也會因此失真)
引句:「新行與存活、跑不出結果要重跑的行才用新順序。」
- 輸入:帳上最新一筆是 survived、`tests_sha` 沒變、不是 cov 判的行,上線後第一次推送。
- `_choice_kill_pick`(`scripts/lumos:80070`)那條 `elif disp == "survived" and only is None and evs[-1].get("tests_sha") == tests_sha` 把它放進 `carried`,不重跑。這筆存活判的是舊壞法。
- 但 `_choice_points_lines` 與推送閘用的 `x["mutant"]` 是新挑法挑出的壞法。帳上寫「存活」,畫面上卻顯示一個從沒跑過的新壞法,人去補測試或放行都是針對錯的壞法。
- 同樣的錯位對 killed 與 waived 也成立:〈白話〉寫「舊行停在舊挑法挑到的那個壞法」,但程式沒有任何地方保留舊壞法,顯示的是新挑法的壞法,帳上的 `new_sha` 才是舊的。
- spec 的〈實務隱患〉只講了「舊放行蓋住新順序」,沒講這個錯位。

## F4 RET 與等級表的上線順序沒定義,自檢紅燈對兩個順序的後果不同
severity: minor
blocking: 否(判準:是排程銜接問題,在 repo 內開發階段就會紅,不會傳到已安裝的消費專案)
引句:「不是兄弟寫法也不是運算子)。自檢會擋住漏補。」
- spec 只改第四批計劃,補一句「`CHOICE_TIERS` 加 RET」。
- 第四批計劃 `status: todo`,它的〈做法〉第 4 點寫的是 `CHOICE_CATEGORIES` 尾端加 RET、同時加 RET:2。
- 若第四批先進主線,本計劃的 `CHOICE_TIERS`(只有 7 類)一落地,自檢就把整張表判壞。反過來也一樣:先進的那份要在同一個提交補另一份的鍵。spec 只講了其中一個方向。
- 自檢的實際後果:`_choice_tables`(`scripts/lumos:78813`)在 probs 非空時回 `None, "表壞…"`,所有取表的入口(`scripts/lumos:79658`、`80110`、`81370`、`82495`、`82656`)都擋。
- `CHOICE_TIERS` 與 `CHOICE_CATEGORIES` 同在 `check.py`,同版本一起落地時,已安裝的消費專案不會自己撞上這條。
- 版本錯位時是靜默退回舊挑法,沒有提醒。例如規則包複本是舊 `check.py`、lumos 是新版,表裡沒有 `tiers` 鍵,`tables.get("tiers")` 為 None。

## 已讀,無 finding 的節與查證
- `tiers=None` 等於舊挑法:成立。
  - 舊程式是 `cats = [c for c in categories if …]` 再 `random.Random(seed).shuffle(cats)`。
  - spec 的 None 分支是整個當一級,清單、順序、種子都一樣。
  - 單一級的行也同理(S2、S4 單級行、S5 都成立)。
- 〈白話〉的類別列數表(35、2、1、5、8、2、2,共 55)我用型錄機械數過,吻合。
- 跳過集合以 `new_sha` 比對、不受挑法順序影響:成立。
  - `_choice_pick`(`scripts/lumos:79383`)的 skip 看的是 `identity["new_sha"]`,`exhausted` 判法也只依賴 `pick()` 是否還有候選。
- 〈回退〉:有效處置的鍵是 `(檔, 行指紋)`,不帶壞法,回退後舊紀錄仍有效,與程式相符。
- 〈白話〉裡論文引用、〈依據來源〉、PRIOR-ART、RETIRE-IF:本輪沒有新宣稱需要查證,已讀,無 finding。

最嚴重 severity:major;blocking 條數:3(F1、F2、F3)。
