severity: major

## F1 CI 的 code-loop 步驟只在 push 事件跑,PR 流程沒有 CI 驗紀錄
severity: major
blocking: 是 判準:「CI 驗紀錄」是這份 spec 的核心承諾,而現有 CI 形狀讓它在標準 PR 流程不成立,spec 沒寫。
引句:「這樣先略過檢查推了改程式的提交、再推一個只改文件的提交,CI 照樣擋。」
資料怎麼流第 3 步〈範圍〉,以及實務隱患那條「擋合併靠專案在 GitHub 把 CI 這道檢查設成合併前必須通過」。
問題有三個:
- code-loop gate 步驟帶 `if: github.event_name == 'push'`,而 workflow 的 push 只觸發 `branches: [main]`。
  - PR 事件的 CI 完全不跑這一步,feature 分支的 push 也不觸發 CI。
  - 把 CI 設成合併前必須通過,擋的是沒有 E2E 判定的那組檢查。
- 推到 main 時,「分支跟主線的分岔點」就是頂端本身(note-shape 步驟的註解也寫了這個形狀),範圍為空,判定不要求紀錄。
  - 所以 S8 的「CI 照樣擋」只有在 CI 以 push 事件跑在被推分支上才成立,現有 ci.yml 做不到。
- 用 `--no-verify` 直接推 main 時,CI 也不會補查。
spec 要嘛新增一個 pull_request 事件的步驟(用 base 與 head 算範圍),要嘛把 CI 實際擋什麼寫實。
佐證 file: `.github/workflows/ci.yml:3-9`、`.github/workflows/ci.yml:207-213`

## F2 設定檔從被推送的提交讀,同一個提交裡改設定就能關掉判定
severity: major
blocking: 是 判準:「AI 為了讓推送過去而順手做」的最短繞法,既有的安全證據閘已經針對同型問題立過規則。
引句:「專案沒有 `.lumos/android-e2e.json` 時這道不跑。」
資料怎麼流第 3 步、條款 S1、S7、回退節。
問題:
- spec 沒說設定從哪個版本讀。
  - 指紋與範圍都從「被推送提交的檔案樹」算,設定很可能也從那裡讀。
  - 同一個提交裡刪掉 `.lumos/android-e2e.json`、把 `app_dirs` 改成 `[]` 或指到不存在的目錄,判定就變成不跑或永遠沒改到。
- S1 的 check-config 只驗型別、`package` 字元與路徑不跳出根,沒驗 `app_dirs` 在樹裡存在且非空。
  - 空指紋是常數,一份紀錄就能永遠充數。
- 安全證據閘的做法是只讀主線 tip 版的設定,被推提交自己的設定不參與。
  - 它的 WHY 寫明了理由:被推的提交自己指定「拿誰比」,等於自己對自己。
- 設定檔本身壞掉(JSON 語法錯)時,spec 沒定義是擋、不跑還是回 2。
  - 回 2 會被 pre-push 放行,這是第二條關閘路徑。
修法:設定與「有沒有這道判定」只讀主線 tip 版。主線版有、被推版刪掉或改弱時要擋。check-config 加上 `app_dirs` 必須在樹裡且至少一個檔。
佐證 file: `scripts/lumos:8779`(被推提交自己的設定不採用)、`docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:52`

## F3 tag 與其他非分支 ref 不跑這道判定
severity: major
blocking: 否 判準:非 PR 合併路徑,但 Android 的發布流程常由 tag 觸發,spec 沒表態也沒回頭條件。
引句:「不然會被跳過;pre-push 帶 `--keep-going` 時跟其他判定一起列出擋下原因」
資料怎麼流第 3 步〈位置〉。
問題:
- pre-push 只對 `refs/heads/*` 叫完整的 `code-loop check`。
  - tag 與其他 namespace 只跑 `--security-only`。
- CI 的 tag 工作 `security_tag` 同樣只跑安全證據。
- 對沒驗收過的 App 提交推 tag(例如發布 tag)就能繞過,而且 spec 沒把它列在「不做」。
- spec 要嘛把 tag 納入(tag 指向的提交算指紋、查紀錄),要嘛在「不做」寫明並附回頭條件。
佐證 file: `scripts/hooks/pre-push:625-660`、`.github/workflows/ci.yml:20-44`

## F4 紀錄檔名等於指紋,內容沒有「自帶指紋」的比對,放行門檻只有 10 字
severity: major
blocking: 否 判準:偽造本身在威脅模型外,但這兩個捷徑不是偽造,是 AI 順手就做的事。
引句:「寫下誰(git 設定的使用者)、哪一天、理由,治理帳記一筆 `android-e2e-waive` 事件」
資料怎麼流第 4 步、條款 S9、〈查證紀錄長怎樣〉。
問題有四個:
- 紀錄只靠檔名對指紋。
  - 把舊的 pass 紀錄複製或改名成新指紋,不用手改任何欄位,判定就過。
  - 紀錄內容應含指紋,判定時要求內容指紋等於檔名等於重算值,並記 APK sha 與裝置實際安裝 sha 是否一致。
  - spec 只記下這兩個 sha,沒規定比對。
