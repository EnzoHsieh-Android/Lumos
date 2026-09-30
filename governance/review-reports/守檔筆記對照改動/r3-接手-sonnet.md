severity: major

## F1 上線公告「CHANGELOG 一條」跟 CHANGELOG 的版本規矩衝突,接手者照字面做會踩守衛或擅自發版
severity: major
blocking: 是
引句:「**上線公告**:CHANGELOG 一條(寫明 codex 編排時準度沒量過、判定者是 sonnet),並用跨會談訊息請 rtb 會談 `lumos update` 拿新掛鉤與範本、兩週後回報紀錄檔。」
file: `scripts/../CHANGELOG.md:1-8`(repo 根的 CHANGELOG.md 開頭規矩;版本常數在 `scripts/lumos:270` LUMOS_VERSION = "v1.1")
1. CHANGELOG.md 開頭明寫:只記「對外放出去的版本」,標題必須是 `## vMAJOR.MINOR — YYYY-MM-DD`,「還沒發版的變更……不進這份」、刻意不留「未發布」區塊,否則守衛每次推送都紅;第一筆要跟 `LUMOS_VERSION` 一致(RELEASING.md 第 1 步)。
2. spec 只說「CHANGELOG 一條」,沒說要不要升 `LUMOS_VERSION`、標題寫哪個版號、是否走 RELEASING.md 的 release 快轉。沒脈絡的下一個會談只有三條路:(a) 加「未發布」區塊,違反該檔規矩、守衛紅;(b) 只加新版本標題不升版常數,兩邊不一致守衛紅;(c) 自己升 v1.2 並進發版流程,但發版是「不可逆、要人在場」的維護者步驟,spec 沒授權。
3. 連帶:消費專案(rtb)只在 `lumos update` 拿到 release 線上的東西,而 spec 的 REVISIT 2026-10-21 / 12-02「上線日」與「請 rtb `lumos update`」都沒說上線日是推 main 那天還是 release 快轉那天;兩週量準度的起算與 rtb 能不能拿到新掛鉤取決於此,照字面會在 rtb 還拿不到新掛鉤時就開始算兩週。
4. 該補的是一句:要升版就寫「升到 vX.Y、照 RELEASING.md,上線日=release 快轉那天」,或者改成「公告寫在 Projects 筆記與跨會談訊息,CHANGELOG 等下次發版再帶」。

## F2 S10 每個提交當一個範圍,沒寫範圍的拼法
severity: minor
blocking: 否
引句:「(`governance/eval/home-check/validate/selection.json`,每個提交當一個範圍)」
file: `governance/eval/home-check/validate/selection.json:1-30`
1. selection.json 只有提交編號(`picked[].commit`),reread-prepare 的 `--diff` 要 `<起點>..<終點>`。接手者得自己猜成 `<c>^..<c>`。我對 15 個 rtb 提交實測過這種拼法:用產品的家定義(Systems、doing/done/stale)加「筆記被同提交改過」的篩選,實驗二 17 行真漂移全落在會成為候選的筆記上(只有 1 行邊界的筆記沒被同提交改過),所以 14 行門檻可達,不是 blocking。
2. 「12 到 13 行重跑一次取兩次平均再判」也沒寫平均後跟哪個數比(應是 14);放行理由:接手者合理推得出,只是不精確。

已讀其餘各節(做法 0–6、條款、回退、實務隱患、誠實界線、附錄),無其他 finding。已核對:掛鉤標記字串 `# lumos note-audit reread-check` 不含 `note-audit check`、`_nodehome_clamp_base` 對 rtb 歷史提交(無上線標記)不截斷、`_KNOWN_GATES` 需登記 `note-reread`(spec 已寫)、`_nodehome_name_status(norm=False)` 與 `_nodehome_homes` 簽名跟 spec 用法一致。

最高等級:major;blocking 共 1 條
