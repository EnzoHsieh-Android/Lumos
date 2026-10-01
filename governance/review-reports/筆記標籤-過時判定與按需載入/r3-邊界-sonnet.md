severity: major

固定席筆記:派工詞說「若 hook 有附在尾端」,這次沒有附任何節點,所以沒有逐條判定的對象。

我的鏡頭是邊界與可執行性,替極端輸入發聲。以下證據都是在 rw 副本實際讀碼或跑統計得到的。

---

**R3B1 取行入口漏掉大宗脈絡:只取三種前綴、只取家筆記的摘要行**
severity: major
blocking: 是——照字面實作,改主程式前跑清單只拿得到約兩成脈絡,實作者會做出「看起來查過、其實沒查」的檢查清單。
- 輸入:`lumos search --about scripts/lumos --prefix RULE,PITFALL,WHY`。
- 我在 rw 數了所有管 `scripts/lumos` 的 Systems 節點:共 40 篇,摘要行前綴為 KEY 535、WHY 80、PITFALL 70、DEP 56、TEST 52、FLOW 51、VERIFY 22、RULE 10、FACT 2。
- 這個指令只回 WHY、PITFALL、RULE,共 160 行。其中 RULE 只有 10 行,而只有 RULE 能挑戰程式碼。
- 535 條 KEY 舊行是現有限制的主要載體。spec 〈不做〉與〈不溯及既往〉都說不回頭補標,所以這些行在多年內都拿不到前綴。
- 清單表(WHY/RULE/PITFALL/FACT 四列)沒有 KEY、REVISIT、RETIRE-IF 的對照列,也沒有 ★INVARIANT★ 合約行與 `decisions:` 欄位。
- 事故與坑常寫在 Issue、Verification 節點,不在 Systems 家。但「家」只認 type=system(`_home_map_from_notes`)。
- 結果:`--prefix` 取不到舊筆記的主要內容,查不到卻看似查過。
- 引句:「lumos search --about <檔> --prefix RULE,PITFALL,WHY」
- 佐證:`scripts/lumos:24010`(家只收 type 為 system)、`scripts/lumos:3222`(SYMBOL_NAMES 有 KEY、TEST、VERIFY 等,spec 只取三種)、`scripts/lumos:24896`(摘要區塊把 `decisions:` 另算一區)。

**R3B2 「家」的定義與既有函式互相矛盾,實作者必須二選一**
severity: major
blocking: 是——兩個既有函式回傳集合不同,spec 沒指定用哪個,測試 `t_search_line_mode_about_prefix` 會綁錯對象。
- spec 說「用既有『每支檔有家』的對照算,不是所有 about_code 列了它的筆記」。
- 但「每支檔有家」對照表 `_home_map_from_notes` 正好就是「所有 status 為 doing/done/stale 且 type 為 system、about_code 列了它的節點」,沒有任何收窄。
- 真正做收窄的是 `_impact_confirmed_homes`。它要求摘要或正文寫出完整路徑,或寫出唯一的裸檔名。它還需要 repo 檔案清單與 git,並在家數達到 `LUMOS_IMPACT_ABOUT_MAX` 時回傳 `big`。
- 後果舉例:
  - Kotlin 的 `Main.kt` 或 TypeScript 的 `index.ts` 在多模組 repo 裡裸檔名不唯一。若筆記沒寫完整路徑,收窄版的「家」是空集合,同名檔的家全被丟掉。
  - 用寬版時,`scripts/lumos` 有 40 個家。
