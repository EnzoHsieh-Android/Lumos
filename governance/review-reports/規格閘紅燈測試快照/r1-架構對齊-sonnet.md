severity: major

## 第 1 問 分層與依賴方向

**大致對齊,有一處跨層缺口(A1)。**

- **寫的一側。**
  - 逐支結果現在確實拿不到:`_spec_gate_judge_items` 的逐支 rows 只在 `_spec_gate_run_clauses` 彙整成條款層級就丟掉(`scripts/lumos:14636`、`scripts/lumos:14654`)。
  - `_spec_gate_record` 目前只記測試名(`scripts/lumos:14178`),留痕同時寫審查帳與治理帳(`_gate_event`,`scripts/lumos:14206`、`scripts/lumos:1784`)。
  - 把紅燈版指標掛在這同一筆留痕上,跟既有「審查帳與治理帳同欄位」的做法一致。
  - 找檔用 `_platform_name_files`,殘留索引與 e2e 對照也共用這支(`scripts/lumos:26443`、`scripts/lumos:26481`)。
  - `_judge_items` 有四個呼叫端(`scripts/lumos:14656`、`scripts/lumos:14688`、`scripts/lumos:15670`、`scripts/lumos:21512`)。改它的回傳形狀要保持其他三處不變,設計沒有講。
- **讀的一側。**
  - `_lint_new_guard` 本來就只經 `_tg_start`、`_tg_analyze` 兩個入口取候選(`scripts/lumos:39064`–`scripts/lumos:39073`),`cmd_test_guard` 也是(`scripts/lumos:49351`)。
  - 外部只有這兩個入口被呼叫。紅燈版的讀取放在 `_tg_analyze` 裡,新增告警閘就不會繞過比對工具。這一點設計的寫法對齊。
- **寫端借用比對工具的內部函式。**
  - 規格閘要呼叫 `_tg_functions` 和 `_TG_MAX_BYTES`(`scripts/lumos:48575`、`scripts/lumos:48396`)。
  - 這是第一次有 `_tg_` 內部函式被比對工具以外的程式呼叫。
  - 但 test-guard 自己也借 Room 守衛的 `_rg_methods`(`docs/lumos-toolchain-knowledge/Systems/test-guard.md:36`),所以我不判為跨層違規。
  - 借用的好處是寫端與讀端的函式鍵算法一致。這一點列在 ⚠。
- **缺口。**
  - `tq/redbase-rebound` 要讀終點版的計劃檔,取條款編號綁的測試名。
  - 比對工具目前只有 git 和 repo 根(`scripts/lumos:49351`、`scripts/lumos:39064`),沒有 vault。
  - 現有的條款綁定解析都吃 vault 或磁碟上的平台設定:`_clause_bindings_for(env, …)` 與 `_platform_test_index(rr)`(`scripts/lumos:14438`、`scripts/lumos:23001`)。

## 第 2 問 命名與錯誤處理

**大致對齊,有兩處小偏離(A3、A4)。**

- **規則代號。**
  - `tq/redbase-weakened`、`-rebound`、`-unmatched` 的前綴與 `tq/assert-weakened` 等一致(`scripts/lumos:49027`)。
  - 一條規則合併多種原因、靠 `extra` 寫明,已有先例:`tq/skip-added` 同時管跳過與 `expected=`(`scripts/lumos:49304`)。
  - 實作時要補進 `_TG_WHY`,否則 `_tg_cand` 會 KeyError(`scripts/lumos:49044`)。設計只提到同步 `_TG_LIMITS` 和標準文件。
- **資料夾與欄位名。**
  - 資料夾名 `redbase` 是新造詞。其他紀錄夾是「內容名詞加複數」:`governance/reread-verdicts/`、`governance/note-verdicts/`(`scripts/lumos:37605`–`scripts/lumos:37611`)。
  - 以迴圈編號分子夾對得上 `governance/replay/<id>/`。這只是用詞差異,不構成結構問題,不列。
  - 加進 `_BOOKKEEPING_DIRS` 的做法與寫法都對齊。
  - 「代碼審留痕失效的判斷另外看資料夾內有無程式檔、其他消費者只看前綴」的描述屬實(`scripts/lumos:68981`、`scripts/lumos:69017`)。
