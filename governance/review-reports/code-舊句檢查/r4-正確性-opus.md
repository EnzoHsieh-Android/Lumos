severity: minor

# 舊句檢查代碼審第 4 輪 — 正確性-opus

範圍:只看提交 73d55192 的第 3 輪修正(凍結 patch `r4-snapshot.patch`)。實驗在自己的 `git clone --shared` 複本 `scratchpad/r4cor-opus`(82c93a23… 暫存區)跑,直譯器 /opt/homebrew/bin/python3(3.14)。實驗腳本在同一個暫存區的 `r4cor-opus-exp/`(mut.py、e2e.py、short.py、states.py、ch.py)。

## F1 超長行用純子字串判「有關」,名稱只是別的識別字前綴時照判不了擋,結論還說行裡有這個名稱

severity: minor
blocking: 否
引句:「行內以子字串出現任一候選名稱的,可能藏著舊句 → long_lines(照判不了算)」
file: `scripts/lumos:29239`
file: `scripts/lumos:28902`

1. 輸入(真 git repo,e2e.py 的 E2):`.lumos/config.json` 寫 `{"drift_check": {"old_sentence": "block"}}`;`src/a.py` 起點有 `def get_user()` 與 `def keep_me_x()`,終點刪掉 `get_user`;`Systems/Table.md` 有一行 `"| get_user_id | 值 |" * 1500`(超過 2 萬字),這行只提到 `get_user_id`,沒有提到 `get_user` 這個整字。
2. 實跑 `drift check --diff base..HEAD`:rc 1,帳記 `kind blocked`、`long_lines 1`、`long_lines_other 0`;結論是「擋下:舊句檢查:這次消失 1 個名稱;有 1 行太長沒看…」,位置那行寫「(行裡有這次消失的名稱、算判不了):Systems/Table.md:6」。
3. 對照組 E3:同樣內容,但只重複 1000 次(不到 2 萬字)→ rc 0、`passed`、「筆記裡沒有還在講的」。同一段文字只因為變長,就從「確定沒提到」變成「擋下」。
4. 原因:`_drift_m1_note_long` 對每個候選名稱做 `n in ln` 純子字串比對。不過現成的 `_drift_m1_line_names(idx, ln)` 已經證明是整字正則命中的超集(它的說明文件說明了這點,r1 另外用隨機 3000 組比過),單行成本也有上限。對 E2 那行,整字正則跟 `_drift_m1_line_names` 都回 `[]`。所以純子字串多出來的那幾行,照定義不可能影響判定。這違反第 3 輪收窄自己寫進〈做法〉1 的原則「只有可能影響判定的才擋」。印出來的「行裡有這次消失的名稱」這句也跟事實不符。
5. 影響面:只在圖譜有超過 2 萬字的行、而且消失的名稱剛好是那行某個較長識別字的一段時才會發生(`Result`/`Results`、`old_name`/`old_name_v2`)。在 block 模式下這會擋推送,只能改那行或單次略過;warn 模式只會多印一行。我同時確認了反方向沒有漏掉:純子字串是整字命中的超集,不會放掉真的舊句。

## F2 留痕檔短寫的修法只改了回傳值,唯一的呼叫端不看回傳值,殘留的半行還會吃掉下一筆

severity: minor
blocking: 否
引句:「if os.write(fd, data) != len(data):   # 比照 _ledger_append:短寫(磁碟滿)不算寫成」
file: `scripts/lumos:29469`
file: `scripts/lumos:29501`

1. 唯一的正式呼叫端是 `_drift_m1_ledger` 裡那行 `_drift_m1_ledger_miss(root, tip, st)`,它不收回傳值。所以短寫時回 True 或回 False,推送的輸出、rc、帳都一樣。`t_drift_m1_review_r3_ledger_miss_short_write` 翻紅的只是一個沒人讀的回傳值。
2. 實跑(short.py):把 `_gate_event` 換成回 False,先讓 `os.write` 只寫 30 位元組,再正常跑一次。兩次的 stderr 完全相同,都只有既有那句 telemetry-write-failed。`ledger-miss.jsonl` 最後只有 1 行,而且這行不是合法 JSON:`{"ts": "2026-09-30T13:03:42+08{"ts": "2026-09-30T13:03:42+08:00", "repo": "/private/var/…`。第一筆被截斷的半行沒被收回(沒有截回原長度,也沒補換行),第二筆寫成功的留痕接在它後面,兩筆一起壞掉。
3. 對 REVISIT 的後果:計劃說「照 repo 篩,有 1 行就算樣本不足」。如果照 repo 篩時是逐行 `json.loads`,這兩次漏記都會被略過,樣本不足那條就不會成立,也就是量準度時會漏掉「帳沒記到」的訊號。`_ledger_append` 的呼叫端至少會把短寫變成 rc 2 讓人看到,這裡「比照」只比照了檢查那一行,沒有比照它的效果。

## F3 計劃的帳欄位定義沒跟著第 3 輪收窄改

severity: minor
blocking: 否
引句:「`long_lines`(超過 2 萬字沒看的行數)」
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:142`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:119`
file: `docs/lumos-toolchain-knowledge/Projects/舊句檢查_計劃.md:184`

1. 〈做法〉3 的帳欄位清單還把 `long_lines` 定義成「超過 2 萬字沒看的行數」,也沒有列 `long_lines_other`。第 3 輪之後,`long_lines` 只算「行內以子字串出現候選名稱」的超長行(〈做法〉1、RETIRE-IF、程式都是這樣)。照欄位清單去讀帳的人,會把無關的超長行也當成在 `long_lines` 裡。
2. 同一節結論行的清單裡,「done、兩層有任一筆」那句還無條件寫著「這時不算『有東西』、沒有開頭詞、kind passed」。可是同一節下一條與 kind 對照都寫了:有 `long_lines` 時照判不了算(開頭加擋下／提醒、kind 記 blocked／warned)。states.py 實跑:done、只列出 1 筆、`long_lines` 2 → kind 記 warned／blocked。程式照新規矩走,是那句沒改。
3. [S6] 的欄位列同樣沒有 `long_lines`／`long_lines_other`。第 3 輪 spec 對照-F1 說「S6 同步」,但同步的只有 kind 那一段。

