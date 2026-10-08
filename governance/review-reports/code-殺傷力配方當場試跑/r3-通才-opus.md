severity: major

# 殺傷力配方當場試跑 代碼審第 3 輪 通才-opus 席報告

臨時 clone:`trc-r3-work-通才-opus/repo`(HEAD ed16a50f),對照組 `trc-r3-work-通才-opus/repo-r2`(fe722c3c,也就是第 2 輪修正前)。實驗腳本:`trc-r3-work-通才-opus/exp/probe.py`、`probe2.py`(每格一個獨立 repo,照 `_mk_kill_env` 的形狀造)。

## 兩條修正的驗收

- **① `--id` 改用 `_kill_recipe_judge` 判格式壞:判法跟 P2 一致,但「不當掉」這個承諾沒守住(見 F1、F2)。**
  - 跟 P2 一致這件事成立:兩邊呼叫同一支判斷,用的 repo 根在 `docs/<slug>-knowledge` 這種擺法下相同(doctor 取 `docs` 的上一層,`_repo_root_from_env` 也一樣)。我實跑了 test 名不合法、platform 是清單、正式路徑下 old=null 三種:`--id` 擋下(回 2,stdout 空),P2 也列成「配方欄位格式不對」,修法裡的短身分跟擋下訊息裡的一致。
  - 設定檔壞(`{bad`):判斷回 `cfg`、不擋。接著 guard kill 自己讀設定,退回單一預設平台,因為沒有 run_cmd 而擋下,回 2、不當掉,stdout 空。P2 也不列成格式壞,兩邊一致。
  - 平台根找不到(`noroot`)、平台不在設定(`noplat`,含 platform=5):不擋。guard kill 判成 error(回 2)、不當掉,一致。
  - 原文出現 0 次或多次(`hits`):不擋。guard kill 判成 drifted,走不到套壞法,new 不是字串也不會當掉(第 2 輪 ⑥c 那格)。
  - **漏掉的同類:** 判斷遇到 `path`(file 不是提交裡的正式寫法)就停下,不再看 old/new 的型別。可是 guard kill 照字面把檔打開,`./prod.py`、連結、在 macOS 上只差大小寫的寫法都開得到,開到之後碰上 old=null 或 new 不是字串就當掉(F1)。另外,判斷沒考慮合約片段過濾這一步:invariant 不是字串時,帶片段一起跑會當掉(F2)。第 2 輪另寫的那支判法擋得住這兩種,這一輪換成 P2 的判法之後重新打開。
- **② 修正關卡的說明行:修好了。** 知識庫不在 repo 裡時回一行說明;呼叫端把它併進 notes(`--json` 的 notes 陣列也會有),不影響關卡過不過。`t_fix_check_recipe_rerun_note` ③c 綠(7 passed)。順帶一提:這行在專案一條配方都沒有時也會印,但第 2 輪通才席試不出能走到這條路的真實情境,我也沒找到,所以不列 finding。

跑過的測試:`-k guard_kill_only_ids` 14 passed;`-k fix_check_recipe_rerun` 7 passed;`-k guard_kill_json_purity` 6 passed;`-k guard_kill_rc_precedence` 4 passed。

