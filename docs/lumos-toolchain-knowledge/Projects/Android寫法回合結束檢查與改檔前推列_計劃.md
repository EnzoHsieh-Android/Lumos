---
type: project
status: todo
created: 2026-11-06
updated: 2026-11-06
tags:
  - type/project
  - status/todo
  - scope/stack-knowledge
related:
  - "[[Projects/Android寫法寫完當下自動檢查_計劃]]"
  - "[[Projects/Android協程與API寫法機械檢查標準_計劃]]"
  - "[[Projects/Android寫法語意情境表態與盲判_計劃]]"
  - "[[Systems/graph-sync-coverage]]"
  - "[[Systems/改檔前推播]]"
  - "[[Systems/hook逾時預算]]"
lands_in:
  - Systems/graph-sync-coverage
  - Systems/改檔前推播
  - Systems/hook逾時預算
  - Systems/棧別提問表態閘
---
# Android寫法回合結束檢查與改檔前推列_計劃

> 白話:[[Projects/Android寫法寫完當下自動檢查_計劃]] 第二輪設計審後(2026-11-06)拆出來的兩個機制:①AI 每回合收工時,自動對這一回合改過、還沒提交的檔跑規則包(工作樹檢查),有新增告警就擋下叫它先修;②AI 要改 kt 檔時,把型錄〈情境決策表〉相關的一到三列推到眼前。母計劃只留「代碼審記通過前先跑機械檢查」。這兩個機制兩輪設計審累計折了 60 多條,問題集中在回合邊界怎麼算、自動執行命令的白名單、鉤子與 lumos 之間的介面、跟既有做法重複;照設計審熔斷提示(累計折入超過 20 條就拆小)先拆出來,下次動筆前先處理下面〈待解問題〉。

## 起稿依據

下次動筆從卷證 `governance/review-reports/android寫法寫完當下自動檢查/r2-snapshot.md` 的〈用詞〉(工作樹檢查、回合時間戳、這一回合碰過的檔、自動執行白名單)、範圍 2(工作樹檢查)、範圍 3(回合結束自動檢查)、範圍 4(改檔前推相關列)起稿;那份第二輪的四份席報告(同目錄 `r2-*-sonnet.md`)是下面每組問題的原文。

## 待解問題(第二輪設計審四席,依根因分組)

1. **自動執行白名單繞得過、正例自相矛盾**(通才 F1、F2,邊界 F3,資源 F3):`--config` 值只比字串前綴、沒有正規化 `..` 與符號連結;「開頭的 `$HOME`」跟範本把 `$HOME` 放在 `--config` 值裡對不上;S3 正例 `--config x.yml` 違反自己的規則;「工具鏈安裝目錄」有 `LUMOS_HOME`、`~/harness/lumos-toolchain`、`lumos` 所在目錄三個來源沒指定。
2. **回合邊界算法有洞**(通才 F3、F5,邊界 F1、F2,資源 F1、F9):第一次收工不查讓單回合會談(`claude -p`、無人看顧的自動流程)永遠不被查,S7 照字面跑不過;`stop_hook_active` 那次也推進時間戳,續做改的檔永遠不再被查,跟範圍 3 的宣稱相反;rc3 或被殺時時間戳已推進、那批永久漏掉。候選方向:在既有 SessionStart 鉤子記回合起點(邊界 F1 指出已有註冊),`stop_hook_active` 那次不推進。
3. **鉤子與 `lint-new` 之間沒有機讀介面**(通才 F4,邊界 F5):批次雜湊要全部指紋,人讀輸出只印 20 條;rc1 同時是擋與未捕捉例外,崩潰時會空原因擋人。對照:推送前掛鉤用 `LUMOS-BLOCKS:` 機讀行。
4. **擋停名額先佔、輸出延後會永久遺失**(資源 F2):既有那道在判完之後還有多處不輸出的提早返回、例外與外層逾時。
5. **時間預算算式漏項**(通才 F6,資源 F5):沒算 SIGKILL 寬限與逐字稿讀取,既有那道可能拿不到 25 秒。
6. **git 呼叫細節**(邊界 F4、F6、F7,通才 F7、F8,資源 F4、F10,架構 F6):`git diff --quiet HEAD` 實測會改寫索引(`diff-index` 不會);未追蹤的 `.lumos/config.json` 判成沒修改;`--no-optional-locks` 與 v1 `-z` 解析是新寫、不是沿用 `_handoff_files`;`R` 在第二格的改名解析;`A` 狀態的基準;快照殘留在 `.lumos/` 被鉤子算進碰過的檔。
7. **另起第二套做法**(架構 F1–F5,邊界 F8,資源 F7、F8):另寫 `_kotlin_strip` 而既有 `_strip_c_comments` 註明全庫只此一支;另起 `decision_rows` 通道而既有 `_stack_applicability` 已對 kt 編輯做觸發比對;同一支鉤子重新引入「這一回合」而 2026-09-18 已裁改用工作樹語意(Systems/graph-sync-coverage);新的 SIGTERM 收尾而既有 `_kill_proc_group`;`delta_new` 跟既有 `delta_text` 重複;讀決策表已有 check.py 的 `dt_triggers`;兩份計劃對觸發字邊界定義不同。
8. **改檔前推列細節**(邊界 F9、F10):沒圖譜時 `cmd_impact` 回 rc3、鉤子不解析輸出;型錄觸發字含 `Composable`、`Modifier` 這類幾乎每支檔都有的字,停用字表沒擋到。
9. **鉤子取檔與專案根**(邊界 F11、F12,通才 F9):鉤子既有 `git status` 不帶 `-z`;擋下原因裡的檔名要沿用 `_safe_path` 消毒;專案根在子目錄時 `lint-new` 永遠 rc3;條件只看宣告檔存在,沒有白名單命令的專案每回合白跑。
10. **決策關係沒寫明**(通才 F12,架構 F7 與兩條 ⚠):同會談最多擋三次延伸了「同會談只擋一次」的既有決策;擋下原因要有固定標頭;寫法檢查要不要拆成另一支 Stop 鉤子;rc3 在 lumos 另有「找不到圖譜」的意思。
11. **撤除條件量不到**(通才 F13):擋停與推列都沒寫治理帳,`stop-block/` 七天清掉。

REVISIT:2026-12-15 照〈待解問題〉十一組改寫成完整設計(先查世界:回合起點事件、鉤子機讀輸出),跑規格閘與設計審
