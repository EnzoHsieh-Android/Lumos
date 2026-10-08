# r3 收貨紀錄(舊句檢查設計審,上限輪)

## 席位收貨

- 凍結材料:`r3-snapshot.md`(r2 與 r2 鏡像核對折入後的整份計劃,第 2 輪已提交在 35742a11)。4 席全新(派工單 `r3-dispatch.json`):正確性 opus;邊界、併發 sonnet 5.5;外家否決 Codex(唯讀沙盒,stdout 另存)。換掉前兩輪的接手與架構對齊鏡頭,改看邊界與併發。報告在編排者暫存 `os-r3/`,檔案時間 06:38–06:45,都在派工之後。
- report-normalize 4 份都已是正規化格式。quote-check:正確性、併發、外家否決 3 份對 r3-snapshot.md 全數錨定;邊界席的引句沒用「」包(寫成「引句:原文」),工具抽不到引句、擋下。席位引句不改,改用機械重現:把 7 句引句去掉空白、反引號、星號後逐句在凍結版裡找,7 句都找得到(腳本 `osfold/qa.py`)。
- 發現 26 條(機器數各報告的 F 標題與 severity 行):正確性 8、邊界 7、併發 7、外家否決 4;major 7 條,也就是 blocking 的那 7 條(正確性 F1 F2、邊界 F1、外家否決 F1–F4;併發 0)。
- 多席獨立報到的同一件:帳一行 4 KB 量不準、丟光 rows 還超過(正確性 F5、邊界 F4、併發 F1);revisit 用(筆記, 行)算放過,一行只放過部分名稱時算不到(正確性 F8、外家否決 F2);候選名稱沒有長度上限而表態只收 200 字(邊界 F5、外家否決 F4);大檔的批次讀沒有大小上限(邊界 F3、併發 F3)。多席一致或附了程式位置與實跑,直接處置,不開辯方。

## 判讀

- **編排者裁定照做**:
  1. 邊界 F1:超過 4 MB 的檔改用文字抽定義(`_drift_m1_text_defs`,形狀跟 `_drift_py_def_re` 同一組,加 `add_argument` 引號旗標),兩版都抽、照樣判消失,結論行與帳標明「N 支用文字比對」。上限的理由(ast 尖峰約原始碼 280 倍)寫進去,「4 MB」定義成大於 4194304 位元組。實測 `scripts/test_lumos.py`(3568962 位元組):文字抽 0.05 秒、ast 1.85 秒;ast 認得的 1703 個函式與類別名文字抽全部抽到,另多 54 個。終點語料裡剖不動或太大的檔也改成一支檔掃一次的文字抽,順帶解掉邊界 F2 的「每個名稱各掃一次」。
  2. 正確性 F1:補「要處理 0、只列出 B」那一格(沿用同一句、A 印 0、沒有開頭詞、kind passed),S13、S17 都補。
  3. 正確性 F2:〈前置〉加第 2 條「rtb 更新到含 `m1` 的工具版並重跑安裝」,由本工具鏈會談用跨會談訊息請 rtb 會談做,不動 rtb repo。REVISIT 從兩條前置都成立那天起算,rtb 沒接上就不起算。預期量寫明:工具鏈兩週接近 0,rtb 非爆發期每週約 4 筆,20 筆大概要五週;第一次 REVISIT 多半是延長,滿六週不到就攤給人裁,是預期中的走向。
  4. 外家否決 F1:實驗程式加 `FormalCode`(排除清單同 `_excluded`、Python 用 `_drift_probe_is_py`、其他程式檔用 `_nodehome_code_kind`),revisit 改用它;`run` 的 P4r、P4r2、P4r3 不動。合成 repo 實跑:原本的 `Code` 刪 `src/OldPanel.tsx` 不列,`FormalCode` 列。
  5. 外家否決 F2、正確性 F8:revisit 的「放過」改成同一行的名稱集合相減,鍵是(筆記, 行, 名稱)。合成 repo 實跑「現況先呼叫 `stale_alpha`;沒有參數時呼叫 `stale_beta`」:P4r3 列 {stale_alpha},`clause_released` 抓到 {stale_beta}、標 `line_also_in_main`。
  6. 外家否決 F4:候選名稱去頭尾空白後超過 200 字、或帶控制字元的不列,結論行下面印「N 個名稱太長沒列」、帳記 `too_long`;表態上限不動。控制字元一併處理是邊界 F5 第 2 點(git `-z` 路徑可帶 tab 或換行,表態的一行檢查會擋)。新增 S18。
  7. 外家否決 F3(我判):折。有既有機制可用——`m1` 的定義快取已經用 `~/.cache/lumos/` 的信任目錄那套(`_mkdir_trusted_under_home`、`_trusted_private_dir`)。`_gate_event` 回 False 時,另在 `~/.cache/lumos/drift-m1/ledger-miss.jsonl` 追加一行(ts、repo、head_sha、state);放在另一個子目錄,不受快取 14 天清舊檔影響;REVISIT 讀它,有 1 行就算樣本不足。沒放 git 目錄:專案裡沒有寫進 git 目錄的先例(r1 快取位置選的就是這個理由)。這個檔也寫不進去的殘餘情況(同一顆磁碟滿、家目錄唯讀)寫進〈誠實界線〉。
