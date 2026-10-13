severity: minor

我在 `/tmp/lumos-seat-work/code-待決問題改存開頭欄位/r7-通才回歸-sonnet/` 放了修前(19bd4719)和修後(36d4ffed)兩份 clone。每份用一份相同的臨時筆記庫,各跑 31 支指令,涵蓋正常、CRLF、BOM、非 UTF-8、無開頭欄位、符號連結(庫內、庫外、壞連結)、唯讀、讀不到等情況。逐支比 stdout、stderr、rc 和檔案內容。批次類指令(`reindex --all`、`updated-sync`)另外讓兩篇筆記都壞,比對有沒有略過一篇繼續下一篇。找不到會擋合併的問題,以下是會讓人踩到的行為差異。

1. 符號連結筆記:唯讀路徑被新的拒絕規則波及
severity: minor
blocking: 否
- 輸入:筆記是符號連結,指到庫內或庫外的檔都一樣。
- 走到的程式:`load_raw_for_edit` 開頭新增 `_write_symlink_reason`,讀檔前就丟 `WriteBlocked`。這支原本只讀,所以以前不寫入的呼叫也會被擋。
- 差異一:`lumos guard bind Systems/N "foo bar" t_foo`,合約已綁好、不需寫入。修前輸出「已綁 [test:t_foo],無需重綁」,rc0。修後 rc2,印「擋下:這篇筆記是符號連結…」。
- 差異二:doctor 的 P2「配方驗的測試不在合約清單上」提醒走 `_kill_p2_unbound`,它先呼叫 `_kill_read_recipes` 再呼叫 `load_raw_for_edit`,外面包 `except Exception: continue`。符號連結筆記現在被靜默略過。
- 重現:在 `p2.py` 對同一份帶 `kill_recipes` 的筆記呼叫 `_kill_p2_unbound`。修前和修後的一般檔都回 1 條提醒。符號連結版修前回 1 條,修後回 `[]`。
- 影響:唯讀的提醒與無需寫入的 no-op 被寫入端的規則波及。符號連結筆記不多,所以只算小問題。
- 歸因:有證據的修復回歸。
- 兩版命令:`python3.14 h.py symlink g-bind`(修前 rc0,修後 rc2);`python3.14 p2.py before link` 和 `python3.14 p2.py after link`。
引句:「why = _write_symlink_reason(path)」
佐證:file: `scripts/lumos:20368`(`load_raw_for_edit`)、`scripts/lumos:17311`(`_kill_p2_unbound`)。

2. signoff 成功時 stdout 少了一行
severity: minor
blocking: 否
- 輸入:正常的 `lumos signoff Systems/N --note ok`。
- 走到的程式:`_signoff_write_locked` 用 `contextlib.redirect_stdout(set_out)` 吞掉了 `_cmd_set_locked` 的輸出。
- 差異:修前 stdout 兩行,第一行是 `✓ set Systems/N.md: signed_off 已改成 "2026-10-13"`,第二行是 `✓ signoff …`。修後只剩第二行。rc 都是 0,帳和筆記都寫了。
- 影響:派工單要求「輸出逐字與修前相同」,這點沒做到。`-k signoff` 的測試沒抓到這個差異。
- 歸因:有證據的修復回歸。
- 兩版命令:`python3.14 h.py normal signoff`。
引句:「with contextlib.redirect_stdout(set_out):」
佐證:file: `scripts/lumos:9105`。

3. ⚠ signoff 失敗還原時,可能蓋掉別的會談剛寫的筆記
severity: minor
blocking: 否
- 輸入:signoff 在鎖外先讀 `original`,拿鎖之後才寫。這段空檔內另一個程序改了同一篇,接著帳檔追加失敗。
- 走到的程式:`scripts/lumos:9138` 先讀原稿,`scripts/lumos:9088` 的 `_signoff_restore` 把這份舊內容寫回。
- 重現:`race.py` 在 `_vault_write_lock` 前插一次加 `tags` 的改動,並讓帳檔 open 丟 `PermissionError`。結果是 `WriteBlocked`,筆記被還原成舊內容,別人加的 `other-session-edit` 消失(印出 False)。
- 修前:先寫帳、再 `cmd_set`,沒有用舊內容覆寫的動作,不會蓋掉別人的改動。
- 判斷:需要帳檔寫入失敗,又剛好有並行寫入,機率低。修法是把讀原稿移進鎖內。
- 歸因:有證據的修復回歸。
- 兩版命令:`python3.14 race.py` 在修後是 False。修前沒有等價路徑,是讀碼判斷。
引句:「original = _signoff_read_original(path)」
佐證:file: `scripts/lumos:9138`、`scripts/lumos:9088`。

