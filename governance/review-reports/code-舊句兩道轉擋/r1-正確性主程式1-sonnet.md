severity: minor

這次 Bash 全部報 ENOSPC(磁碟滿,連指令輸出檔都寫不出來),clone 沒建成,測試和最小重現都沒跑。以下全部是讀真檔 `scripts/lumos`、`scripts/hooks/pre-push` 逐路徑走出來的,兩條 finding 都標「未能重現」。

## F1 reread-record 寫得出超過讀端上限的判定紀錄,之後該筆記的每次推送都會被擋
severity: minor
blocking: 否
引句:「_NOTE_REREAD_VERDICT_MAX = 256 * 1024」
file: `scripts/lumos:34356`、`scripts/lumos:35090-35091`(`reread-record` 把 `r["text"]` 設成整條實體行,沒有截斷)

1. 寫端:`_note_reread_rows` 只把 `quote`、`why` 各截到 500 字,`reread-record` 卻把 `text` 設成筆記該行的完整內容,沒有上限。一份紀錄的列數最多等於筆記行數。
2. 讀端:`_note_reread_verdicts` 用 `_nodehome_cat_blobs_capped` 讀,單份超過 256 KB 就丟 `_NoteRereadStop`。
3. 輸入:筆記第 5 行是 300 KB 的貼上資料,判定者點出第 5 行。
   - `reread-record` 照收並寫檔。
   - 下一次有候選的推送,在 `_note_reread_judge` 讀紀錄時走到 `_note_reread_unread_why`,印「判定紀錄 … 超過 256 KB 上限」。
   - block 加 `--gate` 時回 1。
4. 影響:出口只有 `git rm` 那份,而且還要重判。同一筆記的所有後續推送都被擋,不只這一份。
5. 規格 S17 把「紀錄讀不懂就擋」當成預期。但寫端製造出自己讀端會拒絕的檔,是寫入慣例和讀取保證不對稱。
6. 失敗場景不常見:要有極長行,而且判定者剛好點到它。所以只標 minor。

## F2 還沒提交且來源核對沒過的紀錄,會讓 reread-prepare 略過重派,與 record 剛說的「請重派判定者」相反
severity: minor
blocking: 否
引句:「if m and f.is_file() and f.name not in committed:」
file: `scripts/lumos:34830`(`_note_reread_uncommitted`)、`scripts/lumos:35098`(record 的「請重派判定者」提示)

1. 輸入:判定報告的 `model:` 開頭行與項目檔不符。
   - `reread-record` 寫出 `provenance_ok: false` 的紀錄。
   - 它印「這份不算對照,請重派判定者」。
   - 紀錄還在工作目錄,尚未提交。
2. 照提示馬上跑不帶 `--all` 的 `reread-prepare`:
   - `_note_reread_covered` 只收 `provenance_ok` 為真的,所以 `done` 是空集合。
   - `_note_reread_uncommitted(root, tip)` 只比檔名(合規且不在頂端樹),不看 `provenance_ok`,所以這份的指紋進了 `wip`。
   - `todo = [... if fps[rel] not in done and fps[rel] not in wip]` 把這篇排除。
3. 結果:印「已對照 … 其中 N 篇紀錄還沒提交,記得提交」和「都對照過這一版程式了,不產項目檔」,回 0。
   - 使用者被引導去 `git add` 一份不算對照的紀錄。
   - 提交後 check 才說「來源核對沒過」,再跑一次 prepare 才會產項目檔。
4. 規格 S7 只規定「已提交」的來源核對沒過紀錄。工作目錄版本沒有規定,但 `_note_reread_uncommitted` 的 docstring 寫「只影響提醒的措辭」,實際上它也決定 prepare 要不要產檔。
5. `--all` 可繞過,所以只標 minor。

