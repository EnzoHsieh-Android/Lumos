severity: major

# 代碼審 r1 — 通才席(opus)

審查對象:`r1-code.patch`(scripts/lumos + scripts/test_lumos.py,699 行),對照 `r1-snapshot.patch` 的計劃筆記〈做法〉1–7 與條款 S1–S12。
實驗都在自己的 `git clone --shared` 臨時副本 `scratchpad/rv-opus`(HEAD 42848bd6)做;重現腳本在 `scratchpad/code-vr/r1/opus-repro/repro.py`(用 `python3.14 repro.py <情境>` 跑)。

## F1 多掛提醒印的 remove 改法沒加 shell 引號也沒濾控制字元:照貼會執行 verified_by 項裡的 `$(…)`,檔名帶空白時照貼直接失敗
severity: major
blocking: 是
引句:「改法:lumos remove {sys_rel[:-3]} verified_by \"{a}\",或把它補進那份的 system_refs」
file: `scripts/lumos:33328`(`_drift_sh`:「檔名帶 $(…)、; 或反引號的筆記,照貼提示就會執行攻擊者的指令;正確性席:帶空白會被切成兩個參數」——同一支檔已有的照貼指令引號規矩)
file: `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:80`(PITFALL:照貼指令遇控制字元要不印,舊句檢查代碼審 r3 四席)
file: `scripts/lumos:15063`(`_kill_add_template`:帶控制字元的欄位不放進可貼的範本)

1. 輸入:`Systems/B.md` 的 `verified_by` 有一項 `"[[Verification/V|$(touch /tmp/opus_rv_pwned)]]"`(別名部分任意寫,`link_target` 去掉別名後照樣解析到 V);`Verification/V.md` 寫 `system_refs: ["[[Systems/A]]"]`、沒寫壞項。
2. 走到 doctor 3/4 多掛那段:`a` 是登記原字面,被直接塞進雙引號裡,印出 `lumos remove Systems/B verified_by "[[Verification/V|$(touch /tmp/opus_rv_pwned)]]"`。雙引號擋不住 `$(…)` 與反引號。
3. 重現(當場翻紅):`python3.14 repro.py paste` 把印出的改法原樣丟給 `bash -c` 跑,結果 `rc= 0 ✓ remove Systems/B.md: verified_by 拿掉了 [[Verification/V|]]`、`被執行了嗎: True`——指令被執行,而且 remove 實際拿掉的字面也被 shell 改掉了(`|` 後面變空)。
4. 無惡意的同類:功能筆記叫 `Systems/My Feature.md` 時印出 `lumos remove Systems/My Feature verified_by "[[Verification/V]]"`,照貼 rc=2「擋下:不認得這幾個參數」。登記值裡有 `"`(別名帶引號)時同樣斷字。
5. 這一行也沒過 `_esc_clean`(上面寫壞那段 `sr_bad` 有過),`a` 帶 ESC/換行時直接打進終端。
6. 改法建議:節點用 `_drift_sh(sys_rel[:-3], node=True)`、值用 `_drift_sh(a)`(或 `_sh_quote`),值帶 Cc/Cf/Zl/Zp 時改印佔位字(照 `_kill_add_template` 的 `ok()`);整行再過 `_esc_clean`。注意 S6 測試 `t_doctor_check3_system_refs_extra_backlink` ① 斷言的是未加引號的字面 `'lumos remove Systems/B verified_by "[[Verification/V]]"'`,改了要一起改,並補一條帶 `$(` 與空白檔名的案例。

## F2 孤兒推薦對有宣告的紀錄只照檔名長度排序,同長度時順序由集合雜湊決定,每次跑不一樣;超過 3 項時隨機挑 3 項、其餘被說成「較弱線索」
severity: minor
blocking: 否
引句:「key=lambda x: -len(env.notes[x[0]].stem or ""))」

