# 計劃依據來源必填 — 設計審 r2 收貨(2026-11-06,四席:通才、可行性、依據、架構對齊,皆 sonnet)

## 收貨三道

- 正規化:四份已是正規化格式。
- quote-check:四份全數錨定(r2-snapshot.md)。
- refcheck:通才 12 ok + 1 行號超出 + 1 標將新增(兩者都是席位故意示範繞過手法的例子 `scripts/lumos:99999` 與「(新增)」,不是引錯);可行性 4、依據 11、架構對齊 21 全 ok。
- seat-check:這輪派工單頂層也列 materials,四席都標 unreported(報告沒寫出快照路徑);引句全錨進快照,判定有讀;只觀測不擋。

## 更正 r1-intake.md(那份已入帳,不改原檔)

r1-intake.md 重現表「依據-F10」那列寫 `scripts/templates/graph-discipline.md` 的家是 `Systems/lumos-cli-lifecycle`、`skills/lumos-design-loop/SKILL.md` 的家是 `Systems/convergence-evidence-gate`、`Systems/lumos-refcheck`——**這是錯的**。當時用 awk 比對到整篇筆記而不是 about_code 清單。r2 依據席 F4 指出後重驗:`lumos impact --file` 對這兩支檔都沒有「這支檔的家」段;`Systems/lumos-cli-lifecycle` 與 `Systems/convergence-evidence-gate` 的 about_code 都沒列它們(.md 不在每支檔有家要求的副檔名清單,不違反鐵則)。只有 `skills/lumos-code-loop/SKILL.md` 的家是 `Systems/每輪修補差異派工`,這點對。r1 依據-F10「家在診斷迴圈先行」那半條仍不成立(那篇也沒列)。

## 重現表

| 席-條 | 怎麼試 | 結果 |
|---|---|---|
| 可行性-F1 | 讀快照預期值表:「表頭寫成「機制|出處」兩欄」那列格內 `|` 沒跳脫成 `\|`;席位在複本跑 `spec-gate --no-run` 回 1、印 5 格 | HIT |
| 可行性-F2、依據-F1、通才-F2 | 讀 `_spec_gate_push_scan` 的 `_live`(doing 或範圍碰到的 done)與 `_spec_gate_push_candidates`(收連到被碰 Systems 的 doing);可行性席臨時 repo 實跑 todo 新計劃沒被查 | HIT |
| 通才-F1、可行性-F3 | 讀 `_refcheck_scan` 抽取:只收含 `/` 且首段是頂層目錄的反引號詞,點開頭目錄排除;狀態另有 planned、line_out_of_range;可行性席實跑 `CLAUDE.md`、`.github/workflows/x.yml` 回 [] | HIT |
| 依據-F3 | `Systems/kotlin規則包.md` WHY 行那句使用者原話記 2026-11-05;快照〈依據來源〉「網址只驗格式不連網」列寫 2026-11-06,且那句不支持不連網 | HIT |
| 依據-F2 | 對照〈用詞〉機制定義逐個找正文選擇:舊計劃只提醒、表頭固定、留帳帶 200 字、健檢不改退出碼、型錄前 20 個、只有網址也算未查證、不回頭改結案計劃等沒有列 | HIT |
| 依據-F4 | 見上節更正 | HIT |
| 依據-F7 | `lumos doctor` 已對紀律範本體積警告(席位附 `scripts/lumos:3790`) | HIT(讀碼) |
| 通才-F5、可行性-F7 | 可行性席實測 185 篇逐篇判新舊共 19.9 秒;通才席估 45–60 秒 | HIT |
| 可行性-F4 | 本分支 `check.py` 沒有 `dt_sources`,只在盲判那條分支 | HIT |
| 其餘 | 讀快照原文與席位附的 file:line | HIT |

## 先查世界