- **寫檔失敗。** 印一句、不擋、留痕照寫,對齊 `_spec_gate_record` 的 `留痕寫不進…` 處理(`scripts/lumos:14196`–`scripts/lumos:14210`)。
- **紅燈版壞掉的處理。** 這條偏離既有慣例,見 A3。

## 第 3 問 第二種做法

- **讀某一版的治理帳並做行差(A2,偏離)。**
  - 設計描述的程序(git 讀起點與終點兩版 → 只取終點新增的列)已有現成實作:`_residual_blob_at`(三態:ok/missing/unreadable)與 `_residual_ask_rows_at`、`_residual_ask_rows_delta`(Counter 行差)(`scripts/lumos:59935`、`scripts/lumos:60049`、`scripts/lumos:60107`)。
  - `_residual_blob_at` 的說明寫明「殘留索引與治理帳兩版比對共用這一支」,是代碼審架構對齊席當年合併出來的。
  - `_gov_vc_gate_events` 只讀工作目錄(`scripts/lumos:21705`),設計為了 S10 不用它,這個理由成立。
  - 治理帳有數十 MB(`scripts/lumos:68880` 的註解寫約 19 MB),超過 `_TG_MAX_BYTES` 的 5 MB,不能走 `_tg_read`(`scripts/lumos:49069`)。
- **讀 git 某一版的檔。** 紅燈版 JSON 本身可走 `_nodehome_cat_blobs_capped`,對照 `_tg_read` 和回頭重讀的 `_note_reread_verdicts`(`scripts/lumos:44093`、`scripts/lumos:51797`–`scripts/lumos:51808`)。設計只說「用 git 讀」,沒指名。
- **「取最早一份」。** 這跟 `_secev_gk_backing` 取祖先最深一筆(`scripts/lumos:9438`)語意不同,不必共用。但時間比較應沿用 `_loop_ts_key`,同秒用帳內序號打破平手,跟 `_spec_gate_pick`(`scripts/lumos:15030`)一致。設計沒寫。
- **存內容快照。**
  - 長期保存的內容快照放在 `governance/` 底下並提交,有先例:`governance/replay/`。
  - spec-freeze 的取向相反(短命、不掛分支,`scripts/lumos:66940`–`scripts/lumos:66943`)。
  - 所以紅燈版不算第二種快照做法。
  - 它重提了計劃自己承認被否決過的「內容比對 ratchet」,但 Enzo 已裁「照設計開審」,不在我的範圍。

## 第 4 問 落點

**三篇合理,不需要另開一篇。**

- `Systems/規格閘`:responsibility 含「審查帳留痕」,寫紅燈版歸它。
- `Systems/test-guard`:responsibility 含 tq/ 規則、指紋、讀兩端內容、接進新增告警閘那一層(`docs/lumos-toolchain-knowledge/Systems/test-guard.md:6`)。
- `Systems/test-quality-cli`:管標準文件的「規則一覽」與「抓不到」(`docs/lumos-toolchain-knowledge/Systems/test-guard.md:36`、`docs/lumos-toolchain-knowledge/Systems/test-quality-cli.md:6`)。

我確認過 lands_in 裡的 test-guard 已在這個 repo 存在。

## ⚠ 交編排者,不硬判

1. **`_BOOKKEEPING_DIRS` 的家。**
   - 先例不一致。e2e-records 的 WHY 寫在 `Systems/pitfalls-code-loop`(`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:65`)。reread-verdicts 的說明在 `Systems/筆記內容審`。
   - 該篇的 KEY 還寫「現在有哪些以程式為準」(`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:64`)。
   - 要不要把 pitfalls-code-loop 加進 lands_in 由你們裁。
2. **紅燈版檔案格式的擁有者。** 寫端在規格閘、讀端在 test-guard,格式(含函式鍵)是兩邊的合約。建議指定由規格閘那篇為單一來源,test-guard 那篇用 `SEE` 指過去,否則兩篇會各寫一半。
3. **寫端借用 `_tg_functions`。** 我判為對齊先例(借 `_rg_methods`)。但函式鍵算法一變,舊紅燈版會全部變成 `unmatched`(見 A4)。

### A1 搬家對照需要的計劃綁定,設計沒有說比對工具怎麼取得
severity: major
blocking: 是 — 純 git 的比對工具要讀 vault 裡的計劃並解析條款綁定,要嘛呼叫條款層與 vault 的函式(跨層),要嘛另寫一套解析器(第二種做法)
引句:「計劃裡同一個條款編號綁的測試名跟紅燈版不同、而紅燈版記的名字在終點那一版不存在」

