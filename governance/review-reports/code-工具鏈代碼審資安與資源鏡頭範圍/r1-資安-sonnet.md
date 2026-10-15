severity: major

我讀了 patch 中 `scripts/lumos`、`templates.md` §7.8 和 Issues 檔的新增部分。範本填空沒有作者可控文字進派工詞,只有鏡頭範圍的誤判有洞。

**Finding 1:`lens_scope` 看的是帳本所在 repo,不是被審的 repo,會讓消費專案被少審**

severity: major
blocking: 是 — 一步就能走到的非刻意誤判(照平常的跨 repo 派工),後果是消費專案的資安席被靜默收窄成三類、少審 SQL 注入、權限、密鑰、加密;印出的那一行也沒有警語。
引句:「跨 repo 派工時這一行看的是帳本所在 repo,被審 repo 由編排者自己看(範本 §7.8 填空寫明)。」
- 誰:照平常操作的 AI 或使用者。
- 從哪:在工具鏈本 repo 開會談,審消費專案的分支。這個工作區就是這種配置(`lumos-toolchain/` 底下放著消費專案的 worktree)。
- 送什麼:`lumos loop next code-<編號>`。
- 拿到什麼:`_lens_root` 取自 `_vault_repo_root(env)`,也就是帳本所在 repo,不是被審 repo。於是輸出 `lens_scope: toolchain`,並印固定字串「鏡頭範圍: 工具鏈本 repo——派資安席時照…〈工具鏈三類〉、派併發與資源鏡頭時改資源、§3 第 1 點併發兩問不問(消費專案照舊)」。
- 後果:這一行是命令式語氣,「消費專案照舊」只是括號尾巴。照行動的編排者會對消費專案貼三類清單和「併發兩問不問」。
- 唯一的緩解是 §7.8 的一段散文,要求編排者自己去看被審 repo 的根。工具本身不防,而且 `loop next` 沒有被審 repo 的參數可用,範本還明講「不要為了這一行帶 `--repo`」。
- 實驗(`/tmp/lumos-seat-work/code-工具鏈代碼審資安與資源鏡頭範圍/資安-sonnet/c1` 是我造的臨時 repo,帳本和標記檔都在這裡面):
  - 有 `skills/lumos-project-notes/SKILL.md` 時,`python3.14 scripts/lumos loop next code-x --json` 得到 `gate-pending toolchain`。文字模式第 12 行印出「鏡頭範圍: 工具鏈本 repo——…」。
  - 拿掉標記檔後得到 `default`。
  - 把標記路徑換成同名目錄(不是檔案)也得到 `default`。
- 佐證:``file: `scripts/lumos:16430-16434` ``、``file: `scripts/lumos:25452-25459` ``、``file: `scripts/lumos:11229-11237` ``
- 修法方向:讓 `loop next` 讀被審 repo 的根來判別(例如從帳上記的審查材料或 diff 範圍推),推不出時不印這一行。或者那一行改成必須先確認被審 repo 才可套用的語氣。

**Finding 2:判別鍵是被審 repo 裡作者可造的檔案**

severity: minor
blocking: 否 — 判別鍵沿用既有慣例(`_self_repo_origin` 等),要在陌生 repo 放這個檔才觸發。但這次是第一次拿它來「縮小」審查範圍,方向跟過去相反,值得標。
引句:「根有 `skills/lumos-project-notes/SKILL.md` 就是工具鏈本 repo」
- 誰:陌生 repo 的作者,或一個 fork 了工具鏈的消費專案。
- 從哪:repo 根放一個空的 `skills/lumos-project-notes/SKILL.md`。
- 送什麼:使用者照平常對它跑 `loop next code-…`。
- 拿到什麼:`lens_scope` 變 `toolchain`,資安審被收窄成三類,併發兩問不問。上面實驗就是用空檔案(`touch`)重現的。
- 佐證:``file: `scripts/lumos:25458` ``

**Finding 3:範圍外手法紀錄把席報告文字寫進圖譜**

severity: minor
blocking: 否 — 範圍外且是刻意多步偽造的下游,依指示只提一句。
引句:「在下表追加一行:日期、迴圈與輪次、手法一句、被繞過的守衛」
- 「手法一句」由席報告(外部可控文字)轉寫,進到圖譜 Issue 筆記。後續會談讀到時,它是間接提示注入的載體,但範本沒有要求編排者轉述而不是照抄。
- 這篇筆記屬「只追加」,舊列不改不刪,所以注入文字一旦寫入就不會被清掉。

**已讀,無 finding**
- 新增的固定字串 `_LENS_SCOPE_TOOLCHAIN_LINE` 不含任何作者可控值。
- `lens_scope` 只會是 `toolchain` 或 `default`,不是自由文字。
- 例外時退回 `default`,方向是多審而不是少審,fail-open 方向正確。
- 範本的逐類清單、範圍外兩個填空是固定文字,沒有拼接作者可控內容。
- 刪檔紀律那句只是文字規則,沒有新的執行路徑。
- `anchor-baseline.json` 的改動只是重簽雜湊。

最高等級 major,blocking 1 條。
