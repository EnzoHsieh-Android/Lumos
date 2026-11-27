severity: clean

整份對照下來,第 3 版沒有引入第二種做法,也沒有跨層直呼;只有兩個判不準、不影響結論的註記(A1、A2)。

## A1 ⚠ 兩處對照都找得到既有做法,只有一個小缺口
severity: clean
blocking: 否
引句:「帳上最新那筆的 new_sha 等於這次挑到的 new_sha 才沿用,不等就排進要重跑」

**_choice_kill_pick 的比對寫法:同一套,沒有第二種。**

既有做法:
- 依覆蓋判的存活分支:`scripts/lumos:80071-80073` 取 `evs[-1]`(帳上最新一筆),用 `==` 比 `cov_sha`,不等就落到重跑。
- 依測試雜湊判的存活分支:`scripts/lumos:80076` 比 `evs[-1].get("tests_sha") == tests_sha`。
- 判讀事件:`_choice_layer_state` 在 `scripts/lumos:81263` 比 `ev["new_sha"] != new_sha`,不等就當作廢。

第 3 版在沿用存活的那個分支,把 `new_sha` 當成 `evs[-1]` 上多一項相等比對,形狀跟上面三處一致:
- 同樣取帳上最新一筆。
- 同樣用相等比對,不相等就走重跑。
- 殺掉、放行、依覆蓋判的存活、過期、跑不出結果的分支都不動。

資料來源也不是新做法:
- 這次挑到的 `new_sha` 取自 `x["mutant"]["identity"]["new_sha"]`,現成路徑在 `scripts/lumos:79678`。
- 帳上事件的 `new_sha` 欄位早已在 `scripts/lumos:18577` 的型別表裡。
- 覆蓋分支靠 `cov_sha` 把 `new_sha` 間接納入(`scripts/lumos:80441-80447`),所以覆蓋分支不用再補比對。計劃寫「依覆蓋判的存活不動」站得住。

唯一缺口是介面沒寫:
- `identity` 在 `scripts/lumos:79389` 有可能是 None,第 3 版沒交代這種情況的處置。
- 這是行為細節,不是架構分歧,所以不列為 major。
- 實作時只要照 `cs = ... if ... else None` 的寫法,取不到就當作對不上、重跑即可。

## A2 ⚠ S7 的實測做法與既有上線前實測同路,少了「只讀」的前後指紋比對
severity: clean
blocking: 否
引句:「在 `git clone --shared` 的複本裡,用主線版與本計劃版的 lumos 各跑一次 choice-points 輸出 JSON 比對」

既有做法:
- `docs/lumos-toolchain-knowledge/Verification/2026-11-22_選擇點第三批上線前實測.md` 的〈量法〉:
  - 主線版與分支版各跑一次 `lumos choice-points`。
  - 樣本固定,不抽樣。
  - 前後輸出逐字比對。
  - 跑前跑後對照治理帳指紋與 `git status`,證明是只讀。
- `docs/lumos-toolchain-knowledge/Verification/2026-11-17_選擇點第二批上線前實測.md:42`:在暫存區用 `git clone` 出複本,在複本裡實測。

S7 的作法是在複本裡,拿主線版和新版各跑一次 choice-points,再比對輸出。這跟上面的流程同一套。`--shared` 只是複本的建法不同,還是「不動原專案的複本加前後比對」,不算第二種做法。

一次性腳本放會談暫存區、不進 repo,符合專案不留一次性工具的慣例,也沒有新引入工具。

有一處判不準:
- S7 沒寫「跑前跑後治理帳指紋相同」這個只讀證明。第三批有寫,第二批沒有。
- 腳本只讀帳,且複本是 `--shared`(共用物件庫),風險低,不算分歧。
- 若想與第三批齊平,驗證紀錄可補上這一句。

最嚴重:clean
blocking 條數:0
