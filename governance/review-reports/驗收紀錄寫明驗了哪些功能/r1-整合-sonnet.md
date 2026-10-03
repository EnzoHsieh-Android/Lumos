severity: major

整合與接手鏡頭。實驗在 `git clone --shared` 的臨時目錄(scratchpad/vr1)做,未動 repo。已確認不會翻的:既有測試 t_sync_verified_by、t_new_verification_bidirectional、t_new_verification_backlink_blocked_still_says_note_created、t_new_verification_plan_backlink_blocked_still_says_note_created、t_check3_*、t_check_e1_dead_endorsement 的夾具都沒有 `system_refs` 鍵,「有鍵才換判法」所以不會翻;`LIST_KEYS` 加一鍵後 lint 已知欄位(`_known = set(_KNOWN_FRONTMATTER_KEYS) | set(LIST_KEYS) | ...`)確實自動認得它,S7 的 lint 半句成立;doctor [N] 的 count 標記加鍵前後都是「11 個不符」,沒有新增紅燈。

## F1 `lumos remove` 拿掉最後一項會把整個 system_refs 鍵刪掉,靜默退回「從正文推」,S3 的空清單狀態用指令到不了
severity: major
blocking: 是
引句:「開頭欄位有 `system_refs` 這個鍵(寫成空清單也算)→ 只看它」
file: `scripts/lumos:17339`(edit_fm_remove 註解與行為:清完若 list 空了,連 key 行一起移除)
1. 實測(vr1 臨時 vault):驗收紀錄 `system_refs: [ "[[Systems/A]]" ]`、正文有指路 `[[Systems/B]]`。跑 `lumos remove Verification/2026-01-01_v system_refs "[[Systems/A]]"` → 檔案變成完全沒有 `system_refs` 鍵;之後 doctor 3/4 出現「Systems/B.md 漏: 2026-01-01_v」。預期(依計劃「宣告優先」)應是「空清單=不要求任何反向登記」。
2. 這表示:作者想把「驗了 A」改成「其實一個都沒驗」,用計劃唯一提供的寫側指令(append/remove)做不到;只會從「宣告」掉回「推測」,而且原本被指路連結誤擋的問題原樣回來(正是本案要解的)。S3 只測手寫 `system_refs: []`,測不到這條路徑。
3. 修法方向:要嘛 `remove` 對 `system_refs` 清空時留下 `system_refs: []`(edit_fm_remove 要為此鍵特例,並改測試釘),要嘛計劃明講「空清單只能手寫、remove 到空會失效」並在 remove 輸出提示;再補一支 `t_system_refs_remove_last_keeps_declared` 先紅測試。
4. 另:`new verification` 沒帶 `--systems` 時也不會寫 `system_refs`,所以「建檔時就宣告『我沒驗任何功能』」同樣沒有入口(計劃已明說不改範本,但沒給替代)。

## F2 S4「指到不存在的節點只由 doctor 2/4 報」對非單一純連結寫法不成立,會靜默丟掉背書
severity: major
blocking: 是
引句:「指到不存在的節點時只由 doctor 2/4 報、3/4 不重複報」
file: `scripts/lumos:597-611`(`_note_from_text`:只有「整個值恰為單一 wikilink」才進 fm_targets;區塊寫法整段排除)
1. 2/4 的 unresolved 來源是 `n.targets`(`scripts/lumos:1404`),而 `system_refs` 只有「每項恰為單一 `[[連結]]`」才進 `n.targets`。計劃做法 1 的「解析每項連結」沒說明其他寫法怎麼辦。
2. 實測:`system_refs: "[[Systems/A]], [[Systems/Nope]]"`(單行多連結,lint 的 L 段會唸,但只是 ⚠)→ doctor 2/4 顯示「✓ 沒有連到不存在筆記的連結」,3/4 沒任何輸出,A 沒被要求登記。也就是這份紀錄「宣告了一個鍵」但驗了誰變成空集合,沒有任何硬 issue 擋。同樣的洞:`system_refs: Systems/A`(純路徑,像 core_refs 寫法)、`system_refs: |` 區塊寫法、`[[Systems/A]]` 帶裝飾文字。
3. 這跟 RETIRE-IF「漏列」的風險不同:作者意圖是列了,工具卻靜默當成空。建議:共用函式對「鍵存在但某項不是可解析的單一連結」也收進問題清單(或至少一個 warn),S4 補一支寫法變體的測試(單行多連結、純路徑、區塊)。
4. 另外 `edit_fm_append` 對已存在的純量 `system_refs: "[[Systems/A]]"` 會先轉清單再加(可行),但純量+單連結這種寫法本身計劃沒定義「算不算有鍵」——`fields["system_refs"]` 是字串不是 list,做法 1 的「解析每項」要明講用 `as_list`。

## F3 `new verification --systems` 只檢查檔案存在,指到非 Systems 也會被寫進 system_refs,建檔當下就製造 S4 的 doctor issue
severity: major
blocking: 是
引句:「照舊對 A、B 加 `verified_by`,另對新紀錄自己加 `system_refs`(每項一行,走既有的 `cmd_append`,照 `plan_refs` 那段的寫法)」
file: `scripts/lumos:19138`(`for rel in sys_rels + plan_rels:` 只驗存在,不驗是 Systems/)
1. 現行 `--systems Projects/某計劃` 或 `--systems Issues/X` 能建檔且 rc0(只存在檢查);舊行為是往那篇加 `verified_by`,doctor 3/4 不看(expected 只收 Systems/)。
2. 加上本案後同一條指令會把 `[[Projects/某計劃]]` 寫進新紀錄的 `system_refs`,3/4 新增的「有 N 項 system_refs 指到的不是功能筆記」立刻算 issue,`doctor --ci` 擋推送;而且是工具自己寫出來的、作者沒打錯。
3. 修法方向:`new` 在寫之前就對 `--systems` 做 Systems/ 前綴檢查(早於建檔,跟「全部先驗完才建檔」同一處),或不是 Systems 的不寫 `system_refs`;補測 `t_new_verification_systems_non_system_rejected`。S6 目前只測 Systems 正向。

