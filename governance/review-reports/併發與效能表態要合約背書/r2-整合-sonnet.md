severity: major

既有讀者逐一判定:治理帳 mapper 整包傳遞 dispositions(`scripts/lumos:7278`),無;`_codeloop_read_dispositions` 治理帳備援整包取出(`scripts/lumos:37098`),CI 讀得到,無;`_codeloop_record_valid` 只看 head_sha(`scripts/lumos:37134`),無;`_dispositions_validate` 不做欄位白名單(`scripts/lumos:36970`),無;--carry 會帶舊 backing(`scripts/lumos:37393`),寫入時丟掉重算銜接得上;gov --stats 表態段見 G3;gov 第 5 源讀 kill-log(`scripts/lumos:7291`)多三欄不壞,commit 語意改變見 G5;配方存在 frontmatter kill_recipes 單行 JSON;`_kill_read_recipes`(`scripts/lumos:12789`)只讀不驗鍵,多 covers 不壞;guard list、guard trace(`scripts/lumos:11615`、`scripts/lumos:13316`)不讀配方內容。

**G1 配方分組鍵少了配方身分**
severity: major
blocking: 是——會把有配方 survived 的情況判成 strong。
kill-add 去重鍵是 invariant、file、old;kill-log 不含 old 或配方編號,同組兩條配方 A survived、B killed 判 strong;invariant 欄存使用者敲的子字串,不同片段會把同一配方拆兩組;S7 沒測同組兩條配方。
引句:「配方=同一 node、同一 invariant、同一 file」
file: `scripts/lumos:12850`
file: `scripts/lumos:13209`

**G2 教學流程漏了「先提交再跑 kill」**
severity: major
blocking: 是——照文件走完可能是 none 或表態失效,沒有任何一步提醒。
cmd_guard_kill 以 HEAD 為基準、提示配方/測試需先 commit;kill-add 改的節點筆記不是簿記檔,kill 後表態再提交筆記會讓表態失效;同步清單與補救指令都沒寫提交順序。
引句:「寫次數或併發測試 → `guard kill-add --covers <題目id>` → `guard kill` → 重表態」
file: `scripts/lumos:21527`
file: `scripts/lumos:37134`

**G3 gov --stats 的有背書/沒有背書會被舊事件與 off 模式灌水**
severity: major
blocking: 是——撤除判準的量法實作後就不準。
沒定義分母;舊事件、off 模式、換機器重表態都被算成沒有背書;同 sha 重表態重複計數;REVISIT 的背書比例被灌水。
引句:「本案在該段多印「有背書/沒有背書」兩個數」
file: `scripts/lumos:7054`

**G4 強證據=killed 與破壞測試自己標的弱證據不一致**
severity: major
blocking: 是——會把工具自己標為弱的紀錄當強。
run_cmd 沒有 {method} 時整套跑,detail 標弱證據但 verdict 仍 killed;maestro/playwright 有 flaky_risk 仍 killed;寫 kill-log 丟掉 detail;spec 沒補 whole_suite 標記也沒說 flaky_risk 要不要降級。
引句:「也就是綁定測試紅了、而且紅的就是那支測試」
file: `scripts/lumos:13176`
file: `scripts/lumos:13209`

**G5 每筆記自己平台 HEAD 會改變 gov 第 5 源的去重**
severity: minor
blocking: 否——只影響 gov 計數。
去重鍵含 commit(`scripts/lumos:7326`),token 是 invariant+ts(`scripts/lumos:7293`);改後多平台列不再折疊。
引句:「`lumos gov` 讀 kill-log 只取既有欄位,多出來的欄位不影響。」
file: `scripts/lumos:7291`

**G6 派工鏡頭表頭文字會說錯,註記位置要在截斷之後**
severity: minor
blocking: 否——措辭與細節。
表頭「寫入時工具只驗了形狀…答案對不對沒人驗」(`scripts/lumos:34826`)上線後是舊說法且沒列進同步清單;每行 str(tail)[:200];快取鍵那段 spec 說對了(`scripts/lumos:35777`)。
引句:「每筆被標題目的 satisfied 行尾多印「背書:強證據(配方:<note 前 40 字>)」」
file: `scripts/lumos:34822`

**G7 同步清單不齊,引用原句對不上**
severity: minor
blocking: 否——文件精度問題。
那句原文找不到,實際是 reference.md:199 與 :569、SKILL.md:24 的近似句;S17 說六處實際七處;漏列 Systems/效能檢核目錄(消費專案設定)、commands/INDEX.md、kill-add 的 argparse help;slim/ 已凍結不用改。
引句:「`skills/lumos-code-loop/reference.md` 兩處「工具只驗證據存在,不驗答案對不對」」
file: `skills/lumos-code-loop/reference.md:199`
file: `skills/lumos-code-loop/reference.md:569`
file: `docs/lumos-toolchain-knowledge/Systems/效能檢核目錄.md:79`

**G8 off 模式沒說要不要清掉手填 backing;設定函式提前返回路徑**
severity: minor
blocking: 否。
off 下手填 strong 會留在記錄;`_stack_questions_config` 有多個提前 return,預設值要放進初始 dict。
引句:「樣板裡若已帶 `backing`,一律丟掉重算,不信任手填或 `--carry` 帶過來的值」
file: `scripts/lumos:21417`

**G9 --covers 對既有配方沒有補宣告的路,也沒驗 id;kill-log 在消費專案被忽略**
severity: minor
blocking: 否。
kill-add 同鍵直接擋;沒驗 id;換機器、新 worktree、新 clone 重表態一律 none;天花板沒講 kill 在別的分支或提交上跑;配對不看 commit 是否為被推版本祖先。本 repo kill-log 被追蹤,沒這問題。
引句:「`--covers` 是寫配方的人自己宣告的,工具不判那條壞法跟題目真的有關」
file: `scripts/lumos:12850`
file: `scripts/lumos:18250`

**G10 REVISIT 日期寫死成今天加 8 週**
severity: minor
blocking: 否。
實作另日上線,doctor 到期會叫人驗還沒跑滿 8 週的東西。
引句:「REVISIT:2026-11-26 上線第 8 週」

其餘:緣起、題目、推送前檢查(warnings 由 check 印成提醒、pre-push 過濾看得到,`scripts/lumos:37874`、`scripts/hooks/pre-push:449`)、過期、合約候選、回退:已讀,無 finding。實務隱患:併發、效能、資源、輸出純度無;相容見 G3、G5、G8。

最嚴重 severity: major,blocking 共 4 條(G1、G2、G3、G4)。
