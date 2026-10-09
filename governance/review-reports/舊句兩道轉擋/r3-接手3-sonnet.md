severity: major

審稿範圍:我把 spec(與 `/tmp/舊句兩道轉擋-r3.md` 逐字相同)對照 repo 逐段查過,並實際跑了 `_slot_replacement_dead`。沒有附固定席節點,所以那一項不適用。只有 F1 到得了 major。

### F1 「已對照」只認來源核對過的紀錄,但配套的訊息與「待提交」判斷沒跟著改,一旦遇到來源核對沒過的紀錄就走進死迴圈
severity: major
blocking: 是(照字面實作,S7 會紅;沒紅的那一半會讓人照訊息走進迴圈)

- **spec 段落**:〈重讀:候選與兩層〉的「已對照」共用口徑,加上〈輸出〉末條改 `cmd_note_audit_reread_record` 收尾句。
  引句:「所以只有來源核對沒過的紀錄時,check 擋、prepare 也會重產項目檔(不用 `--all`)。」
  引句:「它印的 `git add` 提示改列這次寫的具體檔名」
- **撞牆場景**:判定者報告的 `model:`、`provider:` 或 `prepared:` 沒照抄,例如把 `model:` 寫成自己的完整型號,或 `prepared:` 抄錯。
  1. `reread-record` 照收,印「提醒:…照收,紀錄標 provenance_ok: false」,標籤只寫「照收」,沒說這份不算對照。
  2. 使用者照指示提交,再推。
  3. 被擋,而且擋下訊息跟第一次一模一樣。
  4. 使用者照訊息再跑 `reread-prepare`,但還沒提交那份紀錄,又被告知「已對照、略過」。
  5. 推送一直被擋,只剩 `LUMOS_SKIP_REREAD_CHECK=1` 或 `--all` 兩條路,而訊息只教人 prepare 不加 `--all`。
- **字面實作會踩到的錯**:spec 只說用 `_note_reread_covered` 取代 `_note_reread_committed`,沒碰 prepare 與 check 各自算「待提交」的那行。
  - file: `scripts/lumos:34781` 是 `wip = _note_reread_uncommitted(root) - done`。
  - file: `scripts/lumos:34712` 的 `_note_reread_uncommitted` 只是列工作目錄裡所有檔名,不管有沒有提交。
  - `done` 一改成「只含來源核對過的」,已提交但來源核對沒過的紀錄就掉進 `wip`。
  - 結果是 prepare 把它當「還沒提交」略過,S7 要求的「不帶 `--all` 也重產」做不到。
  - file: `scripts/lumos:34987` 的 check 會對已提交的紀錄印「在工作目錄有對照紀錄、還沒提交:git add…」,這句話是錯的。
- **來源核對沒過的處理**:file: `scripts/lumos:34876-34882` 就是現在「照收」的那段。spec 沒列這句,也沒說第一層擋下訊息要分出「N 篇只有來源核對沒過的紀錄,請重派」。
- **查證佐證**:`_note_audit_parse_report`(`scripts/lumos:34159` 附近)只對值比對,漏一個欄位就算沒過。目前已提交的 5 份都是 true,所以今天看不到;一轉擋,這就是走不出來的路徑。
- **建議補法**:
  - `wip` 改成「工作目錄有、頂端樹沒有」的差集,用頂端所有檔名(不是 covered)相減。
  - record 對 provenance_ok 為假的紀錄改印「這份不算對照,請重派」。
  - 第一層擋下訊息分列「沒有紀錄」與「紀錄來源核對沒過」。

### F2 `[被取代:Projects/舊句兩道轉擋_計劃]` 的寫法 doctor 認不得
severity: minor
blocking: 否

- **spec 段落**:〈開關〉名稱消失檢查那條(回退段也要求一樣的 superseded 寫法)。
  引句:「落地時把它標 `[status:superseded]`、補 `[被取代:Projects/舊句兩道轉擋_計劃]`,並寫新 RULE。」