## F4 「要同步的文件」清單與真碼不符:slim 版有 plan_refs 一節、commands/04 沒有 3/4 段,真正的錨點沒列
severity: minor
blocking: 否
引句:「精簡版 `slim/skills/lumos-project-notes/reference.md` 沒有驗收紀錄欄位那一節,不用同步」
file: `slim/skills/lumos-project-notes/reference.md:472`(「### plan_refs 欄位(Verification → 計劃的意圖鏈)」)、`slim/skills/lumos-project-notes/reference.md:48`(append 清單欄位列舉)、`skills/lumos-project-notes/commands/04-自檢與健康.md:6,22`(只有泛泛的 doctor 一行,沒有 3/4 專段)
1. slim 版確實有 plan_refs 節與 `append` 清單列舉(:48、:312),判斷「沒有那一節」是錯的;至少要在實作時決定 slim 要不要同步並寫出理由,而不是以「沒有」帶過。
2. 計劃列的 `commands/04-自檢與健康.md`「3/4 段」不存在,接手的人會找不到錨點;真正提到驗收紀錄雙向掛接的是 `commands/03-寫回圖譜.md:7,19`、`skills/lumos-project-notes/SKILL.md:71`、`reference.md:97(append 列舉 verified_by/plan_refs/related/tags)`、`reference.md:594-596(sync-verified-by 說明)`,都沒列進清單。
3. 程式內的同步面也漏列:`scripts/lumos:44589` append 子命令的 help 寫死「(verified_by/plan_refs/related/tags)」、`:44613` `--systems` help 只說「同步 append verified_by」、`:44518` sync-verified-by help、`NEW_HINT["verification"]`(:19100,計劃有列)、`cmd_sync_verified_by` dry-run 末尾「判準同 doctor Check 3:Verification 連到某 Systems 即視為驗證它」那句(計劃只說補一句,但那句本身變成對有 system_refs 的紀錄是錯的)。
4. 好消息(不必報成問題):`docs/.../Systems/lumos-cli-write.md:36` 的 LIST_KEYS 列舉已自註「以常數為準勿再列舉」,count 標記本來就不符(8 vs 實 9),加一鍵不改變 doctor [N] 的 11 條;cli-write 其他筆記行沒有寫死 LIST_KEYS 鍵數。

## F5 orphan 推薦與 sync 對有 system_refs 的紀錄會互相矛盾
severity: minor
blocking: 否
引句:「`sync-verified-by` 的 dry-run 說明句補一句「有 system_refs 的紀錄只看它」。」
file: `scripts/lumos:15911`(`_suggest_systems_for_orphan` 仍用 `n.targets` 推,reason 印「本篇正文連向(verified_by 未同步 → 可 sync-verified-by)」)
1. 計劃只讓 doctor 3/4 與 sync 改走共用函式,但 doctor 1/4 `--suggest` 的 `_suggest_systems_for_orphan` 也是從 `n.targets` 推「驗了誰」,而且建議「跑 sync-verified-by」。對寫了 `system_refs` 的紀錄,它會推薦指路連結的 Systems、sync 卻不補,使用者照做後 1/4 孤兒依舊,卡住。
2. 這是計劃「n.targets 的組成說明」之外的第三個「驗了誰」的消費者;範圍收窄可以不改,但至少要在「不做」寫明、或讓它也呼叫共用函式(回傳是集合,改動小),並測一條 `--suggest` 場景。

## F6 版本不齊的相容只講了單向
severity: minor
blocking: 否
引句:「舊紀錄不寫就照舊,消費專案 `lumos update` 後行為不變;只有自己寫了欄位的紀錄換判法。」
file: `scripts/lumos:5891`(舊版 lint 對未知鍵只 warn「不認得這個欄位」)、`scripts/lumos:17772`(舊版 `append` 對非白名單鍵 rc2)
1. 只談了「新版讀舊紀錄」。反方向:團隊/CI 有人還在舊版 lumos(例如 CI 釘舊版、另一台機器未 `lumos update`),讀到 `system_refs` 時 doctor 3/4 仍從 `n.targets` 推,指路連結照樣擋推送(而 `system_refs` 每項又都在 n.targets 裡,所以舊版還會把 system_refs 列的功能也算進去,結果≥新版,不會少擋但也沒解誤擋);舊版 lint 唸「沒見過的鍵」(軟提醒),舊版 `append system_refs` rc2。
2. 回退節「revert 後 lint 會唸不認得的欄位」只說到本機 revert,沒說多版本並存期。建議在「相容」補一句:要靠指路連結的專案得等全體升版;並在 RETIRE-IF/REVISIT 的量測裡加「有沒有 CI 還是舊版」(⚠ 我沒查 `cmd_update` 實際分發方式,判不準消費專案的 CI 是否釘版)。

最高等級:major,blocking 共 3 條
