severity: minor

## 審查範圍與結論

我讀了修補差異全文,並對 `lens-repo` 做了三項實驗,全程唯讀,實驗目錄已刪。

- **一般使用走得通。** 同一工作樹路徑和 `<提交>:<路徑>` 兩種寫法都實跑過,計劃來源行、程式檔行、牽連檔行、「太泛不列」計數都正確。
- **合法名字沒被誤藏。** 我拿這個 repo 全部 13717 個追蹤檔名過白名單,0 個被擋。含中文、空白、`Issues/`、全形括號的都正常。節點名最長沒超過 80 字。
- **計數與「另有 N 個」沒問題。** `_lens_spec_names_line` 的條件運算式優先序正確,全不合或部分不合兩種情形的輸出都對。
- **`--json` 沒有被動到。** `code_files`、`too_generic`、`only_in_commit` 仍是原始值,只有 `text` 經過出口。這是有意的取捨。
- **掛鉤十六進位那段正常。** 七到六十四碼的邊界、大小寫、六十五碼以上落入整段檢查,都沒問題。
- **資料狀態五問:** 這輪沒有新增持久狀態,不快取、不寫帳。凍結快照和 `spec-freeze` 的寫入路徑不在這輪修補內,我沒細查。
- **be-api-compat:** 欄位名稱與型別沒變,只有 `text` 內容變。舊版呼叫端讀得懂。
- **be-authz:** 不適用,沒有新端點。

以下兩條是我找到的問題。

---

severity: minor
blocking: 否 — 只影響少見的韓文 NFD 寫法,列不到的節點仍有計數,不會讓派工詞出錯
引句:「if _ud.normalize("NFC", node) in seen:   # 比 NFC 鍵:同一篇的 NFC 與 NFD 寫法只算一次(代碼審 r4 正確性2)」

**問題(正確性 1,NFC 去重後少列)。** `_lens_spec_linked` 先用 NFC 鍵去重,再檢查名字。白名單收韓文音節 U+AC00 到 U+D7AF,但不收 NFD 展開後的韓文字母 U+1100 一帶。同一個節點的兩種寫法,名字檢查的結果不同。

具體情境:
- 輸入:計劃先出現 `[[Systems/한글]]` 的 NFD 寫法(macOS 複製檔名常見),後面又出現 NFC 寫法,而且會談目錄真有這篇。
- 實測 `_lens_spec_linked` 回傳 `([], [], 1, 0, 0, False)`:`linked` 空、`n_bad` 為 1。
- 預期:修補前兩種寫法各自處理,NFC 那篇會進 `linked`。現在它因為 `seen` 已記了 NFD 的 NFC 鍵而被略過,存在的節點沒被列出。

`_lens_spec_code_cands` 同族:去重後「留第一次出現的寫法」,先出現 NFD 就留下會被出口判不合的寫法。

修法:去重鍵之外,先在白名單過 NFC 後的寫法,或遇到不合的 NFD 時不把鍵放進 `seen`。

佐證:
- `scripts/lumos:670` 附近的 `_lens_spec_linked`(去重那行在 `if _ud.normalize("NFC", node) in seen`),在 repo 內的實際位置約為 `scripts/lumos:49665`。
- `scripts/lumos:49495` 附近的 `_lens_spec_code_cands`。
- 範圍外提醒:本 repo 威脅模型只顧中英文。若判定韓文不在範圍,可放行並附理由。

---

severity: minor
blocking: 否 — 目標架構段仍附規則與檔數,只是看不出是哪幾支檔,審查席退回照鄰居審
引句:「shown = {node: [_lens_author_name_show(f, _LENS_SPEC_PATH_MAX) for f in fs] for node, fs in _arch_target_split(cands, rules).items()}」

**問題(正確性 2,出口誤藏合法名字)。** 目標架構段的檔名在 `_arch_target_text` 裡本來就會逐一經過 `_kill_esc`,特殊字元會變成看得見的 `\uXXXX`。現在又先過白名單出口,所以在白名單外的字元不是被轉義,而是整支檔名被換成固定字樣。

具體情境:
- 輸入:消費專案(Next.js 或 Android)的計劃用反引號寫 `app/[id]/page.tsx`、`src/@types/x.d.ts`、`a+b.kt`、`Foo$Bar.kt`。
- 結果:「基準:目標架構 X(3 支檔):(名字含不收的字元), (名字含不收的字元), …」。審查席不知道哪幾支檔要照目標規則審,而這段的用途正是「段裡列到的檔照這些規則審」。
- 修補前:這些名字原本會被安全轉義後照列。

反引號那條候選正規式 `[^`\s]+/[^`\s]+\.[A-Za-z0-9]+` 收得進這些名字,但程式檔那條只收 ASCII 的 `[A-Za-z0-9_./\-]`,所以這個損失只落在反引號寫法。

修法:這一段已有 `_kill_esc` 保護,可以不再經出口,或出口對這一段改用「轉義而不是整串換字樣」。`t_dispatch_lens_spec_author_names_single_exit` 的掃描若要求每個輸出點都走出口,這個例外要明講。

佐證:
- `scripts/lumos:49844`(`_dispatch_lens_spec_arch_text`)。
- `scripts/lumos:_arch_target_text`(每個檔名插值前都有 `cl(f)`)。

---

最高等級 minor,blocking 0 條。
