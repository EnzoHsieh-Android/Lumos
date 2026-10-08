severity: major

# r3 邊界席(sonnet)——治理帳例行紀錄分流 第 3 版

範圍:只看 blocking 級與「第 2 輪的修正有沒有改對」。r2 折入的項目(白名單、hard 恰好 False、舊檔凍結、docs/.gitignore 不存在就建、尾端補換行、取路徑函式吃 docs 資料夾)我逐項對過程式碼,方向都改對了,不重報。實驗在 /tmp/r3e 的暫時 git repo 做,沒動 /home/user/Lumos。

白話:本機帳的「門」(忽略規則)裝了,但門還沒裝好的那段時間,有人把帳整個搬進版控,工具會把它當成「改了程式」,代碼審的通過紀錄就作廢、推送被擋。這個洞 r2 回滾席提過,r3 沒補。

1. 本機帳被提交進版控時,不在簿記白名單,會讓代碼審留痕失效而擋推
severity: major
blocking: 是(判準:會在正常操作序列下讓推送被擋、且被提交後檔案永久進版控,無法靠還原本案提交回到原行為)
引句:「全域工具更新後到專案跑 `lumos update` 之前,本機帳會以未追蹤檔出現(偏吵)」
場景:消費專案先拿到新版全域工具、還沒跑 `lumos update`(沒有 docs/.gitignore 或沒有那兩行)。提交前 hook 寫出 `docs/.governance-local.jsonl`,使用者或 AI `git add -A` / `git add docs`,本機帳進了提交。之後代碼審 pass 留痕要判「pass 之後有沒有只動簿記檔」:`_codeloop_record_valid_ex` 以 `_BOOKKEEPING_FILES` 為準,這兩個新檔名不在裡面,於是回「記錄 sha 之後動了代碼(非純簿記增量)」,留痕失效、要重審才能推。檔案一旦被追蹤,之後補上忽略規則也沒用(`.gitignore` 不管已追蹤的檔),兩台機器各自追加還會 merge 衝突,而且 `_pull_source_or_abort` 的 append-only 聯集合併也不認它。spec 只把這段寫成「偏吵」,〈做法〉7 的同步範圍、〈範圍〉都沒有「把兩個新檔名加進 `_BOOKKEEPING_FILES` 與 `_COCHANGE_DEFAULT_EXCLUDE`」這一項;r2 回滾席 `r2-回滾-sonnet.md:45,48` 已提,r2-intake 沒有處置紀錄,r3 也沒折。
修法方向:新兩個檔名進 `_BOOKKEEPING_FILES`(兩行,一次加好),舊 `.usage-log.jsonl` 保留(舊版來源 clone 仍要);加一條測試釘「只動本機帳的提交不讓留痕失效」。
佐證:file: `scripts/lumos:24193`(`_BOOKKEEPING_FILES` 無新檔名);file: `scripts/lumos:43398`(`all(f in _BOOKKEEPING_FILES ...)` 才豁免,否則 43400 回「動了代碼」);file: `scripts/lumos:36523`(`_COCHANGE_DEFAULT_EXCLUDE` 同樣沒有);file: `scripts/lumos:20585`(來源髒檔聯集合併只認 `_BOOKKEEPING_FILES`)。

2. doctor 軟提醒「本機帳存在但沒被忽略」沒定義怎麼判斷,三種邊界各有不同結果
severity: minor
blocking: 否(判準:只是軟提醒、不影響任何判定,但實作者照字面寫會在三種情境給出錯的提示)
引句:「本機帳存在但沒被忽略時,提示跑 `lumos update`」
我在 /tmp 暫時 repo 實驗(`git check-ignore -q <路徑>`):
- 非 git 目錄:回傳 128(fatal: not a git repository)。若實作寫成「回傳非 0 就提醒」,非 git 的 vault 每次 doctor 都會喊「沒被忽略」。要明寫:128 視為不適用、不提醒。
- 本機帳已被提交進版控(即第 1 條的情境):`check-ignore` 回 1(已追蹤的檔不算被忽略),加 `--no-index` 才回 0。照字面會永遠提示「跑 `lumos update`」,但 update 補忽略規則救不了已追蹤的檔——提示變成永遠消不掉的假警報。要嘛提示改說「已被追蹤,需 `git rm --cached`」,要嘛判斷用 `--no-index` 並另外單獨檢查 `git ls-files`。
- 本機帳檔案不存在:`check-ignore` 仍照規則判斷,不會出錯;spec 寫「存在」才提醒,所以這格是對的,但測試要涵蓋。
佐證:file: `scripts/lumos:16181`(`_usage_log` 無檔也靜默吞錯,所以「存在」是合理的前提);程式裡目前沒有任何 `check-ignore` 呼叫(grep 為空),這段是全新邏輯,不能抄既有先例。

