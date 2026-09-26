severity: clean

已看,無:全篇逐節讀完(一句話/適用範圍/做法一二三/條款 S1–S11/回退/實務隱患/不在本案/誠實界線/審計修正紀錄)。針對「整合與知識同步」鏡頭逐一核對如下,均與程式碼現況接得上、與既有決定一致、r2 指出的問題也確實解了:

- `_review_yield_round`(scripts/lumos:7364):回傳 dict 含 `F`(折)欄,純函式、對迴圈種類不分——spec PRIOR-ART 一句「直接呼叫,不靠處置閘印出的那段」與 r2-intake r2a-F2 的折入結論(部分 HIT:函式本身不分迴圈種類,漏掉的是印出點對 code 迴圈被跳過)完全對得上;`_review_yield_round` 的呼叫點目前只有問閘尾(scripts/lumos:18550,被 `if not readonly and not str(loop_id).startswith("code")` 包住)與 `gov --stats`(scripts/lumos:6725),spec 要求 cap_hint 另外直接呼叫、不繞這個印出點,可行且無旁路副作用。
- 空輪算折 0(S7):`_loop_status_disposal` 的「處置集合」步驟(scripts/lumos:18352–18376)本就用逐列 `findings` 欄判斷 vacuous(`carrier is None and all(_fz)`),這正是 spec 講的「各席帳的 findings 全是 0」的依據欄位,不是 `_review_yield_round` 內部欄——spec 文字「那一輪沒有彙總帳時……算折 0;否則印『這輪沒記處置』」與這段既有邏輯的落點(carrier 有無)一致,兩者不衝突。
- `_TIER_PARAMS`(scripts/lumos:9801)與 `_loop_anchor_tier`(scripts/lumos:17905,取首筆帶 tier 的值):loop next 內既有 `eff_tier = anchor or tier` 再 fallback `"standard" if panel_fmt else "legacy"`(scripts/lumos:10368–10398)已把 `anchor` 可能是 None 的情形處理掉——cap_hint 若在 `emit()`(scripts/lumos:10419 起)內取用同一個已算好的 `eff_tier`/`cap`,不會重蹈直接 index `_TIER_PARAMS[None]` 的坑;`_gated_seats_for`(scripts/lumos:18045)也示範了處置閘直接呼叫 `_loop_anchor_tier` 拿到 None 時走 `_TIER_ROSTER.get(("code", tier)) → None → skip` 的既有容錯樣式,disposal 端「自己查分級上限表」照這個樣式做不會炸。
- `_panel_retired_for`(scripts/lumos:8197,`rounds[0]` 的 ts 日期 ≥ 2026-08-26 cutoff)語意與「只印給 2026-08-26(含)之後開的多席迴圈」精確對應,S9 的排除範圍(light/code 循序單審/舊迴圈)在程式碼裡分屬三個不同判準(light 旗標、`_roster_kind==code` 且 `not panel_fmt`、`_panel_retired_for`),spec 三個都點到,沒有漏項。
- `--json` 欄位改名 `cap_hint`/`hint`(不用 `advice`/`advisory`):loop next 的 `emit()` 既有輸出本身就帶了一個 `"advisory"` 鍵(scripts/lumos:10421,"分級由編排者第一筆記錄時宣告……"),跟舊草案想用的 `advice`/`advisory` 撞名——r2 折入紀錄裡「JSON 欄位改名避開 advisory」這個理由是有機械根據的,不是空想。
- 處置閘唯讀慣例(S3):`_loop_status_disposal` 簽名帶 `readonly=False` 參數(scripts/lumos:18265),既有的 roster/severity 觀測尾巴、intake 觀測、`_review_yield_round` 問閘尾都已經用 `if not readonly:`/`if not readonly and not ...code` 包住(scripts/lumos:18534–18552),三個呼叫端(freeze 兩次 scripts/lumos:634/648、golden 回放 scripts/lumos:797)都傳 `readonly=True`——spec 說「新段落自己包一層唯讀判斷,不假設外面已經包好」是對的:這幾段觀測尾巴是各自局部判斷,不是外層一次包住全函式,cap_hint 不能假設自己天然被涵蓋。
- 處置閘「判定之後印,不論過或沒過」(S2)與 G3/一輪多處置帳/findings 壞值三個提前 `return 2`(scripts/lumos:18325/18350/18365)的關係:這三個提前 return 在函式內物理位置早於 PASS/FAIL 判定與 roster/severity 尾端,既有註解已明講「三個提前 return 2 路……刻意不掛」(scripts/lumos:18486)——只要 cap_hint 印出點跟這些觀測尾巴一樣放在判定之後、提前 return 之後,結構上就自然不會在那三條 abort 路徑印出,不需要 spec 額外交代(這點原先懷疑是缺口,查完既有慣例確認不是)。
- `emit()` 是 loop next 文字與 --json 唯一的輸出收斂點(scripts/lumos:10419–10421 起組 `out` dict,10563 起分流印文字或 `json.dumps`),spec「文字與 --json 都要印」「cap_hint 只加一個欄位」在這個既有結構下是可行的最小改動,不會動到 `phase`/`tier`/`round` 等既有欄位值。
- `cap-reached` 治理帳寫入(scripts/lumos:10677 `_loop_gov_mark(env, loop_id, "cap-reached", ...)`)是到上限時原本就會發生的既有行為,不是這份 spec 新增的——S11「這段印出、治理帳與審查帳行數不變」讀作「這個新功能本身不多寫」而非「到上限這件事本身不能有任何寫入」,兩者不矛盾,disposal 端本就只讀不寫,S11 對它是天生成立。
- lands_in 落點 Systems/loop-convergence-recording:讀過該節點 summary 與 decisions(d1 tail-K 滑動窗、d2「可觀測性+摩擦+一個地板,非機械自我終止 oracle」的誠實定位)——cap_hint 只印不擋、不改收斂判定、不改嚴重度自報機制,跟 d1/d2 的既有邊界沒有衝突;d2 的誠實校正精神與這份 spec 的〈誠實界線〉一節同調,不衝突。

實務隱患(逐類):
- 併發:無新增——只讀既有帳本(`rounds` 參數/既有讀帳路徑),不另開檔案控制代碼,跟 disposal 既有讀法共用同一份 `latest`/`rounds`。
- 效能:無實質風險——`_review_yield_round` 是純記憶體運算(輸入是已讀進來的 `rounds` list),每輪呼叫一次,不重讀帳本、不讀凍結審材(quote-check 那類 IO 密集操作不牽涉)。
- 金流/對外送出/不可逆:已排除(spec 自己列了,查證後同意:只印文字、不呼叫外部服務、不寫任何檔,回退即拔掉兩處呼叫)。
- 守衛面:無——S1/S2/S11 綁測試「階段名、退出碼、過關判定不變」,且 loop next 用同一個 `emit()` 收斂點、disposal 用既有觀測尾巴的包法,結構上不會意外影響判定路徑。

沒有查到跟第 2 輪(r2-intake)相牴觸或第 2 輪修復不完整的地方;沒有找到新的 blocking 級問題(未定義詞/欄位/旗標、壞引用、內部矛盾、與程式碼現況不符的宣稱、可執行性缺口皆未命中)。

總結:severity clean,blocking 0 條。
