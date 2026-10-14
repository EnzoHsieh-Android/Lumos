severity: minor

這輪我只找到一條 finding:拿掉兩個漢字中間的空白,會讓一些正常中文寫法被判成危險詞。我在實驗 clone 裡跑了門掃描,並跑了 `-k note_lines`、`-k nogo` 兩組測試,共 24 項通過。實驗目錄已刪。

severity: minor
blocking: 否 — 只會把誠實計劃多判成風險高,作者按訊息改寫或補已排除行就能繞過去;真實計劃庫實測沒有一份受影響。
引句:「兩個漢字中間的空白拿掉」
問題:`_door_scan_text` 在比對前把兩個漢字之間的空格拿掉,詞與詞之間的空白也一併拿掉。前一個詞的最後一字加後一個詞的第一字,就可能拼出危險詞。作者只承認了「面對 外部」。我實際跑了 `_door_keyword_hits`,下面這些都被判成危險詞:
- 「針對 外部服務的串接」被判成對外送出(拼出「對外」)。
- 「以上 架構如下」和「向上 架構分層」被判成不可逆(拼出「上架」)。
- 「折扣 款式分類」被判成金流(拼出「扣款」)。
- 「配送 出貨流程」和「運送 出貨」被判成對外送出(拼出「送出」)。
- 「精簡 訊息提示」被判成對外送出(拼出「簡訊」)。
- 「郵寄 送達時間」被判成對外送出(拼出「寄送」)。
- 「搬遷 移除舊檔」被判成不可逆(拼出「遷移」)。
- 「不可 逆向推導」被判成不可逆。
- 「資金 流向圖」被判成金流。

「針對 外部」、「以上 架構」、「折扣 款式」比「面對 外部」常見得多。全形空白經 NFKC 變成一般空格,tab 被壓成一個空格,所以這兩種分隔也一樣會拼起來。

具體失敗情境:計劃正文寫「針對 外部服務做串接」,但實際沒有任何對外動作。輸入後得到風險高,要走設計審,或在實務隱患節補已排除行。我用 `/Users/enzo/orca/workspaces/lumos-toolchain/Backend_improve/docs/lumos-toolchain-knowledge/Projects` 的 334 份計劃量過,新規則新增的命中是 0 份,所以現實頻率低。這個副作用的代價(多判高、不會漏判)作者已承認,但注釋只舉了一個例子,低估了範圍。

佐證:``file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:8203` ``(`_DOOR_HAN_GAP_RE`)與 ``file: `/Users/enzo/orca/workspaces/lumos-toolchain/spec-gate-nondo/scripts/lumos:8198` ``(`_door_scan_text`)。

其餘重點的結論:
- 切行與行號:已讀,無 finding。門掃描、不做清單、找節、條款定義與指紋、`[keeps]`、條款檢查、計劃連結這一族都走 `_note_lines`,行號一致。`_note_lines` 對結尾換行和空字串的行為與 `splitlines` 在一般文字上相同。
- 沒改的函式與行號:已讀,無 finding。仍用 `split("\n")` 或 `splitlines` 的函式有三類。`_pq_clause_tests` 與 `_intake_declared` 只看內容、不用行號。報告相關函式處理的是別種文字。`_ns_test_ref_lines` 把條款定義行號(`\n`、`\r` 都切)和 `_visible_lines(text.split("\n"))`(只切 `\n`)拿來交集,只有文字裡出現單獨的 `\r` 才會對不上。檔案經 `read_text` 或文字模式的 git 讀入時 `\r` 會先轉成 `\n`,所以我判定走不到,沒當成 finding。
- 誠實流程:已讀,無 finding。相關測試通過。
- 門規則版本 9 對既有留痕:已讀,無 finding。舊留痕在新規則下判高時,訊息會帶「留痕用的是較舊的門判定規則」。舊留痕仍判低、但不做清單裡多了新命中時,只會報「風險低留痕過期」,雖然沒有版本說明,但指示重跑,可接受。
- 資料狀態五問:已讀,無 finding。治理帳改在 `_nogo_ctx` 讀一次,我實測 20MB 的帳讀一次約 0.18 秒。帳壞時只影響 (b) 出口,讀不到審查帳的早退分支也不會用到它。`door_rule` 欄位缺漏或型別不對時已有 `isinstance` 守衛。

最高等級 minor,blocking 0 條。
