severity: major

1. 控制字元過濾另寫了一套,沒重用同檔的 `_esc_clean`
severity: major
blocking: 是
引句:「snippet = "".join(c for c in re.sub(r"\s+", " ", first) if unicodedata.category(c) not in ("Cc", "Cf")).strip()[:60] if first else "-"」
file: `scripts/lumos:12328`(既有的 `_esc_clean`)、`scripts/lumos:7132`(既有的 `_PATH_SPECIAL_CATS` 用法)
- 要做的事是把審查席可控的文字寫進治理帳之前,先清掉終端控制序列。同一支檔已經有專門做這件事的 `_esc_clean`:它清 C0、DEL、C1、雙向覆寫與隔離字元,也處理孤立代理字元,並有截斷。它的 docstring 還寫明:換成空格的有損清洗用 `_esc_clean`,要無損跳脫才用 `_PATH_SPECIAL_CATS` 那組,「兩種用途不併」。
- 這次修補第三種做法:用 `unicodedata.category` 判 `Cc` 和 `Cf`,把字元直接刪掉。
- 這套寫法跟 `_esc_clean` 有兩處不一樣:
  - 它整類刪掉 `Cf`,會把 ZWJ 和軟連字號刪掉,而 `_esc_clean` 刻意保留它們。
  - 它不處理 `_esc_clean` 會處理的情況,例如 U+2028 與 U+2029 不在 `Cc`/`Cf` 裡,也不會被濾掉。
- 該重用的是 `_esc_clean(first, 60)`。要先壓空白的話,再前置一次 `re.sub`。
- `unicodedata` 在檔頭 line 63 已經 import,函式內又 `import unicodedata`,這是順帶的重複。

2. 印給人照抄的診斷指令:有現成的 `_sh_quote`,又在函式內另 import shlex
severity: minor
blocking: 否
引句:「import shlex as _shlex_q   # 印給人照抄的指令,路徑加引號(同檔回放過期提示的做法;代碼審 r1 回滾席)」
file: `scripts/lumos:450`(模組層 `_sh_quote`,docstring 寫的就是「印給人照貼的指令裡的一個參數加 shell 引號」)、`scripts/lumos:1251`
- ⚠ 既有寫法有兩種:函式內 `import shlex as _shlex`(line 1251、15670 等)和 `_sh_quote`(line 17433、24220、36869 等),所以這不算新引入第二種做法。
- 新程式碼選了 `_shlex_q` 這個新別名,成了第三種拼法。診斷指令用模組層的 `_sh_quote(str(rp))` 就夠。
- 同檔 line 14648 和 14655 的 `_retro_cmd` 家族,是 `shlex.quote` 後再過 `_esc_clean`,因為帳上路徑可能含控制字元。這裡 `rp`、`sp` 是帳上的路徑,`shlex.quote` 不會去掉 ESC,控制字元仍會原樣印到終端。這條跟第 1 條同源,但 line 1251 也沒清,所以只標 ⚠。

3. MemoryError 只在處置閘一處照常往外丟,同一功能的其他 `except Exception` 沒跟上
severity: minor
blocking: 否
引句:「except MemoryError:      # 資源不足不是判準的錯,照常往外丟(代碼審 r1 資源席:否則會被當成判準丟例外凍成判失敗)」
file: `scripts/lumos:25979`(`_quote_block_note` 的 `except Exception`)
- ⚠ repo 裡沒有「先 `except MemoryError: raise` 再 `except Exception`」的既有寫法。既有的 MemoryError 處理是 line 38352 和 39285,那兩處是把它跟 SyntaxError 一起當「解析不了」處理,方向相反。
- 同一功能內的寫側 `_quote_block_note` 仍用 `except Exception` 吞掉 MemoryError,記成 `kind=unknown`。處置閘讀側與寫側因此對同一個資源錯誤的處理不一致。
- `_quote_compare_rules` 的 `_quote_rows` 呼叫沒有任何 try,MemoryError 本來就會往外丟。
- 如果要統一,只要這個功能三處採同一種處理,不用另立規則。

沒有列入 finding 的檢查:
- 比較模式帳上路徑的防線,寫法是 `resolve()` 之後 `is_relative_to(root_real)` 加 `is_file()`。
  - repo 內判「路徑必須在根底下」的寫法有兩種,`resolve().relative_to(root)` 加 `except ValueError`(line 21069、21092、26299)和 `is_relative_to`(line 14096、27319)。
  - 新寫法屬於其中一種,沒有引入第二種做法。
  - repo 裡沒有可重用的共用函式,`_about_code_path` 和 `_events_path_safe` 都綁各自的場景。
  - `_read` 沒有跨層直呼。

總結:最高等級 major,blocking 共 1 條
