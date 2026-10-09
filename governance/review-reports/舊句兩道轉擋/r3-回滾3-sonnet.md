severity: major

未附固定席節點,不適用。

先說回退面查到的:前進式 v1.4 撤回是退得掉的,留下的資料也不會弄壞舊版。
- `_version_nudge` 只在來源版本較新時提示(file: `scripts/lumos:22296`,`ct >= st` 就回 None),所以 v1.4 會讓已更新到 v1.3 的專案收到提示,不倒回 v1.2 的判斷成立。
- CHANGELOG 守衛只比第一個標題與 `LUMOS_VERSION`(file: `scripts/test_lumos.py:8357`),加 v1.4 段、保留 v1.3 不會紅。
- 我在 /tmp 的 clone 裡塞了一筆 `kind=reread` 帶 `verdicts` 的表態,用現有舊工具跑 `drift scan`、`drift check`、`doctor`,都沒崩。`_drift_load_acks` 確實只收 `_DRIFT_KINDS`(file: `scripts/lumos:37232`)。
- 新增的治理帳 `blocked` 事件不會讓舊版出事。

被誤擋當下的四條出路:
- 改句:可走。會讓已過的代碼審留痕失效,spec 已承認。
- `drift ack`:可走。表態檔在簿記白名單(file: `scripts/lumos:26898`),提交它不會作廢留痕。單行 summary 的條目走不通,見 F7。
- `LUMOS_SKIP_REREAD_CHECK`:可走。環境變數在掃描前就讀(file: `scripts/lumos:34912`)。`skipped-env` 不在本機帳白名單(file: `scripts/lumos:1363`),所以會進版控治理帳,「會留帳」成立。
- 設定改 warn:可走。設定從被推頂端讀(file: `scripts/lumos:34941`),`.lumos/config.json` 在這個 repo 有被追蹤。
- RELEASING.md 本來就規定發版推 `main:release` 要 `--no-verify`,所以新掛鉤不影響發版與撤回的發佈步驟。

## 實務隱患逐類
- 金流:無。只有判定者的呼叫成本,不碰付款或計費。
- 不可逆:無新增。帳是只增不減,表態檔舊版會略過。發版本身不可逆(RELEASING.md 已寫),所以 spec 用前進式 v1.4,這一點是對的。
- 對外送出:無新增。check 本身不送資料,送出發生在人手動 prepare 與派判定者那一步。spec 已列為風險並給 warn/off 出路。
- 守衛面:有,見 F1、F3、F6、F7。
- 並行會談:有,併入 F1。

### F1 對照指紋含頂端程式 blob,本機推送在 rebase 或合過主線後一樣整批作廢,「本機只看增量」的前提不成立
severity: major
blocking: 是
判準:spec 用「本機只看增量」排除 CI 才有的合併誤擋,並以此取得人裁「接受第一層成本」。這個前提在合過主線或 rebase 後為假,第一層的成本與 RETIRE-IF 第一條的基準都會偏掉。
- spec 段落:〈開關〉重讀那條,與〈候選與兩層〉第一層。
- 引句:「兩邊候選與指紋都不同,設計審前兩輪找到的 CI 誤擋情境(合併讓指紋變、分次推送、兩個分支各自表態)都出在這裡」
- 引句:「程式改了(含合併主線帶進別人對同一支程式的改動、筆記改名、about_code 增減)就要重判」
- 場景:
  - 兩個並行會談(使用者全域規則就是這樣用)共用一個 repo。會談 A 對 10 篇守檔筆記派判定者、記錄、提交。
  - 這時會談 B 先把改到 `scripts/lumos` 的提交推上主線。A 做 `pull --rebase` 或把 main 合進分支,再推。
  - A 的範圍起點不再是遠端舊值。`_push_pick_base` 在分岔點不是舊值祖先時,改取跟主線的分岔點,範圍變成整段分支累計(file: `scripts/lumos:44793-44815`)。
  - 對照指紋用的是頂端 blob(file: `scripts/lumos:34459-34469`),B 的改動讓 A 那 10 份紀錄全部對不上,要重判。判定者要跑幾分鐘,這段時間 B 或 C 再推就再作廢一次,A 只能走略過或 warn。
