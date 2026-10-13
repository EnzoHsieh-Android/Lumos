severity: minor

規格〈做法〉〈驗收條款 S1–S8〉〈兩階段上線〉〈量測與留痕〉〈同步改的地方·第一階段〉逐條對過,實作都照字面做到,只有下面三處落差,都是 minor。我讀了現行 repo(HEAD 9ef31b97,與 patch 一致)的 `scripts/lumos`,並實際跑過程式。

**核對結果(符合的部分)**
- **抽取規則**:預先配對、標籤、unclosed(`quote` 取開引號後到行尾且最多 200 字)、被補閉合只成一條、尾段各條自己數(`stray`)、只有格式不合的列截 200 字,都和規格一致。
- **舊判準**:`_quote_rows_legacy` 函式本體與改名前的 `_quote_rows` 逐字相同(我用 diff 對 cb832b56 的原文,結果相同)。
- **章與常數**:
  - `rule` 是只收關鍵字的必填參數,其他值丟 `ValueError`。
  - `_QUOTE_WRITE_RULE` 是 `"legacy"`,寫側通過才蓋章,被擋不寫帳。
  - 讀章用 `_quote_rule_of`,缺鍵走 legacy,值不認得時印規格指定的訊息。
- **處置閘**:
  - 印「引句判準:<版本>」;沒章時印「legacy(帳上無章)」。
  - 判準丟例外印「引句判準 <版本> 丟例外:<型別>:<前 120 字>」。
  - `MemoryError` 照常往外丟。
  - 診斷指令帶 shell 引號,零引句、讀檔失敗、丟例外、錨不到都印,章不認得不印。
  - 「(其中 N 條格式不合)」在。
- **擋下事件 note**:欄位順序和規格逐字一致(`quote-rule:… kind= cats= report= report_sha= loop= auditor= id= quote=`),`quote=` 排最後,濾控制與格式字元,前 60 字。
- **`gov --stats`**:四格互斥,逐字是「記帳被寫側擋下 N 次(報告沒正規化 a / 缺 refuted-set b / findings 多於 reported c / 引句判準 d)」。
- **比較模式**:
  - 實跑了小型假帳本:五行交叉表與略過行逐字相符,清單格式符合,同一組只算一次,路徑指到 `/etc/passwd` 算讀不到,壞行計 2 列。
  - 帶報告、`--spec` 或 `--rule` 時 rc2,帳本不存在時 rc2,缺報告或 `--spec` 時手動擋下 rc2。
  - 在 repo 上實跑:23 秒內跑完,結果 2631 / 361 / 22 / 43 / 236,略過 19 組、1 組、0 列。
  - 計劃寫的「2627 / 359 / 21 / 43 / 235」是當時的量測。我重跑的數字多了幾組,因為帳本後來又加了 r1 席報告,不算不符。
- **其他**:`quote-check` 的 `--rule` 用 argparse choices,人讀輸出第一行印判準,`--json` 帶 `rule`;`seat-check` 用常數;兩個測試替身已改成收 `**kw`。八支 `t_quote_full_span_*` 都存在,`-k quote_full_span` 79 條通過。
- **第一階段的文字範圍**:Issue 兩篇、兩處手冊改動、`loop-convergence-recording` 新節都在;`templates.md` 的引句判準行沒動,符合規格。

**findings**

1. 寫側擋下事件的 `cats` 把舊判準的引號沒閉合歸成 `miss`
severity: minor
blocking: 否
引句:「cats = sorted({x.get("kind") or ("short" if x.get("too_short") else "miss") for x in rows if not x["ok"]})」
file: `scripts/lumos:25833`
- 規格把 `cats` 的值域寫成 unclosed、stray、miss、short、none。
- 第一階段寫側用的是 legacy。舊判準遇到「引句:」標籤數大於抽到的條數時,會補一列 `malformed: True`、沒有 `kind` 的列。
- 這種列在事件裡變成 `cats=miss`,其實語意是 unclosed。
- 目前唯一會真的寫事件的就是 legacy,所以第一階段的事件在這一類上會被誤歸。規格沒說 legacy 的 malformed 列該怎麼分,屬規格沒寫。

2. 計劃第二條 REVISIT 的指令讀不到 `quote=` 片段
severity: minor
blocking: 否
引句:「lumos gov --since 60 --full | grep 'quote-rule:' | grep 'kind=new-only'」
file: `docs/lumos-toolchain-knowledge/Projects/引句錨定整段比對_計劃.md`(patch 第 126 行)
- `gov --full` 每筆事件只印 `detail[:50]`(`scripts/lumos:9856`)。
- `quote-rule:full-span-v1 kind=new-only` 只有 37 字,所以 grep 能命中,也能列出事件。
- 但 `quote=` 排在 note 最後,前 50 字內看不到。計劃說「逐筆讀 note 裡的 `quote=` 片段」,走這條指令做不到,要改去讀 `docs/.governance-log.jsonl` 原檔。
- 這是規格內部的不一致。帳上資料是完整的,只是展示被截短,所以只算 minor。

3. 人讀的 `quote-check` 輸出看不出格式不合與 kind,比較模式的 `--json` 被靜默忽略
severity: minor
blocking: 否
引句:「print(f"  {mark} #{i} 「{r['quote'][:60]}」{short}")」
file: `scripts/lumos:26799`
- 我實跑 `quote-check r/a.md --spec r/snap.md --rule full-span-v1`,stray 那條只顯示「✗ #1 「合法前綴文字至少十個字」」。看不出是格式不合,也看不出 kind,只能看到被截短的前綴,容易被誤讀成單純錨不到。
- 規格沒要求人讀輸出顯示 `kind`,屬程式做了或沒做、規格都沒寫。
- 比較模式帶 `--json` 時既不報錯也不生效。規格寫「不另設 `--json`」,沒說帶了要擋。
- 兩點都不影響閘的判定。

**順帶說明,不算 finding**
- `quote=` 片段以 `-` 作空值標記,規格沒寫。
- 規格要求手冊「凍結入口同族一次掃完」,patch 實際寫的是「…同族一次掃完再報」,用字略有不同,語意相同。

總結:最高等級 minor,blocking 共 0 條
