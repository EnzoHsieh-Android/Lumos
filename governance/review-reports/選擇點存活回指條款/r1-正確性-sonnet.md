severity: major

先講結論:這份設計有 6 條 major(1–6)與 4 條 minor(7–10)。最重要的一條是 1:處置途中補任何一支測試或條款,所有已記的層判讀就全部作廢,「補到殺掉才算處置完」那條流程要重判 O(n²) 次。

## 逐節結論

- 〈白話〉〈用詞〉:見 finding 1、2、3、7、8。
- 〈範圍〉1–7:見 finding 4、5、7、8、9。
- 〈範圍〉8、9、10:見 finding 1、4、5、7。
- 〈範圍〉11:見 finding 2、3、10。
- 〈舊否決比對〉〈不做〉〈回退〉〈天花板〉〈依據來源〉:已讀,無 finding。文件內交叉引用(`[[Projects/…]]`、範圍編號、S 編號)的目標都存在,`--point`、`--clause`、`--plan`、`--test` 旗標也都有。
- 〈驗收條款〉〈預期值表〉:S13 與〈用詞〉不一致,見 finding 7。其餘已讀,無 finding。
- 〈實務隱患〉:見最後的「實務隱患鏡頭」。

## Findings

**1. 層與 reach 的新鮮度鍵是全域雜湊,處置途中補一支測試或條款,所有已記判讀全部作廢**

引句:「`tests_sha` 與 `spec_sha` 都等於現在的才算對得上;計劃改了就要重判」

severity: major
blocking: 是

- `_choice_tests_sha(guard["tests"], blobs)` 是全部守衛測試名加所在檔 blob 的單一雜湊(`scripts/lumos:78773`),不分行。
- 輸入:62 個存活、已記好層,人照第 3 層補了一支測試。`tests_sha` 變了,其餘 61 筆層事件與 reach 事件全部對不上,輸出退成「未判讀」。
- 照第 2 層補子條款或照第 1 層用 `situation-rule` 寫回,會改計劃檔,`spec_sha` 同樣全變。
- 〈WHY〉要求第 2、3 層「補到壞法被殺掉才算處置完」,所以每處置一條就要重判其餘全部,總共 O(n²) 次代理判讀。
- 〈回退〉說「計劃改了要能重判」,但沒有任何降低重判量的辦法,例如只比該存活用到的條款與測試的雜湊。
- 順帶:現行 `_choice_kill_pick` 在 `tests_sha` 變後會重跑所有 survived(`scripts/lumos:79092`),reach 與 layer 的重算成本疊上去。

**2. 換候選的每次嘗試都記一筆壞法事件,會讓 stats、rc 與治理帳統計錯誤**

引句:「每次都記一筆既有的壞法事件;`attempt` 是那一行在帳上的累計筆數」

severity: major
blocking: 是

- `_ChoiceKillRun.finish` 對每個判定都做 `self.stats[verdict] += 1`,並寫帳(`scripts/lumos:79243-79250`)。
- `_choice_kill_report` 靠 `st["no_result"]` 決定 rc:`return 2 if (nores or …)`(`scripts/lumos:79354`、`79363`)。
- 輸入:某行第 1 個候選編不過、第 2 個被殺掉。照 spec 記一筆 no_result 事件再記一筆 killed 事件。
- 結果一:`st["no_result"]=1`,choice-kill 收尾 rc 2,印「跑不出結果 1」。這與 S17「換到能編譯的就照常判」和〈白話〉「不留成跑不出結果」矛盾。
- 結果二:`_gov_choice_count_verdict` 只算 `attempt==1 and via=="run"` 的 `first`(`scripts/lumos:17961`)。編不過那筆佔走 attempt 1,真正的判定成了 attempt 2,「第一次跑的判定」分布被扭曲。
- 結果三:`c["nores"]` 的原因分布會多出「壞法編不過」的中間筆。
- 〈範圍〉5 說 gov 統計會加「編譯不過換候選幾次」,但沒說這些中間 no_result 要從現有計數排除。

**3. 換候選的實作面對不上現有結構,spec 沒交代怎麼接**

引句:「`_choice_pick` 現在只回第一個產得出來的候選,要加一個「排除這些壞法身分」的參數,不唯一的候選照舊跳過」

severity: major
blocking: 是

四個缺口,都從現有程式驗得出來:

- **「照舊跳過」與程式不符。** `_choice_pick` 不跳過不唯一的候選。`_choice_identity` 回 None 時照樣把壞法 dict(identity 為 None)返回,上層標成 `not_unique`(`scripts/lumos:78460-78464`、`78551-78553`)。
  - 照字面「跳過」會改變 `not_unique` 行的分類。
  - 照「排除壞法身分」參數,identity 為 None 的候選又沒有身分可排除。