4. `guard kill` 讀 BOM 筆記時錯誤訊息變得誤導
severity: minor
blocking: 否
- 輸入:筆記開頭帶 BOM。
- 走到的程式:`_kill_read_recipes` 改用 `read_text(utf-8)` 加 `split_frontmatter`,BOM 沒被去掉。
- 差異:修前訊息是「這個檔開頭帶 BOM 標記…」。修後是「frontmatter 解析失敗: 開頭沒有欄位區塊」,但檔案其實有欄位區塊。rc 兩邊都是 2。CRLF 筆記修前被拒,現在改成能讀,這點無害。
- 歸因:有證據的修復回歸(只影響訊息)。
- 兩版命令:`python3.14 h.py bom g-kill`。
引句:「return None, "frontmatter 解析失敗: 開頭沒有欄位區塊"」
佐證:file: `scripts/lumos:16823`。

沒找到問題的項目,這些是「原本只接 ValueError 的批次迴圈會不會中斷」那類擔心的結果:
- **批次迴圈:** `reindex --all` 在 CRLF 筆記(N、M 兩篇都壞,兩版都不中斷)下,兩版都是逐篇印 ✗、統計「0 處理 / 2 拒絕」、rc2。其中 `Systems/M.md` 的 ✗ 行訊息長相相同。
- **`_drift_fix_load` 與 `updated-sync`:** 都接得住 `WriteBlocked`。
- **重複印兩次:** 全部情境裡沒有「擋下」印兩次的案例。
- **traceback 變成 rc2:** 修前直接噴 traceback、rc1 的情況(壞連結、讀不到、非 UTF-8、signoff 遇 CRLF/BOM/符號連結),修後全部是乾淨的「擋下」加 rc2,其中 signoff 的 `FILEDIFF` 是修前留下半截帳,修後不留。
- **rc 反過來:** 沒有。唯一的 rc 變動是 rc1 變 rc2,而且都是 traceback 變乾淨訊息。
- **CRLF 訊息:** 文字有一處小改(`.,或` 變 `.。或`),無害。
- **`guard kill`:** 讀到非 UTF-8 仍是 rc1,`t_kill_recipe_check_matches_guard_kill` 綠。
- **鎖被占住:** 沒做端到端。程式裡 `WriteBlocked` 同時是 ValueError 和 RuntimeError,舊的接法都還接得住。
- **測試子集(修後):** 全綠,0 failed。
  - `signoff` 15、`summary_line` 27、`guard_` 592、`drift` 1076。
  - `set_` 155、`append` 215、`decision` 127、`cascade` 52。
  - `kill_recipe_check` 96、`qfm_r6` 13、`qfm_r7` 21。

圖譜鏡頭:
- `lumos-cli-write.md:124` 還寫「任一步丟 `RuntimeError`」,同篇第 118 行已寫成 `WriteBlocked`。程式以 `WriteBlocked` 為準(它同時是 RuntimeError 子類),所以這是筆記內部不一致,應立一篇 Issue。
- 該筆記第 118 行沒說符號連結拒絕也會波及唯讀呼叫端,即上面第 1 條。
- `規格閘.md` 第 156 行「讀法讀得懂 CRLF/BOM、指令寫不進去」與程式一致。
- `lumos-cli-read.md` 和 `bound-tests-gate.md` 的內容與這次改動無牴觸。

三問:
- **①原問題的修復效果:** 有行為證據。修前的 traceback、rc1 和 signoff 只寫一半的帳,修後都變成乾淨的 rc2,帳和筆記兩邊都不留半截(見上面第三項,例如 `crlf/signoff`、`bom/signoff`、`broken/*`、`unreadable/*`、`symlink/signoff` 的修前修後對照)。
- **②修補處的正常、錯誤與相鄰路徑:**
  - 正常路徑:除第 2 條 signoff 少一行 stdout 之外,31 支指令的 rc 與 stdout 都和修前相同。
  - 錯誤路徑:只有 rc1 變 rc2、traceback 變乾淨訊息,沒有反向。
  - 相鄰路徑:唯讀呼叫端被符號連結規則波及(第 1 條)、signoff 的還原有競態(第 3 條)。
- **③新發現案例的修前修後:**
  - 符號連結 `guard bind`:修前 rc0,修後 rc2。
  - P2 提醒:修前 1 條,修後 0 條。
  - signoff 輸出:修前 2 行,修後 1 行。
  - signoff 競態:修前不會蓋掉別人的改動,修後會。
  - BOM 的 `guard kill`:兩版 rc 同為 2,訊息不同。

總結:這次修補在寫入端和錯誤端的行為都成立,測試子集全綠,留下的都是不擋合併的小回歸,建議在合併前順手收掉。
