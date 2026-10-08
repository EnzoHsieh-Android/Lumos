severity: major

# 設計審第 1 輪 正確性-opus:守檔筆記對照改動_計劃

鏡頭:照字面實作時,候選、diff、指紋、record、check 每一步在真實輸入上會不會算錯、漏算或多算;條款能不能寫成會翻紅的測試;沿用的既有函式參數與回傳能不能那樣用。
實驗在 `rr-r1-work-正確性-opus/`(repo 用 `git clone --shared`;另建小 repo `exp/` 重現起點分岔;實驗資料唯讀讀 negguard 的 `governance/eval/home-check/`,rtb 用 `/Users/enzo/rtb-production-agent-demo` 唯讀 `git show`/`git grep`)。

附錄 V3 逐字核對:用 `tune/scripts/build_prompt.py` 的 HEAD + HIST_V3(partial=全文、extra/evfield 空)渲染,跟凍結稿附錄逐字元相同(True),這點無 finding。

## F1 about_code 列了的測試檔兩頭都不收,判定者看不到被綁測試的改動
severity: major
blocking: 是
引句:「再用每支檔有家的 `_nodehome_required` 判哪些是要有家的程式檔」
file: `scripts/lumos:23833`
1. `_nodehome_required` 在第 23833 行用 `_nodehome_is_test(p, layout)` 把測試檔排除。實測 `tests/model/test_modelclient.py`、`tests/conftest.py`、`tests/model/fakes.py`、`scripts/test_lumos.py` 都判成測試(True)。所以照第 1 節,「改到的程式檔」裡不會有測試檔。
2. 第 2 節 diff 只放「about_code 列了、而且這次有改到的程式檔」。這裡的「程式檔」如果照第 1 節的定義,about_code 列了的測試檔就不在裡面。另一條補測試檔的規則又限定「沒被任何家的 about_code 列到」,把「列了的」排掉。結果是:家筆記 about_code 明寫的測試檔改了,兩個集合都不收,diff 裡沒有它。
3. 量過準度的材料不是這樣。實驗的 `mine = [f for f in code if f in ac]`(`governance/eval/home-check/validate/scripts/vcommon.py:130`)會把列了的測試一起放進 diff。實驗二 rtb 有 20 份 prompt 的 home_files 含 tests/…(例:R01n1 的 `tests/dsp/test_server.py` 等;R06n2 列了 11 支測試)。工具鏈那組 10 份含 `scripts/test_lumos.py`。實驗一 D2 列了 `tests/conftest.py`、`tests/model/fakes.py` 等 8 支。
4. 更極端的情況:家只列了測試檔、這次也只改到測試檔,照第 1 節連候選都不是。實驗二 rtb 有 7 份是這種(R03n1、R07n5、R08n2、R10n5、R12n1、R13n2、R15n1),其中 R10n5、R15n1 各點出一行。
5. 判定問法明寫「綁了哪支測試([test:…])…一律要檢查」,〈做法〉5 也說轉擋起點是「帶 `[test:]` 的結構行」。照字面實作,正好是這類行看不到它綁的那支測試改了什麼。S2 的字面(「about_code 列了而且這次改到的程式檔」)也沒釘測試檔算不算,兩種寫法都能過測試。
6. 建議:diff 的「列了的檔」改成「about_code 列了、這次改到的任何檔」(不經 `_nodehome_required` 過濾),候選觸發也要算列了的測試檔;S2 補一個「列了的測試檔改了要進 diff」的案例。

