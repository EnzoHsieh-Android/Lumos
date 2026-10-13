severity: major

1. 擋下事件片段的消毒是 repo 裡的第三套寫法,既有的 `_events_clean` 可以直接用
severity: major
blocking: 是
引句:「另外濾掉 Cf(標籤字元、方向標記、零寬)與 Co(私用區),」
file: `scripts/lumos:25844`(`_quote_block_note` 的 snippet 那行)
- 新寫法:`_esc_clean(first[:400], 400)` 之後,用 `unicodedata.category(c) not in ("Cf","Co")` 逐字元丟掉。
- 既有對照一:`_events_clean`(`scripts/lumos:27189-27194`)。它的 docstring 寫「沿用既有兩道(不另寫第三套):_esc_clean 再加 _PATH_SPECIAL_CATS 換空格」,用在事件帳印到終端前。
- 既有對照二:`_note_reread_show`(`scripts/lumos:36292-36297`),同樣是 `_esc_clean` 後接 `_PATH_SPECIAL_CATS` 變體。
- `_PATH_SPECIAL_CATS`(`scripts/lumos:36271`)已含 Cc/Cf/Zl/Zp/Cs,所以 Cf 這一半是重做。
- 第三套與既有兩套有三處不同:
  - 新寫的是「刪掉」,既有的是「換空格」。
  - 多了 Co,既有的 `_PATH_SPECIAL_CATS` 沒有 Co。
  - 不處理 Zl/Zp 和 Cs。
- Zl/Zp 在這裡會被後面的 `re.sub(r"\s+", " ", …)` 吃掉,但 `re.sub` 在 Cf 過濾之前,不構成缺口。Cs 已被 `_esc_clean` 換掉。
- 「刪掉」和「換空格」的差別沒有載重理由,測試期望 `quote=甲乙` 只是順著新寫法定的。
- 這是前三輪同一類「補防護前先找既有」問題的再犯。上一輪才在代碼審手冊步驟 5 加了這條規定,卻沒照做。
- 較貼切的做法:呼叫 `_events_clean(first[:400], 400)`,Co 這一類另補一層並註明理由。Co 若確實需要,應補進共用組或做成 `_events_clean` 的參數,不要在呼叫點另寫一個過濾迴圈。

2. 比較模式讀檔的「解析後要在 repo 內」是 repo 裡的第二套寫法
severity: major
blocking: 是
引句:「if not fp.is_relative_to(root_real):」
file: `scripts/lumos:26728`(對照:`scripts/lumos:35890-35908` 的 `_repo_path_unsafe`)
- `_repo_path_unsafe` 的 docstring 明寫:「逐層擋符號連結+解析後要在 repo 內只有這一份」。
- 同檔還有一個先例:`_retro_path_unsafe` 的 docstring 說「不另寫 realpath/startswith」,因為自寫版會放行「上層是捷徑」。r3 就是因此被點出來。
- 這裡 `_read` 的做法是 `Path.resolve()` 後 `is_relative_to`。這正是自寫版的形狀。
- 它跟隨中間層的符號連結,只要最終解析結果在 repo 內就放行。`_regular_own_fd` 只擋最後一段。
- 帳上路徑是不可信輸入。跟 `_repo_path_unsafe` 比,這裡少了「逐層符號連結」這道。
- ⚠ 這份政策差異算不算漏洞,我判不準。但就寫法一致性,這是引入第二種做法。
- 較貼切的做法:`_repo_path_unsafe(root, rel)` 回非 None 就視為讀不到,再交給 `_retro_read_bytes`。

3. 重用 `_retro_read_bytes` 的對象合理,但它的超限錯誤訊息寫死「256KB」
severity: minor
blocking: 否
引句:「raw, err = _retro_read_bytes(fp, limit=cap)」
file: `scripts/lumos:14567-14588`(`_retro_read_bytes` 的 `超過 256KB` 字串)
- `_retro_read_bytes` 同檔已有 `limit=None` 的治理帳用法(`scripts/lumos:14519`)。跨域重用本身沒問題,底層 `_regular_own_fd` 也對。
- 但超限訊息寫死「超過 256KB」。比較模式的上限是 128MB 與 4MB,這個訊息會變成誤導。
- `_read` 目前把它包成 `OSError(err)` 後,在呼叫端只當作「讀不到」計數,訊息不外露,所以影響很小。
- 建議把訊息改成帶 `limit` 的格式字串。

其他確認過、沒有問題的地方:
- `_drift_sh(..., node=True)` 的用法對:開頭是 `-` 補成 `./`、含空白加引號,跟同檔 `_drift_fix_hint` 的用法一致。
- 診斷整行再過 `_esc_clean`,不是第二套。
- `except MemoryError: raise` 的規則在三處一致。
- 整條分支沒看到其他自寫的第二套。比較模式 `_read` 的換行統一是 `read_text` 的行為,是對照而不是重做。

總結:最高等級 major,blocking 共 2 條
