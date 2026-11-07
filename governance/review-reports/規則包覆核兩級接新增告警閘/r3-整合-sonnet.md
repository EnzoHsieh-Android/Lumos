severity: major

## F1 做 5 與 S3 的「大小寫變體」寫法在 Linux CI 上不成立,和現有測試互相抵觸,也沒交代 samefile 找不到檔時怎麼辦
severity: major
blocking: 是——驗收條款 S3 綁的測試在 CI(ubuntu)上會紅或跟現有測試矛盾,屬於修補驗收不過。
- spec 段落:範圍做 5、驗收條款 S3、預期值表 S3 第三列。
- 引句:「指向 `sgconfig.yml`(含 `$HOME/` 寫法與大小寫變體) 應 照舊執行」
- 問題有三個:
  1. 現有白名單的大小寫處理方向相反。宣告寫成 `$HOME/Harness/...`(目錄大小寫不對)時,現有程式碼和現有測試都要求拒絕,而且原因是「照實際大小寫改宣告」。S3 若指目錄大小寫,就和 `t_lint_new_worktree_allowlist` 的斷言直接衝突。
  2. 若指檔名大小寫(例如 `SGCONFIG.YML`),結果取決於檔案系統。macOS 不分大小寫,samefile 判同一支,放行。CI 是 `runs-on: ubuntu-latest`,那個路徑根本不存在。spec 沒說這個測試在 Linux 上怎麼寫。
  3. 做 5 講的「既有判目錄時的 samefile 救濟」其實是個永遠拒絕的分支(只負責換一句「大小寫不同」的原因),不是放行分支。同一支檔判斷得新寫。新寫的 `os.path.samefile` 在路徑不存在時會丟 `OSError`,而 spec 沒要求接住。若把例外放過去,收工鉤子會當掉。若判在 `commonpath` 之後,Linux 上的 `SGCONFIG.YML` 也會走到那一步。
- 佐證:
  - file: `scripts/lumos:41184-41277`(主線 `_lint_wt_allow`)。大小寫那段 samefile 只用於回傳拒絕原因。
  - file: `scripts/test_lumos.py:132186-132190`(主線)。斷言宣告路徑大小寫不同時 `g is None`。
  - file: `.github/workflows/ci.yml:27`(主線)。runs-on 是 ubuntu-latest。
- 修法方向:S3 把「大小寫變體」拿掉,或明寫成只在不分大小寫的檔案系統上才驗。做 5 要寫明用 try/except OSError 判不是同一支,並回傳拒絕原因。

## F2 接閘的覆核級規則本身就是已知會誤報的一級,跟 spec 用來排除提示級的同一條 RULE 自相矛盾
severity: major
blocking: 是——d2 的立論(有效力的誤報一成 RULE 不推翻)套到覆核級會得出相反結論。接上之後誤擋量沒有機械上限,而驗收只有人工那條 [S4]。
- spec 段落:決策 d2、範圍做 4、實務隱患「誤擋量」、S4。
- 引句:「接閘的是覆核級 12 條,在真專案的命中量沒量過。」
- 問題:
  - d2 以「規則包那條 RULE:誤報超過一成就降提示級」為由,不接提示級。
  - 覆核級的定義就是「形狀分不出對錯」。好例樣本裡已有已知誤報的 `review-fp-*.kt`,至少兩條規則有記:`kt-statein-eagerly`、`kt-suspendcancellable-no-oncancel`。
  - 同一條 RULE 對這些規則一樣適用:誤報不是未知,而是已記錄。
  - spec 對提示級要求「先在專案量過誤報低於一成才接」,對覆核級卻是先接、上線前才量。這個非對稱沒有理由。
  - 做 6 把 RULE 改成「降到提示級或 `rules-unwired/`」,等於承認覆核級不在去處清單裡,卻讓覆核級可以擋人。
- 佐證:
  - file: `configs/ast-grep/kotlin-android/samples/good/kt-statein-eagerly/src/main/kotlin/review-fp-reason-above-property.kt:1`(主線)。第一行就寫「語意覆核級已知誤報」。
  - file: `docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md:24`(主線)。RULE 欄位齊全,`[confirmed:2026-11-05]`。
- 修法方向,二選一:
  - (a) 把已有 `review-fp-` 樣本的規則先放 `rules-unwired/`,其餘等量過再接。
  - (b) 明寫「覆核級為何例外於該 RULE」,並附 `[依據:人]` 的使用者裁定出處。目前只引用「語意覆核照計畫重寫」,沒有一句講到可以不受這條 RULE 約束。

