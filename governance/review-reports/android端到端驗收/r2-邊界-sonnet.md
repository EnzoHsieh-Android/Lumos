severity: major

## F1 回退節指的設定檔不存在
severity: major
blocking: 是,回退步驟照字面做不到,屬可執行性缺口(major)。

〈回退〉第一條寫「專案刪掉 `.lumos/android-e2e.json`,判定就不跑」。但〈設定〉規定設定放在 `.lumos/macrobench.json` 的 `e2e` 段,「不另開設定檔」。全文沒有任何地方定義 `.lumos/android-e2e.json`。

輸入→結果:出事時照回退節刪檔,什麼都不會變,判定照擋。真正的關閉方式是刪或改 `e2e` 段。這一步又受〈設定〉規定的「合進主線才生效」限制,所以要先推一個提交才能關。誤擋卡住時,回退節給的是假出口。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:40`(設定放進 macrobench.json 的 e2e 段)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:176`(回退節寫的檔名)

引句:「專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑」

## F2 指紋把「e2e 段本身」算進素材,但指紋只由 git ls-tree 的物件編號組成
severity: major
blocking: 是,指紋定義內部矛盾,實作者只能二選一,而兩種選法都有後果(major)。

〈設定〉「驗收素材」與〈查證紀錄〉都說「這一段設定本身」算進指紋。〈查證紀錄〉的 `fingerprint` 定義、S2 和最後一條都明寫只用 `git ls-tree` 的 mode、物件編號、路徑,不讀檔案內容。「一段」不是樹裡的項目,樹裡只有整份 `.lumos/macrobench.json` 的 blob。

輸入→結果:
- 若把整個檔案的 oid 算進去,動 `macrobench` 的基準、`results_dirs`、`stability` 段或門檻,甚至只是格式整理,都讓所有 e2e 紀錄作廢,要重跑十幾到幾十分鐘的實機驗收。
- 若要抽出 `e2e` 段另外雜湊,就違反 S2「只用 mode、物件編號與路徑」和「不讀檔案內容」。
- 不處理則「改了 e2e 段指紋就全變」(〈查證紀錄〉)不成立:改弱門檻不會觸發重驗。

S2 的測試名 `t_android_e2e_fingerprint` 沒有涵蓋這兩種情況。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:52`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:96`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:149`

引句:「驗收素材:`flows` 的檔、`visual` 對應的 flow 與基準圖、門檻檔、這一段設定本身,都算進指紋」

## F3 推送檢查遇到「主線設定本身壞掉」時沒有規定行為,預設會落進靜默 fail-open
severity: major
blocking: 是,漏洞讓守衛整道無聲失效,屬守衛面缺口(major)。

S1 只規定 `check-config` 回 2。但推送檢查讀的是主線版的 `e2e` 段,CI 與 pre-push 都不跑 `check-config`。〈資料怎麼流〉第 4 步只定義「紀錄讀不懂→擋」。其餘「沒料到的內部錯誤」走 fail-open 並記帳。

輸入→結果(都沒定義,都落在 fail-open):
- 有人合進主線一個 `"app_dirs": []` 或 `"flows": "x"` 型別錯的 `e2e` 段。
- `app_dirs` 的某一項在被推送提交的樹裡不存在,例如該分支把 `app` 改名。此時指紋是空集合,還是丟例外,spec 沒說。
- 判定遇到這些就無聲放行,整道守衛關掉,只在治理帳多一筆 failopen。REVISIT 只排了 2026-12-31 回頭看,且只涵蓋「算不出分岔點」。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:83`(只有紀錄壞掉才擋)
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:148`(S1 只管 check-config)

引句:「其他沒料到的內部錯誤照 code-loop check 既有做法:接住、記一筆 fail-open 治理帳、這道放行。」

## F4 驗收跑到一半 HEAD 或檔案被改,紀錄綁到沒測過的內容
severity: major
blocking: 是,紀錄可能對一份沒被驗過的程式內容放行,屬守衛面漏洞(major)。

開跑前檢查「沒有未提交改動」只在開始時做一次。judge 在結束時「對目前 HEAD 提交的檔案樹算指紋」。〈資料怎麼流〉第 1 步記了 APK sha256,但沒有記「開跑時的 HEAD 或樹指紋」。一次驗收可能長達幾十分鐘(〈實務隱患〉自己寫的)。

輸入→結果:
- 驗收進行中,使用者在另一個終端改了 `app/` 的檔並 commit(或 amend、rebase)。
- 結束時工作目錄乾淨,S7 的拒絕不觸發。
- 指紋是新 HEAD 的指紋,紀錄卻是用舊程式建的 APK 跑出來的 pass。
- 推送檢查找得到紀錄、指紋相符,放行一份沒驗過的程式。
- APK sha256 只證明「裝的是建的那個」,不證明「建的是這個提交」。

S16 與 S7 都沒有「開跑時的 HEAD 與結束時相同」這一條。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:74`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:78`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:154`

