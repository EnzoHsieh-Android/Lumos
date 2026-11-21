severity: minor

整體判讀:修補處在整合與文件同步上大致站得住,我沒找到 blocker 或 major。我實跑的行為案例都符合修後的預期。剩下的 5 條都是 minor,而且 5 條的成因在修前就存在。

## 行為核對(修後 `af2fb6f85`,在臨時副本裡加探針跑)

**repair 組**

| 案例 | 結果 |
|---|---|
| G3:不帶 `--loop` 卻帶 `--finding-seat c1=亂寫` | rc2,帳不變。訊息:「擋下:--finding-seat 要跟 --loop、--round 一起給」 |
| G5:首筆時間讀不動、沒帶席位 | rc2。訊息含「補帶 --finding-seat」和脫困句;治理帳多一筆 `finding-seat-badts`(實數 1) |
| G5:同一情境,補帶 `--finding-seat` | rc0 |
| G1:`_seat_noise_name` 對 `外家-gemini-2-flash` 與 `外家finder2-codex` | gemini 版本號不動;`外家finder2-codex` 併成 `外家finder-codex` |

**preserve 組**

- G1:我拿真帳 `docs/.canary-log.jsonl` 的 795 個席名跑 `_seat_noise_name`。`正確性2-sonnet`、`正確性-r2-sonnet`、`正確性r2-sonnet` 等都併成 `正確性-sonnet`,`架構對齊`、`邊界`、`資安` 同理,沒有誤切。
- G2、G4、G6、G7 沒有另跑探針,只確認 `python3.14 scripts/test_lumos.py -k finding_seat` 的 54 條全過。要翻紅的核對沒做,所以這幾組我沒有獨立證據。
- G3 preserve(不帶 `--loop`、不帶席位的載體照舊能記)沒有跑,留未判定。

## Findings

severity: minor
blocking: 否
file: `skills/lumos-code-loop/SKILL.md:61`
失敗場景:接手的人照第 6 步下面那條完整的 `lumos canary record none ...` 指令抄,生效日後載體會被擋。這條指令只有 `--finding-kind`,沒有 `--finding-seat`。要到上一行(第 60 行)的粗體段才看得到必填。照做得到 rc2,訊息會指路,所以代價是多一輪。
引句:「`--finding-kind` 一個 id 一個旗標。」
歸因:有證據的原有漏查。修補把同類句子補進了 `reference.md:616` 與 `reference.md` 載體範本,卻漏了 SKILL.md 這一行。
兩版查證:`grep -c finding-seat skills/lumos-code-loop/SKILL.md`,746df1cbd 修前為 0,af2fb6f85 修後為 1(只在第 60 行)。

severity: minor
blocking: 否
file: `skills/lumos-code-loop/reference.md:38` 與 `skills/lumos-code-loop/reference.md:477`
失敗場景:「步驟總覽」第 6 步與頁頂的「現行一律 `canary record none …`」那兩句,仍寫成「carrier 帶 --findings-set/--folded-set/--accepted-set/--refuted-set(2026-09-09 起必帶)」。讀總覽的人不知道還有第四個必帶旗標。
引句:「carrier 帶 --findings-set/--folded-set/--accepted-set/--refuted-set(2026-09-09 起必帶),」
歸因:有證據的原有漏查。
兩版查證:`git show <commit>:skills/lumos-code-loop/reference.md | sed -n 38p | grep -c finding-seat` 修前 0、修後 0。第 477 行同樣是 0。

