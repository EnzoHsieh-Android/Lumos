---
type: project
status: doing
created: 2026-09-30
updated: 2026-09-30
tags:
  - type/project
  - status/doing
  - scope/node-content
lands_in:
  - Systems/存量漂移守衛
  - Systems/lumos-cli-write
  - Systems/guard-kill
related:
  - "[[Projects/存量漂移改法_計劃]]"
  - "[[Projects/存量漂移防線_計劃]]"
  - "[[Projects/code側刪除傳播守衛_計劃]]"
---
# 漂移修法補強_計劃

白話:rtb 2026-09-30 用 `lumos drift fix` 把 26 筆漂移修到 0,回報五個工具不順的地方。這份計劃把它們補掉:c4 的卷證目錄找不到、c4 改完修復帳上沒紀錄、c1 的訊息把「已經改好」講得像出錯、c3 沒辦法寫理由、提交時刪除守衛把工具自己的檔當成專案程式而誤報。

依據:rtb 會談 2026-09-30 回報(跨會談訊息,逐條附了 rtb 的實際案例);Enzo 同日裁「照順序做」(先重新表態、再補這五條、再接推送閘)。

PRIOR-ART: 全部借工具鏈裡現成的東西,不另起做法。①卷證目錄:專案規矩「程式、圖譜筆記、審查卷證放同一個提交」(過代碼審多一個只動帳本的提交,卷證仍在功能提交),所以驗證紀錄第一次被提交的那個提交裡一起加進來的 `governance/review-reports/<目錄>/`,就是它的卷證——比用計劃名猜準;git 查詢借既有 `_plan_first_commit`、`_nodehome_git`、`_nodehome_split_z`。②c4 寫入:把 `lumos set` 整欄換掉的那段(`_set_conditions_locked` 裡驗證與算新內容的部分)拆成不寫檔的共用函式,drift fix 用它算出改後內容,再走 drift fix 原本的乾淨檢查、鎖內寫入、寫後驗證、修復帳——寫法仍是 set 那套已經審過的安全寫法,c4 不再自己判讀原文形狀(存量漂移改法代碼審四輪的教訓)。③工具自己的檔:借既有 `_vendored_state`(讀索引時傳 `ref=""`,同筆記形狀擋的用法)與 `_is_toolchain_repo`,刪除守衛抽被刪名稱時跳過跟安裝清單一致的工具檔。④c3 理由:同 c2 的 `--reason`(一行、4 到 200 字、擋提示佔位字)。
RETIRE-IF: 上線兩個月後:①修復帳裡 c4 的 `reports_via` 在工具鏈與 rtb 合計有一半以上是 `none`(兩種找法都查不到)→ 撤掉同提交找法、改回只給範本;②刪除守衛因工具檔跳過而漏掉真的過期句(有人回報)→ 改回全比對、另找降噪法。
REVISIT:2026-11-30 量上面兩個數(修復帳 c4 各筆的 reports_via、有沒有回報)

## 範圍

- **做**:①c4 證據的卷證目錄改從「驗證紀錄第一次被提交的那個提交裡一起加進來的卷證目錄」找,找不到才退回計劃名比對;②`drift fix --kind c4 --values <各項…>`:用 set 的驗證與整欄算法算出改後內容,走 drift fix 的寫入流程並記修復帳;證據頁印的指令改成這一條;③c1 訊息與 guard settle 的同一句,把「已經是轉正後的說法」跟「真的找不到預告句」分開講;④c3 收 `--reason`,寫進補的那一行;⑤刪除守衛在消費專案跳過跟安裝清單一致的工具自裝檔。
- **不做**:c4 的判定規則;`lumos set` 本身的行為(拆函式後照舊,訊息一字不變);把漂移檢查接進推送閘(另案,[[Projects/存量漂移防線_計劃]]〈做法〉第 4 節第 4 點);機制①(舊句偵測,[[Projects/舊句偵測實驗_計劃]])。

## 做法

### 1. c4 卷證目錄

- 取驗證紀錄第一次被提交的提交(`_plan_first_commit`,有逾時,沒有回 None);列那個提交加進來的檔:`_nodehome_git(root, "-c", "core.quotePath=false", "show", "-z", "--name-only", "--diff-filter=A", "--format=", <提交>)`,用 `_nodehome_split_z` 拆——不加 `--format=` 會混進提交標頭,不關 quotePath 中文目錄名會被跳脫成八進位、永遠比不到。收 `governance/review-reports/<目錄>/` 的目錄名,去重、照字母排。
- 找法順序:同提交找到的目錄跟計劃名比對(`_drift_c4_key`)有交集就只列交集;沒交集就列同提交找到的全部,超過 3 個時標「同提交,可能含別的計劃的卷證,自己挑」;同提交一個都沒有(驗證紀錄另外提交、第一次進歷史的是合併提交、git 失敗或逾時、shallow)才退回計劃名比對。證據頁寫明用的是哪一種(`same-commit` / `name` / `none`)。
- 目錄名印到終端前過 `_esc_clean`;範本句照舊用找到的目錄。

