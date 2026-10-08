severity: major

鏡頭:邊界與輸入(第 3 輪凍結版)。對照 clone-ns 的程式現況推演,能跑的跑了(argparse `--name=` 寫法、`_mk_rx` 邊界、11.5 MB 文字比對計時、5 萬行筆記的 `_notelines_regions` / `_visible_lines` 計時、git 歷史量測試檔大小)。

## F1 4 MB 剖檔上限在本 repo 兩週內就會踩到 test_lumos.py,而且量準度的判不了分母看不到
severity: major
blocking: 是
引句:「blob 超過 `_DRIFT_M1_PARSE_MAX_BYTES`(4 MB)不剖,當剖不動(ast 的尖峰記憶體約原始碼的 100–280 倍」
file: `scripts/test_lumos.py:1`(git cat-file -s:HEAD 3,568,962 位元組)
1. 〈誠實界線〉與〈依據〉只盯 `scripts/lumos`(2.2 MB,約 47 天後才到 4 MB),沒提 `scripts/test_lumos.py` 已是 3.57 MB。我用 git 歷史量:09-12 為 2.55 MB、09-18 為 2.93 MB、09-27 為 3.15 MB、09-30 為 3.57 MB,18 天長 1.02 MB(近三天每天約 140 KB)。離 4,194,304 只剩約 0.62 MB,約 4 到 11 天;凍結版落地還要過代碼審,落地時多半已超過,兩週提醒期(REVISIT 10-14)幾乎整段都在「太大」狀態下量。
2. 超過之後,照字面:改到 test_lumos.py 的推送(這個 repo 幾乎每個功能提交都會改)兩版任一邊太大 → 那支檔「不抽候選」。這個 repo 的筆記大量用 `[test:t_...]` 引用測試名,測試被刪或改名正是主要的舊句來源,所以兩週內最大宗的來源看不到。
3. 這種推送的狀態是 done、candidates 0、kind passed,結論行印「這次改到 P 支程式檔,沒有名稱消失」,另印「1 支太大沒剖」。〈做法〉4 的「判不了」分母只算 timeout / git-failed / unreadable,不含 `oversize` 與 `unparsable`(S16 還明寫記成 done、candidates 0),所以這些被略過的推送在 RETIRE-IF 裡算成乾淨樣本,「樣本不足」判不出來,ledger 裡有 `oversize` 欄卻沒有任何條件去讀它。
4. 〈誠實界線〉末條說「回頭條件接在『N 支太大沒剖』那行帶路徑,工具鏈推送一印出 `scripts/lumos` 就重量剖檔記憶體、調上限」,但被點名的會是 `scripts/test_lumos.py`,條件字面對不上,也沒有說「印出任何路徑」要怎麼處理。
5. 「4 MB」沒定義是 4×1024×1024 還是 4,000,000;兩者差約 194 KB,剛好落在 test_lumos.py 兩三天的成長量裡,測試釘邊界時會各寫各的。
折法方向(擇一即可,不必全做):a) 太大或剖不動的**改到的檔**改用 `_drift_py_def_re` 的逐行文字比對抽起點與終點兩版的定義(不吃 ast 記憶體),不整支略過;b) 上限依實測放寬並寫死單位;c) RETIRE-IF 把「改到的檔有 oversize 或 unparsable」的推送併進判不了分母,並把 REVISIT 觸發條件改成「任何路徑出現在太大沒剖」。

## F2 終點語料裡太大或剖不動的檔,文字比對沒有截止時間檢查
severity: minor
blocking: 否
引句:「全部放進同一次 `_nodehome_cat_blobs` 照內容編號批次讀」
file: `scripts/lumos:26816`(`_drift_py_def_re` 逐名稱編一條 `re.M` 正則)
1. 〈做法〉1「時間」只在 git 呼叫前、每剖一支前、每掃一篇筆記前與每 200 行看截止;〈剖不動(或太大)〉那段是「每個候選名稱 × 每支剖不動的終點檔」各跑一次正則,沒有檢查點。
2. 我量 11.5 MB 的檔,一個名稱一次 `^(?:...def|class... | 名稱 = )` 掃描約 0.085 秒;4.2 MB 約 0.03 秒。F1 之後 test_lumos.py 會成為這種檔;〈範圍〉自己舉的最壞情況「整支主程式被刪」有 1128 個候選,1128 × 0.03 ≈ 34 秒,超過 30 秒預算且不可中斷,而〈實務隱患〉的最壞時間只算了兩段不可中斷呼叫。
折法方向:每支檔用一條交替正則掃一次(名稱先 re.escape 合併),或每個名稱前看截止。

