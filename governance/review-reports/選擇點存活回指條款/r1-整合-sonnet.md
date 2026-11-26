severity: major

**固定席節點判讀**
- `Systems/guard-kill` 的 `t_guard_kill_rc_precedence`:不影響。spec 範圍 2 的覆蓋階段不呼叫 `cmd_guard_kill`,換候選(範圍 11)走 choice-kill 自己的迴圈。
- `Systems/guard-kill` 的 `t_guard_kill_json_purity`:不影響。新增輸出都在 choice-kill 與 choice-points 的文字輸出,不碰 `--json`。
- `Systems/規格閘`:無合約條款,不影響。但推送閘提示的結構會被牽連,見 finding 6。

---

1. 〈範圍〉1 的 `coverage` 設定沒有路徑讀進來。
   - 照字面實作會讀不到設定。
   - `load_platforms` 只回傳 `profile`、`root`、`profile_name`、`run_cmd` 四欄,不帶 `coverage`:`scripts/lumos:6409`、`scripts/lumos:6455-6456`。
   - 單平台(legacy)的設定在 `cfg["test"]` 底下,不在「平台那一節」:`scripts/lumos:6436-6441`。
   - 〈用詞〉說「平台是這次 choice-kill 用的那個平台」,但守的測試可跨多個 kotlin-junit 平台:`scripts/lumos:79152-79157`。
   - spec 沒寫 `coverage` 放哪、怎麼穿過 `load_platforms`,也沒寫多平台時每個平台各自的 `run`/`xml` 怎麼對應。

引句:「平台設定(`.lumos/config.json` 的平台那一節)多一個選填的 `coverage` 物件:」
severity: major
blocking: 是

2. 〈範圍〉11 的換候選會讓下游三條路徑對不到「存活的是哪個候選」。
   - 事件只記 `new_sha` 與 `candidate`,沒有壞法文字。
   - `_situation_rule_point_target` 重新掃描,用 `_choice_pick` 取第一個候選(`scripts/lumos:79865-79871`)。這個第一個候選正是編不過的那個。`situation-rule --point` 的殺傷力驗證必定拿不到 killed,第 1 層的唯一處置路徑會卡死。
   - 範圍 9 判讀材料的「壞法的改動」同樣重算,會印成編不過的那個壞法。
   - `choice-points` 與推送前的掃描也只認第一個候選。
   - spec 只說 `_choice_pick` 要加「排除這些壞法身分」參數,沒規定上述三處怎麼還原第 N 個候選。
   - 候選 2 也沒跟 `_ChoiceKillRun` 對上。`plan_of`、`merge.survived`、`judged` 都以 `loc` 為鍵,且只對候選 1 跑過合併快篩(`scripts/lumos:79200-79245`)。spec 沒說候選 2 的 `judged`、`merge_kind` 怎麼記。

引句:「`_choice_pick` 現在只回第一個產得出來的候選,要加一個「排除這些壞法身分」的參數,不唯一的候選照舊跳過。」
severity: major
blocking: 是

3. 〈範圍〉11 違反母計劃的「一行一個壞法」,舊否決比對沒列。
   - `Projects/改動選擇點都要有需求守住_計劃.md` 〈不做〉(行 143)寫「不接覆蓋率」,天花板 4(行 335)與路線總圖 REVISIT(2026-12-31)都把「同一行換下一個候選壞法」當成待評估的事。
   - 範圍 11 讓一行最多跑 3 個壞法,而〈舊否決比對〉只列了四條,沒列這兩處。
   - 〈不做〉卻寫「不改……擋的判定規則……換候選改變的是結果分布」。
   - 這會改變 `gov --stats` 裡 RETIRE-IF 用的「第一次判定」分母,見 finding 4。

引句:「`--max-mutants` 是跑前切行數,只數行,換候選不另佔名額;換候選的時間算進 `--max-seconds`。」
severity: major
blocking: 是

4. `gov --stats` 的欄位白名單漏列 `candidate`,「第一次判定」統計也沒跟著改。
   - 範圍 5 只說要補 reach 與 layer 的欄位,但〈範圍〉5 又要求印「編譯不過換候選幾次」。
   - `ck` 白名單(`scripts/lumos:18560`)與 `_gov_choice_count_verdict` 只認 `attempt == 1` 算第一次(`scripts/lumos:17943-17965`)。
   - 換候選後,候選 2 的 `attempt` 是 2,不再算第一次,且中間的編不過事件會灌進 `nores` 與 `row_mut`。
   - spec 沒說這些統計要改用 `candidate`。
   - 另外,「四層各幾筆」與「覆蓋四類各幾筆」要不要套「對得上」(`tests_sha`/`spec_sha` 等於現在)也沒定義。`gov --stats` 讀的是帳,拿不到「現在」的計劃檔雜湊。

引句:「治理帳讀取的欄位白名單與型別表要補 reach 與 layer 事件的新欄位(現在只帶既有欄位,新欄位會被丟掉)。」
severity: major
blocking: 是

