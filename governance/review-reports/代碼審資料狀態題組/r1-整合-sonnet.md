severity: major

鏡頭:整合與知識同步(三個月後接手的人,預設文件與現實已經對不上)。逐節讀完 spec、對照 scripts/lumos 現行實作、skills/lumos-code-loop、skills/lumos-design-loop/templates.md、skills/lumos-project-notes/commands/06-代碼審與推送.md、Systems/效能檢核目錄.md、Systems/棧別提問表態閘.md、scripts/test_lumos.py。

## 現況/設計/驗收條款/回退/實務隱患/最小實驗/撤除條件/誠實界線
已讀。設計點 1–8 與 S1–S7 逐條核對程式碼現況(`_stack_key_for_file`、`_is_code_file`、`_stack_applicability`、`_dispositions_template`、`_disp_repo` 測試夾具)全部屬實,S7 鎖定的 `[{stk} 效能檢核]` 印點(`scripts/lumos:26236`)確實存在且會被 `data` 鍵撞到,S4 鎖定的「副檔名剛好叫 data」邊界案例也確實會撞 `_stack_key_for_file`(`scripts/lumos:20221`,`ext = Path(file_rel).suffix...; return ext if ext in _STACK_PERF_QUESTIONS else None`)。以下只報整合與知識同步面向找到的缺口。

## F1 dispatch-lens 附的表態記錄標頭寫死「棧別效能檢核」,ds- 題上線後審查席會被誤導成效能提醒
severity: major
blocking: 是——判準:表態閘的核心設計前提是「工具只驗證據存在,答案對不對留給審查席」,若審查席看到的標頭本身就把資料完整性/不可逆風險錯貼成效能標籤,審查席據此判斷的起點就是錯的,這不是外觀瑕疵而是審查輸入失真。
引句:「所以表態範本、code-loop check、gov --stats、recall-miss 全部照舊運作,不另寫閘」
file: `scripts/lumos:29282-29287` `_lens_dispositions_lines` 印的第一行是 `f"[表態記錄(棧別效能檢核;分支 {rec.get('branch')},版本 {str(rec.get('head_sha') or '')[:8]})——...]"`,字串「棧別效能檢核」是寫死的,函式對 `disp.items()` 逐題印時不分棧、不分 `data` 鍵。
失敗場景:某分支改了一支沒副檔名的 shebang 腳本、新增 `os.replace(`,依 S1 觸發 `ds-partial-write` 並依規表態 satisfied。推派工單時 `_lens_dispositions_lines` 印出「[表態記錄(棧別效能檢核;分支 feat/x,版本 abcd1234)]」,接著列 `ds-partial-write satisfied — path:line`。收到派工單的審查席讀到「棧別效能檢核」這個標頭,會把 `ds-partial-write` 誤判為「這只是某棧的效能建議」而非「寫入中斷後資料會不會壞掉」的正確性問題,反駁力道會系統性偏軟——這正是本計劃設計點 5 想避免的同一種貼錯標籤,只是撞在另一個印點上,S1–S7 沒有任何一條會逼這裡被改。

## F2 code-loop check 擋下訊息同樣寫死「效能檢核」,作者收到的擋下理由會誤稱資料狀態題為效能問題
severity: major
blocking: 是——判準:這是使用者(作者)在推送失敗當下讀到的第一句話,錯誤定性會導致作者用「na:這只是效能建議,不影響上線」這種理由打發資料完整性題,而表態閘本身不驗答案對錯,錯誤定性會被直接放行進治理帳。
引句:「當有資料狀態題適用,pitfalls 的 diff 模式人讀輸出應印」
file: `scripts/lumos:32204` `print(f"擋下:這次改動有 {(dv or {}).get('applicable', 0)} 題效能檢核適用,但表態不完整({len(_pr)} 處)——分支 {branch},版本 {head_sha[:8]}。", file=sys.stderr)`
失敗場景:改動觸發 2 題 `ds-*` 且未表態,`code-loop check` 印「擋下:這次改動有 2 題效能檢核適用,但表態不完整(2 處)」。S6 只驗證「擋下」這個行為本身(有適用題缺表態就擋),沒有任何驗收條款檢查這句訊息的措辭;S7 只修了 `pitfalls --diff` 的人讀輸出(`scripts/lumos:26236`那個印點),沒有涵蓋 `code-loop check` 這條獨立的訊息組裝路徑。作者讀到「效能檢核」四個字,容易當成非阻斷性的建議去敷衍應付。

