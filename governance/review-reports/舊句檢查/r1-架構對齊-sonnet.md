severity: major

(審查對象:舊句檢查_計劃 r1 凍結版。佐證行的路徑都指審查用 clone 的 `scripts/lumos`。)

## F1 「終點整個 repo 有沒有同名定義」另起一套語料與退回法,沒用既有的程式樹判定
severity: major
blocking: 是
引句:「旗標=終點所有 Python 檔都沒有登記它」
file: `scripts/lumos:26943`(`_DriftProbeTree`)、`scripts/lumos:27013`(`corpus`)、`scripts/lumos:27025`(`_defines`)、`scripts/lumos:26777`(`_drift_probe_code_path`)、`scripts/lumos:26816`(`_drift_py_def_re`)
1. 專案裡「某名稱在終點樹還有沒有定義」已經有一條做法:乙(probe)的 symbol 條件走 `_DriftProbeTree.corpus()` 列語料(`_drift_probe_code_path`:排除 docs/、governance/,並分程式檔與測試檔兩類),再用 `_defines()` 逐檔判(`_drift_probe_is_py` → `_drift_py_names`;剖不動退回 `_drift_py_def_re` 逐行正則,寧可多認)。
2. spec〈做法〉1 的「消失」判準另寫成「終點整個 repo 的所有 Python 檔」、剖不動時另寫「文字比一次(`def 名`、`class 名`、`名 =`、`"--旗標"` 字樣)」。PRIOR-ART 只說沿用 `_drift_py_names` 與 `_drift_probe_is_py` 兩支葉子函式,沒說語料枚舉與退回法要不要共用。照字面做就是同一個 repo、同一個問題(名稱還在不在),兩套語料範圍:probe 不看測試檔、docs/、governance/,m1 看所有 Python(含 test_lumos.py、governance/eval 底下的實驗腳本)。
3. 具體失敗場景:函式 `foo_bar` 從 scripts/lumos 刪掉、但測試檔或 governance/eval 的腳本裡有同名 def。probe 的 `when-symbol:foo_bar` 判「不存在」,m1 判「還在」不列筆記裡講它的句子——同一次推送兩個檢查對同一個名稱的裁定相反。反過來的方向(spec 想抓的名稱剛好只剩測試檔定義)沒有被 spec 講清楚是刻意。
4. 退回法不同:既有退回是行首錨定的正則(`def`/`class`/行首 `名 =`),spec 的「字樣」是子字串,註解或字串裡寫到 `def 名` 也算還在;且沒說旗標的文字比對用什麼。旗標(`add_argument`)抽取落點 spec 沒寫:`_drift_py_names` 只回 (函式, 類別, 模組指派) 三集合,失敗時整個回 None,旗標要另剖一次(第二次 ast.parse 且得複製例外組)或改回傳形狀。
5. 要修:在 spec 明寫「終點語料與 `_defines` 共用同一支(或明說為何要不同範圍並列進誠實界線),退回法重用 `_drift_py_def_re`」,並寫旗標抽取擴在 `_drift_py_names` 哪個回傳位置。⚠ 兩種範圍哪個對,要看實驗的 P0→P1 數字是用哪個語料量的(spec 沒說);以上只判「第二套做法沒交代」。

