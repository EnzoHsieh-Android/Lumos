severity: major

## 範圍與已讀節

已讀:設計材料全文、前掃收貨紀錄(r1-intake,未重報)、`scripts/lumos` 裡的 `_note_reread_scan`、`_note_reread_contrast_fp`、`_note_reread_item`、`_note_reread_given`、`_note_reread_diff`、`_note_reread_layer2`、`_note_reread_covered`、`_note_audit_start`、`_codeloop_default_base`、`_push_mainlines`、`_push_range_start`。我在 scratchpad 臨時倉庫裡做了兩個實驗,沒有動 repo。

## findings

severity: major
blocking: 是 — 新指紋把「git 查不到」和「分支沒改」都記成「未改」,路徑對不上時會把該重讀的當成已對照(漏判,對應守衛面最怕的那一種)
引句:「這條分支沒改那支檔:記成「未改」——主線怎麼改它都不影響指紋。」
問題:指紋要拿 about_code 的鍵去問 `git diff -- <路徑>`,沒輸出就記「未改」。但鍵是 NFC 正規化過的(`_nodehome_key`),git 樹裡存的卻可能是 NFD 寫法。設計沒說要不要換回原樣路徑。程式裡 `scan["changed"]` 已經分成 NFC 鍵和 git 原樣值兩套,註解也寫了「NFC 過的路徑在 NFD 樹裡查不到」。我的實驗是在 macOS 預設 `core.precomposeunicode=true` 下,樹裡放 NFD 檔名,用 `--literal-pathspecs diff -- <NFC 或 NFD 字串>` 查,輸出都是 0 行;關掉 precompose 才查得到。逐檔切 diff 時,檔頭帶引號的跳脫檔名也有同樣的對不上風險。
具體失敗情境:
- 輸入:about_code 列了 NFD 檔名的 `é.py`,分支改它並已記紀錄。作者之後又改了它。
- 結果:兩次的指紋裡這一項都是「未改」,指紋不變,紀錄繼續算數,該重讀的沒被列出。v1 用 `ls-tree` 的 blob 編號,不依賴 pathspec,不會有這個洞。
- 同一類:about_code 裡的鍵解不成 pathspec(目錄項、拼錯的路徑)時也一樣,git 靜默回空,被記成「未改」。
修法方向:「未改」要由 `--name-status` 或 `changed` 的成員判定(用 git 原樣路徑),不要由「diff 輸出沒有這一檔」判定;對不上任何樹內路徑的鍵退回 v1。
程式佐證:``file: `scripts/lumos:30724` ``(`_nodehome_list` 的 oids 以 NFC 為鍵);``file: `scripts/lumos:36061` ``(`changed` 同時存 NFC 鍵與 git 原樣值)。

severity: minor
blocking: 否 — 錯在「多列」,方向安全,但會削弱計劃要解的問題
引句:「rebase 時解衝突改到了作者那段,或主線改動落在作者那段的前後三行內(上下文變了),指紋會變——這兩種本來就該重讀。」
問題:設計說只有這兩種情況指紋會變。但 `@@ -a,b +c,d @@` 後面的函式名提示字串(funcname)也被原樣雜湊,只換掉了數字。它是 git 往上找的最近一個第 0 欄起頭的行。實驗:作者改 `def foo()` 內的一行,主線在同一函式上方、離作者改動超過三行處插一行第 0 欄的 `VAR = 3`。作者的 diff 一個字沒變,標頭卻從 `@@ -9,7 +9,7 @@ def foo():` 變成 `@@ -10,7 +10,7 @@ VAR = 3`,指紋變了。repo 的 `.gitattributes` 或本機 `diff.<driver>.xfuncname` 也會改變這一段;S5 只列了 `diff.algorithm`、`noprefix`、`interHunkContext`、`mnemonicPrefix` 與外部 diff 工具,沒列這項。
具體失敗情境:主線在作者那段上方加了第 0 欄的行,不在作者前後三行內。S1 的前提(不在前後三行內)成立,但指紋仍然失效,等於這條 rebase 路徑上 v2 沒有比 v1 好。
建議:標頭只保留 `@@`,把後面的 funcname 去掉,或加 `--no-function-context`(未驗證這個選項能否去掉標頭字串)再加驗收條款。