PRIOR-ART:推送前重查要挑哪些計劃——沿用本 repo 推送前規格閘「只對這次推送改到的東西負責」的既有原則(`_spec_gate_push_scan` 對預期值表只查 live 計劃,是為了不讓別人的計劃擋你;本案缺的是 todo),業界同類:pre-commit 框架只對這次暫存/改動到的檔跑 hook(https://pre-commit.com/ 原文:usually pre-commit will only run on the changed files during git hooks)。採用:只查這次範圍裡**檔案本身被改到**的計劃(不看狀態,不走連結候選);排除:沿用 `_live` 迴圈(漏 todo)、走 `_spec_gate_push_candidates`(會被別人的計劃擋)。
PRIOR-ART:路徑判存在——不用 `_refcheck_scan`(它是給「整段文字裡的引用」用的抽取器,有頂層目錄過濾與 planned 狀態);用它底下的 `_validate_repo_ref`(空值、絕對路徑、含 `..` 一律 missing,本 repo 已用在 [src:] 驗證,`scripts/lumos` 的 `_validate_repo_ref` docstring 寫明「直收已解析 path,無靜默過濾」),只認 status ok 且是檔案。
PRIOR-ART:健檢逐篇查 git 太慢——一次 `git log --diff-filter=A --name-only` 掃整個 Projects 目錄拿全部檔的首次加入日(git 官方 log 文件 `--diff-filter=A` 選加入的檔,https://git-scm.com/docs/git-log );採用批次一次,不逐篇呼叫。
PRIOR-ART:常駐範本體積——`Systems/lumos-cli-lifecycle` 既有 WHY:細節搬進 skill,範本只放表與一個例子;採用:範本只在既有 PRIOR-ART 那句尾巴加一個短子句,細節寫進 lumos-project-notes skill。

## 分組與去向(全數折入)

- 甲 推送前重查挑法與訊息:依據-F1、通才-F2、可行性-F2(major);通才-F3、可行性-F5、架構對齊-F1(minor)→ 只查範圍內檔案本身被改到、而且是〈用詞〉定義的計劃(Projects 底下 `_計劃.md`、type project)的新計劃,不看狀態;另一個標籤與標題分支;推送前擋下也寫 `sources-missing`(額外欄位 stage=push);推送前掛鉤 rc1 那句固定文案改成「看上面列的原因」不再只講條款測試。
- 乙 路徑判存在:通才-F1、可行性-F3(major);架構對齊-F3(minor)→ 抽反引號詞、去掉 `:行號`、用 `_validate_repo_ref` 判,只認 ok 而且是檔案;根目錄檔與點開頭目錄照收;「(新增)」不算;節點連結用 `_SINGLE_WIKILINK_RE` 同一個正規式抽、用圖譜節點索引判存在;共用函式命名 `_plan_source_cell_ok`。
- 丙 本計劃自己的表:可行性-F1、依據-F2、依據-F3(major)→ 跳脫 `|`;補漏列的機制;改掉不支持的出處與錯日期。
- 丁 表格細節:通才-F4、可行性-F6(minor)→ 三格都要有實字;分隔列照預期值表既有處理;使用者原話接受半形或全形冒號、也接受沒冒號直接接引號;引號收「」與 ""。
- 戊 健檢效能:通才-F5、可行性-F7(minor)→ 一次 git log 批次拿首次加入日;`created` 已不早於生效日就直接判新不查 git。
- 己 低風險計劃沒人接「支持與否」:通才-F6(minor)→ 寫進天花板,附 REVISIT 抽查低風險新計劃的〈依據來源〉。
- 庚 三處分工、家、範本體積:依據-F4、F5、F7(minor)→ 分工改寫(PRIOR-ART 照原意「動筆前先問世界」;設計審手冊的「或計劃的審計修正紀錄」也算過程紀錄;沒有計劃筆記的代碼審不適用);lands_in 拿掉 convergence-evidence-gate、改列 Systems/design-loop,寫明 lumos-cli-lifecycle 只管注入、範本改動不碰 sentinel 不變式;範本只加短子句、細節進 skill。
- 辛 出處說法精度:依據-F6(minor)→ Nygard 原文是「一份 ADR 描述一個重大決策」改引 Nygard;拿掉「列為必填」;Wikipedia 改成「要求來源明確支持;機器只判有沒有出處」。
- 壬 dt_sources 不在本分支、型錄主程式兩條路徑:可行性-F4、架構對齊-F2(minor)→ 實作前等盲判那條與 android-lint-ci 兩條都合進主線;計數行在 `--catalog-only` 與完整兩條路徑都印。
