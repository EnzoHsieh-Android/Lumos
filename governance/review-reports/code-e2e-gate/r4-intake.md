# r4 收貨與去向(2026-10-27,破例加開)

起因:第三輪是 high 的上限,修正差異沒有新席看過;編排者依使用者授權記了 cap-decision extra-round(理由見帳),並先寫跑滿回顧 cap-retro.json(乾淨代理起草)。

材料:r4-repair.patch(bf9dac49 → de8a99bc,1586 行,這輪的重點)加 r4-snapshot.patch(0701350..de8a99bc,4321 行,上下文)與 r4-repair-binding.json。7 席全新代理:正確性(C)、邊界(B)、資源(P)、合約與文件(K)、通才(G)、架構對齊(A)、資安(S)。七份報告從逐字稿存檔。資源席初交時第 1 條寫 major 卻標不擋,退回由該席自己重判成 minor,其他內容沒變(存的是重判後的全文)。邊界席審查中把工作目錄切到同一個提交又切回,reflog 核對無改動。quote-check:四席全數錨定;邊界 1 句(B3)、資源 1 句(P3,該席自己註明引錯)、合約 1 句(K6)錨不到,下表重現。

這輪有 major,照代碼審規則 accepted 必須為空:31 條全折(修正前 de8a99bc → 修正後見 r4-fix.json)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| S1、B1 | 紀錄的 feature_runs 鍵名帶換行與 ESC、items 不是清單:waive 與 --ack 的「擋下:」原樣印出鍵名(換行後的字自成一行);補 t_android_e2e_text_gates ②,修前紅 | HIT |
| S2 | app_dirs、shared_paths 帶換行:_e2e_relpath_err 回 None,錯誤訊息原樣回顯;補同一支 ①,修前紅 | HIT |
| S4 | 檔名含 pre-push 記逃逸帳的字樣:結果原樣帶;補 ③,修前紅 | HIT |
| C1、K2、B2 | 提交裡 2MB 以上、16MB 以下的紀錄帶 AI 放行:判定回 waived;補 t_android_e2e_record_size_gate 第一條,修前紅 | HIT |
| C2、K3、A2 | 把 bad_record="git" not in rerr 改成 True,原有測試照綠(三席改壞實測);補同一支第四條(git 暫時失敗時不叫人刪),修前因沒有型別旗標紅 | HIT(守衛缺口) |
| C3、G1、K5、B3 | 超過 2MB 的紀錄算進沒讀,--ack 印「讀超過 60 秒、再跑一次」,重跑永遠一樣;改成判定一律擋太大的紀錄、不算沒讀,--list 標明太大;補同一支第二條,修前紅 | HIT |
| P1、C4 | --list 讀全部紀錄、整份留在記憶體、沒有時間上限(席位實量 250 份 2MB 30 秒、3GB);補同一支第三條,修前紅(不收 budget) | HIT |
| K4 | 拿掉掛鉤的 min(..., _inner_budget()) 與太大算沒讀,原有測試照綠(席位改壞實測);補 t_android_e2e_gate_r4_paths ① | HIT(守衛缺口) |
| S3 | 查主線失敗時 rev-parse 失敗與根提交都變空字串而放行;補同一支 ②,修前紅(沒有 _e2e_parent) | HIT |
| G3 | 這一版自己拿掉主線還要求的 flow,擋下叫人 git merge;補同一支 ③,修前紅 | HIT |
| K1 | SKILL.md 同一行前半六個、後半五道;reference.md、commands/06、commands/08 還寫五 | HIT(grep) |
| K6 | 不印放行指令的擋下不只 README 列的兩種(找不到主線、逾時、要先合主線) | HIT(讀碼;引句錨不到,改以讀碼採信) |
| K7 | 新測試 docstring 的條款編號跟計劃綁的不同 | HIT(讀碼) |
| K8 | pitfalls-code-loop 的早退順序沒列 Android 那一道 | HIT(讀碼) |
| G2 | 設定裡一條 10000 層的功能路徑,maxd 跟著變大,深檔仍是平方(席位實量 50 支 1.8 秒);改成路徑最多 64 層,補 t_android_e2e_text_gates ① | HIT |
| G4、A1 | _e2e_scope_dirs、_e2e_owner_index 的說明還寫三項 | HIT(讀碼) |
| P2 | app_dirs、shared_paths 的長度沒有上限,範圍判斷逐檔逐項比;改成最多 1000 項,補 text_gates ① | HIT(讀碼) |
| P3 | 主線設定不同時多算兩次指紋 | HIT(讀碼;引句錨不到,席位自註引錯,原文在 r4-repair.patch) |
| C5 | 結束時間讀不懂的舊紀錄,judge 重跑也拒寫 | HIT(讀碼;刻意的,跟判定同一套) |
| A3 | 同一區段兩種清理位置(結果出口、逐點) | HIT(讀碼) |
| A4 | _e2e_record_update 用 stat、掃描用 lstat | HIT(讀碼) |