## F3 Systems/棧別提問表態閘.md 現有的「scripts/lumos 不會觸發」這句斷言,本計劃落地後會變假,但 spec 沒有指名要改哪一句
severity: major
blocking: 是——判準:這是圖譜筆記與程式行為的直接矛盾(內部不一致,依派工說明「一律要報」),而且矛盾方向剛好是本計劃 WHY 段落想解決的那件事本身(工具鏈主程式沒有副檔名、零出題)——如果實作完成後沒人去改這句話,下一個 session 的人會照著這句「以為 scripts/lumos 永遠不會被表態閘問到」去做判斷,而這句話此時已經是假的。
引句:「不是測試檔、不是簿記檔的增刪行,不管副檔名是哪一棧。」
file: `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:95` 原句「本 repo 自己（Python）不在題表，這道閘對 scripts/lumos 的改動不會觸發。」
file: `scripts/lumos:6199-6228` `_is_code_file` 對沒副檔名但首行是 `#!` 的檔案(`_nodehome_code_kind` 判成 `shebang?` 再讀首行)回 True——`scripts/lumos` 本身就是這種檔案,所以設計點 2「每支檔有家那套判定,含沒副檔名但首行是 #! 的腳本」收集邏輯會把 `scripts/lumos` 自己的改動行收進 `ds-*` 觸發池。
失敗場景:實作完 S1–S7 後,有人改動 `scripts/lumos` 本體、增行寫了 `os.replace(`,依設計點 2 觸發 `ds-partial-write`,推送前被 `code-loop check` 要求表態——這與 `docs/lumos-toolchain-knowledge/Systems/棧別提問表態閘.md:95` 白紙黑字寫的「這道閘對 scripts/lumos 的改動不會觸發」直接矛盾。spec 的「現況」段落引用了同一份文件的其他行為描述(棧別題按副檔名分棧、工具鏈主程式零出題)當作立案依據,卻沒有回頭指名這句話要跟著改;「回退」節也只講拿掉 `data` 鍵與七題,沒提到這句話一旦寫的話要不要也跟著退回原句。落地時若漏改,這篇是 `about_code: scripts/lumos` 的家節點,依 CLAUDE.md「每支檔有家」的鐵則,錯誤斷言會被當成該檔案的權威脈絡持續誤導。

## F4 既有測試 t_stack_question_triggers 的「id 集合釘住」斷言沒被列進驗收範圍,加 data 鍵會直接翻紅
severity: minor
blocking: 否——判準:失敗會被測試立刻機械攔下(不是悄悄流入生產的那種缺口),但仍是「多一個 data 鍵會讓哪些既有測試翻紅」這個問題明確要查的項目,而且落地順序若沒抓到會讓 S1 的第一次實作直接卡在無關的既有測試上,浪費一輪。
引句:「放進同一張題表(鍵 `data`,題目 id 一律 `ds-` 開頭)」
file: `scripts/test_lumos.py:39248-39260` `t_stack_question_triggers` 的「①id 集合釘住」斷言:`ids = [s["id"] for v in m._STACK_QUESTION_SPECS.values() for s in v]` 再 `check(... set(ids) == {"kt-compose", ... , "dart-platform"}, ...)`——這個字面集合目前只有 44 個既有 id,一旦 `_STACK_QUESTION_SPECS["data"]` 加了七個 `ds-*` id,`set(ids)` 會多出七個,等號兩邊立刻不等,測試翻紅。
補充:同檔 `scripts/test_lumos.py:23241` `t_pitfalls_stack_questions` 的 `set(sq.keys()) == {"kt", "cs", "vue", "sql"}` 使用的夾具(`Screen.kt`/`Api.cs`/`Page.vue`/`query.sql` 各一行極短內容)目前看不出會命中任何常見 ds- 觸發字樣(無 delete/cache/lock/atomic/timestamp 之類字眼),推斷不受影響,但因為 ds- 觸發字表尚未定案,建議實作時就地跑一次這條測試確認,而不是純推斷。

## F5 skills 文件用「效能檢核題」統稱整套表態閘機制,ds- 題落地後這個統稱會蓋牌非效能性質——內部不一致,一律要報
severity: minor
blocking: 否
引句:「觸發面比棧別題廣(任何程式檔寫檔就可能亮)」
file: `skills/lumos-code-loop/SKILL.md:12` 「同一份輸出的 `stack_questions_applicable`(這次改動觸發到的棧別效能檢核題)**跟 tier 無關**」
file: `skills/lumos-code-loop/reference.md:199` 「棧別效能檢核(2026-07-19 紀律層 → 2026-09-09 表態閘機械化)」
file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:5-6` 「這次改動觸發了幾題效能檢核」
這三處都把整套表態閘機制統稱為「(棧別)效能檢核題」,spec 設計點 5 明確在乎「資料狀態檢核」不該被叫成「data 效能檢核」,但只處理了 `pitfalls --diff` 這一個印點(S7),沒有把這個措辭精確性的考量延伸到 skills 說明文件——這些文件是代理人執行代碼審流程時實際會讀的操作指南,而不是被動的參考資料,遇到 `ds-` 題時仍會被引導成「這是效能檢核的一部分」。非阻斷,因為不影響機械判定,只是概念框架會持續漂移;lands_in 也刻意沒列這幾份 skills 文件,合理(它們不是圖譜節點),但落地時建議至少在其中一處補一句「表態閘現在同時涵蓋效能與跨棧資料狀態兩類題,合稱『棧別/跨棧檢核題』」以防措辭固化成錯誤心智模型。

## 派工鏡頭(dispatch-lens)附表態記錄時 ds- 題會怎麼呈現——總結
會呈現,但被錯誤標籤蓋牌(見 F1):`_lens_dispositions_lines` 不分棧地把 `disp.items()` 全部印在同一個「棧別效能檢核」標頭下,`ds-*` 題目 id、status、evidence/reason/tension 四欄都會正常印出(函式邏輯對 `data` 鍵沒有特殊處理需求,純粹是逐 key-value 印,不會漏印或印錯值),缺的只是標頭措辭跟著失真。這是好消息也是壞消息:資料不會丟,但框架會誤導。

---
最嚴重 severity:major;blocking 共 3 條(F1、F2、F3)。
