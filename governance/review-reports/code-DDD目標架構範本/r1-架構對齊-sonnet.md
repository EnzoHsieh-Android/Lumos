severity: minor

我逐問對照了既有檔。結論是整體結構跟鄰居一致,沒有引入第二套架構,也沒有跨層直呼。有四處小差異,都屬 minor,沒有 major。

## 1. 分層與依賴方向

新檔的放法跟鄰居一致。它跟 `test-quality-standard.md` 一樣是 `commands/` 下不帶編號、檔名用英文短橫線的專題檔,自己引用別的說明檔也用同樣的 Markdown 相對連結。

- 新檔指向 06 用 `[06-代碼審與推送.md](06-代碼審與推送.md)`,指向 03 用 `[03-寫回圖譜.md](03-寫回圖譜.md)`。這跟既有的 `[測試品質接入標準](test-quality-standard.md)` 寫法一樣。
  - file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:45`
- INDEX.md 沒收錄新檔,但鄰居 `test-quality-standard.md` 也沒進 INDEX(INDEX 只列九個編號子檔),所以這點對齊。
- 新檔只被 06 的 `arch_targets` 那一列指到。鄰居 `test-quality-standard.md` 被兩處指到:SKILL.md 的進場提示,和 03 的〈實作測試品質〉段。新檔少了 SKILL.md 這一條入口。
  - file: `skills/lumos-project-notes/SKILL.md:9`
  - file: `skills/lumos-project-notes/commands/03-寫回圖譜.md:45`
  - 新檔位置在 06 的 `arch_targets` 列上,主題對得上,所以不算結構錯誤,記成 minor。

ARC-1
引句:「DDD 可直接抄 [target-arch-ddd-template.md](target-arch-ddd-template.md) 的九條範本」
file: `skills/lumos-project-notes/SKILL.md:9`
severity: minor
blocking: 否

## 2. 命名與錯誤處理

測試命名、docstring、收尾印法都跟鄰居一致。

- 命名沿用 `t_arch_target_*` 一族。
- docstring 帶 `翻紅釘:`,收尾印 `print("  ✓ t_...")`。
- 前置斷言放在 `check("前置:…")`。
- 計劃筆記的章節順序(問題與最小解、做法、驗收條款、回退、實務隱患)和 `[S1]` 條款句式,跟 `架構對齊可宣告目標架構_計劃` 一樣。

有兩處寫法跟鄰居不同。

第一,測試夾具。
- 專案測試建臨時圖譜的慣用法是 `mkvault()`,在 `scripts/test_lumos.py` 裡用了 355 次。它會建私有 mkdtemp、`Systems` 等子目錄和 `MOC/idx.md`,再用 `run(v, "lint", ...)`。
  - file: `scripts/test_lumos.py:176-186`
  - 對照用法:`scripts/test_lumos.py:2451`
- 新增的 `_ddd_template_lint` 自己手建一個 `mkdtemp/docs/t-knowledge`,只建 `Systems`,又寫了一條新夾具路徑。
- 我沒有實跑確認用 `mkvault()` 是否同樣讓 lint 回 0 問題,所以 ⚠ 交編排者:若能直接換成 `mkvault()`,這條更接近 major(專案已有同功能的夾具)。

ARC-2
引句:「v = Path(tempfile.mkdtemp(prefix="gctl-ddd-")) / "docs" / "t-knowledge"」
file: `scripts/test_lumos.py:176-186`
severity: minor
blocking: 否

第二,讀 skills 檔案的守門。
- 讀來源 repo 專屬檔的測試,近期寫法是先 `_need_src(rel)`,消費端沒有該檔就記成 skip,不記失敗。
  - file: `scripts/test_lumos.py:8602`
  - file: `scripts/test_lumos.py:65316`
- 新測試改用 `check("前置:範本檔存在", doc.is_file(), ...)`,缺檔會記成失敗而不是 skip。
- 但讀 skills 檔案卻不守門的舊測試也不少:`t_command_index_complete`(`scripts/test_lumos.py:8165`)就沒守,用 `_need_src(` 的只有約 10 處。這條所以不確定,⚠ 交編排者。

ARC-3
引句:「check("前置:範本檔存在", doc.is_file(), str(doc))」
file: `scripts/test_lumos.py:65316`
severity: minor
blocking: 否

## 3. 第二種做法

沒有發現自創的規則引擎或新指令。S1 讀規則時用 `m._arch_target_note_rules` 加 `m._note_from_text`,是 `_load_lumos_inproc()` 的既有用法,見 `scripts/test_lumos.py:32812` 和 `:33472`。取日期的寫法抄 `scripts/lumos:41865` 的 `_arch_target_note_rules`,有註解交代。

只有一處新做法:從說明檔裡抽範本。
- 新檔用 `<!-- 範本開始 -->`/`<!-- 範本結束 -->` 兩個註解加 markdown 圍欄,測試再用正則取出。
- 既有讀說明檔的測試,是用 `split("## 標題")` 取小節,例如 `scripts/test_lumos.py:65316` 附近那支。
- 既有說明檔裡的 `<!-- -->` 都不是這個用途,出現在 `03:112` 和 `scripts/templates/*`。
- 這是專案裡第一個「說明檔內嵌可抽取範本」的做法。它只在測試內部使用,不影響其他讀法,所以記 minor。

ARC-4
引句:「m = _re.search(r"<!-- 範本開始 -->\n```markdown\n(.*?)\n```\n<!-- 範本結束 -->"」
file: `scripts/test_lumos.py:65316`
severity: minor
blocking: 否

不對齊共 4 條,其中 major 0 條

總結最嚴重 severity: minor
