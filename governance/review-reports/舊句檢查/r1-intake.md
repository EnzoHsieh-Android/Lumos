preflight-4: ran

# r1 收貨紀錄(舊句檢查設計審)

## 首輪前掃(四類清單)

前掃員(sonnet 5.5,只讀)報告原樣存為 `r1-preflight.md`。①未定義詞、②壞引用、③範圍矛盾與存在類命中直接修計劃真檔;④語意類命中修真檔並逐條留改前→改後如下;動到核心裁定的 8 條升級為正式 finding,交第一輪席位審(派工詞點名)。

| 前掃條 | 改前 | 改後 | 核心裁定? |
|---|---|---|---|
| ①-1 | 範圍寫「drift check(與 scan 的推送範圍模式)」 | 刪掉 scan;範圍明寫 scan、健檢、考試都不跑 m1 | 否 |
| ①-2 | 沒說 m1 要處理進不進既有 must | m1 要處理不進 must,自己印、自己記帳,回傳碼取大 | 是(分層/模式)→ 核心 A |
| ①-3 | 沒定義起點與空樹起點 | 用 `_note_audit_resolve` 回的起點(已截上線點);空樹時不判並印明;誠實界線補上線點之前看不到 | 否 |
| ①-4 | 「既有否定詞表」沒指定哪份 | 指定 `NEG_LEXICONS["zh"]` 常數,不讀專案設定 | 否 |
| ②-2 | REVISIT grep `"m1"`;工具鏈沒接 drift check | grep 同時比 gate 與 kind;範圍加〈前置〉:推送閘接漂移檢查先推 | 否 |
| ②-3 | 「c1–c5 的 gate」 | 「c1–c5 與 probe」 | 否 |
| ③-1 | 「既有 gate 不管 m1」,但 gate=off 在 core 前就回 0,且 _drift_report_must 只吃一個 mode | 控制流寫明:gate=off 只跳 c1–c5/probe;m1 自己的 mode;回傳碼取大;S3 驗四種組合 | 是 → 核心 B |
| ③-2 | 一行一筆 vs 表態綁單一名稱 | 一筆帶名稱集合;--name 可重複;集合全涵蓋才算已表態 | 是 → 核心 C |
| ③-3 | 時間到「不算要處理」與既有「判不了算要處理」相反、沒說通道 | warn 時只印;block 時照既有算要處理;誠實界線寫明 | 是 → 核心 D |
| ③-4 | 終點剖不動時名稱看似消失 | 終點剖不動的檔改用文字比對,找得到就不當消失 | 是(判法)→ 核心 E |
| ③-5 | 旗標、路徑的「消失」判準沒寫 | 三類各自判準寫明 | 是(判法)→ 核心 E |
| ④-1 | m1 放進 `_drift_check_core` 一個分支 | 另開判定函式,core/考試/歷史重放不動;回退改寫 | 是 → 核心 A |
| ④-2 | `_drift_fix_hint` 單一產生處(簽名沒名稱;通用 ack 行缺 --name;去重鍵沒名稱) | 加名稱參數;通用 ack 行與去重鍵同一處產生 | 否 |
| ④-3 | 表態比對三元組、`_DRIFT_KINDS`/`_DRIFT_KIND_NAMES` 沒列 | 兩常數加 m1;scan/doctor 迴圈排除;--name 必填/禁用;ack 不驗行寫進誠實界線 | 是 → 核心 C |
| ④-4 | 共用預算,沒寫檢查點 | 每剖一支、每掃一篇前檢查;剖檔不可中斷最壞多一支 | 否 |
| ④-5 | `.lumos/config.json` 讀法沒說擴 `_drift_config` | 擴 `_drift_config` 多回 old_sentence;實務隱患引同提交關掉的既有 RULE | 是 → 核心 B |
| ④-6 | 字眼表=否定詞表+12 詞(含單字「叫」),與實驗量成績的表不同 | 照實驗 `HIST_WORDS` 逐字搬 + 詞組「當時叫、擴成、改名為」(不收單字叫);撤除節加節內引用區塊;新表另跑實驗(P4r2)出成績 | 是(判法)→ 核心 F |
| ④-7 | 「沿用治理事件」 | 寫明是新寫入點:每次跑 m1 就記(零筆也記),kind 依結果四種、note 截 2000 字 | 否 |
| ④-8 | `_esc_clean` 屬實;--name 沒一行檢查 | --name 走 `_drift_one_line` | 否 |
| ④-9 | 分區與圍欄屬實 | 不改 | 否 |
| ④-10 | 抽定義沒引用既有 `_drift_py_names`/`_drift_probe_is_py` | PRIOR-ART 與做法 1 改成擴充既有,不另寫 | 否 |
| ④-11 | 同 ②-2 | 同 ②-2 | 否 |
| ④-12 | 快取在 `--git-dir`、沒上限 | `--git-common-dir`;上限 20000 筆、丟最久沒用;原子寫 | 否 |

