severity: major

(整合與接手鏡頭,第 2 輪。實驗在 `git clone --shared` 的臨時目錄做,把 `LIST_KEYS` 手補上 `system_refs` 試了 append / remove / lint,沒動 repo。)

先講結論:做法 1–6 大致接得上真碼,`cmd_remove`、warn 與 warn_soft、建檔、登記這幾處都有明確落點;但有一個會實際崩潰的接點沒定義(孤兒推薦遇到共用函式回 None),其餘是文件與提示的落點偏差。

## F1 孤兒推薦接共用函式時,回 None 的紀錄沒說怎麼處理,而且孤兒清單本來就會放進這些紀錄
severity: major
blocking: 是
引句:「對有宣告的紀錄改用它列的功能」
file: `scripts/lumos:1414-1416`(孤兒只豁免 status 去空白後恰為 `superseded`,stale、fail 都還在孤兒清單裡;沒有轉小寫)
file: `scripts/lumos:805`(`_suggest_systems_for_orphan(env, rel, n)` 現在直接掃 `n.targets`,沒有「跳過」這個分支)
1. 共用函式對 stale、fail、superseded 回 None。但 doctor 1/4 的孤兒清單只排除 superseded,所以 stale 與 fail 的孤兒紀錄會進 `--suggest` 迴圈,接共用函式後拿到 None。做法 3 只寫「有宣告的紀錄改用它列的功能」,沒講 None 時怎麼辦。照字面實作,`for ... in None` 或解包 None 直接崩潰。例:本 repo `Verification/` 有 8 篇 `status: stale`,其中任何一篇沒人引用,`lumos doctor --suggest` 就崩。
2. 做法 1 說 status「去空白、轉小寫」才比對,孤兒篩選卻只 `.strip()`、不轉小寫。`status: Superseded` 的紀錄會進孤兒清單,共用函式卻回 None,同一條崩潰路徑。
3. 要補一句:None 時退回現行推法(正文連結、plan_refs、feature),還是只印「這份已失效、不推薦」。建議前者,同時孤兒篩選與共用函式用同一個 status 正規化,不然兩處判法不一致。
4. 條款 S11 只涵蓋「有宣告」,沒有「回 None」與「寫壞」兩種形狀的條款。

## F2 S11 與實際推薦機制衝突:宣告了 `無 <理由>` 或列了功能時,plan_refs、feature 兩條線索怎麼處理沒定
severity: minor
blocking: 否
引句:「當孤兒驗收紀錄有宣告時,doctor 1/4 的推薦應只推它 `system_refs` 列的功能」
file: `scripts/lumos:815-838`(推薦有三條線索:正文連結 3 分、plan_refs 經計劃 2 分、feature 提到 stem 1 分)
1. 現在推薦有三條線索,「只推它 system_refs 列的功能」若指全部砍成只剩第一條,宣告 `無 <理由>` 的孤兒會印「(feature/plan_refs/連結皆無線索 → 人工判斷)」,但它其實有宣告、不是無線索,訊息誤導。
2. 若只替換第一條、保留另兩條,宣告 `無` 的紀錄仍會被推薦掛到某功能,跟它自己的宣告矛盾。
3. 要定:有宣告時整個推薦改走宣告;宣告為 `無` 時印「這份宣告沒驗任何功能」;寫壞時指到 doctor 3/4。

## F3 `sync-verified-by` 的「指到 doctor 3/4」放哪裡沒定,最自然的位置會被提前 return 吃掉
severity: minor
blocking: 否
引句:「寫壞的項不補、印一行指到 doctor 3/4」
file: `scripts/lumos:15870-15872`(`if not planned:` 印「✓ verified_by 已全同步,無漏寫」後直接 `return 0`)
1. 只有寫壞的項、沒有任何可補的時候,`planned` 是空的,現行流程印綠色的「無漏寫」就返回。若提示接在 dry-run 說明句那一段(`if not apply:` 之後),這個情境根本到不了,使用者看到「已全同步」卻不知道 doctor 3/4 是紅的。
2. 提示要放在 `if not planned` 之前(算完 expected 就收集寫壞的項),並且那句綠字在有寫壞項時不能再說「無漏寫」。`t_sync_verified_by` 斷言「無漏寫」字樣,有寫壞項的案例要另寫。
3. 另外 dry-run 那句既有的說明「判準同 doctor Check 3:Verification 連到某 Systems 即視為驗證它」,對有宣告的紀錄就是錯的;計劃只說補一句,建議把這句改寫成兩種判準都講。

