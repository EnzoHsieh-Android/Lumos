severity: major

審查範圍:併發席。逐節讀完 spec(範圍、做法 1 到 5、條款、回退、實務隱患、誠實界線),對 clone-ns 的程式碼逐項核對;做過一個實驗(下面 F5、F6 引用)。

## F1 --values 整欄取代只驗「c4 消失」,證據頁到寫入之間別的會談改過同一欄會被靜默蓋掉
severity: major
blocking: 是
引句:「用 `_conditions_rewrite(lines, fe, "valid_under", vals)` 算改後內容(有錯回 2)」
file: `scripts/lumos:15153`(`_set_conditions_locked` 對現有欄位整段 `fm[a:b + 1] = new`)
file: `scripts/lumos:27792`、`scripts/lumos:28086-28100`(乾淨檢查只比 HEAD 或修復帳指紋;寫入鎖內只比「判定時讀的位元組」)
1. 時序:會談 A 跑不帶 `--values` 的證據頁,印出 valid_under 三項(時間點 T1)。會談 B 用 `lumos set` 往 valid_under 加第四項並提交(或別人 pull 進來一個提交)。會談 A 隔幾分鐘照證據頁貼上 `--values 項1 項2' 項3`(T2)。
2. `cmd_drift_fix` 在 T2 才讀檔、取 `cx["raw"]`,乾淨檢查因 B 已提交而通過(檔跟 HEAD 一致);鎖內指紋比的是 T2 讀到的內容,也通過。第四項被整欄取代刪掉,寫後驗證只查「`_conds(valid_under) == vals` 且 c4 消失」,也通過;修復帳只留一筆 changed 差異,沒有任何一步說「你給的清單跟現在檔案裡的不是同一份」。
3. 更極端:`--values 一句話` 單獨一項,其他各項全部被丟掉,c4 照樣消失、照樣記「已修」。spec 的「其他項照抄」只是證據頁上的一句提示,沒有任何機械檢查。
4. 現有 `lumos set` 是通用整欄替換所以這樣可以;但 drift fix 是「修一筆 c4」,spec 又明說「不做 c4 的判定規則」與「c4 不再自己判讀原文形狀」,沒補上「只准動被判為 c4 的那一項」的檢查,等於把 set 的整欄覆蓋包了一層「已審」的外衣並記進修復帳。
建議(不強制形式):`--values` 寫入前要求「現有 valid_under 裡沒被 c4 判中的每一項,原文逐字都出現在 vals 裡」,或證據頁印一個內容雜湊、`--values` 要連同 `--expect <雜湊>` 一起帶。

## F2 寫後自驗用未去空白的 vals,含頭尾空白的值必定驗不過且訊息誤導
severity: minor
blocking: 否
引句:「`check=lambda f: _conds(f.get("valid_under")) == vals`」
file: `scripts/lumos:13775`(`_conds` 逐行 `.strip()`)、`scripts/lumos:15130`(`_set_conditions_locked` 是 `vals = [str(v).strip() ...]` 之後才比)
1. spec 的 check 引用的是 `--values` 原始參數;`_conditions_rewrite` 才做 strip,而 spec 只說它回 `(改後行, 錯誤訊息)`,沒說回傳去空白後的 vals。
2. 輸入 `--values " 項目一 "`:寫入的是 strip 後的內容,`_conds` 讀回也是 strip 後,兩邊比 `" 項目一 "` 對 `"項目一"` 不相等,`atomic_write_verify` 在寫檔之前丟 RuntimeError(`scripts/lumos` 的 `atomic_write_verify`),被 `_drift_fix_write` 轉成「寫不進去,筆記沒動」。不會壞資料,但訊息把使用者導向不存在的寫入故障。同一份 spec 裡 `template_used` 卻寫了「去頭尾空白後」,可見作者知道要 strip,只漏了 check。
3. 修法:`_conditions_rewrite` 回傳 strip 後的 vals,check 與 template_used 都用它。

