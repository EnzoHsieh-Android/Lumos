severity: minor

# 舊句檢查 代碼審 r2:正確性-opus(審 r2-snapshot-code.patch、r2-rebase-rangediff.txt)

實驗都在 `--shared` clone(`scratchpad/r2corr/repo`,HEAD 1d6e7289)上跑,直譯器 /opt/homebrew/bin/python3(3.14)。腳本在 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/r2corr/`(`exp_cfg.py`、`exp_block.py`、`perline.py`、`perm.py`、`exp_sub.py`)。

## F1 重定基底之後,doctor 對只寫 old_sentence 的設定(off 或寫錯值)完全不出聲

severity: minor
blocking: 否
引句:「cfg_warns = [w for w in cfg_warns if "old_sentence" not in w]」
file: `scripts/lumos:29545`
file: `scripts/lumos:29553`

1. 重定基底前,gate 預設是 warn,doctor 的條件是「mode 不是 block,而且自己寫了或已接線」。所以 `{"drift_check": {"old_sentence": "off"}}` 會印出一行,結尾是「舊句檢查(drift_check.old_sentence)是 off」。
2. 重定基底後,gate 預設改成 block,old_sentence 的值只接在 gate 那行後面(`osl`)。gate 那行只有兩種情況會印:設定寫壞,或 gate 自己寫了 warn/off。old_sentence 的提醒又在第一行就被濾掉了。
3. 實跑 `exp_cfg.py`(`_drift_gate_doctor_lines` 對真 repo 的 `.lumos/config.json`):下面六種設定 doctor 都回 `[]`:`{"drift_check": {"old_sentence": "off"}}`、`"on"`、`["block"]`、`{"a":1}`、`true`、`null`。可是 `_drift_config` 對寫錯值的那幾種都有產生提醒「drift_check.old_sentence 只能是 block/warn/off,你寫的是 'on',照預設 warn」。
4. 結果有兩種情況看不到:
   - 專案把 m1 關掉了,健檢看不出來。
   - 有人以為寫了 block,其實拼錯了,m1 照 warn 跑,健檢也不講。
   這兩種都違反同一支函式註解寫的原則:「關掉了要看得見」「設定寫壞…也講出寫錯的地方(人明明寫了東西)」。drift check 每次跑都會把拼錯那句印在 stderr,所以推送時還看得到;關掉(off)那種在哪裡都看不到。
5. ⚠ 計劃〈做法〉的 `_drift_config` 那段寫的是「doctor 講開關的那行(gate 的規則…)後面多講 old_sentence 的值」,照字面讀,程式有照做。問題是這樣合併以後,只要 gate 沒寫,old_sentence 自己的「關掉/寫壞」就沒有地方講。

## F2 m1 兜底後,工具出錯時的回傳碼跟說明頁「工具出錯照紅/講一句就放行」兩句都對不上

severity: minor
blocking: 否
引句:「紅燈(drift check 沒寫設定就是 block;設了 warn 不紅;工具出錯照紅)」
file: `skills/lumos-project-notes/commands/08-自動跑的.md:9`
file: `skills/lumos-project-notes/commands/08-自動跑的.md:7`
file: `scripts/lumos:29387`
file: `scripts/lumos:29588`

1. `_drift_m1_guarded` 把 m1 裡任何例外都兜底成 state `error`。warn(old_sentence 沒寫時的預設)回 0,block 回 1。
2. 08 表 CI 那一列寫「工具出錯照紅」,doctor 給消費專案的 CI 範本註解也寫「其他非零是工具出錯或參數錯,也會紅——工具出錯時寧可紅」。m1 在預設 warn 下出錯,rc 是 0,CI 是綠的。
3. 同一張表 pre-push 那一列寫「工具沒跑成(錯誤、git 太慢)講一句就放行」。old_sentence=block 時 m1 出錯回的是 1,掛鉤把它當成擋下,不會放行。
4. 兩句話對 c1 到 c5 都成立:沒接住的例外會變成 traceback,那是另一套 rc 語意。對 m1 則兩個方向都反了。這是 r1 把 m1 改成兜底之後,文件沒有跟上的內部不一致。

## F3 m1 在 old_sentence=block 擋下時,掛鉤與 CI 印的逃生指示叫人把 gate 設成 warn,設了也解不開

severity: minor
blocking: 否
引句:「開關另一個 drift_check.old_sentence(沒寫是 warn 只提醒,block 才擋)」
file: `scripts/hooks/pre-push:483`
file: `.github/workflows/ci.yml:174`

1. 重現 `exp_block.py`:設定 `{"drift_check": {"gate": "warn", "old_sentence": "block"}}`,刪掉 `src/a.py` 的 `def old_func_x`,家筆記的正文還在講它。`lumos drift check --diff base..tip` 的結果:rc 1,印出「擋下:舊句檢查:這次推送消失了 1 個名稱…要處理 1 筆」。
2. 掛鉤看到 rc 1 就印固定的逃生句「整個專案先只提醒 → .lumos/config.json 的 drift_check.gate 設成 warn」。CI 印「或把專案的 drift_check.gate 設成 warn」。可是這個專案的 gate 本來就是 warn;m1 擋下看的是 old_sentence,照這句去改什麼都不會變。
3. state 是 error 或 timeout 的時候(block 下回 1),掛鉤一樣先印「照上面每一筆的 lumos drift fix 指令改掉、或 lumos drift ack 表態」,但這時沒有任何一筆可以改。m1 自己印的 `LUMOS_SKIP_DRIFT_CHECK=1` 那句是對的,只是被掛鉤的錯誤指示蓋在後面。
4. 掛鉤與 CI 這兩段是主線原有的文字,這批沒動。但 m1 多了一個會回 1 的來源,這兩處沒跟著講 old_sentence。

## 查過、沒發現問題的地方(照派工鏡頭逐項)

- **兜底 `error` 與回傳碼**:例外訊息會進結論行(120 字)和帳(`error` 欄 200 字),都過了 `_drift_m1_show`,看得到,沒有被吞。warn 回 0、block 回 1、印出本身又出錯時只印一行(`t_drift_m1_review_r1_non_utf8_and_guard` 綠)。`_DriftM1Stop` 在判定本體裡先接住,timeout 與 git-failed 不會被兜底改寫成 error。KeyboardInterrupt 與 SystemExit 不在 `Exception` 底下,照樣往外丟,掛鉤的 128 以上那條路不受影響。
- **非 UTF-8 轉義**:帳裡每一個會帶路徑或名稱的欄位(`rows` 的 path、names、text,`nodes`、`text_defs_paths`、`error`、ledger-miss 的 `repo`)都過 `_drift_m1_show`。它碰到代理字元不在 U+DC80–DCFF 範圍的情況,會退到 backslashreplace,不會丟例外。印到 stderr 的部分,Python 本來就用 backslashreplace。
- **單行上限與截止時間**:我用反證法驗了逐行候選是超集:整字正則的兩組邊界都排除 ASCII 英數與底線,所以命中處名稱的每一段一定是完整的詞;長度相同的兩個名稱不可能在同一個位置都命中,長的在前的順序在子集裡也保留,所以 finditer 逐位置的結果相同。實測最壞的一行(2600 個不同名稱擠在同一行、每個都命中):每行 35 到 50 毫秒,每行都看截止時間,超時最多多跑一行。超長行先過區塊、可見、撤除三道篩才計數,只算真的會掃的行。
- **無副檔名兩邊各判**:`_drift_m1_kinds` 對 A、D、M 三種狀態分別只判存在的那一版。不是 Python 的那一版當空定義;起點是 Python、終點改成 shell 時,舊定義會進候選,終點語料也不會把它算成還在。子模組(gitlink)推進一版時 m1 不印也不記(`exp_sub.py`)。
- **名稱正規化共用**:候選端、`--name` 驗證、表態比對三處都走 `_drift_m1_name_canon`;寫表態的 `sorted(set(names))` 前面已經驗過,名稱等於正規化結果。strip 與 isspace 兩邊用同一套空白定義。
- **`_nodehome_name_status` 換用**:在 `--no-renames` 下,一個狀態碼配一個路徑,輸出跟原本手刻的逐筆相同。只有兩個差別:排序改成照 NFC 路徑排;同一個名字的 NFC 與 NFD 兩份檔同時一刪一加時會合成一筆(原本是兩筆)。後者只影響 `code_files` 計數,候選判定相同。這個情況很罕見,不算 finding。
- **快取目錄權限放寬**:`group_ok` 只放寬 group 可寫,擁有者與 other 可寫照樣擋,新建的層明給 0700。實測(`perm.py`,umask 002、`~/.cache` 是 0775 的 staff 群組)m1 可以用,派工鏡頭照舊不能用。我查了共享群組(macOS 的 staff)的其他帳號能做什麼:只能在 group 可寫的父層換掉目錄項。換成自己的目錄,擁有者檢查會擋;換成連結,解析路徑比對會擋;在檢查與 `os.chmod(path.parent, 0o700)` 之間換連結,chmod 也只能落到一個叫 drift-defs 的目錄,而葉層與每支快取檔在第一次寫入時都已經收成 0700/0600。所以只剩「讓快取與留痕失效」,那跟放寬前(整個不能用)一樣,不是新洞。留痕檔開了之後再驗擁有者,這點也對。
- **`range-unavailable`**:`gov --stats` 的「被跳過」只數 `skipped` 開頭的 kind,`fail-open` 另一行;range-unavailable 兩邊都不進。code-loop 認留痕只認 passed/skipped,不受影響。
- **gov 去重鍵加 check**:整份 scripts/lumos 只有 m1 那筆帳寫 `check`。在 clone 的真帳上,用新舊兩種鍵各跑一次 `lumos gov --stats --since 400`,6659 行輸出逐字相同。`-k gov` 126 條全過。
- **`_drift_config` 四個回傳值(重定基底)**:18 種設定實跑(`exp_cfg.py`):
  - 沒設定檔、`{}`、`[]` → (block, [], False, warn)。
  - JSON 壞或不是 UTF-8 → gate block 加一句、old_sentence warn 加一句、explicit True。
  - drift_check 不是物件或是 null → gate 加一句,old_sentence warn 不另講。
  - old_sentence 寫 null → warn;寫 list、dict、true → warn 加一句,不丟例外(`_DRIFT_GATE_VALUES` 是 tuple,list 不會引發 unhashable)。
  - gate 寫錯、old_sentence=off → gate block 加一句、old_sentence off。
  全部跟計劃那段逐條相同。兩個呼叫端與測試的解包都改成四個值了。
- **doctor 開頭提醒合併**:`osl` 接在兩個分支後面;壞 JSON 時 old_sentence 那句被濾掉,只講 gate 那句再接「舊句檢查是 warn」。每種情況 doctor 開頭都只有一行,軟段計數不變。old_sentence 自己的提醒被濾掉的後果見 F1。

## 圖譜鏡頭逐條判定

- `Systems/lumos-cli-read`(search 預設排除 superseded、不排除 stale):這批沒碰 search 的濾網,不影響。
- `Systems/bound-tests-gate`(code-loop check 真跑綁定測試,紅、懸空或證不出跑過就擋):沒動 code-loop check。m1 借用的 `range-unavailable` 只是寫帳用的字面值,閘本身不讀 drift-check 的事件,不影響。
- `Systems/guard-kill`(rc 優先序、--json 純度):沒動 guard kill,不影響。
- `Systems/授權與歸屬`(白名單不含授權檔、主程式檔頭):patch 沒碰檔頭,也沒碰 `_VENDORED_TOOLKIT`,不影響。
- `Systems/測試假綠形態`(還原翻紅釘要配前置斷言):r1 新增的測試我看了兩支,都有「①前置」斷言(非 UTF-8 檔名真的在樹上、dense 那行在上限內而另兩行超過)。tests 那份不是我審的範圍,不另判。
- `Systems/lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間):沒動,不影響。
- `Systems/design-loop`(處置閘第五步):沒動,不影響。
- `Systems/pitfalls-code-loop`(RISK):這批改的是推送閘的判定與寫帳,照規矩走代碼審,就是現在這一輪。F2、F3 屬於「擋人的閘回 1 之後,人被指向哪裡」這一類。
- 超出上限只列名的節點:這批碰到的共用部分有三個。`cmd_gov` 的去重鍵實測既有統計逐字不變;`_trusted_private_dir` 與 `_mkdir_trusted_under_home` 的 `group_ok` 預設 False,其他呼叫端行為不變,派工鏡頭實測照舊嚴格;`_home_cache_write` 多一個預設 False 的參數。沒看到會牽動那些節點合約的改動。

最高等級:minor
