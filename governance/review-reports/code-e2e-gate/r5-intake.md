# r5 收貨與去向(2026-10-27,第二次破例加開)

起因:第四輪折了 31 條、其中多數是第三輪修補帶進的;第四輪的修正差異沒有新席看過。編排者依使用者授權再記一筆 cap-decision extra-round,並由新的乾淨代理把跑滿回顧更新到 r1–r4 後記錄。

材料:r5-repair.patch(de8a99bc → 490dac6a,1262 行,這輪的重點)加 r5-snapshot.patch(0701350..490dac6a,4713 行,上下文)與 r5-repair-binding.json。7 席全新代理:正確性(C)、邊界(B)、資源(P)、合約與文件(K)、通才(G)、架構對齊(A)、資安(S)。七份報告從逐字稿存檔;reflog 核對工作目錄沒有被切換。quote-check:五席全數錨定;邊界(B3)、資安(S1)各 1 句錨不到,兩句是同一行既有程式(judge --precheck 的印出),審材只含改動附近的上下文,下表以測試重現。

這輪有 major,照代碼審規則 accepted 必須為空:33 條全折(修正前 490dac6a → 修正後見 r5-fix.json)。

## 重現(觀察與判準分開驗)

| id | 重現 | 結果 |
|---|---|---|
| S1、C1、B3、G1、A2 | 未追蹤檔名帶換行與 ESC:judge --precheck 原樣印出(偽造的獨立一行);_e2e_full_blocked、_e2e_judge_partial、history 等處也直接印;補 t_android_e2e_say_single_exit(掃語法樹,e2e 區直接印「擋下:」就紅,修前列出 8 處)與 precheck 實跑一條,修前紅 | HIT |
| A1 | _macrobench_mode 呼叫 e2e 專屬的 _e2e_say_block(macrobench 在下層) | HIT(讀碼);同一支測試的「清理在底層」斷言修前紅 |
| A4 | 兩串逃逸帳字樣是手抄的、沒有綁到 pre-push | HIT(讀碼);補 pre-push 比對字樣一致的斷言 |
| A5、B4 | 控制字元判斷手抄一組類別,漏了代理字元、私用區、未指派;專案有 _path_special_chars | HIT;補 t_android_e2e_big_records 代理字元與私用區兩條,修前紅 |
| A6、K5、G3 | _E2eGitErr 是 str 子類別當旗標;測試把 _e2e_tree_json 整支換掉,真的產生處沒測(席位把三處 _E2eGitErr 拿掉測試照綠) | HIT;改成第三格旗標,補 t_android_e2e_git_names_and_parent ③ 用真的刪掉 git 物件驗 |
| A7、G5 | _e2e_parent 另寫 rev-list,專案已有 _push_rev | HIT(讀碼) |
| B1、S2 | --depth 1 的淺層 clone 裡刪掉整份設定:check 回 none;補 ② 用真的淺層 clone,修前紅 | HIT |
| C2、K4 | 測試把 _e2e_parent 整支換掉,真函式的失敗分支改回放行照綠(席位改壞實測);補 ② 對真函式的一般、根提交、淺層三種 | HIT(守衛缺口) |
| C3 | "d/"*64 與 "./"+64 層被判超過;補 big_records 一條,修前紅 | HIT |
| C4、B2、P2 | --list 時間用完或有太大的紀錄時收尾說「沒有任何放行」;「再跑一次會從最新的開始讀」重跑永遠一樣;補 big_records 一條,修前紅 | HIT |
| K1 | 2MB+10 的紀錄帶待看 AI 放行:_e2e_ai_pending_all 回 ([], 0)、--ack 說沒有待看;補 big_records 四條(另計、掛鉤、doctor、--ack),修前紅 | HIT |
| K2 | S41 的「不算沒讀」只有兩邊一樣的斷言、沒有絕對值;同上補絕對值斷言 | HIT(守衛缺口) |
| K3、G4 | 九處 _e2e_say_block 改回原樣、shared_paths 上限拿掉,測試照綠(席位改壞實測);靜態守衛加 shared_paths 上限斷言補上 | HIT(守衛缺口) |
| G2 | 2,097,118 位元組的紀錄 waive 寫完長到 2,097,325,提交後判定擋;補 big_records 一條,修前紅 | HIT |
| K6、G6 | README 說「要先合主線」那種不印放行指令,但 mainline_newer 會印;列的不印種類也不全 | HIT(讀碼) |
| K7 | pre-push 的註解還寫三個獨立判定 | HIT(讀碼) |
| A3 | 64 層寫死、函式內重複 import、E2E_DIR_LIST_MAX 名字跟用途不符 | HIT(讀碼) |
| P1 | 1000 項 app_dirs 加 1000 項 exclude 最壞每檔 0.145ms(席位實量),約 40 萬支檔超過 60 秒 | HIT(席位量測) |
| S3 | _esc_clean 不清 U+2028/2029、方向標記、BOM;補 say_single_exit 一條,修前紅 | HIT |