## F2 定義快取是專案裡第三種快取做法:沒有版本鍵、沒有信任檢查、讀就要寫
severity: major
blocking: 是
引句:「定義快取:每個 blob 的定義集合以 blob 雜湊為鍵」
file: `scripts/lumos:33120`(`_lens_cache_path`,鍵含 `schema{_LENS_SCHEMA}`)、`scripts/lumos:33128`(`_lens_cache_read`:自己 uid、group/other 不可寫、TTL)、`scripts/lumos:34746`(bound-filter 快取,鍵含 `schema{_FILTER_PROBE_SCHEMA}`、放 `~/.cache/lumos/`、走 `_trusted_private_dir`)、`scripts/lumos:26839`(drift 的行程內快取,有上限、超過就清空)、`scripts/lumos:14932`(`_write_lf` 原子寫)
1. 既有兩種做法:①行程內模組字典(`_DRIFT_LS_CACHE`/`_DRIFT_OID_CACHE`,註解特別交代有上限);②持久快取放 `~/.cache/lumos/<名>/`,鍵含判定規則版本(schema),讀寫兩端都走 `_trusted_private_dir`/`_mkdir_trusted_under_home`,淘汰靠 TTL(mtime),讀不會寫。spec 的做法三項都不一樣:放 `git-common-dir/lumos/`(專案裡沒有先例寫進 git 目錄)、鍵只有 blob 雜湊、淘汰用「最久沒用到」。
2. 鍵沒有規則版本:blob 雜湊只決定輸入,不決定抽取函式的版本。這份設計本身就要改 `_drift_py_names`(加類別層指派)並新增旗標抽取;之後任何一次再調抽取範圍,舊快取的定義集合照樣命中,少抽的名稱就被判成「消失」(假陽性),多抽的判成「還在」(漏報)。既有快取全都帶 schema 就是為了這件事(`_FILTER_PROBE_SCHEMA` 的註解:「測試工具升級…都會讓判定翻面」)。Python 版本也影響 `ast.parse` 結果(最低 3.14 是下限不是固定值)。
3. 「剖不動」要不要進快取 spec 沒寫:若把 `_drift_py_names` 回 None(含 MemoryError/RecursionError 這種跟環境有關的暫時失敗)也快取,那個 blob 永遠被當剖不動。⚠ spec 沒講,判不準。
4. 「最久沒用到」要求命中時也更新使用時間,也就是每次推送(含全命中)都要重寫整份最多 20000 筆的 JSON;既有快取沒有「讀即寫」。兩個推送並行時整檔 last-write-wins 會互相吃掉對方新增的筆(spec 的〈併發〉只講「讀到壞檔當沒有快取」,沒講這個)。
5. 信任檢查:快取內容直接決定 block 模式下哪些名稱算「消失」(改快取就能讓某個名稱永遠「還在」,等於一條繞過)。既有持久快取在讀寫兩端都驗 uid/權限(`_lens_cache_read`、bound-filter 那段),spec 沒有對應說法。
6. 原子寫:spec 自己寫「暫存檔、自驗讀得回、再原子替換」,專案已有 `_write_lf`(唯一名暫存檔、copymode、os.replace)與 `_lens_cache_write`(mkstemp、chmod 0600),不必第三份;spec 應指定用哪一支。
7. 要修:回到既有兩種做法之一——行程內字典就好(冷快取實測 3.6–7.4 秒在 60 秒預算內),或持久快取放 `~/.cache/lumos/` 並帶抽取版本常數、走 `_trusted_private_dir`、用 TTL 淘汰。若堅持 git 目錄,要在 spec 寫為什麼(多工作樹共用)不能用既有位置,並補版本鍵。

