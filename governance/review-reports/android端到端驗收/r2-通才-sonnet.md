severity: major

固定席判定:
- `Systems/bound-tests-gate` 的 ★INVARIANT★(對 impact 固定席綁定的測試逐支真跑,任一紅、懸空或證不出跑過就擋):不影響。新判定只多一種擋下種類 `android_e2e`,不碰「綁定測試逐支真跑」的邏輯。spec 要求它排在放行早退之前,不會讓綁定測試被略過。
- `Systems/pitfalls-code-loop`:不影響。只加一行連結和簿記目錄一項,該節點沒有合約。
- macrobenchmark-adapter、android-stability-collector、安全證據閘:會議目錄裡沒有這三篇,無法逐條核對 ⚠。從程式碼看,`--results-dir` 只是新增旗標,不改 `--stability` 既有路徑,應不影響。

## F1 只做 UI 與截圖的專案,第一次接入就被既有設定讀取器擋下
severity: major
blocking: 是,第一次接入走不通,spec 沒有補救方案,屬 major。

引句:「跟記憶體與穩定性一樣,放進既有的 `.lumos/macrobench.json` 當一段,不另開設定檔。」
- spec 段落:〈設定〉說 `e2e` 段放進 `.lumos/macrobench.json`。`macrobench` 與 `stability` 都是選填、預設 false,所以 UI 流程加截圖的專案是被允許的。
- 問題:現有 `_macrobench_config` 在沒有 `results_dirs`、也沒有 `stability` 段時,直接回錯誤「macrobench.json 要有 results_dirs」。spec 的〈這次要改到的地方〉沒有列出要改這個讀取器。
- 情境:Citrus_KDS 現在沒有任何 macrobench 設定,spec 要從零接。開發者只寫 `e2e` 段,跑 `lumos android-e2e check-config`。如果 check-config 共用這個讀取器,它得到的是 macrobench 的錯誤,而不是 e2e 的格式錯誤。這時開發者得先補一個沒用的 `results_dirs`,或乾脆放棄。
- 佐證:
  - file: `scripts/lumos:39415` 的 `if not has_dirs and ("results_dirs" in raw or "stability" not in raw): return None, "macrobench.json 要有 results_dirs…"`。
  - file: `scripts/lumos:39407` 到 `scripts/lumos:39410` 只對有 `stability` 段的專案放寬。

## F2 指紋公式裡沒有「e2e 段本身」,但條款與〈設定〉都宣稱它算進指紋
severity: major
blocking: 是,「改標準就要重驗」和「同提交刪段仍照主線版判」兩條保證沒有可實作的定義,屬 major。

引句:「改了 `app_dirs`、`exclude`、驗收素材或 `e2e` 段本身,指紋就全變、舊紀錄都對不上,要重跑一次」
- spec 段落:〈設定〉末條與〈查證紀錄〉末段宣稱 `e2e` 段算進指紋。但〈查證紀錄〉的 `fingerprint` 公式只用 `git ls-tree` 列出的檔案項(mode、物件編號、路徑)。
- 問題:`e2e` 段只是 `.lumos/macrobench.json` 裡的一個 key,不是獨立的樹項目。
  - 若把整個 `macrobench.json` 當驗收素材放進指紋,任何 macrobench 基準或門檻調整、`results_dirs` 變動都會讓 E2E 紀錄全失效,要重跑十幾到幾十分鐘。
  - 若只取該段的內容雜湊,公式沒有定義:怎麼正規化 JSON、怎麼和樹項目拼接。
  - S2 的測試描述也沒有列「改 `e2e` 段會讓指紋變」。
- 情境:開發者只調 macrobench 的門檻,E2E 紀錄全失效,被迫重跑或放行。反過來,若實作者選了取段雜湊,又缺定義,兩個實作會算出不同指紋。
- 佐證:
  - file: `scripts/lumos:39397` 到 `scripts/lumos:39418` 是 `.lumos/macrobench.json` 由整份讀入的讀取器,沒有分段雜湊的既有工具。

