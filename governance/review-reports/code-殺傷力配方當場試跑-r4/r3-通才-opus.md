severity: major

# 另開迴圈第 3 輪(上限輪)通才-opus:只審 r3-delta.patch

審查材料:`governance/review-reports/code-殺傷力配方當場試跑-r4/r3-delta.patch`(40293f99..0e6a99ad)。實驗都在自己的 `git clone --shared` 上跑(新版 0e6a99ad,基準版 40293f99 另開一份 clone 對照)。

## 三項驗收

| 項 | 判定 | 依據 |
|---|---|---|
| ① `--json` 改經 `_kill_esc` | **修好了,但漏了同類(見 F2)** | 網格 1296 格(前一席 1136 格再加 5 種形狀:note 帶替身字元、invariant 帶雙向覆寫、invariant 帶星面格式字元、invariant/note 帶「反斜線+引號+換行+U+2028+U+0085」),新舊版對照:**沒有任何一格「沒崩卻不是恰好一行合法 JSON」**。跟基準版不同的格子全是「舊版崩、新版不崩」(inv/note/test/plat 帶替身字元的 `--json` 共 72 格),外加「反斜引號換行」32 格從「多行」改成「恰好一行」(舊版 U+2028、U+0085 原樣印出,`splitlines()` 會在那裡切斷)。回傳碼照判定(killed_unattributed→1、error→2),沒帶 `--id` 的既有格子回傳碼一格都沒變。讀回的值:只有星面格式字元(U+E0067 這類)讀回來不一樣(F2)。 |
| ② 寫 kill-log 改經 `_kill_esc` | **修了,但漏了同類(F1,blocking)** | 寫入端不崩了,值也讀得回來(BMP 範圍)。可是三個讀端裡,`lumos gov` 把讀回來的落單替身字元原樣印出,**每次執行都崩**。修正之前寫 kill-log 時就崩、帳裡不會出現這種行;現在工具自己會寫進去。合約背書 `_backing_kill_rows` 與 doctor P2 的 survived 清單讀回的值正確(下面另有逐一核對)。 |
| ③ 改名、搬位置、covers 抽成小函式 | **修好了** | `_kill_old_bad`/`_kill_new_bad` 在程式、測試、筆記裡都沒有殘留,只剩舊輪卷證引用(歷史紀錄,不必改);`_kill_detail_str`、`_kill_inv_has`、`_kill_covers_list` 各只定義一次。附帶一提(不算發現):`_backing_note_recipes` 裡還留著一行跟 `_kill_covers_list` 一模一樣的行內寫法(`scripts/lumos:41573`),目前不會出錯。 |

kill-log 讀端一個一個找(用 `grep -rn kill-log` 掃全 repo,只有 `scripts/lumos` 與測試檔會讀),每個讀端都另開一個 repo 端到端跑一次(讀回網格 144 格:19 種字元 × invariant/note/test/節點檔名 × killed/survived):
- **gov 統計**(`cmd_gov` 的第 5 個帳源,file: `scripts/lumos:7706`):讀得到;遇到落單替身字元,印出的時候就崩 → F1。
- **合約背書** `_backing_kill_rows`(file: `scripts/lumos:41527`):除了星面格式字元那幾格,其他格子的 test/node 讀回都等於原值,也對得回配方;節點檔名帶星面格式字元時,行對不回配方、被略過 → F2。
- **doctor P2 survived 清單** `_kill_p2_survived`(file: `scripts/lumos:14301`):invariant 取筆記那一條、經 `_kill_show` 跳脫,替身字元的 survived 格都列得出來、不崩;只有節點檔名帶星面格式字元的 2 格沒列出 → F2。
- 沒有任何讀端拿原始文字直接比對 kill-log(簿記白名單、cochange 排除清單只認檔名;聯集合併按行處理)。

