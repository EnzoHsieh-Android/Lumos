# r4 收貨紀錄(code-舊句檢查;上限後破例驗收輪)

凍結材料:89884251..73d55192 的 git diff -U10(不含治理帳、錨點、卷證),851 行;`r4-snapshot.patch`。破例理由見 `r3-intake.md` 末節。
3 席:正確性 opus、資安 sonnet 5.5、外家否決 Codex(gpt-5.6-sol xhigh)。

## 席位收貨

- 3 席全交,report-normalize 都已正規化;quote-check:正確性全數錨定,資安與外家否決 clean、沒有引句(不適用)。
- 主 repo reflog 在 12:41 多一筆 `reset: moving to HEAD`;同時段主 repo 有別的會談在動(README 改動、12:37 跑過健檢),三席都沒自報動過主 repo(外家否決在唯讀沙盒、正確性在自己的複本),判不出是誰;主 repo 沒有暫存的東西,編排者沒動它,記在這裡。
- 發現 3 條(機器數):正確性 3;major 0。

## 判讀

- 驗收輪沒有 major,照 r3-intake 末節的預先裁定:不再改程式,附理由放行。
- 正確性 F1(超長行用純子字串判「有關」偏寬):只影響把舊句檢查設成 block 的專案(預設 warn),而且不會放掉真的舊句,寫進 Issue「舊句檢查超長行判準偏寬與留痕殘行」。
- 正確性 F2(留痕短寫只回 False、殘行可能讓下一筆接成壞 JSON):影響兩週量測「帳沒記到」的計數;寫進同一篇 Issue,REVISIT 定在兩週回頭那天之前處理,計劃〈誠實界線〉指到它。
- 正確性 F3(計劃文字沒跟上第 3 輪收窄):只改筆記,補齊。

## 機械重現

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | 讀席位在真 repo 的重現(刪 get_user、長行只有 get_user_id、block 回 1)與判準程式 | HIT(現象成立),放行進 Issue |
| 正確性-F2 | 讀 `_drift_m1_ledger_miss` 呼叫端 | HIT(回傳值沒人讀),放行進 Issue |
| 正確性-F3 | 讀計劃帳欄位、結論行、S6 | HIT;補齊(只改筆記) |

## 處置

- 3 條 minor 全部 accepted(附理由),folded 空、refuted 空。
