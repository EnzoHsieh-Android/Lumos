severity: major

### C1 多支流程檔的情境:「有一支被綁到或被提到就不列」沒有測試守
severity: major
blocking: 是
引句:「有一支被綁到或被提到就不列;沒有流程檔的情境不列」
1. 規格 S1 與測試 docstring 都寫明「有一支被綁到或提到就不列」。程式在 `no_notes = sorted(k for k, fl in case_flows.items() if fl and not any(seen(f) for f in fl))` 用 `any`。
2. 測試用到的情境全是單一流程檔(`_e2enote_proj` 的 login.ok 與 other.x,`_e2eg_proj` 的 login.ok)。沒有任何一支測試造「一個情境列兩支流程檔、只有一支有筆記」的輸入。
3. 重現:我在乾淨 clone 把 `not any(` 改成 `not all(`,執行 `python3.14 scripts/test_lumos.py -k t_android_e2e_coverage`,結果 `41 passed, 0 failed`,全綠。
4. 具體壞法:情境 `login.ok` 的 flows 是 `[a.yaml, b.yaml]`,只有 a 被筆記合約綁到。改成 `all` 後 `login.ok` 會被多列,規格 S1 要求不列,測試抓不到。

file: `scripts/test_lumos.py:21440`(`t_android_e2e_coverage_cases_without_notes` 全函式)

### C2 對照表的流程路徑寫 `./` 開頭時,正文路徑比對的正規化沒有測試守
severity: major
blocking: 是
引句:「照對照表的寫法,去掉開頭 `./`」
1. 規格明寫正文比對要先去掉開頭 `./`。程式靠 `case_flows` 裡的 `_e2e_norm(x)` 做到。
2. 所有測試的 `flows` 都寫 `.maestro/login.yaml`,沒有 `./.maestro/...` 的輸入。
3. 重現:我在乾淨 clone 把 `[_e2e_norm(x) for x in c.get("flows")...]` 的 `_e2e_norm` 拿掉,跑同一組 `-k t_android_e2e_coverage`,結果 `41 passed, 0 failed`。
4. 真實後果:此時對照表寫 `"./.maestro/login.yaml"`、筆記正文寫 `.maestro/login.yaml` 的情境,會因為 `"./.maestro/login.yaml" in text` 為假而被誤列為「沒有筆記提到」。
5. 對比:我把正文比對整段拿掉,有 6 支測試翻紅,所以正文提到本身有守,只有 `./` 這個規格點沒守。

file: `scripts/test_lumos.py:21440`(`t_android_e2e_coverage_cases_without_notes` 全函式)

### C3 正文比對用子字串,短路徑會被別的檔名誤算成「提到」
severity: minor
blocking: 否
引句:「return bool(names.get(flow, set()) & bound) or any(flow in t for _r, t in texts)」
1. 輸入:對照表流程列 `login.yaml`(放在專案根,不帶資料夾),某篇筆記正文寫 `relogin.yaml`。
2. 走到 `any(flow in t ...)`:`"login.yaml" in "…relogin.yaml…"` 為真,該情境被當成「有筆記提到」而不列,報告少列一個缺口。
3. 只影響只報告不擋的缺口清單,而且需要流程檔放在根目錄且檔名是別的檔名的尾巴,所以標 minor。

file: `scripts/lumos:42284`(`_e2e_note_gaps` 內的 `seen`)

## 固定席與 manifest 逐條判定

- manifest 0 條,沒有逐條可判。
- 效能與 doctor 10 秒上限:
  - `timeout=10` 只管 `git ls-files`,`load_vault_safe` 不在這個上限內,但它自己有檔數與位元組上限(10000 檔、64MB)。
  - 我在本 repo 實測 948 篇筆記讀一次約 0.05 秒,所以不構成問題。
  - 計劃〈實務隱患〉寫「沿用既有的 10 秒上限」是措辭不精確,不影響行為。
- lumos-cli-read、測試假綠形態、guard-kill、design-loop、lifecycle、bound-tests-gate 等固定席節點:
  - 這份 diff 只在 `scripts/lumos` 新增唯讀的報告函式與 doctor 一行,沒有動它們各自宣稱的行為。這些行為是 search 濾網、guard kill 的 rc 與 JSON、re-inject、處置閘、綁定測試閘。
  - 測試假綠形態那條要求「還原翻紅釘要有前置斷言證明現場成立」。本次沒有修 bug,但上面 C1、C2 就是翻不紅的情況。
- pitfalls-code-loop、loop-convergence-recording 的 ★RISK★:
  - 沒有動審查迴圈、記帳或 pitfalls 的程式。
- 角色卡(後端):
  - 新程式沒有網路呼叫或交易,也不寫檔,只讀 `.lumos/config.json`、流程檔與圖譜。
  - 例外:`OSError` 在讀流程檔時有接。
  - 其他邊界:
    - 平台設定壞時有走回退路徑,測試覆蓋。
    - 流程檔讀不到時回空集合,只靠正文對上,與規格〈實務隱患〉一致。
    - 中文 `name:` 會被 `MAESTRO_NAME_RE` 排除,README 已明寫。
- README 中英兩句的說法:
  - 與程式行為一致:兩項只報告不擋,沒有知識圖譜時略過。
  - 英文版寫 "projects without a knowledge graph skip both",與程式回傳 `None` 相符。
- 規格對照:S1 到 S4 的字面輸入走過一遍,結果與規格相符,只有 C1、C2 的測試覆蓋缺口。

共 3 條,其中 major 2 條
