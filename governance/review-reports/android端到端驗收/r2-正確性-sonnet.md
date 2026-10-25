severity: major

## F1 judge 與 gate 讀不同份設定,改過 `e2e` 段的分支一律對不上紀錄
severity: major
blocking: 是,字面實作下,合進主線後只要有分支改 `e2e` 段(例如加一支 flow),它的合法紀錄就永遠找不到。
- spec 段落:〈設定〉開頭、〈資料怎麼流〉第 2、4 步。
- 引句:「對目前 HEAD 提交的檔案樹算指紋」
- 引句:「推送檢查只讀主線那一版的這一段」
- 問題:judge 沒說用哪一份 `app_dirs`、`exclude`、`flows` 算指紋。它跑在開發者的分支上,自然讀工作目錄或 HEAD 的設定。gate 則明定只讀主線版設定。
- 輸入到結果:
  - 主線 `app_dirs=["app"]`,分支把它改成 `["app","core"]` 並跑完驗收。
  - judge 用分支設定算出指紋 Fb,寫出 `<Fb>.json`。
  - gate 用主線設定重算,得到另一個 Fg,去找 `<Fg>.json`,找不到就擋。
  - 紀錄是對的,卻只能走放行。
- 補充:指紋裡的「`e2e` 段本身」是 `git ls-tree` 看不到的。ls-tree 只給整個 `.lumos/macrobench.json` 的 blob,spec 沒說是整檔還是只取 `e2e` 段。整檔的話,改 `results_dirs` 或 `stability` 段也會作廢紀錄。
- 佐證:
  - file: `scripts/lumos:9974` `_secev_mainline_pick` 是既有的「主線 tip 版設定」機制。
  - file: `scripts/lumos:8779` 說明被推提交自己的設定不參與判定。

## F2 紀錄沒綁「建 APK 當下的提交」,跑驗收中途提交會讓紀錄綁錯程式
severity: major
blocking: 是,時間軸漏洞會直接放行沒驗過的程式。
- spec 段落:〈資料怎麼流〉第 1 步開跑前檢查、第 2 步。
- 引句:「工作目錄在 `app_dirs` 或驗收素材有未提交改動時拒絕寫紀錄」
- 引句:「結束時再讀一次裝置上安裝那份的 sha256(中途被換掉,紀錄記成沒跑成)」
- 問題:
  - 開跑前只查工作目錄乾淨,`steps.json` 沒有記開跑時的 HEAD 或指紋。
  - judge 只在結束時對「目前 HEAD」算指紋。
  - 裝置端 sha256 只防裝置上的 APK 被換,不防原始碼被換。
- 輸入到結果:
  - 乾淨樹開跑,建好 APK。
  - 十幾分鐘的驗收中,開發者改 `app/` 並 commit(樹又乾淨)。
  - judge 把「舊程式的驗收結果」寫成新 HEAD 指紋的 pass,gate 放行。
- 佐證:spec 全文沒有「judge 比對開跑 HEAD 與結束 HEAD」的條款。S7 只測 dirty 工作樹,沒有對應測試。

## F3 指紋沒涵蓋 flow 引用的子 flow 與 toolkit 腳本,改了不會要求重驗
severity: major
blocking: 是,漏擋(舊紀錄被當成有效)。
- spec 段落:〈設定〉最後一條「驗收素材」,以及表格第 66 行。
- 引句:「驗收素材:`flows` 的檔、`visual` 對應的 flow 與基準圖、門檻檔、這一段設定本身,都算進指紋」
- 問題:素材只列出名單上的檔。實際驗收依賴下列檔案,全都不在指紋內:
  - flow 以 `runFlow` 引用的共用子 flow、`config.yaml`。
  - `.maestro/visual-check.sh`、`visual-preflight.sh`、`visual-env.sh`。這些腳本決定門檻下限與狀態列固定方式。
- 輸入到結果:改共用的 `login.yaml`,或改 toolkit 腳本的比對邏輯,指紋不變,舊 pass 照用,gate 不要求重驗。
- 佐證:
  - file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:17` 的 99.5 下限寫在腳本裡。
  - file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:33` 是 `maestro ... test ... "${FLOW}"` 這行,flow 內容決定結果。
  - spec 的 `app_dirs` 預設只排除 `src/test`、`src/androidTest`,不含 `.maestro/` 底下的其他檔。