5. layer 事件大小沒設上限,引句可能被治理帳截掉。
   - 帳行超過 4096 位元組時,`_gate_event_fit` 會從清單尾端丟東西:`scripts/lumos:1884-1925`。
   - 層事件帶 `before`、`after`、`question`、`reason` 與 `basis`(多筆引句),spec 沒訂各欄長度上限,也沒指定 `list_key`。
   - 〈範圍〉5 和 S15 要從 `basis` 印第 2 層的「段名與引句」。`basis` 被截後,印不出來,事件也不會標記壞掉。
   - 對照:`_CHOICE_REASON_MAX = 300`(`scripts/lumos:78740`)已是既有的欄位上限做法。

引句:「結果每個存活一筆 `{file, fp, layer, before, after, basis, question, reason}`」
severity: major
blocking: 是

6. 〈範圍〉6 假設的推送閘提示是逐行的,現況是逐原因的一整句。
   - 現在是 `_CHOICE_PUSH_FIX["存活"]` 一句話,套用整組「存活」原因,每組最多列 20 行示例:`scripts/lumos:79457-79470`、`_CHOICE_PUSH_SHOW`。
   - 要依層換句,就得把「存活」這一條拆成每行或每層一條。`_ChoiceBad` 的 `lines` 計數與 `_spec_gate_push_bad_head` 都吃這個形狀。
   - 〈範圍〉6 沒寫怎麼拆。
   - 沒寫 `site="pass"` 預判路徑(讀工作目錄帳、事件未提交)是否也換句。
   - 沒寫層事件和 reach 事件要先提交進 B 版帳才讀得到。現況的「缺紀錄」提示已有這個提醒,新提示沒帶。

引句:「存活要處置時的那幾行提示,依層換一句(沒有層事件時依覆蓋分類,另加一行跑判讀的指令):」
severity: major
blocking: 是

7. `--reach-only` 與「整次 run 那筆」的 `reach_secs`/`reach_groups` 沒對上。
   - `--reach-only` 不跑壞法階段,spec 沒說它會不會寫 kind `run` 的事件。
   - 若寫 `run`,`changed`、`mutant_lines`、`secs` 會灌進 `gov --stats` 的「choice-kill 呼叫 N 次:改動行中位數」(`scripts/lumos:17943-17950`)。
   - 若不寫,`reach_secs` 沒地方放。
   - 中斷(S7)時 `run` 事件是否仍寫、是否帶 `reach_secs`,spec 只說不寫 reach 事件,沒說 `run`。

引句:「整次 run 那筆多 `reach_secs`(覆蓋階段秒數,無條件進位)與 `reach_groups`(跑了幾群)。」
severity: major
blocking: 是

8. S12 的預期與〈白話〉的實測數字對不上。
   - 〈白話〉:批 3 存活 62 條,最小實驗另是「長跑當時 20 個存活行」(2026-11-23)。
   - S12 與預期值表寫「批 3 版本」「20 個存活行」,18 行經過、2 行沒有。
   - 對批 3 跑 `--reach-only` 會是 62 行,預期值不可能對上。S18 的批 3 則是 62。
   - ⚠ 交編排者:20 行那個版本是否與批 3 不同,spec 沒說清。

引句:「當在實驗專案批 3 版本照範圍 1 設好覆蓋後跑 `choice-kill --reach-only`,分類 應 跟 2026-11-23 最小實驗的人工對照一致(18 行經過條款、2 行沒有條款經過)」
severity: major
blocking: 是

9. 實務隱患「新舊帳互讀」描述的機制與現況不符。
   - 現況:`_choice_ledger_index` 已經只收 gate 與 kind 都是 choice-kill 的事件(`scripts/lumos:78787-78797`)。`_choice_disposition` 不直接讀原始帳。
   - spec 說「現有讀者逐一列出、各補一案」,但全文沒列。
   - 實際讀者至少有:
     - `scripts/lumos:78601`
     - `scripts/lumos:79085`
     - `scripts/lumos:79171`
     - `scripts/lumos:79515-79516`(B 版前篩只認 gate)
     - `scripts/lumos:79581`
     - `scripts/lumos:79612`(blocked 去重)
     - `scripts/lumos:79832`
     - `scripts/lumos:79926`
     - `scripts/lumos:17917`(`gov` 計數)
   - S10 只點名三個,範圍 5 也沒說明哪些讀者要先篩 kind。
   - 回退 2、3 說「篩選要留」,但篩選現在就在共用的 `_choice_ledger_index`,不在各讀者裡。

引句:「`_choice_disposition` 只看同鍵最新一筆,這兩種事件不能被它當成判定;實作時讀者要先篩 kind(現有讀者逐一列出、各補一案)。」
severity: minor
blocking: 否

10. S16 與〈範圍〉6 對第 3 層提示的指令互相矛盾。
    - 〈範圍〉6 第 3 層寫「不用 situation-rule」,只講補測試、綁 `[test:]`。
    - S16 寫「第 3 層的範例指令帶那條條款」。
    - 依 S16 寫測試,實作者會放一條 situation-rule 範例。