## 規格對照(逐條判定)
- S1–S4、S26 照做。`_drift_old_sentence_config(cfg, bad, gate)` 在沒寫、null、值看不懂時回 gate。讀不成 JSON 和整份不是物件回 `_DRIFT_DEFAULT_GATE`。gate=off 時沒寫的項目變 off,明寫的值照原義。
- S5、S6、S8 照做。block 加 `--gate` 走 stderr 的「擋下:」、印 prepare 指令、記 `blocked`,而且不印 TAIL。不帶 `--gate` 時恆回 0,事件為 `reminded`。
- S7:已提交、來源核對沒過的情況照做,見 F2 對工作目錄版本的缺口。
- S9–S15 照做。
  - 比對字串少於 6 字會略過。
  - 找不到比對字串算處理過。
  - 表態以 verdicts 聯集比對。
  - 接續行會歸回條目開頭。
  - 單行 summary 有補寫。
  - 兩層只記一筆 `blocked`。
- S16–S19 照做。`_note_reread_rc` 的分類與規格一致:參數錯回 2,環境沒東西回 0,其他判不了在 block 時回 1。`_NoteRereadArgErr` 只由 `_note_reread_args` 與 range 的 `error` 種類丟出,其餘 `_NoteRereadStop` 與未預期例外都算判不了。
- S20–S22 照做。`_drift_ack_reread_line_err` 與 `_drift_ack_kind_fields` 在寫帳前都會回 2。`--kind` 的 `choices=_DRIFT_KINDS` 已含 reread。`--tracked-in` 因 reread 不在 `_DRIFT_EXPIRING_KINDS` 而被拒。`_DRIFT_SCAN_KINDS` 排除 reread。
- S23:真檔掛鉤 `scripts/hooks/pre-push:537` 帶 `--gate`,128 以上交 `pp_stop_if_signaled`,1 擋下,其他非零放行。
- S24:提示字樣與具體檔名照做。
- S25:`_enforcement_prepush_ungated` 只認非註解行。全檔 `note-audit reread-check` 只在第 537 行有非註解出現且帶 `--gate`,沒有誤判。

## 圖譜鏡頭
派工詞說這次沒附固定席節點(鏡頭計算超時),不必逐條答。我只確認:`_KNOWN_GATES` 的 `note-reread` 註解已更新。`("note-reread", reminded|covered|none)` 且 hard 為 False 仍走本機帳,`blocked` 帶 `hard=True` 走版控帳,分流沒被破壞。

## 角色鏡頭(後端卡)
- be-api-compat:
  - `--gate` 是新增旗標,舊掛鉤不帶它時,新工具印一句「掛鉤沒帶 --gate,這次不擋」,`lumos enforcement` 也會列為沒接上。
  - 新掛鉤搭舊工具時,argparse 回 2,掛鉤放行並提示。
  - 判定紀錄的欄位沒變,舊工具讀新紀錄沒問題。
  - 新表態的 `kind: reread` 靠 `_drift_load_acks` 只收 `_DRIFT_KINDS` 內的種類而被略過。我沒有讀到舊版程式碼,這點是依規格推定。
- be-authz:
  - 沒有新端點。表態的資格只是工作目錄有紀錄點出那一條。
  - 同一次推送也可以把 `note_reread.gate` 改成 warn,這是規格〈實務隱患〉已承認的既有性質,不另列。

## 效能(不成 finding)
- 讀判定紀錄有 256 KB 與 8 MB 的上限,是有界的。
- `_note_reread_layer2` 對同一篇候選的每份紀錄都重新 `_reread_summary_entries(texts[rel])`,每列又掃全部實體行,且第二層內部沒查 `deadline`。在上限內成本有界,我給不出會超過 30 秒軟上限的具體輸入,所以沒標。
- `_note_reread_tip_names` 在一次 check 內被呼叫兩次(`_note_reread_verdicts` 與 `_note_reread_uncommitted`),多一次 `ls-tree`,影響不大。

最高等級:minor(F1、F2,皆未能重現)。