## F2 「同一層目錄」跟實驗的測試檔規則不同,rtb 版面下一支也補不到
severity: major
blocking: 是
引句:「跟這些檔同一層目錄、`_nodehome_is_test` 判是測試、而且沒被任何家的 about_code 列到的測試檔」
file: `governance/eval/home-check/validate/scripts/vcommon.py:111`
1. 實驗在 rtb 用的規則是:`tests/<套件>/…`,套件名取自 `src/rtb/<套件>/…`(vcommon.py:108-112,實驗一 build_prompt.py:111-113 相同)。也就是說程式在 `src/rtb/dsp/`,測試在 `tests/dsp/`,兩者不在同一層目錄。
2. 照 spec 的「同一層目錄」,rtb 的套件測試一支都補不進去。實驗二 rtb 有 13 份 prompt 靠這條規則補進測試(例:R02n1 的 `src/rtb/dsp/*.py` 配 `tests/dsp/test_server.py`、`tests/dsp/test_store.py`)。
3. spec 自己引的理由(「實驗一:rtb 被刪或改名的測試都沒被列,不加就看不到」)正好會失效。實驗一 D3 的 TP 第 122 行「不看廣告狀態」(`tune/line_judgments.tsv:37`)靠的是綁定測試改名;那支測試是 `tests/demo/test_basis.py`(`git grep` 在 b2fc512 證實),實驗是以補進來的測試檔身分給判定者看的。照 spec 的規則,它不會出現在 diff 裡。
4. S10 的重跑用 `validate` 的腳本,只換範本,材料還是實驗那套組法。所以 F1、F2 這種「產品組材料跟實驗不同」的差距,接線前沒有任何步驟會量到。
5. 建議:把規則寫成跟實驗等價、而且不綁 rtb 版面的定義(例:測試檔路徑去掉測試資料夾前綴後的目錄,等於程式檔去掉原始碼根目錄後的目錄;或直接沿用 `_nodehome_layout` 認的測試資料夾對應)。S2 補一個「src/pkg/x.py 配 tests/pkg/test_x.py」的案例;S10 改成用產品的 reread-prepare 產材料來重跑。

## F3 刪掉的程式檔、這次被移出 about_code 的檔,永遠不會觸發候選
severity: major
blocking: 是
引句:「用 `_nodehome_homes`(背後是 `_home_map_from_notes`:Systems 底下、type 是 system、status 是 doing/done/stale 的節點)取頂端版本的」
file: `scripts/lumos:24234`
1. 第 1 節三個輸入都只看頂端:`_nodehome_required` 讀頂端快照,家的對照也取頂端版本。
2. 程式檔在範圍裡被刪掉時,`_nodehome_changes` 回的是 `(D, 舊路徑, None)`,頂端的 `side.files` 裡沒有它,`_nodehome_required(頂端)` 不會收,所以它不算「改到的程式檔」。就算那篇家這次也改過(只往後追加一段),照樣不是候選。
3. 同一種「只看頂端」的漏洞,每支檔有家已經修過:`_nodehome_evaluate` 用 `code_deleted = {p for p in deleted if p in reqB}`(24234,註解「刪掉(含改名的舊路徑)的需要家的檔也算改動(第二輪外家席)」),並且同時算 `homesB`。
4. 第二種漏法:作者在範圍裡把某支檔從 A 篇的 about_code 移走,正文沒回頭改。頂端的家對照已經沒有 A,A 不是候選,但 A 的舊句還在描述那支檔。
5. 刪掉模組或函式是這類漂移的主要來源:實驗一的 TP 多是「b2fc512 刪 _render_ai_rounds」「刪續租回呼」這類刪除。整支檔刪掉是它的極端版。
6. 建議:候選改成「改到的程式檔 = 頂端需要家的改動 ∪ 起點需要家的刪除或改名舊路徑」;家 = 頂端家 ∪ 起點家(限定這次也被改過的)。diff 的 pathspec 要收刪掉的舊路徑。S1 補「刪檔」與「about_code 移出」兩個案例。

