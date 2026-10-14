severity: minor

我沒找到會讓功能做錯事的 bug。以下三條都是邊界上的小問題,後兩條只是測試沒守到某些邊界。

做法:我用臨時夾具對 `loop next ... --json` 跑了 9 個編號乘 7 種 `--repo`,另加三種有無 `.git` 的帳本位置與三種 `--repo` 寫法。夾具已用字面絕對路徑刪掉。

**實測結果(`lens_scope` 值)**

| 輸入 | 結果 |
|---|---|
| `code-x` + 含 SKILL.md 的目錄 | toolchain |
| `code-x` + 符號連結指到該目錄 | toolchain |
| `code-x` + SKILL.md 是空檔 | toolchain |
| `code-x` + SKILL.md 是目錄 | default |
| `code-x` + SKILL.md 是壞掉的符號連結 | default |
| `code-x` + 不存在的路徑 | default,rc 正常,無 traceback |
| `code`、`CODE-x`、`codeX`、`dz-1`、前導空白的 ` code-x` | 全部 default |
| `code-`(後面空)、`code-　x`(全形空白)、`code- x`(半形空白) | toolchain |

**finding 1**
severity: minor
blocking: 否 — 失敗方向是多審不是少審,不會漏掉資安席,只是派工詞退回消費專案六類。
引句:「跨 repo 派工時這一行看的是帳本所在 repo,被審 repo 由編排者自己看(範本 §7.8 填空寫明)。」
問題:判斷工具鏈本 repo 只看一個根目錄上有沒有 `skills/lumos-project-notes/SKILL.md`,不會往上找。帳本根目錄的算法是往上找 `.git`,找不到就退回 vault 的上一層(`docs/`)。
具體失敗情境:
- 輸入一:`docs/x-knowledge` 帳本,`skills/lumos-project-notes/SKILL.md` 在同一個專案根,但專案根沒有 `.git`(例如解壓出來的副本)。跑 `loop next code-z --tier high --json` 得到 `lens_scope=default`,不印「鏡頭範圍」。
- 輸入二:`--repo` 給工具鏈 repo 的子目錄(例如 `<toolchain>/skills/`)。結果也是 `default`,不會往上找到根。
- 輸入三:`--repo .` 且 cwd 不在 repo 內。結果是 `default`,同一條指令換個 cwd 結果就不同。
- 輸出:編排者貼六類而不是三類。
- 這是該 repo 既有的慣例,但文件只寫了「跨 repo 派工」的錯位,沒寫「無 `.git`」和「子目錄」這兩種。
佐證:``file: `scripts/lumos:11229-11237` `` 是 `_vault_repo_root`,``file: `scripts/lumos:25452-25460` `` 是 `_is_toolchain_repo`。

**finding 2**
severity: minor
blocking: 否 — 只影響編號的邊界,不影響任何現有的正常編號。
引句:「def t_loop_next_lens_scope_design_untouched():」
問題:測試只用了 `dz-lens` 和 `codelens9` 兩個反例。`code-`(後面空)、`code- x`、`code-　x`(全形空白)現在都被當成 code 審,印出鏡頭範圍。這和 `startswith("code-")` 的既有寫法一致,但測試沒釘,將來有人收緊編號格式,這條測試照綠。
具體失敗情境:跑 `loop next "code-" --tier high --orchestrator <編排者> --repo <含 SKILL.md 的目錄> --json`,得到 `lens_scope=toolchain`,而且測試不會紅。
佐證:``file: `scripts/lumos:16431` ``。

**finding 3**
severity: minor
blocking: 否 — 測試涵蓋面的缺口,不會讓錯誤的行為放行。
引句:「def _mk_lens_dirs():」
問題:夾具只造了「有 SKILL.md」和「沒有任何東西」兩種目錄。SKILL.md 是目錄、壞掉的符號連結、`--repo` 指到不存在的路徑,都沒測。實測這三種都落在 default,行為合理,但測試沒守。
具體失敗情境:若有人把判別從 `is_file()` 改成 `exists()`,SKILL.md 是目錄時就會誤判成 toolchain,現有 8 支新測試全綠。

**已讀,無 finding**
- 編號邊界:`CODE-x`、`code`、`codeX`、前導空白都落到 default。`code` 沒連字號走設計審的規則沒被破壞。
- `lens_scope` 常駐輸出:rc2 之前的早退路徑不印 JSON 屬既有行為;`out.update(extra)` 不會蓋掉這個欄位。
- fail-open 的 try 範圍涵蓋 `Path(repo).resolve()` 和 `_vault_repo_root`,`_is_toolchain_repo` 自己再吞例外。
- 範本切段測試:`Path.read_text` 會把 CRLF 轉成 `\n`,所以 CRLF 不影響;圍欄標記加長到四個反引號,`count("```\nLUMOS-SEAT:")` 和切段仍然成立;`###` 改成 `####` 時,三個 `\n### ` 小節的存在檢查(⑧)會紅。
- `### ` 小節順序變動:`_sub_block` 切到下一個 `\n### `,順序對換不影響結果。
- 刪檔紀律測試:`templates.md` 第 31、81、146、266、289、327、348、423 行實際都有規則原文;`seat_n==6` 的前置和兩個變異都能咬到。§7.9 通才席沿用 §3 整份,§9 不是席位派工,兩者不漏。

最高等級 minor,blocking 0 條。