## F4 「只有放行的紀錄」的欄位形狀沒定義,可能被 S10 判成讀不懂而擋死放行路徑
severity: major
⚠
blocking: 是,放行是唯一出口,字面實作可能讓它失效。
- spec 段落:〈資料怎麼流〉第 4、5 步,S10、S13。
- 引句:「沒有紀錄就新建一份只有放行的紀錄」
- 引句:「紀錄讀不懂(JSON 壞掉、schema 比這版 lumos 新、result 不是認得的值、指紋欄位對不上)→ 擋(回 1)」
- 問題:
  - 只有放行的紀錄沒有 `runs`,也就沒有 `result`。
  - gate 先驗欄位再看放行,而「result 不是認得的值」會擋。實作者若把缺少 result 當不認得,從沒跑過驗收就放行的路會被自己擋住。
  - spec 沒寫該紀錄的 `runs` 是缺欄位、`null` 還是 `unjudged`,S10、S13 的測試也沒覆蓋「純放行紀錄要通過」。
- 判不準:兩種讀法都合文字,所以標 ⚠。

## F5 終端答 n 或其他答案時該記什麼沒定義,字面實作會把拒絕記成 AI 放行
severity: major
blocking: 是,放行紀錄的人與 AI 區分是這道設計的核心。
- spec 段落:〈資料怎麼流〉第 5 步。
- 引句:「沒有互動終端或沒人回答 → 記成 AI 放行」
- 問題:`_confirm_tty` 有三種回傳:True、False、None。spec 只定義了 True(人放行)和 None(AI 放行),沒定義 False,也就是有人在終端答了 n 或其他答案。
- 輸入到結果:人看到提示後答 n。照「有人答 y 才算人、其餘算 AI」字面實作,會寫入一筆 AI 放行,而人明明拒絕了。正確行為應是回非 0、不寫放行。
- 佐證:file: `scripts/lumos:33560` 的 docstring 寫明回 False 代表答了其他答案(拒絕)。

## F6 `macrobench_cmd` 若走 Gradle connected 測試,會移除或替換 APK,觸發 sha256 中途被換而 stability 無 App 可跑
severity: major
⚠
blocking: 是,`macrobench: true` 時 result 可能恆為非 pass。
- spec 段落:〈資料怎麼流〉第 1 步第三點、表格第 67、68 行、S6。
- 引句:「照 `macrobench_cmd` 跑完,把這次開始後才產生的結果檔複製到」
- 引句:「結束時再讀一次裝置上安裝那份的 sha256(中途被換掉,紀錄記成沒跑成)」
- 問題:
  - Macrobenchmark 常見的跑法是 `./gradlew :benchmark:connectedBenchmarkAndroidTest`。它會自己安裝 benchmark 變體的 App 與測試 APK,結束後(依 AGP 預設)卸載。
  - 於是「裝置上安裝那份」在效能塊之後不是被換就是不存在。
  - 排在它後面的記憶體塊也沒有 App 可跑。
- 輸入到結果:`macrobench: true` 的專案,結尾 sha256 不等於開頭或讀不到,S6 判成非 pass。
- 判不準:AGP 預設行為我沒有在本機環境實跑驗證,所以標 ⚠。
- 佐證:spec 沒寫效能塊前後要重裝 `apk`,也沒寫 sha256 比對要排除這一塊。repo 內三篇相關筆記都沒提這件事。

## F7 `steps.json` 沒記截圖腳本的輸出位置,judge 無法填 S4 要求的相符率與原因
severity: minor
blocking: 否,不影響擋或放行的判定,只影響訊息欄位。
- spec 段落:〈資料怎麼流〉第 1 步最後一點、表格第 66 行、S4。
- 引句:「每一步的回傳碼、開始結束時間、每次嘗試的報告路徑寫進 `<run>/steps.json`(judge 讀它)」
- 問題:S4 要求不相符時記相符率與差異圖路徑,表格寫「原因與相符率照腳本輸出記」。但 `steps.json` 只有回傳碼、時間、報告路徑。
- 缺口:visual 步驟的 stdout 沒有指定存到哪個檔,judge 沒有輸入來源。
- 佐證:file: `/Users/enzo/harness/maestro-visual-toolkit/lib/visual-check.sh:36` 到 `:48` 的相符率與原因只印在 stdout 與 stderr,diff 圖才複製到證據目錄。

## F8 `.e2e-lock` 被強制中斷後沒有清理規則
severity: minor
blocking: 否,只影響本機重跑,可手動刪鎖。
- spec 段落:〈資料怎麼流〉第 1 步第一點。
- 引句:「沒有另一次驗收在跑(`.lumos/artifacts/android/.e2e-lock`)」
- 問題:
  - spec 只寫了 toolkit 的 `.lock-<序號>` 在確認沒人用後才清。
  - `.e2e-lock` 自己被 SIGKILL、斷電或 kill -9 後遺留,沒有任何清除規則。
  - S16 要求「另一次驗收在跑時不開跑」,之後每次開跑都會被擋。
