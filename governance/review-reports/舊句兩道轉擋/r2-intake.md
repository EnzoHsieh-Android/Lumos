# r2 收貨、重現與處置

## 收貨

六席(正確性2、邊界2、接手2、併發2、回滾2、架構對齊2,皆 sonnet,全新代理、沒看過 r1)全部交回後才一次寫進卷證,報告取自逐字稿。兩份退回原席只補格式:正確性2 的引句沒用「」包(機器抽不到),回滾2 有一段「已併入、無獨立 finding」留了發現標題(少一行等級);兩席重交的內容與原報告逐字相同,只改格式。六份正規化、引句錨定、引用路徑檢查全過。repo 沒被席位動過(git status 只有本編排者的卷證與帳;reflog 最新兩筆是本編排者的提交)。併發2 在 /tmp 的 clone 與極簡 repo 做了實驗並附命令與輸出。

## 人裁(收齊後、折入前)

兩件事反覆出現而修補解決不了,攤給 Enzo 裁(2026-10-09,本會談直接選):
- 重讀 CI 要不要也擋 → 「只在本機擋」:CI 那一步不帶新的 `--gate` 旗標、照舊只提醒。合併讓指紋變(r1 三席)、分次推送與兩分支各自表態(r2 併發2 F1、回滾2 F2)這一整類 CI 誤擋因此消失。
- 第一層成本(主程式被約 70 篇認領,判完再改程式就要重判;歷史 18 次推送 47 篇)→ 「接受,照擋」,RETIRE-IF 加量第一層重判篇數。

## 處置(65 條;折 63、放行 2、駁回 0)

編號:C2=正確性2、B2=邊界2、H2=接手2、N2=併發2、R2=回滾2(F7 已併入 F3,無此編號)、A2=架構對齊2(1=反向依賴、2=照留指令產生處、3=表態細節、4=終點找不到分類、5=事件名與輸出流、6=CI 環境變數、7=已對照兩種定義、8=BOUND 綁法、9=規則類第四種判法)。