## F3 表態名稱集合「仿 c2/c3」沒指定取哪一種涵蓋語意,m1 又不能進 `_DRIFT_BOUND_KINDS`
severity: major
blocking: 是
引句:「才算已表態(仿 c2/c3 的 related 涵蓋);新名稱觸發同一行 → 照列」
file: `scripts/lumos:27404`(`_drift_split_acked`)、`scripts/lumos:27413`、`scripts/lumos:27422`、`scripts/lumos:27516`(`cmd_drift_ack` 的 bound 分支先驗「那一行現在真的是這種發現」)、`scripts/lumos:26258`(`_DRIFT_BOUND_KINDS`)、`scripts/lumos:27385`(`_drift_load_acks` 只認 `_DRIFT_KINDS`)
1. c2/c3 的涵蓋不是「所有表態的聯集」:`_drift_split_acked` 只取 seq 最大的那幾筆(`_drift_bound_latest`),而且每一筆都要涵蓋現在的清單才算已表態。照這個「仿」,m1 先表態名稱 {A}、之後為了新出現的 B 再表態 {B},最新那筆只有 {B},A 又被判沒表態、整行重列。要不要聯集,spec 沒寫,S4 的測試也只驗「集合沒全部涵蓋照列」,兩種實作都過。
2. m1 不能直接加進 `_DRIFT_BOUND_KINDS`:那個集合在 `cmd_drift_ack` 會呼叫 `_drift_current_finding` 驗行、寫 `related`,而 spec 明說 m1 的 ack 不驗行、記的是名稱集合;`_drift_split_acked` 與 `_drift_prev_ack_line` 也都硬讀 `f["related"]`。所以 m1 要在寫入端、比對端、提示端各開第二條分支,spec 沒點出位置。
3. 具體陷阱:只把 `m1` 加進 `_DRIFT_KINDS`(spec〈種類登記〉寫的就這件事),m1 的表態就落進 `_drift_split_acked` 的「不是 bound」分支,只比 (路徑, 原文, 種類) 三元組——任何一個名稱的表態就把整行永久豁免,S4「新名稱觸發同一行 → 照列」直接失效。且 spec 沒說 m1 的「只列出」層走不走既有 `listed` 那條(`cmd_drift_check` 對 `listed` 呼叫 `_drift_split_acked`):走的話就踩上面這個陷阱;不走的話就是第二套印與去重。
4. 要修:spec 明寫(a)涵蓋語意:聯集還是只看最新;(b)`_drift_split_acked` 加一條以名稱集合比對的分支(不放進 `_DRIFT_BOUND_KINDS`),(c)m1 列出層與要處理層各走哪支比對與印出。

## F4 治理帳:kind 命名、hard、nodes 欄都偏離既有慣例,「只提醒兩週」的空轉偵測會看不到它
severity: major
blocking: 是
引句:「kind 依結果 `old-sentence-clean` / `old-sentence-warned` / `old-sentence-blocked` / `old-sentence-incomplete`(時間到或沒起點)」
file: `scripts/lumos:28296`(drift-check 擋下:`kind="blocked"`、`hard=True`、`nodes=`)、`scripts/lumos:28299`(`kind="warned"`)、`scripts/lumos:24632`(nodehome-check:kind 只有 passed/warned/blocked,清單放 `nodes`/`extra`)、`scripts/lumos:7186`(`_render_gov_nags` 只認 `kind=="warned"` 且非 hard)、`scripts/lumos:7256`(gov 去重鍵含 commit、nodes、gate、kind)、`scripts/lumos:6465`(spec-gate-run)
1. 「每次都記一筆、零筆也記」有先例(nodehome-check 每次記 passed、spec-gate-run 每次記),這一點與既有做法一致,不算問題。
2. 但 kind 欄的既有慣例是「結果詞」(blocked/warned/passed/skipped…),閘內的子功能靠 gate 名分,不把子功能名塞進 kind。spec 用 `old-sentence-*` 前綴,後果:①`gov --nags` 空轉偵測(專門抓「軟閘對同一篇連喊 N 天沒人理」)只看 kind=="warned",m1 的提醒永遠不進去——而 m1 兩週只提醒就是要靠它發現沒人理;②spec 沒說 block 事件的 `hard` 旗標:既有擋下都 `hard=True`(gov 顯示「硬擋」),漏設會顯示成軟。
3. 位置放 note 而不放 `nodes`/`extra`:既有做法是路徑清單進 `nodes`(上限 50)或 `extra`(nodehome-check 的 `pairs`、`notes`),note 只放一句摘要(既有 note 都是一行短句)。spec 把前 30 筆「路徑:行 名稱」塞進 note、截 2000 字。後果:`lumos gov <節點>` 的節點過濾看不到這些事件;`nodes` 是空,gov 的去重鍵(commit, nodes, gate, kind)會把同一個 HEAD 上不同推送範圍的多筆 m1 折成一筆(去重是讀時折,原始帳還在,所以 REVISIT 的 grep 仍數得到,但 `gov --stats` 的筆數會偏少)。
4. 要修:kind 沿用 `warned`/`blocked`/`passed`/`skipped`(兩週量準度另加 `extra={"check": "old-sentence", ...}` 或在 note 開頭固定前綴,REVISIT 的 grep 改比那個欄);block 事件 `hard=True`;路徑清單進 `nodes`/`extra`。