## F3 做 6 的文字同步清單仍漏項,漏的幾處會把人導向現在會擋的目錄
severity: minor
blocking: 否——只是文字漏同步,不改變機制,補清單即可。
- spec 段落:範圍做 6(「用主線 git grep 列齊」)、`lands_in`。
- 引句:「檔案節分檔那行補第四個目錄」
- 我用主線 `git grep`(預設不接、接上前不擋、盲判、只准 hint、提示級、語意覆核、rules-review、sgconfig-)逐項對過。型錄 checks-catalog 裡「接上前不擋」7 格(API-17、STATE-1、STATE-7、STATE-16、CO-44、DATA-10、DATA-36)與「批一」3 格(API-11、STATE-4、TEST-5)和 spec 列的相符。「預設不接」共 40 格,等於 spec 說的 8 列出處不全加其餘 32 格,數量對得上。漏的有:
  1. `Systems/kotlin規則包.md` 第 73 行第二句:「審查中被點出形狀分不出對錯的,不再放寬形狀,直接留在覆核級」。spec 只改了該行第一句(新規則先放哪)。這句不改,工作流程會把高誤報規則導進現在會擋的目錄,和 F2 同源。
  2. `Issues/Kotlin規則包代碼審放行的小問題.md` 第 17 行 REVISIT(2026-11-20):「規則誤報就改規則或搬語意覆核級」。覆核級現在會擋,搬進去就是接閘。這是有日期的待辦,到期有人照做會出事。
  3. `check.py:29` 的 `REVIEW_FP_PREFIX` 註解 spec 有列。`check.py:362-363` 的「語意類要有盲判席」是型錄欄位另一套機制(情境表態與盲判),不在此範圍,保持不動是對的,不必列入。
  4. 搬 8 條規則後型錄第 881 行的「規則包條數:207(…hint 50)」:嚴重度計數不變,不用改。但那一行說「讀 `rules*/*.yml` 數」,glob 要能涵蓋新目錄;`rules-unwired/` 符合這個 glob,沒問題。
  5. 白名單變窄屬於新增告警閘的行為,家在 `Systems/pitfalls-code-loop`(REVISIT 第 100 行談的就是這個白名單),`Systems/回合結束寫法檢查` 第 19 行 RULE 綁 `t_lint_new_worktree_allowlist`。兩篇都不在 `lands_in`,但按專案 CLAUDE.md 鐵則 5,改到的程式的家要寫說明。
- 修法方向:清單補上 1、2、5(5 要把 `Systems/pitfalls-code-loop` 併進 `lands_in`)。

## F4 收工白名單寫死單一檔,會讓既有照舊範本額外宣告 review/hints 的消費專案無聲退化,將來新增的規則包也自動被擋
severity: minor
blocking: 否——spec 已把「收工看不到覆核級」列入天花板,影響是收工少一道提醒,推送前閘仍擋。
- spec 段落:範圍做 5、不做、天花板 4。
- 引句:「覆核級、`sgconfig-unwired.yml` 與將來任何新設定都只在推送前判(或不判)」
- 問題:
  - 主線 `_lint_wt_allow` 現在放行 `configs/ast-grep/` 底下任何檔,而這個目錄現在只有 kotlin-android 一包,三份設定。主線範本也教過「提示級要用就另加一條宣告指向它」。
  - 照那句做過的消費專案,他們的 hints 宣告在新規則下變成收工不跑。如果 hints 是他們唯一的 ast-grep 宣告,收工整次變成 `not-checked`、原因是「刻意不查」。
  - spec 的「不自動替消費專案改設定」讓這些專案不會被通知。我在工具鏈自己的 `.lumos/lint.json` 查過,只宣告 ruff,沒有 ast-grep,所以工具鏈自己的收工不受影響。消費專案裡有沒有人宣告過 hints,我看不到,⚠ 判不準。
  - 白名單寫死 `kotlin-android/sgconfig.yml`。將來 `configs/ast-grep/<別的棧>/sgconfig.yml` 也會擋的規則包,收工一律被拒,改法是要再動 `scripts/lumos`。
  - 工作樹模式每回合印「工作樹模式不跑:…」那行雜訊,spec 沒提。
- 佐證:file: `scripts/lumos:41530-41569`(主線 `_lint_new_wt_verdict` 對 `wt_rejected` 的處理)。
- 修法方向:至少在 d 裡寫明已知的退化範圍。更好的做法是白名單用「檔名 `sgconfig.yml`」加「工具鏈 configs/ast-grep 底下」判斷,不寫死棧名。

## 其餘風險類逐類答(無需成為 finding)
- 端到端(消費專案照兩條範本接上後):
  - 推送前閘兩條宣告都跑。`_lint_new_cmd_targets` 先挑命令、保留宣告順序,所以 ast-grep 排前面合理。
  - 預算不夠時,推送前閘判擋,工作樹模式判「沒檢查到」(rc3)不擋。spec 做 4 寫「推送被擋」與此一致,而收工那邊不擋這點 spec 沒寫,不影響正確性。
  - 收工檢查:`sgconfig.yml` 放行、`sgconfig-review.yml` 進 `wt_rejected`,不影響前者的判定。
  - `lint-check` 只驗每條命令有沒有 `{LINT_SARIF_OUT}`,兩條並列沒有互斥或重複檢查,所以不會有新報告。
- 檔案與型錄自檢:做 2 的 `dir` 鍵、`rules-unwired` 嚴重度不限,和 `check.py` 現況(`_DIR_SEVERITY`、`CONFIGS`、第 394 行)接得上。`t_kotlin_rulepack_samples` 的「規則目錄全空」迴圈要加第四目錄,spec 已列。
- 對固定席節點的判定:
  - `Systems/kotlin規則包`:這份設計會改變它的 WHY(出處不全只准提示級)、RULE(降提示級)與檔案節,spec 都已列入同步,但上面 F2、F3-1 兩處會讓它的 RULE 與工作流程自相矛盾。判「影響,需同步」。
  - `Systems/linter精選目錄`:該節 12 行 KEY 與範本會被改寫,其中「提示級規則預設不接」那句 spec 已改。其餘 KEY 不涉及 ast-grep。判「影響範圍可控,已列入」。
- 既有測試:我讀過主線全部引用 `_lint_wt_allow` 的測試(`t_lint_new_worktree_allowlist`、`t_lwt_r1_shellfree_argv` 等)。它們用的設定檔都是 `kotlin-android/sgconfig.yml`,其餘是被拒的繞法,新白名單不會讓它們翻紅。我沒有實際跑,理由是只准 `-k` 子集,而 spec 尚未實作,跑了也只是跑現況。

總結:最高等級為 major,blocking 共 2 條