## F4 指紋綁在範圍的 diff 上,手動 prepare 與推送前 check 的起點算法不同,合過主線時紀錄永遠對不上
severity: major
blocking: 是
引句:「手動跑不帶那兩個參數時照 `_lens_push_base`」
file: `scripts/lumos:34701`
1. 項目指紋含「給的 diff 全文雜湊」,diff 是「範圍起點到終點」的,所以指紋取決於起點。
2. 推送前掛鉤與 CI 的 check 帶 `--push-remote/--pushed-ref`,起點走 `_push_range_start`;作者手動跑 prepare 不帶這兩個參數,起點走 `_lens_push_base`。spec 自己也承認後者在合過主線時會多算。
3. 實測(`exp/`:feat 推過 R1 → main 再多一個改 g.py 的提交 → feat 合 main → 再改 f.py):`_lens_push_base(R1, tip)` 回 R1;`_push_range_start(R1, tip, origin, refs/heads/feat)` 回 main2(「合過主線…從最近的分岔點算」)。兩個起點不同,diff 就不同:前者多含主線的 g.py,也多含主線提交碰過的筆記。
4. 照字面實作的流程:check 提醒 → 作者手動 prepare(或照既有 `note-audit check` 的慣例,印原樣的 `--diff {diff_range}`、不帶推送參數;見 `scripts/lumos:26546`)→ record → 提交紀錄 → 再推。check 重算的指紋跟紀錄檔名的不同,同一篇永遠被重列,作者無從解除。〈做法〉4 把「修完被重列」當成刻意行為,但這個情況是算法不一致造成的,不是刻意的,REVISIT 的「修完被重列」統計也會被污染。
5. 同一個機制也影響 skill 推送前那一節的操作順序:推之前先跑 prepare,範圍怎麼給沒有定義。例如 `origin/main..HEAD` 對已推過的分支,跟掛鉤的「遠端舊值..頂端」就不是同一段。
6. 建議(擇一寫死):(a) check 印的 prepare 指令帶已算好、已截上線點的起點 sha(`--diff <起點>..<頂端>`),而且寫明手動 prepare 一律照 check 印的跑;(b) prepare 也收 `--push-remote/--pushed-ref`;(c) 指紋不含範圍相依的東西。S6 補一條:prepare → record → 提交後,帶推送參數的 check 在合過主線的歷史上不再列那篇。

## F5 範圍解析自己也寫 note-audit 的 skipped 事件,跟筆記內容審的 skipped 混在一起,reread 還會記兩筆
severity: minor
blocking: 否
引句:「閘名沿用 `note-audit`(已在 `_KNOWN_GATES`,事件種類不用登記)」
file: `scripts/lumos:26127`
1. `_note_audit_resolve` 碰到淺層 clone 會記 `_gate_event_or_warn(root, gate, "skipped-env", …)`(26111),起點回 None(頂端已在主線)會記 `(gate, "skipped", why)`(26127)。gate 參數照 spec 就是 `note-audit`。
2. 筆記內容審自己的 `skipped` 事件是 `note-audit skip` 子指令「略過 N 行」寫的(26585),`skipped-env` 是 `LUMOS_SKIP_NOTE_AUDIT`。reread-check 每次推送走到這兩條路,都會往筆記內容審的事件流裡多寫一筆同名事件。第 4 節又要求另記 `reread-skipped`,同一件事就記了兩筆。
3. 筆記內容審的 REVISIT(2026-11-27)要用這些事件量;兩週後本案的 REVISIT 要數 `reread-skipped`,也會漏掉只被記成 `skipped` 的那幾次。
4. 建議:呼叫 resolve 時傳自己的 gate 字串,或讓 resolve 回傳原因、由 reread 只記 `reread-skipped`。S6 驗事件時一起釘住。

