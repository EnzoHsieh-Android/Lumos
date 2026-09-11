severity: major

# 推播miss量測_計劃 r1 外部審稿(sonnet)

立場:三個月後接手這份 spec 的人,照著 S1–S5 去改 `recount.py`、去把新步驟塞進每日治理排程、去把 miss 標進 `retrieval-goldset.json`,逐節核對能不能照字面走通。

## 一、frontmatter/summary/緣起

已讀,無 finding。GraphRAG 調研 d1「Enzo 2026-09-11 採納」核對 [[Projects/GraphRAG對節點關聯_調研]] decisions.d1 屬實;F08 否決「新增 lumos 寫帳」的引用核對 [[Projects/全repo審視_計劃]] F08 與 [[Projects/GraphRAG對節點關聯_調研]] 本文一致;REVISIT:2026-09-17 與「既有計劃還掛著」的敘述核對 [[Projects/主session鏡頭利用率_計劃]] 屬實;「r1 裁『比率量到的是圖譜密度』」是對該計劃「r1 推翻的三件事」第 2 點的準確白話轉述,非逐字引用但語意不失真。

## 二、PRIOR-ART

已讀,無 finding。①②③三項齊全,②世界解過的引用(搜尋引擎隱性回饋)未過度延伸,③裁定與正文一致。

## 三、[S1] 推播清單解析三段

C1
severity: major
blocking: 是
引句:「推播清單解析三段都認」
S1 稱「必看」「可能相關的 N 篇」「另外 N 篇分數不高但直接提到這個檔」三段都算「推了」,但 `build_ranked_context` 實際還有第四段「守衛面參考——這 N 篇是軟標記樞紐」(lane),由 `_lane_n = max(0, int(_impact_knob("LUMOS_IMPACT_LANE_N", 3)))` 預設為 3(非 0),預設情況下真實推播文字裡就會出現這一段。`recount.py` 現有 `parse_pins` 目前只認一種標頭類型就 `break`,S1 沒把 lane 段落算進「三段」,只解析三段的話,lane 段推過的節點事後被讀到會被誤判成「沒推卻被讀」的 miss,汙染規則內/關於欄兩類本來要拿去當「impact 回歸案例」的計數。
file: `scripts/hooks/claude/impact-hook.py:663`
file: `scripts/lumos:20568`

## 四、[S2] miss 偵測與分類

C2
severity: major
blocking: 是
引句:「由 `governance/eval/refresh_labels.py` 維護;走它既有的流水線」
S2 稱「判不出」的 miss 標完就能走 `refresh_labels.py` 既有流水線進 goldset,但該流水線的候選池由 `edit_universe()` 呼叫 `lumos impact --file F --ranked --top 50`(未覆寫 `--min-score`,預設 0.20)產生,`must_in_out`/P@k/nDCG 每一個計分函式都只讀這個候選池(`out_nodes`)裡的節點。⚠一個「判不出」的 miss——按定義沒有直連/about_code 可循才會落到這一類——如果現在的排序分數也低於 0.20 門檻,標了 final=2 之後這筆標註永遠不會被任何既有指標讀到,形同白標,而 `ablation_blocked` 的說明文字已自承「候選池是系統自己的 top-N 抓的」,miss 若透過同一支 `edit_universe` 落標,並沒有真的跳出這個同源迴圈。
file: `governance/eval/retrieval_eval.py:124`
file: `governance/eval/retrieval_eval.py:467`
file: `scripts/lumos:24773`

C3
severity: minor
blocking: 否
引句:「判不出的列成候選,交人或雙評審標註,標完進 edit 卷」
`retrieval-goldset.json` 現有 23 筆 `edit` case 每一筆都同時帶 `id`/`file`/`delta`/`commit`/`split` 五個欄位,是機械可驗的既有 schema。S2 沒交代新增的 miss 案例要填哪個 `commit`(編輯當時的 commit 還是發現 miss 時的 HEAD)、`delta` 放什麼、`split` 歸 train 或 held,實作者照 spec 字面走會卡在「既有流水線要這些欄位、spec 沒說給哪個值」。
file: `governance/eval/retrieval-goldset.json`

## 五、[S3] 搜尋零命中