3. 舊 vault 新建的 docs/.gitignore 會把 bypass / kill / signoff / canary 帳也一起藏起來
severity: minor
blocking: 否(判準:不改任何判定、不讓已追蹤檔消失;影響限於「尚未提交過」的帳檔,偏丟不偏吵)⚠ 判不準這些帳在舊消費專案是否本來就期待被提交
引句:「內容同新建 vault 的那份;已追蹤的檔不受 .gitignore 影響」
場景:2026-08-21 之前建的 vault 沒有 docs/.gitignore(忽略檔當時寫在 vault 裡、對上一層無效)。這類專案的 `docs/.bypass-log.jsonl`、`.kill-log.jsonl`、`.signoff-log.jsonl`、`.canary-log.jsonl` 若還沒被提交過,現在是「看得到的未追蹤檔」,使用者可能會提交;`lumos update` 建了新 docs/.gitignore 之後它們全被忽略、再也不會出現在 git status。spec 的保證只涵蓋「已追蹤」的檔。本 repo 自己是把這四本當版控帳刻意追蹤的(〈盤點〉第 1 條),繞道痕跡「照舊進版控」這句承諾對這批舊消費專案就不成立。要嘛 init 對舊 vault 只補本案兩行(不建整份新建 vault 的清單),要嘛在 update 輸出明講「這幾本帳從現在起被忽略」。
佐證:file: `scripts/lumos:20878-20880`(新建 vault 的忽略清單含 bypass/canary/kill/signoff/usage/ci);file: `scripts/lumos:20885-20906`(`_init_additive_setup` 目前只處理 governance/.gitignore)。

4. 逐行比對「去頭尾空白」與 git 的語意不一致;追加時的換行與 CRLF 保存沒定
severity: minor
blocking: 否(判準:極端輸入下才發生,後果是忽略規則沒生效而變成偏吵的未追蹤檔)
引句:「存在就逐行比對(去頭尾空白、容許 CRLF,整行相等才算有)」
實驗結果:
- CRLF 行尾的 `.gitignore` 在 git 裡照樣生效(`.usage-local.jsonl\r\n` → `check-ignore` 回 0),所以「容許 CRLF」的比對方向是對的。
- 前導空白不同:` .usage-local.jsonl`(開頭一個空白)git 當成檔名含空白的規則,`check-ignore` 回 1(沒忽略)。spec 的「去頭尾空白」會把它當作「已有」而不補,結果本機帳實際沒被忽略。尾端空白 git 本來就忽略,所以只該去尾、不該去頭。
- 追加用的換行:原檔是 CRLF 且沒有結尾換行時,spec 只說「補一個換行」,沒說補 `\n` 還是 `\r\n`;若實作是 `read_text`(通用換行)再用 `_write_lf` 寫回,整檔 CRLF 會被一次轉成 LF,違反同一條自己說的「只加不改既有行」(位元組層級會動到每一行,tracked 的 docs/.gitignore 會整檔變 diff)。要寫明用位元組讀、只在尾端接,沿用原檔的行尾風格。
- 無結尾換行直接接:實驗確認會得到 `.usage-local.jsonl.governance-local.jsonl` 單行(兩條規則一起失效),所以「先補換行」這步是必要的,spec 有寫、S5 有測,這點沒問題。
佐證:file: `scripts/lumos:17605`(`_write_lf` 一律 LF、tmp+replace;若 docs/.gitignore 是 symlink 也會被換成一般檔);file: `scripts/lumos:20879`(新建那份用 `\n`)。

5. 兩本帳「依時間排序」沒定義比較方式與壞 ts 的處理
severity: minor
blocking: 否(判準:只影響統計與 doctor 的軟提醒;判定類讀者不讀本機帳)⚠ 未實跑,從程式現有注釋與讀法推得
引句:「把兩本帳合起來、依時間排序後算,同一組事件分流前後結果相同」
場景:既有程式自己承認兩種寫入者時區不同(`_gate_event_build` 用本機時區、code-loop 用 commit 作者時區,見 doctor 帳本成長段 `scripts/lumos:2238` 附近的註解),字串直接排序在不同時區偏移混用時不等於時間順序;DST 切換當天本機時區自己也會錯。另外 ts 缺欄位或非字串的行(既有讀者都會 `isinstance(_tv, str)` 跳過)若用 `sorted(key=ts)` 直接排,會拋 TypeError 讓整個 doctor 段落掉進 `except` 變成「這一段算不出來」。S3 的條款「同一組事件分流前後結果相同」要成立,排序必須用解析後的時間、壞 ts 的行要有固定處置(跳過或放最前),spec 沒寫。同一個 `_append_governance_log` 一批事件共用同一個 ts(`scripts/lumos:1423`,秒級),同秒多筆要穩定排序,否則「取最後一筆 spec-gate-run」可能換人。
佐證:file: `scripts/lumos:1286`(`_gate_event_build` 的 ts);file: `scripts/lumos:2862-2872`(spec-gate 段目前「檔案順序最後一筆勝出」,改成排序後要保持同語意)。

總結:r2 的核心修正(白名單、hard 恰好 False、舊檔凍結、docs/.gitignore 補建與尾端換行)方向都對;剩下唯一擋得住推送的洞是第 1 條——本機帳在被提交的情況下沒有被簿記白名單認得,補兩行 `_BOOKKEEPING_FILES` 並加一條測試即可;其餘四條是 minor,修不修都不阻擋收斂。