## F6 抽出來的共用函式如果把「頂端讀不到的丟掉」搬進去,存量漂移那條嚴格路徑的行為會變
severity: minor
blocking: 否
引句:「`git log --name-only -z -M`,改名取新路徑、頂端讀不到的丟掉」
file: `scripts/lumos:25839`
1. 現行 `_notes_status_flipped` 在 25839-25844 那幾行只做 `git log --format= --name-only -z -M <範圍> -- <vault>`,再篩 `.md`。「頂端讀不到」是後面 `_note_flipped_one` 裡 `reader(p)` 處理的,而且分兩種:strict(存量漂移守衛)時讀不到回 None,整道「判不了」;不嚴格時當成沒翻轉。
2. spec 把「頂端讀不到的丟掉」寫成要抽出的那幾行的一部分。照字面把丟棄放進共用函式,strict 路徑上批次讀失敗(不是刪檔)就會從「判不了」變成「靜靜丟掉」。那是代碼審 r3、r4 修過的方向。S12 只說「行為不變」,沒說要覆蓋讀取失敗這個分支。
3. 建議:寫明共用函式只回「碰過的 .md 路徑(改名取新)」,丟棄由 reread 自己做;S12 補「strict 且 reader 回 None 時 `_notes_status_flipped` 仍回 None」。

## F7 掛鉤「回傳值不看」,漏掉其他每道檢查都有的訊號中斷處理
severity: minor
blocking: 否
引句:「之後加一段,參數照它;回傳值不看」
file: `scripts/hooks/pre-push:479`
1. pre-push 裡每支 lumos 檢查的回傳碼都先過 `pp_stop_if_signaled`(348、360、398、425、479):128 以上代表被 Ctrl-C 中斷,整支掛鉤停下,不往下跑 8 分鐘的全套測試。
2. 照字面「回傳值不看」寫成 `… || true`,使用者在 reread-check 時按 Ctrl-C,掛鉤會繼續往下跑全套。
3. 建議改成「只看 128 以上(照 `pp_stop_if_signaled`),其他非零照放行」。S8 可以順便用文字比對釘住。

## F8 改名舊路徑的 pathspec 來自已經轉成 NFC 的 `_nodehome_changes`,NFD 存的檔名會查不到
severity: minor
blocking: 否
引句:「這次被改名的檔把舊路徑一起放進 pathspec(用第 1 節 `_nodehome_changes` 算出的新舊對照)」
file: `scripts/lumos:23932`
1. `_nodehome_changes` 對每個路徑套 `nfc()`,家對照的鍵也是 NFC。拿這些路徑去給 `git diff … -- <pathspec>`,如果樹裡存的是 NFD(macOS 上用某些工具建的中文檔名),pathspec 對不到,那支檔的 diff 會是空的。
2. 這是踩過的坑:`_nodehome_name_status` 的 docstring 寫「norm=False 保留 git 原樣路徑(要拿去 git 查的呼叫端用;筆記形狀擋驗收輪:NFC 過的路徑對 NFD 樹查不到)」。
3. 建議:寫明 pathspec 用 git 原樣路徑(norm=False 那條),比對家時再轉 NFC。

## F9 record 用哪一版筆記驗行號、取「當時的全文」沒寫;`line: true` 會被當成整數
severity: minor
blocking: 否
引句:「每一項 `line` 不是整數或超出筆記行數的,那一項丟掉並印原因,其餘照收」
file: `scripts/lumos:26272`
1. 「筆記行數」與紀錄檔裡「那一行當時的全文」應該取項目檔裡那份帶行號的終點全文。spec 沒寫來源。照慣例讀工作目錄或 HEAD 的話,作者照判定改過筆記(或提交了別的改動)之後才 record,行號範圍與「當時的全文」都會錯位。
2. Python 的 `isinstance(True, int)` 為真,`{"line": true}` 會被收成第 1 行。「不是整數」要明寫排除 bool。
3. 行數的算法要跟編號一致。實驗的 `numbered` 用 `text.split("\n")`,檔尾換行會多出一個空的最後一行;用 `splitlines()` 則會在 ` `、`\x0c` 這類字元多切,跟「跟檔案行號一致」不符。
4. 建議:寫明 record 從項目檔取筆記全文與行數、行號用 `split("\n")` 口徑、bool 不算整數。S5 補這三個案例。