核心交審清單(派工詞點名要席位驗):A 判定另開函式、m1 不進 must(①-2、④-1);B 兩個開關的控制流與 `_drift_config` 擴充(③-1、④-5);C 表態名稱集合(③-2、④-3);D 時間到 warn/block 兩種處理(③-3);E 三類消失判準與終點剖不動的文字比對(③-4、③-5);F 字眼表 P4r2(④-6)。

## 席位收貨

- 凍結材料:`r1-snapshot.md`(111 行,前掃修正後的版本,sha256 見 `r1-sha.txt`);7 席:正確性 opus;邊界、接手、併發、回滾、架構對齊 sonnet 5.5;外家否決 Codex(唯讀沙盒,stdout 另存)。報告在編排者暫存 `os-r1/`,檔案時間 04:15–05:08,都在派工單(04:13)之後;clone-ns 的 reflog 只有編排者自己的提交。
- report-normalize 7 份都已是正規化格式;quote-check 7 份對 r1-snapshot.md 全數錨定。
- 發現 63 條(機器數各報告的 F 標題與 severity 行):正確性 14、邊界 12、接手 13、併發 5、回滾 5、架構對齊 8、外家否決 6;major 24 條,也就是 blocking 的那 24 條(正確性 F1–F5、邊界 F1 F2 F4、接手 F1 F2 F3 F4 F8、併發 F1、架構對齊 F1–F4、外家否決 F1–F6;回滾 0)。
- 多席獨立報到的同一件:表態提示 `--name --旗標` 照貼 rc 2(正確性 F1、邊界 F2、接手 F1);快取鍵沒有抽法版本、剖不動要不要快取(正確性 F3、接手 F8、併發 F2、架構對齊 F2);共用 60 秒預算讓 block 被前段拖到必擋、校準期量不到大推送(正確性 F5、外家否決 F4、回滾 F4、邊界 F11);`_drift_config` 早退丟掉 old_sentence、三處解包(邊界 F4、架構對齊 F5、回滾 F1、接手 F6);名稱集合涵蓋是聯集還是只看最新(正確性 F11、接手 F7、架構對齊 F3、回滾 F2);檔名消失判準(正確性 F7、邊界 F1、接手 F10);剖不動的文字退路太窄(正確性 F13、外家否決 F6、架構對齊 F1);抽定義跟參考實作不同(正確性 F6、邊界 F9);切句與撤除字樣細節(正確性 F8、邊界 F8、接手 F9);沒起點時的回傳碼與說法(正確性 F12、邊界 F10、接手 F5、回滾 F4);「大小寫混合」沒定義(邊界 F6、接手 F11);治理帳 kind、hard、欄位(架構對齊 F4、回滾 F3、接手 F5、外家否決 F3);通用 ack 句碰不到 m1(正確性 F10、接手 F7、架構對齊 F6);呼叫點在早退之後(併發 F5、接手 F6)。以上多席一致或附了程式位置與實測,直接處置,不開辯方。

## 判讀

