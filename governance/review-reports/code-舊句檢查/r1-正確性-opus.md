severity: major

# 舊句檢查 代碼審 r1:正確性-opus(審 r1-snapshot-code.patch)

## F1 路徑不是 UTF-8 時寫帳丟 UnicodeEncodeError,warn 預設也整支當掉回 1,掛鉤當成擋下

severity: major
blocking: 是
引句:「return len((_j.dumps(ev, ensure_ascii=False) + "\n").encode("utf-8"))」
file: `scripts/lumos:29196`
file: `scripts/lumos:29240`
file: `scripts/lumos:1228`
file: `scripts/hooks/pre-push:479`

1. 路徑從 git 讀進來時用的是 `nfc(os.fsdecode(...))`(`_drift_m1_changes`、`_nodehome_list`)。檔名不是 UTF-8 時,解不開的位元組會變成「孤立代理字元」(例:`\udcf1`)。`_esc_clean` 只換控制字元,這種字元它不換。
2. m1 會把這種路徑放進帳的三個欄位:`text_defs_paths`(剖不動或太大的終點語料檔,原樣)、`rows[].path`、`nodes`。接著 `_drift_m1_fit` 的 `size()` 對整筆事件做 `.encode("utf-8")`,或 `_gate_event` 用 utf-8 的 `f.write` 寫檔。兩處都會丟 `UnicodeEncodeError`。這個例外不是 `OSError`,`_gate_event` 接不住,`_drift_old_sentence_check` 也只接 `_DriftM1Stop`,結果整支 `drift check` 印出 traceback、回 1。
3. 重現(腳本 `/private/tmp/claude-501/-Users-enzo-harness-lumos-toolchain/82c93a23-33db-4a5a-af96-cd2d2b4af3c1/scratchpad/cor-opus-exp/repro-f1.sh`,用 `git update-index --cacheinfo` 直接把檔放進索引,不碰磁碟):
   - repo 裡有一支舊的 Python 2 檔,檔名是 latin-1 位元組 `legacy/se\xf1or.py`(剖不動)。
   - 這次推送只從 `src/a.py` 刪掉 `def old_func_x`,沒有任何筆記提到它。
   - 沒寫設定(old_sentence 預設 warn)時,輸出是 `UnicodeEncodeError: 'utf-8' codec can't encode character '\udcf1' ... surrogates not allowed`,`rc=1`。
   - 同一個範圍設成 `{"drift_check":{"old_sentence":"off"}}` → `rc=0`。所以是 m1 帶進來的。
4. 另一種路徑也會中:一篇檔名是 latin-1 的筆記提到被刪的名稱(`e1.sh`,同一個目錄)。它在「只列出」層產生一筆 rows,`size()` 那行就炸了。
5. 為什麼算嚴重:推送前掛鉤只要看到 rc 1 就擋下,還會印「照 drift fix 改或 drift ack 表態」,可是這兩條路都修不了這個問題。CI 也一樣紅。這個 repo 裡只要那支檔還在,之後每一次刪掉某個定義的推送都會當掉,不會自己好。這跟計劃 [S3] 說的「warn 時 rc_m1 一律 0」、以及〈做法〉1 說的「不會讓整支 check 當掉」都衝突。前提是 repo 裡有檔名不是 UTF-8 的檔,工具鏈與 rtb 都沒有,出現機率低;不過一中就是在預設模式下擋人,所以等級放在這裡。
6. 修法方向(一句):帳的每個字串欄位先換掉代理字元再組事件(例如 `.encode("utf-8","backslashreplace").decode()`),或在 `_drift_m1_ledger` 接住 `UnicodeEncodeError` 改走 ledger-miss 留痕。`text_defs_paths` 照計劃〈做法〉3 本來也該過 `_esc_clean`,這次沒過,要一起補。

## 查過、沒發現問題的地方(照鏡頭逐項)