引句:「第 3 層的範例指令帶那條條款、第 4 層含 `lint-waive` 的等價放行指令」
severity: minor
blocking: 否

11. S13 與〈範圍〉9 附全部條款的條件比〈用詞〉窄。
    - 〈用詞〉:`none`、`clause-unsplit`、`unknown` 都附全部條款。
    - 〈範圍〉9 與 S13:只有 `none` 或沒有 reach 事件才附。
    - `clause-unsplit` 與 `unknown` 的材料因此沒有測試案例。

引句:「覆蓋 `none` 或沒有 reach 事件的存活 應 附那份計劃的全部條款」
severity: minor
blocking: 否

12. S5 前半的前提進不了 choice-kill。
    - `_choice_kill_base` 在簿記檔以外有未提交改動時直接 rc 2,不執行:`scripts/lumos:79099`、`scripts/lumos:79120`。
    - 「使用者工作目錄有未提交改動時,覆蓋指令在 HEAD 另建樹」這段只能用 `--reach-only` 或直接呼叫覆蓋階段函式測。spec 沒寫 `--reach-only` 的入口是否同樣做乾淨檢查。

引句:「當使用者工作目錄裡存活行所在的檔有未提交改動,覆蓋指令 應 在從 HEAD 另建的樹裡跑」
severity: minor
blocking: 否

13. 「對得上」有兩套定義。
    - 〈用詞〉:事件 `tests_sha` 等於「現在」算出的值。
    - 〈範圍〉5 與 S8:reach 事件 `tests_sha` 等於「存活那筆」。
    - 測試檔被改後存活尚未重跑時兩者會分歧:reach 在 S8 下還算數,在〈用詞〉下不算。
    - `--reach-only` 的「沒有對得上的 reach 事件」用哪套也沒寫。

引句:「同一鍵取最新一筆 reach,而且它的 `tests_sha` 等於存活那筆的才用」
severity: minor
blocking: 否

14. 範圍 3 的同名檔規則與範圍 1 的單一 `xml` 路徑不一致。
    - 範圍 1 只有一個 `xml` 路徑。
    - 範圍 3 卻說「兩個以上模組的報告」同名要記不明。
    - 單一報告檔裡同 package 加檔名重複出現時才可能發生,spec 沒說合併報告或多變體的情況。

引句:「報告裡同一個 package 加檔名出現在兩個以上模組的報告,記不明。」
severity: minor
blocking: 否

15. 部分群組失敗時的混合結果沒定義。
    - 某存活行在群組 A 因「覆蓋指令失敗」記不明,在群組 B 是 `ci=0`,該記 `none` 還是 `unknown`?
    - 預期值表 S3 只寫「只靠那群判的行 unknown」。

引句:「那群視為沒有報告;只靠那群判的行 `unknown`」
severity: minor
blocking: 否

16. 第 3 層條款驗證沒排除 `[manual:]` 與 `[keeps]` 條款。
    - 第 3 層的 `where` 只要求「那份計劃裡存在的條款號」。
    - 但 manual 與 keeps 條款沒有綁測試,提示「補一支測試綁到那一條的 `[test:]`」對它們不成立。
    - 守的測試清單已刻意排除這兩類(`scripts/lumos:78884-78935`),層驗證卻沒對齊。

引句:「第 3 層:`basis` 至少一筆 `where` 是那份計劃裡存在的條款號,`quote` 是那條條款原文的子字串。」
severity: minor
blocking: 否

17. 〈範圍〉8 的文件落點不完整,新子命令的登記沒提。
    - `choice-layer` 要登記子命令說明表(`scripts/lumos:82106` 一帶)與 `commands/INDEX.md`;`gov --stats` 文件落點不在列出的兩篇。
    - 路線總圖 WHY 說第 1 步覆蓋資料同時供 `選擇點變異覆蓋選測試_計劃` 用,但本 spec 只記存活行的分類、不留逐條款覆蓋資料,`related` 也沒連那份計劃。路線 WHY 的宣稱在本 spec 沒有落點。

引句:「[[Systems/guard-kill]] 補一條 WHY(分類用條款群組的覆蓋、不用全部測試的覆蓋;覆蓋只是第一道、層由判讀決定)與搬入 RULE、PITFALL;」
severity: minor
blocking: 否

**實務隱患逐類**
- 併發與交易:spec 已排除。補一點:`--reach-only` 與 choice-kill 同時跑時兩邊各讀「沒有對得上的 reach」可能重複補跑。單人依序操作下無隱患。
- 金流、對外送出、不可逆:無。覆蓋在本機跑,帳只追加。
- 守衛面:有。finding 5、6、9 涉及推送閘提示結構與帳讀者,不是只換文字。
- 效能與記憶體:`xml` 有大小上限,層事件沒有(finding 5)。每個存活事件各帶一份計劃正文的材料,有分份上限(範圍 9),未見其他隱患。
- 其他風險類:已讀,無 finding。

總結:最高等級是 major,blocking 共 8 條。
