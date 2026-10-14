severity: minor

我主要查規格閘其他判定、推送前閘、doctor、`--door-rule` 輸出,以及 rebase 後跟主線的互動,找到一條 minor,沒有 blocking。

跑了 `-k` 子集:nogo(93 條)、door_rule(9)、spec_gate_push(8)、spec_gate_door(8)、twoway(18)、escape(170)、small_change(15),全綠。`lumos spec-gate --door-rule` 印出 `door_rule=2` 與釘住的指紋,兩者一致。

---

severity: minor
blocking: 否 — 情境要作者在「## 不做」下寫了肯定句、又剛好帶「不可逆」「無論」這類詞才會碰到,不是一般寫法;分支宣告的風險是「少算」而不是正確性崩壞,而且只是讓風險判定偏鬆,不會弄壞其他判定。
引句:「_NOGO_NEG_RE = re.compile(r"不|沒有|無|排除|暫緩|非本期|\bout of scope\b|\bnot\b", re.I)」
問題:否定字樣用單字元「不」「無」比對,會被不帶否定意思的詞命中。「不可逆」「無論」「不只」「不論」都算數。
具體失敗情境:計劃寫
```
## 不做
- 本版會實作退款(不可逆)
```
我實測 `_nogo_skip_lines` 回 {2},這行整行被跳過。「退款」(金流)和「不可逆」(不可逆類)兩個危險詞都不算進風險。只要實務隱患節的四行已排除也補齊,這份計劃就判成風險低,可以不走設計審。`- 無論如何,實作 Stripe 扣款` 同樣被跳過。留痕裡有 `nogo_skipped_n` 和 `nogo_skipped`,事後查得到;`doctor` 只提醒不擋。建議否定字樣改成「項目開頭(清單標記後)的否定詞」,或把「不可逆」「無論」「不只」「不論」這類複合詞排除,而不是在整行任意位置找「不」。
佐證:``file: `scripts/lumos:8023` ``(`_nogo_skip_lines` 用 `_NOGO_NEG_RE.search` 判整行)

---

已讀,無 finding:
- `doctor` S14 的前 30 份改成先篩 `door_rule` 等於現行版本。現行測試 ④ 涵蓋舊版、字串版和缺欄位。升到 v2 後舊留痕不進前 30,這是計劃裁定的重數。blocker 那條仍看全部。
- 推送前 `_spec_gate_push_stale`:
  - 舊留痕(版本 1)的 `clause_sha` 在 `nogo_skipped` 為空時,指紋與加參數前逐位相同,不會誤判過期。
  - 新版留痕碰上舊版 lumos 時的提示行只加在風險判高的分支,不影響其他回傳。
- `_door_judge` 回傳新增 `nogo_skipped` 鍵。呼叫端(`_spec_gate_front`、`_spec_gate_record`、`_spec_gate_push_stale`)都從同一支取值,沒有自己組 dict 而漏鍵的路徑。
- 跟主線新加的引句判準那批沒有碰到同一段程式。`_visible_lines` 和 `_h2_section_lines` 沒被改,只被這次改動呼叫。
- 子項目、縮排續行、空行後的散文、Setext 底線、HTML 註解、CRLF、tab 縮排我都實測過,行為符合〈做法〉。

總結:最高等級 minor,共 1 條,blocking 0 條。
