severity: minor

臨時目錄 cr-sgn3-邊界 已刪。主審輸入與跑法:我讀了修補差異、跑了 `_nogo_skip_lines` 的邊界輸入,並在複製的工作樹上做了突變測試(複製的樹已刪)。

突變測試只跑完前三個:`fullwidth` 兩處拿掉、`all` 改成 `any`。其餘五個(拿掉 `_NOGO_REF_TOKEN_RE`、保留標頭後第一子句、減少切點、不剝清單標記、一律跳過)因逾時被我終止,沒有結果,只能算沒驗到。

severity: minor
blocking: 否 — 只會讓判定更嚴(誤判成高風險)或更鬆在少見英文句型,沒有繞過已有測試保護的中文主路徑。
引句:「^(?:不做|不支援|不提供|不處理|不含|不包含|不實作|不開發|暫不|本期不|本版不|這一版不|不在本期|排除"」
問題:`_NOGO_NEG_PREFIX_RE` 的英文片語 `will not`、`out of scope`、`won't` 沒有右側字邊界,而且是不分大小寫的前綴比對。
具體失敗情境:`- will notify payment webhook` 被當成「不做」跳過,實測 `_nogo_skip_lines` 回 True,危險詞(webhook、payment)不計入風險。`- 排除障礙後直接扣款` 同樣被跳過。r1 測試專門釘過 `notification` 不算否定,這次改成前綴比對後,同一類英文黏連又開了回來,測試清單沒有對應案例。
佐證:`scripts/lumos:7928`(`_NOGO_NEG_PREFIX_RE`)、`scripts/test_lumos.py` 的 `t_spec_gate_nogo_item_needs_negation`(high 清單沒有 will notify)

severity: minor
blocking: 否 — 守備方向偏嚴,只是讓不做節常見寫法白白判成高風險。
引句:「s = re.sub(r"^\s*(?:[-*+]|\d{1,9}[.)])[ \t\u3000]+", "", _strip_inline_markup(ln)[0]).strip()」
問題:`_strip_inline_markup` 只剝行內程式碼,不剝粗體。標點與括號也都是切點,括號補充、換行折行都會讓整行不跳過。
具體失敗情境(實測都是 False,即照掃):
- `- **不做**退款`、`- **不做退款**`:粗體包住否定詞,前綴比對失敗。
- `- 不做退款(Stripe)`、`- 不做退款(含部分退款)`:括號裡的子句不以否定開頭。
- `- 不做退款,也不做扣款`、`,亦不做`:「也」「亦」開頭的子句不算否定。
- 折行:`- 不做退款流程,包括` 加上下一行 `  Stripe refund`,續行各自判,第二行被掃。
這些都是不做節的典型寫法,功能對它們失效,作者只會看到「危險詞沒算進風險」。
佐證:`scripts/lumos:8002-8009`(`_nogo_line_says_nogo`)

severity: minor
blocking: 否 — 屬測試覆蓋缺口。
引句:「indent = _ns_indent(ln, fullwidth=True)」
問題:`fullwidth=True` 的兩個呼叫端沒有任何行為測試守著。
具體失敗情境:我把這兩處各自改成不傳 `fullwidth`,`-k nogo` 全部 114 支行為測試仍綠,只有原始碼雜湊釘值那支紅(它本來就會對任何改動紅,測不到行為)。原因是現有的全形案例「兩個全形空白對 `- ` 的第 2 欄」,不論全形算 1 格或 2 格都剛好成立。要分得出來得用「`- 不做X` 後接單一個全形空白縮排的 `不做Y`」(全形算 2 格才是續行)。`⓪` 那條只直接測 `_ns_indent` 函式本身。
佐證:`scripts/test_lumos.py` 的 `t_spec_gate_nogo_tab_fullwidth_continuation`

severity: minor
blocking: 否 — 只在作者刻意用句號串起「不做」與要做的事時才放行,屬設計取捨。
引句:「_NOGO_CLAUSE_SPLIT_RE = re.compile(r"[,,;;。:：()()【】\[\]]|但是|但|而是|只有|只|另外|同時|並且|改成|改為|還要|也要"」
問題:切點表不含半形 `.`、`+`、`/`、`→`、`並`、`以及`、`然後`、`then` 等。
具體失敗情境:實測以下都被跳過,後半的危險詞不計入風險:`- 不做退款 並 Stripe 扣款`、`- 不做退款 + 扣款`、`- 不做退款 以及 扣款`、`- 不做退款. Implement Stripe charge`、`- 不做退款 then charge cards`、`- 不做退款 / Do charge cards`、`- 不做退款 → 改用 Stripe 扣款`。全形句號 `。` 倒是有切。屬列舉式切點的固有缺口,但推論「每句都以否定開頭」依賴切點完整。
佐證:`scripts/lumos:7933-7934`

已讀,無 finding:
- `_ns_indent` 加 `fullwidth` 參數:預設行為逐字節等價(`lead` 長度等於原本 `len(e)-len(e.lstrip())`),筆記格子的兩個既有呼叫端 `33910`、`34014` 沒變。
- tab、CRLF、nbsp、換頁、U+2028/U+0085:一律當成斷行或縮排,與 `_visible_lines` 的行號口徑一致,沒有錯位。
- 零寬字元、NFD 組合記號:只會讓行不被跳過或對判定無影響。
- 行內程式碼、未閉合反引號:`_strip_inline_markup` 與關鍵字掃描用同一支,兩邊一致。
- HTML 註解:整行停止,與修補前相同。
- 編號清單與多層巢狀:`10.` 的內容起點和子項縮排判定正確。
- 空子句、只有標點的行:`- ,`、`- 。`、`- ()` 不跳過;`- 不做:` 空標頭跳過,無害。
- `_NOGO_REF_TOKEN_RE`:枚舉所有 0 至 3 小寫字母加數字的字串,沒有任何一個命中四類危險詞表。
- 效能:20 萬項目 1.3 秒、30 萬子句單行 0.2 秒、3000 層巢狀 0.3 秒、5 十萬空白與 20 萬個 `and` 無退化。
- 突變:`all` 改 `any` 有 5 支行為測試紅,測得到逐句判。

最高等級 minor,blocking 0 條。
