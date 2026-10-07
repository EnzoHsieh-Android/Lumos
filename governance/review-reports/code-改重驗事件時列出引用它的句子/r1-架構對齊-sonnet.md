severity: minor

我沒有看到「lumos 自動附加」段(0 篇),所以下面只依凍結快照的正文與程式碼對照。

**1. 分層與依賴方向:對齊。**
- 新碼是模組層函式,由 main 的 set 分支呼叫,依賴方向是 main 到列出函式再到讀取和比對工具。這跟既有幾個列出函式一樣(`/tmp/code-b5/l.py:50501` 對照 `:50507`)。
- 它只呼叫 `_search_visible_lines`、`_inline_hidden`、`env.resolve`、`link_target`、`_esc_clean`,沒有跨層直呼。
- 放置位置跟鄰居不同。鄰居 `_drift_print_backrefs`、`_closing_revisits` 在 drift 區(約 35000 行以後),新碼放在 doctor S21 旁(4150 行)。原因是它沿用 S21 的 `_RREF_LINK`、`_RREF_NOT_END`,依賴方向沒有倒。

**2. 命名與錯誤處理:大致對齊,有兩處不一致。**
- 對齊的部分:
  - 命名是 `_print_*` 加 `_*_lines`,跟鄰居一樣。
  - 標題句帶「(只列出、不擋)」。
  - 行前綴是「  · 」,內容走 `_esc_clean(…, 200)`。
  - 讀改完內容用 `_phys_path` 加 `read_text(encoding="utf-8-sig")`,例外只收 `(OSError, UnicodeDecodeError)` 後靜默 return,跟 `_closing_revisits`(35378 行起)和 `_closing_pending_decisions`(35402 行起)一致。
  - 唯一差別是它多包了一層 `_note_from_text(...).fields`,因為要取欄位值而不是行,這是合理的。
- 不一致的兩處見 A1、A2。

**3. 第二種做法:沒有。**
- 專案裡沒有現成的「連到某篇的那一句」索引。`env.edges` 只到筆記層級,沒有句子。`_drift_backrefs` 的篩選條件是「同一子句寫待定」,條件不同,不能重用。
- 連結比對沿用 S21 的做法:`_RREF_LINK`、`_inline_hidden`、`_search_visible_lines(…, False)`、`env.resolve(link_target(…))`。`_in_spans` 是把 S21 內嵌的二分函式提出來共用,反而去掉重複。
- 切句用 `_SENT_END_RE` 的 `finditer` 加 `search`,既有的做法是 `split(maxsplit=1)`(4087、4113 行),寫法略不同,但句尾定義是同一支,不算第二種做法。

## A1 列出行數沒有上限
severity: minor
blocking: 否
引句:「    for src, no, raw in rows:」
佐證:file: `/tmp/code-b5/l.py:35023`
失敗場景:`_drift_print_backrefs` 用 `rows[:20]`,超過時印「…還有 N 行」(35023 行起)。新函式把全部引用句都印出來。大庫裡一次 `set revalidate_when` 可能印出很長的清單,跟鄰居的輸出紀律不同。

## A2 掃全庫的部分沒有 fail-open
severity: minor
blocking: 否
引句:「    rows = _revalidate_backref_lines(env, rel)」
佐證:file: `/tmp/code-b5/l.py:35013`
失敗場景:`_drift_print_backrefs` 在掃全庫外面包 `try/except`,出錯時在 stderr 說一句「寫入照樣完成了」,不改回傳碼。新函式的全庫掃描沒有這層保護。`env_text` 已吞掉讀檔錯誤,所以目前的風險小。但掃描中如果拋出 `ValueError` 或 `RuntimeError`,例外會穿出 main 的 set 分支,變成寫入已完成卻回報失敗。同一分支下的 `_drift_print_followups` 也沒包,所以鄰居內部本身就有兩種做法。

不對齊共 2 條,其中重大 0 條
總結: 新程式的結構和既有做法一致,沒有另寫一套找連結或切句的邏輯;只有輸出沒設行數上限、掃描沒包安全網這兩處小差異。
