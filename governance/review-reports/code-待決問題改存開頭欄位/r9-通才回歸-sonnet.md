severity: major

這輪修補的主線都站得住:簽核帳截回與刪除、`_write_refusal_reason` 以 lstat 判斷、擋下訊息建立時清洗、決策自由文字的控制字元與日期尾端換行,都有行為證據。但我找到兩個會擋合併的問題。一個是 Ctrl-C 落在 fsync 時,帳和筆記對不上,這是修補造成的回歸。另一個是跨行的 flow 寫法還是能把題目靜默藏起來,修前就有。

1. Ctrl-C 落在簽核帳 fsync 時,帳留了一行但筆記被還原,兩邊對不上(修補造成的回歸)
   - 輸入與路徑:`lumos signoff Systems/S --note n`。筆記已寫入,帳的那一行已完整 `os.write` 進去,Ctrl-C 落在 `_signoff_append` 的 `os.fsync` 上。
   - 走到的行:`KeyboardInterrupt` 不是 OSError、UnicodeError、WriteBlocked,穿過 `_signoff_append`。外層 `except BaseException` 只呼叫 `_signoff_restore_note`,沒有截回帳。
   - 修前:筆記有 `signed_off`、帳有一行,兩邊一致。
   - 修後:筆記被還原成沒有 `signed_off`,帳卻還留著那一行。帳會宣稱有人簽核了,筆記沒有戳記。重跑一次會再多一行。
   - 最小重現:在 `os.fsync` 上包一層,遇到帳檔的 fd 就丟 `KeyboardInterrupt`,然後在記憶體內跑 `lm._cli()` 的 signoff。我的腳本 `ctrlc.py` 輸出:
     - `before rc KeyboardInterrupt | note has signed_off: True | ledger rows: 1`
     - `after rc KeyboardInterrupt | note has signed_off: False | ledger rows: 1`
   - 這是模擬中斷,不是真的 SIGINT。但 fsync 是整個追加動作裡最慢的一步,Ctrl-C 落在這裡並不罕見。
   - 圖譜 `lumos-cli-write.md` 只寫「先還原筆記再把中斷往外丟」,沒提帳。
   - 歸因:有證據的修復回歸。
   - 引句:「Ctrl-C 這類程序內中斷落在筆記已寫、帳還沒寫完之間:先還原筆記再往外丟」
   - file: `scripts/lumos:9235-9240`(修後版,`_signoff_write_locked` 的 `except BaseException` 區塊);追加本體在 `scripts/lumos:9170-9212`
severity: major
   - blocking: 是

2. 跨行的 flow 寫法裡藏題目,清單外規則抓不到,新題號還會撞號(修前就有,這輪「flow 片段逐段同樣認」沒蓋到)
   - 輸入:開頭欄位另一個欄位寫成跨行的 flow mapping。
     ```
     extra: {a: 1,
       b: 2, id: Q2, text: 漏掉的一題, class: 需求, stage: 需求}
     ```
   - 走到的行:第二行不以 `{` 或 `[` 開頭,`_pq_flow_questionish` 的 `candidate[:1] not in ("{", "[")` 直接略過。第一行的 flow 片段只有 `a: 1`,沒有題目鍵。
   - 修前修後都沒報錯(`one.py` 驗證)。PyYAML 把它讀成 `{'a':1,'b':2,'id':'Q2','text':'漏掉的一題',...}`。
   - 實跑 `question-add`:修前修後都回 rc0,新題編號 Q2。標準 YAML 讀者會看到兩個 Q2。
   - 同族的 `- [a,\n b: 2, text: hi]` 也漏。
   - 歸因:有證據的原有漏查(修前修後輸出相同)。
   - 引句:「flow 值／清單項(`{`、`[` 開頭)逐段找題目鍵」
   - file: `scripts/lumos:7266-7283`(`_pq_flow_questionish`,修後版)
severity: major
   - blocking: 是