1. 輸入:孤兒驗收紀錄 `system_refs` 列 `Systems/AA`、`BB`、`CC`、`DD`、`EE`(檔名一樣長),跑 `doctor --suggest`。
2. `r[1]` 是 set,`sorted` 只用 `-len(stem)` 當鍵,同分時保留 set 的迭代順序;字串雜湊每個行程隨機,所以印哪 3 項每次不同。
3. 重現:`python3.14 repro.py order` 用 PYTHONHASHSEED=0..7 跑 8 次,得到 7 種不同的推薦清單;`python3.14 repro.py order2` 印出 3 項推薦加「(另有 2 個較弱線索略過)」——那 2 項跟被印的一樣是本篇宣告的,不是較弱線索。
4. 改法:鍵加 rel 當次序(`(-len(stem), rel)`);有宣告時要嘛全列、要嘛把略過那行改成「另有 N 個宣告的功能」。

## F3 `null`、`~`、行內註解、`""` 這幾種空宣告報的原因跟計劃寫的不一樣,`""` 給的改法照做仍是壞的
severity: minor
blocking: 否
引句:「return None, "空的項——拿掉,或寫成 [[Systems/X]]"」

1. 計劃〈做法〉2 寫明「清單本身一項都沒有(空值、`null`、`~`、只有註解、空清單、清單項沒縮排而解析成空)→ 記一項寫壞『system_refs 讀不出任何一項』」。
2. 實際(`python3.14 repro.py null`):`system_refs: null` 與 `system_refs: ~` 與 `system_refs: # 待補` 都被 `parse_frontmatter` 讀成一個字串值,走 `_typed_link_target` 的 scalar → 報「不是單一連結(多寫了字、純文字路徑或括號不對)」;`system_refs: ""` 讀成 `""` → `as_list` 回 `[""]` → skip → 報「空的項——拿掉,或寫成 [[Systems/X]]」。
3. 仍然都算 issue、沒有默默關掉檢查,所以只是 minor;但「拿掉」照做會剩下裸鍵 `system_refs:`,下一輪變「讀不出任何一項」,使用者要修兩次。改法:items 全是空字串或整欄值是 `null`/`~`/`#` 開頭時,歸到「讀不出任何一項」那條。

## F4 計劃〈做法〉7 點名要同步的 append 說明字串沒改
severity: minor
blocking: 否
引句:「`scripts/lumos` 裡 `append`、`new --systems`、`sync-verified-by` 的說明字串」
file: `scripts/lumos:44868`(`sub.add_parser("append", help="list 欄位追加(verified_by/plan_refs/related/tags)")`,本次未動)

1. `new --systems` 與 `sync-verified-by` 的說明都改了,`append` 的 argparse help 與 `HELP_WHEN["append"]` 都沒提 `system_refs`;`lumos --help` 看不到這個新欄位能 append。
2. 小改:help 字串補 `system_refs`(或改成「見 LIST_KEYS」)。

## F5 條款綁的測試有兩處沒驗到條款點名的行為
severity: minor
blocking: 否
引句:「check("②lint 不把它當打錯的欄位名", "system_refs" not in (r.stdout + r.stderr), r.stdout + r.stderr)」

1. S4 點名「多個連結」,`t_doctor_check3_system_refs_bad_entry` 的 cases 沒有這一形狀;S3 點名「清單項沒縮排」,cases 也沒有。翻紅實驗:把 `_system_ref_item` 裡 `if raw.count("[[") > 1` 改成 `if False`(多連結改報成「不是單一連結」),`-k system_refs` 30 passed、0 failed,沒有一支紅。(行為本身我手動驗過是對的:`python3.14 repro.py shapes`,沒縮排→「讀不出任何一項」、多連結→「一行寫了多個連結」。)
2. S9 ② 接在 append 之後:若 append 失敗(例如 `system_refs` 沒進 `LIST_KEYS`),檔裡根本沒有這個鍵,lint 當然不提它,② 照綠。翻紅實驗:從 `LIST_KEYS` 拿掉 `system_refs`,這支測試 ①③④ 紅、② 綠。整支仍會紅所以不算假綠,但 ② 自己沒驗到「lint 認得欄位名」;直接 `write` 一篇帶 `system_refs` 的紀錄再 lint 才量得到(我實測未登記時 lint 會唸「沒見過的鍵『system_refs』」,所以這條改寫後是能翻紅的)。
3. 改法:cases 補 `'system_refs:\n- "[[Systems/A]]"'` 與 `'system_refs:\n  - "[[Systems/A]] [[Systems/B]]"'`;② 改成獨立夾具。

