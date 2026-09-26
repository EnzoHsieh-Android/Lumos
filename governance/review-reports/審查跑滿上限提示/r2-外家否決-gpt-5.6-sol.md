severity: blocker

## F1 處置閘會在第一個完整輪立即收斂，走勢提示核心分支不可達
severity: blocker
blocking: 是——照 spec 改問處置閘後，合規輪會直接回 converged，根本累積不到可比較的最後兩輪。
引句:「最後一輪折入數 ≥ 前一輪 → **換做法**:拆小改動、回頭改設計、或整類拿掉。」
file: `docs/lumos-toolchain-knowledge/Systems/design-loop.md:48` 現行裁定是單輪每項發現折入或附理由接受即收斂。
file: `scripts/lumos:18397` 處置集合完整便判該步通過；`scripts/lumos:18574` 至 `scripts/lumos:18585` 沒有其他失敗便立即 PASS、寫 converged、回 rc0，不要求第二輪。
file: `scripts/test_lumos.py:24149` 至 `scripts/test_lumos.py:24168` 已釘死 r1 一輪全處置即可收斂，甚至另一席報 major 也不阻止 PASS。
重現場景：standard/high 新迴圈 r1 正常折完並記 carrier；下一次 `loop next --spec` 改問處置閘後立刻 converged，不會進 r2，更不會到 cap。能到 cap 的只剩處置、留痕或材料驗證不完整的異常帳；那時只能叫人修閘前提，`reshape`、`accept-with-reason`、`human-decides` 三條走勢分支沒有正常入口。這也直接破壞相關節點「處置閘單輪 PASS」的既有裁定。

## F2 fail_steps 沒定義處置閘實際失敗名稱到提示分類的映射
severity: major
blocking: 是——照欄位名逐字判斷會把處置失敗錯分成非處置失敗，輸出錯誤 advice。
引句:「`--json` 多一個 `cap_report` 物件:`fail_steps`(失敗步驟名清單)」
file: `scripts/lumos:18375` 至 `scripts/lumos:18376` 無 carrier 時實際失敗名是 `無處置帳`。
file: `scripts/lumos:18393` 至 `scripts/lumos:18395` 集合不完整時實際失敗名是 `處置集合`。
file: `scripts/lumos:18402` 至 `scripts/lumos:18404` 留痕缺欄的失敗名是 `留痕缺席`；其餘還有 `G3`、`留痕`、`quote`、`條款綁定`、`資安席`、`落點`。
spec 卻用「失敗原因只剩處置」作分支條件，沒有定義 `無處置帳`、`處置集合` 如何歸一成 `處置`，也沒說 `fail_steps` 放原始 token 還是顯示分類。某輪有人報 finding 卻缺 carrier 時，字面實作會因 token 不等於 `處置` 而回 `fix-gate`；按第二節規則則應先得到「沒記處置」，再由 `unknown` 優先處理，兩條路結果不同。

## F3 自動 cap-reached 會把尚待人裁的迴圈記成人裁放行並關門，且所寫更正路徑不存在
severity: major
blocking: 是——只要查詢一次到頂狀態，就會不可逆地污染治理統計並把未結案迴圈從開啟清單移除。
引句:「治理帳只追加,寫進去的記號會被 `gov --stats` 的跑滿計數」
引句:「判錯了要人工補記一筆 `loop rewrite` 或在治理帳另記更正」
file: `scripts/lumos:10675` 至 `scripts/lumos:10678` `loop next` 一判定到 cap 就立即寫 `cap-reached`，發生在人作出放行、重寫或續審決定之前。
file: `scripts/lumos:6752` 至 `scripts/lumos:6764` `gov --stats` 把只有 `cap-reached` 的編號直接計為「人裁放行」。
file: `scripts/lumos:8660` `cap-reached` 被列為關門事件，因此 `loop list` 會把它視為已結案。
file: `scripts/lumos:813` 至 `scripts/lumos:820` `loop rewrite` 只允許真正的整份重寫，且強制提供不同的 successor；它不是 cap 誤記更正指令。`lumos gov` 的 help 只有查詢參數，沒有「另記更正」寫入入口。
因此到頂只代表「停下來等人裁」，卻會先被帳面認成「人已裁放行」。誤記時若沒有真正的新重寫編號，spec 提供的兩個修復方式都不可執行。

## F4 「不改退出碼」與出口修正的必要行為直接矛盾
severity: major
blocking: 是——實作者無法同時遵守總則與 S1；任選一邊都會違反另一條驗收語意。
引句:「**只印,不改任何閘的判定與退出碼。**」
file: `scripts/lumos:8284` 至 `scripts/lumos:8289` 新迴圈目前委派舊 panel 閘會回 rc2。
file: `scripts/lumos:10669` 至 `scripts/lumos:10671` `loop next` 原樣傳回這個 rc2。
file: `scripts/lumos:10624` phase 只有 converged 回 rc0，其餘包含 cap-reached 都回 rc1。
本案核心正是把目前 rc2 的路徑改成處置閘 PASS 的 rc0，或處置閘未過且到頂的 cap-reached rc1。這不是「只印」；判定來源與退出碼都會變。若實作者為了守住粗體總則保留 rc2，S1 的出口修正仍未完成；若照 S1 實作，粗體總則與實務隱患的「不改退出碼」宣稱就是錯的。

實務隱患逐類：

- 併發：有碰。報告計算本身只讀，但處置閘 PASS 與 cap 路徑會追加治理帳；重複查詢也會重複追加。主要錯誤已列 F3。
- 效能：有碰。`loop next` 會再走處置閘、重讀帳本及判定輪報告與快照；spec 有揭露額外讀取。目前資料量下未取得具體超時或錯判證據，不另開 finding。
- 不可逆：有碰。`cap-reached` 是只增不改治理事件，且沒有真正的更正原語，見 F3。
- 守衛面：有碰。它改動 `loop next` 選哪一道收斂閘、rc 與關門帳語意，見 F1、F3、F4；不能列為已排除。
- 金流：無；所有路徑只處理本機檔案與輸出，沒有付款或計費呼叫。
- 對外送出：無；相關指令沒有網路或外部服務呼叫。
- 資源／秘密：無具體新增風險；沒有新依賴、憑證或外部輸入執行面。

已看,無: spec 與指定 LUMOS-SPEC 逐字相同；兩個 Wiki 連結、取代案、落點節點及 r1-intake 均存在，r2-intake 不存在；`loop next/status/rewrite/escape`、`canary record`、`quote-check`、`gov` 的參數均以 help 核對；三本帳的既有欄位與 r1 七席、17 條彙總數相符；`_review_yield_round`、`_loop_anchor_tier`、`_panel_retired_for` 均存在。第 1 輪的範圍排除、缺 `--spec` 優先、空輪算合法處置、只留一筆 converged、回放 readonly、JSON 需另接文字輸出等修正已有對應設計；但「真的能在正常流程跑到 cap」沒有解決，見 F1。指定計劃與 `Systems/loop-convergence-recording` 沒有登記正式 contracts；M1 的缺 spec 優先裁定未被破壞，處置閘單輪收斂裁定則被本設計的多輪走勢前提抵觸。

最嚴重 severity: blocker；blocking 共 4 條。