## F1 `--id` 遇到「file 不是正式寫法、old 或 new 型別錯」的配方時不擋,guard kill 當掉、回 1(跟 survived 同碼)
severity: major
blocking: 是
引句:「+        res = _kill_recipe_judge(ctx, r) if rid in want else None」
引句:「+        if res and res["status"] == "malformed":」
file: `scripts/lumos:14177`
file: `scripts/lumos:14185`
file: `scripts/lumos:15172`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方當場試跑_計劃.md:42`
file: `docs/lumos-toolchain-knowledge/Projects/殺傷力配方當場試跑_計劃.md:99`
1. 判斷裡 old/new 的型別放在 `_kill_judge_file` 判完路徑之後才看(14185 行)。file 不是提交裡的正式寫法時,在 14177 行就回 `path`,根本走不到 old/new。這一輪 `_guard_kill_pick` 只擋 `malformed`,所以這條會放行。
2. guard kill 自己不檢查路徑寫法。它用 `os.path.realpath(os.path.join(wt, file))` 把檔打開:`./prod.py`、指向 prod.py 的連結、macOS 上的 `Prod.py` 都開得到,接著在 15172 行 `src.count(r.get("old", ""))` 遇到 None 就當掉。new 是數字時,改在套壞法那行 `src.replace(r["old"], r["new"], 1)` 當掉。
3. 最小重現(`exp/probe.py`,每格一個獨立 repo;配方以外照 `_mk_kill_env`、提交後跑 `guard kill Systems/Limit --id <12 碼> --json`):
   ```
   $ /opt/homebrew/bin/python3 probe.py a_dotslash_oldnull b_dotslash_newint j_oldnull_ok
   === file=./prod.py, old=null: rc=1
     stdout: ''
     stderr: '... line 15172, in cmd_guard_kill\n    cnt = src.count(r.get("old", ""))\nTypeError: count() argument 1 must be str, not None\n'
   === file=./prod.py, new=123: rc=1
     stdout: ''
     stderr: '... line 15179, in cmd_guard_kill\n    _tf.write(src.replace(r["old"], r["new"], 1))\nTypeError: replace() argument 2 must be str, not int\n'
   === old=null 正式路徑(對照): rc=2
     stderr: '擋下:第 1 條配方欄位格式不對(old 不是字串,guard kill 數原文時會程式出錯),跑不了;先 lumos guard kill-rm Systems/Limit --id cc11481a70d1 再重加\n'
   ```
   `probe2.py` 另外驗了 `file` 是連結(`link.py -> prod.py`)加 old=null,以及 `file=Prod.py` 加 old=null:兩格都是同一個 TypeError,rc=1。
   用 fe722c3c(第 2 輪修正前)跑同兩格:`rc=2`,「第 1 條配方格式壞(old 不是字串)」、「(new 不是字串)」,所以這是這一輪換判法帶出來的回歸。
4. 為什麼是 major:
   - old=null 正是既有 Issue 自己的重現,也是第 1 輪 F1(major)點名的形狀。計劃第 42 行承諾「這次只保證 `--id` 不會把人帶進那個崩潰」,S1 寫「對到格式壞的配方時應回 2、印出 kill-rm 指令、不當掉」;這裡只差 file 換一種寫法,就回到 rc 1 加 Traceback。
   - rc 1 對腳本來說跟 survived 分不出來。`--json` 下 stdout 是空的,而 rc 1 正落在 json 純度合約說「恰一行 JSON」的範圍。
   - P2 給這條配方列的是「不是提交裡的正式路徑…修法:kill-rm --id <同一個短身分>」,使用者照短身分改跑 `guard kill --id` 就會撞上。
   - 計劃與 `Systems/guard-kill.md` 都寫「malformed=guard kill 會拒跑或程式出錯的那幾種」,這句跟實際不符:判斷在 `path` 停下時,本來就不預測 guard kill 會怎樣(`_kill_path_issue` 的說明就是這樣寫的)。
5. 建議:別再補判斷的條件(那會變回第二套判法)。改在 guard kill 當掉的那兩行原地擋:old/new 不是字串就把這條記成 `error`(「配方欄位格式不對」)、continue。這樣不管走哪個入口、file 怎麼寫,都不會當掉,`--id` 的承諾也跟著成立;同時要在 `t_kill_recipe_check_matches_guard_kill` 補一格,讓對照測試鎖住這個行為。

## F2 invariant 不是字串的配方,`--id` 加合約片段一起跑時當掉(第 2 輪擋得住)
severity: minor
blocking: 否
引句:「+    格式壞跟 doctor P2、kill-add 提醒同一套判法(_kill_recipe_judge 判 malformed=guard kill 會拒跑或程式出錯;」
file: `scripts/lumos:15052`
1. `_kill_recipe_judge` 不看 invariant(第 2 輪 ⑥c 故意讓缺 invariant 的配方照跑)。可是 `--id` 之後還有合約片段那一步 `invariant_substr in r.get("invariant", "")`,invariant 是數字或 null 時會丟 TypeError。
2. 重現(`exp/probe2.py`):配方 `invariant: 5`,跑 `guard kill Systems/Limit 上限 --id <12 碼>` → rc=1,`TypeError: argument of type 'int' is not a container or iterable`(15052 行)。fe722c3c 的判法(invariant 不是字串就擋)在這裡會回 2。
3. 定成 minor 的理由:不帶 `--id`、只給片段,一樣會當掉,屬既有 Issue 的範圍;要同時給片段和 `--id` 才碰得到。修法可以跟 F1 同一處一起做:片段過濾改成 `isinstance(r.get("invariant"), str) and …`,或只把不是字串的那條記成 error。

## 走過、沒發現問題的路徑

- `--json` 下的擋下路徑(格式壞、對不到、多條、設定壞):訊息全在 stderr,stdout 空。`_kill_cfg_load` 把 load_platforms 的警告收走了,`_kill_plat_top`、`_kill_tree`、`_kill_read_blob` 的 git 都用 `capture_output`,沒有印到 stdout 的路徑。
- 判斷裡的 git 每次呼叫上限 10 秒,一次判定最多四次呼叫。逾時算 `noroot`、不擋,guard kill 照常往下跑;不會卡住,也不會當掉。
- 設定檔頂層是清單(`[1]`):guard kill 本身在 `load_platforms` 當掉(AttributeError)。帶不帶 `--id` 都一樣,改動前就有,不算這輪的問題。
- 配方指到非 UTF-8 檔:判斷回 `undecodable`、不擋,guard kill 讀檔時丟 UnicodeDecodeError 當掉(rc 1)。帶不帶 `--id` 都一樣,改動前就有,而且不是配方格式的問題;P2 本來就有列這條、給了修法。改動前就有,不另列;如果照 F1 第 5 點在當掉處原地擋,建議順手把讀檔那段的 except 擴到 `ValueError`。
- `_guard_kill_pick` 不像 P2 那樣把判斷包進 try:我找不到能讓判斷丟例外的配方輸入(platform 不可雜湊、file 含 NUL、平台根含 NUL 都先被前面的檢查接住),不列。
- `--platform` 覆寫:判斷用預設平台,guard kill 用覆寫的平台,兩邊可能判的不是同一個 repo 根。P2 也沒有覆寫,「P2 判 malformed ⇔ `--id` 擋」不受影響;會當掉的組合要多平台,而且還得疊上 F1 那種形狀,修了 F1 就一起消失,不另列。

## 固定席(LUMOS-IMPACT fe722c3c..ed16a50f)

派工尾端沒附固定席筆記,我自己跑了 `lumos impact --diff`:26 篇固定席,外加 top 8。

- `Systems/guard-kill.md` 的兩條 ★INVARIANT★:
  - rc 優先序:新的擋下發生在跑任何配方之前,回 2 早退,沒動結果的優先序。`t_guard_kill_rc_precedence` 4 passed。
  - `--json` 純度:擋下的路徑 stdout 空,屬於明文排除的 rc 2 早退範圍,`t_guard_kill_json_purity` 6 passed。但 F1 的當掉路徑是 rc 1、stdout 空,剛好落在這條合約要「恰一行 JSON」的範圍。所以 F1 也算碰到這條合約的邊,修 F1 就一起解決。
- `Systems/bound-tests-gate.md`、`測試假綠形態`、`授權與歸屬`、`lumos-cli-read`、`lumos-cli-lifecycle`、`design-loop`、`canary-audit`、`slim-*`、`lumos-deinit`、`check-t-sentinel`、`check-r-guard`、`cochange-guard`、`pitfalls-code-loop`、`loop-convergence-recording`、`reversibility-governance-ledger`、`節點範圍與索引守衛`、`doctor-irreversible-hint`、`lumos-refcheck`、`core-invariant-baseline`、`judge-severity-gate`,以及三篇守衛面計劃:都只是因為共用 `scripts/lumos` 與 `scripts/test_lumos.py` 這兩支大檔才被帶進來。這一輪只改 `_guard_kill_pick`(加上刪掉 `_kill_recipe_shape_bad`)、`_fix_recipe_rerun_notes` 的一行回傳值、測試與筆記,碰不到它們的合約內容(檔頭、白名單、搜尋隱藏規則、審查帳寫入、閘的判定)。未發現破壞。
- `Systems/代碼審修正關卡`(② 的家):說明行只進 notes,不影響過不過、不寫事件欄位,跟「只提醒」的宣稱一致。

最高等級:major,blocking 共 1 條
