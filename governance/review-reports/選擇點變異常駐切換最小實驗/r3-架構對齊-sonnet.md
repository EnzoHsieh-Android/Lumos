severity: minor

## A1 SEE 行寫成帶句子的說明,跟既有「SEE 不寫句子」的格式不一致
severity: minor
blocking: 否
引句:「補一行 SEE 指到本計劃(常駐切換已用實測上限否決),讓查 choice-kill 的人看得到。」
既有做法:專案 CLAUDE.md 的前綴表寫「`SEE:` 不寫句子,至少一個 `[[連結]]`」。唯一一條既有的 Systems 層 SEE 是 `Systems/每輪修補差異派工.md:94`,只放 `SEE:[[Systems/design-loop]]`,沒有說明句。
差在哪:這份把「已用實測上限否決」寫在 SEE 的括號裡。結論本身已經有出處:計劃的 WHY 行、第二段計劃〈依據來源〉那列。SEE 只放連結即可,那句話可以放到 WHY 或 RULE 行。我數到 Systems 底下指向 Projects 的 SEE 是 0 條(只數到上面那一條 SEE),所以「Systems 的 SEE 指向 Projects 計劃」沒有先例,但也沒有規定禁止。我對這點判不準,標 ⚠:是否採用由編排者裁。

## A2 其餘對照項都走既有做法,沒有第二種做法或跨層直呼
severity: clean
blocking: 否
引句:「在 [[Projects/選擇點變異加速第二段_計劃]] 的〈依據來源〉那列與 PRIOR-ART 排除句各補一句本計劃的上限數字」
既有做法與對照結果:
- 否決結論寫回舊計劃:第二段計劃已有〈依據來源〉表的「不做 mutant schemata」那列(`Projects/選擇點變異加速第二段_計劃.md:170`)與 PRIOR-ART 的「排除:mutant schemata」句(同檔 `:35`)。這份在原處補一句,不另開新表,也不翻案舊否決。
- 回頭條件:格式是 `REVISIT:YYYY-MM-DD 一句做法`,跟 `Projects/選擇點變異加速第二段_計劃.md:37` 同形,另配 RETIRE-IF 一行,符合 CLAUDE.md 鐵則 4 與設計與排查那節。
- status 與 lands_in:成熟的先例是 `Projects/檢索核心重建_計劃.md` 一類只下結論的計劃,用 `status: doing/done` 加 `lands_in` 指到現有的 Systems 節點,REVISIT 留在計劃裡。這份 status 是 doing,因為 S2(補第二段計劃兩處文字)還沒做,合理。專案裡 `superseded` 是給被取代的計劃用的,這份不屬於。
- 附帶看到的一處不一致:`lands_in` 列了 `Systems/guard-kill`,但本計劃不改程式。唯一落到那裡的只有一行 SEE,而且 `Systems/guard-kill.md` 目前沒寫負責範圍。這是風格與慣例層的問題,不算引入第二種做法,不列為 blocking。

最嚴重:minor
blocking 條數:0
