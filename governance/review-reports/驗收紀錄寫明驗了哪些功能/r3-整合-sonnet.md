severity: minor

# 第 3 輪整合與接手審查(整合席,sonnet)

做法:把〈做法〉1–7 與 S1–S12 當實作單,在 `git clone --shared` 出來的臨時目錄(scratchpad/vr3-int)對真碼原型一次:抽出單項判法、加 `_verification_status`、`LIST_KEYS` 加 `system_refs`,再跑既有測試與手造 vault。沒有改 repo 任何檔。前兩輪的 blocking(索引行為不變、空鍵與空清單、孤兒連鎖、同步清單)在真碼上都接得起來,本輪沒有新的 blocking。

## F1 單項判法的回傳內容沒定死,照字面抽可能讓「行為不變」(S5)破功
severity: minor
blocking: 否
引句:「從 `build_typed_index` 裡判單項的那段原樣抽出,`build_typed_index` 改呼叫它、行為不變」
file: `scripts/lumos:757-784`(`build_typed_index` 內迴圈)
1. 計劃只寫「合格(落點 rel)或四種不合格」。但現行迴圈的去重鍵是 `(rel, t, etype)`,`t` 是解析前的連結字面(已 nfc、去別名與 `#段落`),ghost 與 ambiguous 兩份清單也靠這個字面去重、且記的是字面不是落點;ambiguous 還要帶排序後的候選清單。
2. 具體例:同一欄位寫 `[[Verification/V1]]` 與 `[[V1]]`(兩個字面、同一落點)。現行索引的反向表會記兩筆;若實作者只拿到「落點 rel」就改用落點去重,反向表變一筆,S5 說的四份清單就跟原本不一樣。同理兩個相同的 `[[Ghost]]` 現行只記一筆 ghost。
3. 我在臨時目錄把函式寫成回 `(種類, (字面, 落點或候選))` 後,`-k typed_index`(7 個)、`-k check3`(5)、`-k check_e1`(3)、`-k sync_verified`(4)、`-k doctor_suggest`(8)、`-k e2`(35)全綠;`build_typed_index` 的其他呼叫端(E2、關聯連鎖、drift、impact、graph 輸出)都只讀回傳的五個鍵,所以抽出本身安全。現有 `t_typed_index_contracts` 沒蓋到「同落點不同字面」與「重複 ghost」,建議 `t_typed_link_target_unchanged` 明寫這兩例,並在〈做法〉1 寫明回傳要帶字面。

## F2 清單項解出空字面時被索引的舊規則默默丟掉,跟「寫壞一律報出來」衝突
severity: minor
blocking: 否
引句:「寫壞了一律報出來、不默默當成沒驗」
file: `scripts/lumos:765-772`、`scripts/lumos:774-775`
1. 現行索引對「去空白後是空字串」與「連結去掉別名、`#段落` 後是空字串」直接 `continue`,不進任何一份清單。〈做法〉1 說抽出的不合格只有四種,沒有這第五種。
2. 實測(臨時目錄,`system_refs` 為 `- "[[Systems/Alpha]]"` / `- "[[#x]]"` / `- ""` / `- "[[ ]]"`):索引的 scalars、ghosts 兩份都是空的,三個壞項完全無聲。若 `system_refs` 只有這類項,會落到 S3 的「讀不出任何一項」,沒問題;但跟一個合格項混寫時,壞項被吞、doctor 3/4 沒有任何輸出,等於默默放行。
3. 建議〈做法〉1 補第五種「連結內容為空」,在 `system_refs` 路徑報壞,索引那邊維持原樣(對索引呼叫端行為不變);S4 補一例。

## F3 `new verification --systems` 要「照檔案的大小寫」,但沒講怎麼拿到真實路徑,且有平台差異
severity: minor
blocking: 否
引句:「用 `env.notes` 裡那篇的真實路徑(檔名大小寫照檔案)寫進新紀錄自己的 `system_refs`」
file: `scripts/lumos:19143-19148`(存在檢查用 `(env.vault / rel).exists()`)
1. 實測在 macOS(預設不分大小寫的檔案系統):`new verification VV --systems Systems/alpha`(實際檔名 `Systems/Alpha.md`)通過存在檢查,`verified_by` 寫進去了,但 `env.notes` 是以精確字串為鍵,沒有 `Systems/alpha.md`——所謂「env.notes 裡那篇」查不到,計劃沒定義怎麼從使用者打的字找回真實路徑(要不分大小寫掃 `env.notes`?還是改存在檢查?)。
2. 在 Linux(CI)同一個輸入會在存在檢查就被擋下 rc2,S8 若用大小寫不同的輸入當測試,本機綠、CI 紅(或反過來)。
3. 建議〈做法〉5 寫明:用 `env.notes` 不分大小寫比對一次、比出唯一一篇才用它的鍵,比不到就維持現行行為並不寫 `system_refs`;S8 的測試不要依賴檔案系統是否分大小寫。