severity: minor
blocking: 否
file: `skills/lumos-code-loop/reference.md`(載體席範本,約第 134–142 行)
失敗場景:範本裡的 `--accept-reason <id=理由>  # 放行幾條就給幾個旗標` 行尾沒有 `\`,下一行 `--refuted-set ...` 在 shell 裡會變成獨立指令。修補只給 `--refuted-set` 行補了 `\`,後面接 `--finding-seat`,上一行的斷點沒修。直接貼進 shell 會執行失敗。
引句:「  --accept-reason <id=理由>  # 放行幾條就給幾個旗標」
歸因:有證據的原有漏查。修前同一行就沒有續行符號。
兩版查證:`git show 746df1cbd:skills/lumos-code-loop/reference.md | sed -n 138,139p` 與 af2fb6f85 版同範圍,兩版都是 `--accept-reason` 行無 `\`,下一行另起。

severity: minor
blocking: 否
file: `scripts/lumos:19601-19608`(`_finding_seat_required_block` 的壞時間檢查)
失敗場景:壞時間檢查排在生效日比較之前。把 `_FINDING_SEAT_SINCE` 退成 `9999-12-31`,或在 2026-11-22 之前使用,只要同迴圈帳上有一列時間讀不動(沒帶時區),載體不帶 `--finding-seat` 就會 rc2 並留 `finding-seat-badts` 事件。這跟〈回退〉寫的「旗標變回選填」衝突。真帳 6608 列全帶時區,所以只有人工改壞的帳才會撞到;脫困句(補帶 `--finding-seat`)也夠用。
引句:「判不了是不是生效日後開的迴圈,不能判定可以免帶 --finding-seat」
歸因:有證據的原有漏查。修後只是多了事件與脫困句。
兩版查證:測試總檔預設 `LUMOS_FINDING_SEAT_SINCE=9999-12-31`,把 code-zz 迴圈首列 ts 改成 `garbage` 後記載體,修後得到 `rc 2 擋下:這個迴圈帳上有一筆時間讀不動…`。修前 `746df1cbd:scripts/lumos` 的 `first = min(keys)` 之前同樣有 `if any(k is None for k in keys): … return 2`,行為相同。

severity: minor
blocking: 否
file: `scripts/lumos:81740` 與三份手冊的日期寫法
失敗場景:有兩處精度問題。
- `--help` 說明沒寫「要跟 `--loop` 一起給」,也沒寫生效日;新增的擋下就是這條規則。
- 「目前 2026-11-22」手寫進 `skills/lumos-code-loop/SKILL.md`、`skills/lumos-code-loop/reference.md`、`skills/lumos-project-notes/commands/06-代碼審與推送.md` 三處。測試裡沒有任何一處核對它與 `_FINDING_SEAT_SINCE` 一致。生效日一改,只靠〈回退〉那句人工提醒;改漏了,擋下訊息(用常數)和手冊就會說不同的日期。
引句:「`--finding-seat` 是生效日(`_FINDING_SEAT_SINCE`,目前 2026-11-22)起新開的代碼審迴圈必帶」
歸因:未判定。日期同步是修補新加的文字,`--help` 缺漏則兩版都有。
兩版查證:`grep -rn '2026-11-22' scripts/test_lumos.py` 兩版皆無結果。

## 固定席圖譜鏡頭

派工附註寫明這次沒附固定席節點(鏡頭計算超時),所以我沒有逐條判定可對照的固定席筆記。我只能就修補內容判斷:

- `Systems/loop-convergence-recording` 的新文字與程式一致。尾碼開頭的 `r2-`、中文角色尾巴的 `r2`/`2` 被去掉,以及 repr 席名和事件去空白,都有對上程式行為。
- 我沒有看到 `Systems/canary-audit` 在 r2 修補裡被改動。這部分標為未判定。

## 三問

1. **原問題的修復效果有何行為證據?** G3(沒帶 `--loop`)、G5(壞時間事件與脫困句)、G1(席名正規化)我獨立跑過,結果都符合預期。G1 還用 795 個真帳席名對過。G2、G4、G6、G7 的修復只有既有測試通過,我沒有獨立重現。
2. **修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 成立。`code` 開頭無連字號的迴圈照舊從嚴。設計審不必填。生效日前的迴圈不受影響。我沒有發現修補自己引入的新洞。唯一的相鄰漏洞是壞時間檢查跑在生效日之前(上面第 4 條),修前就在。
3. **新發現的同一案例在修前、修後各是什麼結果?** 5 條都是修前就存在的缺漏,修前修後結果相同,詳見各條的兩版查證。

另有一個小觀察,因為場景不現實所以沒單獨列條:`_seat_noise_name("資安-2-sonnet")` 會輸出 `資安--sonnet`。這種席名不符合 `<鏡頭>-<模型>` 的命名規則,修前的舊正則也會得到同樣結果。

最嚴重等級 minor