## F4 doctor 3/4 的綠勾與兩個新標題的排法沒定,會同段「全綠又有警告」
severity: minor
blocking: 否
引句:「每項印紀錄、原文、原因與改法」
file: `scripts/lumos:1503`(綠勾條件現在只看 `not missing`)
file: `scripts/lumos:3329-3346`(收尾:`warn` 只加 `issues`,`warn_soft` 只加提醒段數與條數,不進 issue 數)
1. 現行是 `if not missing: ok(...) else: warn(...)`。多了兩個清單後,若只在 `missing` 空時印「✓ 每份驗證紀錄都掛到了」,寫壞或多掛存在時會同段先綠勾再警告。要改成三個清單都空才印綠勾。
2. 順序建議:漏寫(warn)→ 寫壞(warn)→ 多掛(warn_soft)。硬的在前,軟的收尾,跟其他段一致。
3. 收尾計數接得上:`warn` 進 `issues`(所以 `doctor --ci` 會擋),`warn_soft` 進「另有 N 段、共 M 條提醒」,不進 issue 數,符合計劃宣稱。`warn_soft` 每段預設只顯示 3 條(`--ci` 與 `--verbose` 全列),多掛清單在互動預設會被收成「另 N 條」,正常。
4. 計劃寫的「每項印紀錄、原文、原因與改法」是一條 bullet 裡塞多段資訊,`warn` 的 `advice` 只有一句全段共用,逐項改法得塞進 bullet 本身,實作時注意別讓一條變多行(`issues += len(lines)` 以 bullet 計)。

## F5 `cmd_remove` 接得上,但計劃沒寫落點與判法;要在寫入後、用新的欄位內容判「刪光」
severity: minor
blocking: 否
引句:「`remove` 拿掉最後一項時鍵會一起消失(既有行為)」
file: `scripts/lumos:17805-17880`(`cmd_remove(env, rel, key, value)` → `_cmd_remove_locked`,簽名裡有 `rel` 與 `key`)
file: `scripts/lumos:17339`(`edit_fm_remove` 清空時連 key 行一起刪)
1. 可行性沒問題:`_cmd_remove_locked` 手上有 `rel`、`key`,條件寫 `key == "system_refs" and rel.startswith("Verification/")`(doctor 3/4 自己也是用這個前綴判斷,子資料夾一併涵蓋),「刪光」用 `edit_fm_remove` 回傳的 `new_fm` 判:`key` 不在 `fm_structure(new_fm)` 就是刪光。實驗:刪掉最後一項後 frontmatter 確實不留 `system_refs`。
2. 提醒要印在 `atomic_write_verify` 成功之後,不然寫失敗還印了提醒。remove 刪掉一項寫壞的 `無 …` 或某個連結而留下其他項時不印,合乎「刪光」定義。
3. 要補一個邊角:舊式寫法 `system_refs: [[Systems/A]]`(純量)remove 時也會經 `_list_key_scalar_to_list` 轉清單後刪光,同樣要印。
4. ⚠ `append`/`remove`/dedup 全走 `link_target(value)`,它會把 `#` 與 `|` 後面都切掉。實驗:`lumos append 驗收 system_refs "無 #12 改字"` 與 `"無 #13 別的理由"` 的比對鍵都是 `無`,第二次會被當成「已經有」靜默 no-op;`remove "無 #12 改字"` 會連同其他以 `無` 開頭的項一起拿掉。判寫壞要用原文不要用 `link_target` 的結果,否則「理由至少 4 個字」會被切短;理由裡有 `#`、`|` 時要在說明講。(實驗確認 `無 這份只改文件` 與 `"無 #12 改字"` 都能 append,lint 不唸,`LIST_KEYS` 併入即可,不必加 `_KNOWN_FRONTMATTER_KEYS`,跟做法 5 一致。)