## F3 卷證目錄的 git 查詢沒寫明在鎖外,而鎖的過期接手門檻(30 秒)小於兩次 git 逾時之和(40 秒)
severity: minor
blocking: 否
引句:「取驗證紀錄第一次被提交的提交(`_plan_first_commit`,有逾時,沒有回 None)」
file: `scripts/lumos:14979`(`_VAULT_LOCK_STALE_SEC = 30`)、`scripts/lumos:5865`(逾時 20 秒)、`scripts/lumos:33068-33077`(`_lens_git` 固定 20 秒)
1. 現況 `_drift_fix_c4` 在 `cmd_drift_fix` 的「鎖外判定」步驟跑,git 查詢在鎖外,這是對的。spec 新增 `--values` 後,`extra`(reports、reports_via)是寫修復帳的內容;spec 沒寫證據要在哪一步算。
2. 若實作者為了「reports 用寫入當下的歷史」把 `_drift_c4_evidence` 挪進 `_drift_fix_write` 或 `_drift_fix_record` 的 `with _vault_write_lock` 裡:`git log` 最多 20 秒 + `git show` 最多 20 秒 = 40 秒,超過 30 秒過期門檻,別的程序(例如同時的 `lumos set`)會把鎖當成死鎖原子接手,兩個寫入者同時在「讀—改—寫」。
3. 需要:spec 一句話寫死「證據在鎖外、判定步驟算完,鎖內只做指紋比對與寫入」,並讓 S2 的測試斷言這個順序(例如用 `LUMOS_DRIFT_FIX_FAULT` 那類接縫)。無此句時屬可被誤實作的空白。

## F4 乾淨檢查現在被 `kind != "c4"` 整個跳過,spec 沒提要改這一行
severity: minor
blocking: 否
引句:「帶 `--values`:做乾淨檢查(會寫檔;帶 `--dry-run` 時照慣例不做)」
file: `scripts/lumos:27792`
1. 程式碼在 `_drift_fix_load` 是 `if not o.get("dry_run") and kind != "c4":`,註解「c4 只列證據」。spec 只在做法第 2 節講「做乾淨檢查」,沒指名這一行;照著 spec 只在 `_drift_fix_c4` 補邏輯的實作會寫到「跟 HEAD 有差、又不是修復帳留下的」檔案上。
2. 這直接影響〈實務隱患〉「已排除:不可逆:寫入前的乾淨檢查保證 git 退得回來」這句的成立條件;也讓 F1 的「B 沒提交就被乾淨檢查擋下」這道天然保護在 c4 消失。
3. 建議在做法 2 明寫:條件改成 `kind != "c4" or o.get("values")`,並加一條測試(髒檔案帶 `--values` 要被擋)。

## F5 刪除守衛的工具檔判定:每次 18 次序列 git 子程序、各自 20 秒逾時,不受 15 秒總期限約束
severity: minor
blocking: 否
引句:「才取 `_vendored_state(root, "")[0]`(讀索引裡的檔與 `.lumos/vendored.json`)」
file: `scripts/lumos:17788`(每檔一次 `git show`,`_lens_git` 20 秒)、`scripts/lumos:29423`(delguard 的 deadline=15 秒)、`scripts/hooks/pre-commit:148-151`(註解:hang 由 lumos 內部 deadline 兜)
實驗:在暫存 git repo 跑 `_vendored_state(root, "")`(共 17 個檔 + 1 份清單),正常環境 0.30 秒,`ref=""` 確實讀索引(清單沒暫存→交集空;兩者都暫存→跳過;檔比清單新→交集空,皆與 spec 預期相符)。
1. 問題只在異常時序:`git show` 卡住(網路磁碟、fsmonitor、防毒掃描)時,每次最多 20 秒、串 18 次,最壞 6 分鐘,pre-commit 卡在一個「只提醒不擋」的守衛上;spec 沒寫這步排在 `git diff --cached` 之前或之後,也沒把剩餘 deadline 傳進去(`_vendored_state` 沒有 timeout 參數)。排在 diff 之前更糟:卡住之後 diff 只剩 0.1 秒逾時。
2. 建議:排在 diff 之後,用 `_over()` 判斷,超時走既有降級路徑(`degraded`),或改用一次 `git ls-files -s` 加單一 `cat-file --batch`。⚠ 只在 git 卡住時出現,判不準是否夠格 major,取 minor。

