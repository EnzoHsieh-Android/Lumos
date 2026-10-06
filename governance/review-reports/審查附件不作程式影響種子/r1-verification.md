severity: major

DESIGN-VERIFICATION-1：特殊字元路徑在分類前已失真，S1 無法保留真正的程式種子

severity: major

blocking: 是

引句:「路徑特殊字元使首行不可安全批次讀取；這些狀態不當作排除證據，保守保留。」

觀察：`impact --diff` 先以非 NUL 分隔的 `git diff --name-only` 取得檔名，再用 `splitlines()` 拆解。含換行、行分隔符等特殊字元的路徑，會在進入 `_impact_diff_modes` 前被 Git 引號化或被 Python 拆成多段；程式也沒有反引號解碼。因此後續處理的是偽路徑，不是真實 Git 路徑。

具體錯誤行為：若簿記目錄內的無副檔名程式帶特殊字元，輸出的 `files` 會含引號化字串或路徑碎片；逐檔 diff、家反查及事故內容比對均查不到真檔。條款所稱「保守保留」遂只留下無法使用的假種子，正式程式的家與事故可能漏派。

file: `scripts/lumos:41146`

file: `scripts/lumos:41151`

file: `scripts/lumos:41043`

file: `scripts/lumos:41055`

驗收空白：兩支主要控制測試只使用普通路徑，沒有特殊字元路徑，也未斷言這類程式的真實路徑、家與事故仍能命中。

file: `scripts/test_lumos.py:23051`

file: `scripts/test_lumos.py:23069`

file: `scripts/test_lumos.py:23092`

file: `scripts/test_lumos.py:23101`

判準：改後的驗收應以無損路徑取得方式餵入真入口，至少證明一支特殊字元路徑的程式仍以原始路徑出現在 `files`，且其家與事故會被推送；相鄰的普通卷證仍須被排除。這是補足既有 S1，不需要另建分類機制。

## 逐節結果

- 最小改法／S1：有上述 major。一般附件、副檔名程式、可執行檔、無副檔名 shebang、刪檔舊模式及 staged 索引模式已有實作與控制組；特殊字元分支在更早的路徑取得層失效。
- 證據與範圍：未發現新增問題。文件如實標明這是實作後補審，且沒有重設代碼審輪次。
- 實務隱患：未發現新增問題。守衛面已升高風險，沒有用「不改閘判準」排除。
- 回退：未發現新增問題。撤回分類修補及重驗既有程式例外的判準具體。
- 終審揭露的分類例外：除特殊路徑外，`.py`、`.sh`、可執行文字／文件副檔名、無副檔名腳本及已刪可執行檔均有真入口控制。
- 第二輪完整例外：共享 raw parser 確實同時提供模式與物件；舊 `_codeloop_raw_modes` 仍只投影模式對，未見既有消費者語意被破壞。
- 修復驗證的時間前提：未發現新增問題。兩個內容功能案例明示使用 30 秒測試預算；零預算另有禁止 Git／選檔探針與真時間斷言。文件也明確沒有宣稱所有正預算 Git 查詢都受硬期限約束。
- 併發、資源釋放及效能：批次物件讀取有數量、大小與 timeout 邊界，沒有新增長駐資源；未見額外 finding。

## 實際鏡頭逐項判定

- `Systems/retrieval-ranking`：遭上述 finding 破壞。特殊路徑的真種子、家與事故可能漏失。
- `Systems/測試假綠形態`：驗收不足。S1 正式寫出特殊字元承諾，但現有測試沒有讓該現場成立，屬「合約文字寬於測試覆蓋」。
- `Systems/pitfalls-code-loop`：未見破壞。raw parser 的舊模式投影、凍結物件選擇及零預算角色返回均維持既有語意。

## 已讀材料

- `/Users/enzo/.agents/skills/lumos-project-notes/SKILL.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/CLAUDE.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/MOC/index.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Projects/審查附件不作程式影響種子_計劃.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-snapshot.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/governance/review-reports/審查附件不作程式影響種子/r1-lens.txt`
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/lumos`（指定函式及相關 helper）
- `/private/tmp/lumos-review-artifact-impact-inputs/scripts/test_lumos.py`（對應測試）
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/retrieval-ranking.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/測試假綠形態.md`
- `/private/tmp/lumos-review-artifact-impact-inputs/docs/lumos-toolchain-knowledge/Systems/pitfalls-code-loop.md`
- 上述三個 Systems 節點的 `lumos contracts` 輸出

凍結副本與工作樹 spec 經 `cmp` 確認逐位元相同。未讀其他輪審查報告或結果。唯讀沙盒不允許建立臨時 Git repo，因此未執行特殊檔名實驗，也不把靜態核對冒稱為測試通過。

最嚴重 severity：major  
blocking 總數：1