severity: major

派工尾端沒附固定席節點,所以沒有要逐條判的節點。本輪實驗放在 `/tmp/lumos-seat-work/舊句兩道轉擋/併發3-sonnet/`。

### F1 「已對照」改成只認 provenance_ok 之後,工作目錄的 wip 比對沒跟著改,S7 做不出來
severity: major
blocking: 是
判準:照字面實作,S7 要求的行為不可能成立,而且擋下後給的指令會帶人走進死路。

- spec 段落:〈重讀:候選與兩層〉的「已對照」共用口徑,以及 S7。
- 引句:「所以只有來源核對沒過的紀錄時,check 擋、prepare 也會重產項目檔(不用 `--all`)」
- 引句:「reread-prepare 不帶 `--all` 也應為它產項目檔」
- 時序:
  1. 某篇的判定紀錄 `provenance_ok` 為 false,但已經提交。
  2. 帶 `--gate` 的 check 把它當沒對照,擋下,並印出 prepare 指令(不帶 `--all`)。
  3. 使用者照貼 prepare。
- 壞在哪:
  - spec 只把 `_note_reread_committed` 換成 `_note_reread_covered`,沒提 `_note_reread_uncommitted`。
  - `_note_reread_uncommitted` 實際列的是工作目錄資料夾裡所有符合檔名正規式的檔,包含已提交的。file: `scripts/lumos:34712-34724`。
  - prepare 用 `wip = _note_reread_uncommitted(root) - done`,所以那份「已提交但來源沒過」的紀錄落進 wip,被排出 todo。file: `scripts/lumos:34781`。
  - 結果是 prepare 印「紀錄還沒提交」,不產項目檔。
  - check 的 `wip` 提示同樣出錯,會叫人 `git add && git commit` 一份早已提交的檔。file: `scripts/lumos:34987`。
  - 擋住之後只有加 `--all` 或 `LUMOS_SKIP_REREAD_CHECK=1` 能脫身,但擋下訊息印的指令不帶 `--all`。
- 實驗:`python3.14 exp2.py`。臨時 repo 裡提交一份 `provenance_ok:false` 的紀錄,工作目錄乾淨,輸出如下。
```
git status clean: True
committed(fps in tip tree): {'0123456789abcdef'}
covered (spec: provenance_ok only): set()
wip = _note_reread_uncommitted(root) - covered = {'0123456789abcdef'} <- prepare 會當成'還沒提交'略過
```
- 修法方向:wip 只能是「工作目錄有、而且不在頂端樹裡」的檔。

### F2 掛鉤檔來自主工作目錄、工具來自各工作樹;舊掛鉤搭新工具時擋整個失效且沒有任何訊號
severity: major
blocking: 是
判準:「本機預設擋」的核心合約在常見的多工作樹配置下會靜默落空,而 spec 只處理了「新掛鉤搭舊工具」這一個方向。

- spec 段落:〈開關〉的 `--gate` 旗標、〈掛鉤與 CI〉、〈對消費專案的影響〉。
- 引句:「不帶時(CI、手動跑)不論設定都照舊只印、回 0、記既有事件。只有推送前掛鉤帶 `--gate`。」
- 引句:「標準錯誤照其他會擋的閘不丟(擋下原因在那裡;舊版工具的用法說明也會印出,這是部分更新時的已知雜訊)」
- 時序:
  1. 這台機器 `core.hooksPath` 是絕對路徑,指到主工作目錄。實測:`git config --get core.hooksPath` 回 `/Users/enzo/harness/lumos-toolchain/scripts/hooks`,而我審的這份 repo 是 linked worktree。
  2. 本案合進 main 後,各工作樹的 `scripts/lumos` 已是新版,但主工作目錄還沒 pull,掛鉤仍是舊的、沒帶 `--gate`。
  3. 在工作樹推送時,新工具收不到 `--gate`,config 預設 block 也不會擋,只印舊式提醒。
- 壞在哪:
  - 實驗確認掛鉤檔取自主工作目錄,工具卻取自 `$REPO_ROOT/scripts/lumos`(推送所在工作樹)。這種版本錯位是日常狀態。
  - `lumos enforcement` 只查 `core.hooksPath` 是否指向本專案,以及工作樹自己的 `scripts/hooks/pre-push` 是否存在。它不看實際被執行的那份掛鉤有沒有 `--gate`。file: `scripts/lumos:25786-25795`。
  - 治理帳裡 `blocked` 會是 0,RETIRE-IF 與 REVISIT 的量測會把「沒擋」誤讀成「沒問題」。
  - 新掛鉤搭舊工具(回 2、放行並印用法)spec 已寫。舊掛鉤搭新工具這個方向沒寫,也沒訊號。
