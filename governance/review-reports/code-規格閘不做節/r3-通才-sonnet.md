severity: minor

已讀,無 finding 的部分:
- `_ns_indent` 既有兩個呼叫端(筆記格子的續行判斷)。預設 `fullwidth=False`,算法跟原本逐字相同。
- `_clause_block_sha` 在 nogo_skipped 為空時不加任何 parts,舊留痕指紋不變。
- 門判定規則版本 2 之後,doctor 的前 30 份只數現行版本;blocker 那條仍看全部。
- 舊版本留痕在推送前重判時不會被誤殺,新版留痕在舊版 lumos 上有「先更新 lumos」的提示。
- `_door_judge` 回傳多了 `nogo_skipped`。所有消費端(`_spec_gate_record`、推送前重驗、`_spec_gate_print_door`)都有取到它。
- 我跑了子集 `-k nogo`(115 個)、`-k door_rule`(15 個)、`-k spec_gate`(207 個),全部通過。
- 標題下的清單邊界(空行後不是項目、`###`、行號斷開、圍欄)我實測過,都會正確停。

severity: minor
blocking: 否 — 只會讓風險判定在作者自己寫不做清單時偏寬,而且得是作者刻意或疏忽寫出轉折;推送前的留痕雜湊還會把被跳過的詞記帳。
引句:「_NOGO_CLAUSE_SPLIT_RE = re.compile(r"[,，;；。:：()（）【】\[\]]|但是|但|而是|只有|只|另外|同時|並且|改成|改為|還要|也要"」
問題:子句切點只收一部分轉折詞,中文沒有標點隔開的轉折會漏切。整行因此被判成「每一句都在說不做」而整行跳過,行內的危險詞不算進風險。
具體失敗情境:我實測 `## 不做` 底下這幾行都被跳過。
- `- 不做退款而且順便刪 production 資料`
- `- 不做退款並發信給客戶`
- `- 不做退款然後 send email`
- `- 不做退款 then send email`

「而且、順便、並、然後、再、以及、then」都不在切點裡,後面接的要做的事就成了前一句的一部分。對照之下,`,以及發信給客戶` 和 `;順便 send email` 反而不跳過,是靠標點才切開的。規則的設計意圖(r2 說「能把要做的事接在不做後面的詞」要切)沒做完。上面第四行的 then 是英文,而 `\b(?:and|but|instead|also)\b` 只收這四個詞,同類的 then、plus、while 都沒收。
佐證:file: `scripts/lumos:7926`(`_NOGO_CLAUSE_SPLIT_RE`)、file: `scripts/lumos:8008`(`_nogo_line_says_nogo`)。

最高等級 minor,blocking 0 條。
