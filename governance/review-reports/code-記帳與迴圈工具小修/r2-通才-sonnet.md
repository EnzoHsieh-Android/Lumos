severity: minor

整體:第 2 輪修補的測試半多數有效。我在 f791d8ba 的複本上做了 17 組拿掉實作或改壞一行的實驗,其中 11 組讓對應測試翻紅。這 11 組是整本帳壞的訊息、`--regression-set` 全空白、`--round` 純空白、編號帶 ESC 的範例指令、suggested 的 evidence 型別、existing 的 null、S33,以及寫側 `rv` 過濾、`_loop_round_format` 內層過濾與 panel、loop next 的外層過濾(後三項要兩處一起拿掉才紅,見下面第 1 條)。S14、S15、S12、S22、S32、S33 的新斷言抓得到它們宣稱要抓的錯。只有下面 4 條站得住。

1. 讀側結局帳過濾有多層重複,測試分不出哪一層在守,回放與跑滿提示路徑沒有行為測試。
severity: minor
   blocking: 否
   - 現場:`_review_rows` 的過濾出現在 `_loop_round_format` 內層(`scripts/lumos:11357`),也出現在 `cmd_loop_status`(`:14058`)、`loop next`(`:16467`)、`_disposal_judge`(`:28397`)三處呼叫端。
   - 實驗結果(拿掉一處,跑 `-k outcome_exempt`):
     - 只拿掉 `:14058` 或只拿掉 `:16467`,全綠。
     - 只拿掉 `:28397`,全綠。
     - 只拿掉 `:11357`,全綠。
     - 內層加 `:14058` 一起拿掉,S14 的 loop next 與 `--panel` 兩條斷言翻紅。
     - 內層加 `:16467` 一起拿掉,S14 的 loop next 斷言翻紅。
     - 內層加 `:28397` 一起拿掉,全綠。
     - 內層加 `:11057`(跑滿提示的 `_cap_hint_scope`)一起拿掉,`-k cap_hint`(40 條)與 `outcome_exempt` 全綠。
   - 原因:
     - S14 的處置閘斷言 `rd` 只做否定檢查(`有的帶輪次` 不在 stderr)。實際走完整條處置閘,輸出是正常的 G3 ✗,這個斷言沒有檢查任何正向結果。
     - loop next 走處置閘時,內層輸出被 redirect 進 buf,`rn.stderr` 裡本來就不會有那句話。我在 `:28397` 與 `:11357` 同時拿掉的情況下對照 loop next 輸出,和原版完全相同。
     - 結局帳之後的 `_cap_hint_scope`、回放(`:9614`)、`loop next` 內的 `_disposal_judge` 呼叫(`:16859`)都沒有行為測試。
   - 要改的話:要嘛砍到只留一層,要嘛補測試。補法是在這三處之後各放一筆結局帳,斷言正向輸出,例如處置閘第 N 步的內容,不要只斷言「沒有某句話」。
   - 引句:「check("S14 結局帳之後處置閘不判混用", "有的帶輪次" not in rd.stderr and "分不出哪輪" not in rd.stderr, rd.stderr[-300:])」
   - 歸因:未判定。修前沒有這些過濾,但這是新增守衛的測試覆蓋缺口,不是回歸。

