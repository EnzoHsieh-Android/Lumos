severity: minor

## F1 還沒提交的紀錄現在會被讀內容,遞迴爆掉的 JSON 讓 `_note_reread_uncommitted` 丟出 RecursionError
severity: minor
blocking: 否
引句:「_n, fp, doc = _note_reread_verdict_doc(f.name, f.read_bytes())」
file: `scripts/lumos:34857`
歸因:有證據的修復回歸。修前 f80352f6 只比檔名、不讀內容,同一個輸入不丟例外。修後 5ce8115d 丟 RecursionError。

1. 輸入:`governance/reread-verdicts/` 下有一份還沒提交、檔名合規、約 250KB 的 `[[[…]]]`。125000 層,低於 256KB 上限,Python 3.14 的 `json.loads` 在約 120000 層以上會丟 RecursionError。
2. 路徑:`_note_reread_uncommitted` 檢查 `st_size` 通過後,呼叫 `_note_reread_verdict_doc`。其中 `json.loads` 只接 `(ValueError, UnicodeDecodeError)`,RecursionError 穿過 `except (OSError, _NoteRereadStop)`。
3. 結果:`reread-prepare` 的第 35028 行沒有外層 try,直接崩出 traceback,訊息裡沒有檔名。check 路徑被 `_note_reread_guarded` 接成「判不了」。
4. 這違反新 docstring 的承諾:「讀不了、讀不懂、太大、符號連結的都不算」。
5. 重現:`python3.14 /tmp/lumos-seat-work/code-舊句兩道轉擋/正確性主程式2-sonnet/t2.py <repo>`,把 `nested` 設成 `"["*125000+"]"*125000`。修前印 `{'bbbb…','aaaa…'}`(兩份都算),修後印 `RAISED RecursionError`。
6. 已提交的紀錄走 `_note_reread_verdicts` 也有同樣的脆弱,是原有問題,本條不算它。

