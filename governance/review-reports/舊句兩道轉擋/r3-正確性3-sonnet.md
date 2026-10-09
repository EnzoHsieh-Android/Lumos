severity: major

派工尾端沒有附固定席節點,所以沒有可逐條判的節點。

## 已驗的既有函式
- `_note_reread_committed`、`_note_reread_uncommitted`、`_note_reread_cmdline`、`_note_audit_resolve`、`_note_summary_entries`、`_ns_summary_logical`、`INVARIANT_RE`、`TEST_REF_RE`、`_drift_old_sentence_config`、`_drift_retire_config`、`_drift_check_c`、`cmd_drift_ack`、`_drift_ack_line_err`、`_drift_ack_text`、`_drift_load_acks`、`_drift_m1_split_acked`、`_drift_fix_hint`、`_drift_sh`、`_drift_unknown_hint` 都開檔看過語意。
- 掛鉤 `scripts/hooks/pre-push`、`.github/workflows/ci.yml:247-264` 和真實判定紀錄 `governance/reread-verdicts/` 的 5 份也看過。
- 治理帳數字(18、12、5、47)我重算過,跟 spec 一致。
- 在 /tmp 的複製品跑 `reread-check --diff HEAD~40..HEAD`,18 篇候選共 2.7 秒,逾時不是現實風險。

### F1 prepare 的「工作目錄紀錄」略過邏輯沒跟著改,S7 做不出來,擋下後出口也被堵
severity: major
blocking: 是(照字面實作會讓 spec 自己承諾的行為做不出來,而且第一層擋下後沒有出口)

- **spec 段落**:〈重讀〉「已對照的共用口徑」那一條,以及驗收條款 S7。
- **引句**:
引句:「所以只有來源核對沒過的紀錄時,check 擋、prepare 也會重產項目檔(不用 `--all`)」
- **輸入或順序**:候選的紀錄是 `provenance_ok` 為假,而且已提交。
  1. 把 `_note_reread_committed` 換成 `_note_reread_covered` 之後,`done` 不含這份指紋,check 的第一層擋下,印出 prepare 指令。
  2. 照貼 prepare,`wip = _note_reread_uncommitted(root) - done` 只看檔名、不看 `provenance_ok`,也不看有沒有提交。這份紀錄在工作目錄裡,所以指紋進了 `wip`。
  3. `todo` 排除 `wip`,prepare 因此印「已對照 1 篇…略過」「其中 1 篇紀錄還沒提交」「都對照過…不產項目檔」,回 0。
  4. check 那邊 `wip = _note_reread_uncommitted(root) & {...}` 同理,會印錯誤的「還沒提交,git add…」。
- **壞在哪**:擋下訊息叫人跑 prepare,prepare 卻拒絕產檔,唯一出口是 spec 逃生段沒提的 `--all`,或 `LUMOS_SKIP_REREAD_CHECK`。spec 全文沒有提到 `_note_reread_uncommitted`。
- **查證**:file: `scripts/lumos:34774-34790`(prepare 的 `done`、`wip`、`todo`)、file: `scripts/lumos:34712-34723`(`_note_reread_uncommitted` 只比檔名正規式)、file: `scripts/lumos:34987`(check 的 wip 提示)。
- **現有測試**:`scripts/test_lumos.py:65389` 的 `t_note_audit_reread_prepare_skips_uncommitted_records` 只測 `provenance_ok` 為真的情況,抓不到這個。
- **取代後的呼叫端**:`_note_reread_committed` 全檔只有 prepare 與 check 兩個呼叫端,這兩處都要改成 `covered`。
- **要補的規定**:`wip` 也得套 `provenance_ok` 並扣掉頂端已有的檔,錯誤的「還沒提交」提示一併改。

### F2 單行 `summary:` 的規則類條目:第二層擋得到,表態卻簽不出
severity: major
blocking: 是(這種輸入沒有出口,只能略過或改 warn)

