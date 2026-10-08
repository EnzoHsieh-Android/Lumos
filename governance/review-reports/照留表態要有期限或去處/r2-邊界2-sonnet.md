severity: minor

# 邊界與可執行鏡頭(第 2 輪)

圖譜鏡頭:派工時沒有附上固定席的合約或事故節點(只給了 LUMOS-SPEC 路徑),所以沒有逐條判「不影響」的對象;我自己對照程式的結論:表態檔本來就是只追加、判定只在讀取時算,spec 沒動寫入格式以外的行為,不破壞既有合約。

已實驗/已讀程式驗過的事實(都在 /Users/enzo/harness/lumos-b1,唯讀):
- 空表態檔、檔案缺、符號連結:`_drift_load_acks` 回 [],spec 新增的邏輯只在「有同鍵照留」時才走,不受影響。`scripts/lumos:34353`
- 中文與 NFD 路徑:`Env.from_texts` 與 `Env.find` 都先 NFC,`status_of` 用 `env.notes` 查,NFD 輸入進得來也查得到。`scripts/lumos:698`、`scripts/lumos:424`
- 呼叫端全數:`_drift_split_acked` 只有五處呼叫(撤除條件、check_c、m1 報告、scan、doctor);doctor 只傳 c1 到 c6 的發現,m1 報告不碰 probe/retire,spec 說「考試與歷史重放不扣表態」成立。
- `_drift_scan_print` 已經在印 `_drift_prev_ack_line`(`scripts/lumos:36771` 附近),spec 步驟 7 說「那裡也印」是已存在的行為,不是新增;但 `_drift_prev_ack_line` 目前直接取 `pa["related"]`,spec 步驟 5 要它先判 `dead` 再碰 related,實作時順序不能反。
- Python 3.14 的 `date.fromisoformat` 接受 `20261105` 與 `2026-W45-1`,不接受全形數字、前導空白、帶時間。

## F1 `date` 欄位壞了或在未來時,期限規則沒定義
severity: minor
blocking: 否(要手改表態檔或本機時鐘錯過才會碰到,而且失敗方向只是照留撐得比預期久或例外,不放行新寫就成立的條件)
spec 段落:做法第 3 點(判斷一筆照留還算不算數)。
引句:「`until` 存在時要是 ISO 日期字串、不早於表態日 `date`、不晚於 `date` + 30 天,否則失效」
問題:規則只約束 `until` 相對 `date`,沒說 `date` 本身缺、型別不對、不是日期時怎麼辦;也沒把 `date` 對 `today` 設上限。
具體例:
- 輸入 `{"kind":"probe","date":"2099-06-01","until":"2099-06-30",...}`(本機時鐘被調到未來時記的,或手改)→ 預期 scan 判失效;實際 `until` 落在 `date` 到 `date+30` 之間、`today` 早於期限,判活著,照留撐到 2099 年。
- 輸入 `{"until":"2026-11-01"}` 沒有 `date` → 預期失效;實際取決於實作怎麼比,可能丟 KeyError/TypeError,違反「任何型別不對都回失效,不丟例外」。
- `until: null`、`until: ""` 算「存在」還是「沒有」:前者走舊表態寬限到 11-05,後者算寫壞,spec 沒講。
- 另外 `fromisoformat` 在 3.14 收 `20261105`、`2026-W45-1`:spec 的「ISO 日期字串」沒釘成 YYYY-MM-DD,實作者可能放行這兩種,和 `cmd_drift_ack` 寫出的格式不一致。
補法方向:`date` 先過同一套日期檢查、`date` 晚於 `today` 一律失效或夾到 `today`、`until: null` 明寫算沒有。S3 的測試加這四個輸入。

## F2 `_drift_ack_live` 簽名查不了「在圖譜資料夾底下」,`..` 的判法也沒釘
severity: minor
blocking: 否
spec 段落:做法第 3、4 點。
引句:「`tracked_in` 存在:要是字串、不帶 `..`、在圖譜資料夾底下,否則失效」
引句:「新增純函式 `_drift_ack_live(a, today, status_of) -> (活著?, 失效原因)`」
問題:
- 純函式沒有 vault_rel 參數,「在圖譜資料夾底下」判不了;第 4 點又說 `status_of` 會「去掉圖譜資料夾前綴」,沒說前綴對不上時回什麼。實作者若直接切掉固定長度的前綴,`docs/other-knowledge/Projects/X.md`(前綴同長、資料夾不同)會被切成 `Projects/X.md` 查到別的圖譜的同名筆記,綁去處就綁到不是這個圖譜的東西;S3 只列了「路徑帶 ..」,沒有這個輸入,測不到。
- 「不帶 `..`」若當子字串比,`cmd_drift_ack` 用 `env.find` 收下的合法節點名(例如 `Projects/v1..v2_調研.md`)寫入成功、下一次 scan 立刻判「綁的節點寫壞了」,表態當場失效。若當路徑段比,則沒問題;spec 沒選。
補法方向:`status_of` 負責前綴檢查(前綴不符回 None),純函式只檢查字串與路徑段;寫入與判定共用同一支路徑檢查。

