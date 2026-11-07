severity: major

審查範圍:第 3 版全文,對照 `Lumos/main` 的 `scripts/lumos`、`check.py`、`test_lumos.py`、型錄與範本。我沒有跑 `scripts/test_lumos.py`,所以沒有任何測試是我自己跑過的,下面的核對都靠讀碼與數檔案。

## F1 做 5 的 samefile 沒說檔案不存在或讀不出來時怎麼辦,大小寫變體也有衝突
severity: major
blocking: 是(實作時 S3 測試在 CI 與既有大小寫測試之間會互相打架,而且有例外外洩的路徑;判準是會讓條款綁的測試沒法成立)
引句:「用既有判目錄時的 `os.path.samefile` 救濟,不比字串」
- 段落:做 5,以及 S3 的「含 `$HOME/` 寫法與大小寫變體 應 照舊執行」。
- 問題一:新增的「是不是同一支檔」判斷若直接呼叫 `os.path.samefile`,路徑不存在或工具鏈根底下沒有該檔時會丟 `FileNotFoundError`。現在 `_lint_wt_allow` 對「在 configs/ast-grep 底下但檔不存在」的路徑是放行的,之後才由 ast-grep 失敗歸入環境失敗。加了新判斷後,這條路徑會變成例外。
- 問題二:既有的 `_same_file_path` 在 samefile 失敗時會退回字串比對,這與 spec 的「不比字串」互相衝突。spec 沒說該用哪一個,也沒說要不要接住 `OSError`。
- 問題三:S3 要求大小寫變體「照舊執行」。這只在大小寫不敏感的檔案系統(macOS)成立。Linux CI 上 `SGCONFIG.YML` 不存在,samefile 失敗,測試 `t_lint_wt_allow_only_blocking_pack` 在 CI 無法成立。
- 問題四:既有測試對「目錄」大小寫不同的處置是不通過(`Harness` 對 `harness`),新規則卻讓「檔名」大小寫不同的變體通過,兩邊規則不一致。
- 佐證:`scripts/lumos:41184` 的 `_lint_wt_allow` 只在 `commonpath` 之後用 samefile 找祖先,且包了 `except OSError`。`scripts/lumos:16688` 的 `_same_file_path` 有字串退路。`scripts/test_lumos.py:132186` 是既有的目錄大小寫不通過案例。
- 修法:S3 把變體案例限定為「大小寫不敏感的檔案系統才驗」,或改成不接受大小寫變體。再明寫「samefile 丟 OSError 就判不是同一支檔,回拒絕原因,不丟例外」。

## F2 型錄範本的兩條宣告沒有任何機械綁定,S4 只有 manual
severity: minor
blocking: 否(spec 已承認 manual,屬可改進;判準是不影響設計成立)
引句:「[manual:上線前在實驗專案照範本接上,造一筆命中跑一次推送前檢查與 lint-waive,結果記進這份計劃]」
- 段落:做 4、S4。
- 問題:這一版真正「接上」的動作,就是把範本文字從一條改成兩條。工具鏈裡沒有任何測試會讀 `linter精選目錄.md` 的 `sgconfig` 範本行。detekt 範本有(`scripts/test_lumos.py:128473` 一帶讀取 `detekt --input` 開頭的行再交給閘跑),ast-grep 範本沒有。`_lwt_sg_cmd` 自己拼命令字串。
- 後果:範本裡打錯 `sgconfig-review.yml` 路徑、漏 `--format sarif`、或哪天有人改掉範本,測試全綠。
- 建議:比照 detekt 那段,讀範本兩行、換掉工具鏈路徑後交給 `_lint_run_and_parse` 跑,斷言覆核級壞例有命中。

