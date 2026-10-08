severity: minor

整體判斷:這份修正差異的主要邏輯成立,我沒有找到會導致誤放行或誤擋的問題。`t_slots_retire_followups` 在 python3.14 下 18 項全過(跑前清過 `__pycache__`)。下面 3 條 finding 都不擋推送。審材外的查證與突變實驗在 `scratchpad/mu` 的臨時 clone 裡做,沒動 repo。

## 逐點走過、判無問題的路徑

- **判定與 ack 讀到的文字是同一份。**
  - 判定那邊用 `_drift_tree_env`,解碼 `utf-8-sig`;ack 那邊用 `env_text`,也是 `utf-8-sig`。兩邊都走 `_ns_summary_logical(text)`。
  - 它對每個實體行先做 `strip()` 再用單一空格接回。所以 CRLF 的 `\r` 和 BOM 不會讓兩邊的整條文字不同。
  - 比對鍵 `_drift_ack_key` 也會 `strip()` 再 NFC 正規化。
- **沒有續行時,整條等於實體行。** 沒有續行的 RULE 在判定和 ack 兩邊都等於原本的實體行,所以不受影響。
- **其他種類的表態沒變。** `_drift_ack_text` 對非 retire 種類(c1–c5、probe、m1)直接回 `lines[line - 1].strip()`,和舊行為逐字相同。
- **只改續行裡跟條件無關的字(例如補 `[confirmed:]`)導致舊表態失效,可以接受,不會卡住使用者。**
  - 判定要的是「本次推送讓條件從不成立變成立」。`_drift_probe_old` 只比條件元組。
  - 起點已有同一條件的行不是候選。所以只有在同一個推送範圍內既轉成立、又改文字時才會失效。
  - 失效後的補救是重新 ack 一次,代價小。
- **同一篇裡兩條整條完全相同的 RULE,ack 一條會放行兩條。** 這是「路徑 + 原文 + 種類」比對的固有性質,兩條也確實無法區分,可接受。
- **舊表態相容。** `_DRIFT_KINDS` 的 `retire` 是本功能新增的,上線前沒有舊 retire 表態檔需要相容。r1 到 r3 之間若有人對「有續行的 RULE」記過實體行表態,會失效,屬預期。
- **記帳出錯。**
  - `_gate_event` 只吞 `OSError`,其餘例外會往外拋。
  - 外層 `except` 的兜底記帳自己包了 `try/except`,不會再拋。
  - 帳檔不存在時 `_gate_event` 回 None,`_gate_event_or_warn` 靜默,也沒問題。
  - 起點是 tuple 時不會呼叫(`rt_mode != "off" and not isinstance(base, tuple)`)。

## 發現

R3C1
severity: minor
blocking: 否 — 對續行或正文行下 ack 不會報錯,只是之後不會被比對命中,使用者重打正確行號即可。
1. `cmd_drift_ack` 收到的 `line` 如果是續行行號,或是摘要區外正文裡的 RULE 行,`_drift_ack_text` 查不到整條,會退回記該實體行。表態檔照寫,指令也成功回 0,但判定給的原文是整條,永遠對不上。使用者不知道這筆表態是廢的,下次推送仍被擋。
   - 走法:Pay 摘要裡的 RULE 第 5 行,續行在第 6 行。`lumos drift ack Systems/Pay 6 --kind retire --reason x` 會記下第 6 行的 `[retire:when-file:src/a.py]`。
   - 擋下時印出的行號是 `no`,也就是第一行,所以照提示打不會踩到,觸發需要手打錯行號。
   - 建議:`kind == "retire"` 時,若 `line` 不在 `_ns_summary_logical(text)` 的鍵裡,就擋下並提示「請用條目第一行的行號」。
引句:「    return lines[line - 1].strip()」

