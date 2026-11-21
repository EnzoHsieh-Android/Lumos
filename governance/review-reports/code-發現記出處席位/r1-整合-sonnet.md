severity: major

## 發現

**F1**
severity: major
blocking: 是
file: `skills/lumos-code-loop/reference.md:133`(載體席記帳範本,到 141 行)、`:196`(逐條放行範例,到 206 行)、`:613`(舊版步驟 6)。這份 diff 沒碰 reference.md。
引句:「**載體必帶 `--finding-seat <id>=<席名>`**(2026-11-22 起新開的代碼審迴圈;生效前開的照舊可不帶)」
具體失敗場景:SKILL.md 第 6 步只叫人另外去看新旗標。但 SKILL.md 與 06 命令速查(`commands/06-代碼審與推送.md`)都指向 `reference.md` 作為載體席的詳細範本,而這份範本沒更新。三個月後接手的人照 `reference.md:133` 那段「載體席」範本記帳,會得到:

- 範本:`--findings-set … --folded-set … --accepted-set … --refuted-set <id=理由,…|none>`,沒有 `--finding-seat`。
- 走到 `cmd_canary` 呼叫 `_finding_seat_write_block` 的那一行(新增的 `_fsb = …`),進 `_finding_seat_required_block`。生效日(2026-11-22)後新開的代碼審迴圈,在這裡回 rc 2、不寫帳。
- 在 `reference.md` 的範例旁(196-206)也看不到「載體最後記、席名必須先入帳」的說明。

因為 `loop next` 的 `disposal_cmd` 範本有帶旗標,走範本的人不會踩到。只有照 reference 手抄的人會踩到。擋下訊息有給寫法,所以能脫困,但這就是文件不一致:照文件做會被擋。

重現(文件面):`grep -c "finding-seat" skills/lumos-code-loop/reference.md` 回 0,而計劃 S12 與 SKILL 都宣稱手冊已涵蓋。

**F2**
severity: minor
blocking: 否
file: `skills/lumos-design-loop/templates.md:30`、`:81`、`:148`、`:338`、`:359`、`:446`(各派工詞開頭的 `LUMOS-SEAT: {loop}/{rN}/{席名}`);diff 沒碰這個檔。
引句:「派工與記帳的席名一律不帶輪次(寫 `正確性-sonnet`,不寫 `正確性r2-sonnet`),逐席沒用率才不會拆成好幾列」
具體失敗場景:計劃〈做法〉統計寫「派工詞與手冊另寫明席名不帶輪次」。但派工詞範本 `templates.md` 完全沒改,`{席名}` 沒有任何「不帶輪次、載體最後記、席名要等於 `--auditor`」的說明。派工的人不會讀到這條規則。統計雖會併回輪次記號,但 `鏡頭1-正確性-sonnet`、`正確性A-sonnet` 這類寫法會碎片化。計劃自己承認這個隱患(〈席名碎片〉),而收斂手段只剩 SKILL 的一句話。

**F3**
severity: minor
blocking: 否
file: `scripts/lumos`,`_finding_seat_required_block` 的擋下訊息(diff 第 459 行附近)。
引句:「擋下:代碼審載體要帶 --finding-seat:每條發現(含 --refuted-set 那幾條)各標是哪一席報的,」
具體失敗場景:消費專案第一次被擋,拿到的資訊是:
- 缺的 id 清單。
- 寫法 `--finding-seat c1=<那一席的 --auditor>`。

訊息沒講三件事:
- 席名必須是這一輪已入帳的席,所以載體要最後記。這點要等到第二道 `finding-seat-unknown` 擋下才說。
- 這條規則只管生效日(2026-11-22)後新開的迴圈。
- 訊息指向 `Projects/代碼審發現記出處席位_計劃`,這個節點只存在於工具鏈本 repo,消費專案查不到。

我沒有找到會卡死的路徑,因為第二道擋下訊息有指路,所以只標 minor。

**F4**
severity: minor
blocking: 否
file: `scripts/lumos`,`_loop_next_hints`(`scripts/lumos:24875`,到 24893 行);diff 只改了範本字串,沒改這個函式。
引句:「if _roster_kind(str(loop_id)) != "design":   # 代碼審發現記出處席位_計劃 範圍⑤:設計審不必填、不印」
具體失敗場景:範本印出 `--finding-seat <id=席名>`,但 `loop next` 的「記帳順序」提示只在 `eff_tier == "high"` 才印,而且只講「載體最後記」跟 `--finding-source` 的關係。standard 代碼審的 `loop next` 沒有任何說明為什麼席名要先入帳。編排者照範本一次填完、先記載體,就會被 `finding-seat-unknown` 擋一次。

**F5**
severity: minor
blocking: 否
file: `skills/lumos-code-loop/SKILL.md:60`、`commands/06-代碼審與推送.md:55`。
引句:「**載體必帶 `--finding-seat <id>=<席名>`**(2026-11-22 起新開的代碼審迴圈;生效前開的照舊可不帶)」
具體失敗場景:生效日在兩份手冊裡寫死成字面日期,常數 `_FINDING_SEAT_SINCE` 才是真相。計劃〈回退〉只講改常數,沒講要同步改手冊。若合併日期延後或回退改成 9999,這兩處還是會說「2026-11-22 起必填」。照文件做的人會多帶旗標,影響不大。

## 固定席

這次沒附固定席節點(LUMOS-LENS 說鏡頭計算超時),所以沒有節點要逐條判。我另外自己比對了兩份既有筆記:

- `Systems/canary-audit` 的 d4 與新 d6:d6 只豁免逐席沒用率,d4 其餘照舊有效。節點第 31 行的 KEY 與第 76 行摘要仍寫「否決跨期統計/席位信譽」。這些行沒有指向 d6,但字面上不衝突,判不破壞。
- `Systems/loop-convergence-recording`:新增段落跟程式的行為(56 天窗口、同 (迴圈, 輪) 取最後一筆、席名只去輪次記號)逐項一致。「載體最後記」的既有段落只講 `--finding-source`,新段落已在自己那一段補上席名這一層,判不破壞。

## 總結
最嚴重等級 major,blocking 1 條(F1)。
(總結句由該席 2026-11-21 續談時改寫:原句會被收貨工具當成第二個嚴重度宣告)
