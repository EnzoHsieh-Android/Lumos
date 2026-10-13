severity: major

這輪我在同一份臨時筆記庫裡,拿修前版(afb9e0da)和修後版(5498fec8)各跑一次一般筆記和符號連結筆記,逐支比 stdout、stderr 和 rc。工作檔都在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r6-通才回歸-sonnet/`。

**測試子集(修後)**:`-k summary_line` 27 項、`-k set_` 155 項、`-k append` 215 項、`-k guard_` 592 項、`-k qfm` 253 項,全綠,0 失敗。

**修前修後逐支比對**
- **一般筆記**:set(status、updated、valid_under、revalidate_when)、append、remove(含整欄拿掉)、decision-add、decision-supersede、question-add、summary-line(正常、對到多處、`--nth`、`--dry-run`)、updated-sync、decision-reindex、guard bind、guard audit、self-audit、signoff、decision-refs 全部 rc 和輸出逐字相同。
- **資料夾是符號連結、整個筆記庫是符號連結**:兩種都完全沒變(都只比對筆記檔本身那一層)。
- **推送提醒**:一般檔名經過 `_esc_clean` 不變。只有檔名超過 200 字會被截斷,實務上不會發生。

1. 筆記是符號連結時,signoff 和 about-code restamp 會噴 Python 堆疊,signoff 還會留下半套帳。
severity: major
   blocking: 是
   - 輸入:筆記是符號連結(指到庫內或庫外都一樣)。
   - 路徑:`cmd_signoff` 先把簽核寫進 `.signoff-log.jsonl`,再叫 `cmd_set`,然後走到新加的符號連結擋下。`cmd_about_code_restamp` 也直接叫 `cmd_set`。`main()` 對這兩條路徑沒有接 `RuntimeError`,不像 `set`、`append`、`question-*` 在分派層會轉成「擋下:…」rc2。
   - 修前:`signoff Projects/n_計劃 --note ok` 回 rc0,印「✓ signoff」。`about-code restamp` 也回 rc0。
   - 修後:兩支都是 rc1 加完整 Traceback,結尾是 `RuntimeError: 這篇筆記是符號連結…`。signoff 的帳已經寫進去,但筆記的 `signed_off` 沒蓋章,帳和筆記不一致。這跟 R3 宣稱的「擋下講明」不符。
   - 重現:`ln -s <庫外>/e.md kg/Projects/n_計劃.md; lumos --vault kg signoff Projects/n_計劃 --note ok; echo $?`。修前版 rc0,修後版 rc1 加堆疊,`.signoff-log.jsonl` 多一行。
   - 查證檔:`exp2.out`、`exp3.out`。
   - 歸因:有證據的修復回歸。擋下是這次新加的,讓原本只在「沒拿鎖」才可能丟的 `RuntimeError` 變成一般使用者會踩到。未接例外的呼叫點是原本就有的漏接,這次才被觸發。
   - 佐證:`scripts/lumos:19982`、`scripts/lumos:8752`、`scripts/lumos:20719`。
   引句:「if os.path.islink(path):」

2. summary-line 遇到符號連結,先印「改前/改後」才擋下,看起來像已經改了。
severity: minor
   blocking: 否
   - 輸入:`summary-line` 的目標筆記是符號連結(非 `--dry-run`)。
   - 路徑:`_summary_line_locked` 先印兩行,再呼叫 `atomic_write_verify` 時被擋。
   - 修前:印改前/改後和「✓ 改好了」,rc0。實際上是把連結換成一般檔,指到的那篇沒改。
   - 修後:stdout 仍印「改後:…」,stderr 才是「擋下:…」,rc2,檔案沒動。人看到「改後」可能誤以為改成了。`--dry-run` 兩版相同,仍是 rc0。
   - 歸因:有證據的修復回歸,但只是顯示順序,不傷資料。
   - 佐證:`scripts/lumos:20208`。
   引句:「return _summary_line_locked(env, rel, old, new, nth, dry_run)」

3. ⚠ 所有寫開頭欄位的指令對符號連結筆記一律改成擋下。這是設計取捨,不是 bug。
severity: minor
   blocking: 否
   - 修前:set、append、remove、decision-add、question-add、guard bind、guard audit、self-audit、dref add-ai 等,對符號連結筆記回 rc0,但實際上是悄悄把連結換成一般檔,指到的那篇沒改。
   - 修後:一律 rc2,訊息是「請直接改它指到的那一篇」。
   - 我沒找到有正當用途的「寫穿連結」,因為修前也沒有寫穿。如果有人靠符號連結共享筆記(例如核心圖譜的節點),現在要改成改實體檔。`lumos-cli-write.md` 的 WHY 有寫這個決定,但沒列例外。
   - 控制字元:我用 ESC、BEL 和雙向覆寫字元(U+202E)當連結目標跑過,訊息裡都被換成空格,沒有洩漏。macOS 檔名不接受非 UTF-8 位元組,所以那一類沒法造出來測。
   - 歸因:未判定,屬於修補本意。
   - 佐證:`scripts/lumos:19982`。
   引句:「這篇筆記是符號連結(指到 {_esc_clean(os.readlink(path), 160)})」

**三問**
- **① 原問題的修復效果有何行為證據?** 一般 set、append、decision-add 等 22 個呼叫都擋得到符號連結,連結和目標檔不變,訊息裡的控制字元和雙向覆寫字元已清掉。一般筆記的寫入、鎖檢查、summary-line 的四種用法都和修前一致,五個子集全綠。
- **② 修補處的正常、錯誤與相鄰呼叫路徑是否仍成立?** 正常路徑和錯誤路徑成立。相鄰的呼叫端有兩條不成立:signoff 和 about-code restamp 沒接新的 `RuntimeError`(第 1 條)。summary-line 的顯示順序有點誤導(第 2 條)。
- **③ 新發現的同一案例在修前、修後各是什麼結果?**
  - 修前:符號連結筆記跑 signoff 或 restamp,rc0,但連結被換成一般檔。
  - 修後:同一輸入 rc1 加堆疊,signoff 留下半套帳。
  - 其他寫入指令對同一輸入修前 rc0、修後乾淨的 rc2 擋下。

**總結**:修補的主要行為站得住,測試全綠,但符號連結擋下漏接了 signoff 和 about-code restamp 兩個呼叫端,會噴堆疊,signoff 還留下半套帳,所以這輪要擋合併。