- **照字面實作會做錯的一律折**:表態提示、撤除節②、快取鍵與讀法、程式檔範圍、預算、`_drift_config`、表態涵蓋、治理帳、輸出通道,照字面做都會做出錯的東西或兩種都合字面的實作,全折。
- **編排者裁定照做**:①撤除節②收窄成同一行要有範圍宣告字(下面、以下、本節、這一節、整篇、之後);②`m1` 自己 30 秒;③快取鍵帶抽法版本與 Python 主次版本、批次讀、剖不動不寫快取、放 `~/.cache/lumos/`;④程式檔範圍逐字抄參考實作排除清單、驗收以參考實作為準;⑤整字 = ASCII 識別字邊界;⑥`--name=`;⑦跟 `_DriftProbeTree` 能共用的共用、不能的寫明差在哪;⑧kind 用既有結果詞加 `extra.check`;⑨準度量法寫死、REVISIT 的兩項量測走參考實作子命令;⑩形狀過濾自己量。
- **快取挑哪一種**:架構對齊席點名的兩種是行程內字典與 `~/.cache/lumos/<名>/` 持久快取。挑持久那種:推送前掛鉤每次是新行程,行程內字典等於沒快取;持久那種有現成的信任目錄、唯一暫存名原子寫、mtime 保鮮與開跑前清舊檔的先例。一個 blob 一支檔,讀不寫、不做「最久沒用到」,併發席的 lost-update 與固定暫存名問題、接手席的上限不可測一起消失(拿掉 20000 筆上限)。
- **形狀過濾(外家否決 F1)**:量了才決定。拿掉它,rtb 182 個提交多 43 筆(要處理 +8)、工具鏈 300 個提交多 23 筆(要處理 +2),66 筆逐筆看:觸發名都是被刪的測試輔助函式、資料類別欄位、區域方法(`investigation`、`locked`、`env`、`opener`、`busy`、`pending`、`stamp`),筆記裡講的是同一個英文字或路徑片段,0 筆真舊句。拿掉會用誤報吃光 60% 的準度門檻,換不到任何一筆真的,所以附理由接受;外家席要的另一條路「明確縮小承諾、另量漏報」照做:〈誠實界線〉寫明哪幾類名稱永遠不查(引外家席的 3.6%/10.1%),revisit 子命令兩週後再數一次。
- **歷史字眼的漏報(外家否決 F2)**:不改判法(把字眼綁到語法關係是另一個實驗),但把量漏報接上電:revisit 子命令對兩週每一組範圍都重跑「關掉字眼過濾」,抽判多出來的,真舊句達三分之一以上就不轉擋(RETIRE-IF ④)。折。
- **撤除節②收窄的量測**:工具鏈圖譜只因②不看的行 603 行/10 篇 → 163 行/2 篇(剩 `Systems/記憶過期清掃` 107 行真宣告、`Projects/主session鏡頭利用率_計劃` 56 行誤觸發);rtb 0 → 0;9 題、rtb 182、工具鏈 300 跟 P4r2 逐筆相同;對照組誤報第 4 筆照樣放過。收窄的代價:真宣告沒帶範圍字的(`Verification/2026-08-22_受波及合約測試真跑閘落地` 15 行)現在照掃,方向是多列。
- **編排者自查多出的一條**:計劃原本想直接拿 `_DriftNames` 先篩候選名稱,但它切詞用 `\w+`,Python 的 `\w` 含中文字,「改了foo_bar函式」切成一整段、`foo_bar` 查不到,先篩會把該列的名稱篩掉(機械重現見下)。改成照它的做法、切詞用 ASCII `[A-Za-z0-9_]+`,寫進計劃。
- **接受的三條**:外家否決 F1(major,理由見上,有數據);邊界 F6(`Result` 這種首字大寫單字算大小寫混合:照參考實作才對得上驗收數字,中文圖譜兩份資料沒踩到,英文圖譜的風險寫進〈誠實界線〉);邊界 F7(撤除行的否定只認「未」緊接:照參考實作,兩份圖譜帶「未被/沒有/撤除條件」的撤除行量到 0 行,寫進〈誠實界線〉並在 REVISIT 再數)。
- 不成立:無。

## 機械重現(在 clone-ns 與編排者暫存 `osfold/` 跑,只讀;對照腳本 `osfold/variant.py`、`osfold/mech.py`;結果照抄)