- **名稱抽取(ast)**:對 repo 裡全部 `.py`、`scripts/lumos` 與 3.14 標準函式庫,共 2308 支檔,逐支比對 `_drift_py_names(txt, m1=True)` 四個集合的聯集跟參考實作 `Code.py` 的 `defs|flags`。只有 1 支不同(`test/tokenizedata/bad_coding2.py`,開頭有 BOM),正好落在刻意差異第 4 條。腳本:`cor-opus-exp/x1.py`。
- **文字退路**:在 150 支標準函式庫檔與 `scripts/*.py` 上抽 13214 個名稱,比 `_DRIFT_M1_TEXT_DEF_RE` 跟 `_drift_py_def_re(name, False)` 的判斷,0 筆不同(`x4.py`)。4 MB 用的是原始位元組的 `len(raw) >`,跟計劃「大於它就算太大」一致。改到的檔只要有一版太大,兩版都改用文字抽;剖不動的判斷優先。都照〈做法〉1。
- **撤除節①②、about_code、句內切句**:對工具鏈全部 3325 篇 `.md`,比 `_drift_m1_retired` 跟參考實作 `Note.ret_full3`、`_drift_m1_about` 跟 `Note._about`,都是 0 篇不同。對 27.9 萬行、每行隨機取位置比 `_drift_m1_clause_hist` 跟 `_clause_has_hist(..., HIST_RX2)`,0 筆不同(`x2.py`)。54 個字眼跟正則字面上也等於參考實作的 `HIST_WORDS2`/`HIST_RX2`。
- **形狀過濾、整字正則、「消失」三類**:`_drift_m1_shape_ok`、`_drift_m1_name_rx` 跟 `_shape_ok`、`_mk_rx` 逐行相同。三類消失的判法(定義名要終點語料的聯集裡也沒有、路徑直接加入、檔名要終點任何位置都沒有同名)跟 `_gone_defs`/`_gone_paths` 的結構一樣,形狀過濾先做或後做結果相同。另外在工具鏈最近 20 個提交(40c1fe0d 之後、驗收沒涵蓋的那段)實跑 P4r3 對照正式判定,0 筆不同。不過這段期間兩邊都沒命中,這項佐證偏弱(`x3.py`)。
- **名稱先篩**:兩組正則的邊界都排除 ASCII 英數與底線,所以命中時名稱的每一段 ASCII 詞在全文裡一定是完整的詞。「先篩不改結果」的論證成立。
- **gate 與 old_sentence 兩個開關、回傳碼取大**:`cmd_drift_check` 先跑 `_drift_check_c` 拿 rc_core,old_sentence=off 直接回;不是 off 就另算 30 秒截止、回 `max(rc_core, rc_m1)`。gate=off 那句只在 old_sentence 不是 off 時換成新說法。`_drift_config` 拆成兩支後,gate 的三個回傳值在沒設定檔、JSON 壞掉、不是物件、沒寫 gate 這幾種情況都跟原本一樣。`_drift_report_must` 只把判不了那句抽成共用函式,字面相同。
- **結論行、分層、表態、帳**:六種結論字樣、block/warn 的開頭詞、「要處理 0、只列出 N」不算有東西、no-base 記 skipped、判不了時 handle/listed 是 null、rows 先丟只列出再丟要處理、再把 nodes 截到 20,都照〈做法〉3。表態取同路徑同原文所有 m1 表態名稱的聯集,沒有 names 欄的不涵蓋;`--name=` 過 `_drift_sh`。
- **快取**:鍵是「內容編號、schema、Python 主次版本」三者的 sha256;只有剖得動的才寫;讀的時候驗擁有者與權限,也驗保鮮期;開跑前刪過期檔,目錄不可信時一支都不碰。跟計劃一致。
- **既有行為**:在 clone 裡跑 `python3.14 scripts/test_lumos.py -k drift`,709 條全過(含 c1 到 c5、probe、exam、scan、fix、prepush 相關,以及 18 支 m1 條款測試)。`_drift_split_acked` 對非 m1 的發現走原路;m1 表態進了 c 類的 keys 集合,種類不同所以不會命中。`_drift_scan_print` 改用 `_DRIFT_SCAN_KINDS`,內容等於原本的 `_DRIFT_KINDS`。`_gate_event` 與 `_lens_cache_write` 抽出共用函式後,組出的事件與寫檔行為不變(只多回傳一個布林)。

## 圖譜鏡頭逐條判定

- `Systems/lumos-cli-read`(search 排除 superseded):這次沒動 search 的濾網,不影響。
- `Systems/bound-tests-gate`(code-loop check 真跑綁定測試):沒動 code-loop check,不影響。
- `Systems/guard-kill`(rc 優先序、--json 純度):沒動 guard kill,不影響。
- `Systems/授權與歸屬`(`_VENDORED_TOOLKIT` 不含授權檔、主程式檔頭 SPDX 與 MIT 全文):patch 沒碰檔頭,也沒碰白名單,不影響。
- `Systems/測試假綠形態`(還原翻紅釘要配前置斷言):patch 帶的 m1 測試每支都有「①前置」斷言。這一份不是我審的範圍,只看到這一點,不另判。
- `Systems/lumos-cli-lifecycle`(re-inject 只覆蓋 sentinel 之間):沒動,不影響。
- `Systems/design-loop`(處置閘第五步):沒動,不影響。
- `Systems/pitfalls-code-loop`(RISK):這次是 scripts/lumos 的推送閘改動,照規矩走代碼審,就是現在這一輪。F1 就是這一類「擋人的閘在邊界輸入下當掉」的風險。
- 超出上限只列名的那些節點:這份 patch 碰到的共用部分只有 `_gate_event`(抽出 `_gate_event_build`,行為不變)、`_lens_cache_write`(抽出 `_home_cache_write`,行為不變)、doctor 開關那一行(多講 old_sentence),沒看到會牽動那些節點合約的改動。

最高等級:major