- 輸入到結果:強制殺掉驗收後,下一次永遠回「另一次驗收在跑」。

## F9 暫存檔放在系統暫存目錄,跨檔案系統時 `os.replace` 失敗
severity: minor
blocking: 否,僅限 repo 與暫存目錄不同檔案系統的機器。
- spec 段落:〈查證紀錄長怎樣〉寫入條。
- 引句:「暫存檔放在系統暫存目錄,不放進 `.lumos/e2e-records/`」
- 問題:暫存檔與目標若在不同檔案系統(例如 repo 在外接碟,或 Linux 的 `/tmp` 是 tmpfs),換名會丟 `OSError`(EXDEV),紀錄寫不出來。
- 佐證:file: `scripts/lumos:59194` 既有的快取寫入明寫「同目錄 mkstemp 唯一暫存名」。正確做法是暫存檔放同一檔案系統,例如 `.lumos/` 下另一個子目錄。

## F10 RETIRE-IF 與回頭條件指的資料帳上沒有,且事件名對不上
severity: minor
blocking: 否,文件層面的撤除條件失效,不影響擋推送判定。
- spec 段落:RETIRE-IF 行、第二條 REVISIT、〈資料怎麼流〉第 5 步最後一點。
- 引句:「治理帳 android-e2e 的 waived 對照紀錄裡的 pass」
- 問題:
  - 治理帳只記 `waived`。
  - 紀錄的 `runs` 每次覆蓋,pass 與 fail 的歷史次數都不留。
  - 要量「放行多過修好再跑通過」,資料只有 waived 一邊,分母量不出來。
- 另一處:REVISIT 寫的「failopen」,實際事件種類字串是 `fail-open`。
- 佐證:
  - file: `scripts/lumos:63137` `_gate_failopen` 呼叫 `_gate_event_or_warn(repo_root, gate, "fail-open", ...)`。
  - file: `scripts/lumos:1595` `_gate_event_build` 只寫入傳進來的 kind。

## F11 新舊版 lumos 與 `steps.json` 沒有版本欄位,舊版 lumos 對新設定靜默放行
severity: minor
blocking: 否,spec 已承認版本需相容,但沒給機械守衛。
- spec 段落:WHY「做法採範本腳本碰裝置」的代價、〈這次要改到的地方〉pre-push 一條。
- 引句:「範本腳本最後會呼叫 lumos android-e2e judge,跑驗收的那台機器要裝相容的 lumos」
- 問題 1:`steps.json` 沒有 schema 或版本欄位。舊版 judge 讀新版腳本寫的檔會悄悄誤判。紀錄有 `schema`,中間的 `steps.json` 沒有。
- 問題 2:舊版 lumos 的 code-loop check 沒有這道判定,pre-push 看不出差別。
- 輸入到結果:專案主線已有 `e2e` 段,某台機器的 lumos 太舊,推送靜默通過,沒有任何提醒。CI 第一版又不補查。
- 佐證:file: `scripts/hooks/pre-push:654` 附近的 `--security-only` 探法會在舊版時印「太舊」的提醒,這道新判定沒有對應探法。

## F12 `.lumos/macrobench.json` 只有 `e2e`(沒有 `results_dirs`、`stability`)時,既有 `lumos macrobench` 會回 2
severity: minor
blocking: 否,影響 UI-only 的試點專案。
- spec 段落:〈設定〉開頭、S19(KDS 試點只跑 UI 流程)。
- 引句:「跟記憶體與穩定性一樣,放進既有的 `.lumos/macrobench.json` 當一段,不另開設定檔。」
- 問題:既有解析器在沒有 `results_dirs` 又沒有 `stability` 時回 `macrobench.json 要有 results_dirs`。
- 輸入到結果:
  - 只寫 `e2e` 段的專案,`lumos macrobench` 與 `lumos macrobench --check-config` 都回 2。
  - `macrobench: true` 但漏寫 `results_dirs`,S1 的 `android-e2e check-config` 沒有檢查這個欄位。
- 佐證:file: `scripts/lumos:39415` 到 `:39416`。

