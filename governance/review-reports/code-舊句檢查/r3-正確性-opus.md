severity: major

# 舊句檢查 代碼審 r3:正確性-opus

實驗環境:`git clone --shared` 到 `scratchpad/r3c/repo`(翻紅用)與 `repo2`(實驗用),HEAD e6725219(含 89884251),直譯器 /opt/homebrew/bin/python3(3.14.6)。`-k m1_review_r2` 23 條斷言全綠;鄰居子集 `-k trusted/private/vault_lock/dispatch_lens/bound_filter/umask/doctor_drift` 全綠。

## F1 任何一篇沒改到、跟消失名稱無關的筆記裡有一行超過 2 萬字,block 下所有刪名稱的推送都被擋,而且不講是哪一篇哪一行
severity: major
blocking: 是
引句:「return bool(handle) or res["state"] in _DRIFT_M1_UNKNOWN or bool(res.get("long_lines"))」
file: `scripts/lumos:29239`
file: `scripts/lumos:29488`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:86`

1. `long_lines` 在 `_drift_m1_scan_note` 裡對整份圖譜每一篇、每一行可見的正文都計數(`scripts/lumos:29239`),不看那篇有沒有在這次範圍裡改到、也不看那一行有沒有可能提到任何候選名稱。r2 把它接進「有東西」之後,只要候選名稱大於 0,一行無關的長行就讓 block 擋下。
2. 重現(`scratchpad/r3c/exp1.py`):old_sentence=block;`Systems/Table.md` 有一行 `| 資料 | …` 共 3 萬多字、完全沒提 `old_func_x`;`Systems/A.md` 只寫「講別的事」;這次推送只刪 `src/a.py` 的 `old_func_x`。輸出:
   ```
   E1 rc 1
   擋下:舊句檢查:這次消失 1 個名稱;有 1 行太長沒看(超過 20000 字),看得到的行沒有提到
     判不了:舊句檢查有 1 行超過 20000 字沒看(把那幾行拆短就能判)——…
   {'kind': 'blocked', 'state': 'done', 'handle': 0, 'listed': 0, 'long_lines': 1, 'candidates': 1}
   ```
   之後每一次刪掉任何一個過形狀過濾名稱的推送都一樣擋,直到有人把那篇的長行拆掉或每次單次略過。
3. 這跟計劃自己在讀不出的筆記上定的規矩相反:「這次範圍改到的算判不了;沒改到的只印…(不然一篇壞筆記會讓 block 的專案永遠推不動)」(`舊句檢查_計劃.md:86`)。r2 資安-F1 要堵的是「把舊句補到 2 萬字藏起來」,需要的條件是那一行真的可能提到消失的名稱;現在的判法把「整份圖譜任何地方有長行」也算進去。
4. 擋下的訊息(`scripts/lumos:29488`)只說「有 N 行超過 20000 字沒看(把那幾行拆短就能判)」,沒有筆記路徑與行號;帳的 rows 也是空的(handle 0)。被擋的人要自己在整份圖譜裡找哪一行超過 2 萬字。
5. warn(預設)下同一個情況每次有候選的推送都印「提醒:」、帳記 `warned`,兩週回頭數要處理量時會混進這種跟舊句無關的事件。

## F2 路徑帶控制字元(tab、ESC 等)的筆記照樣印可照貼的表態指令,印出來控制字元已換成空白,照貼找不到那篇筆記
severity: minor
blocking: 否
引句:「if kind == "m1" and _drift_c4_show_name(path) != path:」
file: `scripts/lumos:28185`
file: `scripts/lumos:27855`

1. 「不印可照貼指令」的條件只看 `_drift_c4_show_name` 會不會改動路徑,而那一支只換 Cf(方向控制、零寬)與非 UTF-8(`scripts/lumos:28185`),不管 Cc 控制字元。指令接著在 `_drift_print_hints` 過 `_esc_clean`(`scripts/lumos:27855`),Cc 被換成空白。修法宣稱的「印出來的樣子跟實際檔名不同,照貼也找不到」在這一類輸入上照樣成立,只是沒被擋掉。
2. 重現(`scratchpad/r3c/exp2.py`):筆記 `Systems/a\tb.md` 寫「呼叫 gone_tab_x。」,推送刪 `gone_tab_x`。改法印:
   `lumos drift ack 'Systems/a b' 6 --kind m1 --name=gone_tab_x --reason "<為什麼照留>"`
   把理由換掉照貼 → rc 2「擋下:圖譜裡找不到叫「Systems/a b」的筆記」。如果圖譜裡剛好有 `Systems/a b.md`,表態會寫到另一篇(m1 表態不驗那一行真的是 m1)。
3. 這篇是家筆記時是要處理層,block 下被擋、照貼的出路不通,也不會像 Cf 那種一樣看到「先把檔名改掉再推」。

## F3 剖不動、文字抽定義那一行的程式檔路徑沒走 `_drift_c4_show_name`,方向控制字元原樣印到終端
severity: minor
blocking: 否
引句:「m1 印到終端的路徑、原文、說明走 c4 證據頁那支 `_drift_c4_show_name`」
file: `scripts/lumos:29348`

1. r2 資安-F3 的修法只套在列出的發現(`_drift_m1_show_row`)與改法;`_drift_m1_print_extra` 印的程式檔路徑仍用 `_drift_m1_show`(只換控制字元與非 UTF-8,不換 Cf),計劃那句「m1 印到終端的路徑…走 `_drift_c4_show_name`」在這一行不成立。
2. 重現(`scratchpad/r3c/exp2.py` E3):`src/x‮y.py` 起點定義 `gone_rlo_x`、終點改成剖不動的 `def (:`。輸出:
   `'舊句檢查:這次改到 1 支程式檔,沒有名稱消失\n  1 支剖不動、0 支用文字比對:src/x‮y.py\n'`,`"‮" in out` 為 True。
3. 同一類的還有 error 狀態結論行裡的例外訊息(`_drift_m1_show(res.get('error'))`),例外訊息帶檔名時一樣不轉義。

## F4 超長行的計數在時間到、git 失敗、讀不出、出錯四種狀態下完全不印了,計劃還寫著「結論行下面印」
severity: minor
blocking: 否
引句:「結論行下面印「N 行超過 20000 字沒掃」」
file: `scripts/lumos:29345`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:82`

1. r2 把 `_drift_m1_print_extra` 裡的「N 行超過 20000 字沒掃」刪了,改成只在 done 的結論行後面接 `_drift_m1_long_note`,block 的原因句又用 `elif`,排在判不了的後面。所以狀態是 timeout、git-failed、unreadable、error 時,終端上沒有任何地方提到有幾行沒看。
2. 重現(`scratchpad/r3c/exp4.py`):一篇筆記有一行 20001 字、掃完那篇之後讓時間到。`state timeout long_lines 1`,warn 的整段輸出只有
   `'提醒:舊句檢查:這次沒跑完(時間到,30 秒)(drift_check.old_sentence=warn,不擋)\n'`。
3. 計劃〈做法〉1 時間那段(同一段 r2 改寫過)仍寫「、結論行下面印「N 行超過 20000 字沒掃」」,跟現在的程式對不上(done 時講的是結論行裡的「有 N 行太長沒看」,其他狀態不講)。

## F5 old_sentence 寫成 block 的專案,doctor 每次都多一段 ⚠ 軟提醒,只有把開關改弱才消得掉
severity: minor
blocking: 否
引句:「寫錯值(含設定檔壞掉)、寫了 off、寫了 block 各一句;預設的 warn 不唸」
file: `scripts/lumos:29638`
file: `scripts/lumos:1318`
file: `scripts/lumos:3199`

1. `_drift_old_sentence_doctor_lines` 對 `old_sentence=block` 回一行;doctor 把這一段每一行都以 ⚠ 印出並加進 `_top_soft`(`scripts/lumos:1318`),收尾行因此永遠多「另有 1 段、共 1 條提醒沒算進上面那個數字」(`scripts/lumos:3199`)。
2. 實跑 47 種設定組合(`scratchpad/r3c/exp3.py`):`{"drift_check": {"old_sentence": "block"}}` → doctor 行 `['這個專案的舊句檢查是 block(drift_check.old_sentence)——…推送會被擋']`;同一支 gate 的規矩是「只在自己寫了 warn/off、或設定寫壞時才唸」,寫最嚴格的 block 不唸;node_home 也是「不是 on」才唸。old_sentence 是唯一一個「選了比預設更嚴」也會掛 ⚠ 的開關,專案要拿到沒有提醒的 doctor 只能把舊句檢查調回 warn。
3. 其餘 46 種組合(沒設定檔、JSON 壞、非 UTF-8、drift_check 不是物件、gate 與 old_sentence 各自 缺/block/warn/off/寫錯/null/非字串)兩個開關各講各的,都符合計劃;這條只針對 block 那一句。

## 查過成立的(不是 finding)

- 還原翻紅(`scratchpad/r3c/mut.py`,每次改完清 `__pycache__`,跑 `-k m1_review` 共 61 條):計劃列的翻紅全紅——不帶 O_NONBLOCK(③卡住被 alarm 殺)、改法照印指令、印出不經 `_drift_m1_show_row`、「有東西」不算超長行、桶裡不看時間、建索引不看時間、入口不經 `_drift_m1_guarded`(EXCEPTION entry-boom)、doctor 拿掉 old_sentence 那行(5 條紅)。mkdir 不給 0700 與拿掉 chmod 兩個一起還原 → 紅。
- 還原了仍全綠(沒被釘,但我給不出會出事的輸入,所以不列 finding):只拿掉 `_mkdir_private_layer` 的 `_chmod_no_follow`(`mkdir(mode=0o700)` 在任何 umask 下已經是 0700,這一步本來就多餘);只拿掉 `mode=0o700` 保留 chmod;名稱先篩兩處的截止時間檢查;沒有 ASCII 段那一桶的截止時間檢查;留痕的 `S_ISREG` 判斷(沒有讀端的 FIFO 在 O_NONBLOCK 開檔時就 ENXIO,輪不到它)。
- `_mkdir_private_layer`:既有的連結、既有的一般檔 → FileExistsError 回 True,交下面 `is_symlink`/`is_dir` 擋掉;建完被換成連結 → `_chmod_no_follow` 用 O_NOFOLLOW 開失敗回 False。umask 002 全新家目錄下 vault-lock、dispatch-lens、bound-filter、drift-defs、drift-m1 都建得起、每層 0700。既有 0775 的 `~/.cache` 照樣不信(快取與留痕都不可用),這是 r2 裁定接受的範圍,不重報。
- 入口兜底:warn 回 0、block 回 1、帳 state error;m1 擋下時多印改 `drift_check.old_sentence` 的逃生句,推送前掛鉤與 CI 的固定句也補了。
- 超長行 done 狀態:要處理 0/只列出 0、要處理 0/只列出 N、要處理 N 三種結論行都帶「有 N 行太長沒看」;帳 kind 照 warned/blocked、state done、handle/listed 照記整數,跟計劃〈代碼審 r2 折入〉的自述一致。

## 圖譜鏡頭逐條判定

- Systems/lumos-cli-read(search 預設排除 superseded、不排除 stale):這次沒碰 search 與過濾順序,不影響。
- Systems/bound-tests-gate(code-loop check 逐支真跑綁定測試,紅/懸空/證不出跑過就擋):這次只動到 bound-filter 快取目錄的建法(新建層改 0700),快取寫不進時本來就是 `except OSError: pass` 盡力而為,不改判定與回傳碼;`-k bound_filter` 9 條綠。不影響。
- Systems/guard-kill(rc 優先序、--json 純度):沒碰 guard kill,不影響。
- Systems/授權與歸屬(授權檔不得進 _VENDORED_TOOLKIT;主程式檔頭 SPDX+MIT):這次沒新增被複製的檔、沒動檔頭與白名單,不影響。
- Systems/測試假綠形態(還原翻紅釘要配前置斷言):r2 新測試裡 long_lines、bidi、budget 三支有明寫「①前置」;entry_guard 用「輸出含 entry-boom」證明走到兜底;strict_home_dirs ③ 的前置(那個位置真的是 FIFO、目錄過了信任檢查)只寫在失敗訊息裡、沒有斷言——單看這支,如果目錄檢查先失敗,③ 會因為 ok is False 空轉變綠;但同一個檔的 r1 測試 ① 有「全新家目錄留痕寫得進去」的正向對照,而且我實跑拿掉 O_NONBLOCK 確實翻紅,現況沒有破壞這條合約。
- Systems/lumos-cli-lifecycle(re-inject 只覆蓋 sentinel 之間):沒碰注入,不影響。
- Systems/design-loop(處置閘第五步):沒碰 loop status/處置閘,不影響。
- Systems/pitfalls-code-loop(RISK):沒碰 pitfalls 分級,不影響。
- 超出上限只列名的那些節點(loop-convergence-recording、reversibility-governance-ledger、節點範圍與索引守衛、lumos-deinit、check-t-sentinel、cochange-guard、check-r-guard、doctor-irreversible-hint、lumos-refcheck、canary-audit、slim-*、雙向門放行、規格落成可驗收條件、逃逸自動記、core-invariant-baseline、judge-severity-gate):這輪的改動範圍是 `_trusted_private_dir`/`_mkdir_trusted_under_home` 共用函式、m1 本身、doctor 的存量漂移那段、pre-push 與 CI 的一句逃生文字;它們之中只有 doctor 那段跟 doctor-irreversible-hint 同在 doctor 開頭提醒區,這次多出的一行只在 old_sentence 寫了東西時出現,`-k doctor_drift` 綠;其餘沒有牽連到的程式碼。

最高等級:major