### 2. c4 走 drift fix 寫入

- `_set_conditions_locked` 拆出 `_conditions_rewrite(lines, e, key, vals) → (改後行, 錯誤訊息)`:把現在的「空值、多行、佔位字」三道檢查與算新開頭欄位那段搬進去,錯誤訊息整句原樣回傳;`_set_conditions_locked` 讀檔 → 呼叫它 → 有錯就照原樣印到 stderr、回 2 → 沒錯才 `atomic_write_verify`。`lumos set` 的行為與訊息一字不變。
- `drift fix --kind c4`:新增 `--values`(argparse `nargs="+"`,加進 `_DRIFT_FIX_OPTS`,`_DRIFT_FIX_ALLOWED["c4"] = {"values"}`)。
  - 不帶 `--values`:照舊只列證據與預填指令,不做乾淨檢查;指令改成 `lumos drift fix <節點> <行號> --kind c4 --values …`,要改的那項放 `<整項新內容>`、其他項照抄。
  - 帶 `--values`:做乾淨檢查(會寫檔;帶 `--dry-run` 時照慣例不做);用 `_conditions_rewrite(lines, fe, "valid_under", vals)` 算改後內容(有錯回 2);`res` 照 drift fix 的鍵組:`check=lambda f: _conds(f.get("valid_under")) == vals`、`handled=_drift_no_kind("c4")`、`extra={"template_used": 任一項去頭尾空白後等於範本句, "reports": 找到的目錄, "reports_via": same-commit|name|none}`;`--values` 各項已由 `_conditions_rewrite` 擋空值、多行、佔位字,再過 `_drift_one_line` 擋 U+2028 這類分行字元;不送筆記形狀擋(開頭欄位不在它的範圍,存量漂移改法設計時已定)。之後照 drift fix 原流程:`--dry-run` 到此 → 鎖內比指紋寫入 → 驗證磁碟內容等於算出的內容且 c4 消失 → 修復帳。
- `lumos set <節點> valid_under …` 照舊可用,但不記修復帳;證據頁只印 drift fix 那條。

### 3. c1 與 settle 的「找不到」訊息

- guard 區段加一支共用判定 `_guard_prose_settled(lines, kind)`:四種預告句各自的「轉正後說法」在不在——TEST:摘要有 `TEST:[日期] 預告已轉正` 開頭的行;WHY:沿用既有 `why-done` 的辨認(行尾「(日期 已轉正)」);whynot:正文有「預告當時」開頭的行;settle:正文有「(日期 已轉正)」那一行,或既有 `settle-del` 已判出下一行是手補的「已轉正」段。
- `_drift_fix_c1` 與 `guard settle` 印「找不到」時先問它:在就講「〈那一種〉已經是轉正後的說法,不用改」,不在才講「找不到〈那一種〉,可能被手改過,看一下」。

### 4. c3 的理由

- `--kind c3` 收選填的 `--reason`(規則同 c2:一行、4 到 200 字、擋提示佔位字;佔位字檢查從 `_drift_fix_c2_args` 抽成 c2、c3 共用)。
- 補的那一行三種寫法(有 `--by` 且是 pass:「由 [[X]] 解決」;有 `--by` 其他狀態:「參考 [[X]]」;沒 `--by`)都一樣:有給理由就在最後接「;理由:<理由>」,沒給照舊。

### 5. 刪除守衛跳過工具自裝檔

- `cmd_delguard_check` 先判 `_is_toolchain_repo(root)`:是工具鏈本身就不跳(那些檔是它自己的程式);不是才取 `_vendored_state(root, "")[0]`(讀索引裡的檔與 `.lumos/vendored.json`),得到「跟安裝清單一致」的工具檔集合。
- `_delguard_parse_diff` 加一個 `skip` 參數(預設空集合),抽 `-` 行名稱與收 `+` 行回收表的兩遍都用它跳過。
- 被改過的工具檔(跟清單不一致)照舊抽,不放過消費專案自己改工具檔的情形。