## F3 〈回退〉寫的設定檔 `.lumos/android-e2e.json` 全文沒有定義
severity: major
blocking: 是,回退段與設定段互相矛盾,照回退段操作會讓擋推送回退失效,屬 major。

引句:「專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑,其他判定不受影響。」
- spec 段落:〈回退〉第一條。
- 問題:〈設定〉明說不另開設定檔,判定的開關是主線版 `macrobench.json` 裡有沒有 `e2e` 段。這是補丁和原文銜接處的殘留。
- 情境:誤擋卡住開發時,開發者照〈回退〉刪那個檔。檔案不存在,判定照擋。他只能轉去放行或略過檢查。這正是 RETIRE-IF 想避免的路徑。
- 佐證:
  - file: `docs/lumos-toolchain-knowledge/Projects/Android端到端驗收_計劃.md:176` 提到 `.lumos/android-e2e.json`。
  - 我在 `scripts` 與 `docs` 下搜尋這個檔名,只有計劃這一處。
  - 正確的回退應是「從主線移除 `e2e` 段」,並要走主線合併才生效(〈設定〉已說同提交刪段不生效)。

## F4 AI 放行的「主動通知」其實是被動列表,無人看顧時沒有任何人被通知
severity: major
blocking: 是,WHY 的核心承諾與機制不符,最省力的放行路徑實際上沒人監督,屬 major。

引句:「AI 也能放行,但標成 AI 放的、主動通知人」
- spec 段落:WHY 第二條。對照〈資料怎麼流〉第 5 點「通知:`lumos doctor` 與開場的 lumos 提示列出還沒被人看過的 AI 放行」。
- 問題:doctor 與開場提示都要人自己開會談或跑 doctor 才看得到。沒有推送、郵件或擋推送等主動動作。
- 情境:無人看顧的 AI 遇到驗收紅,最短路徑是跑 `waive --note "裝置狀態誤擋重試過"`(10 字以上即可)。`_confirm_tty` 在沒有終端機時回 None,記成 AI 放行並放行。人幾週後才開 doctor,期間所有推送都已通過。
- 佐證:
  - file: `scripts/lumos:33560` 到 `scripts/lumos:33585` 顯示 `_confirm_tty` 在非互動、無 `/dev/tty` 時回 None,AI 路徑確實不會被擋。
  - spec 〈不做〉第 4 條明說不防 AI 冒充人。這我接受。但 WHY 用了「主動」一詞,承諾比機制強。
  - 要嘛把 WHY 改成「被動列出」,要嘛加一個擋點,例如 AI 放行累積幾筆未被人看過就擋。

## F5 RETIRE-IF 的度量在治理帳裡沒有資料來源
severity: major
blocking: 是,撤除條件永遠算不出來,等於沒有撤除條件,屬 major。

引句:「治理帳 android-e2e 的 waived 對照紀錄裡的 pass),或 AI 放行佔全部放行的一半以上,就把擋推送降回只提醒。」
- spec 段落:RETIRE-IF。
- 問題:spec 規定治理帳只記 `waived` 事件(以及 REVISIT 提到的 `failopen`)。judge 的 pass 並沒有被規定寫進治理帳。「放行多過修好再跑通過」需要的 pass 計數沒有地方可查。
- 情境:三個月後有人要依 RETIRE-IF 評估,治理帳裡只有 waived,沒有 pass。若改去掃各專案 `.lumos/e2e-records/`,紀錄又只留「最近一次」結果(`runs` 被覆蓋)。歷次通過的次數消失,條件算不出。
- 佐證:
  - file: `scripts/lumos:15996` 的 `_KNOWN_GATES` 是登記閘名,不是事件種類。事件種類要由 spec 另外規定,而 spec 只列了 `waived` 與 `failopen`。
  - 要嘛 judge 也記一筆 `judged` 事件(pass、fail、unjudged),要嘛 RETIRE-IF 改成只用 waived 與 failopen 能算的量。