## F3 批次讀用 `_nodehome_cat_blobs`,沒有大小上限
severity: minor
blocking: 否
引句:「全部放進同一次 `_nodehome_cat_blobs` 照內容編號批次讀」
file: `scripts/lumos:23965`(`_nodehome_cat_blobs_capped` 已存在:先問大小、超過的不讀進記憶體)
1. 〈做法〉1 說 4 MB 是為了不吃記憶體,但讀取步驟用的是無上限的 `_nodehome_cat_blobs`:超過 4 MB 的 blob 因為不寫快取,每推一次都整個讀進來(`r.stdout` 一份、切片再一份)。冷快取時整個終點語料一次讀完,語料愈大愈吃記憶體。
2. 既有 `_nodehome_cat_blobs_capped` 正是同一個需求(先 `_nodehome_cat_sizes` 問大小),spec 的 PRIOR-ART 沒列它,也沒說太大的檔怎麼在不讀內容的情況下被識別成「太大」。
折法方向:改用 capped 版,回 None 的視為太大。

## F4 治理帳「整行 4 KB」的量法對不上 `_gate_event`,截到底仍可能超過
severity: minor
blocking: 否
引句:「整行(json 編碼後的位元組)還超過 4 KB 就先從只列出、再從要處理尾端丟」
file: `scripts/lumos:1147`(`_gate_event` 自己組 ts / commit / gate / kind / hard / nodes / note / detail / head_sha 再合併 extra,`ensure_ascii=False`)
1. `_gate_event` 內部才組出完整事件,m1 呼叫前拿不到最終位元組數;要量準得複製它的組欄邏輯或重構它(〈回退〉清單沒列 `_gate_event`)。只量 extra 會少算約 400 位元組,剛好落在邊界的那一行會誤放。
2. 「超過」沒定義是 >4096 還是 ≥4096、是否含結尾換行;`_ledger_append` 的規則是 `len(bytes + "\n") > 4096`。S6 的邊界測試因此沒有唯一答案。
3. 丟光 rows 之後,`nodes`(最多 50 篇,每篇路徑常 60 至 80 位元組)、`note` 與 `detail`(同一句寫兩次)、`oversize_paths` 加起來仍可能超過 4 KB;規則沒說這時怎麼辦(繼續寫?縮 nodes?)。實際上 `_gate_event` 不擋長度,所以會寫出去,但那與「不超過 4 KB」的宣稱矛盾。
折法方向:寫明量法(含結尾換行、`>4096`)、把組欄抽成共用函式供量測用,並規定 nodes 也一起縮。

## F5 名稱可以超過 200 字,但 `--name` 只收 1 到 200 字
severity: minor
blocking: 否
引句:「每個值去頭尾空白後 1 到 200 字、過 `_drift_one_line`」
file: `scripts/lumos:27483`(`_drift_ack_args_err`);`scripts/lumos:9765`(`_esc_clean` 預設 limit=200,超過補「…」)
1. 路徑類候選(只要含 `/` 就過形狀過濾)沒有長度上限。被刪的 Java / Kotlin 深層套件檔,筆記又寫了完整路徑,名稱可超過 200 字。提示會印 `--name=<超過 200 字的路徑>`,`drift ack` 回 2,這一筆在 block 模式沒有表態出路,只剩改寫那一行或整批略過。
2. 名稱含控制字元(git `-z` 路徑可含 tab 或換行)時,`_drift_one_line` 也擋掉;提示行又過 `_esc_clean` 會把控制字元換成空白,照貼的名稱跟原名稱不同,永遠對不上。
3. 〈做法〉3 的 `why` 行走既有 `_drift_print_findings`,那支對 why 有 `_esc_clean(...,1000)` 截斷;同一行 20 個名稱、每個帶「(原本在 路徑)」時,why 會被截掉尾巴,只有改法行有完整名單,spec 沒提這個截斷。
折法方向:名稱上限跟候選一致(或候選超過上限就只列出、不進要處理並不要求表態),並在 why 行處理截斷。

## F6 `./路徑` 寫法(相對路徑加點)提到的被刪腳本不會被列
severity: minor
blocking: 否
引句:「前面不能緊接 ASCII 英數、底線、`/`、`.`、`-`,後面不能緊接 ASCII 英數、底線、`-`」
file: `governance/eval/drift-exam/old-sentence/old_sentence_exp.py:667`(`_mk_rx`)
1. 我跑了 `_mk_rx`:候選 {`tools/run_all.sh`, `run_all.sh`},「執行 ./tools/run_all.sh 即可」與「../tools/run_all.sh」都命中 0 個(前一字元是 `/`);「bash tools/run_all.sh」、「(tools/run_all.sh)」、行尾句點結尾則命中。`./scripts/x.sh` 是筆記裡很常見的寫法,基本名也因前面是 `/` 一併排除。
2. 這是照參考實作的行為,不是實作錯;但〈誠實界線〉沒列這個漏報形狀,REVISIT 的 revisit 子命令也沒有對應的放行量。
折法方向:〈誠實界線〉補一句並在兩週後用 revisit 數;要修就放寬前綴(允許 `./` 與 `../`)並重跑三組驗收數字。