## 條款

- [S1] 當 c4 證據要列卷證目錄,工具應先取驗證紀錄第一次被提交的那個提交裡一起加進來的卷證目錄(中文目錄名照原樣),跟計劃名比對有交集就只列交集,同提交一個都沒有才退回計劃名比對,並寫明用的是哪一種 [test:t_drift_c4_reports_from_first_commit]
- [S2] 當 `drift fix --kind c4` 帶 `--values`,工具應用 set 的驗證與整欄算法算出改後內容、做乾淨檢查、在鎖內寫入、寫後驗證、記一筆帶 reports 與 reports_via 的修復帳;值裡留著 `<整項新內容>`、空值、多行時擋下不寫;`--dry-run` 只印不寫 [test:t_drift_fix_c4_values_writes_via_set_rewrite]
- [S3] 當 `lumos set` 整欄改 valid_under/revalidate_when,行為與錯誤訊息應與拆函式前完全相同 [test:t_drift_fix_c4_values_writes_via_set_rewrite]
- [S4] 當 c1 或 guard settle 找不到某種預告句而那一種已經是轉正後的說法,訊息應講「已經是轉正後的說法」;真的找不到時才講「找不到」 [test:t_drift_fix_c1_already_settled_message]
- [S5] 當 `drift fix --kind c3` 帶 `--reason`,補的那一行應以「;理由:<理由>」收尾(三種寫法都一樣);理由的規則與 c2 相同 [test:t_drift_fix_c3_reason]
- [S6] 當消費專案提交時工具自裝檔跟安裝清單一致,刪除守衛不應從它抽被刪名稱;被改過的工具檔與工具鏈來源 repo 照舊抽 [test:t_delguard_skips_vendored_toolkit]

## 回退

- 五條各自可還原:卷證目錄退回計劃名比對(`_drift_c4_evidence` 改回);c4 退回只印 `lumos set` 指令(`_drift_c4_print` 的指令與 `--values` 一起拿掉,`_conditions_rewrite` 可以留著,set 行為不變);c1 與 settle 的訊息、c3 的 `--reason`、刪除守衛的 `skip` 各自拿掉。
- 已經用 `--values` 改過的筆記是一般筆記改動,修復帳上有紀錄;要退用 git 還原那些提交。

## 實務隱患

- 已排除:不可逆:只改本機筆記與修復帳,寫入前的乾淨檢查保證 git 退得回來,還原提交後外面不用收拾
- 已排除:金流:這是本機命令列工具,不碰任何付款或帳務
- 已排除:對外送出:不寄信、不打外部服務,git 指令只印給人看
- 守衛面(碰到):刪除守衛(只提醒不擋)在消費專案少抽工具自裝檔;c1 與 settle 的訊息判定放在 guard 區段。被改過的工具檔照舊抽,寧可誤報不漏
- 資安(碰到):c4 的值走 set 既有的安全寫法;卷證目錄名印到終端前過 `_esc_clean`,印成照貼指令的參數走 `_drift_sh`
- 效能(碰到):卷證目錄多一次 `git show`,只在 c4 證據頁與 `--values` 寫入時跑,有逾時
- 併發(碰到):c4 寫入走 drift fix 既有的鎖與指紋比對,不另開寫入路

## 誠實界線

- 卷證目錄的同提交找法,前提是「程式、筆記、卷證放同一個提交」這條規矩有被遵守;驗證紀錄另外提交、或第一次進歷史的是合併提交時,只能退回猜名字。壓成一個的大提交可能含好幾份計劃的卷證,超過 3 個時證據頁會標明、由人挑。
- `lumos set` 直接改 valid_under 不記修復帳(set 是通用指令,不綁漂移);要記帳就走 drift fix 那條。
- 刪除守衛跳過工具檔,前提是安裝清單正確;清單壞掉時 `_vendored_state` 判不一致,照舊抽(寧可誤報不漏)。拆除工具鏈(把工具檔刪掉)的那個提交,索引裡已經沒有那些檔,不會跳過,照舊可能誤報。
REVISIT:2026-11-30 看有沒有拆除工具鏈的提交被刪除守衛誤報的回報;有就改成也認「起點跟清單一致、這次被刪」的工具檔

## 合約候選

(實作後再判。)

## 審計修正紀錄

- 前置掃描(2026-09-30,便宜席):四項清單命中未定義 4、壞引用 0(2 條註記)、範圍矛盾 4、語意對不上 6;全部折入,對照表在 `governance/review-reports/漂移修法補強/r1-intake.md`。