## F5 `_drift_config` 「多回一個值」照現在的早退結構會在沒寫 gate 時丟掉 old_sentence
severity: minor
blocking: 否
引句:「`_drift_config` 擴充,多回 `old_sentence` 的值(同一支讀同一個鍵,不另開第二支」
file: `scripts/lumos:28196`(`_drift_config` 六個 return,全是三元組)、`scripts/lumos:28254`、`scripts/lumos:28420`(兩個呼叫端)
1. 既有函式在「沒有 drift_check」「不是物件」「gate 是 null 或沒寫」「gate 值不合法」各自早退(`return _DRIFT_DEFAULT_GATE, ..., True`),之後才回 gate。設定 `{"drift_check": {"old_sentence": "block"}}`(沒寫 gate)在 `g is None` 那個早退就回了,`old_sentence` 完全沒被讀,靜默降回 warn——方向是放寬。
2. 三元組變四元組要同時改兩個呼叫端(28254、28420);spec 沒列 doctor 那個呼叫端,doctor 的「開關不是 block 時講一聲」也沒涵蓋 old_sentence。
3. 「同一支讀同一個鍵」跟既有的 `explicit` 擴充先例一致(這點沒問題);問題只在早退結構。要修:spec 寫明先讀 `old_sentence` 再判 gate 的早退,並在 S3 加「只寫 old_sentence、沒寫 gate」一組。

## F6 m1 自己一條輸出、判不了、回傳碼通道,並第二次建整份圖譜樹
severity: minor
blocking: 否
引句:「`m1` 的要處理不進既有 `must` 清單,自己印、自己記帳;check 的回傳碼」
file: `scripts/lumos:26572`(core 內 `_drift_tree_env` 建一次,傳給 `_drift_probe_check`)、`scripts/lumos:27142`(probe 回 (must, listed, unknown) 併進 core 的三元組)、`scripts/lumos:28276`(`_drift_report_must`:標題、判不了的 `LUMOS_SKIP_DRIFT_CHECK` 提示、改法、ack 行、記帳)
1. 「判定另開函式、不進 core」這條方向本身合理(core 也給考試與歷史重放用,probe 進 core 就是已經改過那份噪音基準);但既有先例是新判定回 (must, listed, unknown) 併進同一條輸出通道。spec 讓 m1 回 (要處理, 只列出, 剖不動支數, 跑完沒),另外自己印、自己記帳、自己取回傳碼:`_drift_report_must` 的標題句、block 模式「判不了算要處理」那段提示(含 `LUMOS_SKIP_DRIFT_CHECK=1 git push`)、hint、ack 行都得重寫一份,或讓 m1 的判不了走 `_drift_report_must`(它吃的是 gate 的 mode,不是 old_sentence 的 mode,標題會寫成 `drift_check.gate=warn`)。spec〈提示〉說要改 `_drift_report_must` 那行通用 ack 句,但 m1 不進 must,那處改動沒有作用對象,也沒說 m1 的 ack 行由誰印。
2. 判定函式簽名 `(root, base, tip, vault_rel, deadline)` 沒有 `tenv`;需要的筆記全文與 about_code(判「家」)要在函式內再呼叫一次 `_drift_tree_env`(整份圖譜再讀一遍),既有 probe 是接收 core 建好的 `tenv`。共用 60 秒預算下(spec 自己引 rtb 首推前段用掉 67 秒),多一次整份讀取是實在的成本。要修:簽名收 `tenv`(cmd_drift_check 在 core 之後自己再建一次的話,至少寫明並算進預算),並指定輸出通道由哪支印。

## F7 種類登記:「排除 m1」是逐處補丁,專案已有子集常數的先例
severity: minor
blocking: 否
引句:「`drift scan` 與 doctor 逐種類計數的迴圈排除 `m1`」
file: `scripts/lumos:26257`(`_DRIFT_FIX_KINDS` 子集常數)、`scripts/lumos:28357`、`scripts/lumos:28360`(scan 印出迴圈直接用 `_DRIFT_KINDS`,單獨 `k != "probe"`)、`scripts/lumos:28401`(doctor 寫死 `("c1","c2","c3","c4","c5")`)、`scripts/lumos:27484`、`scripts/lumos:37584`(ack 的 choices)
1. 既有做法是「全部種類」與「各自的子集常數」分開(`_DRIFT_FIX_KINDS`);scan 的迴圈是全集加一個 `!= "probe"` 的臨時排除。spec 再加一個 `!= "m1"` 就是第二個臨時排除。scan 印出迴圈(28360)漏排一處就會用 `_DRIFT_KIND_NAMES["m1"]` 印出空的「[m1] …:0」或計數行多一格。
2. 要修:spec 指定新增 `_DRIFT_SCAN_KINDS`(或同等)子集常數並列出要改的迴圈,ack 的 choices、`_drift_ack_args_err` 繼續用全集。

## F8 字眼表「逐字搬」與引用 `NEG_LEXICONS["zh"]` 兩種讀法都有後果
severity: minor
blocking: 否
引句:「字眼表照實驗程式 `HIST_WORDS` 逐字搬」
file: `scripts/lumos:4277`(`NEG_LEXICONS`,tuple)、`scripts/lumos:2975`、`scripts/lumos:4293`(另兩處消費者)
1. spec 同段又說「`NEG_LEXICONS["zh"]` 常數,不讀專案的 neg_lexicon 設定」。實驗程式的 `HIST_WORDS` 是 `tuple(LM.NEG_LEXICONS["zh"]) + (…)`。實作有兩種讀法:①在 m1 的模組常數裡再抄一份 25 個詞(第二份,`NEG_LEXICONS["zh"]` 之後增減兩邊不同步);②用 `tuple(NEG_LEXICONS["zh"]) + 額外詞` 引用——那 `NEG_LEXICONS["zh"]` 被別的功能(符號檢查)調整時,m1 的判準跟著變、實驗量到的成績(P4r2 那份數字)無聲失效。
2. 要修:spec 選一種並寫明;選引用就在測試釘「`NEG_LEXICONS["zh"]` 目前的內容」一起翻紅(S2 只說「逐項釘」新增的部分)。

## 六組核心裁定從架構鏡頭的判定
- A(判定另開函式、m1 不進 must):方向做得出來且對——core 給考試與歷史重放共用;問題在通道與 tenv 重建(F6)、表態與列出層的接法(F3)。
- B(兩個開關控制流、`_drift_config` 擴充):擴充同一支函式與既有 `explicit` 先例一致;早退結構會丟值(F5)。gate=off 只跳 c1–c5/probe 可行:`cmd_drift_check` 現有 `mode == "off"` 直接 `return 0`,要改成往下走。
- C(表態名稱集合):做不出唯一實作,見 F3。
- D(時間到 warn/block):兩種處理各自做得出來,但 block 那條要「判不了算要處理」得複製 `_drift_report_must` 的提示(F6)。
- E(三類消失判準與終點剖不動):見 F1;剖不動的退回法與既有 `_drift_py_def_re` 不同。
- F(字眼表 P4r2):見 F8;撤除節 ①② 用既有 `_notelines_regions`/`_visible_lines` 分區,與 `_probe_lines` 同一套,沒有第二種做法(但 probe 不掃表格行、m1 沒說,未列為 finding)。

## ★INVARIANT★ 合約
Systems/guard-kill 兩條(rc 優先序、`--json` 純度)只管 `guard kill`,這份設計不動它,不影響。Systems/lumos-cli-write 與 Systems/存量漂移守衛在此 clone 無 ★INVARIANT★ 行(grep 為空),無可判。

## 已讀,無 finding
〈範圍〉〈回退〉〈實務隱患〉〈誠實界線〉:已讀;與既有做法不衝突的部分(每次記帳有 nodehome-check/spec-gate-run 先例、`.lumos/config.json` 讀被推送頂端的版本、`_esc_clean` 與 `_drift_one_line` 沿用)已核對屬實。

最高等級:major;blocking 共 4 條
