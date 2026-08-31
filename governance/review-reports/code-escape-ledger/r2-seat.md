# esc r2 終態回歸席(全新)

F2-1|major|blocking:是:既存 symlink 繞過建檔保護,共用寫入原語 open('a') 跟隨連結——實測寫進外部檔 rc0。對照 _ledger_append 每次寫都 O_NOFOLLOW。
引句:「此原語=OSError 擋下+讀回自驗(canary 家族同款)」
F2-2|minor|blocking:是:兩則 stderr 訊息洩內部審次代號(「r1 兩席」「r1 外家裁」),違反白話三段式「代號全砍」條款。
引句:「照原樣執行你會以為記了其實一筆都沒寫(r1 兩席實測的靜默吞資料)」
F2-3|minor:token 撞鍵時讀回比對可能對到舊筆——canary 全家族既有天花板,非本批新引入。
引句:「rc_w = _jsonl_append_verified(log, rec, "token", rec["token"])」

severity: major