- 實驗:
```
$ git init main; git worktree add ../wt -b feat; git config core.hooksPath <main>/scripts/hooks
$ (在 wt 內 git push)
HOOKFILE=…/exp/main/scripts/hooks/pre-push TOP=/private/tmp/…/exp/wt  VER=old(no --gate)
```
- 修法方向:
  - 工具在非 CI、有帶 `--push-remote`、沒帶 `--gate` 時,印一句「掛鉤沒帶 `--gate`,這次不擋」。
  - 或讓 doctor 與 enforcement 讀實際生效的掛鉤檔,查有沒有 `--gate`。

### F3 spec 說要改 CI 裡 drift 步驟的逃生句,卻又說 CI 步驟指紋測試照舊
severity: minor
blocking: 否
判準:實作者會先撞到紅燈,是文字矛盾,不是執行時錯誤。

- spec 段落:〈開關〉的連帶改清單、〈實務隱患〉末段。
- 引句:「`_drift_check_c` 在 gate=off 時的提示句、推送前掛鉤與 CI 那兩處」
- 引句:「CI 那一步不改,`t_ci_yml_matrix_and_gates_shape` 的步驟指紋照舊。」
- 壞在哪:
  - 「改 gate 沒用」的逃生句在 CI 裡是 drift 步驟 `run` 的 `::error::` 那行。file: `.github/workflows/ci.yml:242`。
  - drift 步驟本身受指紋釘住,`"drift check (存量漂移檢查;--no-verify 後盾)": "f6f6bc3db304d1e7"`。file: `scripts/test_lumos.py:62209`。
  - `_dr_ci_step_fp` 把 `run` 內容算進指紋,所以改了那句話,指紋就變。
  - 要改 CI 那句話,就得連指紋一起改,而 spec 沒把這個測試列進要改的清單。

### F4 規則類條目的「作廢」例外只給了 `RULE:`,測試綁定那一類標了 superseded 仍擋
severity: minor
blocking: 否
判準:正規的作廢寫法放不了人,只剩「照留」這個說法相反的出口。

- spec 段落:〈重讀:候選與兩層〉規則類條目定義。
- 引句:「或以摘要前綴開頭(前綴清單取專案既有的摘要前綴表,不另寫)且含 `TEST_REF_RE` 認得的測試綁定」
- 壞在哪:
  - 只有 `RULE:` 那一支寫了「沒標 `[status:superseded]`」。
  - 帶 `[test:]` 的 `WHY:` 或 `PITFALL:` 若被正式作廢(`[status:superseded]` 加 `[被取代:]`),引句通常還留在條目裡,第二層仍判它要處理。
  - 作者只能 `drift ack`(語意是「這行照留」),或硬改引句,與作廢的原意相反。

### F5 spec 沒寫 reread 表態從哪棵樹讀
severity: minor
blocking: 否
判準:漏寫一個既有慣例就能補,但字面實作可能選錯預設。

- spec 段落:〈照留表態〉。
- 引句:「同一條目的所有 reread 表態取 `verdicts` 聯集(不取 seq 最新),點出某列的紀錄指紋在聯集裡就算涵蓋。」
- 壞在哪:
  - 判定紀錄明寫「頂端提交」,表態來源卻沒寫。
  - `_drift_load_acks(root, where=None)` 預設讀工作目錄。file: `scripts/lumos:37220`。
  - 預設 `where=None` 的讀法,會讓工作目錄裡沒提交的表態放行推送,推上去的提交卻沒有它,而且被推的分支未必是目前 checkout 的那條。
  - 既有慣例是 check 傳 `tip`(`scripts/lumos:38647`),而且 `cmd_drift_ack` 結尾也叫人提交表態檔。
  - spec 需明寫「從頂端樹讀」。
  - 擋下訊息也該提醒「表態要提交」,否則作者表態完不提交再推,會原樣被擋兩次。

### F6 既有 `_NoteRereadStop` 的丟出點沒逐一對到三類回傳碼
severity: minor
blocking: 否
判準:字面實作可能把「git 失敗」誤歸成放行,屬於分類表漏項。

- spec 段落:〈回傳碼與判不了〉。
- 引句:「判不了(`undecidable`、逾時、判定紀錄讀不了或讀不懂、沒預料的例外):設定是 block 時回 1」
- 壞在哪:
  - 現在的 `_NoteRereadStop` 同時用於參數錯和 git 失敗。file: `scripts/lumos:34932`、`34935`、`34939` 是參數錯,`34959` 是起點算不出,`34972` 是列不出已提交紀錄,`34400-34420` 是掃描的 git 失敗。
  - spec 只把參數錯(回 2)、`undecidable` 和逾時分了類。
  - 「起點算不出來」「掃描 git 失敗」「列不出已提交紀錄」沒有歸屬,還有一個 `_NoteRereadStop` 丟出的子型別(已知 `ls-tree` 失敗改記 `undecidable`)。
  - 若沿用「`_NoteRereadStop` 統一記 skipped、回 0」就是 fail-open,與 drift 同題的做法相反。
  - 補一句「所有 `_NoteRereadStop` 除參數錯外一律歸判不了」即可。