C4
severity: major
blocking: 是
引句:「從同一批逐字稿數 agent 用 Bash 敲的 `lumos search`,配對它的輸出,判零命中」
`recount.py` 現有的 `scan_file`/`classify_bash` 只解析 assistant 訊息裡 `tool_use` 的 command 字串,整支檔案沒有任何地方讀取 Bash 的 `tool_result`(輸出)內容,S3 需要的「輸出」不是現有程式碼的資料流,要新寫一段轉譯。一個 Bash 呼叫可能鏈接多個 `lumos search`(`;`/`&&`)但只有一段合併輸出,`run_in_background` 的 Bash 更沒有同步可讀的 tool_result——S3 沒交代這兩種情形怎麼配對,只靠「判不出」兜底,量測基礎(建議二的評測材料)可能系統性低估零命中數。
file: `governance/eval/lens-utilization/recount.py:393`

## 六、[S4] 每週留存

C5
severity: major
blocking: 是
引句:「在每日治理那支排程的週期觀測段加一步」
本 repo 真正名為「週期觀測」且已有「本週沒跑過才跑」慣例(`.weekly-stamp`/`nags-last-week.txt`,`date +%G-W%V`)的段落,是 `governance/autonomous-loop.sh` 裡 run_exam/run_probe/run_nags/run_replay 那幾段(受同檔「整跑鎖」保護,且在 `LUMOS_AUTOLOOP_OFF` 判斷之前),不是 `governance/daily-governance.sh` 自己那五個 rc1..rc5+`write_health` 的固定步驟。派工單附的參考檔清單只列了 `governance/daily-governance.sh`,完全沒提 `governance/autonomous-loop.sh`,照著做容易把新步驟塞進錯的檔、錯的鎖保護範圍之外,還得自己重造一套冪等機制而不是沿用既有 stamp 慣例。
file: `governance/daily-governance.sh:239`
file: `governance/autonomous-loop.sh:420`
file: `governance/autonomous-loop.sh:467`

C6
severity: major
blocking: 是
引句:「只存推導出來的列:工作階段代號的雜湊、被改的檔、推了哪些節點、之後讀了哪些、miss 分類、零命中查詢字串」
零命中查詢字串本身就是 agent 當下打的自由文字,跟「不存原文」要避免的「逐字稿原文」性質上是同一種東西,差別只在少了上下文。README 明寫逐字稿本機保留期是 Claude Code 預設 30 天會被清,而這裡的設計是把查詢字串寫進每週一份、依既有慣例會進版控的 JSON(同 2026-09-04 首報 commit a39741ab 的先例),等於把原本 30 天內會自動消失的本機資料改成永久留在 git 歷史裡,S4 的隱私段落完全沒有討論這個「本機可清 vs. 永久共享留存」的性質轉變。
file: `governance/eval/lens-utilization/README.md`

## 七、[S5] README 同步

已讀,無 finding。manual 核對方式明確,無機械宣稱,無交叉引用問題。

## 八、邊界與不做

已讀,無 finding。「不動 impact hook、不動派工鏡頭、不改 `docs/.usage-log.jsonl`(F08)」三項核對現況(impact-hook.py 未被此案觸及、`docs/.usage-log.jsonl` 這次也沒被要求動)均屬實,沒有跟既有裁定打架。

## 九、承認的限制

已讀「位置偏差」「用現在的圖譜判當時的推播」「判不出那一類要人標」三條,格式合鐵則四(REVISIT 獨立行緊鄰原句,或明寫事件入口),數字與 [[Projects/主session鏡頭利用率_計劃]] 的既有裁定規則(門檻 20)核對一致,無 finding。

C7
severity: minor
blocking: 否
引句:「既有計劃記過一個 session 372 次 Bash、0 次 Edit」
來源筆記原句是「372 次 Bash、0 次 Edit、1 次 Write」——同一份計劃自己也認 Write 一樣會觸發 impact-hook(`HOOKS = {"PreToolUse:Edit", "PreToolUse:Write", "PreToolUse:MultiEdit"}`)。這份 spec 省略「1 次 Write」,讓「那個 session 完全沒機會被推播」的印象比原始數據更絕對,不影響 S2/S3 機制設計,但引用既有計劃數字不夠精確。
file: `docs/lumos-toolchain-knowledge/Projects/主session鏡頭利用率_計劃.md:59`
file: `governance/eval/lens-utilization/recount.py:16`

