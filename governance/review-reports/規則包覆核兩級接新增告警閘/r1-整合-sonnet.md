severity: major

我把設計當投稿審了一遍,逐節讀完,現況假設都查過。實驗放在 `/tmp/lumos-seat-work/規則包覆核兩級接新增告警閘/整合-sonnet/`,沒改 repo 任何檔。我在那裡裝了 ast-grep 0.51.1,拿真規則包的壞例樣本掃了三份設定,又建了臨時 git repo 跑 `lumos lint-new`。

## F1 範本三條宣告也會接上「回合結束檢查」,spec 完全沒評估
severity: major
blocking: 是(這是新增的會擋入口,不在設計範圍內,上線後每個消費專案的每個回合都會被它影響)
- spec 段落:範圍 4(宣告範本)、實務隱患、天花板 2。
- 問題:spec 只談「推送前」擋。但 Stop 鉤子(收工寫法檢查)的預篩條件是 `.lumos/lint.json` 有 ast-grep 字樣。它會用寫死白名單 `_lint_wt_allow` 在工作樹模式跑所有 ast-grep 宣告。
  - 白名單只認 `--config` 在 `<工具鏈根>/configs/ast-grep/` 底下的路徑,新範本的三條都過得了。
  - 所以兩級新增命中,包含誤報偏高的提示級,會在每回合結束擋 agent,同回合最多三批。
  - 擋住之後 agent 的唯一出口是 `lint-waive`,沒有互動終端就記成 AI 放行。AI 會變成放行的主要作者,spec 的天花板只說「AI 也能放行」,沒意識到這是預設路徑。
  - 鉤子總預算約 19 秒,單條命令保底 1 秒,三條各跑兩邊。預算不夠時後面的命令「歸沒檢查到、不擋」,哪幾條會被丟取決於宣告順序,spec 沒規定。
  - 所謂「doctor 數、同一個天花板」,實際沒有上限。doctor 只在放行清單裡 AI 放的有幾條時印軟提醒,不擋,而且健檢軟提醒每段只印前三條。
- 佐證:`scripts/lumos` 的 `_lint_wt_allow`、`_lint_new_wt_verdict`、doctor 新增告警閘放行段(約 4198–4232 行)。`stop-lint-hook.py` 的說明寫「預篩(repo 根的 .lumos/lint.json 有 ast-grep 字樣)」。`scripts/merge-claude-settings.py` 的 `HOOK_BUDGET["stop-lint-hook.py"]` 是 30。
- 引句:「專案宣告了這兩份規則設定,推送前每一筆這次新帶進來的命中就跟一般新增告警一樣被擋」

## F2 S2 的驗證落在一個不存在的 CI 步驟,而且 SARIF 問題會被現有測試濾掉
severity: major
blocking: 是(條款寫成的驗法驗不到;一旦 SARIF 檢查失敗,CI 照綠)
- spec 段落:範圍 3、驗收條款 S2。
- 問題:
  - CI 沒有獨立的「型錄自檢那一步」。`.github/workflows/ci.yml` 只有「裝釘版本的 ast-grep」(0.51.1)接著跑測試分片。
  - 唯一在 CI 跑完整模式的是 `t_kotlin_rulepack_samples`,它呼叫 `m.check(sg)`。
  - 這支測試只留訊息含「壞例、好例、樣本、載入、祖先」任一詞的問題。新增的 SARIF 問題如果措辭沒包含這幾個詞,會被靜默丟掉,CI 照綠。
  - spec 沒規定問題措辭,也沒規定要把 S2 綁測試。「看最後兩行」沒有地方可看。
- 實驗結果:spec 擔心的「提示級在 SARIF 沒輸出」,在 0.51.1 不成立。我拿壞例樣本各掃一次:
  - 覆核級 60 筆,level 全是 `note`。
  - 提示級 148 筆,level 全是 `note`。
  - 會擋的規則 488 筆(error 82、warning 406)。
  - 閘的 SARIF 解析讀的是 uri、行號、訊息、ruleId,完全不讀 `level`,所以 `note` 不會被濾掉。
  - 因此 spec 的備案(提示級提到 info)是死路。真正需要的是把「至少一筆」寫成有綁測試、措辭含關鍵詞的檢查。
- 另注意:消費專案裝的是 `brew install ast-grep`,只要求 0.51.1 以上,沒釘版本。SARIF 對應只在 CI 這一版驗過,spec 天花板 3 有寫,但範本的安裝句沒提醒。⚠ 新版 ast-grep 的對應是否不變沒人驗。
- 佐證:`.github/workflows/ci.yml` 第 141–144 行;`scripts/test_lumos.py` 的 `t_kotlin_rulepack_samples` 內 `sample_probs = [p for p in probs if any(k in p[1] for k in (...))]`;`scripts/lumos` 的 `_lint_run_and_parse`。
- 引句:「[manual:CI 的型錄自檢那一步(要 ast-grep 0.51.1)看最後兩行沒有 SARIF 相關問題]」