## 去向(根因分組;第二次以上出現的類別換形狀)

1. 外來文字(第五次出現,再換形狀):S1、C1、B3、G1、A2、A1、A4、S3 → 折。清理搬到底層(_PREPUSH_ESCAPE_MARKERS、_out_clean、_say_block 放在 _esc_clean 旁邊,macrobench 與 e2e 共用);e2e 區剩下的「擋下:」全部改走 _say_block,另加掃語法樹的守衛測試——以後誰在 e2e 區直接印「擋下:」測試就紅,不再靠人逐點找;從 git 取來的改到的檔名在源頭擋(推送前判定與 --changed 都要求先改名);pre-push 比對的兩串字跟程式裡的綁一條斷言。
2. 用專案既有的輪子:A5、B4、A6、A7、G5 → 折。控制字元判斷改用 _path_special_chars(加私用區與未指派);git 暫時讀不出改成照 _push_rev 慣例的第三格旗標;取上一版改用 _push_rev。
3. 淺層 clone:B1、S2 → 折。_push_rev 查不到上一版時再問是不是淺層 clone,是就算判不出;查主線一個候選都沒有時也跑上一版檢查。
4. 測試把被測函式整個替換:C2、K4、K5、G3、K2、K3、G4 → 折。改用真的淺層 clone、真的刪掉 git 物件、真的根提交與一般提交;太大紀錄的計數改成絕對值斷言;出口改由靜態守衛涵蓋全部呼叫點。
5. 太大的紀錄:K1、G2 → 折。另計成「超過 2MB 沒讀(修好或刪掉)」,doctor、開場提示、--ack 都講;寫入端檢查寫完的大小。
6. --list 收尾:C4、B2、P2 → 折。沒讀完或有太大的紀錄時改說「讀到的紀錄裡沒有放行」,時間用完講「較舊的 N 份沒列出」並說明怎麼看到它們。
7. 邊界與上限:C3、P1、A3 → 折。層數照正規化後算、上限具名(E2E_PATH_DEPTH_MAX);清單上限降到 200 並改名 E2E_PATH_LIST_MAX;拿掉函式內的重複 import。
8. 文件:K6、G6、K7 → 折。README 中英改成「有些擋下不印放行指令」並列較完整的例子;pre-push 註解改成各道判定。

## 修補因果(載體帶 --regression-set)

- 有證據的修復回歸(r4 修補帶進的):A1、A3、A4、A5、A6、A7(r4 新加的函式與常數另起一套)、C2、K4、K5、G3(r4 新加的守衛,測試替換了被測函式)、C3(r4 新加的 64 層判斷)、C4、B2、P2(r4 新加的 --list 時間上限與訊息)、K1、K2(r4 拿掉太大算沒讀)、K3、G4(r4 新加的出口只測了兩處)、G2(r4 新加的判定端 2MB)、G6(r4 新寫的 README 句)。
- 原有漏查:S1、C1、B3、G1、A2(judge 的印出修前就在,r4 宣稱統一卻沒掃到)、B1、S2(淺層 clone 修前同樣放行)、B4(修前完全沒有類別檢查)、P1、K7。
- 未判定:S3、G5、K6。

## 上限

這是第二次破例加開的第五輪。這一輪的修正差異沒有再給新席看;下一步的決定記在帳(cap-decision)與回顧。
