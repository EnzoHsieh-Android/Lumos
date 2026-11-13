severity: clean

## 1. 分層與依賴方向:對齊
新寫的語法樹檢查直接放在 `t_extcode_single_source` 裡,和鄰居一樣。它只用 `_insp`、`_ast`、`_tw` 這幾個標準庫,沒有新增跨層呼叫,也沒有碰被測模組以外的東西。
- 對照:`scripts/test_lumos.py:71266`、`:73065`、`:70723`、`:42204` 都是在測試函式裡就地用 `_ast.walk` 收 `Call` 且 `func` 是 `Name` 的名字。
- 這次的 `_calls` 是同一種寫法,只多了 `inspect.getsource` 加 `textwrap.dedent` 再 `_ast.parse`。這和 `:1150` 附近、`:9855` 附近解析原始碼的既有做法同類。

引句:「called = _calls(m._lens_changed_lines) | _calls(m._extcode_hit)」

## 2. 命名與錯誤處理:對齊
- 命名:`_calls` 是內層函式、以底線開頭,和 `:73064` 的 `_calls(node)` 同名同形,`:71266` 的 `called(name)` 也是同類。`import ast as _ast` 的別名也沿用專案慣例。
- check 寫法:`check("S4 …", 條件, str(sorted(called)))` 失敗時把實際收到的名字集合印出來。舊版的第三個參數是空字串,新版比它更有用,結構沒變。
- 子集比較寫成 `{…} <= called`,和 `:80205` 附近的集合比對一樣。
- Issue 筆記:前置欄位(`type/status/created/updated/aliases/about_code/tags`)、`FLAG:TECHNICAL` 加 `PITFALL:` 摘要行(附 `[出處:][根因:][repro:]`)都和 `Issues/人裁指令中斷收尾邊角與收鎖放錯層.md:13-14` 一致。
- 段落:`## 症狀`、`## 根因`、`## 現在怎麼繞`、`## 什麼條件算修好` 是既有 Issue 常見的段名。我數了 `Issues/` 底下 162 篇,其中 51 篇有「現在怎麼繞」、47 篇有「什麼條件算修好」。

引句:「PITFALL:人裁把 flatMapLatest 換成 flatMapConcat 驗殺傷力時,換完編譯不過(檔頭只 import 了 flatMapLatest),判成弱證據而拒絕寫回」

## 3. 第二種做法:否
- 專案裡沒有共用的「找 Call 名字」頂層 helper。我 grep 了 `def _calls`、`_called_names`、`_call_names` 和 `_ast_calls`,頂層沒有任何一個。
- 既有慣例就是每個測試各自內嵌一份。新增的 `_calls` 是在跟隨這個慣例,所以不算第二種做法。
- 「`_kt_sit_path_ok` 往下查一層」的手工展開,在 `:73067` 附近(用 `defs` 做遞移閉包)也有類似做法。
- 目錄縮短沒有拿掉別處依賴的字。我跑了 `-k t_command_index_complete`,結果 16 passed、0 failed。
  - 這支測試用整個 `commands/*.md` 當比對全文(corpus),而 `kill-add`、`kill-rm`、`reread-*` 等子指令都還在 `06-代碼審與推送.md` 和 INDEX 裡。
  - `:122943`、`:122967`、`:114934` 這些檢查的是 `room-guard`、`test-guard`、手冊檔名這幾個詞,縮短時都沒動。
  - 我沒找到任何測試比對被刪掉的字樣,例如 `--covers`、`--try`、「不帶 --id」或「情境題人裁寫回規格」。
- 不過 `t_command_index_complete` 上限是 4500 字元,這次縮短是為了壓在上限內。這是目錄長度的合理調整,不算不一致。

引句:「# 鏡頭的路徑篩選收進 _kt_sit_path_ok(情境段與型錄自檢共用,情境決策點窮舉計劃),它再叫 _stack_changed_ok:往下查一層」

不對齊共 0 條,其中 major 0 條
