severity: clean

已看 r3-code.patch 全文(724 行)和 r3-snapshot.patch 的檔名清單,另對照 repo 裡 `_lumos_config_at_ref` 與 `_arch_target_rule_index` 的現行實作。三類逐項結論如下。

**① 提示注入:已看,無。**
- 舊檔清單 `.lumos/arch-legacy.json` 是被審 repo 寫的檔,但它的內容只被讀成 NFC 路徑集合,當查表用。
- 清單內容不會原文進派工詞。
- `_arch_legacy_apply` 只是把改動檔從 `targets` 扣掉或放回。進派工詞的檔名仍走既有的 `_arch_target_text`,也就是名字出口、`_frame_injected` 加框和控制字元過濾。這條路徑本次沒動。
- doctor 與 code-loop check 新增的行,只印數字和寫死的常數 `_ARCH_LEGACY_REL`,沒有插入清單裡的字串。
- 計劃檔 `Android目標架構開關與舊檔畢業_計劃.md` 與 `arch-alignment-lens.md` 是給人讀的圖譜筆記。
- `templates.md` 只多一句靜態說明,沒有帶值。

**② 讀寫與執行越界:已看,無。**
- 清單只經 `_json_at_ref`,也就是 `git show <ref>:.lumos/arch-legacy.json` 讀取,走的是 git 物件,不是工作目錄的檔。所以不會跟著符號連結去讀 repo 外的檔。
- 本次沒有寫檔、shell 插值或 `subprocess` 拼接。
- 清單路徑不會被當作檔案路徑去 open,只做字串比對。
- 沒有新增密鑰、信箱,也沒有改動安裝腳本或下載網址。
- 卷證和帳本檔(`r*-snapshot.patch`、`r*-*.md`、`r*-dispatch.json`、`r2-repair-binding.json`、`verdict.json`、`.governance-log.jsonl`、`.canary-log.jsonl`)只靠檔名清單與性質判斷。它們是既有的審查歸檔慣例,沒有被本次 diff 新增的程式讀進派工詞或執行。測試會呼叫 `run(...)` 子程序,但命令都是寫死的 `code-loop`、`doctor` 等,參數只有測試自己造的 repo 路徑與分支名。

**③ 非刻意、一步就能繞過的守衛:已看,無。**
- 以下四種失敗方向都是多審,不是漏審:
  - 起點版清單不存在,視同空清單。
  - 起點版清單讀不懂,視同空清單。
  - 頂端版清單讀不懂,不畢業。
  - git 失敗,走既有的失敗說明。
- 分支自己在頂端版加行,審查不認(照讀起點版),code-loop check 另印「多了 N 行」提示。這不是意外走過的守衛。要靠它讓架構測試跳過檔案,得刻意編輯清單,屬範圍外的刻意偽造。
- 畢業只在「宣告完全相同、頂端清單讀得懂」時才放寬,而且放寬的方向是審得更嚴。
- NFC 與 NFD 檔名、中文檔名,以及清單混入非字串元素,都有 `t_arch_target_graduate_same_branch` 的 J、H、H2 情境蓋住。
- 本次沒有新增 `LUMOS_SKIP_*` 或 `PYTHONPATH` 類的環境入口。
- 設計審路徑讀 `HEAD` 版清單,與它原本讀 `HEAD` 版宣告的信任模型一致,沒有新增洞。

**順手提一句(範圍外,不計入)。** 計劃筆記「守衛面」一節已承認:Konsist 架構測試讀工作目錄那一版清單,分支往清單加行,可以讓測試跳過那支檔。這是刻意操作,而且 `REVISIT:2027-04-30` 已排了評估,不另報。

最嚴重等級為 clean,blocking 共 0 條
