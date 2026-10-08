# 使用者授權例外第4輪

沿code-repair-pilot-01及試行第1案，三輪歷史不重置。使用者聽取三個具體缺口與「再一輪」範圍後明確說繼續；授權記於試行計劃23:53:17事件。不改三輪機械規則、不新增名額。

## 修前根因／改變／保持

| id | 根因 | 要改 | 必須保持 | 配對基線 |
|---|---|---|---|---|
| r3 correctness F1 | 缺合法id的已發呼叫被略過，誤當完整零呼叫 | 畸形id形成unknown，不進有效分母 | 合法完成正證據present；完整零呼叫absent；有正證據仍優先 | 637989b1（code=4a60b231） |
| r3 boundary R3-B1 / security 1 | 清定位環境卻保留Git設定注入與使用者設定來源 | _git_env去command-scope config並封閉global/system設定來源 | PATH等非Git環境保留；副本自己的local hooksPath仍有效；兩runner一致 | 同上 |
| r3 security 2 | 只验来源gitdir，複製的絕對間接路徑可指回來源 | rsync後、任何Git寫入前驗副本gitdir、commondir及worktree實際落點 | 普通clone與安全的相對內部gitfile可用；拒絕時來源byte-equal、臨時副本清掉 | 同上 |

先補三組測試跑紅；涉及Git實驗只在臨時fixture，無網路、真模型或真push。前兩組屬既有4個修復根因组，第三組是本輪首次修復的Git間接路徑根因，第5組；同一缺陷双席不重算。新finding若出現按同例修前後分類，正式只加r4。

## 第4輪收貨、重現與去重

2026-10-04T00:17左右派工（精確起點以r4-dispatch.json為準），審材為2db51cc4..8922c3c9全分支29670行凍結patch，sha256見dispatch；code/context/delta供每席，歷史archive拆5份。五席同一模型家族，無外家辯方；每席報告獨立，全部收齊後才判讀，無改凍結程式。`pitfalls --diff 2db51cc4`篩得tier high與48項全分支告警；`--diff 2db51cc4..HEAD`此次工具卻回filtered:false及2006條全檔告警，故採前者保存為r4-pitfalls.json。本輪修補相對637989b1新增告警為0，整分支仍不等於零告警。

五席原始報告：correctness 1 blocker，boundary 2 blocker+2 major，measurement 2 major，security 2 blocker，arch 1 minor；合計10條，去重後是多個仍未處置的blocking行為與前輪已知A1品質警告。所有引句quote-check及引用refcheck通過；seat-check四席0 unreported，measurement未逐字列snapshot檔名而顯示1 unreported，該席已記完整snapshot hash及共用/分派材料，原稿保留。安全席是唯讀推論，父代理已用臨時Git補實檔重現，不能把安全席本身說成做過寫入實驗。

| 同根因項 / 席位ID | 父代理機械核對 | 637989b1→8922c3c9 | 來源與處置 |
|---|---|---|---|
| local include / worktree config：R4-C1、R4-B2、R4-M2、R4-S1 | HIT；include殘留remote，worktree scope覆蓋hooksPath；本機bare dry-run可走通 | 兩版皆可；r4-parent-reproduction.json，worktree另有dry-run配對 | 舊漏看、r4 Git設定修復不完整；同一有效設定/remote驗後缺口，只計一根因，仍blocking |
| nested submodule：R4-B1、R4-S2 | HIT；副本頂層remote空，巢狀remote仍在、hook缺；臨時bare實際新增ref | 兩版皆可；同檔paired結果 | 舊漏看、頂層路徑驗證邊界不足，仍blocking；資安席另提絕對巢狀gitfile來源寫入，未單獨重現，不宣稱該子形狀已證 |
| 共用沙盒清理：R4-B3 | HIT；第一題毀臨時副本.git後兩道清理失敗，第二題仍見污染而整批rc0 | 兩版皆可；同檔paired結果 | 舊漏看、修補範圍外；仍major |
| Claude空ID：R4-B4 | HIT；空ID工具呼叫與結果錯誤配對，source_evidence=present並可評分通過 | 兩版皆可；同檔paired結果 | 舊漏看、新S3兩runner處理不一致；仍major |
| 全unknown分母：R4-M1 | HIT；0有效/1排除卻匯出total=1且history無inconclusive；程式與[S3]語句/既有不足半數LINE保護有張力 | 兩版皆可；非r4引入 | 待辯方核對具體合約與下游；原席major不私降，仍未處置 |
| 解析器品質：R4-A1 | HIT；C901=34>10，第三輪已報 | 本輪未加劇 | minor，與r3同一品質告警不重算新行為缺陷 |

所有Git實驗限臨時目錄及本機bare，未對真遠端push。boundary的paired腳本位於原報告；security worktree case父代理另用相同兩版臨時fixture驗remote/hook及dry-run，兩版remote=escape、hook指外部空目錄、dry-run rc0。性質是路徑存在證據，不聲稱已發生真專案寫入。先前正確性席一度懷疑fatal之後摘要1/1，核對既有設計後撤回：rc3與inconclusive有標，原有效場保留，不能單靠1/1判錯；未列finding。這與M1全unknown且history缺inconclusive不同，M1另待核對。

## 停手與記帳

使用者只授權追加一次r4；本輪仍有blocking，不修改凍結程式、不自行開r5、不建假的folded/accepted全集，不寫code-loop pass或推送。raw五席記帳後用`loop status --disposal`問閘，預期FAIL。原前置三項修復與207項回歸屬局部通過，不等於全分支放行。第1案仍占一格，其他四案尚未開始。未真跑模型/全套/部署，無放行後14天觀測；成本完整總時間與新步驟總時間仍未知，不能拿席位時間加總。第四輪新發現多為修前已有，只有本輪修補不完整，尚未證本輪新增行為bug；r2那1個已證修復引入缺陷仍是歷史累計。

原先佔位文字在全席收貨後替換；不追加已綁定r3材料。