- waive 的操作者和被擋的是同一個 AI、同一個 git 使用者。
  - 條款 S9 只要求理由 10 字以上(中文 10 字很容易湊)。
  - 「人」留痕在實作上沒有任何東西與 AI 區分,等於把擋合併降成「多打一行指令」。
  - 安全證據閘是靠核可鏈簽名把人分出來,spec 沒說為何這裡不用,也沒說放行後要有什麼人看得見的告警。
  - RETIRE-IF 只在三個月後看統計,沒有即時回頭條件。
- 放行紀錄沒說是否必須已提交進被推的提交。
  - 工作目錄的紀錄在本機判定會過,CI 因為讀不到而紅。
  - 對 pre-push 是讀樹還是讀工作目錄也沒寫。
- 「同一個指紋再跑一次就覆蓋成新的那份」會把先前的放行洗掉(waived 變成 fail 或 pass),沒寫清楚合併規則。
佐證 file: `scripts/lumos:63137-63148`(既有 fail-open 帳的做法)、`scripts/lumos:8779`

## F5 判定自己出錯時 fail-open,且 spec 把已能確認的事推給實作時
severity: minor
blocking: 否 判準:既有行為且 spec 已承認,但缺回頭條件,且本機能被「弄壞輸入」關掉。
引句:「pre-push 對非 1 的回傳碼照舊放行並印出原因——這是既有的 fail-open 行為,本計劃不改。」
資料怎麼流第 3 步、實務隱患。
問題:
- 本機可用「讓判定回 2」的方式關閘:弄壞紀錄 JSON、設定 JSON,或讓 mainline ref 查不到。
  - 這是 F2 的另一條路,spec 沒列哪些錯誤固定回 1。
  - 紀錄壞掉、設定壞掉在已有 `.lumos/android-e2e.json` 的專案裡,應該判成擋(回 1),不要回 2。
- spec 說「CI 判定回 2 時 CI 步驟是否算紅要在實作時確認」。
  - 現在就能確認:CI 步驟在 rc 不是 1 時 `exit "$rc"`,會紅。
  - 請直接寫成事實。
- spec 沒說找不到主線(CI 上沒有本地 main、`main@{upstream}` 沒設)時怎麼辦。
  - 既有做法是回空樹或放行。
  - 對這道判定,找不到主線要擋(或明寫 fail-open 並記帳),不能靜默。
- 這道判定要不要呼叫 `_gate_failopen` 留帳也沒寫。
佐證 file: `.github/workflows/ci.yml:221-228`、`scripts/lumos:59104-59113`、`scripts/lumos:58578-58610`

## F6 指紋只算 `app_dirs`,App 行為會被目錄外的檔與驗收自己的素材影響
severity: major
blocking: 否 判準:會造成漏擋(沒重驗就過),但 `app_dirs` 由專案填,可由設定修正,屬設定面風險,但 spec 要提供引導。
引句:「指紋:被推送那個提交的檔案樹裡,`app_dirs` 底下的檔,依路徑排序後「路徑+內容」一起算 sha256;不看提交編號、不看目錄外的檔。」
〈查證紀錄長怎樣〉、〈設定〉。
問題:
- 多模組專案的其他 module、`gradle.properties`、`settings.gradle*`、`libs.versions.toml`、`build-logic`、proguard 檔都在 `app/` 之外。
  - 改了依賴版本或 minify 設定,App 行為變了,指紋不變,舊紀錄照過。
  - 範例設定 `["app/src", "app/build.gradle.kts"]` 就漏了這些。
- 指紋也不含 `flows`、`.maestro/baseline/*.png`、`visual`、`visual_threshold` 與 Macrobenchmark 門檻檔。
  - 先把基準圖換成壞掉的畫面,或降低門檻,紀錄的指紋沒變,照過。
  - 這又是一條不用偽造的順手繞法:改基準而不重驗。
- spec 沒要求 check-config 對常見遺漏(如 settings.gradle 列出的 module 目錄不在 `app_dirs`)提醒。
- 驗收素材(flows、baseline、門檻)至少要進指紋。
佐證 file: `scripts/lumos:8779`(同一個設計問題:判定的依據不能由被推提交單方決定)