- **其餘 minor 自己判**:
  - 正確性 F3、F4、F6、F7:直接折。F6 列成刻意差異第 9 條,about_code 寫明只認區塊清單;F7 讓 ①② 成立也攤給人裁並定下一個回頭日期,六週的起算點改成 rtb 接上那天。
  - 正確性 F5、邊界 F4、併發 F1:折。把 `_gate_event` 組事件那段抽成 `_gate_event_build`,量完整事件、量法照 `_ledger_append`(含換行、`> 4096`);rows 丟光再把 nodes 截到 20,再超過就照寫。「8 KB 緩衝」改成實測值(3.14 是 128 KB),寫明 4 KB 是政策值、不是交錯邊界。
  - 邊界 F7:折成〈範圍〉的相容性變更與〈誠實界線〉一句;設計不改(兩個開關各管各的,是 r1 定的)。純文件推送那句的字樣改成「有改到程式檔時照跑」。
  - 併發 F2:折成說明——`gov` 與 `--nags` 會把同提交、同筆記的 c 類與 `m1` 事件折在一起,量 `m1` 一律讀原始帳。不加 token,改 `gov` 是另一支程式的事。
  - 併發 F3:折——批次讀次數改成 0–2、S5 寫明最多 2 次;〈實務隱患〉記憶體補「批次讀不設上限」的量級與重量條件(`parsed + text_defs` 超過 5000 支,或時間到集中在冷快取)。
  - 併發 F4、F5:折進 S5(抽法輸出雜湊釘住、兩執行緒同寫同鍵)與帳欄位 `parsed`、`cache_hits`。
  - 併發 F6:折進〈實務隱患〉效能的數字口徑。
  - 併發 F7:折——〈實務隱患〉併發連到 [[Issues/治理帳多個寫入者都沒上鎖]],寫明實作時登記 `m1` 為寫入者。
- **接受 2 條(minor)**:
  - **邊界-F3**(批次讀不改用 `_nodehome_cat_blobs_capped`):裁定 1 要把超過 4 MB 的檔讀進來做文字抽定義,capped 讀擋掉的正是這些檔;現況 rtb Python 原始碼約 8 MB、工具鏈約 6 MB,讀進記憶體約兩倍,無害。量級與重量條件寫在〈實務隱患〉記憶體(同併發 F3 的折法)。
  - **邊界-F6**(`./tools/run_all.sh` 這種寫法不算提到):這是參考實作 `_mk_rx` 的行為,改整字規則要重跑三組驗收數字,上限輪不動判法。寫進〈誠實界線〉,REVISIT 抽判時把這類漏報單獨記。
- 不成立:無。