## F10 `{{trunc}}`、`{{others}}` 要填什麼沒定義,正式範本的材料跟量過的不同
severity: minor
blocking: 否
引句:「正式範本把 `{trunc}` 這類佔位字改成 `{{trunc}}`(JSON 範例的單大括號不動)」
file: `governance/eval/home-check/validate/scripts/vcommon.py:138`
1. 實驗裡 `{trunc}` 不是空字串:有補測試檔時填「,另加同套件目錄裡沒有家的測試檔(…)」,有截斷時填「(原始 diff N 字元,超過 100000 上限:上下文縮成 k 行…,截掉處有註明)」。`{others}` 沒有時填「無」,超過 40 支時填「…等共 N 支」。沒有要放的 diff 時 `{diff}` 填「(無)」。
2. spec 只講要列 40 個檔名、要在截斷處註明,這幾段填入字串沒寫。實作者可能把 `{{trunc}}` 留空,判定者就不知道 diff 裡混了補進來的測試檔、也不知道被截過。這會動到 S10 要保住的「量過的問法」,也讓 S3 的「等於範本一次填入的結果」測不到填的內容對不對。
3. 建議:把這四個填入字串照實驗逐字寫進第 2 節,S3 釘住。

## F11 S6 列的回 0 情況漏了「推送參數只給一個」,照存量漂移那支抄會回 2
severity: minor
blocking: 否
引句:「範圍格式錯、終點找不到、起點算不出、git 失敗時應印原因並回 0」
file: `scripts/lumos:28842`
1. spec 要求呼叫方式照存量漂移檢查。`cmd_drift_check` 在 `--push-remote`、`--pushed-ref` 只給一個時直接 `return 2`(28839-28842)。照抄就違反第 4 節「任何情況都回 0」,S6 列的情況又沒包含它,測試不會紅。
2. 另外還有沒預期到的例外(Python traceback,rc1)也不在列舉裡。掛鉤不看回傳碼、CI 有 `|| true`,所以沒有實害,但條款跟文字不一致。
3. 建議:S6 改成「任何參數組合與例外都回 0」,並列入這一種。

## F12 指紋對 git 的 diff 設定敏感,CI 與本機算出的會不同
severity: minor
blocking: 否
引句:「對每篇算當下的項目指紋,看被推頂端提交的樹裡」
file: `scripts/lumos:23909`
1. 指紋含 diff 全文雜湊。`git diff` 的輸出會隨使用者設定變:`diff.algorithm=histogram`、`diff.mnemonicPrefix`、`diff.noprefix`、`diff.renameLimit`、外部 diff 驅動、textconv 都會。作者本機 `~/.gitconfig` 有其中任一項,本機 prepare 的指紋跟 CI(預設設定)重算的就不同。CI 那步會把每一篇已經對照過、也提交了紀錄的都列成「沒對照」。
2. 建議:寫明組 diff 時固定參數(`--no-ext-diff --no-textconv --no-color --diff-algorithm=myers --src-prefix=a/ --dst-prefix=b/`,或 `-c` 蓋掉相關設定)。S3 或 S6 補一條「設了 diff.algorithm=histogram 時指紋不變」。

## 各節逐一
- 依據、PRIOR-ART、RETIRE-IF、REVISIT:已讀,無 finding(數字與實驗檔對得上;附錄逐字核過)。
- 範圍:已讀,無 finding。
- 做法 1:F1、F3、F4、F5、F6。
- 做法 2:F1、F2、F8、F10、F12。
- 做法 3:F9。
- 做法 4:F4、F7、F11。
- 做法 5:已讀,無 finding。
- 條款:S2(F1、F2)、S5(F9)、S6(F4、F11)、S10(F2 第 4 點)、S12(F6);S4、S7、S8、S9、S11 都能照字面寫成會翻紅的測試,無 finding。
- 回退、實務隱患、誠實界線:已讀,無 finding。

最高等級:major;blocking 共 4 條