「零命中判法靠輸出字樣」一條沒有掛 REVISIT 或明寫事件入口,但緩解手段是「釘一條測試」,測試本身就是自動觸發的機械守衛(輸出字樣一改測試就紅),等同滿足鐵則四精神,不另計 finding。

## 十、實務隱患(逐類複核)

- 併發:唯讀掃逐字稿部分無風險;週跑寫檔部分,若照 C5 誤植到 `daily-governance.sh` 自己的線性步驟或被人直接裸跑 `recount.py --out <週檔路徑>`,會繞過 `governance/autonomous-loop.sh` 既有的「整跑鎖」,兩個行程同時判定「本週沒跑」並各自完整重算,最後覆寫的那個贏——不是資料損毀(spec 的原子寫入已擋住),但會出現排程跟人手動同時跑時「結果取決於誰後寫完」的靜默覆蓋。此風險跟 C5 同源,不重複計分。
- 效能:spec 只估了掃逐字稿本身的秒級成本。

C8
severity: minor
blocking: 否
引句:「掃 `~/.claude/projects/*/` 全部逐字稿,現在一次約數秒到十幾秒」
S2 的「事後才有」排除規則要求對每筆 miss 候選查「git 第一次加入的時間晚於編輯」,等於每個候選節點要另開一次 `git log`(或等價)子行程,而 `recount.py` 目前唯一的 git 呼叫只有 `repo_paths()` 裡一次性的 `git worktree list`。實務隱患的「效能」段完全沒把這塊「每筆候選一次 git log」的成本算進去,候選數量會隨掃描的歷史逐字稿份數增加而放大。
file: `governance/eval/lens-utilization/recount.py:120`

- 資源:只開檔讀、不開連線的敘述屬實,週跑寫入一個小檔案,無新增資源風險,無 finding。
- 隱私:見 C6(已計分,不重複)。
- 金流/對外送出/不可逆:「不適用」核對屬實——本案不碰金流、輸出檔可刪可重跑,無 finding。

## 十一、驗收

C9
severity: major
blocking: 是
引句:「既有 `t_lens_recount_classify` 全綠」
這支測試用 `SourceFileLoader` 直接載入 `governance/eval/lens-utilization/recount.py`,卻沒有像其他數十支測試一樣先呼叫 `_need_src(...)` 守門;`recount.py` 所在的 `governance/eval/` 不在 `_VENDORED_TOOLKIT`/`_VENDORED_TREE_FILES` 清單裡不會被 `lumos update` 裝進消費專案,而 `test_lumos.py` 本身會被裝進去,這支測試在消費專案執行時很可能因檔案不存在直接炸掉——正是圖譜「vendored測試套件在消費端假紅」那篇事故記過的同一種病。S1–S4 新增的四支測試如果照抄同一個 `SourceFileLoader` 寫法,會把假紅範圍再擴大,這份 spec 完全沒提到要補 `_need_src` 守門。
file: `scripts/test_lumos.py:29862`
file: `scripts/test_lumos.py:56`
file: `scripts/lumos:13378`

C10
severity: minor
blocking: 否
引句:「不猜 [test:t_lens_recount_parses_all_sections]」
新測試要掛進 `test_lumos.py`,而該檔是 `ANCHOR_FILES` 清單裡的錨點檔,改動要走 `lumos anchor approve --note` 才是合法路徑,否則 push 前錨點完整性核對會擋下。這份 spec 從條款到驗收都沒有一處提到這個步驟,跟姊妹計劃「主session鏡頭利用率_計劃」自己「同步清單」裡明寫「test_lumos.py(錨點檔,approve)」的做法不一致——屬非阻斷,因為 pre-push 機械閘會自己攔住遺漏。
file: `scripts/lumos:14763`
file: `scripts/lumos:16168`

其餘驗收條目(S1–S4 各自的注入/miss/週跑斷言)敘述具體、可轉成測試,無 finding。

## 總結

全份最高嚴重度是 major。blocking 共 6 條(C1、C2、C4、C5、C6、C9)。