## 機械重現(在 clone-ns 與編排者暫存 `osfold/` 跑,只讀;腳本 `osfold/mech3.py`、`osfold/qa.py`,合成 repo 在 `osfold/synth/`;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | 讀凍結版〈做法〉3 結論行:done 只有「候選 0」「兩層都 0」「有東西」三句,「有東西」= 要處理有筆數或判不了 | HIT:要處理 0、只列出 >0 套不上任何一句 |
| 正確性-F2 | `grep -c drift scripts/hooks/pre-push`;讀凍結版〈範圍〉前置 | HIT:0;前置只寫工具鏈 |
| 正確性-F3 | 讀凍結版〈做法〉3 超過 20 筆那句與 S13 | HIT:引號裡帶 `drift scan`,S13 要不提 |
| 正確性-F4 | 讀凍結版〈做法〉4 抽 pairs 的那行 | HIT:只濾 `base_sha`,timeout 等三種會進 pairs |
| 正確性-F5 | 讀 `_gate_event`:note 另寫一份 detail、補 ts 等欄;凍結版只丟 rows | HIT |
| 正確性-F6 | 讀參考實作 `homes_any` 用 `code_changes(True)`、`_about` 只認區塊清單;rtb 1 次、命中差 0 採信席位實測 | HIT |
| 正確性-F7 | 讀凍結版 RETIRE-IF:①② 成立只寫留在提醒;六週從第一次 REVISIT 起算 | HIT |
| 正確性-F8 | 讀改前 `cmd_revisit`:`k not in main_`,k =(筆記, 行);合成 repo 用改後版本實跑 | HIT:改前算不到;改後 `clause_released` 抓到 {stale_beta} |
| 邊界-F1 | `git cat-file -s HEAD:scripts/test_lumos.py` | HIT:3568962 位元組,離 4194304 只差 0.6 MB |
| 邊界-F2 | 讀凍結版剖不動那段:每個候選 × 每支剖不動檔各跑一次 `_drift_py_def_re` | HIT;席位實測 1128 × 0.03 秒採信 |
| 邊界-F3 | 讀 `_nodehome_cat_blobs` 與 `_nodehome_cat_blobs_capped` | HIT:前者沒有大小上限 |
| 邊界-F4 | 同正確性-F5 | HIT |
| 邊界-F5 | 讀凍結版候選判定(沒有長度上限)與表態(1 到 200 字) | HIT |
| 邊界-F6 | `_mk_rx(["tools/run_all.sh","run_all.sh"])` 掃「執行 ./tools/run_all.sh 即可」「../tools/run_all.sh」「bash tools/run_all.sh」 | HIT:[False, False, True] |
| 邊界-F7 | 讀 `cmd_drift_check`:現行 gate=off 直接回 0 | HIT |
| 併發-F1 | `io.DEFAULT_BUFFER_SIZE`;同正確性-F5 | HIT:131072,凍結版寫 8 KB |
| 併發-F2 | 讀 `cmd_gov` 的去重鍵 | HIT:(commit, frozenset(nodes), gate, kind, token),drift-check 沒有 token |
| 併發-F3 | 讀凍結版〈做法〉1 讀取(0–1 次)與〈做法〉3 寫死的順序 | HIT:有粗候選時是 2 次 |
| 併發-F4 | 讀凍結版 S5 | HIT:只測常數改了不命中,沒有抽法改了常數沒改就翻紅的測試 |
| 併發-F5 | 讀凍結版 S5 與帳欄位 | HIT:沒有併發寫的測試,帳看不出快取有沒有在用 |
| 併發-F6 | 讀凍結版〈依據〉r2 那段與〈實務隱患〉效能 | HIT;席位量「過先篩 2000 個 16.9 秒」採信 |
| 併發-F7 | `ls docs/lumos-toolchain-knowledge/Issues/` | HIT:`治理帳多個寫入者都沒上鎖.md` 在,計劃沒提 |
| 外家否決-F1 | 合成 repo(刪 `src/OldPanel.tsx`、`config.json`)用參考實作 P4r3 各跑原本的 `Code` 與新的 `FormalCode` | HIT:`Code` 只列 stale_alpha 那行;`FormalCode` 多列 `src/OldPanel.tsx`,兩者都不列 `config.json` 那行 |
| 外家否決-F2 | 同正確性-F8 | HIT |
| 外家否決-F3 | 讀 `_gate_event_or_warn` | HIT:寫不進去只印 stderr、回 False |
| 外家否決-F4 | 同邊界-F5 | HIT |

表外(不對應單一發現):
- 文字抽定義對 ast:`scripts/test_lumos.py` 文字抽 0.05 秒、ast 1.85 秒;ast 認得的 1703 個函式與類別名文字抽全部抽到,文字抽另多 54 個(模組層指派與三引號字串裡行首的 def)。
- revisit 改後冒煙(工具鏈 828a68be、1474d5d2、b4060e37 三組):命中與四種放過的筆數跟改前一樣(這三組沒有一行只放過部分名稱的情況);P4r、P4r2、P4r3 的定義沒動。
- 邊界席 7 句引句(工具抽不到)手動錨定:7 句都在 r3-snapshot.md。
- `spec-gate` 判門:風險高(守衛面)、18 條全標、懸空 18 只提醒,指到 `lumos loop next`;它跑的時候順帶寫了 `docs/.canary-log.jsonl` 一行。

## 處置

- **折入(24 條)**:正確性-F1、正確性-F2、正確性-F3、正確性-F4、正確性-F5、正確性-F6、正確性-F7、正確性-F8;邊界-F1、邊界-F2、邊界-F4、邊界-F5、邊界-F7;併發-F1、併發-F2、併發-F3、併發-F4、併發-F5、併發-F6、併發-F7;外家否決-F1、外家否決-F2、外家否決-F3、外家否決-F4。落點:
  - 計劃:RETIRE-IF、REVISIT、〈範圍〉(前置第 2 條、相容性變更)、〈做法〉1–4、〈與參考實作的刻意差異〉第 2、3、9、10 條、〈條款〉(改 S5、S6、S13、S16、S17,補 S18)、〈回退〉、〈實務隱患〉、〈誠實界線〉。
  - 參考實作:加 `FormalCode`,revisit 用它並以名稱集合相減。
  - 家筆記 `Systems/存量漂移守衛`:補一句 revisit 的判定口徑。
- **接受(2 條,minor)**:
  - 邊界-F3:文字抽定義要讀大檔,capped 讀會擋掉這些檔;現況量級無害,重量條件寫在〈實務隱患〉。
  - 邊界-F6:這是參考實作的整字規則,改了要重跑驗收,上限輪不動判法;寫進〈誠實界線〉並在 REVISIT 單獨記。
- **不成立**:無。