## F6 跳過判定只看索引且要求清單也在索引裡:只 `git add scripts/` 的更新提交仍然全部誤報
severity: minor
blocking: 否
引句:「被改過的工具檔(跟清單不一致)照舊抽,不放過消費專案自己改工具檔的情形。」
file: `scripts/lumos:17748-17762`(`_vendored_manifest_write` 寫進 `.lumos/`,不在 `scripts/` 底下)、`scripts/lumos:18035`
實驗(同 F5):工具檔已暫存、`.lumos/vendored.json` 未暫存 → `_vendored_state(root,"")[0]` 是空集合,一支都不跳。
1. `lumos update` 只動工作目錄(`_vendor_toolchain` 用 `shutil.copy2` 逐檔覆蓋、最後才寫清單;不碰索引,所以我查過,「同時進行的 update 跟 delguard 拼出兩個時間點」在 update 這一側不成立,兩次索引讀取來自同一份索引)。真正的兩個時間點是「提交者暫存到哪」:使用者更新後習慣只 `git add scripts/`,清單在 `.lumos/` 沒進索引,守衛判全部不一致,rtb 回報的噪音原樣重現,而〈誠實界線〉沒列這一情形。
2. 方向是保守(寧可誤報),不會漏,故取 minor;但 S6 的測試若只造「兩者都暫存」就測不到這條,需加「清單未暫存」的案例並把它寫進誠實界線,或改成「索引沒清單時退看 HEAD 的清單」。

## 逐類實務隱患(併發席)

- 併發-鎖是否同一把:已讀。`cmd_set`(`scripts/lumos:15080`)與 drift fix 寫入(`scripts/lumos:28089`)、修復帳追加(`scripts/lumos:28133`)都用 `_vault_write_lock(env.vault)`,同一把、可重入(`_VAULT_LOCK_HELD`)。`_set_conditions_locked` 拆出 `_conditions_rewrite` 後,鎖仍在 `cmd_set` 外層,拆函式不會改變鎖的層級;drift fix 路徑在鎖外算、鎖內比位元組指紋。無 finding(F1 是「指紋以誰為基準」的問題,不是鎖不同把)。
- 修復帳序號:`_drift_next_seq` 與 `_drift_ledger_append` 都在同一個 `with _vault_write_lock` 裡(`scripts/lumos:28133-28141`),同一筆記庫內序號不會撞;多工作樹合併同號是既有已知(`_drift_bound_latest` 註解),`--values` 只多加 reports 欄位,不改序號邏輯。無 finding。
- 寫到一半被中斷:筆記是原子換名,只有「筆記已改、修復帳沒記」一種殘留;下一次乾淨檢查是 `diff HEAD` 有差且最後帳指紋對不上→「有未提交的改動(不是 drift fix 自己留下的)」擋下,訊息叫人先提交或還原,不會在半狀態上再寫。c4 走新路徑後行為同 c1 到 c3,沒有新洞。無 finding。
- 帳檔尾端斷行:`_drift_ledger_append` 先補檔尾換行再追加,半行 JSON 被 `_drift_jsonl_parse` 略過;無 finding。
- 卷證目錄查詢兩次 git 之間歷史變動(rebase、gc):`show` 失敗回 None,退回名稱比對,`reports_via` 記成 `name` 但範本句的 sha 還在,只影響稽核精度,不影響筆記正確性;無 finding。
- 資安、金流、對外送出:與併發無關,無變動。

## ★INVARIANT★ 合約行逐條

- Systems/guard-kill 第 20 行「guard kill rc 優先序」:spec 只動 c1 與 guard settle 的訊息文字(節 3),不碰 kill 的 rc 判定;不影響,因為 kill 走獨立函式且 rc 由 survived/drifted 判定產生,不讀「找不到預告句」那句訊息。
- Systems/guard-kill 第 21 行「--json 成功時 stdout 恰一行 JSON」:同上,訊息改動在 `_drift_fix_c1` 與 settle 的人讀輸出;不影響 kill 的 --json 路徑。
- Systems/lumos-cli-write:全篇無 ★INVARIANT★ 行;其 KEY 段講的鎖(信任檢查、可重入)本設計沿用、不改。
- Systems/存量漂移守衛:無 ★INVARIANT★ 行;WHY 段的「不自動還原、乾淨檢查」是設計前提,F4 說明 c4 會脫離這個前提。

最高等級:major;blocking 共 1 條