### F7 直推 main 時,非快轉被拒後 rebase 會讓所有判定作廢,追不上
severity: minor
blocking: 否
判準:屬於 Enzo 已接受的第一層成本,但「同時推送加重試」這個最壞時序 spec 沒點名。⚠ 我沒實測 remote 競速,只依指紋定義推論。

- spec 段落:〈重讀〉第一層、〈實務隱患〉第一條。
- 引句:「程式改了(含合併主線帶進別人對同一支程式的改動、筆記改名、about_code 增減)就要重判」
- 時序:
  1. 兩個工作樹都直推 main,都改 `scripts/lumos` 加各自的家筆記。
  2. A 在掛鉤通過後被遠端以非快轉拒絕,`git pull --rebase`。
  3. B 那次推送改了 `scripts/lumos`,A 的候選指紋全變,第一層重擋。
  4. A 重派判定(幾分鐘、每篇約 0.17 美元)後再推;若這時 B 又推,就得再來一輪。
- 依據:對照指紋含 about_code 每一項的頂端 blob。file: `scripts/lumos:34459-34470`。
- 出口:只有 `LUMOS_SKIP_REREAD_CHECK=1`。這是 spec 已接受的成本,只是「非快轉重試」沒列在 RETIRE-IF 的量測口徑裡。

### F8 判定紀錄永久不過期,加上表態以整條原文為鍵,「點過一次的規則行」只增不減地越積越多
severity: minor
blocking: 否
判準:是 spec 自己寫明的「刻意保守」,但長期摩擦沒進 RETIRE-IF。⚠ 沒做大量實測。

- spec 段落:〈第二層〉、〈實務隱患〉第三條。
- 引句:「舊紀錄點出、新紀錄沒點出的規則類條目也會擋,是刻意保守」
- 壞在哪:
  - 紀錄只增不減,引句只要還在筆記裡,該條目就永遠算被點出。
  - 表態以整條原文(接續行併回後)為鍵。每次例行改那條,例如更新 `[confirmed:]` 日期,舊表態就對不上。
  - 之後任何人(含不是原作者的人)只要又改到這篇的程式和筆記,就會被舊紀錄擋下,得重新表態。
  - 表態檔 `governance/drift-acks.jsonl` 沒有 `merge=union`(`.gitattributes` 查無),兩條分支各自追加表態時會有結尾衝突。
  - RETIRE-IF 只抽樣誤報率,沒量這個累積摩擦。

### 逐節結論
- 原問題與範圍:已讀,無 finding。
- 〈開關〉(名稱消失檢查):已讀,無 finding。
  - 補一個測試缺口(minor):`gate=off` 加 `old_sentence` 沒寫時 m1 不跑,這個行為變化沒有對應的 S 條款。
- 〈開關〉(重讀):見 F2。
- 〈候選與兩層〉:見 F1、F4、F8。
- 〈回傳碼與判不了〉:見 F6。
- 〈輸出〉:見 F5。
- 〈照留表態〉:見 F5。
- 〈掛鉤與 CI〉:見 F2、F3。
- 〈要一起改的說法〉:見 F3。
- 〈對消費專案的影響〉:已讀,無 finding。
- 驗收條款:S7 見 F1,其餘已讀,無 finding。
- 〈實務隱患〉與〈回退〉:見 F7、F8。已讀,無其他 finding。

### 實務隱患鏡頭逐類
- 金流:無。只動本機掛鉤與工具回傳碼,我沒找到任何付款或計費路徑。
- 不可逆:無。
  - 擋下只是推送失敗,改設定或 `git rm` 判定檔都能復原。
  - 表態檔只追加。
  - `hard=True` 的 blocked 事件會進版控帳(`scripts/lumos:1477-1483`,只有 `hard is False` 的才走本機帳),這與其他閘一致,屬既有行為。
- 對外送出:有,spec 已列。
  - 判定要把筆記全文與程式 diff 送出,擋下訊息預設印 prepare 指令,同時也印了 `note_reread.gate` 改 warn 的寫法,沒有新的遺漏。
- 併發與多工作樹:有。
  - 見 F2(掛鉤與工具版本錯位)、F7(非快轉重試)、F8(表態檔合併衝突)。
  - 判定紀錄用隨機檔名、暫存檔不入集合,寫入端衝突我沒找到問題。
- 守衛面:有。
  - 見 F2。
  - `--no-verify`、設定在頂端自我解除、把程式與筆記拆成兩次推送使候選不成立,spec 已承認或屬原設計前提,不另標。
- 效能與逾時:無新增。
  - 判定紀錄讀取有 256 KB 單檔與 8 MB 總量上限和共用 deadline,逾時歸判不了,按 block 擋。出口是 `LUMOS_SKIP_REREAD_CHECK=1`,RETIRE-IF 已有此量測。

最嚴重的是 F1(prepare 與 check 的「已對照」口徑中途分家,S7 做不出來且擋下後給的指令是死路)與 F2(舊掛鉤搭新工具時整個擋靜默失效),blocking 共 2 條(F1、F2),其餘 6 條均為 minor 且不 blocking。