| finding | 重現 | 根因組 | 去向 |
|---|---|---|---|
| N2-1、N2-3、R2-2(CI 部分)、N2-7 | HIT(N2-1 實驗:本機「沒有要對照的家筆記」、CI 列出候選;合併後 ack 原文對不上) | G-CI 本機與 CI 範圍不同 | 折:人裁只在本機擋,CI 不帶 `--gate` |
| C2-4、B2-6、N2-2、R2-10、A2-6 | HIT(`CI=0` 也算有值) | G-CI 環境變數當開關 | 折:改由掛鉤傳 `--gate`,不讀 `CI` |
| C2-1、B2-14、H2-2、R2-1、A2-7 | HIT(prepare 用 `_note_reread_committed` 只比檔名) | G-COVER 已對照兩種口徑 | 折:新 `_note_reread_covered` 讀內容只收 provenance_ok,prepare 與 check 共用 |
| C2-6、B2-2、H2-1、N2-4、R2-2、A2-8 | HIT(`_drift_current_finding` 只認 c2/c3/c6;`_drift_ack_buckets` 要 related) | G-ACK 表態接錯機制 | 折:自成 `_drift_reread_split_acked`、取聯集、不放進 BOUND;`_DRIFT_KINDS` 明寫要加 |
| C2-2、C2-3、B2-1、B2-4、B2-5、N2-5、R2-6、C2-9 | HIT(B2-1 實測空引句命中 175 行) | G-NEEDLE 比對字串取法 | 折:quote ≥6 字且為 text 子字串才用,否則用 text,兩者皆空略過 |
| B2-3、C2-7、N2-6、R2-12 | HIT(`.tmp-wlf` 殘檔會被 `git add` 整個資料夾帶進去) | G-READ 讀檔範圍與上限 | 折:只讀檔名合正規式的、傳 deadline、超限印最大五份;record 的 git add 改列具體檔名 |
| B2-11、C2-11、A2-3 | HIT(`_ns_summary_logical` 不傳 cont 只回首行) | G-ENTRY 摘要條目口徑 | 折:用 `_note_summary_entries` 同一套讀法,表態記整條、行號為條目開頭 |
| A2-9 | HIT | G-ENTRY 規則類第四種判法 | 折:前綴取既有摘要前綴表、測試綁定用 `TEST_REF_RE`、合約用 `INVARIANT_RE`,收成一支放回頭重讀常數段 |
| C2-8 | HIT | G-ENTRY 不含 IRREVERSIBLE/CHECKPOINT | 折(寫明理由):人裁範圍是 RULE、INVARIANT、帶測試綁定,不另擴;帶測試綁定的照算 |
| C2-5、B2-10(後半)、R2-11、H2-5 | HIT(既有測試④釘 gate=off 加 old_sentence=block 照跑) | G-OSDEF 明寫值受不受總開關壓 | 折:只有沒寫才跟總開關,明寫照原義;gate=off 沒寫的行為變化寫進 CHANGELOG |
| H2-3、H2-4 | HIT(掛鉤與 CI 逃生句「改 gate 沒用」、手冊 06/08、svg) | G-DOCS 漏改清單 | 折:清單補執行時逃生句、手冊、svg 與產生器、守檔計劃的 RETIRE-IF/REVISIT、舊句偵測實驗計劃 |
| H2-11 | HIT | G-DOCS superseded 寫法與綁測條款 | 折:補 `[被取代:]`;條款改寫成不帶 `--gate` 的行為、測試名照舊、S9 限制保留 |
| C2-12、B2-10(前半)、R2-4 | HIT | G-UNDEC 設定讀到之前的失敗 | 折:改讀工作目錄設定判模式,也讀不到才照 block |
| A2-4 | HIT(drift check 對終點找不到回 2) | G-UNDEC 分類與鄰居不同 | 折:終點找不到改回參數錯回 2,跟 drift check 一致 |
| A2-2 | HIT(`_drift_fix_hint` 是照貼指令單一產生處) | G-OUT 第二種指令產生法 | 折:照留指令由 `_drift_fix_hint` 加 reread 分支產生 |
| R2-9、H2-7 | HIT(code-loop 先、reread 後;筆記不在簿記清單) | G-OUT 改句會作廢留痕 | 折:擋下訊息註明,已過代碼審優先表態 |
| B2-8 | HIT | G-OUT 帳 detail 無上限 | 折:detail 前 50 行 |
| H2-10 | HIT | G-OUT CI 擋下訊息 | 折:CI 不擋,議題消失 |
| B2-9、R2-13 | HIT | G-HOOK 128 以上與標準錯誤 | 折(寫明理由):照其他會擋的閘一致;舊工具用法雜訊列為部分更新已知雜訊 |
| R2-3 | HIT(18 筆 reminded 全是已對照 0 篇) | G-COST 第一層成本與量測 | 折:人裁接受;RETIRE-IF 加第一層重判篇數與略過比例 |
| R2-5 | HIT(`_version_nudge` 只在來源較新時提示) | G-ROLLBACK 版本倒退 | 折:回退走 v1.4 撤回 |
| B2-7、B2-13、R2-8、H2-9、H2-8 | HIT(實測 7855 位元組;現存規則類條目 0) | G-EVID 數字宣稱 | 折:改正數字、刪「上線要處理一次」、帳的時間範圍與單位寫明 |
| B2-12 | HIT | G-ACK 讀取來源 | 折:表態讀頂端提交(`_drift_load_acks`);ack 寫入讀工作目錄 |
| H2-6 | HIT | G-READ 殘檔 | 折:同 B2-3 |
| B2-10(改名) | HIT | G-PATH 筆記改名 | 折:寫明改名後舊路徑紀錄不適用、第一層會要求重判 |
| A2-1 | HIT | 回頭重讀那段呼叫存量漂移的 helper | 折(寫明落點):規則類判斷放回頭重讀常數段,drift ack 來呼叫,照 `_path_special_chars` 先例 |
| A2-5 | HIT | 事件名 reminded、提醒走標準輸出 | 放行:沿用既有 18 筆事件名維持統計連續;提醒走標準輸出是既有行為,擋下原因已改走標準錯誤;minor |
| C2-10 | HIT(`_note_reread_scan` 把控制字元路徑放 ctrl) | 控制字元路徑被排在候選外 | 放行:放過而非誤擋,沿用既有行為並在設計寫明;minor |

`refuted-set`:none。
