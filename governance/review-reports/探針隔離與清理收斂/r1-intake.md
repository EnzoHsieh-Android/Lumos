preflight-4: ran

首輪前掃（唯讀獨立席，2026-10-04）：引用存在性、未定義詞、範圍矛盾、程式語意四項皆查。`lumos refcheck` missing=0、out_of_range=0；`lumos prose-lint` 0 命中；`lumos pitfalls --check` 有節。前掃不是正式設計審。

| 類別 | 修改前 | 修改後／處置 |
|---|---|---|
| 未定義詞 | 「頂層安全相對 gitfile繼續允許」 | 明訂頂層相對 gitfile 指向副本內 `.hidden-git` 且通過 gitdir/common-dir/toplevel/符號連結檢查；S1 同步。 |
| 程式語意 | 「保持完整歷史及未提交的工作樹」 | 訂正為保留已有歷史與 `rsync` 複製範圍內內容，副本會提交快照；現行仍排除 `node_modules`、`.venv`。 |
| 範圍矛盾（交正式席） | 「驗收失敗即刪副本」與「`--keep` 保留每次副本」衝突 | 涉及失敗處置核心裁定；未由前掃擅自折入，正式席須裁失敗副本與刪除失敗的語意。 |

## 正式席 F1 根因複現（尚未折入）

邊界席報 `filter.<name>.clean` 可在快照 `git add -A` 執行外部命令。編排者在臨時 Git repo 設 `filter.escape.clean` 寫入同一暫存根的 `outside-marker`，`.gitattributes` 將 `*.txt` 指向該 filter，呼叫現行 `make_sandbox`；輸出 `outside_marker_created=True`、`marker_content=hit`。HIT：模型尚未啟動，副本外已有寫入。實驗僅臨時目錄；正式 repo 未受改動。判準：本案須覆蓋「準備沙盒時不執行來源 Git 設定中的外部命令」，單查 remote/hook 不夠。

## 正式席切分支與一般符號連結複現（尚未折入）

編排者另在兩個臨時 repo 重現。分支條件式 include：來源 main 設 includeIf.onbranch:escape 指向臨時 external config；`make_sandbox` 初始 remote 空、hooksPath=本次 hooks，切到 escape 後 remote=escape、hooksPath=外部空 hooks，對本機 bare 的 dry-run push rc=0。HIT，初始有效值驗收只能證當下，不證切分支後。一般符號連結：來源 `escape-link` 絕對指回來源 `target.txt`，副本建立後寫副本內 link，來源檔變為 poison。HIT，逐次副本不能替代工作樹路徑驗收。兩例都只在暫存目錄做，沒有真遠端寫入。

## 外家唯讀否決席

`r1-外家否決-claude.raw.md` 是 Claude CLI 原始回覆，保留格式原樣；其內嵌 severity 與引句不符合 canary 報告格式，不能直接拿來記帳。其切分支 finding 與同門邏輯席重疊，編排者臨時 repo 實驗為 HIT。未初始化子模組、逾時孫程序、remote.pushDefault 三項是待折入或另驗的線索；外家明說沒有親自重現，不冒稱已機械證實。外家列的 filter.clean 與邊界席相同，編排者已在臨時 repo 實跑 HIT。

## r1 去重與處置（同輪所有席已收）

| id | 原席 | 觀察／編排者核對 | 處置 |
|---|---|---|---|
| G1 | 邏輯 F1 | HIT：切到 escape 後 remote 與弱 hooksPath 才出現，dry-run rc0 | folded：副本 Git 設定改封閉白名單，S3 加切分支驗收。 |
| G2 | 邏輯 F2 | HIT：工作樹絕對連結從副本寫回來源 target | folded：拒絕外指、懸空與成環連結，S2。 |
| G3 | 邏輯 F3／邊界 F2／整合 F2／資源 F5 | HIT：原稿 S2 刪與 S3 全留互斥；全留造成 N 份磁碟 | folded：`--keep` 僅最後已驗收副本，建立失敗仍刪，S4。 |
| G4 | 邊界 F1 | HIT：filter.clean 在 git add 前後寫出副本外 | folded：Git config 白名單在首次 git add 前建立，S3。 |
| G5 | 整合 F1 | HIT：舊試行表第1案仍四輪失敗、四格未登記 | folded：新工作是樣本外儀器介入，新代碼審編號另立但血緣/成本回寫舊計劃，不改舊輪數。 |
| G6 | 整合 F3 | HIT：現行 history_record 無 inconclusive/fatal | folded：JSON/history 增補 fatal、inconclusive、有效分母，S5。 |
| G7 | 資源 F1 | HIT：現行歷史無 sandbox/model 耗時配對 | folded：S7 記兩種耗時，RETIRE-IF 才有入口。 |
| G8 | 資源 F2 | HIT：現行普通題共用同一副本；直從來源逐次複製會漂移 | folded：先凍結一份批次基線，S4。 |
| G9 | 資源 F3 | HIT：Claude runner 用真 HOME，健康檢查只在批末 | folded：S4 只承諾 repo 互不污染；每次後健康檢查，外層隔離入口連原事故。此舉不聲稱證明整個 HOME 安全。 |
| R4 | 資源 F4 | HIT：rsync 無 timeout，現行 --timeout 只包 runner；MISS：原稿並未宣稱 --timeout 是整批 deadline，S4 只管刪除回傳失敗，且此為既有行為。 | refuted as 本案阻擋條件；明寫 setup/cleanup 卡住仍未解，週排程超時是另案外層 watchdog 入口。 |
| G10 | 回滾 F1 | HIT：目前僅 GRADER_VERSION，不能分辨沙盒實作版本 | folded：S7 增 SANDBOX_VERSION，舊列保持 legacy。 |
| G11 | 架構 F1 | HIT：既有 helper 名僅指 source-probe | folded：共用 attempt/cleanup 層，讀碼標記成選配。 |

外家 raw report 的未初始化子模組是新增有效設計線索：即使來源工作樹沒有巢狀 `.git`，gitlink/`.gitmodules` 仍可在 runner 期間初始化；官方 Git submodule 文件支持此入口。已折入 S1，但不灌入六席原報告數。外家「逾時孫程序」未在本輪實跑，保留原稿與原有 timeout 範圍，不能當已驗事實。其他兩項不改本輪存活清單。
