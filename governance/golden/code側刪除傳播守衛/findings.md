# golden findings — code側刪除傳播守衛（design-loop 收斂留痕，2026-08-10）

處置閘 r1/r2 雙 PASS；六席 canary 全 caught（r1: c/b/incident-inv，r2: b/a/c；probe 兩次 recraft 皆一次過）。辯方路由：全部走「多席一致」或「機械證實（編排者自核 file:line）」，零開庭。**全數折入、零「接受不修」**——故無 accept-reason 條目。r2 為單家族輪（Codex 401 缺席退 opus，偏離記 r2-dispatch-s3.json）。

## r1（去重 13＋措辭 2，全折）

| id | finding | 折法 |
|---|---|---|
| d1 | S2 欄位白名單手列漏 plan_refs/aliases/pitfall_when（三席一致） | 先改讀 LIST_KEYS（r2 再改判，見 e3） |
| d2 | alternation 未 re.escape（兩席） | 補（r2 再補全，見 e5） |
| d3 | 「--no-verify 無留痕」與 post-commit bypass 帳（.bypass-log.jsonl）不符 | 訂正為沿用既有機制 |
| d4 | -M 治不了符號改名，測試列偷換概念（兩席） | rename 拆兩型；符號改名明文 v1 不解、不寫假測試 |
| d5 | 「全域消失」快照未定義＋整庫掃描成本漏算（兩席兩面） | 定 staged index（git grep --cached）＋成本入預算 |
| d6 | CJK quotePath／輸入健壯性風險類缺（兩席） | 全 diff 呼叫帶 quotePath=off；python3 主體；風險類補列 |
| d7 | 誤報來源「註解提及／同名符號」零覆蓋 | 明文 v1 不判＝取捨非遺漏 |
| d8 | 落點兩候選輸入不等價（Codex 獨有） | 裁定 Gate CC 旁（ADR d1） |
| d9 | 兩識別字被當可互換搜尋鍵（Codex 獨有） | 案例句精度訂正（不做 call graph） |
| d10 | 歷史段落「標」無機械形式 | 字樣判定撤案（r2 演進為型別排序，見 e1） |
| d11 | S3 lumos search 與 S1 grep 搜尋域不一致（Codex 獨有） | S3 問句改 --code＋註明 superseded 差異 |
| d12 | `\|\| true` 兜不住 hang（Codex 獨有） | python 內建 deadline 契約 |
| d13 | cap／輸出上限無值、超限清零證據（Codex 獨有） | 先驗 40／top-10、超限保留高信心 |
| w1 | 天花板承接者併寫 | 分寫 |
| w2 | Swimm 三級對應措辭過度 | 降為概念級 |

## r2（去重 11＋釐清 1，全折）

| id | finding | 折法 |
|---|---|---|
| e1 | 型別過濾證據屬存量方向，外推 S1 不成立；會壓掉自己的最壞案例（opus＋s1 兩席） | S1 只排序不壓低、全五型別都報；型別當主濾網留存量工具 |
| e2 | 兩信心訊號合成未定義、三處措辭行為分歧（兩席） | 檔位＝符號單一維度；統一「排序壓後」，無「不報」 |
| e3 | LIST_KEYS 是 append 白名單非連結語意；pitfall_when=content-trigger（兩席） | 撤整包，明確子集 LINK_KEYS＋斷言守衛 |
| e4 | should_exclude 不可重用＋第三份清單未接漂移守衛＋源 repo 反轉（兩席） | 對齊不重用；擴 t_precommit_whitelist_drift_guard；語意照抄 |
| e5 | alternation 漏 \b＋re.ASCII（引用處的存在理由） | 完整借 :7189 三件套；測試補詞界／CJK 兩列 |
| e6 | staged 掃 40 次子行程 vs 單掃紀律矛盾 | 單次 git grep 多 -e；benchmark 一併計時 |
| e7 | 存量掃描宣告交付但零落地面；判定強度＞字面 grep | 劃出 v1、另案交付 |
| e8 | 3% 是存量方向數字，frontmatter/DECISION 未限定 | 方向限定；不可挪用為增量誤報率 |
| e9 | 照抄 Gate CC 的 2>/dev/null 會吞降級訊息 | 明定走 stdout＋測試斷言輸出流 |
| e10 | d1「落點裁定」涵蓋不到 S3 | content 限定僅及 S1/S2 |
| e11 | summary 天花板句殘留 r1 被推翻的併寫（折入漏鏡像） | 補鏡像 |
| c1 | 兩個「6」／「4」集合關係未交代 | NEEDS CLARIFICATION → Enzo 補：零重疊、a55030e→4ce602d 時序；併折出「死碼盲區」能力邊界表＋v2 候選（呼叫點判定） |
