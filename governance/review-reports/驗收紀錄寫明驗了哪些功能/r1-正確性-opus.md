severity: major

# r1 正確性席(opus)——驗收紀錄寫明驗了哪些功能_計劃

實驗環境:`git clone --shared` 到 scratchpad/vr-r1/exp-correct-opus(HEAD 19fe606c),臨時圖譜 scratchpad/vr-r1/exp-vault;以 SourceFileLoader 載入 `scripts/lumos` 直接呼叫 `parse_frontmatter` / `link_target` / `Env.resolve` / `edit_fm_remove`,照做法第 1 點字面(「解析每項連結」= `resolve(link_target(項))`)模擬。repo 本身沒動。

## F1 用 CLI 拿掉 system_refs 最後一項會連鍵一起刪,紀錄從「宣告」靜默翻回「從正文推」,S3 的空清單狀態 CLI 走不到
severity: major
blocking: 是
引句:「開頭欄位有 `system_refs` 這個鍵(寫成空清單也算)→ 只看它」
file: `scripts/lumos:17368`(edit_fm_remove:「清完是否還有存活項?沒有就把 key 行也拿掉(空 list 不留裸鍵)」)
file: `scripts/lumos:17877`(_cmd_remove_scalar:清單欄位不准不帶值整欄拿掉)

1. 輸入:Verification/V4 開頭 `system_refs:\n  - "[[Systems/A]]"`,正文「現況見 [[Systems/B]]」(就是 rtb 那種指路連結)。發現 A 其實也不是這份驗的,照計劃做法 4 的「登記成可 `append`/`remove` 的清單欄位」跑 `lumos remove V4 system_refs "[[Systems/A]]"`。
2. 實測 `edit_fm_remove(["type: verification","status: pass","system_refs:",'  - "[[Systems/A]]"'], "system_refs", "[[Systems/A]]")` → `['type: verification', 'status: pass']`,`system_refs` 鍵整個消失。
3. 依做法 1「沒有這個鍵 → 照舊用現行 `n.targets`」,V4 立刻退回從正文推:doctor 3/4 要求 B 反向登記 V4、算 issue、`doctor --ci` 擋推送——正是本計劃要消滅的誤報,而且是經由計劃自己指定的寫法觸發,沒有任何提示。
4. 反方向:S3 說空清單代表「不要求任何功能反向登記」,但 CLI 沒有任何一條路產出 `system_refs: []`(append 一定帶值;remove 到空會刪鍵;不帶值整欄 remove 被擋)。要達成 S3 只能手改開頭欄位,違反專案鐵則「開頭欄位用指令改」。
5. 預期:設計要定死「最後一項被 remove 時 system_refs 保留為 `[]`」(edit_fm_remove 對 system_refs 例外),或改語意讓空清單不具意義並刪掉 S3;並補一條條款+測試釘住「remove 最後一項後判法不翻回正文推」。

## F2 寫壞的 system_refs 項既不進集合、doctor 2/4 也不報,鍵在就等於「宣告沒驗任何東西」,檢查靜默關掉;多連結塞一行還會錯掛到最後一個
severity: major
blocking: 是
引句:「解析不到的不收(doctor 2/4 會報)」
file: `scripts/lumos:1404`(doctor 2/4 的 unresolved 只從 `n.targets` 收)
file: `scripts/lumos:603`(開頭欄位只有「整個值恰為單一 `[[..]]`」才進 `n.targets`)、`scripts/lumos:599`(區塊寫法整段不進)
file: `scripts/lumos:634`(resolve 帶斜線找不到時退回取最後一段當檔名)

1. 「doctor 2/4 會報」這個前提只對「整個值恰為一個 `[[..]]`」的項成立。其他寫法 2/4 看不到,實測(都 `status: pass`):
   - V2 `system_refs:` 下兩項 `Systems/Typo`(照 `core_refs` 純路徑習慣寫、又打錯)與 `"[[Systems/A]] (主要)"`(後面多補一句)→ 兩項 resolve 都是 None、`n.targets` 為空、2/4 不報、lint 也空。照做法 1:鍵存在 → 集合為空 → doctor 3/4 不要求任何反向登記,也不在新的「不是功能筆記」標題下列出(那個只收「存在但不是 Systems」)。結果:一份真的驗了 A 的紀錄,A 漏登記不會被抓,全程零訊息。
   - V1 單項 `"[[Systems/A]], [[Systems/B]]"` → `link_target` 得 `Systems/A, Systems/B`,resolve 帶斜線找不到、退回取最後一段 `B` → 解到 `Systems/B.md`。只要求 B,A 靜默掉。lint 雖然唸「會被當成一個不存在的 ghost 筆記」,但在本計劃的判法下它其實解到了 B,lint 的說法也錯;且 lint 只提醒不擋。
   - V3 寫成區塊 `system_refs: |` 兩行 `[[Systems/A]]` `[[Systems/C]]` → 欄位值是一個含換行的字串,resolve 退回最後一段解到 `Systems/C.md`;A 靜默掉,2/4 因區塊寫法整段排除也不報,lint 空。