## F2 超過上限的錯誤訊息自相矛盾:「256 KB,超過上限 256 KB」
severity: minor
blocking: 否
引句:「return None, (f"這份紀錄有 {size // 1024} KB,超過讀端單份上限 {max_bytes // 1024} KB——寫了推送前的檢查也讀不了,不寫"」
file: `scripts/lumos:34069`
歸因:有證據的修復回歸(修補新加的訊息;修前沒有這個檢查)。

1. 輸入:序列化後 262145 到 263167 位元組,也就是上限加 1 到加 1023。
2. 兩個數字都用 `// 1024` 向下取整,訊息變成「這份紀錄有 256 KB,超過讀端單份上限 256 KB」。
3. 重現(t5.py):修後 delta=+1 和 +1023 都印這句。修前沒有 max_bytes 參數,照寫檔。
4. 邊界本身是對的:剛好等於上限(262144)會寫,與讀端 `n > max_bytes` 才拒的口徑一致。

## F3 太大時的處置提示只點最長那一行,實際原因常是點出的行數太多 ⚠
severity: minor
blocking: 否
引句:「hint = (f"(點出的第 {longest['line']} 行有 {len(longest['text'])} 字)——把筆記裡那幾行拆短,重新 reread-prepare 再派判定者"」
file: `scripts/lumos:35133`
歸因:有證據的修復回歸(修補新加的提示)。

1. 輸入:100 行規則句、每行 3300 字,判定者全部點出。
2. 重現(t8.py 100 3300):修後 rc2,印「這份紀錄有 330 KB,超過…(點出的第 11 行有 3307 字)——把筆記裡那幾行拆短」。修前照寫、rc0,留下一份讀端讀不了的紀錄。
3. 總量由「列數 × 行長」決定。提示只怪單行,把單行拆成三行,點出的列數很可能跟著變多,不保證能降到上限內。這點我沒驗,標 ⚠。
4. 原問題本身(寫出讀不了的紀錄)確實修好了。

## F4 note-reread 的帳整行沒真正壓進 4096:量的跟寫的不是同一行
severity: minor
blocking: 否
引句:「nodes = _gate_event_fit(root, "note-reread", kind, note, extra, "rows", hard=hard, nodes=nodes, nodes_cap=20)」
file: `scripts/lumos:35429`、`scripts/lumos:1523`
歸因:有證據的修復殘留,修補縮小了問題但沒消除。修前 f80352f6 的 15、30、50 篇沒對照分別是 5835、8940、12600 位元組。修後 5ce8115d 是 4051、5886、8446。

1. 量錯:`_gate_event_fit` 這裡沒傳 `head_sha`,量的事件是 `commit:""` 且沒有 `head_sha`。`_gate_event` 寫入時才補 `HEAD`,多出 `commit` 7 字元和約 56 位元組的 `head_sha` 欄。`_gate_event_fit` 的 docstring 說「量的跟寫的是同一行」,這裡不成立。舊句檢查傳 `head_sha=tip`,所以沒有這個落差。
2. 重現(t1.py):`must` 有 21 行時,fit 判定「裝得下」並留 19 列,實際寫出 4107 位元組。
3. 沒修到的部分:`note` 的 `path=指紋` 清單沒有被截,而且同時寫進 `note` 和 `detail` 兩欄。重現(t7.py):30 篇沒對照時 rows 已丟光、nodes 已截到 20,整行仍有 5886 位元組。
4. 帳寫入端(`_gate_event`)沒有硬上限,所以只是超出自己宣稱的 4 KB,沒有事件被丟。

## 修補三問

**① 原問題修復的行為證據(repair)**

- **record 寫前量大小。**
  - 輸入:100 列、每列 3300 字的判定。
  - 修前:寫出 330KB 的紀錄,rc0。
  - 修後:rc2、不寫,資料夾沒有殘檔,也沒有暫存檔(t8.py)。
- **「還沒提交」只算 provenance_ok 為真。**
  - 輸入:工作目錄有一份 `provenance_ok:false` 的未提交紀錄。
  - 修前:該指紋算 wip。
  - 修後:不算(t2b.py)。
  - `-k reread` 226 項全綠。
- **帶 `--gate` 的參數錯措辭。**
  - 指令:`reread-check --gate --diff bad`。
  - 修前:印「回頭重讀提醒:這次沒提醒:…」,rc2。
  - 修後:印「擋下:--diff 要給…」,rc2。
  - 不帶 `--gate` 兩版都印提醒、rc0。
- **第二層有東西那筆帳走 `_gate_event_fit`。**
  - 修前:帳不截,12600 位元組。
  - 修後:會截 rows,但見 F4。
- **超長行整字先篩。**
  - 輸入:有 `get_user` 這個消失名稱,超長行只有 `get_user_id`。
  - 修前:判有關(long_lines)。
  - 修後:判無關(long_other)(t4.py)。
  - 「Foo 對 Foobar」「xsrc/a.py 黏字」同樣由有關改成無關。
- **`_in_ci` 單一條件。**
  - 輸入:只設 `GITHUB_ACTIONS`。
  - 只讀碼推論,帳的來源會由 hook 變成 ci;沒另外跑。
- **判不了那筆帳改記 `state` 字串。**
  - 讀者:程式裡沒有人讀舊的布林欄 `undecidable`。
  - `t_reread_block_undecidable` 在 `-k reread` 裡通過。

**② 相鄰路徑與正常路徑(preserve)**

- **`_note_audit_write_verdict` 的其他呼叫端。**
  - 筆記內容審的兩處(第 34244、34349 行)沒傳 `max_bytes`,預設 `None`,行為不變。
  - 剛好等於上限(262144)與上限減 1 兩版都寫,檔大小一致。
- **`_hooks_path_is_ours`。** 輸入包括絕對、相對、`./`、結尾斜線、`scripts/../scripts/hooks`、`.githooks`、空字串、`~/x`、前綴空白。兩版輸出逐行相同(t6.py)。`_enforcement_prepush_ungated` 只在 hooksPath 指向本 repo 時才會走到,預設分支用不到。
- **`_drift_m1_note_long` 的正常命中。** 整字名稱、純中文名、中英混合名、路徑名都仍判有關,兩版一致。
- **效能。** 5000 組、共 10000 個名稱,線長 20000、20001、1M、10M 分別是 0.055、0.054、2.19、22.5 秒,修前修後相同。成本由「名稱數 × 行長」決定,大迴圈每 256 個名稱呼叫 `check_time`,所以 30 秒軟上限仍然有效。整字先篩沒有讓它變快,也沒有讓它變慢。
- **整體測試。** `-k reread` 226 項、`-k drift_m1` 252 項全綠。

**③ 新發現案例的修前修後**

| 案例 | 修前 | 修後 |
|---|---|---|
| F1 | 不丟例外 | 丟 RecursionError |
| F2 | 沒這個檢查 | 訊息矛盾 |
| F3 | 沒這個檢查 | 提示偏向單行 |
| F4 | 12600 位元組 | 8446 位元組(30 篇時 5886),仍超過 4096 |

## 圖譜鏡頭

本次派工沒有附固定席筆記(鏡頭計算超時),我也沒有自己補算。唯一對照的合約是計劃的 S5 到 S25,涵蓋 S7、S18、S24、S25。

- **S7(provenance 為假視同沒對照):** 修補後 `_note_reread_uncommitted` 與 `_note_reread_covered` 同口徑,不影響,還補強了它。
- **S18(參數錯回 2):** 回傳碼不變,只換措辭。
- **S25(未帶 `--gate` 的 hook 提示):** `_in_ci()` 取代原來的 CI 或 GITHUB_ACTIONS 判斷,語意不變。
- **角色卡 be-api-compat:** 治理帳的 `undecidable` 布林欄改成 `state` 字串,程式裡沒有舊欄位的讀者。
- **角色卡 be-authz:** 沒有新增端點,不適用。

## 未驗範圍

- 沒跑全套測試。
- `_in_ci` 的 `GITHUB_ACTIONS`-only 路徑沒實跑。
- 報告含孤立代理字元時 `body.encode` 的行為沒驗。
- 已提交紀錄合計 8MB 上限不受寫端檢查保證,沒驗實際觸發。
- 設計文件內部的筆記互相引用沒逐條查。

這一輪最高等級是 minor。