3. 頂格的清單項 `- status: …` 被當成頂格 status 放行(原有漏查,可信度低)
   - 輸入:`x:\n- status: done`、`x:\n- - "status": y`。
   - 走到的行:`indent` 用的是整行的原始縮排(0),不是鍵所在欄位(2 或 4)。
   - 兩版都不報錯。PyYAML 把 `status` 讀成巢狀鍵。
   - 單獨一個 status 不構成題目,因為 `id`、`text` 等鍵仍會被擋。所以我只標 minor。
   - 歸因:有證據的原有漏查。
   - 引句:「if qk and not (qk == "status" and indent == 0):」
   - file: `scripts/lumos:7358`
severity: minor
   - blocking: 否

4. `decision-supersede --ended` 的尾端換行沒補,同族漏修
   - 輸入:`--ended $'2026-10-13\n'`。
   - 走到的行:`scripts/lumos:21403` 仍是 `DATE_RE.match(ended)`,`$` 放過尾端換行。
   - 修前修後都回 rc0,並在決策項目中間寫進一個空行(`ended: 2026-10-13` 之後多一行空白)。
   - 這輪只把 `decision-add` 改成 `fullmatch`。
   - 同族的 `set updated` 因為先 `strip()`,沒問題。
   - 歸因:有證據的原有漏查。
   - 引句:「fullmatch:`$` 會放過尾端換行,寫進一個空行」
   - file: `scripts/lumos:21403`
severity: minor
   - blocking: 否

5. `--decided` 的錯誤訊息原樣回顯參數,控制字元進得了終端(清洗只做在 WriteBlocked)
   - 輸入:`decision-add … --decided $'20\x1b[31mRED'`。
   - 走到的行:`ValueError` 訊息直接帶 `{decided}`。
   - 修前修後 stderr 都出現原始 ESC。
   - 這不是 WriteBlocked,所以建立時清洗沒蓋到。影響只在使用者自己的參數。
   - 歸因:有證據的原有漏查。
   - 引句:「raise ValueError(f"擋下:--decided 要寫成 年-月-日(例如 2026-08-22),你給的是 {decided}")」
   - file: `scripts/lumos:21508-21509`
severity: minor
   - blocking: 否

6. ⚠ 未指派碼位拒讀,舊版 Python 讀不了新版 Python 寫的題目
   - 輸入:題目含 U+1FAEA(Unicode 17 的 emoji),在 Python 3.14(Unicode 16.0)讀。
   - 整份清單判無法判定。訊息講得清楚,但最低版本是 3.14,3.15 以上機器寫的筆記在 3.14 機器上會讀不了。
   - 這是規格寫明的行為,我只標出跨機器的相容風險,判不準。
   - 歸因:未判定。
   - 引句:「私用區與未指派碼位(含非字元)多數字型畫成空白或方框」
   - file: `scripts/lumos:7139-7141`(修後版 `_pq_bad_char` 的 `Co`、`Cn` 分支)
severity: minor
   - blocking: 否

**通才回歸的查核結果(修前 d705e3d7 對修後 75620ccf,同一份臨時筆記庫)**
- 矩陣:19 支指令(`set`/`append`/`remove`/`summary-line`/`guard bind`/`audit`/`kill`/`kill-add`/`decision-add`/`amend`/`supersede`/`reindex`/`reindex --all`/`question-add`/`signoff`/`updated-sync`/`self-audit`/`decision-refs add-ai`/`new`),乘 8 種筆記(正常、CRLF、BOM、符號連結指庫內與庫外、硬連結、唯讀、非 UTF-8、目錄)。逐支比 stdout、stderr、rc 與檔案內容,152 組裡只有暫存路徑名和時間戳不同。
- 未成功覆蓋:`about-code restamp`、`rel-cascade confirm`、`question-set` 只跑了 rc2 的錯誤參數,沒有驗到正常路徑。「鎖被占住」沒有重跑,因為每組要等 60 秒。
- 讀檔路徑:`load_raw_for_edit` 在修前修後原文相同,本來就不拒符號連結。`_write_refusal_reason` 只有 3 個呼叫處(`atomic_write_verify`、簽核帳、drift fix 載入),與圖譜一致。
- 擋下訊息沒有印兩次的情況。
- `guard audit`、`guard bind` 在筆記檔名含 ESC 時,修前輸出原始 ESC,修後乾淨。
- 簽核帳異常(`sig.py`):
  - 帳是 FIFO:修前卡住逾時,修後 rc2。
  - 帳是目錄:訊息從「多個硬連結」改為「不是一般檔案」。
  - 帳是符號連結、硬連結、唯讀:都 rc2,筆記已還原,帳沒動。
  - 訊息段落順序有變。
  - 正常簽核(含新建帳)輸出與修前逐字相同。