- **spec 段落**:〈重讀〉第二層的條目歸屬,對照〈照留表態〉的行號規定。
- **引句**:
引句:「用 `_note_summary_entries` 同一套讀法」
引句:「行號要是一條摘要條目的開頭行(跟 retire 一樣,記整條)」
- **輸入**:筆記寫成 `summary: "RULE:… [依據:人]…"`(整個 summary 只有一行)。
  1. `_note_summary_entries` 先呼叫 `_ns_summary_logical`,拿到空,再退回單行讀法,以 `summary:` 那一行為條目、值為原文。第二層因此會把它判成規則類而擋下。
  2. 「跟 retire 一樣」的表態卻走 `_drift_ack_line_err` 的 `line not in _ns_summary_logical(text)`,這對單行 summary 恆為真,所以回 2。
  3. `_drift_ack_text` 在 retire 分支拿不到 whole,退回 `lines[line-1].strip()`,記下含 `summary:` 與引號的整行,跟第二層的條目原文(去引號的值)對不上。
- **壞在哪**:兩邊口徑不同源,這種筆記一旦被點出就永遠擋。
- **查證**:我實測 `_ns_summary_logical('---\n…summary: "RULE:…"\n---')` 回 `{}`(file: `scripts/lumos:31963-31979`、`_notelines_regions` 在 `scripts/lumos:30347`,頂層鍵那一行標 other),而 `_note_summary_entries` 有單行補丁(file: `scripts/lumos:4027-4040`)。
- **需要的規定**:表態的行號驗證與記下的原文,要跟第二層共用同一支讀法。

### F3 「兩者都是空字串才略過」漏了「quote 非空但太短、text 是空白行」,空比對字串會命中每一條
severity: major
blocking: 是(照字面實作會把整篇的規則類條目全判成被點出,一次要簽一整批)

- **spec 段落**:〈重讀〉第二層「逐列決定比對字串」,對應 S12 與審計紀錄 r2 的例子。
- **引句**:
引句:「否則用 `text` 去頭尾空白;兩者都是空字串 → 這一列點不出任何行,略過」
- **輸入**:判定者把行號點在空白行(LLM 數行號常差一行),`quote` 填了「…」或少於 6 字的非空字串,`text` 是空白行。
  1. `quote` 不夠 6 字,改用 `text.strip()`,得到 `""`。
  2. 「兩者都是空字串」字面上不成立,因為 `quote` 非空,於是不略過。
  3. `"" in 某實體行` 對每一行都為真,筆記裡每一條規則類條目都算被點出,各要一筆表態。
  4. 表態那邊「某列比對字串出現在這一條」對空字串也恆真,所以不會有人察覺。
- **同族**:`text` 的退路沒有最短長度,只有 `quote` 有 6 字門檻。`text` 若是 `---`、`}` 這類短行,會命中大量不相干的摘要行。
- **壞在哪**:規則應該寫成「選定的比對字串為空就略過」,而不是 quote 與 text 都空。
- **查證**:真實紀錄的 `text` 取自 `lines[r["line"]-1]`,空白行會是空字串(file: `scripts/lumos:34868-34870`)。

### F4 S18 沒寫 `--gate` 前提,跟「不帶時全部回 0」互相矛盾
severity: minor
blocking: 否(實作者看設計段落多半會做對,但測試會被寫錯)

- **spec 段落**:S18 與〈回傳碼〉。
- **引句**:
引句:「推送參數只給一個或終點找不到時應回 2」
引句:「不帶時全部回 0、事件照舊」
- **壞在哪**:S18 的前提沒寫 `--gate`,不帶 `--gate` 的 CI 若真回 2,沒加 `|| true` 的消費專案 CI 會變紅,違反〈開關〉的相容承諾。S5、S9、S17 都有寫 `--gate`,只有 S18、S16 沒寫。

### F5 `_NoteRereadStop` 的非逾時來源沒歸進三類
severity: minor
blocking: 否

- **spec 段落**:〈回傳碼〉三類。
- **引句**:
引句:「判不了(`undecidable`、逾時、判定紀錄讀不了或讀不懂、沒預料的例外)」
- **壞在哪**:現有 `_note_reread_scan` 有四處 git 失敗會丟 `_NoteRereadStop`(file: `scripts/lumos:34400-34420`),`_note_reread_check` 還有「推送範圍的起點算不出來」(file: `scripts/lumos:34964`)。這些既不是 `undecidable`,也不是逾時。
- **風險**:照舊的 `except _NoteRereadStop → skipped → 回 0` 會讓這些情況在 `--gate` 下放行,違背 spec 自己的「判不了不放行」。
- **要補的規定**:明寫它們算判不了。