R3C2
severity: minor
blocking: 否 — 純測試覆蓋缺口,行為本身目前正確。
2. 記帳改動只有「成立時一筆 blocked」與「放行不寫」兩個斷言咬得住。我對 `scripts/lumos` 的臨時副本逐一做突變,重跑 `-k t_slots_retire_followups`,下列突變全部仍是 18 passed:
   - 只有判不了時也記帳(`if must or unknown` 改成 `if must`)。
   - 只有判不了時記成 `blocked`,而不是 `warned`。
   - 成立且 block 時 `hard` 改成永遠 False。
   - `nodes` 改成空清單。
   - `base_sha` 對非字串起點不轉成空字串。
   - 例外兜底那一筆(我的突變造成語法錯誤而非行為變更,但測試裡沒有任何情境走到這條路徑)。
   - 對 `kind != "retire"` 也記整條:本測試只測 retire,其他種類的 `_drift_ack_text` 行為不在這支測試裡,要靠別的測試守。
   - 建議:補一個「預算用完只有判不了」的情境,斷言有一筆 `warned`、`handle == 0`、`listed == 1`、`hard` 為 False。再補一個讓 `_drift_probe_check` 丟例外的情境,斷言兜底那筆帶 `error`。
   - 另外,斷言 `ev[0].get("kind") == "blocked"` 時順手加上 `hard` 和 `nodes`。
引句:「放行不寫帳(drift-check 閘的既有規矩」

R3C3
severity: minor
blocking: 否 — 只在極端情況觸發,而且判定行為沿用既有的「沒跑完不擋」設計。
3. ⚠ 外層 `try` 裡,`_drift_retire_report` 先寫完正式那筆帳,之後 `_drift_print_findings` 或 `_drift_print_hints` 若丟例外,`except` 會再記一筆 `warned`,同一次推送出現兩筆 `check: retire`。同時 `return 0` 會把原本該擋的 `must` 變成放行。
   - 這個結構在這份 diff 之前就有,新增的兜底記帳讓重複記帳變得可能。
   - `_esc_clean` 已把控制字元清掉,我沒找到現成會丟例外的輸入,所以不升級。
   - 若要收斂:把兜底記帳限定在「report 尚未記過帳」時才寫。
引句:「沒跑完也留一筆(r2 架構席:m1 的兜底照記帳)」

## 圖譜鏡頭

派工時沒有附 LUMOS-IMPACT 的固定席筆記,尾端也沒有備援段,所以我只能依這份 diff 實際動到的節點判斷:

- **`Systems/存量漂移守衛`:不影響其合約。**
  - 摘要 WHY 行改成「表態記接回續行的整條」,和 `_retire_lines`、`_drift_ack_text` 的行為一致。
  - 「記帳同閘其他判定放行不寫」也和 `_drift_retire_report` 一致。
  - 沒有動 `RULE:` 或 `★INVARIANT★` 行。
  - 綁的 `[test:t_slots_retire_followups]` 在改動後仍然通過。
- **`Issues/治理帳多個寫入者都沒上鎖`:不影響。** 只在「現在怎麼繞」補了一句寫入頻率說明,「什麼算修好」的四條判準沒動。新增的 `check: retire` 事件走通用寫入器 `_gate_event`,沒有新增寫入者種類。
- 我搜過 `docs`,沒有其他筆記還在寫「表態對第一個實體行」,也沒有地方記「撤除條件每次都記帳」。

## 突變實驗(第 3 點)

- 把判定原文改回實體行,同時讓 ack 只記實體行,這是 r2 修之前的狀態。結果 ①b 和 ①c 紅(`16 passed, 2 failed`)。
- 這顯示「改續行條件後舊表態失效」與「第一行相同但續行不同的兩條不互相放行」這兩項確實咬住。
- 沒有針對 ① 與 ②–④ 另做突變:① 在上一個突變下的結果沒單獨列出;②–④ 依 diff 是從舊測試搬過來,僅有小工具抽出,我沒做突變。

最高嚴重度 minor,blocking 0 條
