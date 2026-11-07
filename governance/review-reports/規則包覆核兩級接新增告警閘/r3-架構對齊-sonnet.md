severity: minor

審查依據:`git -C /Users/enzo/orca/workspaces/lumos-toolchain/rulepack-review-bj show Lumos/main:<路徑>` 的現況對照 r3-snapshot.md。

## F1 做 5 用 samefile 放行,跟既有 samefile 只用來拒絕不一致
severity: minor
blocking: 否
引句:「用既有判目錄時的 `os.path.samefile` 救濟,不比字串」
佐證 ``scripts/lumos:41269-41276``(既有 samefile 迴圈只在 `not inside` 時,為了找出大小寫不同的祖先目錄而回「照實際大小寫改宣告」,是拒絕路徑);S3 要求「大小寫變體照舊執行」,等於把 samefile 從拒絕改成放行,結構一樣但語意相反,計劃沒講明。

## F2 白名單形狀從「目錄前綴」變成「單檔」,拒絕原因句也沒對上既有格式
severity: minor
blocking: 否
引句:「工作樹模式只自動執行規則包會擋的 sgconfig.yml,<那支檔名> 留給推送前」
佐證 ``scripts/lumos:41277-41283``
- 形狀:既有是白名單,判法是「`realpath` 加 `commonpath` 落在 `configs/ast-grep/` 底下」,都回 `(None, 原因)` 二元組,這點新設計一致。差別是既有範圍是整個目錄樹,新設計收成單檔。
- 原因句:既有都是「事實加括號裡的實際值」,例如 `f"--config 的真實路徑不在工具鏈的 configs/ast-grep/ 底下({real})"`。新句帶 `<那支檔名>` 佔位,沒寫印的是 `real` 還是 basename,也沒寫是否跟既有的路徑括號格式一致。
- ⚠ 我沒在 `scripts/lumos` 找到其他地方寫死 `kotlin-android`。通用的 `_lint_wt_allow` 會第一次內嵌規則包專屬路徑,這是新的耦合,但屬結構判斷,我不確定算不算第二種做法。

## F3 `rules-unwired` 不限嚴重度,跟 `_DIR_SEVERITY` 的形狀沒說怎麼接
severity: minor
blocking: 否
引句:「`_DIR_SEVERITY` 對 `rules-unwired` 不限嚴重度」
佐證 ``configs/ast-grep/kotlin-android/check.py:27、664-665``
- 既有慣例:`_DIR_SEVERITY` 是「目錄對應嚴重度元組」,第 664 行用 `.get(dir, ())` 檢查。查不到的目錄預設是空元組,等於全拒。
- 計劃沒寫「不限」怎麼實作,有兩種做法。一種是補成 `("error","warning","info","hint")`,仍是同一張表,形狀一致。另一種是在檢查裡對 unwired 特判跳過,那就是第二種做法。計劃要寫明走前一種。
- 665 行的訊息「hint 放 rules-hints/、info 放 rules-review/」計劃已列要補。
- 慣例落差:計劃要求 `r.get("dir")`,但既有第 664、759 行都是 `r["dir"]`,等於同檔兩種取法。理由是測試假規則沒有 dir 鍵,可接受,但屬不一致。

## F4 做 5 改的 `_lint_wt_allow` 的家沒列進落點
severity: minor
blocking: 否
引句:「`scripts/lumos` 的 `_lint_wt_allow` 在既有「真實路徑在工具鏈 `configs/ast-grep/` 底下」之後再加一條」
佐證 ``docs/lumos-toolchain-knowledge/Systems/回合結束寫法檢查.md:19``
- 該節點的 RULE 寫「只准 lumos 寫死的 ast-grep 白名單形狀」,並綁 `t_lint_new_worktree_allowlist`、`[retire:when-gone:scripts/lumos::def _lint_wt_allow(]`。
- 該節點 `about_code` 只列兩支 hook 檔,不含 `scripts/lumos`。判定本體歸 `Systems/pitfalls-code-loop` 的新增告警閘。
- 計劃的 `lands_in` 只有 kotlin規則包與 linter精選目錄。做 6 的文字同步清單也沒寫要改 `回合結束寫法檢查` 的 RULE 或 `[test:]`:白名單變窄、S3 綁新測試 `t_lint_wt_allow_only_blocking_pack`,舊綁定與敘述都會偏。
- 這是我的判斷:改 `_lint_wt_allow` 該寫進它的家(回合結束寫法檢查或 pitfalls-code-loop),但沒列。

## 四問

**1. 分層與依賴方向**
結構對齊。`check.py` 加第四組 `CONFIGS`、`_DIR_SEVERITY` 改表,留在規則包自檢層(`check.py:25-27`)。白名單改動留在 `scripts/lumos` 的 `_lint_wt_allow`,沒有跨層直呼。唯一的新耦合是通用函式第一次寫死 `kotlin-android/sgconfig.yml`(F2 的 ⚠)。

**2. 命名與錯誤處理**
- `(problem_id, 原因句)` 二元組與 `(None, 原因)` 二元組的形狀都沿用既有。
- 缺口在 F2 的原因句格式與 F3 的 `r.get("dir")` 對 `r["dir"]`。

**3. 第二種做法**
- 目前沒有確定的第二種做法。
- 風險點是 F3 的「不限」若用特判而不是補元組,就會變成第二種。
- 另外 samefile 由拒絕改為放行(F1)只是語意反轉,不算第二種。

**4. 落點**
- `lands_in` 的 `Systems/kotlin規則包` 管 `check.py` 與 `sgconfig*.yml`,`Systems/linter精選目錄` 管範本,都已存在,對得上。
- `Systems/kotlin規則包` 的 `about_code` 沒列 `rules-unwired/` 與 `sgconfig-unwired.yml`,做 6 有寫補檔案節,但沒提補 `about_code`。
- `_lint_wt_allow` 的家沒列(F4)。

不對齊共 4 條
