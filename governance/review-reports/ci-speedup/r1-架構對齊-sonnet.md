severity: major

# CI加速計劃 r1 架構對齊審查(sonnet)

## 問 1 分層與依賴方向

結構大致對:判斷邏輯放 scripts/lumos 成一支指令,ci.yml 只用 `python scripts/lumos <子指令> --repo .` 呼叫,跟現有步驟一致。
file: `.github/workflows/ci.yml:52`(pitfalls 用 `--repo .`、`|| true` 吃失敗)、`.github/workflows/ci.yml:124`(code-loop check 用 `|| {` 處理回傳碼)。
讀寫兩端分居:讀(ci-reuse)進 lumos,寫(mark 工作的 `gh api` 寫提交狀態)直接寫在 workflow YAML。現有 ci.yml 沒有任何直呼 gh 的步驟,這是新增的一種呼叫位置,但寫狀態一事 lumos 目前也沒有對應指令,不算跨層直呼,列為 minor 提醒。

severity: minor
blocking: 否 + 判準:結構對(workflow 呼叫 lumos),只是讀走 lumos、寫走 YAML 兩種位置並存,不是第二種呼叫 gh 的做法。
引句:「用 `gh api` 對 `github.event.pull_request.head.sha` 寫狀態 context `lumos/full-suite-tree`」
file: `scripts/lumos:39168`(`_ci_gh` 是唯一包 gh 的函式,寫入沒有現成對應)

## 問 2 命名與錯誤處理

指令名 `ci-reuse` 與 `ci-wait`、`ci-status` 同前綴,命名一致。回傳碼一律 0:`ci-status` 恆 rc0(file: `scripts/lumos:39474`),`ci-wait` 在 gh 缺席、查詢失敗時也 fail-open 回 0(file: `scripts/lumos:39257`),方向一致。

不一致處(都是 minor):
- 輸出格式:鄰居印人話加「→ 判定: <verdict>」,機器讀走 `--json`(file: `scripts/lumos:39262`、`scripts/lumos:39473`);ci-reuse 另創 `reuse=true/false` 鍵值行,沒有 `--json`。
- 旗標名:鄰居用 `--repo-dir`(file: `scripts/lumos:46529`、`scripts/lumos:46536`);計劃寫 `--repo .`,跟 ci.yml 其他子指令一致(file: `.github/workflows/ci.yml:201`),但跟 ci 家族不一致。
- 啟用開關:鄰居一律先過 `_ci_config`(.lumos/config.json 的 ci 區塊,未宣告=關閉)(file: `scripts/lumos:39146`);計劃沒說 ci-reuse 要不要過這道。不過的話,沒宣告 ci 區塊的專案也會打 GitHub。⚠ 判不準,計劃沒寫。
- 失敗原因去處:鄰居 fail-open 的原因寫 stderr(file: `scripts/lumos:39321` 附近的 `(fail-open,不擋任何流程)`);計劃把原因跟 reuse 行一起印 stdout,而 ci.yml 會解析 stdout,原因文字混進去會干擾解析。

severity: minor
blocking: 否 + 判準:錯誤處理方向(fail 往安全側、回傳碼 0)一致,只是輸出格式、旗標名、啟用開關沒對齊鄰居。
引句:「全部成立印 `reuse=true` 與原因(含合併請求編號);任何一步失敗印 `reuse=false` 與原因;回傳碼一律 0。」

## 問 3 第二種做法

severity: major
blocking: 是 + 判準:引入第二套取 repo 名的做法(major 錨:第二種做法)。
引句:「repo 名從 `git remote get-url origin` 或環境變數 `GITHUB_REPOSITORY` 取。」
既有做法:ci 家族根本不取 repo 名,`gh` 以 cwd 的 git 遠端自己判定,呼叫時只給 `cwd=repo_root`。
file: `scripts/lumos:39168`(`_ci_gh` 以 cwd=repo_root 跑 gh)、`scripts/lumos:39180`(`_ci_list_runs` 沒帶 repo 參數)。
專案內唯一另一處讀 origin 是 bootstrap 找工具鏈來源,語意不同,且帶身分探針(file: `scripts/lumos:21970`),不能當共用的取名函式。
建議:`gh api repos/{owner}/{repo}/...` 用 gh 內建的佔位符,由 gh 依 cwd 代入,或交給 `GH_REPO`,就不必自己解析 remote URL(ssh/https/.git 尾綴的解析本身也是新風險)。

severity: minor
blocking: 否 + 判準:呼叫 gh 的方式計劃沒寫明要不要走 `_ci_gh`;沒說就判不準,⚠ 要求寫明是重用現有函式。
引句:「`gh` 不在、沒有 token、網路錯、JSON 看不懂,都算 false。」
既有做法:`_ci_gh` 已把「gh 缺席回 None、逾時、非零回傳碼」收成同一個回傳形狀,`_ci_list_runs` 與 `_ci_failed_step` 都靠它,JSON 解析失敗各自就地處理。
file: `scripts/lumos:39168`(`_ci_gh`)、`scripts/lumos:39206`(`_ci_failed_step` 的 JSON 看不懂處理)。
若 ci-reuse 另寫一套 subprocess 呼叫就是第二種做法(升為 major);計劃用字「gh 不在」與 `_ci_gh` 的契約吻合,推測會重用,⚠。

## 問 4 落點

severity: minor
blocking: 否 + 判準:現況寫進 bound-tests-gate 合理,但有兩個小缺口(命令說明表、ci 家族沒有 Systems 家),屬補寫、不是選錯家。
引句:「(放 scripts/lumos,家是 [[Systems/bound-tests-gate]])」
- bound-tests-gate 的 about_code 已列 `.github/workflows/ci.yml`、`scripts/hooks/pre-push`、`scripts/lumos`(file: `docs/lumos-toolchain-knowledge/Systems/bound-tests-gate.md:49`),CI 全套切片與純文件子集的既有脈絡(2026-09-12、2026-09-18 兩條)已在這篇。拆工作與跳過全套是同一件事的延續,合理。
- 大小:該篇約 21.5KB(21497 位元組),不小,但這個 repo 的 Systems 節點普遍這種規模,新加一條 WHY 不構成換家理由。
- CI回流開場提醒不適合:它的 about_code 只有 `scripts/hooks/claude/ci-status-hook.py`,責任寫明「只讀帳不打網路、不跑 CI、不寫帳」(file: `docs/lumos-toolchain-knowledge/Systems/CI回流開場提醒.md:7`),而 ci-reuse 要打網路,放進去違反它自己的責任邊界。
- 缺口:計劃〈做法〉6 只列改摘要與註解,沒提 ci-reuse 要進指令說明表與 argparse 註冊。鄰居三處對應:說明表(file: `scripts/lumos:45783`)、註冊(file: `scripts/lumos:46529`)、分派(file: `scripts/lumos:47101`)。漏掉說明表可能被既有的「每個子指令要有說明」類測試抓到,⚠ 我沒跑該測試確認。另 ci 家族(ci-wait/ci-status)目前沒有專屬 Systems 節點,只有 Projects 計劃,新指令歸 bound-tests-gate 不衝突。

總結:不對齊共 5 條,其中 major 1 條