| 發現 | 做法 | 結果 |
|---|---|---|
| 正確性-F1 | argparse `--name` append:餵 `--name --restore --reason x` 與 `--name=--restore --reason x` | HIT:前者 SystemExit 2,後者拿到 `['--restore']` |
| 邊界-F2 | argparse `--name` append:餵 `--name --restore --reason x` 與 `--name=--restore --reason x` | HIT:前者 SystemExit 2,後者拿到 `['--restore']` |
| 接手-F1 | argparse `--name` append:餵 `--name --restore --reason x` 與 `--name=--restore --reason x` | HIT:前者 SystemExit 2,後者拿到 `['--restore']` |
| 正確性-F2 | 參考實作 `ret_full2` 減 `ret_full`,數現在工具鏈與 rtb 圖譜只因②不看的非空行;再數收窄版 | HIT:工具鏈 603 行/10 篇(rtb 0),收窄後 163 行/2 篇 |
| 正確性-F3 | 讀快照〈做法〉1 快取句與既有 `_lens_cache_path`、`_FILTER_PROBE_SCHEMA` | HIT:快照鍵只有 blob 雜湊;既有兩種持久快取的鍵都帶 schema |
| 接手-F8 | 讀快照〈做法〉1 快取句與既有 `_lens_cache_path`、`_FILTER_PROBE_SCHEMA` | HIT:快照鍵只有 blob 雜湊;既有兩種持久快取的鍵都帶 schema |
| 併發-F2 | 讀快照〈做法〉1 快取句與既有 `_lens_cache_path`、`_FILTER_PROBE_SCHEMA` | HIT:快照鍵只有 blob 雜湊;既有兩種持久快取的鍵都帶 schema |
| 架構對齊-F2 | 讀快照〈做法〉1 快取句與既有 `_lens_cache_path`、`_FILTER_PROBE_SCHEMA` | HIT:快照鍵只有 blob 雜湊;既有兩種持久快取的鍵都帶 schema |
| 正確性-F4 | 重跑正確性席比對器 `osr1out/cmp.py . scope` | HIT:工具鏈 300 個提交 1 → 6 筆、要處理 0 → 1 |
| 正確性-F5 | 讀 `cmd_drift_check`:截止時間只在呼叫 core 時算一次;〈實務隱患〉引的 67 秒 | HIT:m1 照快照會吃同一個截止時間,gate 的值會經由預算改變 m1 |
| 外家否決-F4 | 讀 `cmd_drift_check`:截止時間只在呼叫 core 時算一次;〈實務隱患〉引的 67 秒 | HIT:m1 照快照會吃同一個截止時間,gate 的值會經由預算改變 m1 |
| 正確性-F6 | `_drift_py_names` 餵 `A_ONE, B_TWO = 1, 2`、模組層 try/if 指派、類別裡 `field_x: int` | HIT:指派集合是空的;`osr1out/cmp.py . defs` 歷史重放 0 差別 |
| 邊界-F9 | `_drift_py_names` 餵 `A_ONE, B_TWO = 1, 2`、模組層 try/if 指派、類別裡 `field_x: int` | HIT:指派集合是空的;`osr1out/cmp.py . defs` 歷史重放 0 差別 |
| 正確性-F7 | 讀參考實作 `disappeared` 路徑段 | HIT:檔名要 `bn not in tip_bases`,快照沒寫 |
| 邊界-F1 | 讀參考實作 `disappeared` 路徑段 | HIT:檔名要 `bn not in tip_bases`,快照沒寫 |
| 接手-F10 | 讀參考實作 `disappeared` 路徑段 | HIT:檔名要 `bn not in tip_bases`,快照沒寫 |
| 正確性-F8 | 讀參考實作 `RETIRE_WORDS`、`NOT_YET`、切句字元 | HIT:多 `Superseded`,切 `。;；!?！？`,快照只寫句號分號 |
| 接手-F9 | 讀參考實作 `RETIRE_WORDS`、`NOT_YET`、切句字元 | HIT:多 `Superseded`,切 `。;；!?！？`,快照只寫句號分號 |
| 正確性-F9 | 讀參考實作 `homes_any` | HIT:起點與終點兩棵樹、新舊路徑、所有程式檔 |
| 正確性-F10 | 讀 `_drift_report_must` 的通用 ack 句迴圈 | HIT:只對 must 的種類印;另 core 內建 `tenv`、不回傳 |
| 架構對齊-F6 | 讀 `_drift_report_must` 的通用 ack 句迴圈 | HIT:只對 must 的種類印;另 core 內建 `tenv`、不回傳 |
| 正確性-F11 | 讀 `_drift_split_acked` | HIT:bound 種類只看 seq 最大那批;非 bound 分支只比三元組、不看名稱 |
| 接手-F7 | 讀 `_drift_split_acked` | HIT:bound 種類只看 seq 最大那批;非 bound 分支只比三元組、不看名稱 |
| 架構對齊-F3 | 讀 `_drift_split_acked` | HIT:bound 種類只看 seq 最大那批;非 bound 分支只比三元組、不看名稱 |
| 回滾-F2 | 讀 `_drift_split_acked` | HIT:bound 種類只看 seq 最大那批;非 bound 分支只比三元組、不看名稱 |
| 正確性-F12 | 讀 `_note_audit_resolve` 回傳與 `_nodehome_clamp_base` | HIT:只有空樹起點回 None;有上線點標記時空樹被換成上線點 |
| 邊界-F10 | 讀 `_note_audit_resolve` 回傳與 `_nodehome_clamp_base` | HIT:只有空樹起點回 None;有上線點標記時空樹被換成上線點 |
| 接手-F5 | 讀 `_note_audit_resolve` 回傳與 `_nodehome_clamp_base` | HIT:只有空樹起點回 None;有上線點標記時空樹被換成上線點 |
| 回滾-F4 | 讀 `_note_audit_resolve` 回傳與 `_nodehome_clamp_base` | HIT:只有空樹起點回 None;有上線點標記時空樹被換成上線點 |
| 正確性-F13 | `_drift_py_def_re("old_name", False)` 與快照字面 `名 =`、`"--旗標"` 對 `old_name: Callable = handler`、`add_argument('--foo')` | HIT:既有正則認得 AnnAssign;字面兩樣都認不到 |
| 外家否決-F6 | `_drift_py_def_re("old_name", False)` 與快照字面 `名 =`、`"--旗標"` 對 `old_name: Callable = handler`、`add_argument('--foo')` | HIT:既有正則認得 AnnAssign;字面兩樣都認不到 |
| 正確性-F14 | 讀 `Systems/存量漂移守衛` 摘要的 RULE 行 | HIT:「預設改 block 要三條全過」,沒有 `[confirmed:]` |
| 邊界-F3 | 讀 `_drift_print_hints` | HIT:每條 `_esc_clean(x, 300)` |
| 邊界-F4 | `_drift_config(b'{"drift_check": {"old_sentence": "block"}}')`;grep 解包處 | HIT:在 `g is None` 早退回 `('warn', [], True)`;解包三處(check、doctor、測試) |
| 架構對齊-F5 | `_drift_config(b'{"drift_check": {"old_sentence": "block"}}')`;grep 解包處 | HIT:在 `g is None` 早退回 `('warn', [], True)`;解包三處(check、doctor、測試) |
| 回滾-F1 | `_drift_config(b'{"drift_check": {"old_sentence": "block"}}')`;grep 解包處 | HIT:在 `g is None` 早退回 `('warn', [], True)`;解包三處(check、doctor、測試) |
| 邊界-F5 | 位元組 `\xe9t\xe9 = 1` 用 strict utf-8-sig 解與用 `_drift_decode` 解 | HIT:strict 丟 UnicodeDecodeError;`_drift_decode` 換字元不丟 |
| 邊界-F6 | `_shape_ok` 對 `Result`、`main`、`lumos`、`pre-push` | HIT:`[True, False, False, False]` |
| 接手-F11 | `_shape_ok` 對 `Result`、`main`、`lumos`、`pre-push` | HIT:`[True, False, False, False]` |
| 邊界-F7 | `_is_banner` 對「未被取代」「沒有作廢」「撤除條件」「尚未撤除」;兩份圖譜數這類撤除行 | HIT:`[True, True, True, False]`;圖譜裡這類行工具鏈 0、rtb 0 |
| 邊界-F8 | `_clause_has_hist` 對巢狀括號句與英文句點句 | HIT:兩句都判有歷史字眼(不列),快照沒寫 |
| 邊界-F11 | 讀快照〈治理帳〉零筆也記;交替正則時間用邊界席實測 | HIT:純文件推送也會記;時間數字採信,未重跑 |
| 邊界-F12 | `_notelines_regions` 餵帶 BOM 與去掉 BOM 的同一篇 | HIT:帶 BOM 整篇都是 body(摘要與 about_code 認不到),去掉後正常 |
| 接手-F2 | `\bfoo_bar\b` 與參考實作 `_mk_rx` 對「改了foo_bar函式」 | HIT:`\b` 對不上,`_mk_rx` 對得上 |
| 接手-F3 | 讀 `_gate_event`:沒給 head_sha 就跑 `rev-parse HEAD`;既有 drift-check 兩處呼叫都沒給;快照帳只留前 30 筆位置 | HIT |
| 外家否決-F3 | 讀 `_gate_event`:沒給 head_sha 就跑 `rev-parse HEAD`;既有 drift-check 兩處呼叫都沒給;快照帳只留前 30 筆位置 | HIT |
| 接手-F4 | 讀快照〈做法〉與〈誠實界線〉 | HIT:沒有關掉字眼過濾的方法,也沒有②豁免行數的輸出 |
| 接手-F6 | 讀 `cmd_drift_check` | HIT:gate=off、must 與 unknown 皆空、`_drift_report_must` 三處提早回傳 |
| 併發-F5 | 讀 `cmd_drift_check` | HIT:gate=off、must 與 unknown 皆空、`_drift_report_must` 三處提早回傳 |
| 接手-F12 | 讀快照 | HIT:發現行字樣、讀終點樹還是工作目錄都沒寫 |
| 接手-F13 | 讀快照 | HIT:發現行字樣、讀終點樹還是工作目錄都沒寫 |
| 併發-F1 | 讀 `_drift_probe_is_py(p, txt)` 簽名與 `_drift_cat`、`_nodehome_cat_blobs` | HIT:快照沒寫編號從哪來、要不要批次讀;既有批次讀寫法就在 `_drift_cat` |
| 併發-F3 | 讀 `_write_lf` 的固定暫存名事故註解 | HIT:快照只寫「走暫存檔」,沒寫唯一名與何時寫 |
| 併發-F4 | 採信席位的剖檔記憶體實測(11.5 MB → 3.2 GB),讀 `_nodehome_cat_blobs_capped` | HIT(數字未重跑) |
| 回滾-F3 | 讀「閘的動作」統計與 `_render_gov_nags` | HIT:只認 kind == blocked 與 warned,`old-sentence-*` 兩邊都看不到 |
| 架構對齊-F4 | 讀「閘的動作」統計與 `_render_gov_nags` | HIT:只認 kind == blocked 與 warned,`old-sentence-*` 兩邊都看不到 |
| 回滾-F5 | 讀 `_drift_scan_print` 與 `_DRIFT_FIX_KINDS` | HIT:scan 直接迭代 `_DRIFT_KINDS` 只排除 probe;子集常數先例在 |
| 架構對齊-F7 | 讀 `_drift_scan_print` 與 `_DRIFT_FIX_KINDS` | HIT:scan 直接迭代 `_DRIFT_KINDS` 只排除 probe;子集常數先例在 |
| 架構對齊-F1 | 讀 `_DriftProbeTree.corpus` 與 `_defines` | HIT:語料用 `_drift_probe_code_path`、分測試與非測試;退路用 `_drift_py_def_re` |
| 架構對齊-F8 | 讀參考實作 `HIST_WORDS` 定義 | HIT:`tuple(LM.NEG_LEXICONS["zh"]) + (…)`,快照兩種讀法都說得通 |
| 外家否決-F1 | 參考實作把 `_shape_ok` 換成恆真,跑 9 題、rtb 182、工具鏈 300,跟基線逐筆比 | HIT(過濾確實排除一類名稱):rtb 91 → 134(要處理 20 → 28)、工具鏈 1 → 24(要處理 0 → 2)、9 題與 13 題不變;多出的 66 筆逐筆看 0 筆真 |
| 外家否決-F2 | `_clause_has_hist` 對「沒有參數時呼叫 old_handler」 | HIT:判有歷史字眼、不列 |
| 外家否決-F5 | `_esc_clean("src/x;rm -rf $(y).py")` 與 `_drift_sh("--name=src/x;y.py")` | HIT:`_esc_clean` 原樣;`_drift_sh` 加單引號 |

