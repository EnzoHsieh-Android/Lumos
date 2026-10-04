severity: clean

## 已走過沒問題的範圍
引句:「(old_start_line + "\n" + old_body + "\n").splitlines(keepends=True),」
- body 由 _expected_claude_body 與 _extract_claude_block_span 兩端皆 strip("\n"),故補的 "\n" 不會讓舊 body 已換行結尾的情況多出空行;只差版本號、body 相同時兩邊同補,只剩 START 行差異;完全相同走 unchanged 早退,不會印差異。實測 difflib:最後一行 B 換 C 輸出 "-B\n+C\n" 不黏;相同輸入輸出空字串。
- 補換行只影響 out["diff"];new_text、version_only、status 在 diff 組裝之前已定,未受影響。呼叫端 _reinject_all 只取 diff.splitlines()[:20],doctor/init 不讀 diff。
- 引句:「q = _sh_quote(str(Path(src).resolve()))」_sh_quote 內部就是 shlex.quote,輸出相同;file: `scripts/lumos:438`
- 引句:「print(f"  root: {root}")」grep scripts/test_lumos.py、docs、skills、commands 無找舊字樣「專案: 」的斷言或文件。
- 引句:「lines = [ln.strip() for ln in r.stdout.splitlines()]」新斷言夾具舊 body 為單行且為區塊最後一行,舊程式會輸出 "-舊版…+新版…" 黏一行,整行比對 "-舊版紀律:docs/p-knowledge/" in lines 必翻紅;新程式為獨立行才為真。python3.14 scripts/test_lumos.py -k update_dry_run 28 passed。

整份變更只動 diff 顯示的換行與標籤,未發現會出錯的輸入。