## F3 圖譜裡仍有效的 RULE 和工作流程跟新接法直接矛盾,spec 只說「補 WHY」
severity: major
blocking: 是(`Systems/kotlin規則包` 那條 RULE 欄位齊全、半年內確認過,有挑戰程式碼的效力,spec 沒處理就上線會讓筆記和行為互打)
- spec 段落:範圍 5、依據來源表第 3 列。
- 問題:接上之後,覆核級與提示級都會擋,「新增命中降到不擋」的意思變了。`Systems/kotlin規則包` 有三處沒被列入改動:
  - `RULE:規則在真專案誤報超過命中的一成就降提示級或改形狀`(since、retire、confirmed 2026-11-05 齊全)。降提示級不再等於不擋,現在只有搬進 `rules-hints-unsourced/` 才不擋。
  - 工作流程第 1 點:「新規則一律先放語意覆核級,量過誤報低於一成才升到會擋的 `rules/`」。覆核級現在跟 `rules/` 一樣擋,這個分階段保護沒了,新規則一寫進去,消費專案拉工具鏈後下一次推送起,每筆新命中就被擋。
  - 第 62、63 行本文:「接上前範本不接」「範本預設不接」。
  - 既有 WHY(第 20 行,綁 `t_kotlin_catalog_rows_wired`)寫「引用它的規則只准提示級」,範圍 2 把它改成「只准放 `rules-hints-unsourced/`」,WHY 的字面和綁的測試都要同步翻案。spec 只寫「補 WHY」,沒寫翻案或作廢舊 WHY。
- 佐證:`docs/lumos-toolchain-knowledge/Systems/kotlin規則包.md` 的 WHY(第 20 行)、RULE(第 24 行)、第 62–63 行、第 73 行;`scripts/test_lumos.py` 的 `t_kotlin_rulepack_messages_cite_catalog` 斷言「只准 hint 級」。
- 引句:「補 WHY;前案計劃標作廢、指向本計劃。」

## F4 前案作廢後的反向引用清單列不齊
severity: minor
blocking: 否(漏的是文字同步,不影響行為,推送前的圖譜檢查會逼著補)
- spec 段落:範圍 5。
- 問題:spec 只列了 `checks-catalog.md` 第 11 行、`check.py` 開頭三級說明、`Systems/kotlin規則包` 與前案本身。我在主線查到還指向前案的有:
  - `Projects/Android協程與API寫法機械檢查標準_計劃` 第 138 行。
  - `Projects/Android寫法語意情境表態與盲判_計劃` 第 60 行。
  - `check.py` 第 29 行(`REVIEW_FP_PREFIX` 註解)與第 777 行附近的註解,寫「要靠盲判排除」。
  - `Systems/kotlin規則包` 第 62 行。
- 另一處數字對不上:`checks-catalog.md` 的覆核級列裡,確實只有 7 格寫「接上前不擋」(API-17、STATE-1、STATE-7、STATE-16、CO-44、DATA-10、DATA-36),跟 spec 的「7 格」相符。但 API-11、STATE-4、TEST-5 這三條覆核級列,批次欄寫的是「批一」(「會擋的規則已上線」),在舊制下就是錯標,spec 沒提。
- 手冊與 skill:`README*`、`skills/kotlin-idioms/SKILL.md`、`scripts/lumos` 的 doctor 範本都沒講 ast-grep 範本,沒有別處要改。
- 佐證:`git grep` 主線的「語意覆核級命中走盲判」;`skills/kotlin-idioms/checks-catalog.md` 第 159、165、227、230、233、242、303、506、532、584 行。
- 引句:「`check.py` 開頭三級說明的註解」

## F5 消費專案已自己加過提示級宣告時,命中會重複列出
severity: minor
blocking: 否(只是顯示與計數膨脹,放行一次仍覆蓋兩筆)
- spec 段落:範圍 4。
- 實驗:`.lumos/lint.json` 放兩條指向同一份 `sgconfig-hints.yml`、命令字面不同(一條 `--config`、一條 `-c`),掃兩筆真命中。
  - 結果:`lint-new` 回報 total 4,同一規則同一行出現兩次,指紋相同。
  - 命令字面完全相同的兩條會被去重,不受影響。
- 影響:舊範本明寫「要用就另加一條宣告指向它」,這類專案照新範本再抄一條,就會雙倍計數。RETIRE-IF 的命中數與統計也跟著失真。放行一次兩筆都蓋掉。
- spec 的「不自動替消費專案改」沒有給「檢查是否已有等價宣告」的提示。
- 其他整合點(都不影響):
  - `lumos lint-check` 對三條新範本宣告和上述重複宣告都回「宣告健康」,它只驗佔位符與引號,不驗重複。
  - 時間:三份 ast-grep 各掃約 0.03 秒,在我的臨時 repo 裡,1 條對 4 條宣告的推送前閘各約 1.4 秒,多跑兩份可忽略。消費大專案如 nowinandroid(310 支檔)未實測,但 ast-grep 本身不是瓶頸。