引句:「對目前 HEAD 提交的檔案樹算指紋(工作目錄在 `app_dirs` 或驗收素材有未提交改動時拒絕寫紀錄)」

## F5 「未提交改動」沒講未追蹤檔與 app_dirs 以外的檔,但 build 吃整個工作目錄
severity: major
blocking: 是,APK 內容與指紋綁定的內容可以不同,屬守衛面漏洞(major)。

〈資料怎麼流〉第 1 步說 `build` 在「乾淨的工作目錄」上建,但沒定義怎麼讓它乾淨。第 1 步和 S7 的髒檢查只涵蓋 `app_dirs` 與驗收素材。

輸入→結果:
1. 使用者新增 `app/src/main/Foo.kt` 還沒 `git add`。若「未提交改動」只看 `git diff` 或 `git status` 的已追蹤檔,這個未追蹤檔會被 Gradle 建進 APK,卻不在 `git ls-tree` 指紋裡。測試通過後,推上去的程式不含 Foo.kt。
2. 不在 `app_dirs` 的模組或 `local.properties`、gitignored 的 `.gradle` 設定被改過,同樣進了 APK。〈實務隱患〉只承認「漏列」會讓改動不觸發重驗,沒講髒改動會污染這次驗收結果。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:47`
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:74`

引句:「範本腳本在乾淨的工作目錄上照它建」

## F6 `.e2e-lock` 被 SIGKILL 或斷電留下後沒有復原路徑
severity: major
blocking: 是,中途失敗後永久擋住下一次驗收,spec 沒給復原步驟(major)。

〈資料怎麼流〉第 1 步為 toolkit 的 `.maestro/.lock-<序號>` 寫了「上一次被強制中斷留下的…確認沒有 visual-check.sh 正在跑之後才清」。但範本腳本自己的 `.lumos/artifacts/android/.e2e-lock` 沒有任何殘留處理。S16 規定「另一次驗收在跑」時不開跑。

輸入→結果:
- 筆電斷電、`kill -9` 或終端被關,TERM 與 Ctrl-C 的 trap 都沒機會跑。
- 鎖留下來,之後每次驗收都回「另一次驗收在跑」。
- 沒有 PID、沒有逾時、沒有清法。使用者只能手動 `rm` 或走放行。
- 鎖是目錄還是檔案、有沒有帶 PID,spec 沒說。

toolkit 的鎖是 `mkdir` 目錄,且只靠 `trap EXIT`,不帶 PID。所以「確認沒有 visual-check.sh 正在跑」用什麼判斷也沒定義,多半是 `pgrep` 比對。

佐證:
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:19`(`mkdir` 鎖)
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:21`(`trap` 只處理 EXIT)

引句:「沒有另一次驗收在跑(`.lumos/artifacts/android/.e2e-lock`)」

## F7 spec 宣稱的「既有原子寫入把暫存檔放系統暫存目錄」與 `_write_bytes_atomic` 不符
severity: minor
blocking: 否,宣稱與現況不符但影響有限,不改變判定結果,屬文字與實作銜接錯(minor)。

〈查證紀錄〉說「寫入一律用既有的原子寫入(先寫暫存檔再換名,暫存檔放在系統暫存目錄,不放進 `.lumos/e2e-records/`)」。查 `_write_lf` 到 `_write_bytes_atomic`:暫存檔名是 `path.with_name(...)`,與目標同目錄,名字帶 `.tmp-wlf`。

輸入→結果:
- 照現況直接呼叫 `_write_lf`,寫到一半被殺會在 `.lumos/e2e-records/` 留下 `<fp>.json.<pid>-<uuid>.tmp-wlf`。這個目錄是要提交的簿記目錄,殘檔會被 `git add` 帶進去。
- 若改成系統暫存目錄,跨磁碟區的 `os.replace` 會 `EXDEV` 失敗(專案在外接碟或 `/tmp` 與工作目錄不同卷時)。
- 兩種都需要新寫法,spec 沒有交代。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/scripts/lumos:28464`

引句:「暫存檔放在系統暫存目錄,不放進 `.lumos/e2e-records/`」

## F8 `visual_threshold` 只擋下限與非有限數,toolkit 的格式限制沒對上
severity: minor
blocking: 否,極端值只會讓人自己卡住且 `check-config` 可補一條規則,屬局部規則缺口(minor)。

S1 只擋「不是有限數或低於 99.5」。toolkit 要求 `THRESHOLD` 符合 `^[0-9]+(\.[0-9]+)?$`,不合回 2。

輸入→結果:
- `visual_threshold` 設 `150`:Maestro 比對永遠過不了,每次都是「截圖沒過」,卻通過 `check-config`。
- 設 `1e16` 這類值:Python 轉字串成 `1e+16`,toolkit 回 2。
- 兩者都會讓整套驗收永遠擋推送,而 `check-config` 回 0。

佐證:
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:12`
- file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:16`

引句:「`visual_threshold` 不是有限數或低於 99.5」

## F9 重跑或被中斷的驗收會蓋掉同一指紋上已有的 pass
severity: minor
blocking: 否,損失是多跑一次,不會放過壞程式,屬便利性缺口(minor)。

〈查證紀錄〉的 `runs` 只留最近一次,「每一次 judge 覆蓋這一欄」。被 Ctrl-C 中斷時,範本腳本仍會呼叫 judge(〈資料怎麼流〉第 1 步)。

輸入→結果:同一指紋已有 pass,使用者好奇再跑一次;因為裝置抖動或手動 Ctrl-C,新紀錄變成 fail 或 unjudged。工作目錄這份檔被覆蓋成非 pass;只要這份被提交,推送就被擋,要再花十幾分鐘到幾十分鐘重跑才能恢復。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:97`