表外(不對應單一發現):
- 編排者自查(先篩):`re.findall(r"\w+", "改了foo_bar函式")` → HIT:`['改了foo_bar函式']`,直接用 `_DriftNames` 會篩掉 `foo_bar`
- 撤除節②收窄驗收:參考實作 P4r2 換成收窄版②,跑 9 題、rtb 182、工具鏈 300 → 跟 P4r2 逐筆相同;對照組誤報第 4 筆照樣放過
- 其他程式檔副檔名清單:參考實作的 `TEXT_EXTS` 換成既有 `_nodehome_code_kind`,同上三組 → 跟 P4r2 逐筆相同

## 處置

- **折入(60 條)**:正確性-F1、正確性-F2、正確性-F3、正確性-F4、正確性-F5、正確性-F6、正確性-F7、正確性-F8、正確性-F9、正確性-F10、正確性-F11、正確性-F12、正確性-F13、正確性-F14;邊界-F1、邊界-F2、邊界-F3、邊界-F4、邊界-F5、邊界-F8、邊界-F9、邊界-F10、邊界-F11、邊界-F12;接手-F1、接手-F2、接手-F3、接手-F4、接手-F5、接手-F6、接手-F7、接手-F8、接手-F9、接手-F10、接手-F11、接手-F12、接手-F13;併發-F1、併發-F2、併發-F3、併發-F4、併發-F5;回滾-F1、回滾-F2、回滾-F3、回滾-F4、回滾-F5;架構對齊-F1、架構對齊-F2、架構對齊-F3、架構對齊-F4、架構對齊-F5、架構對齊-F6、架構對齊-F7、架構對齊-F8;外家否決-F2、外家否決-F3、外家否決-F4、外家否決-F5、外家否決-F6。落點都在計劃〈依據〉的 r1 量測、〈做法〉1–4、〈條款〉S1–S7(新增 S7)、〈回退〉、〈實務隱患〉、〈誠實界線〉。
- **接受(3 條,附理由)**:外家否決-F1(major:拿掉形狀過濾多 66 筆、0 筆真;改成明寫不查哪幾類並在 REVISIT 再數);邊界-F6(minor:大小寫混合照參考實作,驗收數字靠它,英文圖譜風險寫進〈誠實界線〉);邊界-F7(minor:否定只認緊接照參考實作,兩份圖譜量到 0 行,寫進〈誠實界線〉並在 REVISIT 再數)。
- **不成立**:無。