- 佐證:`scripts/lumos` 的 `_lintcheck_validate`;臨時 repo 實測。
- 引句:「三條同一個寫法、各自 `{LINT_FILES}`、`{LINT_SARIF_OUT}`」

## F6 新檔需要家,8 條規則其實是拆檔,且舊測試要翻案
severity: minor
blocking: 否(提交時的「每支檔有家」與測試會逼出來,屬實作細節遺漏)
- spec 段落:範圍 1、2。
- 問題:
  - 新增 `sgconfig-hints-unsourced.yml` 與 `rules-hints-unsourced/*.yml`,鐵則 5 要求每支程式檔有家。`Systems/kotlin規則包` 的 about_code 目前只列 `check.py`、三份 sgconfig、型錄與測試範本,spec 的 lands_in 沒寫要把新檔補進 about_code。
  - 8 條出處不全的規則分布在 7 支 `rules-hints/*.yml`(api、architecture、compose、coroutines、flow、state、testing),每支同檔還有 4 到 6 條有出處的規則。所以「搬」是把多文件 yaml 拆開,不是移檔。「檔名照原主題」可行,但要避免拆壞其他規則的載入。我數出的 8 條對應規則是 `kt-error-by-message-string`(API-36)、`kt-click-navigate-unguarded`(ARCH-3)、`kt-compose-preview-no-theme`(UI-103)、`kt-mutex-reentrant`(CO-37)、`kt-asflow-not-cancellable`(FLOW-14)、`kt-whilesubscribed-no-timeout`(STATE-9)、`kt-prod-reads-system-clock`(TEST-16)、`kt-robolectric-legacy-looper`(TEST-33),與 spec 的 8 列吻合。
  - 型錄主表標「出處不全」的共 34 列,其中引用它們的規則目前只有這 8 條。
- 佐證:`Systems/kotlin規則包.md` frontmatter about_code;上述 7 支檔的規則 id 與訊息編號。
- 引句:「新增 `sgconfig-hints-unsourced.yml` 只載這個目錄。」

## F7 RETIRE-IF 的分母在現有帳裡記不到
severity: minor
blocking: 否(條件寫了但現在量不出來,屬後續落地)
- spec 段落:RETIRE-IF、REVISIT:2026-12-08。
- 問題:RETIRE-IF 要算「新增命中有八成以上被放行」。放行有帳(`lint-waivers.json`,記規則、檔、理由、誰放)。但被擋後改掉的命中沒有任何記錄:
  - `_LINT_NEW_COUNTED_KINDS` 只數 `fail-open`、`skipped`、`skipped-env`、`warned`、`relax-deferred`、`no-baseline`,沒有「擋下幾筆、哪條規則」。
  - 放行檔與治理帳都在各消費專案自己的 repo,工具鏈這邊看不到。
  - 所以八成放行率和「少於 10 筆新增命中」兩個條件都算不出來。
- 佐證:`scripts/lumos` 的 `_LINT_NEW_COUNTED_KINDS`、`_lint_new_kind_counts`。
- 引句:「上線八週後,覆核兩級的新增命中有八成以上被放行、而且放行理由多是誤報」

## 固定席逐條判
- `Systems/kotlin規則包`(0 條合約、0 行 KEY):不是「不影響」。它有一條效力完整的 RULE(第 24 行)、一條綁測試的 WHY(第 20 行,`t_kotlin_catalog_rows_wired`)與工作流程第 1 點,都被本設計的「覆核與提示級都擋」翻掉,見 F3。沒有合約行會被破壞。
- `Systems/linter精選目錄`(12 行 KEY、0 條合約):其他 KEY 行不影響,宣告範本與第 198 行「提示級規則預設不接」被本案改寫是預期內。範本改三條不會破壞該節點宣稱的 `{LINT_FILES}` 與 `$HOME` 規則,新範本三條都過 `_lint_wt_allow` 與 `lint-check`。
- 風險類逐類答:
  - 驗得過嗎:`lumos lint-check` 驗得過三條範本宣告。
  - 時間:不是問題,見 F5。
  - 重複:會,見 F5。
  - CI:有 ast-grep 0.51.1,但沒有獨立的型錄自檢步驟,見 F2。
  - SARIF:提示級在 0.51.1 有輸出,見 F2。
  - 前案反向引用:見 F4。
  - 手冊與 skill:沒有額外要改,見 F4。
  - 回合結束鉤子:新增,見 F1。

臨時資料(虛擬環境、規則包副本、實驗 repo)都在上面那個目錄,依規定由編排者收貨後刪,我沒動。

總結:最高等級為 major,blocking 共 3 條