## F4 同步清單第 7 點:該改的錨點大多存在,但「其他段落」沒點名,真正會互相矛盾的段落沒列
severity: minor
blocking: 否
引句:「`scripts/lumos` 裡 `append`、`new --systems`、`sync-verified-by` 的說明字串」
file: `skills/lumos-project-notes/reference.md:798`、`:950`、`:987`、`:885`;`scripts/lumos:15877`;`docs/lumos-toolchain-knowledge/Systems/lumos-cli-write.md:93`
1. 逐項核對:`commands/03-寫回圖譜.md` 第 7、19 行、`SKILL.md` 第 71 行、`reference.md` 第 63(健康巡檢列)、97(list 追加列)、591-596(補 verified_by 漏寫)、827(plan_refs 欄位節)行,以及兩篇 Systems 的 doctor 與 new verification 段都在;精簡版 `slim/` 確實有 `verified_by` 與 `append` 的說明,凍結不同步合理。
2. 「其他提到『Verification 連到 Systems 即視為驗證』的段落」這句字面在文件裡搜不到;唯一逐字出現的是程式字串 `scripts/lumos:15877`(dry-run 說明),計劃只寫「補一句」,但那句對有宣告的紀錄本身就不對,應整句改寫成兩種判準。
3. 真正會跟新行為打架的是 `reference.md` 第 798、950、987 行(「Verification 的『## 相關模組』列了幾個 Systems,就要更新幾個」):`new verification --systems` 之後每份新紀錄都會寫 `system_refs`、變成「宣告」,之後在正文「相關模組」多連的 Systems 不再被要求反向登記、sync 也不補。這是〈實務隱患〉已承認的「漏網」代價,但文件那條慣例沒同步改成「同時寫進 `system_refs`」,實作者會照舊慣例寫、被宣告制默默吃掉。建議清單把這幾行點名。
4. `lumos-cli-write.md:93` 寫「2026-08-24 為 8 項」,現行 `LIST_KEYS` 已是 9 項、加了之後 10 項,順手訂正。

## F5 封頂 20 項與 `warn` 的計數方式沒對上
severity: minor
blocking: 否
引句:「(`warn`,算 issue,照 doctor 4/4 對 `plan_refs` 斷鏈自己報的先例;最多印 20 項」
file: `scripts/lumos:1361-1373`(`warn` 以 `issues += len(lines)` 計數)
1. `warn(lines, head, advice)` 把傳進去的行數全算成 issue。若實作者把「另 N 項」那行也塞進 `lines`,issue 數變成 21 而不是 N;若只傳 20 項再另行印一行,issue 數變成 20 而不是 N。S12 只驗印出幾行,沒驗問題數。
2. 建議〈做法〉3 寫明問題數算 N(全部寫壞項)還是印出的行數,並在 S12 加一句。

## F6 作廢/失效「不分大小寫」只改四處,其餘讀 status 的地方仍分大小寫
severity: minor
blocking: 否
引句:「應照各自原本的規則處理,不因大小寫判成不同」
file: `scripts/lumos:16400`(`lumos stale` 清單用 `== "stale"`)、`scripts/lumos:14586`、`:1770`、`:1826`、`:2409`
1. 一份 `status: Superseded` 的紀錄會被 doctor 3/4、E1、sync、孤兒清單當作廢,卻在 `lumos stale` 清單與「作廢才跳過」的其他關卡(14586 等)被當有效,同一篇筆記兩套判法。計劃〈相容〉已講「本 repo 實查沒有這種寫法」,風險低,但 S10 的措辭「不因大小寫判成不同」讀起來是全面保證。
2. 建議 S10 加一句範圍「僅這四處」,並在〈範圍〉不做裡補一句其餘讀 status 的地方不動。

## F7 孤兒推薦對有宣告的紀錄,理由字串與建議動作文字沒定
severity: minor
blocking: 否
引句:「共用函式回宣告且有合格項時,只推它列的功能;回 None 或沒宣告,照原本的推薦」
file: `scripts/lumos:805-835`、`scripts/lumos:1431-1432`
1. 現行推薦理由寫死「本篇正文連向(verified_by 未同步 → 可 sync-verified-by)」,收尾建議也只講「本篇正文連向」。宣告制下推的是 `system_refs` 列的項,理由字串要換成「本篇 system_refs 列了它」,否則人看到「正文連向」會去找不存在的正文連結。S11 只驗推了誰,沒驗理由。

## 看過沒問題的(不是 finding)
- 抽 `_typed_link_target` 後的索引呼叫端:`build_typed_index` 在 doctor E2、關聯連鎖、drift 一批函式、impact、graph 輸出共約 10 個呼叫端,都只讀回傳的 `rev/fwd/ghosts/ambiguous/scalars` 五個鍵;原型版回傳同鍵、同形狀,相關既有測試無一翻紅。
- `_verification_status` 改 E1:E1 的 `vst` 取自被引用的任何筆記,改成去空白、轉小寫後,既有 `t_check_e1_dead_endorsement`、`t_check3_skips_stale_verification` 全綠(測試用的都是小寫 status);訊息裡 `status=` 會變成小寫,但現有測試只比小寫寫法。
- 解析行為與計劃假設一致(實測 `_note_from_text`):`system_refs:` 空值、`[]`、清單項沒縮排都解成空清單;`""` 解成空字串;區塊寫法進 `block_keys` 且不進 `n.targets`;純量單一連結 `system_refs: [[Systems/A]]` 解成單一字串、能過單項判法;`null`、`~`、多連結純量、`[[[…]]]` 都落到「不是單一連結」。S3、S4 的分類落得下去。
- 登記:`LIST_KEYS` 加 `system_refs` 後,`append` 白名單接受、lint 不唸欄位名(`cmd_lint` 在執行期併入 `LIST_KEYS`,不必另改 `_KNOWN_FRONTMATTER_KEYS`);`append` 不驗值,寫入純文字或不存在的連結也成功,doctor 3/4 才是把關處,符合計劃。`LINK_KEYS` 不加,`delguard` 子集守衛(`LINK_KEYS ⊆ LIST_KEYS`)不受影響。
- 測試名在 `scripts/test_lumos.py` 都還不存在,屬預先宣告,與「實作時新增」一致;`-k append`、`-k delguard` 等較大的子集我只跑到一半(逾時轉背景),沒有看到失敗,但不能算完整確認。

最高等級:minor,blocking 共 0 條