## 圖譜鏡頭逐條判定

- `Systems/lumos-cli-read`(search 預設排除 superseded):不影響。這次沒動 search 或它的濾網,改到的全是 m1 印出、記帳、doctor 兩個開關那一行,以及 `_mkdir_private_layer`。
- `Systems/bound-tests-gate`(code-loop check 逐支真跑綁定測試):不影響。閘的程式沒動。存量漂移守衛那行 `TEST:` 加的 6 支 r3 測試都存在,`-k drift_m1_review_r3` 實跑 18 條斷言全綠,`-k drift_m1` 248 全綠。
- `Systems/guard-kill`(rc 優先序、`--json` 純度):不影響,guard kill 的程式沒動。
- `Systems/授權與歸屬`(授權檔不得進 `_VENDORED_TOOLKIT`、主程式檔頭):不影響,白名單與檔頭都沒動。
- `Systems/測試假綠形態`(還原翻紅要配前置斷言):合約成立。我把 12 個修法各自還原(mut.py:無關的也算判不了、永不算判不了、不記位置、只在 done 時印、判準改回 `_drift_c4_show_name`、不看名稱、剖不動那行回 `_drift_m1_show`、出錯那句回 `_drift_m1_show`、父層不講、block 又唸、chmod 失敗當錯、不驗短寫),綁的那支測試全部翻紅。每次都先清 `__pycache__`,跑完原檔還原,`git status` 是乾淨的。前置斷言的狀況:long_lines_narrowed ①、ledger_miss ① 有明寫;paste 的 ② 一般路徑照印、③ 端到端先看到 `gone_tab_x`,terminal_escapes 有正向的 `in out`,這些都當得了現場證明。只有 chmod_unsupported 沒斷言「替身真的被呼叫到」。目前還原後會紅,證明現在走得到;將來要是改成「權限已經是 0700 就不 chmod」,這支會變空殼,但這不是這次 diff 造成的假綠。另外 F2 那支的翻紅雖然有效,釘的卻是沒人讀的回傳值(見 F2)。
- `Systems/lumos-cli-lifecycle`(re-inject 只動 sentinel 之間):不影響,沒動注入。
- `Systems/design-loop`(處置閘第五步):不影響,沒動 loop 程式。
- `Systems/pitfalls-code-loop`:不影響,沒動分級程式。
- 只列名的節點(節點範圍與索引守衛、lumos-deinit、slim 安裝與卸載、canary-audit 等):這次唯一碰到它們共用路徑的是 `_mkdir_private_layer`(vault-lock、dispatch-lens、bound-filter、drift-defs、drift-m1 都走它)。我實測了三種情況(ch.py):① 模擬不理 mode 的檔案系統,建出 0777 再讓 chmod 失敗 → `_mkdir_trusted_under_home` 回 False、快取目錄是 None;② 正常 0700 加 chmod 失敗 → True;③ mkdir 之後、chmod 之前把那層換成指向別處的連結 → False,別人的目錄裡沒被建東西。每一層建完後,「連結、目錄、擁有者、group/other 可寫」這四項檢查照做,收權限失敗不會讓不安全的目錄被信任。鄰居子集:private_dir 18、vault_lock 10、dispatch_lens 79、bound_filter 9 全綠。其餘節點跟這次改的函式沒有交集。

## 查過、沒問題的

- 超長行收窄會不會放掉真的舊句:不會。長行判的是全部可列的名稱(`names`,不是先篩過的),`n in ln` 是 `_drift_m1_name_rx` 任何命中的超集(正則逐字 escape、沒有大小寫或正規化)。撤除節與圍欄在長度判斷之前就已經跳過,這點跟一般行相同。
- 計數:每一行只進兩種計數其中一種;位置各記前 5 個,超過的印「…」;時間到時 ticker 丟出例外,那一行不計數。六種狀態 × warn/block 實跑(states.py):兩種計數與位置在 done、timeout、git-failed、unreadable、error 都印,帳的 `long_lines`、`long_lines_other` 都有記;`long_lines_other` 不影響 kind 與 rc。no-base 與 error 兜底在實務上不會掃到筆記,計數是 0。
- 照貼指令的字元判準:`_esc_clean` 會改掉的字元(小於空白、0x7f–0x9f)都屬於 Cc;非 UTF-8 經無損解碼後是 Cs。兩者都在新判準裡,所以印出的照貼指令一定跟實際字串相同。非 UTF-8 筆記檔名端到端(e2e.py E1):不印照貼指令,改說請手動表態。
- doctor:`{"drift_check": "off"|null|[…]}` 時,gate 那句與舊句檢查那句各講各的;block 不唸;推送時 `_drift_config` 也會帶上那句。
- 旁註(找不到自然觸發的場景,所以不列 finding):`_drift_m1_guarded` 最後的保底 print(`scripts/lumos:29515`)仍用 `_drift_m1_show` 印例外訊息,跟第 3 輪改成 `_drift_m1_term` 的那一句屬於同一種問題、但這一處漏掉了。只有在「判定出錯之後、印出與記帳又出錯」時才會走到這裡;我用 OSError 試過,它的訊息本來就用 repr,方向控制字元已經被跳脫了。

最高等級:minor