## F6 擋下訊息遇到「紀錄已產生但還沒提交」時,指示的下一步是錯的
severity: major
blocking: 是,這是第一次被擋時最常見的情境,錯誤指示會推人去放行,屬 major。

引句:「印出哪一塊沒過、紀錄路徑、要跑的指令(重跑驗收,或放行)」
- spec 段落:〈資料怎麼流〉第 3 點「紀錄要提交進版控」,第 4 點上述擋下訊息,S10「紀錄沒提交…擋下」。
- 問題:judge 終端輸出只規定印「每一塊的結果、沒過的原因與證據路徑」,沒要求提醒「請提交這份紀錄」。擋下訊息對「找不到」與「工作目錄有紀錄但沒提交」沒有區分。
- 情境:開發者花 20 到 30 分鐘跑完驗收,結果是 pass,直接 `git push`。gate 從被推送提交的樹讀不到紀錄,印出「重跑驗收,或放行」。開發者不知道只要 `git add` 並提交,就會選放行(AI 會用 `waive`,見 F4)。
- 佐證:
  - file: `scripts/lumos:15996` 的治理帳機制,放行事件會直接進統計並拉高 RETIRE-IF 的放行比例。
  - 需要加一個分支:偵測工作目錄有該指紋的未提交紀錄時,擋下訊息改成「請提交 `.lumos/e2e-records/<指紋>.json`」。判定 judge 輸出末行也要印同一句。

## F7 步驟 4 與步驟 2 對「判定用的指紋」的設定來源,在 judge 端沒有說清
severity: minor
blocking: 否,不影響首次接入,只影響邊界一致性,屬 minor。

引句:「推送檢查只讀主線那一版的這一段」
- spec 段落:第 2 點 judge「對目前 HEAD 提交的檔案樹算指紋」,第 4 點 gate 只讀「主線版」設定。
- 問題:judge 用工作目錄裡的 `e2e` 段(未合進主線)算 `app_dirs` 與 `exclude`;gate 用主線版的。改了 `app_dirs` 但還沒合進主線時,紀錄的指紋與 gate 重算值對不上,S10 會把它當「指紋欄位對不上」擋下。
- 情境:一個 PR 同時擴大 `app_dirs` 並改 App 程式。合進主線後,gate 才開始用新 `app_dirs`。PR 內的紀錄全部失效,必須在新設定合進主線後重跑。〈設定〉只說「要等合進主線才生效」,沒提到這個重跑成本。⚠ 判不準這是否被視為可接受的刻意行為,所以只列 minor。
- 佐證:這是文件內部推論,審材外沒有檔案可佐證。

已讀、無 finding 的節:PRIOR-ART、〈第一次接入的順序〉、〈一次驗收跑什麼〉(visual-check.sh 的回傳碼 0、1、2 與 `THRESHOLD`、`MAESTRO_DEVICE` 的用法,已對 `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh` 核對相符)、〈不做〉、〈實驗室驗收〉、〈實務隱患〉。

交叉引用核對:related 與正文引用的 `Projects/Android效能判定統計化_計劃`、`Android記憶體與穩定性驗收_計劃`、`Android側UI測試綁圖譜工作流_計劃`、`截圖基準驗收流程_計劃`、`Maestro截圖基準比對_調研`,以及 `Verification/2026-10-24_效能判定規則實機評測`、`2026-10-23_macrobench實機端到端`,在 `docs/lumos-toolchain-knowledge` 下都存在。`Systems/macrobenchmark-adapter` 與 `android-stability-collector` 在會談目錄不存在(審材附註已說),無法核對。

使用者流程走查結論:第一次接入(F1)、第一次被擋(F6)、無人看顧放行(F4)、回退(F3)四處,手段與目的有落差。設計方向本身可行,沒有更簡單的替代做法。

最嚴重 severity:major。blocking 共 6 條(F1 到 F6),minor 1 條(F7)。