## 鏡像核對

鏡像核對員(只讀)讀折入後的計劃,報告在編排者暫存 `os-r1-mirror.md`:17 條命中(折入只做一部分 3、前後說法打架 9、條款可測性 5)。編號照報告的順序記為 鏡像-F1 到 鏡像-F17。17 條全補進計劃,不成立 0 條。上面〈處置〉那句「〈條款〉S1–S7(新增 S7)」以本節為準:條款現在是 S1–S13。

| id | 報告位置 | 命中 | 處理 |
|---|---|---|---|
| 鏡像-F1 | 一-1 | 邊界-F11 只接了「沒程式改動就短路」,名稱多時沒分批 | 補了:先篩後超過 200 個名稱每 200 個一批、每批前看時間(〈做法〉1 時間、〈做法〉2 名稱先篩、[S10]) |
| 鏡像-F2 | 一-2 | 回滾-F4:block 下空樹起點放行、時間到卻擋,取捨沒進界線 | 補了:〈誠實界線〉新增一條,寫明何時會出現、為什麼不擋、CI 有主線可比是後盾、REVISIT 看 skipped-no-base 次數 |
| 鏡像-F3 | 一-3 | 架構對齊-F6:m1 再讀一次整份圖譜沒交代 | 補了:〈做法〉1 讀取寫明不共用 core 的 tenv(改簽名會動考試與重放)、多讀一次算進 m1 的 30 秒,git 行程數改成 m1 自己的口徑 |
| 鏡像-F4 | 二-1 | 驗收以參考實作為準,但 repo 裡的參考實作沒有收窄與 revisit | 補了:實驗程式加候選 P4r3(收窄版②)、P4r3c、P4r3s 與 `revisit` 子命令,P4r、P4r2 原樣;重跑確認數字寫進〈依據〉;家筆記 `Systems/存量漂移守衛` 正文補一段 P4r3 是什麼 |
| 鏡像-F5 | 二-2 | S5「不讀內容」對上沒副檔名檔每次要讀首行 | 補了:〈做法〉1 讀取寫明沒副檔名檔每次讀、快取不存「不是 Python」;[S5] 限定 `.py` blob |
| 鏡像-F6 | 二-3 | S3「gate 不改變回傳碼」兩種讀法、四種組合沒列 | 補了:[S3] 寫明只管 rc_m1、整支回 max,列出固定情境下的四種組合與預期 rc |
| 鏡像-F7 | 二-4 | 〈範圍〉⑤⑥還是舊說法 | 補了:⑤加「沒有起點也記一筆」,⑥鍵寫成內容編號加抽法版本加 Python 主次版本,⑦改成已收進實驗程式 |
| 鏡像-F8 | 二-5 | 「起點是 None」把兩條路徑混在一起 | 補了:〈做法〉1 起點分三種(resolve 回整數 → m1 不跑;空樹 → 回 None、不判;其他 → 照判),寫明空樹何時出現、上線點標記何時截 |
| 鏡像-F9 | 二-6 | state 值集合沒寫死 | 補了:done、timeout、git-failed、unreadable、no-base 五種(另有不記帳的 no-candidates);〈做法〉4 分母只收 done,其餘各自另數 |
| 鏡像-F10 | 二-7 | 「再兩個月」沒有 REVISIT、10-14 那行沒列要數的東西、前置沒接上時日期寫死 | 補了:加 `REVISIT:2026-12-14`;10-14 那行列出 revisit 子命令的四樣,並寫明前置沒接上就把日期改成接上後滿兩週 |
| 鏡像-F11 | 二-8 | 〈回退〉漏 `_drift_scan_print`、新常數、doctor 那行 | 補了 |
| 鏡像-F12 | 二-9 | 效能數字口徑沒標 | 補了:〈實務隱患〉效能分成整次判定與只算剖檔兩個口徑,各標誰量的 |
| 鏡像-F13 | 三-S1 | 一條綁約 10 個行為 | 補了:S1 只留消失判定,拆出 [S8] 抽定義、[S9] 路徑與形狀過濾、[S10] 整字與先篩、[S11] 空樹、剖不動、太大、讀不出,各一支測試 |
| 鏡像-F14 | 三-S3 | 同鏡像-F6 | 補了(同鏡像-F6) |
| 鏡像-F15 | 三-S5 | 沒副檔名檔會紅;換 Python 版本怎麼注入沒說 | 補了:[S5] 排除沒副檔名檔,Python 版本由一支小函式取、測試換掉它,時間到靠調小 `_DRIFT_M1_BUDGET_SEC` 造 |
| 鏡像-F16 | 三-S6 | 「有候選名稱」、state、layer 沒定義 | 補了:候選名稱 = 過形狀過濾與消失判定、筆記先篩之前的名稱;state 五種;layer 是 handle 或 list(〈做法〉3 與 [S6]) |
| 鏡像-F17 | 三-缺條款 | 太大不剖、讀不出筆記、scan/doctor 不含 m1、印出字樣、剖不動退路沒有條款 | 補了:[S11](太大、讀不出、退路)、[S12](scan、doctor、考試不含 m1,drift fix 回 2)、[S13](印出字樣) |