## F3 推送檢查多建一棵樹:沒預算、讀失敗沒定義、函式名對不上程式
severity: minor
blocking: 否
spec 段落:做法第 7 點。
引句:「呼叫端:`cmd_drift_check` 的 probe 路徑、`_drift_retire_guarded` 不傳 today」
引句:「時才 `_drift_tree_env(root, tip, …)` 建一次(大部分推送不會建)」
問題:
- 程式裡扣表態的地方是 `_drift_check_c`(`scripts/lumos:35668`、`scripts/lumos:35742` 一帶),不是 `cmd_drift_check`;`_drift_check_core` 內部那棵樹(帶 override)在 `_drift_check_c` 拿不到,所以真的要「再建一次」,整份圖譜每篇筆記重讀一次。
- `…` 把 deadline 省略了。`_drift_tree_env` 的 deadline 預設 None 時批次讀取吃滿 60 秒(`scripts/lumos:32632` 一帶);`_drift_check_c` 沒有剩餘預算可傳,等於核心用光 60 秒後再加最多 60 秒,超出核心與撤除條件各自的截止時間規矩。
- `_drift_tree_env` 回 None(git 失敗、逾時)時 spec 沒說 `status_of` 怎麼辦;依步驟 3 的字面,所有 `tracked_in` 都會走「綁的 X 不在了」,訊息把「讀樹失敗」說成「筆記被刪」,推送的人會去重綁一個其實存在的筆記。比照判不了的做法:讀樹失敗算判不了、印原因,不印「不在了」。
- 讀不出(非 UTF-8)的筆記同樣被說成「不在了」;步驟 4 已把它回 None,但沒有對應的失效原因文字。
具體例:大型 vault(上千篇)加一筆新寫就成立的 retire 條件並帶 `--tracked-in` 推送 → 預期一次樹讀取;實際核心一次、`_drift_check_c` 一次,無截止時間。
補法方向:把核心已建的樹傳出來或回傳,否則至少傳剩餘 deadline;讀樹失敗走判不了。

## F4 推送路徑的失效原因來源沒定義
severity: minor
blocking: 否
spec 段落:做法第 5、7 點。
引句:「沒算上、但有同鍵照留的發現帶 `prev_ack={reason, dead}`(取 seq 或檔內順序最後一筆)」
問題:`dead` 的文字全來自 `_drift_ack_live`,而推送路徑不傳 `today`、也不呼叫它(只認 `tracked_in` 且 `status_of` 判開著)。所以「新寫就成立、補了裸照留或綁了已收尾筆記」時 `dead` 要印什麼沒寫:裸照留沒有失效原因可借;綁到已收尾筆記才有「已收尾」可講。另外「取 seq 或檔內順序最後一筆」沒說 seq 缺或壞(手改)時和有 seq 的混在一起怎麼排,現有 `_drift_bound_latest` 是把壞 seq 當 0。實作時印出的訊息會和步驟 5 的固定改法提示(「照留要帶 --tracked-in」)重複兩次同一句。
補法方向:推送路徑自己列兩種 dead 文字(沒綁去處、綁的那篇已收尾或讀不到),不經 `_drift_ack_live`;seq 取法沿用 `_drift_ack_seq`。

## F5 驗收缺極端輸入的測試
severity: minor
blocking: 否
spec 段落:驗收條款 S1 到 S7。
問題:S1 到 S7 沒有任何一條覆蓋:同一行同時有裸照留、綁已收尾、綁開著三種的推送結果(spec 只在 scan 規定「任何一筆活著就算」,推送路徑的「任何一筆」沒寫,但實作會共用迴圈);NFD 輸入的 `--tracked-in`;中文節點名;手改壞的表態檔(整行不是 JSON、欄位型別錯、`tracked_in` 是清單);同名筆記兩份時 `env.find` 只警告後取第一個(`scripts/lumos` 的 `find`),`--tracked-in 某名` 會靜默綁到第一個。S3 的純函式測試也沒包含 F1、F2 的輸入。
補法方向:S3 補壞欄位表;S6 補混合三筆的推送;S2 補同名筆記改要求給路徑或擋下。

## 逐節

- 白話與依據段:已讀,無 finding。
- 範圍:已讀,無 finding(「不做」那幾條與程式現況一致:`drift fix --keep` 固定 c2,`cmd_drift_ack` 簽名只需加預設值參數)。
- 做法 1(常數):已讀,無 finding。2026-11-05 = 2026-10-06 + 30 天,算術對。
- 做法 2(寫入):已讀,無 finding 之外見 F2 的同名筆記補充(F5)。
- 做法 3:見 F1、F2。
- 做法 4:見 F2、F3。
- 做法 5:見 F4;`_drift_split_acked` 的 m1 分支遞迴呼叫沒有轉傳新參數,但五個呼叫點裡沒有任何一處會把 m1 與 probe/retire 混在同一個清單,所以目前沒有具體失敗場景,不標。
- 做法 6(born_now):已讀,無 finding;`old` 不為真正好等於 `_drift_probe_judge` 的新寫分支,也涵蓋沒有起點。
- 做法 7:見 F3。
- 做法 8、9(提示與寫回):已讀,無 finding。
- 實務隱患(日期取本機、舊表態、改名、退回提交):已讀,無 finding;改名一條與 `find` 全 NFC 化一致。
- 驗收條款:見 F5。
- 回退與天花板:已讀,無 finding。

## 實務隱患逐類
- 時間與時區:scan 才算期限,本機日期;推送不看日期。唯一缺口是 F1 的未來 `date`。
- 路徑與編碼:NFC 全程一致,驗過;缺口只有 F2 的前綴與 `..`。
- 資料損壞或手改:F1、F4、F5。
- 效能與記憶體:`_drift_split_acked` 逐筆照留 O(照留數),字典查表,大量表態無問題;F3 的多建一棵樹是唯一放大點。
- 並行與鎖:`cmd_drift_ack` 解析節點在鎖外、寫入在鎖內,綁的筆記在表態到提交之間改狀態只會讓推送時判失效,方向是收緊,無 finding。
- 輸出注入:兩個印出點都包了 `_esc_clean(prev, 400)`;手改的路徑含控制字元不會直通終端。無 finding。
- 金流、對外送出、不可逆:無,spec 已排除且與程式一致(表態檔只追加)。

總結:最嚴重 minor,blocking 0 條(F1 到 F5 全是 minor)。