- 查證:我在 /tmp 的 clone 對範圍 `HEAD~15..HEAD` 跑 `reread-check`,`lumos-cli-read.md` 的指紋是 `b2f7df8160b420fe`。我在頂端多加一個「別人只動 `scripts/lumos`」的提交後,同範圍同筆記變成 `ba1696d18d7d0038`。
- 缺口:spec 〈原問題〉自己寫了「主程式被約 70 篇筆記認領、幾乎每個提交都改」,但〈開關〉的理由沒把這件事算進本機推送。
- 建議:把「本機=增量」改成實際行為並重估第一層成本,或在 RETIRE-IF 第一條加量「rebase 或合併後重判」的次數。
- 備註:spec 排除了「改指紋組成」,所以不能直接改指紋。

### F2 回退清單漏了新測試與計劃自己的收尾,退完會留下懸空綁定與過期提醒
severity: minor
blocking: 否
判準:照回退節做完,doctor 會唸懸空,不會擋推送。
- spec 段落:〈回退〉,對照〈驗收條款〉與 REVISIT。
- 引句:「改過斷言的既有測試、被改寫的筆記條款(含標 superseded 的 RULE)」
- 引句:「REVISIT:2026-12-04 上線滿 8 週照 RETIRE-IF 四條量」
- 場景:
  - 回退只談「改過斷言的既有測試」,沒說新增的 `t_reread_block_layer1`、`t_reread_block_layer2`、`t_reread_block_undecidable`、`t_reread_block_hook_and_ci_wiring`、`t_old_sentence_default_follows_gate`、`t_drift_ack_reread_kind` 怎麼辦。
  - 留著它們會紅;刪掉它們,本計劃 S1 到 S24 的 `[test:]` 就指不到。這個 repo 的筆記測試綁定要存在,推送時對碰到的筆記開擋(Projects/筆記測試綁定要存在_計劃)。
  - 計劃本身的 status、`lands_in`,以及 2026-12-04 的 REVISIT 也沒交代,退回後 doctor 仍會到期唸「量已不存在的閘」。
- 佐證:舊工具能容忍殘留資料(見上方查到的)。問題只在筆記面。

### F3 〈開關〉要改 CI 的 drift 逃生句,卻又寫「CI 步驟指紋照舊」,兩處互相矛盾
severity: minor
blocking: 否
判準:照字面做會讓 `t_ci_yml_matrix_and_gates_shape` 翻紅,spec 的待改測試清單沒列。
- spec 段落:〈開關〉末尾「連帶改」,與〈實務隱患〉待改測試清單。
- 引句:「推送前掛鉤與 CI 那兩處」
- 引句:「CI 那一步不改,`t_ci_yml_matrix_and_gates_shape` 的步驟指紋照舊」
- 查證:
  - CI 的 drift 步驟指紋涵蓋整段 `run:`(file: `.github/workflows/ci.yml:242` 的 echo 在 run 內,file: `scripts/test_lumos.py:62209` 的 `_DR_CI_GATE_STEP_FP`)。改那句會讓 drift 步驟指紋紅。
  - 實際只有 `scripts/hooks/pre-push:516` 寫了「改 gate 沒用」。CI 那句寫的是「改的是 drift_check.old_sentence」,新語意下只是不完整,不是錯。
- 建議:不要改 CI 那句,或明說同步更新該指紋。

### F4 升版只寫 CHANGELOG,漏了紀律區塊戳記重注入;v1.3 與 v1.4 兩次升版都會踩
severity: minor
blocking: 否
判準:推送前全套會紅,修法是跑 `lumos update` 重注入。
- spec 段落:〈原問題與範圍〉⑧,與〈回退〉。
- 引句:「`LUMOS_VERSION` 升 v1.3、CHANGELOG 加同版一段」
- 引句:「CHANGELOG 加 v1.4 撤回段,不刪 v1.3」
- 查證:`t_discipline_block_stamp_matches_version` 要求本 repo 的 CLAUDE.md 與 AGENTS.md 的紀律區塊戳記等於 `LUMOS_VERSION`(file: `scripts/test_lumos.py:65515`)。兩處都沒列重注入。