severity: minor
blocking: 否 — 結論(分支不改的檔不進指紋)本身站得住,但理由句不實,RETIRE-IF 也量不到漏判
引句:「主線的改動由合進主線那次推送自己的回頭重讀負責。」
問題:這個前提在幾條路上不成立。
- 候選必須同時是「範圍裡改到的檔的家」和「範圍裡被碰過的筆記」。主線有人改了 `a.py` 但沒碰筆記 N,N 在主線那次推送根本不是候選,沒人重讀。
- `note_reread.gate` 不是 block 時,或用 `--no-verify` 時,主線那次推送也不擋。筆記內容審的 WHY 行已寫明「代價:用 --no-verify 跳過本機掛鉤時這道沒有 CI 兜底」。
- 別人直接推主線時,同樣只有本機掛鉤。
實際上這不是 v2 新增的漏洞。v1 在 rebase 後重派,判定者看到的 diff 也只有作者自己的(範圍起點在 rebase 後是新主線,或取不是舊值祖先的分岔點),看不到主線改動,所以 v1 並沒有提供主線感知。建議把理由改成這個事實,不要拿主線那次推送當擔保。RETIRE-IF 的「該重讀卻被當成已對照」沒有任何機制會被人回報,REVISIT 數不到它。
程式佐證:``file: `scripts/lumos:36061` ``(候選 = homed ∩ touched);``file: `scripts/lumos:36204` ``(`_note_reread_diff` 只傳作者範圍的 diff)。

severity: minor
blocking: 否 — 只會多列,但 S3 與「必然相同」的措辭過強
引句:「所以手動 prepare 與推送前 check 在同一份 refs 狀態、同一個頂端下算出的分岔點必然相同。」
問題:新簽名 `(repo_root, tip)` 在指向頂端的本機分支「零條或多條」時退回目前簽出的分支,用它的遠端去算主線候選。prepare(手動,簽出的就是工作分支)與 pre-push(推的可能是別條,例如 `git push origin other:feature`,或兩條本機分支指同一提交)的簽出分支可能不同,遠端也就不同(origin 對 fork),`_push_mainlines` 的候選與 merge-base 不同,對照指紋不同。結果是 prepare 記的紀錄對不上 check,提醒消不掉,正是舊否決理由要避免的現象(方向安全,只是又回到舊問題)。這個前提應該寫進 S3 的條件,並補一支「兩條本機分支指向同一頂端」的測試。

## 資料狀態五問

- 新舊互讀(v1/v2 共存):已讀,無 finding。v2 多一行版本字樣,雜湊不會撞 v1。退回 v1 時只會接受 blob 綁死的舊紀錄,方向安全。第二層按筆記路徑取聯集,舊 v1 紀錄點出的規則類條目在新紀錄出現後要重表態,設計已寫明。
- 寫一半(逾時、共用 diff 失敗):已讀,無 finding。共用那次 `git diff` 失敗會讓所有候選退回 v1,等於靜默退回舊行為,只多列不漏判。但這會讓升級的好處在慢機器上無聲消失,建議印一句「這次退回 v1」,屬優化,不計 finding。
- 衍生資料(第二層表態):已讀,無 finding。表態以紀錄指紋為鍵,v2 指紋穩定後表態在 rebase 後仍然有效,符合設計意圖。
- 時間(rebase 前後):除上述 funcname 與 NFC 兩條外,已讀,無 finding。分岔點只在分支吸收新主線時才會變。
- 不可逆:已讀,無 finding。紀錄檔格式不變,回退只會讓 v2 紀錄失效,不會讓錯的紀錄生效。

總結:最高等級 major,blocking 共 1 條(NFC 與 git 原樣路徑造成的靜默「未改」漏判),另有 3 條 minor 不擋。
