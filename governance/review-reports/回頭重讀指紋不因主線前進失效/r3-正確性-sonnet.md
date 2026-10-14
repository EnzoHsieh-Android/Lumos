severity: minor

我只讀程式和計劃,沒有建暫存目錄,也沒有跑實驗,沒有東西要清。

**已讀,無 finding 的節**
- 「先判 `v1` 再判 `v2`」:順序只影響 `covered_by` 的統計,不影響是否放行。
- fetch 前後:不 rebase 時分岔點不變,不產生新漏洞。
- 記帳時檔名撞名:記錄檔名含時間戳和 32 位亂數(`_NOTE_REREAD_VERDICT_NAME_RE`),同一指紋的新紀錄不會覆寫分岔點裡的舊檔,所以新分支重判後,新紀錄一定是分支新增的。
- 合過主線:分岔點取「上游遠端的主線」,含主線紀錄的合併會把紀錄推進分岔點,被排除。

severity: minor
blocking: 否 — 要手動 `git cp`、`git mv` 或 cherry-pick 才能繞過,不在「單人、AI 依序操作」的威脅模型內;若實作時不補,r2 的「只認分支自己的」就只擋得住無意的情形。
引句:「而且那支紀錄檔是這條分支自己新增的」
問題:「自己新增」只比檔名在分岔點樹裡有沒有,紀錄與指紋的綁定也只靠檔名前 16 碼。
- 現有 `_note_reread_verdict_doc` 的指紋取自檔名(`.group(1)`),不比內容裡的 `contrast_fp`。
- `_note_reread_covered` 現在只回傳指紋集合,沒有逐筆的名稱或來源可供「是否分支新增」判斷。計劃的第 8 點只說「收兩種指紋」,沒交代這個。

失敗情境:
- 主線上有舊紀錄 `F-T0-uuid.json`(指紋 F),分支把它複製成 `F-T1-uuid2.json`(同一指紋、新時間戳)。這個名字不在分岔點樹裡,算「分支自己新增」。之後逐字相同的改動命中 F,舊紀錄就替新狀態背書,正是 r2 要擋的情形。
- 把別人未合併分支的某個提交 cherry-pick 進來,附帶的紀錄同樣算「自己新增」。
- 把舊紀錄改名成新指紋也一樣,因為指紋只看檔名。

建議:判定「自己新增」時,同時要求紀錄內容的 `contrast_fp` 等於檔名指紋,並要求紀錄內容的 `tip` 不是分岔點的祖先(即在 base..tip 之間)。
file: `scripts/lumos:36435`(`_note_reread_verdict_doc` 只用檔名)、`scripts/lumos:36465`(`_note_reread_covered` 只回指紋集合)

severity: minor
blocking: 否 — `contrast_fp_v1` 是新增、可手改、不核對的欄位;它的威力不比舊式 `v1` 檔名大,所以不是新增的漏判,是新增的另一個手改面。
引句:「紀錄內容的 `contrast_fp_v1` 欄位等於它」
問題:
- 紀錄的 JSON 內容沒有來源核對,`provenance_ok` 只是紀錄時寫進去的布林值,check 時不重算。
- `contrast_fp_v1` 是新的第二個身分欄位,`_note_reread_doc_err` 沒驗它的型別。

失敗情境:
- 型別:`"contrast_fp_v1": []` 或 `{}` 放進比對用的集合時丟 `TypeError`。計劃沒寫 check 遇到時是降級還是整個崩潰。
- 繞過:把主線上任一份 `provenance_ok: true` 的舊紀錄的 `contrast_fp_v1` 手改成現在的 `v1`,就走「先判 `v1`」的路徑。這條路徑沒有「分支自己新增」的限制,等於整個繞過 r2 的修補。
- 無意情形:不經手改,因為 `v1` 只含程式 blob、不含筆記內容,所以主線上舊紀錄在程式位元組又相同時,本來就命中。這跟舊設計的語意一樣,不是新洞。

建議:只在 `isinstance(str)` 且符合 16 碼十六進位時才收這個欄位;並把「內容欄位 `contrast_fp_v1` 命中」的紀錄也限定為檔名指紋或 `tip` 能對上的紀錄。
file: `scripts/lumos:36449`(`_note_reread_doc_err` 沒驗新欄位)、`scripts/lumos:36806`(紀錄內容的寫入處)

severity: minor
blocking: 否 — 需要遠端追蹤 ref 比分支所含的主線舊,而且推送範圍起點正常、v2 剛好等於舊紀錄的指紋,實際上很難同時成立。
引句:「分岔點只看遠端主線」
問題:分岔點取 `refs/remotes/*` 的 ref,沒有 fetch 的保證。
- 如果分支內含的主線比追蹤 ref 新(例如從另一個遠端或工作樹得到),`merge-base` 會落在舊的追蹤 ref 上。
- 這時新進的主線紀錄不在分岔點樹裡,會被當成「自己新增」。
- 同時 `v2` 也會把別人的改動算進去。

失敗情境:分支只有改筆記加一小段程式,但主線舊紀錄 R 的指紋剛好等於 base_old..tip 的改動指紋時,R 被當成已對照。因為候選要求推送範圍內改到程式檔,這個條件其實幾乎不會成立。
建議:這種情形下 `v2` 的失敗方向是多列,不是漏判;放行即可,但計劃可以在 `fp_counts` 加一個「追蹤 ref 比本機主線舊」的退回原因,方便日後量測。
file: `scripts/lumos:47244`(`_push_mainlines` 只用追蹤 ref)、`scripts/lumos:50959`(`_codeloop_default_base`)

**總結**:最高等級 minor,blocking 0 條。我沒找到「該重讀的筆記被當成已對照」的非手動路徑。三條 minor 都靠手改、cherry-pick 或過期追蹤 ref,最值得補的是把「自己新增」改成同時檢查內容 `contrast_fp` 與 `tip`。