- 治理帳裡的 `plan` 是 vault 相對路徑(`scripts/lumos:14186`、`scripts/lumos:14206`)。比對工具沒有 vault,要先拼成 repo 路徑才能從終點版讀,例如 `_spec_gate_status_at` 用 `env.vault` 拼(`scripts/lumos:15689`–`scripts/lumos:15707`)。
- 測試名要走 `resolve_test_refs`(`scripts/lumos:6419`)。現有入口吃的平台設定來自磁碟的工作目錄,不是終點版:`_clause_bindings_for`、`_platform_test_index`(`scripts/lumos:14438`、`scripts/lumos:23001`)。
- 其他讀設定的閘已經標明「從被檢查的版本讀」,例如 `_lint_new_relax` 用 `from_git=True`(`scripts/lumos:39166` 附近)。
- 若設計改成只用共用的純文字常數與函式(`_note_text_at_rev`(`scripts/lumos:28831`)、`SPEC_CLAUSE_RE`(`scripts/lumos:13616`)、`TEST_REF_RE`(`scripts/lumos:5947`)),並寫明平台設定也從終點版取,可降為 minor。

### A2 讀兩版治理帳並做行差,設計沒指名沿用既有的讀法
severity: minor
blocking: 否 — 功能與既有的 `_residual_ask_rows_delta` 一致,只差沒指名沿用;結構上還沒走偏
引句:「只取終點有、起點沒有的 `spec-gate-record` 行裡的 `redbase` 欄位」

- 該沿用 `_residual_blob_at` 與 Counter 行差,把 `_residual_ask_rows_at` 的閘名篩選參數化,不要另寫第三份。
- 還要補寫「取最早」的時間比較用 `_loop_ts_key`,平手用帳內序號。
- 若落地時另寫一份讀取函式,這條要升為 major。

### A3 紅燈版檔壞掉時整個比對報錯、無法放行,跟既有「單一怪檔變可放行候選」的慣例不一致
severity: minor
blocking: 否 — 錯誤處理與鄰居不同但結構成立,屬刻意取捨
引句:「讀不到、不是合法 JSON、或內容的 sha256 對不上欄位 → 記成比對沒跑完(跟比對工具出錯同一條路)」

- 既有慣例:`_lint_new_guard` 的說明寫明「單一怪檔不走這裡:配不平、含 NUL、太大、讀不出來都是可放行的候選」(`scripts/lumos:39064`–`scripts/lumos:39067`)。
- 對應的規則是 `tq/unreadable`、`tq/too-large`、`tq/unparsable`(`scripts/lumos:49027`–`scripts/lumos:49040`)。
- 整次報錯在 test-guard 的 WHY 只用於程式錯、逾時、git 算不出改動(`docs/lumos-toolchain-knowledge/Systems/test-guard.md:14`)。
- 紅燈版 JSON 缺失或指紋不符屬單一檔案問題,卻走整次報錯。這一類只能靠 `LUMOS_SKIP_LINT_NEW` 逃生,不能 `lint-waive`。
- 這樣是否刻意(防篡改不准放行)請設計自己寫明。

### A4 寫進 repo 的紅燈版 JSON 沒有格式或演算法版本欄位
severity: minor
blocking: 否 — 只是持久化紀錄的慣例沒跟上,不影響現在的結構
引句:「`tests` 每支一列(測試名、條款編號、檔案相對路徑、函式鍵),`files` 每支檔一份內容與 sha256」

- 鄰居寫進 repo 的紀錄都帶版本或規則版本:留痕有 `door_rule`、`inputs_sha`(`scripts/lumos:14186`–`scripts/lumos:14190`),JSON 檔有 `"version": 1`(`scripts/lumos:32067`、`scripts/lumos:40113`)。
- 紅燈版存的函式鍵是 `_tg_functions` 當下算的,該函式的鍵演算法(多載序號、`_TG_MAX_PATH_CHARS` 截斷等)日後一改,舊紀錄就會誤判成 `tq/redbase-unmatched`。
- 建議補一個格式版本欄位,讀端遇到不認得的版本時照 A3 的處理。

不對齊共 4 條,其中 major 1 條

被審材料與參考的程式都在 `/Users/enzo/harness/lumos-spec-snapshot` 下。我沒有建立任何檔案或暫存目錄,也沒有改動任何東西。