2. S17 那條斷言的名稱和它實際斷言的結果相反,測試函式的 docstring 也沒跟著改。
severity: minor
   blocking: 否
   - 斷言標籤寫「沒有人裁紀錄的迴圈不受跑滿回顧影響」,條件卻是 `r.returncode == 2 and ... "讀不懂" in r.stderr`,也就是被擋下。
   - 函式 docstring 還寫「沒人裁的不受影響」。
   - 照標籤讀,會以為這個迴圈能照常記帳,實際上是被輪次規則擋下。
   - 原本要守的「跑滿回顧只擋有人裁紀錄的迴圈」現在只靠新加的 `t_cap_retro_only_blocks_decided_loops`。我拿掉那個守衛(把 `applies` 為假時的 `return None` 換成 `pass`),S33 的 B 斷言翻紅,所以新測試是有效的。
   - 要改:S17 標籤和 docstring 改成實際行為,例如「帳壞時沒人裁的迴圈改由輪次規則擋(不落 cap-ledger-bad)」。
   - 引句:「check("S17 沒有人裁紀錄的迴圈不受跑滿回顧影響(不落 cap-ledger-bad;帳壞改由輪次規則擋)」
   - 歸因:有證據的修復造成。這條斷言的語意是第 2 輪改的,上一輪改的是期望值,這輪只補了註解。

3. 「編號帶 ESC 與換行」的測試只覆蓋 `first-no-round` 這一條路徑。
severity: minor
   blocking: 否
   - 把 `:11407` 的 `_esc_clean(loop, 60)` 拿掉,`-k t_canary_record_`(129 條)全綠。
   - 這是 `code-first-no-tier` 路徑,編號以 `code-` 開頭、沒帶 `--tier` 也沒帶 `--round`,訊息裡直接印編號。
   - 拿掉 `:11386` 的 `q = _shlex.quote(_esc_clean(...))` 則會讓 S10 翻紅,所以只有 `first-no-round` 受保護。
   - 要補的話,再加一個不帶 `--tier` 的 `\x1b` 編號案例即可。
   - 引句:「check("S10 編號帶 ESC 與換行:訊息裡的範例指令過 _esc_clean", r.returncode == 2 and "\x1b" not in r.stderr, repr(r.stderr[-200:]))」
   - 歸因:未判定。

4. S14 的 loop next 斷言用 `returncode != 2` 加否定字串,太鬆。
severity: minor
   blocking: 否
   - 修後 loop next 的 returncode 是 1(正常的 gate-pending),所以 `!= 2` 能過;但任何非 2 的 rc,包含參數錯誤之外的其他失敗,也都會過。
   - 把 loop next 的外層過濾和內層過濾一起拿掉後,這條會翻紅,所以它有抓到東西。但如果混用守衛的文字被改掉,這條會靜默變成永遠通過。
   - 改法:加一條正向斷言,例如輸出包含 `disposal_cmd` 或某個 phase 字樣。
   - 引句:「check("S14 結局帳之後 loop next 不判混用", rn.returncode != 2 and "有的帶輪次" not in rn.stderr, rn.stderr[-300:])」
   - 歸因:未判定。

三問回答:
- ①原問題的修復效果:S15 的反向對照(之後不帶輪次的審查帳仍被混用擋,而且筆數不含結局帳)有行為證據。把寫側 `rv` 過濾拿掉(`:11393`)後翻紅:「這個審查編號既有 2 筆裡 1 筆帶輪次…」。其餘讀側過濾的證據見第 1 條。
- ②修補處的相鄰路徑:
  - S9 整本帳壞和單編號壞的訊息區分有效,把 `whole_ledger_bad` 改成 False 即翻紅。
  - `--regression-set` 全空白與 `none,` 有效,改成 `not regression_set` 即翻紅。
  - `--round` 純空白有效。
  - suggested 的 evidence 型別有效,三種型別全翻紅。
  - existing 的 null 有效。
  - S12「換新編號」的措辭已驗過,拿掉實作會紅。
- ③新發現的修前修後差異:第 1、3、4 條在修前沒有對應過濾或測試,是新增覆蓋缺口,不是行為回歸。第 2 條的語意在第 2 輪才改,屬於修復造成。

未驗範圍:
- 完整 `test_lumos.py` 沒跑,只跑了相關子集。`t_canary_record_` 129 條全綠。
- `t_seq_cap_and_roster` 在修前(d2da0e8c)和修後我這邊都因 JSON 解析失敗而紅(`Expecting value: line 1 column 1`)。兩版一樣,判定為環境問題,與本次修補無關,未深究。
- 另外只驗了 `t_cap_retro_bad_ledger_fail_closed` 的 S17 斷言,沒逐條重驗它其餘的斷言。

清理:實驗用的複本與腳本已刪。我自己兩次紅燈留下的 gctl-run 現場已刪(`gctl-run-su9v0hkv`、`gctl-run-b8y4ez3v`)。mutation 紅燈留下的其他 gctl-run 現場我分不出哪些是我的,按規則沒用萬用字元刪。

最嚴重 severity:minor,blocking 共 0 條。