## F7 gate=off 的專案預設會被開起舊句檢查
severity: minor
blocking: 否
引句:「gate=off → 不跑 c1–c5/probe,`rc_core` = 0;印的那句在 old_sentence 不是 off 時改成」
file: `scripts/lumos:28238`(`cmd_drift_check` 現行 `mode == "off"` 直接 return 0)
1. 現行 `drift_check.gate=off` 的意思是整道 drift check 不跑。改版後沒寫 `old_sentence` 的專案(預設 warn)在 gate=off 下仍會跑 m1:多 30 秒預算、多一行 stderr、每次有程式改動的推送多一筆治理帳。設計是刻意的(S14),但那些專案原本明確說了「這道關掉」,升級後行為變了,〈範圍〉與〈回退〉都沒把它列為相容性變更。rc 仍是 0,所以是噪音與時間,不是擋人。
2. 純文件推送時 m1 什麼都不跑,那句「舊句檢查另有開關…照跑」仍會印,內容與實況不符(輕微)。
折法方向:〈範圍〉列為相容性變更,或 gate=off 時預設 old_sentence 也 off(只在明寫時才跑)。

## 已讀,無 finding 的邊界推演(逐項)
- 純文件推送:diff 只列 `docs/`、`.md` 與圖譜檔,`_drift_m1_code_path` 全 False → 不印不記、rc 0;沒副檔名的頂層檔(LICENSE、`.gitignore`)只多一次首行讀取,git 呼叫數不隨檔數成長。無問題。
- 只刪 `.sh`:程式檔支數 1、路徑類候選 `tools/run_all.sh`(含 `/`)過形狀、基本名 `run_all.sh`(有底線)也過;`deploy.sh` 這類無底線基本名不成候選但完整路徑成(〈誠實界線〉已寫)。粗候選非空所以會剖整個終點語料(對純路徑候選其實用不到,只是多花時間,不算錯)。
- 空 repo 首推與新分支首推:`_lens_push_base` 找不到主線回空樹、`_note_audit_resolve` 回 None → no-base、rc 0、記 skipped,與〈做法〉1 描述一致;有主線時取分岔點正常判。SHA-256 repo 的空樹編號不同,spec 沒說 diff 用 `_drift_empty_tree`(既有 core 用它),實作照既有慣例即可,列為提醒。
- 名稱是旗標:`--name=--restore`、`--name=a b`、`--name=a=b` 我用 Python 3.14 argparse 跑過都解析正確;`--name --restore` 確實回 2、`--name=` 給空字串(由 spec 的 1 到 200 字檢查擋)。與 S4 一致。
- 名稱是路徑或中文:CJK 路徑 `tools/匯出報表.py` 與 `計算_總額` 的 ASCII 詞先篩推演成立(段 `tools`、`py`、`_` 都在全文詞集合);純中文無底線名稱過不了形狀過濾,所以先篩的「純中文一律留下」實際只會遇到含底線的中文名。macOS NFD 與 NFC 的差異(帶重音拉丁字、韓文)spec 沒說 diff `-z` 取得的路徑要不要 NFC 化,既有 `_drift_oids` 是 NFC 鍵;CJK 基本不受影響,判不準是否會出誤差 ⚠。
- 同一行 20 個消失名稱:一條交替正則、集合聯集表態、改法上限 4000 字,推演成立(F5 談 why 行截斷)。
- 一篇筆記 5 萬行:我量 `_notelines_regions` 0.007 秒、`_visible_lines` 0.002 秒、50 個名稱的整字正則掃 5 萬行 0.04 秒;每 200 行看時間足夠。5 萬行全命中時發現筆數是 5 萬,輸出與帳都有上限,沒問題。
- 快取目錄不可寫或屬別人:`_mkdir_trusted_under_home` / `_trusted_private_dir` 不過就不讀不寫不刪,照常剖;設計與既有 dispatch-lens 一致。清舊檔那段要注意借 `_note_audit_work_dir` 時它的 glob 是 `*.md`,快取檔沒副檔名,實作要改樣式,spec 沒點名(提醒,不算 finding)。

最高等級:major;blocking 共 1 條
