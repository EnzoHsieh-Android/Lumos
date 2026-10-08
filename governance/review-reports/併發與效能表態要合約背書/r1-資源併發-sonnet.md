severity: major

治理帳實測 97335 行、15MB,整檔讀一遍約 0.07 秒。緣起、用詞、題目、其他表態、教人、不做、驗收、回退、合約候選:已讀,無獨立 finding(合約候選與超時放行矛盾併入 F5)。

**F1**
severity: major
blocking: 是,後來被證明守不住的測試繼續拿到背書。
只在 killed 事件裡挑最新,之後的 survived/drifted/killed_unattributed 被忽略;「最新」沒說按檔案順序或 ts。
引句:「找同一個測試名、`verdict=killed` 的最新一筆」
file: `scripts/lumos:13199` kill-log 與治理帳只增不改;`docs/.kill-log.jsonl` 同一測試三筆 killed_unattributed 後才出現 killed。

**F2**
severity: major
blocking: 是,多平台專案的背書永遠判不過。
commit 各平台用 proot 取 --short HEAD、迴圈外只留最後一組;test 欄多平台時是 plat:name;files 是 proot 內相對路徑。
引句:「`commit`(跑的當下 HEAD)」
file: `scripts/lumos:13090` 用 proot 取 commit;`scripts/lumos:13119` 取 method_full;`scripts/lumos:13103` 處理 plat: 前綴。

**F3**
severity: major
blocking: 是,事件根本寫不進帳。
gate 名沒指定;`_gate_event` 不在 `_KNOWN_GATES` 就不寫;要改名單與漂移釘 t_gov_stats_gate_drift。
引句:「為每條配方各寫一筆 `kind=guard-kill`」
file: `scripts/lumos:1220` 閘名不在名單就不寫;`scripts/lumos:6943` `_KNOWN_GATES`。

**F4**
severity: major
blocking: 是,本專案規定推送前壓成一個提交,每次正規流程走完背書都變成沒有。
壓提交或 rebase 後寫帳時的 sha 不再是祖先;帳寫在工作樹追蹤檔,CI 讀不到未提交的;guard kill 在 worktree 或暫存目錄跑時帳落在那棵樹。
引句:「那筆的 `commit` 不是被推送版本的祖先」
file: `scripts/lumos:1215` 事件寫 root/docs 下;`scripts/lumos:36139` CI 只讀 tracked 的治理帳。

**F5**
severity: major
blocking: 是,超時放行與 block 模式合約自相矛盾。
deadline 只在題與題之間檢查;新 subprocess 沒有逐次 timeout;一超預算未查的題全部不判、不寫 warn,block 等於靜默放行,與合約候選衝突。
引句:「整道檢查的外層例外與超時才走 `_gate_failopen` 放行」
file: `scripts/lumos:37397` deadline 只在題與題之間檢查;`scripts/lumos:37537` 預算 _DISP_BUDGET=20.0;`scripts/lumos:36926` 定義。

**F6**
severity: major
blocking: 是,機率性競態的判斷只對了一半。
破壞測試只跑一次:突變後隨機紅就算 killed,是誤放行;flaky_risk 只標 yaml/maestro/playwright;強制交錯只在技能文件建議,沒有機械守衛。
引句:「方向是誤提醒而非誤放行」
file: `scripts/lumos:13102` flaky 只看 scaffold_ext 與平台名;`scripts/lumos:13139` verdict 單次決定。

**F7**
severity: major
blocking: 是,過期判定只看配方檔,背書可被後續改動掏空。
測試本身被改弱或其他保護檔改動,背書照樣有效;files 只來自 r.get("file")。
引句:「從那筆的 `commit` 到被推送版本之間,`files` 裡任一支檔有改動」
file: `scripts/lumos:13129` 只取 r.get("file") 做突變目標。

**F8**
severity: minor
blocking: 否,只影響統計與讀者預期。
gov 已把 .kill-log.jsonl 讀成 gate=kill 事件,新事件會讓同一次驗證出現兩套;沒有 token、去重沒說。
引句:「讀它的只有本案的檢查與 `lumos gov` 統計」
file: `scripts/lumos:7291` 第 5 源 load kill-log。

**F9**
severity: minor
blocking: 否,失敗方向是少背書。
寫入順序與中斷未定義;讀帳要容錯半筆;每條配方各開一次檔,寫入次數倍增,「不加重」不精確。
引句:「本案新增兩種事件走同一個寫入函式,不另開寫入點,不加重也不修它」
file: `scripts/lumos:13199` kill-log 迴圈外批次寫;`scripts/lumos:1234` 每次呼叫各開檔。

實務隱患:並行見 F1、F5、F6、F9;推送前 hook 與 CI 各讀各的 checkout,無共享讀寫點;資源見 F5;寫入位置見 F2、F4;沒有圖譜的專案與程式一致,無 finding。

最嚴重 severity:major;blocking 共 7 條(F1–F7),F8、F9 為 minor。