- **撞牆場景**:照字面寫,doctor S17 每次都軟警告「[被取代:] 指不到」,而且永遠消不掉。
- **查證佐證**:
  - file: `scripts/lumos:4086-4099`(S17)走 `_slot_replacement_dead`,file: `scripts/lumos:20575` 的 `_dref_parse` 只認 `節點#dN`。
  - 我實跑 `_slot_replacement_dead(None, "Projects/舊句兩道轉擋_計劃")`,回「寫法認不出(要 [[節點]]、節點路徑#dN 或 無 <理由>)」。
  - 合法寫法有 `[[Projects/舊句兩道轉擋_計劃]]`,或例如 file: `docs/lumos-toolchain-knowledge/Projects/筆記格子寫法與過期檢查_計劃.md:100` 的 `…_計劃#d2`。
  - S17 是軟警告(file: `scripts/lumos:3004-3009`,不計入問題數),所以只標 minor。

### F3 〈要一起改的說法〉清單用 grep 掃全文,仍漏了幾處
severity: minor
blocking: 否

- **spec 段落**:〈要一起改的說法〉。
  引句:「[[Systems/README圖產生器]] 管的推送前關卡圖(重讀那列改成擋)」
  引句:「README 與英文版的推送前段落與圖的替代文字」
- **漏列 1:名稱消失那一列的圖**。
  - file: `assets/readme-diagrams/generate.py:481`(名稱消失那一列,中英兩版)與 `:497`(替代文字)寫的是「只提醒」或 Warn only。
  - 預設改 block 後這就是假話,可是清單的括號只點名重讀那一列。
  - 該產生器的筆記宣稱擋或提醒都對過程式預設(file: `docs/lumos-toolchain-knowledge/Systems/README圖產生器.md:41`)。
  - README 正文 `README.md:90` 和 `README.en.md:90`(「only trigger warnings」)在「推送前段落」裡,可能被覆蓋,但清單沒明寫。
- **漏列 2:手冊與掛鉤**。
  - file: `skills/lumos-project-notes/commands/06-代碼審與推送.md:94` 寫「跟存量漂移的表態沒有相依」。第二層加了 `drift ack --kind reread` 後這句就錯了,而清單只列第 4 步與「只提醒、不擋」。
  - file: `scripts/hooks/pre-push:543` 的執行時句「照推——這道只提醒、不擋」會被改掉,但清單只列了註解。
  - 命令表那條和 `note-audit` 父指令的說明(file: `scripts/lumos:49357`、`scripts/lumos:50250`)寫「(只提醒)」,清單只點名 reread-check 與 drift check 兩個 `--help`。
- **漏列 3:過期的回頭條件**。
  - file: `docs/lumos-toolchain-knowledge/Projects/漂移防治路線圖_計劃.md:31` 的 `REVISIT:2026-10-15` 與第 48 列,依賴「等 10-15 那批兩週數字」。
  - 本案取消了這批量測,所以這行 REVISIT 會在 10-15 空等。
- **測試**:`t_note_audit_reread_skill_section`(file: `scripts/test_lumos.py:64713`)釘手冊字樣,也該預期會紅。

### F4 擋下訊息教人改 `note_reread.gate` 當逃生,卻沒說要提交
severity: minor
blocking: 否

- **spec 段落**:〈輸出〉。
  引句:「另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`(單次略過、會留帳)與 `note_reread.gate` 改 warn 的寫法。」
- **撞牆場景**:沒有 Claude/Codex 環境的使用者只改工作目錄的 `.lumos/config.json` 再推,仍被擋。
- **查證佐證**:file: `scripts/lumos:34941` 的設定是從被推頂端提交讀的(`_nodehome_reader(root, tip0)`)。回退段有寫這個性質,輸出段沒有。
- **連帶**:提交設定檔會讓已過的代碼審留痕失效,因為 `.lumos/config.json` 不在簿記名單(file: `scripts/lumos:26898` 起)。訊息應註明「要提交進去才算」,並先推薦單次略過。

### F5 第二層讀表態檔的來源沒寫(頂端還是工作目錄)
severity: minor
blocking: 否

- **spec 段落**:〈照留表態〉。
  引句:「同一條目的所有 reread 表態取 `verdicts` 聯集(不取 seq 最新)」
- **撞牆場景**:判定紀錄那邊寫了「頂端提交」,表態這邊沒寫。
  - file: `scripts/lumos:37220` 的 `_drift_load_acks(root, where=None)` 預設讀工作目錄。
  - 照字面呼叫預設值,沒提交的表態也能放行,和掛鉤文字「兩種都要提交進去才算」(file: `scripts/hooks/pre-push:516`)矛盾。
  - 隊友拉下來之後會再被同一條擋。
- **建議**:照 m1 的先例寫明 `_drift_load_acks(root, tip)`。

### F6 S6 的「不論設定是什麼」與設定 off 的行為互相矛盾
severity: minor
blocking: 否

- **spec 段落**:驗收條款 S6。
  引句:「reread-check 應回 0 並記 reminded,不論設定是什麼。」
- **衝突**:〈開關〉寫 off 照原義。file: `scripts/lumos:34944-34946` 在 off 時印一句就回 0、不寫帳。測試依字面寫 off 會紅。

### F7 「順帶結掉複雜度放行」只做了四支裡的一支
severity: minor
blocking: 否

- **spec 段落**:〈回傳碼與判不了〉末條。
  引句:「順帶結掉 [[Systems/筆記內容審]] 那筆 2026-11-01 前要拆小的複雜度放行」
- **查證佐證**:
  - file: `docs/lumos-toolchain-knowledge/Systems/筆記內容審.md:100-101` 的放行是四支:`cmd_note_audit_reread_prepare`、`cmd_note_audit_reread_record`、`_note_reread_check`、`_note_audit_resolve`。
  - `.lumos/lint-waivers.json` 恰有四條回頭重讀的放行。
  - spec 只拆 `_note_reread_check`,`_note_audit_resolve` 還多加一個分支。
- **風險**:照字面刪掉那條 REVISIT,等於讓另外三支的回頭條件消失,違反「承認風險要附回頭條件」。應改成只勾掉一支、保留其餘。

### F8 「上線那次推送不會被舊紀錄擋」只驗了本 repo 的 5 份
severity: minor
blocking: 否

- **spec 段落**:〈實務隱患〉。
  引句:「現存的規則類條目是 0,上線那次推送不會被舊紀錄擋」
- **我的查證**:我逐列對本 repo 那 5 份,確實沒有規則類條目被點出。
- **未驗證的部分**:消費專案(手冊 `06-代碼審與推送.md:96` 寫 rtb 2026-10-01 已接上)已提交過紀錄,而舊的收尾句(file: `scripts/lumos:34899`)教人「確認是誤判就不動」,所以那些專案的規則類行從沒表態過。
- **撞牆場景**:升級後第一次碰到該筆記的推送,第二層會被數週前的紀錄擋住,需要逐條補表態。
- **處理**:⚠ 我看不到 rtb 的紀錄,規模未知;CHANGELOG 可加一句提醒。

### F9 掛鉤改成「128 以上都交 `pp_stop_if_signaled`」,推翻了現行刻意的 130 限定
severity: minor
blocking: 否

- **spec 段落**:〈掛鉤與 CI〉。
  引句:「128 以上交 `pp_stop_if_signaled`;回 1 擋下並印逃生段;」
- **衝突**:file: `scripts/hooks/pre-push:533-537` 的註解明講「只有 130 停下,其他訊號例如記憶體不夠被砍掉不該擋推送」。擋人之後,OOM 的 137 變成「被中斷,推送停下」,沒有逃生說明。
- **處理**:spec 沒交代這是有意推翻,應註明;至少 137 這類要印單次略過的寫法。

### 其他節
- 已讀,無 finding:〈原問題與範圍〉、〈回傳碼與判不了〉三分類、〈回退〉(`_drift_load_acks` 確實濾掉不認得的 kind,file: `scripts/lumos:37232`)、〈對消費專案的影響〉(除 F8)、其餘驗收條款。
- 查證通過的帳:18 次 reminded 合計 47 篇、recorded 5、none 12,和 `docs/.governance-log.jsonl` 一致。
- 測試名稱存在:〈實務隱患〉列的 10 個測試名稱和 `t_ci_yml_matrix_and_gates_shape` 在 `scripts/test_lumos.py` 都找得到。

### 實務隱患鏡頭(逐類)
- **金流**:無。只動本機掛鉤與回傳碼。
- **不可逆**:無。
  - 擋下只是讓推送失敗,表態檔只追加。
  - 要注意 `blocked`(`hard=True`)寫進版控帳 `docs/.governance-log.jsonl`,擋一次髒一次,但它在簿記名單內(`scripts/lumos:26892`),不影響留痕。
- **對外送出**:有。
  - prepare 會把筆記全文與程式 diff 交給判定模型,Codex 時是外部服務。
  - 緩解是設 warn/off,spec 已寫;F4 提到的「改設定要提交」是補充。
- **守衛面**:有。
  - 設定從被推頂端讀,可在同一提交自我解除,spec 已承認。
  - `--no-verify` 沒有 CI 兜底。
  - 沒有其他新旁路,但 F1 的死迴圈會把人推向 `LUMOS_SKIP_REREAD_CHECK`,正好撐大 RETIRE-IF 第一條。
- **併發/資源**:有。
  - 第一層從只列目錄變成讀全部紀錄內容(上限 8 MB)。
  - 30 秒預算逾時變成擋推送,與 m1/retire 的先例一致,未見新洞。
  - 平行會談:record 的 `git add` 改列具體檔名正好補洞,但 prepare 與 check 仍印整個資料夾(file: `scripts/lumos:34787`、`:34988`),不一致,屬 minor,未單獨列。
- **資安(路徑與跳脫)**:無新洞。
  - spec 要求從紀錄與筆記來的字串一律過 `_note_reread_show`。
  - 含控制字元的候選已被排除,非 UTF-8 路徑不印可照貼指令。
  - 子字串比對沒有正規式風險。
- **相容/升級**:有。新掛鉤配舊工具回 2 會放行;舊掛鉤配新工具不帶 `--gate`,維持提醒。已涵蓋。

最嚴重的是 F1(來源核對沒過的紀錄會讓第一層走進死迴圈,`wip` 扣除與 record 訊息都沒配套);blocking 共 1 條,其餘 8 條 minor 都不擋。