## F13 主線版的 `e2e` 段本身有問題時,gate 該擋、略過還是 fail-open 沒寫
severity: minor
blocking: 否,觸發條件是主線上已經壞了一份設定。
- spec 段落:〈資料怎麼流〉第 4 步。
- 引句:「主線版有 `e2e` 段,而且「主線分岔點的指紋」跟「被推送提交的指紋」不同」
- 問題:S1 只定義 `check-config` 對壞設定回 2。gate 面對主線 `macrobench.json` 壞 JSON、`app_dirs` 在主線樹不存在,算不出指紋時怎麼辦,沒有規則。
- 輸入到結果:字面實作會落入「其他沒料到的內部錯誤 → fail-open」,整道判定靜默關閉。
- 佐證:spec 的 fail-open 只列了「算不出主線分岔點」與一般內部錯誤。

## F14 「既有推送範圍的算法」與「推到主線時分岔點就是頂端」互相矛盾
severity: major
blocking: 是,同一句話兩種實作對應相反的行為,其中一種在 CI 或第二次推送失效。
- spec 段落:〈資料怎麼流〉第 4 步「何時要求」與「CI」兩項。
- 引句:「主線分岔點用既有推送範圍的算法」
- 引句:「推到主線時分岔點就是頂端,這道不要求」
- 問題:
  - 既有的「推送範圍」有兩套。pre-push 傳給 `code-loop check` 的是 `_brange`,已存在的分支是 `遠端舊頂端..本地頂端`,只有新分支首推才是與主線的分岔點。CI 傳的是 `BEFORE..SHA`。
  - 另一套才是 `merge-base` 主線(`_push_range_start` 系列,security evidence 用的)。
- 輸入到結果:
  - 用 `_brange` 的話,分支第一次用 `--no-verify` 推上去。第二次只改文件再推,範圍只含文件,指紋相同,這道不要求,繞過成功。
  - CI 推到主線時 `BEFORE..SHA` 的起點是舊主線,差異含 app 變更,「CI 不要求」的宣稱不成立。
- 佐證:
  - file: `scripts/hooks/pre-push:472` 到 `:474` 的註解寫明 `_brange` 只在新分支首推時是分岔點,其他形狀同 `_range`。
  - file: `.github/workflows/ci.yml:221` 傳入 `--diff "$BEFORE..$SHA"`。
  - file: `scripts/lumos:9974` 到 `:9977` 寫明分岔點照 `_push_range_start` 的 `git merge-base`。

## F15 〈回退〉指向不存在的設定檔,關不掉這道判定
severity: minor
blocking: 否,不影響功能,但回退步驟不可執行。
- spec 段落:〈回退〉第一條。
- 引句:「專案刪掉 `.lumos/android-e2e.json`,`code-loop check` 的 Android E2E 判定就不跑」
- 問題:設定在 `.lumos/macrobench.json` 的 `e2e` 段,spec 全文沒有 `.lumos/android-e2e.json` 這個檔。照回退步驟刪除不存在的檔,判定照跑。
- 實際可行的關法:移除 `e2e` 段並合進主線,這與〈設定〉「要等合進主線才生效」一致,但回退段沒這樣寫。

---
已讀無 finding 的節:〈第一次接入的順序〉(除上述各條涉及處)、〈不做〉、〈實務隱患〉、〈實驗室驗收〉。

交叉引用已核對:
- 12 個 `[[...]]` 目標檔都在 `/Users/enzo/orca/workspaces/lumos-toolchain/android-e2e/docs/lumos-toolchain-knowledge/` 下。
- `Systems/android-e2e-acceptance` 是新開節點,尚未存在,屬預期。

固定席判定(該節點宣稱的行為或合約會不會被破壞):
- `Systems/bound-tests-gate` 的 ★INVARIANT★(bound-tests 逐支真跑,任一紅、懸空、不可過濾即擋 rc1)不受影響。新判定是另一種 `reason_kind`,不碰 bound-tests 的判定與 `t_bound_tests_g`。唯一的接觸面是 pre-push 的原因對照表(F14 以外沒有新增問題)。
- `Systems/pitfalls-code-loop`:加簿記目錄 `.lumos/e2e-records/` 不會讓既有的留痕失效。F2 的時間軸問題屬於新判定自己的缺口,不屬於該節點。

最嚴重 severity: major;blocking 共 6 條(F1、F2、F3、F4、F5、F6、F14 中除 F4、F6 標 ⚠ 外皆為確定,合計 blocking 7 條)。

**修正總結:blocking 共 7 條(F1、F2、F3、F4、F5、F6、F14),其中 F4、F6 為 ⚠;其餘 8 條(F7 到 F13、F15)為 minor。**