參考實作重跑(〈依據〉那組驗收數字的來源;`old_sentence_exp.py run --cands P4r,P4r2,P4r3,P4r3s`,rtb 唯讀複製、工具鏈頂端 40c1fe0d、300 個提交):P4r:9 題擋到 7、rtb 91 筆(要處理 20,b2fc512 16/65)、工具鏈 4 筆(要處理 2),跟原報告一致;P4r2:9 題擋到 7、rtb 91(要處理 20)、工具鏈 1 筆只列出,跟原報告一致;**P4r3:9 題擋到 7、rtb 91(要處理 20)、13 題非漂移誤列 0、工具鏈 1 筆只列出、要處理 0,跟 P4r2 逐筆相同(9 題、rtb、工具鏈三組命中集合比對皆相等)**;P4r3s(拿掉形狀過濾):rtb 134(要處理 28)、工具鏈 24(要處理 2),跟 r1 對照腳本的量測一致。結果檔在編排者暫存 `osfold/p4r3-results.json`。

revisit 子命令冒煙測試(工具鏈 828a68be、1474d5d2、b4060e37 三組各自的上一個提交..它):三組都跑得完;828a68be 那組 P4r3 命中 0、字眼過濾放過 2、形狀過濾放過 23,跟 r1 的 P4r2/形狀過濾量測對得上;撤除節②豁免 158 行、否定撤除行 0。