## F3 做 4 描述的範本現況跟主線不符
severity: minor
blocking: 否(措辭問題)
引句:「安裝句從「0.51.1 以上」改成釘 `pipx install ast-grep-cli==0.51.1`」
- 問題:主線型錄範本已經寫了 `pipx install ast-grep-cli==0.51.1` 或 `brew install ast-grep`(要 0.51.1 以上)。pipx 那句早已釘版,要改的只是 brew 那句與「以上」的措辭。
- 佐證:`docs/lumos-toolchain-knowledge/Systems/linter精選目錄.md` 第 192 行。實作者照 spec 字面改會困惑。
- 建議:改寫成「保留 pipx 釘版,brew 那句補『只在 0.51.1 實測過』」。

## F4 SARIF 自檢沒說明用哪份設定掃、掃哪個目錄,「樣本」過濾條件也沒驗
severity: minor
blocking: 否
引句:「拿 `rules-review/` 的 `kt-livedata-setvalue-background` 與 `rules-hints/` 的 `kt-value-assign-background` 兩條規則的壞例樣本用 `--format sarif` 掃」
- 問題:兩條規則各在不同設定檔(`sgconfig-review.yml` 與 `sgconfig-hints.yml`),spec 沒寫各用哪份。若實作者用 `sgconfig.yml` 掃,兩條都不會出現,自檢永遠報錯。
- 還有:`t_kotlin_rulepack_samples` 只留含「樣本」等字的問題,新訊息有「樣本」二字,算過關。但「讀不懂輸出照『跑不起來』報」那條,若其原因句不含這五個字之一,會被該測試濾掉而變成靜默通過。
- 佐證:`configs/ast-grep/kotlin-android/rules-review/state.yml` 第 1 行與 `rules-hints/state.yml` 第 1 行,兩個 id 都存在(已核)。`check.py` 的 `scan` 與 `_TIMED_OUT` 為共用逾時機制。
- 建議:寫明「各用自己目錄的設定檔」,並要求兩種失敗原因句都含「樣本」。

## 已核對、沒發現問題的項目
- **8 條出處不全規則的歸屬。** 我用型錄的 `(出處不全)` 列與規則訊息對照,這 8 條確實各掛一條,分散在 `rules-hints/` 的 api、architecture、compose、coroutines、flow、state、testing 共 7 支檔,testing 有兩條。「同檔還有 4 到 6 條」我數過也對。
- **壞例、好例樣本以規則 id 分目錄。** 樣本目錄是 `samples/bad/<id>`、`samples/good/<id>`,規則搬到 `rules-unwired/` 不用搬樣本。
- **文字同步清單。** 我 `git grep` 了 `rules-hints`、`rules-review`、`sgconfig-hints`、`sgconfig-review`,檔案集合與 spec 清單一致。唯一多出來的是 `rules/api.yml:234` 的一行路徑註解,它指的是 `rules-review/api.yml`,搬動後仍然成立。
- **新增告警閘的處置。** `_lint_new_run_cmds` 的預算不足會記成 `undone` 的 `budget`,推送前判擋。逾時、工具沒裝記成 `env`,放行並記帳。工作樹模式把 `budget` 與 `too-long` 歸成沒檢查到(rc3)而不擋。這跟 spec 的描述一致。我只讀了註解與分支,沒有跑推送模式。⚠
- **SARIF 等級。** `scripts/lumos:9267` 附近的 `level in ("note","none")` 過濾是資安證據用的 `_secev_sarif_hit`,不是新增告警閘。這與 spec 的「閘照收 note」不矛盾。
- **S4 的 `[manual:]`。** 在本專案允許,但見 F2。

## 圖譜節點(固定席)判定
計劃節點宣稱的行為是兩個目標、五件要做的事。本設計不破壞它,理由是:
- `kotlin規則包` 與 `linter精選目錄` 都沒有掛合約行(0 條合約,12 行 KEY 在後者),spec 只改 WHY 與 RULE 的字面並重新確認。
- 「不改新增告警閘的判定本身」這條邊界,我核到做 1 到 6 都沒有碰指紋、放行或逾時處置的程式。
- 做 5 收窄工作樹白名單,不影響推送前的行為。

總結:最高等級為 major,blocking 共 1 條