- 855 篇 repo 筆記各插入一題後,`pq_parse` 修前修後結果相同,0 差異。
- `parse_frontmatter`、`parse_decisions`、`fm_structure`:這輪差異在這三處完全沒有改動,`BLOCK_SCALAR_HEADERS` 早就存在。
- 以 PyYAML 當對照做隨機測試共約 20 萬筆:
  - 區塊純量:0 個漏。
  - 單行結構:只剩第 2、3 條。
- 效能:各種重複結構的長行都呈線性(資料量四倍,時間約四倍);20 萬行 2.1 秒。Unicode 對抗輸入在 20 萬字內也是線性。
- Unicode:愛心加 FE0F、旗、彩虹旗、家庭、膚色、波斯文 ZWNJ、僧伽羅文、梵文都照常放行。軟連字號夾漢字被擋,符合預期。
- 子集(在 `git archive` 出來的副本上跑,沒有 `.git` 和 `skills/`):
  - 全綠:signoff 28、summary_line 27、set_ 134、append 207、decision 127、cascade 52、`qfm_r8` 76、`kill_recipe_check_matches` 92。後者釘住 `guard kill` 對非 UTF-8 檔 rc1 的約定。
  - 有紅:guard_ 539 過 1 紅,drift 1012 過 2 紅,lint 382 過 1 紅。
  - 這 4 個紅(`t_role_cards_guard_names_missing_item`、`t_drift_when_gone_grammar`、D5、`t_repo_graph_passes_note_lint`)缺的都是副本裡沒有的 `skills/` 與 hooks 檔。drift 與 lint 在修前副本上一樣紅,所以不是修補造成。guard_ 那個沒在修前跑對照,但它缺的是同一類檔案。
- 圖譜鏡頭:`lumos-cli-write.md` 的描述與程式一致,只有第 1 點的 Ctrl-C 說法漏了帳。`lumos-cli-read.md`、`規格閘.md`、`bound-tests-gate.md` 我沒有逐段對照,只查了與寫入拒絕相關的字串。

**三問**
- ①原問題的修復效果:
  - 帳寫不進去時截回、新建的帳刪掉;連結檢查本身出錯時還原筆記。
  - FIFO 不再卡住,目錄的訊息講對。
  - 擋下訊息建立時清洗,`guard audit` 與 `guard bind` 不再印出 ESC。
  - 決策文字的 ESC 與 tab 被拒,日期尾端換行被拒。
  - `- ` 連串線性,JSON 風格、引號後空白、雙引號跳脫的鍵,`? ` 複雜鍵,flow 內 anchor 與 tag 的鍵,縮排的 `pending_questions:` 都被抓到。
  - 例外:Ctrl-C 的還原有第 1 點的缺口,跨行 flow 有第 2 點的缺口。
- ②正常、錯誤與相鄰路徑:矩陣與正常簽核流程都與修前相同。`_cli()` 接住的訊息與 rc 與修前裝飾器一致,repo 內沒有其他 `main()` 的非測試呼叫端。精簡版產生器不在這個 repo,我無法驗證它對新形狀的處理(⚠)。
- ③新發現案例的修前修後:第 1 點修前一致、修後不一致;第 2 至 5 點修前修後相同(都沒擋);第 6 點是修補新增的行為。

總結句:這輪修補大致站得住,但簽核在 Ctrl-C 落於 fsync 時會讓帳與筆記不一致,而且跨行 flow 仍能靜默藏題並撞號,這兩點需要先處理。

證據腳本都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r9-通才回歸-sonnet/`(`matrix.py`、`ctrlc.py`、`fuzz.py`、`fuzz2.py`、`sig.py`、`one.py` 等),由編排者收貨後刪除。`$TMPDIR` 底下我自己跑 guard_ 時留下的 `gctl-run-qzwseazc` 已刪。drift、lint 等其他測試現場看不出是不是我的,沒動,留給編排者確認後清理。
