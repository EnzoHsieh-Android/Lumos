severity: major

# 編排者實際追加發現與修復紀錄

本報告是編排者自行重現所得，不是乾淨審查員或另一家族驗收；引句是最後修復來源，修前故障及來源各見原始控制收據。前四項後於957修復，後兩項957已包含修復，不能混稱全部都是957之後新增修補。

## author-change-window 活動改動清單不能替固定Git樹背書

severity: major
blocking: 是
引句:「changed_paths = {p for _c, old_path, new_path in changes for p in (old_path, new_path) if p}」
固定同案例修前兩項紅、修後16綠；r3-fixed-source-boundaries。

## author-version-config 起終版本各自讀設定

severity: major
blocking: 是
引句:「old_read = _nodehome_reader(repo_root, B.where, from_git=True)」
固定同案例修前四項紅、修後18綠；只限index補助，不改push-end政策。

## author-read-limits 新宣告重讀需要單筆、整批與共享截止

severity: major
blocking: 是
引句:「256 * 1024, timeout=5, max_total_bytes=8 * 1024 * 1024,」
固定控制before22紅、after32綠；診斷文字誤斷言另留原輸出。

## author-owner-isolation 其他合法家不能替本篇途中假宣告作證

severity: major
blocking: 是
引句:「candidates = (possible & (old | captured)) - untrusted」
固定控制before2紅、after358子集綠；r3-owner-isolation-proof。

## author-test-writer 測試本身固定字元窗會漏寫入點

severity: minor
blocking: 否
引句:「home_writer = next(n for n in _ast.parse(src).body」
早於957修復，完整函式故障挑戰writer_removed與wrong_kind均咬指定斷言；r3-drift-preflight。

## author-role-card-fixture 預設卡片是否啟用要由fixture明確宣告

severity: minor
blocking: 否
引句:「card_ids = [q["id"] for cards in _load_lumos_inproc()._ROLE_CARDS.values() for q in cards]」
早於957修復；原11923/1真紅與當時fixture控制封存；454子集包含本方法。