相關測試子集在 clone 上全綠:`t_guard_kill_only_ids` 30、`t_guard_kill_json_purity` 6、`t_kill_recipe_check_matches_guard_kill` 92、`t_doctor_p2_lists_survived` 13。

## F1 kill-log 改經 _kill_esc 之後,帶落單替身字元的行會寫進帳,lumos gov 從此每次都崩
severity: major
blocking: 是
引句:「fh.write(_kill_esc(json.dumps({"ts": ts, "node": rel, "commit": commit,」
file: `scripts/lumos:7798`
file: `scripts/lumos:7706`
file: `scripts/lumos:29453`

1. 白話:這次修好了「寫帳的時候崩」,可是被跳脫的字元讀回來還是原來那個印不出的字元。`lumos gov` 把它接進 detail 字串直接印出來,就在印的地方崩。結果是崩潰從 guard kill(只崩那一次)搬到了 gov(帳還在就每次崩)。
2. 最小重現(note 欄寫 `"x\ud800"`,其他照 `_mk_kill_env`;腳本在我的臨時目錄 `repro.py`,參數是 repo、欄位、值):
   ```
   $ python3 repro.py <基準 40293f99> note "'x\ud800'"
   $ lumos guard kill Systems/Limit --json → rc=1  stderr末行="UnicodeEncodeError: ... surrogates not allowed"
   kill-log: (空)
   $ lumos gov → rc=0  stdout='\n近 90 天共 0 筆治理事件\n'
   $ lumos gov --stats → rc=0
   $ python3 repro.py <新版 0e6a99ad> note "'x\ud800'"
   $ lumos guard kill Systems/Limit --json → rc=1  stdout='{"results": [{... "note": "x\\ud800", ...'(正確)
   kill-log: {... "note": "x\ud800", ...}
   $ lumos gov → rc=1  stderr末行="UnicodeEncodeError: 'utf-8' codec can't encode character '\\ud800' in position 70: surrogates not allowed"
   $ lumos gov --stats → rc=1  (同上)
   ```
   崩在 `cmd_gov` 印時間軸那一行 `print(f"{r['ts'][:10]} [{r['gate']}/{r['kind']}/{mark}] ... {r['detail'][:50]}")`。另外驗了 `gov Limit`、`gov --full` 也是 rc=1;`gov --nags 14 --since 120` 只有一筆時沒崩。
3. 觸發範圍(讀回網格實測):invariant、note、test 任一欄帶落單高位或低位替身字元,不論 `--json` 或人讀模式、killed 或 survived,只要 guard kill 走到寫帳那一步,gov、`gov <節點>`、`gov --stats` 三種都崩,共 18 格(高位、低位、高位接反斜線 u 三種 × 三欄 × 兩種判定)。人讀模式的 test/platform 替身字元格,是先寫完帳才在印結果行時崩,帳一樣被寫進去。修正前這些格子都在寫帳時就崩了、帳裡不會出現。
4. 為什麼算 major:這個 repo 的 kill-log 進版控,而且在簿記白名單裡(提交它不會讓代碼審留痕失效,`_pull_source_or_abort` 會聯集合併)。所以一次 guard kill 寫進去的一行,會讓所有拉到這版的人 `lumos gov` 全部崩,直到有人手動刪掉那行。同一支程式裡有先例把這種情況當成缺陷修掉了:file: `scripts/lumos:29453` 的註解寫著「原樣路徑寫進治理帳後 lumos gov 每次當掉」。
5. 修法方向(只是方向):派工詞列的三個讀端應該一起處理。gov 的 kill 帳源在組 detail/token 時經 `_kill_esc`(或在 gov 印出前統一處理不可印字元);背書與 P2 已經不印帳上的原文,不用改。再補一格測試:⑥h 的替身字元格子跑完 guard kill 之後,再跑一次 `lumos gov` 斷言沒有 Traceback。

## F2 _kill_esc 把 U+FFFF 以上的格式字元寫成 5 碼的 \uXXXXX,--json 與 kill-log 讀回的值變了
severity: minor
blocking: 否
引句:「經 _kill_esc 改寫成 \uXXXX 跳脫,讀回來是同一個值(另開迴圈通才席)」
file: `scripts/lumos:14028`

1. `_kill_esc` 的寫法是 `f"\\u{ord(c):04x}"`。字元落在 Cf 類別、而且碼位超過 U+FFFF 時(例如 U+E0067 標籤字元、U+1D173 樂譜格式字元;英格蘭、蘇格蘭、威爾斯的旗幟 emoji 就是用標籤字元組成的),會寫成 `7`。JSON 只認 4 碼,所以讀回來變成 U+E006 加上字元「7」。輸出仍是合法 JSON,只是值不對了,跟這段註解宣稱的「讀回來是同一個值」矛盾。
2. 重現(note 欄寫「旗」加英格蘭旗):
   ```
   基準 40293f99:kill-log note 讀回 == 原值: True  '旗\U0001f3f4\U000e0067...'
   新版 0e6a99ad:kill-log note 讀回 == 原值: False '旗\U0001f3f472...'
   新版 --json stdout:"note": "旗🏴\\ue0067\\ue0062\\ue0065\\ue0...
   ```
   網格 `inv=星面Cf` 32 格:kill-log 讀回 32 格全錯,`--json` 16 格全錯。讀回網格裡,invariant、note、test 三欄都會中。
3. 讀端的實際影響:筆記檔名帶這類字元時,kill-log 的 node 被改寫,`_backing_kill_rows` 對不回配方、整行略過(背書少一筆證據),doctor P2 的 survived 清單也不列這條(讀回網格 `星面Cf-tag`、`星面Cf-樂譜`、`英格蘭旗` 的 node/survived 三格 E=False)。觸發要靠罕見字元,所以算 minor;修正後這是第一次會「默默改值」而不是崩潰。
4. 修法方向:碼位超過 U+FFFF 的字元改寫成 UTF-16 代理對的兩段 `\uD8xx\uDCxx`,或者這類字元不跳脫;`_kill_rm` 印配方(file: `scripts/lumos:14799`)用的是同一支,印出來的東西也一樣不對。

## F3 Issue 改寫後的「還會崩的」清單漏了 file、platform 帶替身字元,而且宣稱「任何欄位都不再崩」
severity: minor
blocking: 否
引句:「invariant、test 帶替身字元時的人讀輸出(結果行會印這兩欄)」
file: `scripts/lumos:15193`
file: `scripts/lumos:15326`

1. 這次修正把 Issue 的清單從「invariant/platform/file/test 帶替身字元時的人讀輸出」縮成只剩 invariant、test,帶 `--id` 的那句也從「invariant/platform/file」縮成只剩 invariant;同一行還寫著「任何欄位帶替身字元都不再崩」。網格實測不是這樣(這幾格新舊版都崩,不是這次弄壞的,是筆記寫錯):
   - `file` 帶替身字元:`--json` 與人讀、帶不帶 `--id` 都崩,8 格,崩在 `os.path.realpath(os.path.join(wt, r.get("file", "")))`。重現:`repro.py <新版> file "'prod\ud800.py'" --json` → rc=1、stdout 空、`UnicodeEncodeError ... surrogates not allowed`。
   - `platform` 帶替身字元:人讀模式帶不帶 `--id` 都崩,16 格,崩在印結果行(detail 是「平台 'p\ud800' 不在 config」)。重現:`repro.py <新版> platform "'p\ud800'" ""` → rc=1、stdout 空、`UnicodeEncodeError`,而且帳已經先寫進去了(會觸發 F1)。
2. 這篇 Issue 是下一次修這類崩潰時的待辦清單,少列兩項就會被漏掉。同一句宣稱也寫進了 Systems/guard-kill 的 PITFALL 行(「人寫欄位帶替身字元不再崩」),兩處要一起改正。

最高等級:major,blocking 共 1 條