## 看過、沒問題的部分

- **`build_typed_index` 改呼叫 `_typed_link_target` 行為不變**:逐分支對照舊碼——skip(空字串、抽完空目標)照舊 `continue` 且不進去重集;scalar 照舊不去重、附原字串;去重鍵 `t` 取 ok 的 `val[1]`、ambiguous 的 `val[0]`、ghost 的 `val`,三者都是舊碼的 nfc、去別名段落、保留 `.md` 的字面;ambiguous 候選照舊 `sorted(cands)`。翻紅實驗:把 ok 的去重鍵改成 `val[0]`(落點 rel),S5 ① 翻紅。
- **`issues += len(sr_bad) - len(_shown)`**:`issues` 是 `run_doctor` 的區域變數,`warn` 用 `nonlocal` 加 `len(lines)`;超過 20 項時 `_shown` 是 21 行(含「另 N 項」),`warn` 加 21、這行再補 `N-21`,合計 N;剛好 21 項時補 0,合計 21;≤20 時補 0。`--ci` 下 rc 照 issues 判,寫壞項會擋推送,符合計劃「誤擋是本意」。
- **`_verification_system_targets` 各寫法**:沒鍵→舊路徑;區塊寫法→一項寫壞;`system_refs:`/`[]`/沒縮排→「讀不出任何一項」;多項其中一項壞→好的照收、壞的列出、`sr_declared` 標有壞項;行內純量 `"[[Systems/A]]"` 照收。`as_list("")` 回 `[""]`(見 F3)。
- **多掛提醒遇純量 verified_by、帶別名的登記**:`edit_fm_remove` 對 `LIST_KEYS` 的純量會先轉清單、比對用 `link_target`,所以原字面帶別名或純量都 remove 得掉(問題只在引號,見 F1)。
- **孤兒推薦**:有宣告且合格→只推宣告的;全寫壞→印提示後 `continue`,但 `issues += len(orphans)` 在迴圈外,照算;None(失效)與沒宣告走原本。翻紅實驗:拿掉 `not dec[1]` 條件,S6 ③ 翻紅。
- **sync-verified-by**:`n_bad` 提醒放在 `if not planned` 之前,dry-run 與 `--apply` 兩條路都會先印;沒宣告的紀錄用 `env.resolve` 落在 Systems 的,與舊碼一致。
- **狀態不分大小寫**:四處都改用 `_verification_status`,各自的跳過集合維持原樣(1/4 只豁免 superseded、其餘三處 `_VERIF_INACTIVE`)。翻紅實驗:拿掉 `.lower()`,S10 四條全紅。
- **S3 空值空清單**:翻紅實驗把 `if not items:` 改成 `if False:`,S3 兩條紅。
- 9 支新測試在臨時副本全綠(`-k system_refs` 30 passed 等)。

## 圖譜鏡頭

派工單尾端沒有附固定席筆記(也沒有角色卡),依規則不逐條答。我自己跑了 `lumos impact --diff e594a964..HEAD` 抽看兩篇家筆記:
- `Systems/lumos-cli-read`:KEY 行宣稱「Check3 skip 集+sync-verified-by 過濾+orphan 豁免四位一致」——這次把四處改成同一支 `_verification_status`,一致性更強,沒破壞。
- `Systems/lumos-cli-write`:「LIST_KEYS 2026-10-03 為 10 項」與常數實數 10 項相符。
- F1 違反的是 `Systems/存量漂移守衛` 兩條 PITFALL 記下的照貼指令規矩(那是線索層,不是合約行),所以列 finding 不以「破壞合約」論。

最高等級:major,blocking 共 1 條