### F5 〈回傳碼與判不了〉三分類沒覆蓋幾個現有的停下點,字面實作會變成放行
severity: minor
blocking: 否
判準:fail-open 與 fail-closed 在這幾處靠實作者猜。
- spec 段落:〈回傳碼與判不了〉,與〈候選與兩層〉最後一條讀取判定紀錄。
- 引句:「判不了(`undecidable`、逾時、判定紀錄讀不了或讀不懂、沒預料的例外)」
- 引句:「總量超過時印最大的五份檔名」
- 場景 1:現有 `_NoteRereadStop` 還會從這幾處丟出,spec 沒指明歸哪類:
  - 起點算不出來(file: `scripts/lumos:34959`)。
  - 列不出已提交紀錄(file: `scripts/lumos:34972`)。
  - `_note_reread_scan` 內的各種 git 失敗(file: `scripts/lumos:34383-34430`)。
  - 它們不是「未預料的例外」,也不是三類之一。放行會讓 hook 說「這次沒檢查」。
  - 對照 `_push_range_start` 的文件(file: `scripts/lumos:44706-44707`):起點 UNKNOWN 要「照判不了」。drift check 也這樣處理。
- 場景 2:`_nodehome_cat_blobs_capped` 只回 bytes 或 None,不回大小(file: `scripts/lumos:29495-29524`)。超過上限的檔(單檔超過或總量超過後被跳過的)都是 None。
  - 要印「最大的五份檔名」得另外呼叫 `_nodehome_cat_sizes`。
  - 總量超過時哪些檔被跳過取決於順序,不是最大的那幾份。

### F6 第一層「只認來源核對過的紀錄」,但 record 的「照收」訊息與擋下訊息都沒改,人會原地打轉
severity: minor
blocking: 否
判準:有出路(重 prepare、略過、warn),但訊息誤導。
- spec 段落:〈候選與兩層〉「已對照」口徑,與〈輸出〉。
- 引句:「所以只有來源核對沒過的紀錄時,check 擋、prepare 也會重產項目檔」
- 場景:
  - 判定者報告開頭四行抄錯,`reread-record` 印「照收,紀錄標 provenance_ok: false」(file: `scripts/lumos:34878-34881`)。
  - 人提交後推送,被擋,訊息仍是「還沒對照」,看不出紀錄在但不算數。
  - 〈要一起改的說法〉只改 record 收尾那句,沒改這句「照收」。若 Codex 編排系統性對不上開頭四行,會變成無限循環。

### F7 `drift ack --kind reread` 照 retire 的行號檢查,但第二層用的是含單行 summary 的讀法,兩邊不一致
severity: minor
blocking: 否
判準:單行 summary 的規則類條目會被擋、卻無法表態,仍可改句、略過或改 warn。
- spec 段落:〈照留表態〉,對照〈候選與兩層〉的 `_note_summary_entries`。
- 引句:「行號要是一條摘要條目的開頭行(跟 retire 一樣,記整條)」
- 查證:
  - 第二層用 `_note_summary_entries`,它補了單行 summary(file: `scripts/lumos:4027-4037`)。
  - retire 的行號檢查走 `_ns_summary_logical`,沒有單行 summary 的補法(file: `scripts/lumos:37457`、`31963`)。
  - 單行 summary 的條目會被擋下,但 `drift ack` 回 2「不是摘要裡一條的第一行」。

## 各節狀態
- 〈原問題與範圍〉:已讀,無 finding。帳上數字我重算過,18 次 reminded、none 12、recorded 5、合計 47 篇、18 次皆「已對照 0 篇」,都對。
- 〈開關〉名稱消失檢查:已讀,無 finding。`_drift_retire_config` 有同型先例。
- 〈輸出〉:已讀,無 finding。
- 〈對消費專案的影響〉:已讀,無 finding。CI 不帶 `--gate`、恆回 0,所以不會讓消費專案 CI 變紅。
- 〈驗收條款〉:已讀,無 finding。
- 審計修正紀錄:已讀,無 finding。

最嚴重的是 F1(本機指紋含頂端程式 blob,rebase 或合過主線後整批作廢,「本機只看增量」的前提不成立);blocking 共 1 條。