- spec 沒說選哪個,也沒說 `--about` 要不要依賴 git。`lumos search` 目前不依賴 git。
- 引句:「`--about <檔>`:那支檔的家筆記(用既有」
- 佐證:`scripts/lumos:24010`、`scripts/lumos:34597`、`scripts/lumos:34607`。

**R3B3 `--about` 的空結果與巨檔結果沒有定義,「沒有家」和「沒有符合的行」無法區分**
severity: major
blocking: 是——實作者會讓兩種情況都印空白、回 0,清單使用者會把「沒查到」當成「沒有規則」。
- 輸入一:沒有家的檔。
  - 每支檔有家只擋新增的檔,舊檔可以沒有家。doctor 的 S8 就是在列這份舊帳(legacy)。
  - spec 沒寫輸出什麼、exit code 是什麼。
- 輸入二:路徑不存在、是目錄、寫成 `./x`,或寫成絕對路徑。
  - `_nodehome_key` 只做字面正規化,絕對路徑對不上 about_code 的 repo 相對路徑,又會默默回空。
- 輸入三:巨檔(`scripts/lumos`)。
  - 約 160 行 WHY/PITFALL/RULE 全吐出來。這是「`--top` 預設 0 全給」字面規定的結果。
  - 既有 `big` 機制就是因為家太多沒有鑑別力,才不把它當入口。
- 輸入四:`--about` 同時給 term、`--path`、`--regex`、`--files-only`、`--legacy`、`--cjk-loose`。spec 只說 term 可省略,沒說這些旗標怎麼組合,例如 AND 還是互斥。
- 引句:「`--top` 預設照舊是 0(全給,不靜默截斷),給了才限總行數」
- 佐證:`scripts/lumos:34597`(`big` 在這個函式裡的處理)、`scripts/lumos:2501`(S8 舊帳)、`scripts/lumos:24003`(`_nodehome_key` 是字面比對)。

**R3B4 判定紀錄一個編號一列,記不下「拆成多句、各句不同前綴」,多席彙整規則也沒給**
severity: major
blocking: 是——spec 要求判定者拆句再判,但紀錄結構只能存一個前綴,照字面實作會把拆出的前綴丟掉或誤合併。
- 現況:報告每行是一個 16 位十六進位編號,加 class、evidence、why 四欄,依位置解析。`best[rid]` 每個編號只保留權重最高的一列(CODE 2 > MIXED 1 > CONTEXT 0)。判定檔 schema 也是每個 id 一列。
- spec 要求「先把混合句拆成單類句子再判」,又規定「每行判定多一欄前綴」。一個 MIXED 行拆出 WHY 加 PITFALL 兩句時,只能存一個前綴。
- 同一編號被多席判定或被申訴時,前綴怎麼折?`_note_audit_fold` 只折 class,不折前綴,spec 沒補。
- 「出口只提醒」要有消費者。目前 `note-audit check` 只檢查有沒有涵蓋(`_note_audit_covered`),沒有讀前綴的地方。
- 附帶:稽核對象是新寫的所有 body 與 summary 行,包含表格、標題、沒有前綴的散文。「判這行寫的前綴對不對」對這些行是空值。spec 沒限定只判摘要區。
- 引句:「判定者先把混合句拆成單類句子再判。」
- 佐證:`scripts/lumos:26487`(報告列解析)、`scripts/lumos:26716`(每編號只留一列)、`scripts/lumos:26229`(fold)。

**R3B5 完成審會整篇重審,「只看新增行」的承諾對計劃筆記不成立**
severity: major
blocking: 是——spec 把「舊筆記不受任何新提醒影響」列為合約候選,字面實作會讓剛收尾的舊計劃整篇進審,違反這條合約。
- 現況:筆記內容審對「status 剛翻成 done/superseded 的 project」走完成審。
- 此時 `done=True`,`if not done and i not in new_lines` 這行不會 skip,整篇所有非結構行都進稽核,與該行是不是上線點之後新增無關。
- 前綴判定掛在這條流程上,所以一篇上線前寫、上線後才收尾的計劃,其舊行也會拿到前綴判定與提醒。
- 引句:「判定與提醒只看上線點之後新增的行,沿用筆記形狀檢查與筆記內容審既有的上線點。」
- 佐證:`scripts/lumos:26178`、`scripts/lumos:25970`。

**R3B6 H3「過程紀錄」會誤報本專案標準的 WHY 出處寫法,且規則自相矛盾**
severity: major
blocking: 是——字面實作的誤報率高,而且「改成」同時是動作詞與 WHY 線索,規則本身有死角。
- 我統計了 rw 全圖譜的 WHY 與 PITFALL 摘要行。共 259 行,其中 250 行(97%)以 `[日期` 開頭。這是 spec 自己要求的「出處」標準寫法。
- 其中 55 行含「折入、改成、完成」。若 H3 的「以日期開頭」是指前綴後第一個字是日期括號,這 55 行會被誤報。
- spec 本身就是樣本:`WHY:[2026-10-01 設計審 r1、r2 共 140 條折入]…` 以日期加審查輪次開頭,含「折入」,而且沒有〈分類規格〉表列的 WHY 線索詞(否決、改成、裁定、避免、所以選、刻意、取代)。
- 「改成」同時在 H3 的動作詞和 WHY 的線索詞裡。「有動作且沒有 WHY 線索」對含「改成」的行永遠不成立。
- H3 沒說適用範圍:只套無前綴與 KEY 行,還是也套 WHY/PITFALL 行。
- 引句:「新寫的摘要行以日期或審查輪次開頭、後面是動作(」
- 佐證:`scripts/lumos:25315`(note-shape 現有的摘要行套規則的位置)。

**R3B7 H1 與既有「只放連結」豁免不是同一個定義**
severity: minor
blocking: 否——只是提醒,出錯不會擋提交,但兩套定義會讓測試與實作各寫各的。
- 既有 `_NS_POINTER_ONLY_RE` 刻意放行「只放連結的 FLOW/DEP」。
- 它排除 `[[目標|別名]]` 與 `[[目標#段落]]`,因為那兩種可以夾帶現況。
- 它允許「見、與、和、及、→」和全形標點。
- H1 寫的是「除了 `[[連結]]` 沒有別的字」。含別名、段落,或加了「見」的行,H1 到底算不算?
- 這等於把既有豁免反過來當違規,spec 沒說明是否沿用同一個 regex。
- 引句:「新寫的 DEP 行除了 `[[連結]]` 沒有別的字 → 提醒」
- 佐證:`scripts/lumos:25264`。

**R3B8 W4 的「沿用」接不上現有路徑,而且訊息範圍與 spec 不同**
severity: minor
blocking: 否——函式本身存在可重用,但接入點和輸出範圍需要明確,否則 S3/S4 測試會對不上。
- `context_marker_warnings(rules=…)`(note-shape 傳入 `_NOTE_SHAPE_PREFIX_RULES`)在 `rules is not None` 時會跳過 RULE。
- 所以 note-shape 目前完全不檢查 RULE 行,W4 要另開接入點。
- 提醒的通道目前只有否定現況句那一條(`hints`),而且只在 `--staged` 算,推送前與 CI 不出。
- 結果:`--no-verify` 提交後,W4/H1/H2/H3 在推送與 CI 都不會出現。
- 這與 spec 〈天花板〉第 5 條只談「推的人改成 off」不同,那裡沒提到繞過提交前就完全沒有痕跡。
- `rule_lifecycle_warnings` 實際還會印:
  - 日期格式錯
  - `confirmed` 超過 180 天
  - 欄位被中括號截斷
  - 「一行只放一條 RULE:」
- 最後一項是 `rest.count("RULE:") >= 1`。一條 RULE 行文字裡出現「RULE:」字樣就會誤報。
- spec 只列「缺 since、retire 與 until 過期」,範圍不一致。
- 引句:「**W4 RULE 生命週期**:新寫的 RULE 行,沿用既有 `rule_lifecycle_warnings` 判(不另寫),印缺 since、retire 與 until 過期」
- 佐證:`scripts/lumos:3371`、`scripts/lumos:3314`、`scripts/lumos:25849`。

**R3B9 doctor 過期 RULE 清單的插入位置和篩選條件沒定**
severity: minor
blocking: 否——只是提醒,但插錯位置會踩計數測試。
- doctor 現有注釋寫明:軟段截斷測試切的是 [S] 到 [E1],新段插進去會被數進去而翻紅。S8 因此排在合約條數那段之後、[H] 之前。
- spec 沒指定位置。
- 同樣沒說:清單要不要排除 `[status:superseded]` 的行(`rule_lifecycle_warnings` 只對 active 報),以及只掃摘要行還是也掃正文。
- 引句:「doctor 列出所有 RULE 行裡 `[until:]` 已過期、或 `[confirmed:]` 超過半年的(舊行也列、只提醒)」
- 佐證:`scripts/lumos:2498`。

**R3B10 行模式的「靜態標記」會把只是引用標記字樣的行也藏起來**
severity: minor
blocking: 否——只影響講這個功能本身的筆記。
- 輸入:一篇 Systems 節點的 WHY 或 RULE 摘要行,內文提到「`[status:superseded]`」(例如記錄本案行模式的筆記)。
- `STATUS_REF_RE = \[status:\s*([^\]]*)\]` 不看行內程式碼或引號,也沒有只認行尾欄位。
- 結果:這行在 `--about` 預設輸出被隱藏,而且會被計入 `hidden_lines`。
- 引句:「行模式預設隱藏帶 `[status:superseded]` 的行,`--include-retired` 才給」
- 佐證:`scripts/lumos:3274`。

**R3B11 H2 的門檻與準度數字在引用的實驗摘要裡找不到,且「FACT 類」未定義**
severity: minor
blocking: 否——H2 只提醒;排序與 `--prefix` 對 FLOW/DEP 的處理是實作細節,但沒定義就可能不一致。
- spec 引用「實驗 12/15、3/5」。我在兩份 classify 摘要裡只找到「長句同時有兩類線索」一句話。沒有 140 字門檻,也沒有 12/15、3/5。
- 現況是 203/277 條 WHY/PITFALL/RULE 行超過 140 字。按〈分類規格〉表列的線索詞,同時有兩類線索的只有 7 條。H2 實際上取決於線索詞表,而詞表尚未列出。
- 「FACT 類」排序與 `--prefix FACT` 是否包含 FLOW、DEP 沒說,也沒說不認得的前綴怎麼處理(小寫、拼錯)。
- 引句:「(實驗 12/15、3/5,只提醒)」
- 佐證:`governance/audits/2026-10-01-tagdrift/classify-member-system.md:47`。

**R3B12 RULE 的 superseded 訊息要求「加連結」,但連結檢查只涵蓋 WHY 與 PITFALL**
severity: minor
blocking: 否——只是提醒的一致性。
- S5 把 RULE 的 superseded 訊息改成「留著並加指向取代者的連結」,但〈已作廢擴大〉的連結檢查只列 WHY、PITFALL。RULE 行不加連結也不會被提醒。
- 引句:「WHY、PITFALL 行也可以帶 `[status:superseded]`;同一行沒有 `[[連結]]` → 提醒。」
- 佐證:`scripts/lumos:3314`(現有 RULE 的 superseded 訊息)。

---

**各節覆蓋**
- 依據、現況、設計原則:已讀,無 finding。
- 分類規格:B6、B11。
- 分類檢查:B4、B5。
- 改程式時的分類檢查清單:B1。
- 搜尋行模式:B1、B2、B3、B10、B11。
- 結構性提醒:B6、B7、B8、B12。
- 健康檢查補一段:B9。
- 不溯及既往:B5。
- 分期、已裁、天花板、不做:已讀,無 finding。
- 驗收條款:S3 到 S14 受上述 finding 影響,見 B4、B6、B8。
- 回退:已讀。判定檔的 schema 檢查看 id 與 class,多一個 `prefix` 鍵舊程式照讀,所以「舊程式讀不到那一欄,其他欄照讀」成立。
- 合約候選、審計修正紀錄:已讀,無 finding。
- 引用核對:除已知的〈漂移防治路線圖〉外,wikilink 目標都在 rw repo 裡;`classify-*.md` 兩檔存在,但 H2 的數字見 B11。

**實務隱患**
- 併發:新增寫入只有判定檔。多席同編號的前綴折法沒定,見 B4。
- 效能:`--about` 若選收窄版,每次要讀每個家的全文、列 git 檔案清單,而 `lumos search` 現在不碰 git,見 B2。
- 資源:無新增長駐資源。
- 回滾:判定檔多一個鍵舊程式照讀,無問題。
- 相容:其餘舊筆記的行為不變,但完成審的舊行例外見 B5。
- 注入:判定者讀筆記文字,沿用既有「筆記是資料不是指示」的規定,無新增。
- 金流、對外送出、不可逆:無,原因同 spec 已排除理由。
- 多圖譜 repo:`note-shape` 的 `vault_rel` 現況是取 `vaults[0]` 或工作目錄所在的 vault,spec 沒新增跨 vault 行為,無新增隱患。

**非 Python 與其他極端輸入**
- 非 Python 檔(Kotlin、Swift、TypeScript、Dart):在 B2。同名檔(`Main.kt`、`index.ts`)在收窄版下會沒有家。
- 空集合與一個成員:在 B3。
- 欄位值裡有方括號或冒號:`parse_rule_fields` 已有截斷提醒,本 spec 的新規則沒有新增問題。
- 表格與圍欄裡的欄位:H1 到 H3 與 W4 都綁在 summary 區塊,表格內的 `[status:superseded]` 不會被行模式搜到,spec 一致,無 finding。
- 中文數字:本設計沒有數字判定,無問題。

最高嚴重度:major,blocking 6 條