## F6 同步清單:精簡版是凍結目錄,而且清單漏了好幾個真有講 verified_by 判準的錨點
severity: minor
blocking: 否
引句:「精簡版 `slim/skills/lumos-project-notes/reference.md` 的 plan_refs 欄位那節」
file: `slim/FROZEN.md:1-12`(「改這裡不會讓任何使用者拿到」,精簡版交付庫已獨立演進)
file: `skills/lumos-project-notes/reference.md:591-596`、`:819`、`:899`、`:969`、`:987`
1. `slim/` 已凍結(2026-08-20),FROZEN.md 明寫要改去交付庫改。做法 6 還把它列進要同步清單,改了不會有人拿到,還跟凍結宣告打架。建議從清單拿掉,或在計劃寫「slim 不動、理由見 FROZEN」。精簡版 lumos 本身是 `slim-gen.py` 從 `scripts/lumos` 生成,新函式會被 AST 閉包自動帶進去,不需手動同步(`append`、`new`、`doctor`、`sync-verified-by` 都在保留的 26 支裡)。
2. 清單列的錨點實查都存在:`SKILL.md` 第 71 行(決策與驗證)、`reference.md` 第 63 行(健康巡檢列)、第 97 行(list 追加那列)、第 827 行(plan_refs 欄位那節)、`commands/03-寫回圖譜.md` 第 19 行。`commands/04-自檢與健康.md` 沒有講 3/4 判準(第 22 行只是泛稱 doctor 各段),r2 拿掉它是對的。
3. 漏的錨點:`reference.md` 第 591-596 行(sync-verified-by 那節,寫「列 Verification 連到 Systems 但 verified_by 漏列的」,對宣告紀錄不成立)、第 819 行(Check 3 描述)、第 899 行、第 987 行(「建 Verification 同步把 wikilink 加進相關 Systems 的 verified_by」)。另外 `NEW_HINT` 的 verification 提示在 `scripts/lumos:19102`,計劃有提;`sync-verified-by` 與 `append` 的說明字串在 `:43987`、`:43996`、`:44518`、`:44589`、`:44613`,計劃只籠統說「說明字串」,`--systems` 那條(`:44613`)寫「同步 append verified_by 的 Systems」要改成「Systems 另寫進 system_refs」。

## F7 既有測試不會因 3/4 多出 issue 而翻(查過,沒找到)
severity: clean
blocking: 否
引句:「讓它少擋指路連結、多擋寫壞的 `system_refs`」
1. 全 repo 沒有任何程式或測試夾具寫 `system_refs`(grep 只命中計劃與審查材料),新增的兩個檢查只對有這個鍵的紀錄生效,所以現有測試的 3/4 輸出不變。
2. 夾具裡沒有奇怪 status:`scripts/test_lumos.py` 沒有大小寫混用的 `status: Stale/Fail`,本 repo `Verification/` 的 status 只有 pass、stale、superseded,全小寫;轉小寫不會改變現有任何判定。`Verification/` 下也沒有子資料夾。
3. 會被擾動的是 `t_sync_verified_by`(斷言「無漏寫」)與 `t_doctor_suggest`(斷言推薦字串),只要 F1、F3 的分支處理成「沒宣告時一字不改」就不會翻。
4. ⚠ 狀態比對有兩套:E1(`scripts/lumos:2147`)、孤兒篩選(`:1416`)仍是只去空白、不轉小寫。共用函式轉小寫後,`status: Fail` 的紀錄在 3/4 與 sync 被跳過,卻在 E1 不算死背書,兩邊不一致。這是計劃新增的不一致,不是既有的;建議在計劃註明「只改 3/4、sync、孤兒三處,E1 不動及其理由」,或一併正規化。

## F8 路徑一致性的比法沒定,可能誤判合法連結為寫壞
severity: minor
blocking: 否
引句:「連結有寫路徑時路徑要跟解析結果一致」
file: `scripts/lumos:623-638`(`resolve` 先試完整路徑;不中就取最後一段用 `by_stem` 小寫比對,取 `hits[0]`)
1. 合法但會被誤擋的寫法:`[[systems/a]]`(大小寫不同,macOS 與 Obsidian 都認)、`[[sub/A]]`(Obsidian 的最短路徑寫法,指到 `Systems/sub/A.md`)。resolve 都靠檔名救回正確的 Systems 節點,但字面「路徑」跟 `Systems/sub/A` 不相等,照「路徑要一致」會報寫壞。
2. 計劃要定義比法:大小寫與 NFC 正規化後、以「路徑是解析結果的後綴」比對,還是嚴格相等;若要嚴格相等,訊息改法就要叫人寫完整 `[[Systems/sub/A]]`。要補測試案例。
3. 同名衝突時 `hits[0]` 取決於載入順序;計劃寫的「Projects/A 與 Systems/A 同名」例子在 `Projects` 排在 `Systems` 前時 `[[A]]` 會落到 Projects 被判寫壞,反過來則靜默通過,行為取決於排序而非判法,要在測試固定。

最高等級:major,blocking 共 1 條