## F7 誤擋成本:只改測試、註解與主線前進都要重跑實機,放行會變常態
severity: minor
blocking: 否 判準:RETIRE-IF 已預見但誤擋入口沒設計。
引句:「這段裡有任何提交改到 `app_dirs` 底下的檔,就要求紀錄。」
〈資料怎麼流〉第 3 步〈範圍〉。
問題:
- `app/src/test`、`androidTest`、註解、KDoc、純資源說明檔都在 `app/src` 底下。
  - 加一個單元測試或改一行註解,都要接實機跑幾十分鐘。
  - 這正是 spec 自己預告的「改走略過檢查」。
- 「任何提交改到」是逐提交算。
  - 先改後還原、淨改動為零的分支,仍會要求目前樹的指紋有紀錄。
  - 若主線那個指紋沒有紀錄(例如 main 上是別人略過檢查或放行進去的),就被擋,而且不是這個人造成的。
  - 範圍用「兩端樹的差異」判,不用逐提交判,才不會被這種往返誤擋。
- 多人同時改:主線前進後把主線合進分支,樹裡的 `app_dirs` 內容變了,指紋變了,必須重跑。
  - 兩條都要上主線的分支會輪流重跑,沒有「合併後的指紋」可預先驗。
  - spec 沒說這個代價,也沒給緩解(例如只改測試與資源的排除清單)。
- 建議 `app_dirs` 之外另有 `exclude` 欄位(排除測試與文件),或預設排除 `src/test`、`src/androidTest`。
佐證 file: `docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md:40`(壓提交或 rebase 讓留痕失效的前例;本 spec 用內容指紋已解決這一點,S10 方向正確)

## F8 判定在新分支首推、淺層 clone 與主線過期時的範圍行為沒定義
severity: minor
blocking: 否 判準:屬於實作時一定會踩的邊界,spec 的範圍定義要先寫。
引句:「範圍:從這個分支跟主線的分岔點,到這次被推送的提交(不是只看這一次推送帶了哪些提交)」
〈資料怎麼流〉第 3 步。
問題:
- 本機 `main@{upstream}` 過期(沒 fetch),分岔點被算在更舊處,範圍多算別人已進主線的提交。
  - 那些提交若是別人略過檢查進主線,這個人被擋。
  - 反過來,本地 `main` 領先遠端,範圍會少算,漏擋。
- 淺層 clone 沒有分岔點。
- 分支沒設 upstream、遠端不叫 origin 這些情形,既有的 `_lens_push_base` 與 `_push_range_start` 兩套並存且規則不同。
  - spec 沒說用哪一套,也沒說算不出時擋或放行。
- 新分支首推時 pre-push 傳的是 `push-range` 算的區間,CI 的 BEFORE 是全零。
  - spec 的「忽略推送範圍、只看分岔點」就要自己處理這兩種輸入,這點要寫進條款。
佐證 file: `scripts/lumos:58578-58610`、`scripts/hooks/pre-push:55-66`

## 固定席節點對照
- `Systems/pitfalls-code-loop`:會談目錄版管 `_codeloop_guard_verdict`。
  - spec 新增的判定排在 `_codeloop_security_step` 之後、早退之前,與既有「安全證據排最前」不衝突。
  - 既有 KEY 沒有宣稱「code-loop check 只有五道」的合約。
  - 該節點 line 40 所記壓提交或 rebase 讓留痕失效的坑,這份 spec 用內容指紋避開,方向正確。
  - 不破壞既有行為與合約,但需要同步改:`_codeloop_kg_finish` 的 reason_kind 清單、pre-push 的 `pp_cl_reason` 對照表(有雙向測試 `t_prepush_cl_reason_table_matches_lumos`)、keep-going 的「五道」說法。
  - spec 的「這次要改到的地方」沒列 pre-push 與 CI 兩處。
- `Systems/macrobenchmark-adapter`、`Systems/android-stability-collector`:會談目錄裡沒有,無法逐條對照。
  - 只能依 spec 自己引用的行為判。
  - 這道新守衛只讀它們的 JSON 輸出,不改它們,判不影響。

## 逐類答覆
- 繞過(威脅模型內,不防):手改 result、跨指紋複製紀錄中的偽造部分。
  - 其中「改名複製」「waive 自己放行」「換基準圖不重驗」屬順手捷徑,見 F4、F6。
- 繞過(應擋):改設定或刪設定(F2)、推 tag(F3)、PR 與 main 事件下 CI 不查(F1)、壞檔讓判定回 2 被放行(F5)。
- tag 推送、分支名、force push、CI 事件:分別見 F3、F8、F1。force push 改寫主線屬存心繞過,既有 `_lens_push_base` 已有同樣取捨。
- 誤擋:見 F7、F8。
- 判定失效(靜默不跑或 fail-open):見 F1、F2、F5、F8。

總結:最嚴重為 major,blocking 共 2 條