- **`plan_of` 以 `file:line` 為鍵,`finish` 開頭有 `if p["done"]: return`(`scripts/lumos:79216`、`79233`)。** 同一行的第 2 個候選不重建 `plan_of` 條目,會被當成已判完而丟棄。
- **配方身分 `_kill_recipe_key` 只雜湊 `(node, invariant, file, old)`,不含 `new`。** 候選 1 與候選 2 的 `old` 相同(同行),配方 id 相同,`rid_map` 會撞號。
- **`run()` 只呼叫一次 `cmd_guard_kill`,且 `_choice_compute` 只留下挑中的那個壞法。** 重新取得該行的 nodes 與 `line_of`、`ctx`,必須在一次 guard-kill 呼叫結束後再開第二次呼叫。這一整段設計 spec 沒寫,時限也沒說明在批次呼叫與重試之間怎麼分。

**4. 第 2、3 層「引句要對得到計劃原文」的機械驗證沒有最短長度,擋不住憑印象編依據**

引句:「第 3 層:`basis` 至少一筆 `where` 是那份計劃裡存在的條款號,`quote` 是那條條款原文的子字串」

severity: major
blocking: 是

- 〈實務隱患〉把引句驗證列為「判讀把該問人的歸成第 2、3 層」這個最貴的錯的第二道擋。
- 輸入:第 3 層,`where: S3`,`quote: "的"`(或空白、任一常見字)。是 S3 原文子字串,通過驗證。
- 第 2 層也有同樣的洞:任一罕見單字若不出現在任何條款,就是正文子字串、不是條款子字串,同樣通過。
- 第 1 層與第 4 層沒有任何依據驗證。這與「拿不準歸第 1 層」的偏向互補,但第 2、3 層的機械驗證等於形同虛設。
- 缺的是:引句最短實字數(例如沿用實字數函式),或引句必須涵蓋改壞行為相關的詞。spec 兩個都沒要求。

**5. `spec_sha` 的「碰到的計劃」集合隨範圍與版本變動,層事件會靜默失效**

引句:「`spec_sha`(碰到的計劃檔內容雜湊,依路徑排序後串起來算)」

severity: major
blocking: 是

- 〈用詞〉對得上說:choice-kill、choice-points、choice-layer 讀「範圍終點」,推送閘讀被推的 B 版。
- 「碰到的計劃」是 `_choice_spec_calc(rr, rng, at_sha)` 對範圍算出的進行中計劃集合。判讀時用的 `--diff` 範圍與推送閘的分岔點起範圍(`_choice_push_range` 回 `start..tip`)可能不同。
- 輸入:判讀範圍只碰到計劃 P,推送範圍多含一個碰到計劃 Q 的提交(或反過來少)。
- 計劃集合不同,`spec_sha` 就不同,所有層事件在推送閘判成「不一致」,提示退回覆蓋分類與「未判讀」,而人不知道為什麼。
- 同一次 push 裡任何無關的提交碰到另一份進行中計劃,也會讓全部層事件作廢。spec 沒有對這一點的處理,也沒有測試。

**6. p1 的判定:編不過的最終去向,spec 的白話、WHY 與範圍 11 互相矛盾**

引句:「3 個都編不過記 `no_result`,原因「壞法都編不過(試了 3 個)」」

severity: major
blocking: 是

- 矛盾兩處:
  - 〈白話〉與 WHY 寫「不留成跑不出結果」「不選:記成跑不出結果交人處置」。
  - 〈範圍〉11 卻在 3 個都編不過或沒有候選時記 no_result。
  - 〈用詞〉「第 4 層只有編譯不過是工具自己判的」,但工具不寫層事件。
- 實際效果:`_choice_disposition` 對 no_result 回 `"no_result"`,推送閘判為擋下,修法是「修好後重跑」(`scripts/lumos:79587`、`78813`)。這正是 WHY 要避免的「讓人去查一個不存在的問題」。
- 我建議的方向:承認這個終態,不要偷偷記成 no_result 又在文字上否認。
  - 在 `_choice_kill_judge` 之外新增終態(例如 `verdict: "no_mutant"`,與 `not_unique` 同層級)。
  - 推送閘與 `_choice_disposition` 把它當有效處置,不擋;或至少給出專屬提示:`lint-waive choice:<檔>:<行> --note "不適用:全部候選編不過"`。
  - 把「第 4 層只有編譯不過是工具自己判的」那句改成「編譯不過耗盡候選時工具記終態」。
- 若要保持「不改擋的判定規則」,就改〈白話〉與 WHY,承認會記 no_result,並給專屬的放行提示。判斷題,交編排者裁。

**7. S13 與〈用詞〉對「附全部條款」的條件不一致;clause-unsplit 與 unknown 的提示句沒定義**

引句:「覆蓋 `none` 或沒有 reach 事件的存活 應 附那份計劃的全部條款」

severity: minor
blocking: 否