### F6 表態從哪棵樹讀、第二層怎麼歸屬條目,沒寫死
severity: minor
blocking: 否

- **spec 段落**:〈重讀〉第二層。
- **引句**:
引句:「實體行落在某條目的開頭行到下一條目之前,就屬於那一條」
- **兩個缺口**:
  1. 這句字面上會把最後一條之後的整個檔(`decisions:`、正文)都歸給它,全靠後面一句「不在摘要裡的實體行一律不算」補救。`_ns_summary_logical` 的 `cont` 參數才是正解,而 `_note_summary_entries` 沒回傳它。
  2. 本 repo 有 3 行屬於摘要區、卻不是條目也不是續行的雜行(`2026-06-19_canary-audit.md:19` 等),字面實作會歸給前一條。
- **表態來源**:spec 對第二層讀紀錄明寫「頂端提交」,對 kind=reread 表態沒寫從 `where=tip` 還是工作目錄載入。`_DRIFT_KINDS` 那句只說 `_drift_load_acks` 收,沒說樹(file: `scripts/lumos:37220`)。若用工作目錄載入,未提交的表態就能放行本機推送,但 CI 不會認。

### F7 設定逃生句沒講「要提交進被推的頂端才生效」
severity: minor
blocking: 否

- **spec 段落**:〈輸出〉逃生,與〈對消費專案的影響〉。
- **引句**:
引句:「另印 `LUMOS_SKIP_REREAD_CHECK=1 git push`(單次略過、會留帳)與 `note_reread.gate` 改 warn 的寫法」
- **壞在哪**:設定從被推頂端讀。預設改成 block 後,沒有判定者環境的專案會照字面只改工作目錄設定,重推仍被擋。

## 其餘段落
- **`--gate` 在各路徑的行為**:已讀,無 finding(除 F4、F5)。
  - 舊工具搭配新掛鉤時,argparse 回 2,按設計放行。
  - 新工具搭配舊掛鉤時,不帶 `--gate`,維持提醒。
  - 設定在被推頂端(`_nodehome_reader(root, tip0)`)讀,工作目錄設定只用於設定讀到之前的例外。
- **子開關跟總開關**:已讀,無 finding。唯一呼叫端是 `scripts/lumos:38497`,明寫值照原義,`gate=off` 搭 `old_sentence=block` 照跑也確認。
- **掛鉤、CI、帳**:已讀,無 finding。
  - 簿記白名單已含 `governance/reread-verdicts/` 與 `governance/drift-acks.jsonl`,所以紀錄與表態提交不會讓代碼審留痕失效。
  - `blocked` 帶 `hard=True`,會進版控帳。
  - `pp_stop_if_signaled` 對 128 以上一律停,語意跟 drift 一致。
- **[[Systems/存量漂移守衛]] 的舊 RULE**:已讀,無 finding。它在 `docs/lumos-toolchain-knowledge/Systems/存量漂移守衛.md:82`,欄位齊全、半年內確認過,有挑戰程式碼的效力。spec 以人裁翻案並標 superseded,做法正確。

## 實務隱患鏡頭
- **金流**:無。只動掛鉤與回傳碼,判定者費用是用量成本,不是付款路徑。
- **不可逆**:無。表態與紀錄只追加,`git rm` 紀錄可由 git 還原。
- **對外送出**:有,spec 已揭露。筆記全文與程式 diff 送判定模型,預設改 block 後,保密專案升級後第一次推送就被擋。補充見 F7。
- **守衛面**:有。同提交改設定自我解除是既有性質,spec 已寫;F1 的死路屬這一類,因為出口只剩略過。
- **併發**:無新增。`drift-acks.jsonl` 寫入有 `_vault_write_lock`,紀錄檔名帶 32 位亂數。
- **注入與跳脫**:無新洞。引句、路徑過 `_note_reread_show`,照貼指令過 `_drift_sh`。
- **效能與記憶體**:無。實測 2.7 秒,紀錄單檔 256 KB、總量 8 MB 有上限,現況 5 份約 7.8 KB。
- **相容**:除 F4 外無。新舊掛鉤搭配上面已逐條走過。

最嚴重的是 F1(prepare 的工作目錄紀錄略過邏輯沒改,第一層擋下後 prepare 拒絕產檔);blocking 共 3 條(F1、F2、F3),另有 4 條 minor。