2. 計劃在「不做」裡自己講過這種失敗模式有多糟(「會讓忘了填的紀錄變成『沒驗任何東西』,反而把檢查關掉」),但上面三種輸入正是用 system_refs 把檢查關掉、而且比空範本更隱形。
3. 預期:做法 1 對 system_refs 每一項要求「整個值恰為單一 `[[..]]`」(與 `n.targets` 收錄規則同一條);不符的項(純路徑、帶尾巴、多連結、區塊寫法)一律收進問題清單由 3/4 報並算 issue,不靠 2/4。S4 要補這幾種輸入的測試。

## F3 new verification --systems 收任何存在的節點,照做法 3 會把非 Systems 寫進 system_refs,工具自己產出會被 doctor --ci 擋推的狀態
severity: minor
blocking: 否
引句:「照舊對 A、B 加 `verified_by`,另對新紀錄自己加 `system_refs`」
file: `scripts/lumos:19145`、`scripts/lumos:19148`(`--systems` 只檢查檔案存在,不檢查在 `Systems/` 底下)

1. 輸入:`lumos new verification 2026-10-03_X --systems Projects/某計劃`。現行:存在檢查過、對 `Projects/某計劃` 加 verified_by,doctor 不報(本 repo 有 42 篇 Projects 帶 verified_by,把驗收掛在計劃上是既有做法;skill 文件寫的也是 `--systems <節點>`,沒限 Systems)。
2. 照計劃:新紀錄被寫進 `system_refs: [[Projects/某計劃]]` → 做法 2 的新 warn「system_refs 指到的不是功能筆記」→ 算 issue → 推送被擋。工具剛建完、rc=0,下一次 push 才炸。
3. 預期:做法 3 要定 `--systems` 的非 Systems 項怎麼辦——建檔前擋下(跟現有「全部先驗完才建檔」同一處),或只寫 verified_by 不寫 system_refs;S6 補對應測試。

## F4 紀錄改成有 system_refs 後,功能那側舊的 verified_by 背書留著、沒有任何檢查會發現
severity: minor
blocking: 否
引句:「不改功能筆記那側的 `verified_by`」
file: `scripts/lumos:1495`(3/4 只查「紀錄→功能」這一向缺不缺)、`scripts/lumos:2142`(E1 只看驗收紀錄的 status)

1. 輸入:V 原本無 system_refs,正文「現況見 [[Systems/B]]」;之前照 doctor 建議跑過 `sync-verified-by --apply`,B 已有 `verified_by: [[V]]`。現在加 `system_refs: [[Systems/A]]`。
2. 之後 B 仍宣稱「被 V 驗過」,V 卻宣告只驗了 A。3/4 只查正向缺漏不查反向多出;E1 只看 V 的 status(pass),不會判成死背書——所以不會跟 E1 打架,但這條假背書永遠沒人報,而 verified_by 還是 rel-cascade/impact 的具名邊。
3. 推出效果:rtb 這類先被誤報逼著 sync 過的專案,換上 system_refs 後舊汙染全數留下。計劃至少要在「實務隱患」寫明並給收法(例如 3/4 對有 system_refs 的紀錄另列「功能那側掛了、紀錄沒宣告」的軟提醒,或 sync 的 dry-run 列出可 remove 的項)。

## F5 只抽了 3/4 與 sync 兩處,孤兒推薦仍從正文推並叫人跑 sync-verified-by,有 system_refs 時這句建議是錯的
severity: minor
blocking: 否
引句:「這次整段抽成共用一支 `_verification_system_targets`,兩邊改用它」
file: `scripts/lumos:815`(`_suggest_systems_for_orphan` 逐一看 `n.targets`,理由字串「本篇正文連向(verified_by 未同步 → 可 sync-verified-by)」)

1. 輸入:V `system_refs: [[Systems/A]]`,正文「現況見 [[Systems/B]]」,A、B 都沒掛 V → V 是孤兒,`lumos doctor --suggest`。
2. 推薦清單把 B 列為最強線索(3 分)並說「可 sync-verified-by」;使用者照跑 `sync-verified-by --apply`,依 S5 只補 A,B 不補——建議與實際行為對不上。
3. 預期:範圍明列這處是否改用共用函式(或至少有 system_refs 的紀錄只從 system_refs 推薦);不改就寫進「不做」。

## F6 回退段說 revert 只會「lint 唸」,實際上靠 system_refs 排除的指路連結會全部回來擋推送
severity: minor
blocking: 否
引句:「revert 實作提交即可。已寫進筆記的 `system_refs` 留著」
file: `scripts/lumos:1490`(現行 3/4 判法逐一看 `n.targets`,含正文連結)

1. 輸入:實測 V4(`system_refs: [[Systems/A]]` + 正文「現況見 [[Systems/B]]」)在現行程式下 `n.targets == ['Systems/B', 'Systems/A']`。
2. revert 後判法回到現行:B 漏 V4 → 3/4 算 issue → `doctor --ci` 擋。凡是靠 system_refs 才能留著指路連結的紀錄全部重新被擋;消費專案 `lumos update` 到回退版就會撞上。
3. 回退段只寫「不會少掛」,漏寫「會多擋」與收法(把指路連結改純文字、或接受 sync 補上假背書——後者又回到 F4)。

最高等級:major,blocking 共 2 條