## 去向(根因分組;第二次以上出現的類別換形狀)

1. 外來文字進輸出(第四次出現,換形狀):S1、B1、S2、S4、A3 → 折。兩層看門:源頭 _e2e_relpath_err 拒收控制字元、換行與看不見的格式字元;出口兩支(判定結果 _e2e_gate_out、指令的「擋下:」_e2e_say_block)共用 _e2e_clean,e2e 區段與設定檢查、判讀的十二處「擋下:」全部改走它;_e2e_clean 另把 pre-push 記逃逸帳的兩串字拆開。寫成 Systems/android-e2e-acceptance 的 WHY。
2. 大小上限兩端不一致:C1、K2、B2、C3、G1、K5、B3、A4 → 折。判定讀紀錄也用 E2E_RECORD_FILE_MAX(2MB),超過就擋、叫人修好或刪掉;太大的紀錄不再算進沒讀(判定擋它,放行不生效),--list 標明太大;寫入端改 lstat。
3. --list 的資源:P1、C4 → 折。邊讀邊印、時間上限 60 秒、用完講沒讀到幾份。
4. 分流與守衛缺口:C2、K3、A2、K4 → 折。git 暫時失敗的錯誤帶型別 _E2eGitErr,判定看型別不看訊息文字;補 git 暫時失敗、掛鉤預算兩條測試。
5. 判不清就擋:S3 → 折。_e2e_parent 分開「git 失敗」與「根提交」,前者擋。
6. 訊息:G3 → 折。主線跟分岔點不同才叫人合主線;主線跟分岔點一樣、是這一版自己改弱的,叫人改回去。
7. 輸入上限:G2、P2 → 折。路徑最多 64 層;app_dirs、exclude、shared_paths 最多 1000 項。
8. 文件:K1、K6、K7、K8、G4、A1 → 折。五道全改;README 中英改成「擋下訊息有印放行指令時」並列全不印的幾種;測試條款編號、早退順序、兩支說明跟上。
9. 刻意的行為:C5、P3 → 折成 Systems/android-e2e-acceptance 的兩條 WHY(寫入端跟判定同一套所以重跑也不覆蓋;設定不同時才多算指紋)。

## 修補因果(載體帶 --regression-set)

- 有證據的修復回歸(r3 修補帶進的):B1、S1(r3 新加的 _e2e_record_err 訊息帶 {k}、寫入端改驗它)、C2、K3(r3 新加的 git 分流沒有測試)、C3、G1、K5、B3(r3 新加的 unread += 1)、P1、C4(r3 拿掉 --list 的份數上限)、K1(r3 只改了半行)、K2、B2(r3 新加的條款 S46 與寫入端 2MB)、K4(r3 新加的掛鉤兩行沒有斷言)、K7(r3 新測試的編號)、G2(r3 的 maxd 只修了一半)、G3(r3 新加的 mainline_newer)、S3(r3 新加的上一版檢查)。
- 原有漏查:C1(判定讀紀錄的 16MB 上限修前就是)、S2(路徑檢查本來就不擋控制字元)、S4、K6、K8、P2、A2、A4、G4、A1。
- 未判定:C5、P3(刻意的行為)、A3。

## 上限

這是破例加開的第四輪。這一輪的修正差異同樣沒有再給新席看;下一步的決定記在帳(cap-decision)與回顧。