引句:「`runs`:只留最近一次的結果(每一次 judge 覆蓋這一欄,不動 `waivers`)」

## F10 `<名>` 沒定義,同名 flow 的報告檔會互蓋
severity: minor
blocking: 否,需要兩支同名 flow 才會發生,屬命名未定義(minor)。

〈一次驗收跑什麼〉寫報告到 `<run>/ui/<名>.try1.xml`。`flows` 是路徑清單,「名」是檔名、不含副檔名的 stem,還是 flow 的 `name:`,spec 沒定義。

輸入→結果:`flows: ["a/login.yaml", "b/login.yaml"]` 兩支同 stem。後跑的覆蓋先跑的報告。judge 對先跑那支用的是後跑那支的報告:零案例或失敗案例被換掉,可能把該擋的判成過,也可能反過來。S1 沒有檢查 `flows` 內的重複名稱。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:65`

引句:「`flows` 每支 `maestro test --format junit --output <run>/ui/<名>.try1.xml`」

## F11 RETIRE-IF 的度量在治理帳裡沒有資料來源
severity: minor
blocking: 否,影響的是撤除條件算得出來與否,不改變判定行為(minor)。

RETIRE-IF 要比「放行」與「修好再跑通過」,資料來源寫「治理帳 android-e2e 的 waived 對照紀錄裡的 pass」。但〈資料怎麼流〉第 5 步只定義治理帳事件 `waived`,REVISIT 另提到 `failopen`。判定擋下、後來通過這兩件事,都沒有任何事件寫進治理帳。

輸入→結果:撤除條件分母沒有資料,到期時沒人算得出「放行多過修好通過」。

佐證:
- file: `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/governance/review-reports/android端到端驗收/r2-snapshot.md:90`

引句:「治理帳記一筆:閘名 `android-e2e`、事件種類 `waived`(閘名登記進已知閘名清單)」

## 固定席逐條判
- `Systems/pitfalls-code-loop`(只加一行連結並把 `.lumos/e2e-records/` 加進簿記目錄清單):不影響。目前簿記清單是 `_BOOKKEEPING_DIRS`,新增一個前綴不動既有條目,spec 也要求看過清單的其他用處。
- `Systems/bound-tests-gate` 的 ★INVARIANT★(固定席綁定測試逐支真跑):不影響。新判定排在放行早退之前,不改 bound-tests 的判定流程。要確認的是接線處:`_cl_say_block`、`_codeloop_kg_finish` 與 pre-push 對照表必須同步,spec 的 S12 有寫,但 F3 的「設定壞了就 fail-open」與該合約的「算不出就不擋」精神一致,不衝突。
- `Systems/macrobenchmark-adapter` 與 `Systems/android-stability-collector`:不影響。`--results-dir` 是新旗標;收集腳本不改,`run-id` 與輸出位置和 spec 描述相符。

## 實務隱患逐類
- 金流、對外送出、不可逆:無,spec 已排除,查證相符。
- 守衛面:有,見 F3、F4、F5。
- 邊界與資料狀態:空 `app_dirs` 在 F3,上萬檔目錄只呼叫一次 `git ls-tree`,無問題。子模組與符號連結走 mode 與物件編號,無問題。時區是本機時區加時差,無問題。
- 中途失敗:見 F6、F7、F9。
- 新舊版本互讀:schema 比 lumos 新就擋,無問題。

已讀〈設定〉、〈第一次接入的順序〉、〈一次驗收跑什麼〉、〈資料怎麼流〉、〈查證紀錄〉、〈這次要改到的地方〉、〈不做〉、〈實驗室驗收〉、〈條款〉其餘部分,除上列外無其他 finding。

交叉引用已核:`Systems/macrobenchmark-adapter`、`android-stability-collector`、`安全證據閘`、`Maestro截圖基準比對_調研`、`截圖基準驗收流程_計劃`、`Verification/2026-10-24_效能判定規則實機評測`、`2026-10-23_macrobench實機端到端` 都存在。`Systems/android-e2e-acceptance` 為 spec 明說的新建節點。

最嚴重 severity:major,blocking 共 6 條(F1 至 F6)。