- 〈用詞〉判讀材料寫的是「`none`/`clause-unsplit`/`unknown` 時附碰到的計劃的全部條款」,S13 只測 `none` 與沒有 reach 事件。`clause-unsplit` 與 `unknown` 的行為沒有驗收條款守住。
- 〈範圍〉6 末行「經過條款的照原句指向那條」沒說 `clause-unsplit`(沒有具體條款)與 `unknown` 要印什麼提示。

**8. 覆蓋階段只在「這次有存活」時跑,沒寫沿用舊帳的存活算不算**

引句:「只在這次有存活、而且平台有覆蓋設定時跑;`--no-reach` 關掉。」

severity: minor
blocking: 否

- `_choice_kill_pick` 把守的測試沒變的 survived 放進 `carried`、不重跑。
- 輸入:這次所有存活都是 `carried` 的舊存活,且沒有對得上的 reach 事件。「這次有存活」若指新判出的,不會跑覆蓋,使用者得自己知道改跑 `--reach-only`。
- 〈範圍〉7 的 `--reach-only` 是補洞用法,但 spec 沒有在覆蓋階段條件裡說明 `carried` 是否算。

**9. 報告安全檢查的描述有歧義,`reach_why` 字串表有缺口**

引句:「有 `[` 內部子集或 `<!ENTITY` 就整份不收(記不明),不解析外部 DTD。」

severity: minor
blocking: 否

- JaCoCo 報告裡有 `<method desc="([Ljava/lang/String;)V">` 這種陣列描述,整份檔案會含 `[`。若實作成掃整份檔,所有報告都會被拒。spec 沒寫明這個檢查只對 `<!DOCTYPE …>` 宣告本身。
- 「報告開頭有 DOCTYPE」:實際報告開頭是 `<?xml …?>` 宣告,DOCTYPE 在第二行。
- `reach_why` 表缺:XML 解析失敗、DOCTYPE 不是那一種(非內部子集的別種外部宣告)、報告讀不了。而〈範圍〉4 規定 `reach_why` 只用表內字串。

**10. 換候選對重跑成本的影響,與 p2 的判定**

引句:「一行最多試 3 個;`_choice_pick` 現在只回第一個產得出來的候選」

severity: minor
blocking: 否

這是 p2 的 finding,判定如下:

- 現況確認:`scripts/lumos:79077` 寫明 no_result 一律重跑,spec 沒有放寬。
- 換光候選的行因此每次 choice-kill 都白跑 3 次編譯。這個失敗只取決於該行與被測程式,不取決於測試,但現行 carry 鍵是 `tests_sha`,不適用。
- 我建議的方向:對原因為「壞法都編不過」「沒有能編譯的候選」的 no_result,用「該行的 fp 加該檔 blob」當 carry 鍵;鍵不變就不重跑,印「上次已試過全部候選」。這與 finding 6 的終態合併處理最自然。
- 這會動到 `_choice_kill_pick`,與〈不做〉「不改擋的判定規則」要一併改寫措辭。判斷題,交編排者裁。

## 固定席節點判定

- `Systems/guard-kill` INVARIANT「rc 優先序」(`t_guard_kill_rc_precedence`):**不影響**。spec 沒動 `cmd_guard_kill` 的判定。換候選是 choice-kill 自己再呼叫一次 `cmd_guard_kill`,rc 優先序仍由它自己決定。
- `Systems/guard-kill` INVARIANT「`--json` 成功跑完 stdout 恰一行 JSON」(`t_guard_kill_json_purity`):**不影響**。choice-kill 呼叫時把 stdout 導向 `StringIO`(`scripts/lumos:79305`),覆蓋階段另走自己的指令。
- `Systems/規格閘`:**不影響**。推送閘提示只換句,不動擋不擋的判定。但 finding 5 的 `spec_sha` 會讓層提示在推送閘退回覆蓋分類。

## 實務隱患鏡頭

- 併發與交易:**無**。spec 已排除,單人依序操作。但 `--reach-only` 與 choice-kill 同時寫治理帳的順序,沿用既有追加寫法,未見新風險。
- 金流:**無**。只讀測試覆蓋。
- 對外送出:**無**。覆蓋在本機跑。
- 不可逆:**無**。治理帳只追加,同鍵取最新一筆。
- 資安/外部輸入:報告 XML 解析是唯一外部輸入。有大小上限與 DOCTYPE 限制。隱患是 finding 9 的歧義,不是漏洞。
- 資源/效能:覆蓋階段每群一次 Gradle,有時限預估與聯集退路。換候選最壞每行多 2 次編譯,且 no_result 每次重跑(finding 10)。判讀材料有 200KB 與 20 個存活上限。
- 守衛面:**有**。finding 1 與 5 說明層事件新鮮度鍵過粗,實際會讓層分類在處置途中大量失效。

總結:最高等級是 major,blocking 共 6 條
