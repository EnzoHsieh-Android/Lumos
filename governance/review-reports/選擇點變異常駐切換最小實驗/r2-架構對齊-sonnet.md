severity: minor

## A1 量測繞過治理帳,另用一套初始化腳本加外層殼計時
severity: minor
blocking: 否
引句:「量測不經 choice-kill,原型只在實驗專案暫存分支。」
既有做法:第四段實測的數字是從實驗專案治理帳那次 run 讀出的(`docs/lumos-toolchain-knowledge/Verification/2026-11-26_選擇點變異加速第四段實驗專案實測.md:19`)。第二段 RETIRE-IF 讀的也是帳上的 `secs`、`base_secs`、`merged` 欄位(`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速_計劃.md:27`)。
差在哪:本稿用外層殼取 T、用 `Test.afterTest` 取 Σt,這是第二種量測方式。理由站得住:治理帳沒有每支測試的時間,而且本稿要量的是 choice-kill 流程以外的成本。第四段的包裝腳本也是本機自訂,所以不算跨層。
建議:在〈做法〉補一句,說明帳上的 `secs` 拆不出測試時間,所以才另量。這樣下一個讀者不會把兩套數字直接相比。
⚠ 我沒查到第四段包裝腳本的內容,只看到驗證紀錄的描述。

## A2 臨時工作樹與暫存分支用手工建,沒提到既有的 `_isolated_worktree`
severity: minor
blocking: 否
引句:「原型放實驗專案暫存分支 `exp-schemata`,不進 Lumos」
既有做法:choice-kill 的隔離工作樹由 `_isolated_worktree` 建在 mkdtemp 的 `scratch` 之下,初始化腳本放 `scratch` 內、不弄髒工作樹(`docs/lumos-toolchain-knowledge/Projects/選擇點變異加速第四段_計劃.md:58`)。
差在哪:本實驗不走 choice-kill,手建工作樹合理。`exp-schemata` 這個分支名在 repo 裡找不到前例,但也沒有衝突的慣例。回退節已寫明用字面絕對路徑刪除,符合全域規則。
建議:在〈做法〉或〈回退〉寫明臨時工作樹放在哪、誰負責刪。

## A3 驗證紀錄與落點寫法照既有慣例,沒有第二種做法
severity: clean
blocking: 否
引句:「量測結果寫成驗證紀錄(`lumos new verification 2026-11-28_選擇點變異常駐切換最小實驗實測 --plan Projects/選擇點變異常駐切換最小實驗_計劃 --systems Systems/guard-kill`)」
既有做法:`scripts/lumos:85892-85895` 的 `new verification` 支援 `--plan` 和 `--systems`,命名格式與第四段的驗證紀錄一致。結論寫成 `Systems/guard-kill` 的 FACT 並帶 `[來源:人工]`,符合專案的 FACT 格式。否決時回改第二段〈依據來源〉與 PRIOR-ART,跟第三段、第四段互相回指的做法一致。
差在哪:沒有差異。

總結:整體沿用既有的驗證紀錄、落點與回頭條件做法,沒有跨層直呼。只有量測方式與臨時工作樹兩處屬於合理的另起做法,各列為 minor 並建議補一句理由。
